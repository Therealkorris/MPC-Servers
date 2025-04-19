"""
Main entry point for the Visio AI backend application.
"""

import logging
import os
import sys
import uvicorn
import argparse
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiofiles
from typing import List, Optional, Dict, Any
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

app = FastAPI(title="Visio AI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount the uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Import and include API routers
from api.routes import images, models, vision, sessions

# Include the routers with a prefix
app.include_router(images.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(vision.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")

# Define API models
class ProcessRequest(BaseModel):
    image_url: str
    settings: Optional[Dict[str, Any]] = None

class ProcessResponse(BaseModel):
    result: str
    processed_image_url: Optional[str] = None

@app.get("/")
async def read_root():
    return {"message": "Welcome to Visio AI API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    
    async with aiofiles.open(file_location, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return {"filename": file.filename, "file_path": f"/uploads/{file.filename}"}

@app.post("/api/process", response_model=ProcessResponse)
async def process_image(request: ProcessRequest):
    # Placeholder for actual processing logic
    return {
        "result": "Processing completed successfully",
        "processed_image_url": request.image_url
    }

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Visio AI backend server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload) 