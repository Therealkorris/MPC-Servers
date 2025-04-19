@echo off
echo Stopping MPC Servers...

echo Stopping Docker container...
docker-compose down

echo Stopping local Visio service...
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE ne Administrator:*"

echo Servers have been stopped.
echo. 