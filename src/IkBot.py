import asyncio
import copy
import os
import random
import re
import threading
import time
import WikiScraper
from datetime import datetime

import discord
import pygsheets
import pytz
from discord.ext import commands

# import the customized settings and file locations etc, found in myconfig.py
import myconfig

# allow for testing, by forcing the bot to read an old log file for the VT and VD fights
from src.eq_logs.eq_log_event import EQLogEvent
from src.eq_logs.eq_log_event_wiki_link import EQLogEventWikiLink
from src.eq_logs.eq_log_parser import EQLogParser

TEST_BOT = False
# TEST_BOT                = True

CST = pytz.timezone('US/Central')

# Google sheets integration
ENABLE_GOOGLE_SHEET = False
try:
    gc = pygsheets.authorize(service_account_json=myconfig.GOOGLE_SHEETS_KEY)
    ikbot_sheet  = gc.open('IkBot')

    roster_sheet     = ikbot_sheet.worksheet_by_title('Roster')
    #roster_sheet     = ikbot_sheet.worksheet_by_title('IkBot Testing Roster')
    target_sheet     = ikbot_sheet.worksheet_by_title('Targets')
    item_sheet       = ikbot_sheet.worksheet_by_title('Items')
    taunt_Sheet      = ikbot_sheet.worksheet_by_title('Taunts')
    trade_sheet      = ikbot_sheet.worksheet_by_title('Trade')
    quest_sheet      = ikbot_sheet.worksheet_by_title('Quests')
    message_sheet    = ikbot_sheet.worksheet_by_title('Msg Pri')
    ENABLE_GOOGLE_SHEET = True
except AttributeError as e:
    print("Connecting to google sheet failed.\nError: ")
    print(e)

if ENABLE_GOOGLE_SHEET:
    target_list             = [cell[0] for cell in target_sheet.range('A2:A', returnas='matrix')]
    item_list               = [cell[0] for cell in item_sheet.range('A2:A', returnas='matrix')]
    trade_list              = [cell[0] for cell in trade_sheet.range('A2:A', returnas='matrix')]
    roster_list             = [cell[0] for cell in roster_sheet.range('A2:A', returnas='matrix')]
    quest_list              = [cell[0] for cell in quest_sheet.range('A2:A', returnas='matrix')]
    taunt_death_list        = [cell[0] for cell in taunt_Sheet.range('B2:B', returnas='matrix')]
    taunt_new_member_list   = [cell[0] for cell in taunt_Sheet.range('A2:A', returnas='matrix')]
    
else:
    target_list  = ["testSpider"]
    item_list    = ["Iksar Berserker Club"]
    trade_list   = ["testCraft"]
    roster_list  = ["testIksar"]
    taunt_death_list = ["testFAILURE"]
    taunt_new_member_list = ["testWelcome"]

# Set Variables
IkBot_Ver = 'v2023.0.3'
if ENABLE_GOOGLE_SHEET:
    IkBot_Ver_Latest = ikbot_sheet.worksheet_by_title('IkBot Info').get_value('A2')
else:
    IkBot_Ver_Latest = IkBot_Ver
IkBot_Rel = f'https://github.com/Vanifac/P99-Legacy-of-Ik-Bot/releases/tag/{IkBot_Ver_Latest}'

#################################################################################################

