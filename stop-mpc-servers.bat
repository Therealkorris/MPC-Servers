@echo off
echo MPC Servers Shutdown

:menu
echo.
echo Choose what to stop:
echo 1. Stop Docker containers only
echo 2. Stop local services only
echo 3. Stop all services (Docker and local)
echo 4. Exit
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto stop_docker
if "%choice%"=="2" goto stop_local
if "%choice%"=="3" goto stop_all
if "%choice%"=="4" goto exit
echo Invalid choice. Please try again.
goto menu

:stop_docker
echo Stopping Docker containers...
docker-compose down
goto end

:stop_local
echo Stopping local services...
taskkill /F /FI "WINDOWTITLE eq python run_visio_service.py*" /T
taskkill /F /FI "WINDOWTITLE eq python src/run_mpc.py*" /T
goto end

:stop_all
echo Stopping Docker containers...
docker-compose down
echo.
echo Stopping local services...
taskkill /F /FI "WINDOWTITLE eq python run_visio_service.py*" /T
taskkill /F /FI "WINDOWTITLE eq python src/run_mpc.py*" /T
goto end

:exit
echo Exiting...
exit /b

:end
echo.
echo All services have been stopped.
echo. 