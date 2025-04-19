@echo off
echo Simple Docker Startup for MPC Servers
echo ===================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Stopping any existing containers...
docker stop mpc-server visio-service 2>nul
docker rm -f mpc-server visio-service 2>nul

echo Creating network if it doesn't exist...
docker network inspect mpc-network >nul 2>&1 || docker network create --driver bridge mpc-network

echo Starting Visio Service locally...
start cmd /k "python run_visio_service.py"
timeout /t 3 >nul

echo Starting MPC Server in Docker...
docker run -d --name mpc-server -p 8050:8050 -e LOCAL_VISIO_SERVICE=http://host.docker.internal:8051 -e PYTHONUNBUFFERED=1 mpc-server

echo.
echo MPC Server should be accessible at: http://localhost:8050
echo Visio Service should be accessible at: http://localhost:8051
echo.
echo To test if the services are working, run:
echo   python test_visio.py
echo.
echo To stop the services:
echo   docker stop mpc-server
echo   (Close the Visio Service command window)
echo. 