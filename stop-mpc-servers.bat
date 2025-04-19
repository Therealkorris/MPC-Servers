@echo off
echo Stopping MPC Servers...

echo Stopping Docker container...
docker-compose down

echo Stopping local Visio service...
taskkill /F /FI "WINDOWTITLE eq run_visio_service.py*" /T

echo Servers have been stopped.
echo. 