"""
FastAPI application that exposes Visio and Ollama services through a REST API.
"""

import base64
import json
import logging
import os
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, Body, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from visio_service import VisioService
from ollama_service import OllamaService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Visio AI API",
    description="API for interacting with Microsoft Visio files using AI capabilities",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
visio_service = VisioService()
ollama_service = OllamaService()

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# API Models
class VisioFileUpload(BaseModel):
    file_content: str = Field(..., description="Base64 encoded Visio file content")
    file_name: str = Field(..., description="Name of the file to save")

class VisioAnalysisRequest(BaseModel):
    file_path: str = Field(..., description="Path to the Visio file to analyze")
    analysis_type: str = Field("structure", description="Type of analysis to perform: structure, connections, or text")

class VisioModificationRequest(BaseModel):
    file_path: str = Field(..., description="Path to the Visio file to modify")
    instructions: Dict[str, Any] = Field(..., description="Instructions for modifying the diagram")

class VisioDiagramGenerationRequest(BaseModel):
    title: str = Field(..., description="Title of the diagram to generate")
    description: str = Field(..., description="Description of the diagram to generate")
    diagram_type: str = Field("flowchart", description="Type of diagram to generate")
    template_path: Optional[str] = Field(None, description="Optional path to a template file")

class VisioAIQuestionRequest(BaseModel):
    file_path: str = Field(..., description="Path to the Visio file to analyze")
    question: str = Field(..., description="Question about the diagram")
    model: Optional[str] = Field(None, description="Model to use for answering")
    temperature: float = Field(0.7, description="Temperature parameter for generation")

class VisioAIGenerateRequest(BaseModel):
    description: str = Field(..., description="Description of the diagram to generate")
    diagram_type: str = Field("flowchart", description="Type of diagram to generate")
    model: Optional[str] = Field(None, description="Model to use for generation")
    temperature: float = Field(0.7, description="Temperature parameter for generation")

class VisioAIModifyRequest(BaseModel):
    file_path: str = Field(..., description="Path to the Visio file to modify")
    modification_request: str = Field(..., description="Description of the modifications to make")
    model: Optional[str] = Field(None, description="Model to use for generation")
    temperature: float = Field(0.7, description="Temperature parameter for generation")

