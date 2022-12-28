import asyncio
import os
import random
import re
import threading
import time
from datetime import datetime

import discord
import pygsheets
import pytz
from discord.ext import commands

# import the customized settings and file locations etc, found in myconfig.py
import myconfig

# allow for testing, by forcing the bot to read an old log file for the VT and VD fights
TEST_BOT = False
# TEST_BOT                = True

# Set Variables
CST = pytz.timezone('US/Central')

# Google sheets integration
gc = pygsheets.authorize(service_account_json=myconfig.GOOGLE_SHEETS_KEY)
IkBotSheet = gc.open('IkBot')
roster_Sheet = IkBotSheet.worksheet_by_title('Roster')
target_Sheet = IkBotSheet.worksheet_by_title('Targets')
item_Sheet = IkBotSheet.worksheet_by_title('Items')
taunt_Sheet = IkBotSheet.worksheet_by_title('Taunts')
trade_Sheet = IkBotSheet.worksheet_by_title('Trade')


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
        '^There (is|are) . (player|players) in',
        '^You have entered (?!an Arena)',
        '^--(\w)+ (have|has) looted a',
        '^You have gained a level! Welcome to level ',
        '^You have become better at (.+)!',
        # '^You have become better at (.+)! \((1|2)(5|0)0\)',
        '^(\w)+ tells you, \'Attacking (.+) Master.\''
    ]

    # list of targets/items/skills which this log file watches for
    target_list = target_Sheet.range('A:A', returnas='matrix')
    item_list = item_Sheet.range('A:A', returnas='matrix')
    trade_list = trade_Sheet.range('A:A', returnas='matrix')
    guild_list = roster_Sheet.range('A:A', returnas='matrix')

    # General Variables
    myZone = 'Unknown'
    myPet = 'Unknown'
    dictSkills = {}
    strSkills = ''

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

    # def get_cell_values(name, col):
    #    Row = 123
    #    column = 123
    #
    #    return

    # regex match?
    def regex_match(self, line):
        event = None
        # cut off the leading date-time stamp info
        trunc_line = line[27:]
        # walk thru the target list and trigger list and see if we have any match
        for trigger in self.trigger_list:
            if m := re.match(trigger, trunc_line):
                # DEATH
                if 'You have been slain' in trunc_line:
                    mob = trunc_line.index('by ')+3, trunc_line.index("\n")
                    event = 'SelfDeath', trunc_line[mob[0]:mob[1]]

                # Roster Updates
                # elif re.match('^Players (on|in) EverQuest:', trunc_line):
                #    print('Who string start')
                #    roster_Sheet.unlink(save_grid=True)
                elif '<Legacy of Ik>' in trunc_line:
                    char = self.parse_who_string(trunc_line)
                    event = self.update_roster(char)
                # elif re.match('^There (is|are) . (player|players) in', trunc_line):
                    # roster_Sheet.sort_range('A2', 'K100', basecolumnindex=5, sortorder='DESCENDING')
                    # TODO link?

                # Level Parsing
                elif 'You have gained a level! Welcome to level' in trunc_line:
                    level = int(trunc_line[-4:-1].strip('!'))
                    print(level)
                    if level % 5 == 0 and level > 9:
                        event = 'LevelUp', level

                # ZONE Tracking
                elif 'You have entered ' in trunc_line:
                    self.myZone = trunc_line[17:trunc_line.index(".")]

                # Pet Parsing
                elif re.match('^(\w)+ tells you, \'Attacking (.+) Master.\'', trunc_line):
                    self.myPet = trunc_line[:trunc_line.index(' tells')]

                # Kill Parsing
                elif 'You have slain ' in trunc_line:
                    for target in self.target_list:
                        if target[0] in trunc_line:
                            event = 'Kill', self.char_name, target[0]
                elif ' has been slain by ' in trunc_line:
                    for target in self.target_list:
                        if target[0] in trunc_line:
                            if self.myPet in trunc_line:
                                event = 'Kill', self.char_name, target[0]
                            else:
                                for member in self.guild_list:
                                    if member[0] in trunc_line:
                                        event = 'Kill', member[0], target[0]

                # Loot Parsing
                elif 'You have looted a' in trunc_line:
                    for item in self.item_list:
                        if item[0] in trunc_line:
                            event = 'SelfLoot', item[0]
                elif 'has looted a' in trunc_line:
                    for item in self.item_list:
                        if item[0] in trunc_line:
                            for member in self.guild_list:
                                if member[0] in trunc_line:
                                    event = 'GuildLoot', item[0], member[0]

                # Tradeskills
                elif 'You have become better at ' in trunc_line:
                    for trade in self.trade_list:
                        skill = int(
                            trunc_line[-5:trunc_line.index(")")].strip('( '))
                        if trade[0] in trunc_line and skill > 24:
                            if not self.dictSkills:
                                self.strSkills = roster_Sheet.cell((roster_Sheet.find(
                                    self.char_name)[0].row, roster_Sheet.find('Tradeskills')[0].col)).value
                                if self.strSkills:
                                    self.dictSkills = {
                                        x.strip(): y.strip()
                                        for x, y in (
                                            element.split(' ')
                                            for element in self.strSkills.split('/')
                                        )}
                            self.dictSkills.update({trade[0]: f'({skill})'})
                            if skill % 50 == 0:
                                event = 'Trade', trade[0], skill

        # only executes if loops did not return already
        return event
    
    # Build character roster entry
    def parse_who_string(self, whoStr):
        ind = whoStr.index('] '), whoStr.index(' ('), whoStr.index(' ')
        if '<Legacy of Ik> ZONE:' in whoStr:
            z1 = whoStr.index(': '), whoStr.index("\n")-2
            char = [whoStr[ind[0]+2:ind[1]], whoStr[ind[2]+1:ind[0]], whoStr[1:ind[2]], whoStr[z1[0]+2:z1[1]], datetime.now(CST).strftime("%m/%d/%Y")]
            if char[0] in self.char_name:
                self.myZone = char[3]
        else:
            char = [whoStr[ind[0]+2:ind[1]], whoStr[ind[2]+1:ind[0]], whoStr[1:ind[2]], self.myZone, datetime.now(CST).strftime("%m/%d/%Y")]
        if char[0] in self.char_name:
            char.append('/'.join(' '.join((key,val)) for (key,val) in self.dictSkills.items()))
        return char

    # Update the Roster
    def update_roster(self, char):
        cell = roster_Sheet.find(char[0])
        if [] != cell:
            # Update existing member
            print(f"###########  {char[0]} found.. updating roster!  ###########")
            roster_Sheet.update_row(cell[0].row, char[2:], col_offset=2)
            event = 'Update'
        else:
            # Add new member
            print(f"###########  {char[0]} not found.. adding to roster!  ###########")
            roster_Sheet.append_table(values=char)
            event = 'New', char[0]
            self.guild_list = roster_Sheet.range('A:A', returnas='matrix')
        return event


