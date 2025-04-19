# MPC Server Docker Setup

This document explains how to run the MPC server in a Docker container while keeping Visio-related functionality running locally on your Windows machine.

## Architecture

The setup consists of two components:

1. **MPC Server (Docker Container)**: Handles API requests, runs the server with SSE transport.
2. **Local Visio Service (Windows)**: Handles actual Visio operations using COM interfaces.

## Prerequisites

- Docker Desktop for Windows
- Python 3.12 installed locally
- Microsoft Visio installed locally
- Required Python packages installed locally: `fastapi`, `uvicorn`, `win32com`

## Running the Setup

### 1. Start the Local Visio Service

First, start the local Visio service that will handle actual Visio operations:

```bash
# From the project root directory
python run_visio_service.py
```

This will start a service on port 8051 that can handle Visio operations.

### 2. Start the MPC Server Container

Using Docker Compose:

```bash
# From the project root directory
docker-compose up -d
```

This will build the Docker image (if needed) and start the MPC server container.

### 3. Testing the Setup

You can test the setup by running one of the Visio scripts:

```bash
# From the project root directory
python test_connect.py
```

## Troubleshooting

- If you cannot connect to the Docker container from your scripts, ensure the port mapping is correct in docker-compose.yml.
- If the Docker container cannot communicate with the local Visio service, ensure your Docker Desktop settings allow host communication (`http://host.docker.internal:8051`).
- Check logs with `docker-compose logs mpc-server`.
- Make sure your local Visio service is running before starting the Docker container.

## Stopping the Services

```bash
# Stop the Docker container
docker-compose down

# Stop the local Visio service with Ctrl+C in its terminal
``` 