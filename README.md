# Project 1999 - Legacy of Ik - Bot

Everquest Project 1999 log parsing bot that automates tracking of data for the Legacy of Ik guild.

v2021.0.1 was developed by [LevelUpLarry](https://www.leveluplarry.com) himself with the help of an anonymous developer, I am just hosting this for them.

Connect with us in [LevelUpLarry's discord](https://discord.gg/SgKrGnM) in the `#legacy-of-ik` channel!

## Current Features
 - Send a message to [LevelUpLarry's discord](https://discord.gg/SgKrGnM) when your character dies

## Usage

TODO

## Aspirations

We are seeking development help for the following features:

 - Add random "in character" lines from The Emperor for different events
 - Allow the bot to be run via powershell with input parameters saved & passed via commandline to python for `BASE_DIRECTORY` and `DEFAULT_CHAR_NAME`
 - Track achievements in discord for special items that are looted
 - Send level up messages to the discord
 - Add killed by info to the death messages
 - Automatically update the [tracking spreadsheet](https://docs.google.com/spreadsheets/d/1370kZTY0VaTuk82JBYjBFfBSlhyKK4-FO_TlxQtyNb4/edit?pli=1#gid=0) with new levels
   - Our current idea is to use the output of `/who all guild` to send updates 

Development Note:
 - Please do all testing in your own discord by modifying `myconfig.py` with your `PERSONAL_SERVER_NAME` and `PERSONAL_SERVER_POPID` before submitting a pull request

## Debug features
 - Save a log in this directory and allows replay & parsing of the existing log file
   - This is currently an unexplored feature
