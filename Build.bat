@ECHO OFF

DEL config.ini
DEL src\config.ini
pyinstaller --onefile src\IkBot.py
