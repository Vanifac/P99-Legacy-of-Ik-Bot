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
TEST_BOT                = False
#TEST_BOT                = True

# Set Variables
CST = pytz.timezone('US/Central')


# Google sheets integration
# Get Google sheet
gc = pygsheets.authorize(service_file='src\IkBotCred.json')
IkBotSheet = gc.open('IkBot')
roster_Sheet = IkBotSheet.worksheet_by_title('Roster')
target_Sheet = IkBotSheet.worksheet_by_title('Targets')
item_Sheet = IkBotSheet.worksheet_by_title('Items')
taunt_Sheet = IkBotSheet.worksheet_by_title('Taunts')

#################################################################################################


#
# class to encapsulate log file operations
#
class EverquestLogFile:
    myZone = 'Unknown'
    
    # list of regular expressions matching log files indicating the 'target' is spawned and active
    trigger_list = [
        '^(\w)+ (have|has) been slain by*',
        '^(\w)+ (have|has) slain*',
        '^(.+) <Legacy of Ik>*',
        '^(\w)+ have entered*',
        '^--(\w)+ (have|has) looted a*',
        "^(\w)+ tells you, 'Attacking* Master.'",
		#'^(\w)+ have gained a level! Welcome to level',
		]
    
    # list of targets/items which this log file watches for
    target_list = target_Sheet.range('A:A', returnas='matrix')
    item_list = item_Sheet.range('A:A', returnas='matrix')
    
    # emperor taunts
    taunt_NewMember= taunt_Sheet.range('A2:A', returnas='matrix')
    taunt_death = taunt_Sheet.range('A2:A', returnas='matrix')
    
    #
    # ctor
    #
    def __init__(self, char_name = myconfig.DEFAULT_CHAR_NAME):

        # instance data
        self.base_directory = myconfig.BASE_DIRECTORY
        self.logs_directory = myconfig.LOGS_DIRECTORY
        self.char_name      = char_name
        self.server_name    = myconfig.SERVER_NAME
        self.filename       = ''
        self.file           = None

        self.parsing        = threading.Event()
        self.parsing.clear()

        self.author         = ''

        self.prevtime       = time.time()
        self.heartbeat      = myconfig.HEARTBEAT

        # timezone string for current computer
        self.current_tzname = time.tzname[time.daylight]


        # build the filename
        self.build_filename()

    # build the file name
    # call this anytime that the filename attributes change
    def build_filename(self):
        self.filename = self.base_directory + self.logs_directory + 'eqlog_' + self.char_name + '_' + self.server_name + '.txt'

    #def build_filename(self):
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
    def open(self, author, seek_end = True):
        try:
            self.file = open(self.filename)
            if seek_end:
                self.file.seek(0, os.SEEK_END)

            self.author = author
            self.set_parsing()
            return True
        except:
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
            # return value m is either None of an object with information about the RE search
            m = re.match(trigger, trunc_line)
            if (m):
                # DEATH
                if 'You have been slain' in trunc_line:
                    mob = trunc_line.index('by ')+3, trunc_line.index("\n")
                    event = 'SelfDeath', trunc_line[mob[0]:mob[1]]
                # Roster Updates
                elif '<Legacy of Ik>' in trunc_line:
                    event = elf.update_roster(line[27:])
                # ZONE Tracking
                elif 'You have entered ' in trunc_line:
                    elf.myZone = trunc_line[17:trunc_line.index(".")]
                # Kill Parsing
                elif 'You have slain ' in trunc_line:
                    for target in self.target_list:
                        if target[0] in trunc_line:
                            event = 'SelfKill', target[0]
                # Loot Parsing
                elif 'You have looted a' in trunc_line:
                    for item in self.item_list:
                        if item[0] in trunc_line:
                            event = 'SelfLoot', item[0]
                elif 'has looted a' in trunc_line:
                    for item in self.item_list:
                        if item[0] in trunc_line:
                            event = 'TheyLoot', item[0], trunc_line[2:trunc_line.index(' ')]
                

        # only executes if loops did not return already
        return event
     
    # Build roster object / Update Roster
    def update_roster(self, whoStr):
        # Build character roster entry
        ind = whoStr.index('] '), whoStr.index(' ('), whoStr.index(' ')
        if '<Legacy of Ik> ZONE:' in whoStr:
            z1 = whoStr.index(': '), whoStr.index("\n")-2
            char = [whoStr[ind[0]+2:ind[1]], whoStr[ind[2]+1:ind[0]], whoStr[1:ind[2]], whoStr[z1[0]+2:z1[1]], 0, datetime.now(CST).strftime("%m/%d/%Y")]
            if char[0] in self.char_name:
                elf.myZone = char[3]
        else:
            char = [whoStr[ind[0]+2:ind[1]], whoStr[ind[2]+1:ind[0]], whoStr[1:ind[2]], elf.myZone, 0, datetime.now(CST).strftime("%m/%d/%Y")]
        # check roster for existing member
        cell = roster_Sheet.find(char[0])
        if [] != cell:
            # Update existing member
            print("\033[1;32;40m"+char[0]+" found.. updating roster!"+"\033[0;37;40m")
            roster_Sheet.update_row(cell[0].row, char[2:], col_offset=2)
            event = 'Update'
        else:
            # Add new member
            print("\033[1;32;40m"+char[0]+" not found.. adding to roster!"+"\033[0;37;40m")
            roster_Sheet.append_table(values=char)
            event = 'New', char[0]
        return event