#
# class to encapsulate log file operations
#
class EverquestLogFile:

    # list of regular expressions matching log files indicating the 'target' is spawned and active
    trigger_list = [
        '^(.+) (have|has) been slain by',
        '^(.+) (have|has) slain',
        '^Players (on|in) EverQuest:',
        '^(.+)<Legacy of Ik>',
        '^There (is|are) (\d)+ (player|players) in',
        '^You have entered (?!an Arena)',
        '^--(\w)+ (have|has) looted a',
        '^You have gained a level! Welcome to level ',
        '^You have become better at (.+)!',
        "^(\w)+ tells you, 'Attacking (.+) Master.'",
        '^(\w)+ -> (\w)+: IkBot-(Quest|Claim|Thrall)',
        "^(\w)+ (tells|told) (\w)+, 'IkBot-(Quest|Claim|Thrall)"
    ]

    # General Variables
    my_zone = 'Unknown'
    my_level ='1'
    my_pet = 'Unknown'
    tradeskills_dict = {}
    tradeskills_string = ''

    if ENABLE_GOOGLE_SHEET:
        roster_dict         = roster_sheet.get_all_records()
        new_roster_dict     = copy.deepcopy(roster_dict)
        roster_name_list    = [member['Name'] for member in new_roster_dict]

    #
    # ctor
    #

    def __init__(self, char_name=myconfig.DEFAULT_CHAR_NAME):

        # instance data
        self.base_directory = myconfig.BASE_DIRECTORY
        self.logs_directory = myconfig.LOGS_DIRECTORY
        self.char_name = char_name
        self.server_name = myconfig.SERVER_NAME
        self.filename = ''
        self.file = None

        self.parsing = threading.Event()
        self.parsing.clear()

        self.author = ''

        self.prevtime = time.time()
        self.heartbeat = myconfig.HEARTBEAT

        # timezone string for current computer
        self.current_tzname = time.tzname[time.daylight]

        # build the filename
        self.build_filename()

    # build the file name
    # call this anytime that the filename attributes change
    def build_filename(self):
        self.filename = self.base_directory + self.logs_directory + \
            'eqlog_' + self.char_name + '_' + self.server_name + '.txt'

    # def build_filename(self):
    #    self.loglocation = self.base_directory + self.logs_directory
    #    while True: #checking for an active log
    #        try:
    #            max([f for f in os.scandir(self.loglocation)], key=lambda x: x.stat().st_mtime).name
    #            break
    #        except ValueError:
    #            print('No Active Logs Found, retrying in 5s..')
    #            time.sleep(5)
    #    self.filename = max([f for f in os.scandir(self.loglocation)], key=lambda x: x.stat().st_mtime).name
    #    while (self.filename == 'dbg.txt'): #checking for an active log
    #        print('No Active Logs Found, retrying in 5s..')
    #        time.sleep(5)
    #        self.filename = max([f for f in os.scandir(self.loglocation)], key=lambda x: x.stat().st_mtime).name
    #    print(self.filename)

    # is the file being actively parsed
    def set_parsing(self):
        self.parsing.set()

    def clear_parsing(self):
        self.parsing.clear()

    def is_parsing(self):
        return self.parsing.is_set()

    # open the file
    # seek file position to end of file if passed parameter 'seek_end' is true
    def open(self, author, seek_end=True):
        try:
            self.file = open(self.filename)
            if seek_end:
                self.file.seek(0, os.SEEK_END)
            self.author = author
            self.set_parsing()
            return True
        except Exception:
            return False

    # close the file
    def close(self):
        self.file.close()
        self.author = ''
        self.clear_parsing()

    # get the next line
    def readline(self):
        if self.is_parsing():
            return self.file.readline()
        else:
            return None

    # regex match?
    def regex_match(self, line):
        event = None
        # cut off the leading date-time stamp info
        trunc_line = line[27:]
        # walk thru the target list and trigger list and see if we have any match
        for trigger in self.trigger_list:
            if re.match(trigger, trunc_line):
                #print('MATCH')
                # DEATH
                if 'You have been slain' in trunc_line:
                    mob = trunc_line.index('by ')+3, trunc_line.index("\n")
                    event = 'SelfDeath', trunc_line[mob[0]:mob[1]]

                #Roster Updates
                elif re.match('^Players (on|in) EverQuest:', trunc_line):
                    self.roster_dict = roster_sheet.get_all_records()
                    self.roster_name_list  = [member['Name'] for member in self.roster_dict]
                    self.new_roster_dict = copy.deepcopy(elf.roster_dict)
                    return None

                elif '<Legacy of Ik>' in trunc_line:
                    return self.update_roster(trunc_line)

                elif re.match('^There (is|are) (\d)+ (player|players) in', trunc_line):
                    if self.roster_dict != self.new_roster_dict:
                        print('Updating Roster..')
                        self.roster_name_list = [member['Name'] for member in self.new_roster_dict]
                        new_roster_list       = [list(member.values()) for member in self.new_roster_dict]
                        roster_sheet.update_values('A2', new_roster_list, parse=False)
                    return None

                # Level Parsing
                elif 'You have gained a level! Welcome to level' in trunc_line:
                    self.my_level = int(trunc_line[-4:-1].strip('!'))
                    if self.my_level % 5 == 0 and self.my_level > 9:
                        return ['LevelUp', elf.char_name, self.my_level]

                # ZONE Tracking
                elif 'You have entered ' in trunc_line:
                    self.my_zone = trunc_line[17:trunc_line.index(".")]

                # Pet Parsing
                elif re.match('^(\w)+ tells you, \'Attacking (.+) Master.\'', trunc_line):
                    self.my_pet = trunc_line[:trunc_line.index(' tells')]

                # Kill Parsing Self / Pet / Ik Member
                elif 'You have slain ' in trunc_line:
                    if event := [['Kill', elf.char_name, target]
                                 for target in target_list if target in trunc_line]:
                        return event[0]
                elif ' has been slain by ' in trunc_line:
                    if event := [['Kill', elf.char_name, target]
                                 for target in target_list
                                 if elf.my_pet in trunc_line and target in trunc_line]:
                        return event[0]
                    if event := [['Kill', member, target]
                                 for member in self.roster_name_list for target in target_list
                                 if member in trunc_line and target in trunc_line]:
                        return event[0]

                # Loot Parsing
                elif 'You have looted a' in trunc_line:
                    if event := [['Loot', elf.char_name, item]
                                 for item in item_list if item in trunc_line]:
                        return event[0]
                elif 'has looted a' in trunc_line:
                    if event := [['Loot', member, item]
                                 for member in self.roster_name_list for item in item_list
                                 if member in trunc_line and item in trunc_line]:
                        return event[0]

                # Tradeskills
                elif 'You have become better at ' in trunc_line:
                    skill = int(trunc_line[-5:trunc_line.index(")")].strip('( '))
                    for trade in trade_list:
                        if trade in trunc_line and skill > 24:
                            if not self.tradeskills_dict:
                                self.tradeskills_string = roster_sheet.cell((roster_sheet.find(self.char_name)[0].row, roster_sheet.find('Tradeskills')[0].col)).value
                                if self.tradeskills_string:
                                    self.tradeskills_dict = {x.strip(): y.strip() for x, y in (element.split(' ') for element in self.tradeskills_string.split(' / '))}
                            self.tradeskills_dict.update({trade: f'({skill})'})
                            if (skill % 50 == 0) or (skill > 124 and skill % 25 == 0):
                                return 'Trade', trade, skill

                # IkBot Commands
                elif re.match('^(.+)ikbot-quest-', trunc_line.lower()):
                    return self.parse_ikbot_command(trunc_line)

        # only executes if loops did not return already
        return event

    # Build / update roster entry
    def update_roster(self, who_str):
        if '[ANONYMOUS]' in who_str: 
            return None
        who_str = who_str.strip('AFK ')
        ind = who_str.index('] '), who_str.index(' ('), who_str.index(' ')
        name = who_str[ind[0]+2:ind[1]]
        zone = copy.copy(self.my_zone)
        
        if zone_update := 'ZONE:' in who_str:
            zone = (who_str[who_str.index(': ')+2:who_str.index("\n")-2]).strip(' L')
            
        # Check if member is on the roster
        if member := next((item for item in self.new_roster_dict if item['Name'] == name), {}):
            member.update({'Level': int(who_str[1:ind[2]]), 'Zone': zone,
                           'Last Seen': datetime.now(CST).strftime("%m/%d/%Y %H:00")})
        # If member is not on the roster
        else:
            member = dict.fromkeys(self.new_roster_dict[0])
            member.update({'Name': name, 'Class': who_str[ind[2]+1:ind[0]],
                           'Level': int(who_str [1:ind[2]]), 'Zone': zone,
                           'Last Seen': datetime.now(CST).strftime("%m/%d/%Y %H:00"),
                           'Joined': datetime.now(CST).strftime("%m/%d/%Y")})
            self.new_roster_dict.append(member)
            return 'NewMember', member['Name']

        # Do things if this is me
        if name == self.char_name:
            self.my_level = copy.copy(member['Level'])
            member.update({'Last used IkBot': datetime.now(CST).strftime("%m/%d/%Y"), 'IkBot Version': IkBot_Ver})
            if zone_update:
                self.my_zone = copy.deepcopy(zone)
            if self.tradeskills_dict:
                member.update({'Tradeskills': ' / '.join(' '.join((key, val)) for (key, val) in self.tradeskills_dict.items())})
        return None

    def parse_ikbot_command(self, command):
        command = [word.strip(" '") for word in command.lower().split('-')]
        if 'you told ' in command[0]:
            command[0] = self.char_name.lower()
            command.insert(1, 'ikbot')
        elif ' tells you' in command[0]:
            command[0] = command[0].split(' ')[0]
            command.insert(1, 'ikbot')
        if command[2] == 'quest':
            if event := [['Quest', member, item]
                        for member in self.roster_name_list for item in quest_list
                        if member.lower() in command[0] and item.lower() in command[3]]:
                return event[0]
    
    # create (guess) the link to the item on the wiki
    def link_to_Wiki(self, itemName):
        wiki_url_prefix = "https://wiki.project1999.com/"
        wiki_url_item_guess = itemName.replace(" ", "_")
        return wiki_url_prefix + wiki_url_item_guess

            
            
