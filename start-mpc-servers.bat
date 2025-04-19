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

REM Check if images exist
docker image inspect mpc-server >nul 2>&1
if %errorlevel% neq 0 (
    echo Building MPC Server Docker image...
    docker build -t mpc-server -f Dockerfile .
    if not exist mpc-server (
        echo Error building MPC Server image. Image not created.
        goto menu
    )
)

docker image inspect visio-service >nul 2>&1
if %errorlevel% neq 0 (
    echo Building Visio Service Docker image...
    docker build -t visio-service -f Dockerfile.visio .
    if not exist visio-service (
        echo Error building Visio Service image. Image not created.
        goto menu
    )
)

echo Starting Docker services...
docker-compose up -d
if %errorlevel% neq 0 (
    echo Error starting Docker services. See error message above.
    goto menu
)
echo Docker services started successfully.
goto end

:docker_mpc_local_visio
echo Starting Visio Service locally...
start cmd /k "python run_visio_service.py"
echo.

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

echo Starting MPC Server in Docker...
docker-compose up -d mpc-server
if %errorlevel% neq 0 (
    echo Error starting MPC Server. See error message above.
    goto menu
)
echo MPC Server started successfully in Docker.
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
echo To test if everything is working, run:
echo python test-docker-setup.py
echo. 