@app.get("/")
async def root():
    """Check if the API is running."""
    return {"status": "online", "message": "Visio AI API is running"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    services_status = {
        "visio": visio_service.is_visio_available(),
        "ollama": ollama_service.check_ollama_available()
    }
    
    return {
        "status": "healthy" if all(services_status.values()) else "degraded",
        "services": services_status
    }

# Visio file management endpoints
@app.post("/visio/upload")
async def upload_visio_file(file_data: VisioFileUpload):
    """Upload a Visio file (base64 encoded)."""
    try:
        result = visio_service.save_visio_file(file_data.file_content, f"uploads/{file_data.file_name}")
        return result
    except Exception as e:
        logger.exception("Error uploading Visio file")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/visio/upload/form")
async def upload_visio_file_form(file: UploadFile = File(...)):
    """Upload a Visio file using multipart form data."""
    try:
        file_content = await file.read()
        file_content_base64 = base64.b64encode(file_content).decode('utf-8')
        
        filename = file.filename
        save_path = f"uploads/{filename}"
        
        result = visio_service.save_visio_file(file_content_base64, save_path)
        return result
    except Exception as e:
        logger.exception("Error uploading Visio file via form")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/visio/load")
async def load_visio_file(file_path: str):
    """Load a Visio file and return its content as base64."""
    try:
        result = visio_service.load_visio_file(file_path)
        return result
    except Exception as e:
        logger.exception("Error loading Visio file")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/visio/list")
async def list_visio_files():
    """List available Visio files in the uploads directory."""
    try:
        files = []
        for file in os.listdir("uploads"):
            if file.lower().endswith((".vsdx", ".vsd", ".vsdm")):
                files.append({
                    "name": file,
                    "path": f"uploads/{file}",
                    "size": os.path.getsize(f"uploads/{file}")
                })
        return {"files": files}
    except Exception as e:
        logger.exception("Error listing Visio files")
        raise HTTPException(status_code=500, detail=str(e))

# Visio diagram analysis endpoints
@app.post("/visio/analyze")
async def analyze_visio_diagram(request: VisioAnalysisRequest):
    """Analyze a Visio diagram."""
    try:
        result = visio_service.analyze_visio_diagram(request.file_path, request.analysis_type)
        return result
    except Exception as e:
        logger.exception("Error analyzing Visio diagram")
        raise HTTPException(status_code=500, detail=str(e))

# Visio diagram modification endpoints
@app.post("/visio/modify")
async def modify_visio_diagram(request: VisioModificationRequest):
    """Modify a Visio diagram based on provided instructions."""
    try:
        result = visio_service.modify_visio_diagram(request.file_path, request.instructions)
        return result
    except Exception as e:
        logger.exception("Error modifying Visio diagram")
        raise HTTPException(status_code=500, detail=str(e))

# Visio diagram generation endpoints
@app.post("/visio/generate")
async def generate_visio_diagram(request: VisioDiagramGenerationRequest):
    """Generate a new Visio diagram based on provided instructions."""
    try:
        instructions = {
            "title": request.title,
            "pages": [
                {
                    "name": "Page-1",
                    "shapes": [],
                    "connections": []
                }
            ]
        }
        
        result = visio_service.generate_visio_diagram(
            diagram_title=request.title,
            instructions=instructions,
            template_path=request.template_path
        )
        return result
    except Exception as e:
        logger.exception("Error generating Visio diagram")
        raise HTTPException(status_code=500, detail=str(e))

# AI-powered endpoints
@app.post("/ai/ask")
async def ask_about_visio(request: VisioAIQuestionRequest):
    """Ask a question about a Visio diagram and get an AI-powered response."""
    try:
        # First analyze the diagram
        analysis_result = visio_service.analyze_visio_diagram(
            request.file_path, 
            analysis_type="structure"
        )
        
        if analysis_result["status"] != "success":
            return analysis_result
        
        # Then ask the question using Ollama
        result = ollama_service.ask_about_visio(
            question=request.question,
            diagram_analysis=analysis_result["analysis"],
            model=request.model,
            temperature=request.temperature
        )
        
        return result
    except Exception as e:
        logger.exception("Error asking about Visio diagram")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/ask/stream")
async def ask_about_visio_stream(request: VisioAIQuestionRequest):
    """Ask a question about a Visio diagram and stream the AI-powered response."""
    try:
        # First analyze the diagram
        analysis_result = visio_service.analyze_visio_diagram(
            request.file_path, 
            analysis_type="structure"
        )
        
        if analysis_result["status"] != "success":
            return analysis_result
        
        # Then stream the response
        async def stream_generator():
            for chunk in ollama_service.ask_about_visio_stream(
                question=request.question,
                diagram_analysis=analysis_result["analysis"],
                model=request.model,
                temperature=request.temperature
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
                
        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.exception("Error streaming response about Visio diagram")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/generate")
async def generate_visio_with_ai(request: VisioAIGenerateRequest):
    """Generate a Visio diagram using AI-powered instructions."""
    try:
        # Generate diagram instructions
        instructions_result = ollama_service.generate_diagram_instructions(
            description=request.description,
            diagram_type=request.diagram_type,
            model=request.model,
            temperature=request.temperature
        )
        
        if instructions_result["status"] != "success":
            return instructions_result
        
        # Generate the diagram
        diagram_title = instructions_result["instructions"].get("title", "Generated Diagram")
        
        result = visio_service.generate_visio_diagram(
            diagram_title=diagram_title,
            instructions=instructions_result["instructions"]
        )
        
        return {
            "status": result["status"],
            "message": result.get("message", ""),
            "file_path": result.get("file_path", ""),
            "instructions": instructions_result["instructions"]
        }
    except Exception as e:
        logger.exception("Error generating Visio diagram with AI")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/modify")
async def modify_visio_with_ai(request: VisioAIModifyRequest):
    """Modify a Visio diagram using AI-powered instructions."""
    try:
        # First analyze the diagram
        analysis_result = visio_service.analyze_visio_diagram(
            request.file_path, 
            analysis_type="structure"
        )
        
        if analysis_result["status"] != "success":
            return analysis_result
        
        # Generate modification instructions
        instructions_result = ollama_service.modify_diagram_instructions(
            current_analysis=analysis_result["analysis"],
            modification_request=request.modification_request,
            model=request.model,
            temperature=request.temperature
        )
        
        if instructions_result["status"] != "success":
            return instructions_result
        
        # Modify the diagram
        result = visio_service.modify_visio_diagram(
            request.file_path,
            instructions_result["instructions"]
        )
        
        return {
            "status": result["status"],
            "message": result.get("message", ""),
            "file_path": result.get("file_path", ""),
            "modifications": instructions_result["instructions"]
        }
    except Exception as e:
        logger.exception("Error modifying Visio diagram with AI")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 