# create the global instance of the log file class
elf = EverquestLogFile()
# create the global instance of the web scraping class
scraper = WikiScraper.WikiScraper()
# create global for parser
eq_log_parser = EQLogParser()


async def trigger_discord_event(event: EQLogEvent):
    # if event is type EQLogEventWikiLink
    if isinstance(event, EQLogEventWikiLink):
        wiki_link = event.get_wiki_link()
        item_name = event.get_item_name()
        embed = None
        try:
            embed = discord.Embed(
                title=item_name,
                url=wiki_link,
                description=scraper.scrape_wikipage_item(wiki_link))
        except:
            print("failed to parse " + wiki_link)
        to_send = f"{myconfig.DEFAULT_CHAR_NAME} just received the {item_name} as reward for their wonderfully evil deeds, the Empire grows stronger!!"
        await client.alarm(to_send, embed)
    else:
        # TODO: Handle other event types - but ideally clean this up so discord, scraper, myconfig, client and any other dependencies are accessible to external classes
        pass


#################################################################################################

# the background process to parse the log files
#
# override the run method
#


async def parse():
    print('Parsing Started - Make sure to turn on logging in EQ with /log command. FOR IK!')
    print('-'*40)

    # process the log file lines here
    while elf.is_parsing() == True:
        # read a line
        line = elf.readline()
        now = time.time()
        if line:
            #time.sleep(.05)
            elf.prevtime = now
            print(line, end='')

            # NEW PARSING LOGIC
            if event := eq_log_parser.parse(line):
                await trigger_discord_event(event)

            # does it match a trigger? - OLD PARSING LOGIC
            if event := elf.regex_match(line):
                #time.sleep(.5)
                #print(event)
                # Discord Bot Triggers
                
                # Level Up
                if 'LevelUp' in event[0]:
                    await client.alarm(f'{event[1]} has reached level {event[2]}! Now get back to work!')

                # Self Death
                elif 'SelfDeath' in event[0]:
                    await client.alarm(f'{elf.char_name} has fallen to {event[1]}! {random.choice(taunt_death_list)}')

                # Roster Updates
                elif 'New' in event[0]:
                    await client.alarm(f'Bahaha! {event[1]} has pledged their life to the Legacy! {random.choice(taunt_new_member_list)}')

                # Tradeskill Milestones
                elif 'Trade' in event[0]:
                    quip_loc = f'B{str(trade_list.index(event[1]) + 1)}'
                    await client.alarm(f'{event[2]} {event[1]}! Pretty impressive {elf.char_name}. {trade_sheet.get_value(quip_loc)}')

                # Notable Kills
                elif 'Kill' in event[0]:
                    to_send = f'{event[1]} just killed {event[2]}! **FOR IK!** Any good loot?'
                    await client.alarm(to_send)

                # Notable Loot
                elif 'Loot' in event[0]:
                    wiki_link = elf.link_to_Wiki(event[2])
                    embed = None
                    try:
                        embed = discord.Embed(
                        title=event[2],
                        url=wiki_link,
                        description=scraper.scrape_wikipage_item(wiki_link))
                    except: 
                        print("failed to parse " + wiki_link)
                    to_send = f"{event[1]} just looted the {event[2]} for me! Leave it with the War Baron and he'll get it to me."
                    await client.alarm(to_send, embed)

                # IkBot Item
                elif 'Quest' in event[0]:
                    wiki_link = elf.link_to_Wiki(event[2])
                    embed = None
                    try:
                        embed = discord.Embed(
                        title=event[2],
                        url=wiki_link,
                        description=scraper.scrape_wikipage_item(wiki_link))
                    except: 
                        print("failed to parse " + wiki_link)
                    to_send = f"{event[1]} just received the {event[2]} as reward for their wonderfully evil deeds, the Empire grows stronger!!"
                    await client.alarm(to_send, embed)

        else:
            # check the heartbeat.  Has our tracker gone silent?
            elapsed_minutes = (now - elf.prevtime)/60.0
            if elapsed_minutes > elf.heartbeat:
                elf.prevtime = now
                print(
                    f'Heartbeat Warning:  Tracker [{elf.char_name}] logfile has had no new entries in last {elf.heartbeat} minutes.  Is {elf.char_name} still online?')

            await asyncio.sleep(0.1)

    print('Parsing Stopped')


