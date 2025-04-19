# MPC Server Docker Setup

This document explains how to run the MPC server in Docker containers while keeping Visio-related functionality accessible.

## Architecture

The setup consists of two components:

1. **MPC Server (Linux Container)**: Handles API requests, runs the server with SSE transport. Forwards Visio-related operations to the local Visio service.

2. **Visio Service (Local or Windows Container)**: Handles actual Visio operations using COM interfaces.

## Prerequisites

- Docker Desktop for Windows
- Python 3.12 installed locally
- Microsoft Visio installed locally
- Required Python packages installed locally: `fastapi`, `uvicorn`, `win32com`

## Options for Running

You can run the setup in two different configurations:

### Option 1: MPC Server in Docker, Visio Service locally

This is the simplest approach and recommended if you just want to run the MPC server in the background.

#### 1. Start the Local Visio Service

```bash
# From the project root directory
python run_visio_service.py
```

This will start a service on port 8052 that can handle Visio operations.

#### 2. Start the MPC Server Container

```bash
# From the project root directory
docker-compose up -d
```

This will run the MPC server in a Docker container, which forwards Visio requests to your local machine.

### Option 2: Both Services in Docker (Experimental)

This requires Docker to run Windows containers, which may be challenging to set up.

1. Switch Docker Desktop to Windows containers
2. Uncomment the visio-service section in docker-compose.yml
3. Run both services:

```bash
docker-compose up -d
```

Note: This option is experimental and requires Microsoft Visio to be installed in the Windows container, which may have licensing implications.

## Using the Batch Files

For convenience, you can use the provided batch files:

- `start-mpc-servers.bat`: Starts both the local Visio service and the MPC server container
- `stop-mpc-servers.bat`: Stops both services

## Running the Visio Service Without a Visible Window

By default, the Visio service opens a command window when it runs. If you prefer to have it run invisibly, there are two options:

1. **Using pythonw.exe (Simple)**: The updated batch files now use pythonw.exe to run the service without a visible window.

2. **As a Windows Service (Advanced)**: For a more permanent solution, you can install the Visio service as a Windows service:
   - Run `install_service.bat` to install
   - Control the service with `python install_as_service.py [start|stop|remove]`

See `HIDDEN_SERVICE.md` for more details on these options.

## Testing the Setup

You can test the setup by running one of the Visio scripts:

```bash
# From the project root directory
python test_connect.py
```

## Troubleshooting

- If you cannot connect to the Docker container from your scripts, ensure the port mapping is correct in docker-compose.yml.
- If the Docker container cannot communicate with the local Visio service, ensure your Docker Desktop settings allow host communication (`http://host.docker.internal:8052`).
- Check logs with `docker-compose logs mpc-server`.
- Make sure your local Visio service is running before starting the Docker container.
- For Windows containers, ensure proper licensing and installation of Microsoft Visio in the container.

## File Paths

The Docker containers have access to the local file system through volume mounts:

- `/app/examples` in the container maps to `./examples` on your host machine
- This allows the containers to access Visio files in your local examples directory 