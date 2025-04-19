@echo off
echo Starting MPC Servers...

echo Starting local Visio service...
start cmd /k "python run_visio_service.py"

echo Starting Docker container...
docker-compose up -d

echo Servers are starting. You can check their status with:
echo docker-compose ps
echo.
echo To stop the servers, run: stop-mpc-servers.bat
echo. 