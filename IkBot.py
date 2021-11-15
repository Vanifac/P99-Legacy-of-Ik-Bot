import threading
import asyncio
import time
import discord
import random
import os
import re

from discord.ext import commands

# import the customized settings and file locations etc, found in myconfig.py
import myconfig



# allow for testing, by forcing the bot to read an old log file for the VT and VD fights
TEST_BOT                = False
#TEST_BOT                = True




#################################################################################################


#
# class to encapsulate log file operations
#
class EverquestLogFile:

    # list of targets which this log file watches for
    target_list = [
        #'carrion queen',
        #'burynai cutter',
		#'Burynaibane Spider',
		#'a scourgetail scorpion',
		#'Grachnist the Destroyer',
		#'Pit Fighter Dob',
		#'Iksar Bandit Lord',
		#'Iksar Dakoit',
            
        ]

    # list of regular expressions matching log files indicating the 'target' is spawned and active
    trigger_list = [
        '^(\w)+ have been slain by',
		'^(\w)+ have been slain',
        # looted items could be their own array
		#'^(\w)+ have gained a level! Welcome to level',
		#'^(\w)+ has looted a Blockcutter Gloves',
		#'^(\w)+ has looted a Polished Stone Anklet',
		#'^(\w)+ has looted a Dakoit Coin Purse',
		#'^(\w)+ has looted a Carrion Beetle Leggings',
		#'^(\w)+ has looted a Carrion Queen Liver',
		#'^(\w)+ has looted a Scourgetail Bracer',
		#'^(\w)+ has looted a Scourgetail Whip',
		#'^(\w)+ has looted a Scaled Prowler Belt',

		]

    looted_items = [
        'BlockCutter Gloves'
    ]

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
        # cut off the leading date-time stamp info
        trunc_line = line[27:]

        # walk thru the target list and trigger list and see if we have any match
        for trigger in self.trigger_list:
            # return value m is either None of an object with information about the RE search
            m = re.match(trigger, trunc_line)
            if (m):
                return trunc_line

        # TODO: Loop through looted items to find matches
        # if item in trunc_line

        # only executes if loops did not return already
        return None

# create the global instance of the log file class
elf     = EverquestLogFile()

#################################################################################################


# the background process to parse the log files
#
# override the run method
#
async def parse():

    print('Parsing Started')

    # process the log file lines here
    while elf.is_parsing() == True:

        # read a line
        line = elf.readline()
        now = time.time()
        if line:
            elf.prevtime = now
            print(line, end = '')

            # does it match a trigger?
            target = elf.regex_match(line)
            if target:

                # sound the alarm
                await client.alarm('{} has fallen! A failure to the Empire!'.format(myconfig.DEFAULT_CHAR_NAME))
                
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

class myClient(commands.Bot):
    def __init__(self):
        commands.Bot.__init__(self, command_prefix = myconfig.BOT_COMMAND_PREFIX)

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



# TODO: Probably can delete all of the client commands now that it runs automagically


# ping command
@client.command()
async def ping(ctx):
    print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))
    await ctx.send('Latency = {} ms'.format(round(client.latency*1000)))



# firedrill command
# test the ability to send a message to the #logging channel
@client.command(aliases = ['fd', '911'])
async def firedrill(ctx):
    print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))
    await client.alarm('This is a test.  This is only a test.')



# show all the triggers being monitored
@client.command()
async def triggers(ctx):
    print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))

    # list all the target mobs
    await ctx.send('*Target Mobs:*')
    for target in elf.target_list:
        await ctx.send('|        {}'.format(target))

    # list all the triggers
    await ctx.send('*Triggers:*')
    for trigger in elf.trigger_list:
        await ctx.send('|        {}'.format(trigger))



# start command
@client.command(aliases = ['go'])
async def start(ctx, charname = None):
    print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))

    # already parsing?
    if elf.is_parsing():
        await ctx.send('Already parsing character log for: [{}]'.format(elf.char_name))
        await ctx.send('Log filename: [{}]'.format(elf.filename))
        await ctx.send('Parsing initiated by: [{}]'.format(elf.author))
        
    else:
        # new log file name get passed?
        if charname:
            elf.char_name = charname
        else:
            elf.char_name = myconfig.DEFAULT_CHAR_NAME
        elf.build_filename()

        # open the log file to be parsed
        # allow for testing, by forcing the bot to read an old log file for the VT and VD fights
        if TEST_BOT == False:
            # start parsing.  The default behavior is to open the log file, and begin reading it from tne end, i.e. only new entries
            rv = elf.open(ctx.message.author)

        else:
            # use a back door to force the system to read files from the beginning that contain VD / VT fights to test with
            elf.filename = elf.base_directory + elf.logs_directory + 'test_fights.txt'

            # start parsing, but in this case, start reading from the beginning of the file, rather than the end (default)
            rv = elf.open(ctx.message.author, seek_end = False)


        # if the log file was successfully opened, then initiate parsing
        if rv:
            # status message
            await ctx.send('Now parsing character log for: [{}]'.format(elf.char_name))
            await ctx.send('Log filename: [{}]'.format(elf.filename))
            await ctx.send('Parsing initiated by: [{}]'.format(elf.author))
            await ctx.send('Heartbeat timeout (minutes): [{}]'.format(elf.heartbeat))

            # create the background processs and kick it off
            client.loop.create_task(parse())
        else:
            await ctx.send('ERROR: Could not open character log file for: [{}]'.format(elf.char_name))
            await ctx.send('Log filename: [{}]'.format(elf.filename))



# stop command
@client.command()
async def stop(ctx):
    print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))

    if elf.is_parsing():

        # only the person who started the log can close it
        if elf.author == ctx.message.author:
            # stop parsing
            elf.close()
            await ctx.send('Stopped parsing character log for: [{}]'.format(elf.char_name))
        else:
            await ctx.send('Error: Parsing can only be stopped by the same person who started it.  Starter: [{}], !stop requestor [{}]'.format(elf.author, ctx.message.author))

    else:
        await ctx.send('Not currently parsing')



# status command
@client.command()
async def status(ctx):
    print('Command received: [{}] from [{}]'.format(ctx.message.content, ctx.message.author))

    if elf.is_parsing():
        await ctx.send('Parsing character log for: [{}]'.format(elf.char_name))
        await ctx.send('Log filename: [{}]'.format(elf.filename))
        await ctx.send('Parsing initiated by: [{}]'.format(elf.author))
        await ctx.send('Heartbeat timeout (minutes): [{}]'.format(elf.heartbeat))
    else:
        await ctx.send('Not currently parsing')


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