#################################################################################################


# define the client instance to interact with the discord bot

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

class myClient(commands.Bot):

    def __init__(self):
        self.content = ''
        self.last_sent = ''
        self.last_msg_time = time.time()
        self.logging_channel = None
        commands.Bot.__init__(
            self, command_prefix=myconfig.BOT_COMMAND_PREFIX, intents=intents)
    
    def create_logging_channel(self):
        self.logging_channel = self.get_channel(myconfig.DISCORD_SERVER_CHANNELID)

    # sound the alarm
    async def alarm(self, msg, embd=None):
        secs_since_last = time.time() - client.last_msg_time
        if msg == client.last_sent and secs_since_last < 30:
            print('Duplicate message / Delay not met')
            return
        print(f'Alarm: {msg}')
        if ENABLE_GOOGLE_SHEET:
            try: message_sheet.append_table(values=[elf.char_name])
            except: pass
            time.sleep(2)
            if message_sheet.get_value('A2') == elf.char_name:
                message_sheet.clear(start='A2')
                await self.logging_channel.send(msg, embed=embd)
        else:
            await self.logging_channel.send(msg, embed=embd)


# create the global instance of the client that manages communication to the discord bot
client = myClient()

#################################################################################################


#
# add decorator event handlers to the client instance
#

# on_ready
@client.event
async def on_ready():
    print(f'\nIkBot Version: {IkBot_Ver}')
    if IkBot_Ver != IkBot_Ver_Latest:
        print(f'\033[31mYou are running an outdated IkBot! Please check the discord and download \033[32m{IkBot_Ver_Latest}\033[0m')
        time.sleep(3)
    print(f'Discord.py version: {discord.__version__}')
    print(f'Logged on as {client.user}!')
    print(f'App ID: {client.user.id}')
    client.create_logging_channel()

    await auto_start()

