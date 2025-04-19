@echo off
echo MPC Docker Quick Cleanup

REM Detect container mode
echo Detecting Docker container mode...
docker version --format "{{.Server.Os}}" | findstr /C:"windows" >nul
if %errorlevel% equ 0 (
    echo Running in Windows container mode.
    set CONTAINER_MODE=windows
) else (
    echo Running in Linux container mode.
    set CONTAINER_MODE=linux
)

echo.
echo Stopping and removing Docker Compose services...
docker-compose down 2>nul
docker-compose -f docker-compose.full.yml down 2>nul

echo.
echo Stopping and removing mpc-server container...
docker stop mpc-server 2>nul
docker rm -f mpc-server 2>nul

echo Stopping and removing visio-service container...
docker stop visio-service 2>nul
docker rm -f visio-service 2>nul

echo.
echo Checking for running containers...
for /f "tokens=*" %%c in ('docker ps -a -q') do (
    echo Found container: %%c
    docker rm -f %%c 2>nul
)

echo.
echo Cleanup complete.

echo.
echo You can now run start-mpc-servers.bat
echo. 