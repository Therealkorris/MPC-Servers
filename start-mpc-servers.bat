@echo off
echo MPC Servers Setup

:menu
echo.
echo Choose an option:
echo 1. Run both services in Docker (requires Docker Desktop with Windows containers)
echo 2. Run MPC Server in Docker, Visio Service locally (recommended)
echo 3. Run both services locally
echo 4. Exit
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto docker_both
if "%choice%"=="2" goto docker_mpc_local_visio
if "%choice%"=="3" goto local_both
if "%choice%"=="4" goto exit
echo Invalid choice. Please try again.
goto menu

:docker_both
echo Starting both services in Docker...
docker-compose up -d
goto end

:docker_mpc_local_visio
echo Starting Visio Service locally...
start cmd /k "python run_visio_service.py"
echo.
echo Starting MPC Server in Docker...
docker-compose up -d mpc-server
goto end

:local_both
echo Starting Visio Service locally...
start cmd /k "python run_visio_service.py"
echo.
echo Starting MPC Server locally...
start cmd /k "python src/run_mpc.py --transport sse --host 0.0.0.0 --port 8050"
goto end

:exit
echo Exiting...
exit /b

:end
echo.
echo Services are starting. To stop them, run stop-mpc-servers.bat
echo. 