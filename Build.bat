@ECHO OFF

DEL config.ini
DEL src\config.ini
DEL dist\config.ini
DEL dist\IkBot.exe
pyinstaller --onefile src\IkBot.py