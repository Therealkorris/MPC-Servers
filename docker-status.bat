@echo off
echo MPC Docker Status Check
echo ====================
echo.

REM Check Docker is running
echo Checking if Docker is running...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop first.
    exit /b 1
) else (
    echo [OK] Docker is running.
)

REM Detect container mode
echo.
echo Checking Docker container mode...
docker version --format "{{.Server.Os}}" | findstr /C:"windows" >nul
if %errorlevel% equ 0 (
    echo [INFO] Running in Windows container mode.
    set CONTAINER_MODE=windows
) else (
    echo [INFO] Running in Linux container mode.
    set CONTAINER_MODE=linux
)

REM List running containers
echo.
echo Checking for running MPC containers...
docker ps --filter "name=mpc-server" --filter "status=running" | findstr "mpc-server" >nul
if %errorlevel% equ 0 (
    echo [OK] MPC Server container is running.
    docker ps --filter "name=mpc-server" --format "ID: {{.ID}}  Name: {{.Names}}  Ports: {{.Ports}}  Status: {{.Status}}"
    echo.
    echo To view logs: docker logs mpc-server
) else (
    echo [WARNING] MPC Server container is not running.
)

docker ps --filter "name=visio-service" --filter "status=running" | findstr "visio-service" >nul
if %errorlevel% equ 0 (
    echo [OK] Visio Service container is running.
    docker ps --filter "name=visio-service" --format "ID: {{.ID}}  Name: {{.Names}}  Ports: {{.Ports}}  Status: {{.Status}}"
    echo.
    echo To view logs: docker logs visio-service
) else (
    echo [INFO] Visio Service container is not running. (This is normal if using option 2)
)

REM Check ports
echo.
echo Checking if the required ports are in use...
netstat -ano | findstr ":8050" >nul
if %errorlevel% equ 0 (
    echo [OK] Port 8050 (MPC Server) is in use.
) else (
    echo [WARNING] Port 8050 (MPC Server) is not in use. MPC Server may not be running correctly.
)

netstat -ano | findstr ":8051" >nul
if %errorlevel% equ 0 (
    echo [OK] Port 8051 (Visio Service) is in use.
) else (
    echo [WARNING] Port 8051 (Visio Service) is not in use. Visio Service may not be running correctly.
)

REM Print Docker images
echo.
echo Available Docker images:
docker images --format "{{.Repository}}:{{.Tag}}" | findstr /C:"mpc-server" /C:"visio-service"

echo.
echo Status check complete.
echo. 