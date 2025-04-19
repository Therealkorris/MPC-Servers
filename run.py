#!/usr/bin/env python3
"""
Entry point script for running the MPC Server in Docker.
"""
import argparse
import logging
import sys
import os
from pathlib import Path

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
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
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Import here to avoid circular imports
    from src.run_mpc import main as run_mpc_main
    
    # Call the main function from run_mpc.py
    sys.argv = [sys.argv[0]]  # Reset argv to avoid conflicts
    if args.transport:
        sys.argv.extend(["--transport", args.transport])
    if args.host:
        sys.argv.extend(["--host", args.host])
    if args.port:
        sys.argv.extend(["--port", str(args.port)])
    if args.backend_only:
        sys.argv.append("--backend-only")
    if args.reload:
        sys.argv.append("--reload")
    
    logger.info(f"Starting MPC server with args: {sys.argv}")
    run_mpc_main()

if __name__ == "__main__":
    main() 