# create the global instance of the log file class
elf     = EverquestLogFile()

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
            print(line, end = '')

            # does it match a trigger?
            event = elf.regex_match(line)
            if event:
                # Self Death
                if 'SelfDeath' in event:
                    await client.alarm('{} has fallen to {}! {}'.format(elf.char_name, event[1], random.choice(elf.taunt_death)[0]))
                # New Member
                elif 'New' in event:
                    await client.alarm('Bahaha! {} has pledged their life to the Legacy!'.format(event[1], random.choice(elf.taunt_NewMember)[0]))
                # Cool Items?
                elif 'Loot' in event[0]:
                    if 'Self' in event[0]:
                        await client.alarm('{} just looted a {}! Still nice and warm from the corpse!'.format(elf.char_name, event[1]))
                    if 'They' in event[0]:
                        await client.alarm('{} just looted a {}! Still warm from the corpse!'.format(event[2], event[1]))

        else:
            # check the heartbeat.  Has our tracker gone silent?
            elapsed_minutes = (now - elf.prevtime)/60.0
            if elapsed_minutes > elf.heartbeat:
                elf.prevtime = now
                print('Heartbeat Warning:  Tracker [{}] logfile has had no new entries in last {} minutes.  Is {} still online?'.format(elf.char_name, elf.heartbeat, elf.char_name))

            await asyncio.sleep(0.1)

    print('Parsing Stopped')


#################################################################################################


# define the client instance to interact with the discord bot

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

class myClient(commands.Bot):
    def __init__(self):
        commands.Bot.__init__(self, command_prefix = myconfig.BOT_COMMAND_PREFIX, intents = intents)

    # sound the alarm
    async def alarm(self, msg):
        logging_channel = client.get_channel(myconfig.DISCORD_SERVER_CHANNELID)
        await logging_channel.send(msg)

        print('Alarm:' + msg)


# create the global instance of the client that manages communication to the discord bot
client  = myClient()

#################################################################################################


#
# add decorator event handlers to the client instance
#

# on_ready
@client.event
async def on_ready():
    print('FOR IK!')
    print('Discord.py version: {}'.format(discord.__version__))

    print('Logged on as {}!'.format(client.user))
    print('App ID: {}'.format(client.user.id))

    await auto_start()


# on_message - catches everything, messages and commands
# note the final line, which ensures any command gets processed as a command, and not just absorbed here as a message
@client.event
async def on_message(message):
    author = message.author
    content = message.content
    channel = message.channel
    print('Content received: [{}] from [{}] in channel [{}]'.format(content, author, channel))
    await client.process_commands(message)


#################################################################################################


async def auto_start():
    #await client.connect()
    #await client.login(myconfig.BOT_TOKEN)
    #print("Auto start")
    #print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))
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
        print('Now parsing character log for: [{}]'.format(elf.char_name))
        print('Log filename: [{}]'.format(elf.filename))
        print('Parsing initiated by: [{}]'.format(elf.author))
        print('Heartbeat timeout (minutes): [{}]'.format(elf.heartbeat))

        # create the background processs and kick it off
        client.loop.create_task(parse())
    else:
        print('ERROR: Could not open character log file for: [{}]'.format(elf.char_name))
        print('Log filename: [{}]'.format(elf.filename))



# let's go!!
client.run(myconfig.BOT_TOKEN)
