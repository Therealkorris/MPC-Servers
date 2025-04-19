@echo off
echo MPC Servers Shutdown

:menu
echo.
echo Choose what to stop:
echo 1. Stop Docker containers (both MPC Server and Visio Service)
echo 2. Stop Docker MPC Server only
echo 3. Stop local services only
echo 4. Stop all services (Docker and local)
echo 5. Exit
echo.

set /p choice=Enter your choice (1-5): 

if "%choice%"=="1" goto stop_docker_all
if "%choice%"=="2" goto stop_docker_mpc
if "%choice%"=="3" goto stop_local
if "%choice%"=="4" goto stop_all
if "%choice%"=="5" goto exit
echo Invalid choice. Please try again.
goto menu

:stop_docker_all
echo Stopping all Docker containers...
docker-compose -f docker-compose.full.yml down
echo All Docker containers stopped.
goto end

:stop_docker_mpc
echo Stopping Docker MPC Server...
docker-compose down
echo Docker MPC Server stopped.
goto end

:stop_local
echo Stopping local services...
taskkill /F /FI "WINDOWTITLE eq python run_visio_service.py*" /T
taskkill /F /FI "WINDOWTITLE eq python src/run_mpc.py*" /T
goto end

:stop_all
echo Stopping all Docker containers...
docker-compose -f docker-compose.full.yml down
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