# create the global instance of the log file class
elf = EverquestLogFile()

#################################################################################################

# the background process to parse the log files
#
# override the run method
#


async def parse():

    print('Parsing Started')
    print('Make sure to turn on logging in EQ with /log command!')

    # process the log file lines here
    while elf.is_parsing() == True:

        # read a line
        line = elf.readline()
        now = time.time()
        if line:
            elf.prevtime = now
            print(line, end='')

            # does it match a trigger?
            if event := elf.regex_match(line):
                # Discord Bot Triggers
                # Level Up
                if 'LevelUp' in event[0]:
                    await client.alarm(f'{elf.char_name} has reached level {event[1]}! Now get back to work!')
                    
                # Self Death
                if 'SelfDeath' in event[0]:
                    taunt_death = taunt_Sheet.range('B:B', returnas='matrix')
                    await client.alarm(f'{elf.char_name} has fallen to {event[1]}! {random.choice(taunt_death)[0]}')
                    
                # Roster Updates
                elif 'New' in event[0]:
                    taunt_NewMember = taunt_Sheet.range('A:A', returnas='matrix')
                    await client.alarm(f'Bahaha! {event[1]} has pledged their life to the Legacy! {random.choice(taunt_NewMember)[0]}')
                    
                # Tradeskill Milestones
                elif 'Trade' in event[0]:
                    quip_Loc = f'B{str(elf.trade_list.index([event[1]]) + 1)}'
                    await client.alarm(f'{event[2]} {event[1]}! Pretty impressive {elf.char_name}. {trade_Sheet.get_value(quip_Loc)}')
                    
                # Notable Kills
                elif 'Kill' in event[0]:
                    if 'Self' in event[0]:
                        await client.alarm(f'{elf.char_name} just killed {event[1]}! **FOR IK!** Any good loot?')
                    elif 'They' in event[0]:
                        await client.alarm(f'{event[2]} just killed {event[1]}! **FOR IK!** Any good loot?')
                        
                # Notable Loot
                elif 'Loot' in event[0]:
                    if 'Self' in event[0]:
                        await client.alarm(f'{elf.char_name} just looted a {event[1]}! Still warm from the corpse!')
                    elif 'Guild' in event[0]:
                        await client.alarm(f"{event[2]} just looted a {event[1]} for me! Leave it with the War Baron and he\'ll get it to me.")

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
        commands.Bot.__init__(
            self, command_prefix=myconfig.BOT_COMMAND_PREFIX, intents=intents)

    # sound the alarm
    async def alarm(self, msg):
        logging_channel = client.get_channel(myconfig.DISCORD_SERVER_CHANNELID)
        await logging_channel.send(msg)

        print(f'Alarm:{msg}')


# create the global instance of the client that manages communication to the discord bot
client = myClient()

#################################################################################################


#
# add decorator event handlers to the client instance
#

# on_ready
@client.event
async def on_ready():
    print('FOR IK!')
    print(f'Discord.py version: {discord.__version__}')

    print(f'Logged on as {client.user}!')
    print(f'App ID: {client.user.id}')

    await auto_start()


# on_message - catches everything, messages and commands
# note the final line, which ensures any command gets processed as a command, and not just absorbed here as a message
@client.event
async def on_message(message):
    author = message.author
    content = message.content
    channel = message.channel
    print(
        f'Content received: [{content}] from [{author}] in channel [{channel}]')
    await client.process_commands(message)


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
    if TEST_BOT == False:
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
        print(f'Now parsing character log for: [{elf.char_name}]')
        print(f'Log filename: [{elf.filename}]')
        print(f'Parsing initiated by: [{elf.author}]')
        print(f'Heartbeat timeout (minutes): [{elf.heartbeat}]')

        # create the background processs and kick it off
        client.loop.create_task(parse())
    else:
        print(
            f'ERROR: Could not open character log file for: [{elf.char_name}]')
        print(f'Log filename: [{elf.filename}]')


# let's go!!
client.run(myconfig.BOT_TOKEN)

