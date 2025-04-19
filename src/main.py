#!/usr/bin/env python3
"""
MPC-Visio: MPC Server for Microsoft Visio
"""
import argparse
import logging
import os
import sys
from pathlib import Path

from src.backend.server import run_stdio_transport, run_sse_transport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the MCP Server"""
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
    args = parser.parse_args()

    # Validate environment variables
    required_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            logger.error(f"Environment variable {var} is required")
            sys.exit(1)

    # Run the appropriate transport
    if args.transport == "stdio":
        logger.info("Starting MPC-Visio server with stdio transport")
        run_stdio_transport()
    else:
        logger.info(f"Starting MPC-Visio server with SSE transport on {args.host}:{args.port}")
        run_sse_transport(args.host, args.port)


if __name__ == "__main__":
    main() 