# on_message - catches everything, messages and commands
# note the final line, which ensures any command gets processed as a command, and not just absorbed here as a message
@client.event
async def on_message(message):
    author = message.author
    client.content = message.content
    #channel = message.channel
    if author == client.user:
        client.last_sent = message.content
        client.last_msg_time = time.time()
    #print(
    #    f'Content received: [{client.content}] from [{author}] in channel [{channel}]')
    if myconfig.DISCORD_SERVER_CHANNELID == message.channel.id:
        await client.process_commands(message)

# Discord !commands
#Who command - check roster for people in in this hour and lists them in a response on discord
@client.command()
async def who(message):
    if ENABLE_GOOGLE_SHEET:
        print('---Processing !who command.')
        # Get Updated list of members online in this hour
        who_list  = [member for member in roster_sheet.get_all_records()
                     if member['Last Seen'] == datetime.now(CST).strftime("%m/%d/%Y %H:00")]
        # Building /who message list
        who_msg_list = ["Lets see who's out there taking back my empire..", '`Players in EverQuest:', '-'*27]
        for member in who_list:
            who_msg_list.append(f"[{ member['Level'] } {member['Class']}] {member['Name']} (Iksar) <Legacy of Ik> ZONE: {member['Zone']}")
        if len(who_list) == 1:
            who_msg_list.append(f'There is 1 player in EverQuest.`')
        else:
            who_msg_list.append(f'There are {len(who_list)} players in EverQuest.`')
        if len(who_list) == 0:
            who_msg_list.append("**No one?** *Not a single one of you?* **GET BACK OUT THERE AND SLAY THE SOFT SKINS!**")
        # Send /who Message
        await client.alarm('\n'.join(who_msg_list))

