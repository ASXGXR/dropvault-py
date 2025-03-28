@echo off
cd /d "C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py"

start /min cmd /k "python backend/server.py"
start /min cmd /k "http-server frontend -p 5500"
start /min cmd /k "python backend/main.py"