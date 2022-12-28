from configparser import ConfigParser
from tkinter import Tk, filedialog
from json import dumps

CONFIG_NAME             = 'config.ini'
CONFIG_EQ_KEY           = 'EVERQUEST_DATA'
CONFIG_CHAR_NAME_KEY    = 'character_name'
CONFIG_GAME_DIR_KEY     = 'game_directory'

DEFAULT_CHAR_NAME       = 'NULL'

config_object = ConfigParser()

eqdata = None

try:
    config_object.read(CONFIG_NAME)
    eqdata = config_object[CONFIG_EQ_KEY]
except:
    pass

if eqdata is None:
    eqdata = {
        CONFIG_CHAR_NAME_KEY: input("Enter character name:").title()
    }

    print('Select where P99 Everquest is Installed ie C:\\Everquest')
    root = Tk()
    root.withdraw()  # Hide small window
    root.attributes('-topmost', True)  # Opened windows will be active. above all windows despite of selection
    eqdata[CONFIG_GAME_DIR_KEY] = filedialog.askdirectory(title="Everquest Directory")

    config_object[CONFIG_EQ_KEY] = eqdata
    with open(CONFIG_NAME, 'w') as conf:
        config_object.write(conf)

DEFAULT_CHAR_NAME = eqdata[CONFIG_CHAR_NAME_KEY]

# configure location of the everquest log files
BASE_DIRECTORY          = eqdata[CONFIG_GAME_DIR_KEY]


LOGS_DIRECTORY          = '\\logs\\'
SERVER_NAME             = 'P1999Green'

# used in hearbeat test.  Max number of minutes before bot begins warning that tracking toon may be offline
HEARTBEAT               = 60

# change this if you need to have multiple bots with same commands present on a server
BOT_COMMAND_PREFIX      = '!'

# Bot intents/permissions - new in 1.5
#BOT_INTENTS     = 

# token corresponds to the bot from discord developer portal
BOT_TOKEN               = ''

# some server ID's
DISCORD_SERVER_NAME         = ""
DISCORD_SERVER_CHANNELID    = 123  # Replace this with your ChannelID - Select it in Dev mode

# Google Sheets Key
GOOGLE_SHEETS_KEY = dumps({''})    # insert google sheets service account json
