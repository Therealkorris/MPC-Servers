# MPC Visio

This is an MPC (Messenger Communication Protocol) server for Microsoft Visio, providing AI-powered features for Visio diagrams.

## Setup

1. Install Python 3.9 or newer if not already installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the MPC Server

You can run the MPC server in two modes:

### Backend-only mode

This mode starts only the FastAPI backend server:

```
python src/run_mpc.py --backend-only
```

### Full MPC Server

This mode starts the MPC server with SSE transport:

```
python src/run_mpc.py --transport sse
```

### Using Make

You can also use the provided Makefile:

```
# Install dependencies
make setup

# Run tests
make test

# Run backend only
make backend

# Run MPC server
make mpc
```

### Using Docker

You can run the MPC server in Docker using the provided Dockerfile and docker-compose.yml:

```
# Build the Docker image
make docker-build

# Run the Docker container
make docker-run

# Stop the Docker container
make docker-stop
```

Alternatively, you can use Docker Compose directly:

```
# Build and run
docker compose up -d

# Stop
docker compose down
```

Note: The Docker container will not have access to Microsoft Visio. It's primarily intended for running the backend services that don't require direct Visio interaction. For full functionality including Visio automation, run the server directly on your Windows machine.

## MPC Configuration

To connect to this MPC server from a client application, use the following configuration:

```json
{
  "mcpServers": {
    "visio": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

Note for Windsurf users: Use `serverUrl` instead of `url` in your configuration:

```json
{
  "mcpServers": {
    "visio": {
      "transport": "sse",
      "serverUrl": "http://localhost:8050/sse"
    }
  }
}
```

## Features

- Visio file analysis
- AI-powered diagram generation
- AI-powered diagram modification
- Ask AI about Visio diagrams

## API Documentation

When running the backend server, you can access the Swagger documentation at:

```
http://localhost:8000/docs
```

## Running Tests

To run the tests:

```
cd src/backend
python run_tests.py
``` 