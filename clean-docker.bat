@echo off
echo MPC Docker Cleanup Utility

:menu
echo.
echo Choose an option:
echo 1. Stop and remove Docker containers
echo 2. Remove Docker images
echo 3. Remove Docker volumes
echo 4. Reset everything (containers, images, volumes)
echo 5. Exit
echo.

set /p choice=Enter your choice (1-5): 

if "%choice%"=="1" goto clean_containers
if "%choice%"=="2" goto clean_images
if "%choice%"=="3" goto clean_volumes
if "%choice%"=="4" goto clean_all
if "%choice%"=="5" goto exit
echo Invalid choice. Please try again.
goto menu

:clean_containers
echo Stopping and removing Docker containers...
docker-compose down
echo.
echo Removing any remaining containers...
for /f "tokens=*" %%a in ('docker container ls -a -q -f "name=mpc-server"') do (
    docker container rm -f %%a 2>nul
)
for /f "tokens=*" %%a in ('docker container ls -a -q -f "name=visio-service"') do (
    docker container rm -f %%a 2>nul
)
echo Containers removed.
goto menu

:clean_images
echo Removing Docker images...
docker image rm -f mpc-server 2>nul
docker image rm -f visio-service 2>nul
echo Images removed.
goto menu

:clean_volumes
echo Removing Docker volumes...
docker volume prune -f
echo Volumes removed.
goto menu

:clean_all
echo Performing full cleanup...

echo Stopping and removing Docker containers...
docker-compose down
for /f "tokens=*" %%a in ('docker container ls -a -q -f "name=mpc-server"') do (
    docker container rm -f %%a 2>nul
)
for /f "tokens=*" %%a in ('docker container ls -a -q -f "name=visio-service"') do (
    docker container rm -f %%a 2>nul
)

echo Removing Docker images...
docker image rm -f mpc-server 2>nul
docker image rm -f visio-service 2>nul

echo Removing Docker volumes...
docker volume prune -f

echo.
echo All Docker resources have been cleaned up.
goto menu

:exit
echo Exiting...
exit /b 