@client.command()
async def ikbot(message):
    print('---Processing !ikbot command.')
    cmd_msg = f'You can download IkBot {IkBot_Ver_Latest} from:\n{IkBot_Rel}'
    await client.alarm(cmd_msg)

@client.command()
async def roster(message):
    print('---Processing !roster command.')
    cmd_msg = f'My list of MIGHTY IKSAR can be found at:\nhttps://tinyurl.com/Ik-Roster'
    await client.alarm(cmd_msg)
    
#@client.command()
#async def claim(message):
#    print('---Processing !claim command.')
#    elf.roster_dict = roster_sheet.get_all_records()
#    if member := next((item for item in elf.new_roster_dict if item['Name'] == name), {}):
#        member.update({'Discord': '1234'})
#    else:
#       pass 
#    cmd_msg = f'1234'
#    await client.alarm(cmd_msg)

#################################################################################################

async def auto_start():
    # await client.connect()
    # await client.login(myconfig.BOT_TOKEN)
    # print("Auto start")
    # print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))
    elf.char_name = myconfig.DEFAULT_CHAR_NAME
    elf.build_filename()

    author = myconfig.DEFAULT_CHAR_NAME

    # open the log file to be parsed
    # allow for testing, by forcing the bot to read an old log file for the VT and VD fights
    if TEST_BOT is False:
        # start parsing.  The default behavior is to open the log file, and begin reading it from tne end, i.e. only new entries
        rv = elf.open(author)
    else:
        # use a back door to force the system to read files from the beginning that contain VD / VT fights to test with
        elf.filename = elf.base_directory + elf.logs_directory + 'test_fights.txt'

        # start parsing, but in this case, start reading from the beginning of the file, rather than the end (default)
        rv = elf.open(author, seek_end=False)

    # if the log file was successfully opened, then initiate parsing
    if rv:
        # status message
        print(f'Now parsing character log for {elf.char_name}: [{elf.filename}]')
        print(f'Heartbeat timeout (minutes): [{elf.heartbeat}]')

        # create the background processs and kick it off
        client.loop.create_task(parse())
    else:
        print(
            f'ERROR: Could not open character log file for: [{elf.char_name}]')
        print(f'Log filename: [{elf.filename}]')


# let's go!!
client.run(myconfig.BOT_TOKEN)
