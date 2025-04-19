"""
Server implementation for MPC Visio.
"""

import json
import logging
import sys
from typing import Dict, List, Any, Union, Optional

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn

from backend.ollama_service import OllamaService
from backend.visio_service import VisioService

logger = logging.getLogger(__name__)

# Initialize services
visio_service = VisioService()
ollama_service = OllamaService()


app = FastAPI(title="MCP-Visio")


async def process_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Process an MCP message and return the response."""
    try:
        mcp_method = message.get("method")
        mcp_params = message.get("params", {})
        
        if mcp_method == "health":
            # Simple health check method
            services_status = {
                "visio": True,
                "ollama": ollama_service.check_ollama_available()
            }
            return {
                "result": {
                    "status": "healthy" if all(services_status.values()) else "degraded",
                    "services": services_status
                }
            }
        
        elif mcp_method == "ping":
            # Simple ping method
            return {"result": "pong"}
        
        elif mcp_method == "save_visio_file":
            result = visio_service.save_visio_file(
                mcp_params.get("file_content"),
                mcp_params.get("file_path")
            )
            return {"result": result}
        
        elif mcp_method == "load_visio_file":
            result = visio_service.load_visio_file(
                mcp_params.get("file_path")
            )
            return {"result": result}
        
        elif mcp_method == "analyze_visio_diagram":
            result = visio_service.analyze_visio_diagram(
                mcp_params.get("file_path_or_content"),
                mcp_params.get("analysis_type", "structure")
            )
            return {"result": result}
        
        elif mcp_method == "verify_connections":
            result = visio_service.verify_connections(
                mcp_params.get("file_path_or_content"),
                mcp_params.get("connection_attempts", [])
            )
            return {"result": result}
        
        elif mcp_method == "modify_visio_diagram":
            result = visio_service.modify_visio_diagram(
                mcp_params.get("file_path_or_content"),
                mcp_params.get("modification_instructions")
            )
            return {"result": result}
        
        elif mcp_method == "generate_visio_diagram":
            result = visio_service.generate_visio_diagram(
                mcp_params.get("instructions"),
                mcp_params.get("template", None)
            )
            return {"result": result}
        
        elif mcp_method == "get_active_document":
            result = visio_service.get_active_document()
            return {"result": result}
        
        elif mcp_method == "ask_ai_about_visio":
            responses = []
            
            # This is a streaming endpoint
            async for chunk in ollama_service.chat_stream(
                mcp_params.get("messages", []),
                mcp_params.get("model", "llama3"),
                mcp_params.get("context", {})
            ):
                responses.append(chunk)
            
            return {"result": responses[-1] if responses else {}}
            
        else:
            return {"error": {"code": -32601, "message": f"Method '{mcp_method}' not found"}}
    
    except Exception as e:
        logger.exception(f"Error processing message: {e}")
        return {"error": {"code": -32603, "message": f"Internal error: {str(e)}"}}


async def process_stream_message(message: Dict[str, Any]):
    """Process an MCP message and yield streaming responses."""
    try:
        mcp_method = message.get("method")
        mcp_params = message.get("params", {})
        
        if mcp_method == "ask_ai_about_visio":
            # This is a streaming endpoint
            async for chunk in ollama_service.chat_stream(
                mcp_params.get("messages", []),
                mcp_params.get("model", "llama3"),
                mcp_params.get("context", {})
            ):
                yield {
                    "id": message.get("id"),
                    "result": chunk
                }
        else:
            # For non-streaming methods, process normally and yield once
            result = await process_message(message)
            yield result
    
    except Exception as e:
        logger.exception(f"Error processing streaming message: {e}")
        yield {"error": {"code": -32603, "message": f"Internal error: {str(e)}"}}


# SSE Transport
@app.post("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for the MPC server."""
    message = await request.json()
    
    # Check if the method is a streaming method
    mcp_method = message.get("method")
    if mcp_method == "ask_ai_about_visio":
        # For streaming methods, use SSE
        async def event_generator():
            async for result in process_stream_message(message):
                yield json.dumps(result)
        
        return EventSourceResponse(event_generator())
    else:
        # For non-streaming methods, process normally
        result = await process_message(message)
        
        # Return as a single SSE event
        async def single_event_generator():
            yield json.dumps(result)
        
        return EventSourceResponse(single_event_generator())


# Functions for different transports
def run_stdio_transport():
    """Run the MPC server with stdio transport."""
    for line in sys.stdin:
        try:
            message = json.loads(line)
            response = asyncio.run(process_message(message))
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line}")
            print(json.dumps({"error": {"code": -32700, "message": "Parse error"}}), flush=True)
        except Exception as e:
            logger.exception(f"Error in stdio transport: {e}")
            print(json.dumps({"error": {"code": -32603, "message": f"Internal error: {str(e)}"}}), flush=True)


def run_sse_transport(host: str, port: int):
    """Run the MPC server with SSE transport."""
    uvicorn.run(app, host=host, port=port)


# Add asyncio import to top of file
import asyncio 