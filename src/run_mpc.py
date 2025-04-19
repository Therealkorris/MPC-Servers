#!/usr/bin/env python3
"""
MPC-Visio: Main entry point for running the MPC server
"""
import argparse
import logging
import os
import sys
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

def start_backend_server(host, port, reload=False):
    """Start the backend FastAPI server."""
    backend_dir = Path(__file__).parent / "backend"
    cmd = [
        sys.executable,
        str(backend_dir / "main.py"),
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    logger.info(f"Starting backend server with command: {' '.join(cmd)}")
    
    # Run in a subprocess
    process = subprocess.Popen(
        cmd,
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return process

def run_mpc_server(transport, host, port):
    """Run the MPC server with the specified transport."""
    # Fix import statement to use relative import
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backend.server import run_stdio_transport, run_sse_transport
    
    # Start the backend server
    backend_process = None
    if transport == "sse":
        # For SSE transport, we need to start the backend server
        backend_process = start_backend_server(host, port+1)
    
    try:
        # Run the appropriate transport
        if transport == "stdio":
            logger.info("Starting MPC-Visio server with stdio transport")
            run_stdio_transport()
        else:
            logger.info(f"Starting MPC-Visio server with SSE transport on {host}:{port}")
            run_sse_transport(host, port)
    finally:
        # Make sure to terminate the backend server when done
        if backend_process:
            logger.info("Terminating backend server")
            backend_process.terminate()
            backend_process.wait()

def main():
    """Main entry point for the MPC Server"""
    parser = argparse.ArgumentParser(description="Run the MPC-Visio server")
    parser.add_argument(
        "--transport",
        type=str,
        default=os.environ.get("TRANSPORT", "stdio"),
        choices=["stdio", "sse"],
        help="Transport protocol to use (stdio or sse)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Host to bind to when using SSE transport",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8050")),
        help="Port to listen on when using SSE transport",
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Only start the backend server without the MPC server",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development (only for backend)",
    )
    args = parser.parse_args()

    # Validate environment variables
    required_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            logger.error(f"Environment variable {var} is required")
            sys.exit(1)
    
    if args.backend_only:
        # Only start the backend server
        process = start_backend_server(args.host, args.port, args.reload)
        try:
            # Print output from the subprocess
            for line in process.stdout:
                print(line, end="")
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        finally:
            process.terminate()
            process.wait()
    else:
        # Run the MPC server
        run_mpc_server(args.transport, args.host, args.port)

if __name__ == "__main__":
    main() 