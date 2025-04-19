@echo off
echo MPC Server Docker Runner

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

echo.
echo Starting Visio Service locally...
start cmd /k "python run_visio_service.py"
echo.

echo Building MPC Server Docker image...
docker build -t mpc-server -f Dockerfile .
if %errorlevel% neq 0 (
    echo Error building MPC Server image. See error message above.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo Running MPC Server in Docker...
docker run --name mpc-server -p 8050:8050 -e LOCAL_VISIO_SERVICE=http://host.docker.internal:8051 --rm mpc-server
if %errorlevel% neq 0 (
    echo Error running MPC Server. See error message above.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo.
echo MPC Server Docker container stopped.
echo Press any key to exit...
pause >nul 