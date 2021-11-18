# Project 1999 - Legacy of Ik - Bot

Everquest Project 1999 log parsing bot that automates tracking of data for the Legacy of Ik guild.

v2021.0.1 was developed by [LevelUpLarry](https://www.leveluplarry.com) himself with the help of an anonymous developer.

v2021.0.2 was developed by [Thomas Silloway](https://github.com/ThomasSilloway) 

Special Thanks:
 - Vanifac
 - Grondarr

Connect with us in [LevelUpLarry's discord](https://discord.gg/SgKrGnM) in the `#legacy-of-ik` channel!

## Current Features
 - Send a message to [LevelUpLarry's discord](https://discord.gg/SgKrGnM) when your character dies

## Usage
- Start up & login to your Ik character
- Type in `/log` in your chat box
- Run the `dist\IkBot.exe`
- Follow the prompts to enter your character's name & locate the Everquest P99 directory on your harddrive
- And then next time you die, it will show up in the correct discord channel!

Note: To use on another character or if your EQ install changes, you can modify `config.ini` that is created next to the executable

## Aspirations

We are seeking development help for the following features:

- Start parsing immediately when IkBot.py is run instead of requiring the !start command 
- Add random "in character" lines from The Emperor for different events
- Allow the bot to be run via powershell with input parameters saved & passed via commandline to python for `BASE_DIRECTORY` and `DEFAULT_CHAR_NAME`
- Track achievements in discord for special items that are looted
- Send level up messages to the discord
- Add killed by info to the death messages
- Send a message when specific named NPCs die
- Automatically update the [tracking spreadsheet](https://docs.google.com/spreadsheets/d/1370kZTY0VaTuk82JBYjBFfBSlhyKK4-FO_TlxQtyNb4/edit?pli=1#gid=0) with new levels
  - Our current idea is to use the output of `/who all guild` to send updates 

Development Note:
 - Please do all testing in your own discord by modifying `myconfig.py` with your `PERSONAL_SERVER_NAME` and `PERSONAL_SERVER_POPID` before submitting a pull request

## Developer Setup

- Install python 3.7
- Ideally create a virtual environment (optional)
- Run command `pip install -r requirements.txt`

- Using your own discord user, create your own tracking bot.  You need to find the “discord developer portal” for this, and it’s a bit confusing, you will need an App and a Bot.  There are many YouTube videos that can walk you through this step.
- Create a discord server for yourself that you can use for testing.  You don’t need to do much with the test server other than maybe add a #pop channel
- Install the discord bot into your test discord server
- Update `src/myconfig.py` with your discord bot Token, discord server name & the channel ID (can be found via Discord with developer settings turned on)
- Run command `python src\IkBot.py`

## Build Instructions
- Run `Build.bat`
- Manually add `dist\IkBot.exe` to the repo

## Debug features
 - Save a log in this directory and allows replay & parsing of the existing log file
   - This is currently an unexplored feature
