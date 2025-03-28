@echo off
echo Killing backend server, frontend http-server, and backend main...

taskkill /IM python.exe /F
taskkill /IM node.exe /F

REM Optional: only kills terminals opened by 'start cmd'
taskkill /IM cmd.exe /F