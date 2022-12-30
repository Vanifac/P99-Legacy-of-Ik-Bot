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
BOT_TOKEN               = 'OTA5MTk5MTE1MjQ4ODg5OTQ2.G8swX-.pYZBgsuzvJ5ukPNkbpYZFHdCvT_shnoCc3kDW4'

# some server ID's
DISCORD_SERVER_NAME         = "LevelUpDiscord"
DISCORD_SERVER_CHANNELID    = 778384563373473793  # Replace this with your ChannelID - Select it in Dev mode

# Google Sheets Key
GOOGLE_SHEETS_KEY = dumps({
    "type": "service_account",
    "project_id": "ikbot-371601",
    "private_key_id": "84fc7b5a604f7d7587ca4715175ff43a071a5ee7",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDnpWMp65/RcCIF\nDosP+PsfcUbSQrGzqIjwUzkl4piDC5RGInoQ33dc9l8kFKdn63p71xSVGRC+x66N\nq9jkpBpgn9HtMbHJTSU5SLLL0Ba4XRz8ijY9VcNrI3P1XvT4aqlCzgQrcFgueJy5\nmKNSflIhXeZo2MKaJfaY6mZFWIRW0XT5YS1o5p1CryZuS/JeasKx7sKAH4L8pfhM\n99evGwlFUVzxzbhM7coLCoaPZOVGK8qRGauMW3j0HLZWH4PhgALS/FqLjgJ/LJXJ\nkBaJcF/Ol1wL5hRuM5ANTUFauylaHMKINCfEINnria7RkzFm1xQsU7xVC1v7F/A8\nhJKQUHwdAgMBAAECggEAAg+HlUziTBOqSc86T3cQjNQOJDqxp/580V58KKkeYDQP\nKpyN526Fek86w3BnmNYQbd+Y8EabzoaqN9pqgIYxMeDaFjkV8st75EmQRZ3hRdyW\nMGzuVJdZuK9FDc69cSRJwy1f/h7uueMayc/gzBARnPhf31jmSkbCLdQP+tfxvW/1\nO385G9W0u2xgOy13uQyA20Fjn6VDswMo3WX91zwTrEL86OmHcK33nKp0xuNoJ+t4\nP/3GATTJmGn5A1COgObMT2R1KD/QYkPWg2AKwmLnTEljx42+Ga/+jlW6jyKgGr9L\nThes/6tOchG0Fz9IYgPPdG7k/cHv+mm8Vt66WHAnpQKBgQD82I7JeEMF2HYxaKFo\nKT/qxQBfjNlG/qHdlbTK59xsVcDruslNOS0JB9N8IhKo/fNMjVMrqQKaHtZlLWah\nm1wGq1zD//2Dla2KHOE9xM2ztyrRQtjmR4EqpOA3dDT889PLQC3QUAdGkxLTM7wW\nd0cVmygQ1ikKQeyBn5++k8btIwKBgQDqiSEp88tNJh0Bg2IheSE5g2/5/PvfqHOx\nFbuzGdVEhsQug6sf5eglSlISLgJMYrtFm0HkA35IIW4Woap5ID6teIVweLIHcKTo\nA2Hxm/JKFj5oHuMthfEU6BTTElqYshNfLiA1faBU08nHcHK2P9WbOMGokx1Gl3vl\nyMZvW5qlvwKBgQD6D3bP3Ad1DYp+/Pq8mCclmaXv2c29P/F3wypljf/aiMjemgGi\nRQy8JKhM2SnZRibMK+z4fhMbt6nTsJ4S8CKIWgvJsC/aZjqWIE/HFg9WUK2g/dqj\njE47jYpObbhF/yMUnalxnuRDMQtqI30+PsLnpGZwmE1IXsB3xhVnlqEjPwKBgQCt\nJLtE+2Q0+lQjj9jcGU575Rq/lRJlFTkDnKXLHOEjC9K8/BtTGyl8jhd0sF6mAaV7\nR5knOaT6nyNktcjiTvm2muj4FUJo17IGTqj580S1iSJdP6A7NUy7QHJPOJeFbsF6\nXNUOaEX7Gbc28z7caNfLFeVyC9lrCd4/zy8feqL6hQKBgQCFIlUCckOmHd4Rzf8I\nlgHN6jirOdDK9CwUdI2OnD7dCc7KDyulqIqBF+Lu/B2qDch1YMLEmEKRTs6W4Z2S\nqKLZ6IPGFljFVbh75FO1C41or838PxDE3sYuKS5aa1wLy2j7EhpFwH2RzUH+Uex5\nE9hy/lygx2It0F2xrUwKyeql+g==\n-----END PRIVATE KEY-----\n",
    "client_email": "ikbot-45@ikbot-371601.iam.gserviceaccount.com",
    "client_id": "115165225010518352367",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/ikbot-45%40ikbot-371601.iam.gserviceaccount.com"
    })
