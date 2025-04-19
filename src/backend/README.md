# Visio AI Backend

This directory contains the backend server for the Visio AI project.

## Setup

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Server

You can start the server using the following command:

```
python main.py
```

### Command Line Options

- `--host`: Specify the host address (default: 127.0.0.1)
- `--port`: Specify the port number (default: 8000)
- `--reload`: Enable auto-reload for development (default: False)

Example:
```
python main.py --host 0.0.0.0 --port 5000 --reload
```

## Project Structure

- `main.py`: Entry point for the backend server
- `api/`: API routes and endpoints
- `models/`: Data models
- `services/`: Business logic and external service integrations
- `uploads/`: Directory for storing uploaded files (created automatically) 