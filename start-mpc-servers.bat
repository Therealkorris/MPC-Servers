@echo off
echo MPC Servers Setup

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not running. Attempting to start Docker...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Waiting for Docker to start...
    timeout /t 20
    
    REM Check again if Docker is running
    docker info >nul 2>&1
    if %errorlevel% neq 0 (
        echo Docker is still not running. Please start Docker Desktop manually.
        echo Press any key to continue once Docker is running...
        pause >nul
    ) else (
        echo Docker started successfully.
    )
)

REM Track if Visio service is already running to avoid starting it twice
set VISIO_SERVICE_RUNNING=0

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

:check_and_switch_to_windows
REM Check if we're in Windows container mode
docker version --format "{{.Server.Os}}" | findstr /C:"windows" >nul
if %errorlevel% neq 0 (
    echo Detected Linux containers. Switching to Windows containers...
    echo This may take a moment and Docker might restart.
    
    REM Use PowerShell to switch container mode
    powershell -Command "& 'C:\Program Files\Docker\Docker\DockerCli.exe' -SwitchDaemon"
    
    REM Wait for Docker to restart
    echo Waiting for Docker to restart in Windows container mode...
    timeout /t 15
    
    REM Verify switch worked
    docker version --format "{{.Server.Os}}" | findstr /C:"windows" >nul
    if %errorlevel% neq 0 (
        echo Failed to switch to Windows containers.
        echo Please switch manually: right-click Docker icon, select "Switch to Windows containers..."
        echo Press any key when ready...
        pause >nul
    ) else (
        echo Successfully switched to Windows containers.
    )
)
goto :eof

:docker_both
REM Switch to Windows containers if needed
call :check_and_switch_to_windows

echo Starting both services in Docker...
echo.
echo Using Windows containers for Visio service...

REM Clean up any existing containers first
echo Stopping and removing any existing containers...
docker-compose -f docker-compose.full.yml down 2>nul
docker stop mpc-server visio-service 2>nul
docker rm -f mpc-server visio-service 2>nul

REM Create the Docker network if it doesn't exist
echo Ensuring the Docker network exists...
docker network inspect mpc-network >nul 2>&1 || docker network create --driver bridge mpc-network

REM Build the Docker images
echo Building Docker images...
docker build -t mpc-server -f Dockerfile.win . || (
    echo MPC Server build failed, but will continue if image exists
)
docker build -t visio-service -f Dockerfile.visio . || (
    echo Visio Service build failed, but will continue if image exists
)

REM Check if images exist regardless of build success
echo Verifying images exist...
docker image inspect mpc-server >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: MPC Server image does not exist. Cannot continue.
    goto menu
) else (
    echo MPC Server image verified.
)

docker image inspect visio-service >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Visio Service image does not exist. Cannot continue.
    goto menu
) else (
    echo Visio Service image verified.
)

echo Starting Docker services (both MPC Server and Visio Service)...
docker-compose -f docker-compose.full.yml up -d

REM Verify containers are running
echo Verifying containers are running...
timeout /t 3 >nul
docker ps | findstr "mpc-server" >nul
if %errorlevel% neq 0 (
    echo Warning: MPC Server container not found in running containers.
    echo Attempting to start manually...
    docker run -d --name mpc-server --network mpc-network -p 8050:8050 -e LOCAL_VISIO_SERVICE=http://visio-service:8051 mpc-server
) else (
    echo MPC Server container is running.
)

docker ps | findstr "visio-service" >nul
if %errorlevel% neq 0 (
    echo Warning: Visio Service container not found in running containers.
    echo Attempting to start manually...
    docker run -d --name visio-service --network mpc-network -p 8051:8051 visio-service
) else (
    echo Visio Service container is running.
)

echo Docker services started. To see logs, run: docker logs mpc-server
goto end

:docker_mpc_local_visio
REM Only start Visio service if it's not already running
if %VISIO_SERVICE_RUNNING%==0 (
    echo Starting Visio Service locally...
    start cmd /k "python run_visio_service.py"
    set VISIO_SERVICE_RUNNING=1
    echo.
) else (
    echo Visio Service is already running.
    echo.
)

echo Checking if MPC Server Docker image exists...
docker image inspect mpc-server >nul 2>&1
if %errorlevel% neq 0 (
    echo Building MPC Server Docker image...
    docker build -t mpc-server -f Dockerfile .
)

REM Verify image now exists
docker image inspect mpc-server >nul 2>&1
if %errorlevel% neq 0 (
    echo Error building MPC Server image. Image not created.
    goto menu
) else (
    echo MPC Server image built or already exists.
)

echo Stopping any existing MPC server containers...
docker stop mpc-server >nul 2>&1
docker rm -f mpc-server >nul 2>&1

echo Starting MPC Server in Docker...
docker run -d --name mpc-server -p 8050:8050 -e LOCAL_VISIO_SERVICE=http://host.docker.internal:8051 mpc-server
if %errorlevel% neq 0 (
    echo Error starting MPC Server with 'docker run'. Trying with docker-compose...
    docker-compose up -d mpc-server
    
    if %errorlevel% neq 0 (
        echo All attempts to start MPC Server failed. See error messages above.
        goto menu
    ) else (
        echo MPC Server started successfully with docker-compose.
    )
) else (
    echo MPC Server container started successfully with 'docker run'.
)
goto end

:local_both
REM Only start Visio service if it's not already running
if %VISIO_SERVICE_RUNNING%==0 (
    echo Starting Visio Service locally...
    start cmd /k "python run_visio_service.py"
    set VISIO_SERVICE_RUNNING=1
    echo.
) else (
    echo Visio Service is already running.
    echo.
)

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
echo To test if everything is working, run:
echo python test-docker-setup.py
echo. 