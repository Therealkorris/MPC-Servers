# MPC Server Docker Setup

This document explains how to run the MPC server in a Docker container while keeping Visio operations working properly.

## Architecture Options

There are three setup options available:

1. **Full Docker Setup**: Both MPC Server and Visio Service run in Docker containers
   - Requires Docker Desktop with Windows containers support
   - Limited Visio functionality due to containerization constraints

2. **Hybrid Setup (Recommended)**: MPC Server in Docker, Visio Service runs locally
   - MPC Server runs in a Linux container
   - Visio Service runs directly on your Windows host with full access to Visio
   - Communications occur via localhost network

3. **Fully Local Setup**: Both services run directly on your Windows host
   - Simplest setup if you don't need Docker isolation
   - Both services have full access to local resources

## Prerequisites

- Docker Desktop for Windows
- Python 3.12 installed locally
- Microsoft Visio installed locally
- Required Python packages installed locally: `fastapi`, `uvicorn`, `win32com`

## Running the Services

### Quick Start (Using Batch Scripts)

The simplest way to start the services is using the provided batch script:

```bash
# Start the services with options menu
start-mpc-servers.bat
```

This will show a menu where you can choose how to run the services.

To stop the services:

```bash
# Stop the services with options menu
stop-mpc-servers.bat
```

### Manual Setup

If you prefer to start services manually:

#### Option 1: Full Docker Setup

```bash
# Start both services in Docker
docker-compose up -d
```

#### Option 2: Hybrid Setup (Recommended)

```bash
# Start the local Visio service
python run_visio_service.py

# In another terminal, start the MPC Server container
docker-compose up -d mpc-server
```

#### Option 3: Fully Local Setup

```bash
# Start the local Visio service
python run_visio_service.py

# In another terminal, start the MPC Server locally
python src/run_mpc.py --transport sse --host 0.0.0.0 --port 8050
```

## Testing the Setup

You can test the setup by running one of the Visio scripts:

```bash
# From the project root directory
python test_connect.py
```

## Port Configuration

- MPC Server: Port 8050
- Visio Service: Port 8051

## Troubleshooting

- **Docker Containers Not Starting**: Check Docker logs with `docker-compose logs`
- **Container Can't Reach Local Service**: Ensure Docker Desktop settings allow host.docker.internal
- **Visio Service Errors**: Ensure Visio is properly installed and accessible
- **Visio Not Visible**: If using the Visio service locally, opening the Visio file may work better
- **Windows Containers Issues**: If using Option 1, ensure Windows containers are enabled in Docker Desktop

## Docker Switching Between Linux/Windows Containers

If you need to switch between Linux and Windows containers:

1. Right-click Docker Desktop icon in the system tray
2. Select "Switch to Windows containers..." or "Switch to Linux containers..."
3. Allow Docker to restart

Note: Option 1 requires Windows containers, while Option 2 works with Linux containers (recommended). 