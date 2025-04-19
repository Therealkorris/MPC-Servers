#!/usr/bin/env python3
"""
Run a local Visio service that handles actual Visio operations.
This service receives requests from the Docker container.
"""
import json
import logging
import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
import uvicorn
from src.backend.visio_service import VisioService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the FastAPI application
app = FastAPI(title="Local Visio Service")

# Initialize the Visio service
visio_service = VisioService()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/analyze_visio_diagram")
async def analyze_visio_diagram(request: Request):
    """Analyze a Visio diagram."""
    data = await request.json()
    file_path_or_content = data.get("file_path_or_content")
    
    # Handle file paths from Docker container
    if isinstance(file_path_or_content, str) and file_path_or_content.startswith("/app/"):
        # Convert Docker container path to local Windows path
        relative_path = file_path_or_content.replace("/app/", "")
        file_path_or_content = os.path.join(os.getcwd(), relative_path)
        logger.info(f"Converted Docker path to local path: {file_path_or_content}")
    
    analysis_type = data.get("analysis_type", "structure")
    result = visio_service.analyze_visio_diagram(file_path_or_content, analysis_type)
    return result

@app.post("/modify_visio_diagram")
async def modify_visio_diagram(request: Request):
    """Modify a Visio diagram."""
    data = await request.json()
    file_path_or_content = data.get("file_path_or_content")
    
    # Handle file paths from Docker container
    if isinstance(file_path_or_content, str) and file_path_or_content.startswith("/app/"):
        # Convert Docker container path to local Windows path
        relative_path = file_path_or_content.replace("/app/", "")
        file_path_or_content = os.path.join(os.getcwd(), relative_path)
        logger.info(f"Converted Docker path to local path: {file_path_or_content}")
    
    modification_instructions = data.get("modification_instructions")
    result = visio_service.modify_visio_diagram(file_path_or_content, modification_instructions)
    return result

@app.post("/get_active_document")
async def get_active_document():
    """Get the active Visio document."""
    result = visio_service.get_active_document()
    return result

@app.post("/verify_connections")
async def verify_connections(request: Request):
    """Verify connections in a Visio diagram."""
    data = await request.json()
    file_path_or_content = data.get("file_path_or_content")
    
    # Handle file paths from Docker container
    if isinstance(file_path_or_content, str) and file_path_or_content.startswith("/app/"):
        # Convert Docker container path to local Windows path
        relative_path = file_path_or_content.replace("/app/", "")
        file_path_or_content = os.path.join(os.getcwd(), relative_path)
        logger.info(f"Converted Docker path to local path: {file_path_or_content}")
    
    connection_attempts = data.get("connection_attempts", [])
    result = visio_service.verify_connections(file_path_or_content, connection_attempts)
    return result

@app.post("/generate_visio_diagram")
async def generate_visio_diagram(request: Request):
    """Generate a Visio diagram."""
    data = await request.json()
    instructions = data.get("instructions")
    template = data.get("template")
    
    # Handle template path from Docker container
    if isinstance(template, str) and template.startswith("/app/"):
        # Convert Docker container path to local Windows path
        relative_path = template.replace("/app/", "")
        template = os.path.join(os.getcwd(), relative_path)
        logger.info(f"Converted Docker template path to local path: {template}")
    
    result = visio_service.generate_visio_diagram(instructions, template)
    return result

def main():
    """Main entry point."""
    port = int(os.environ.get("VISIO_SERVICE_PORT", "8051"))
    host = os.environ.get("VISIO_SERVICE_HOST", "127.0.0.1")
    
    logger.info(f"Starting local Visio service on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main() 