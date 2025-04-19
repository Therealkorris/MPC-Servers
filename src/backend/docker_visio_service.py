"""
Docker-compatible mock Visio service that forwards requests to a local Visio service.
"""

import logging
import os
import requests
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

# The address of the local machine running the actual Visio service
LOCAL_VISIO_SERVICE = os.environ.get("LOCAL_VISIO_SERVICE", "http://host.docker.internal:8051")

class VisioService:
    """Mock Visio service that forwards requests to a local Visio service."""
    
    def __init__(self):
        """Initialize the Visio service."""
        logger.info(f"Initializing Docker Visio service, forwarding to {LOCAL_VISIO_SERVICE}")
    
    def _forward_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Forward a request to the local Visio service."""
        try:
            response = requests.post(f"{LOCAL_VISIO_SERVICE}/{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.exception(f"Error forwarding request to local Visio service: {e}")
            return {
                "status": "error",
                "message": f"Failed to communicate with local Visio service: {str(e)}"
            }
    
    def analyze_visio_diagram(self, file_path_or_content: str, analysis_type: str = "structure") -> Dict[str, Any]:
        """Forward analyze_visio_diagram request to local service."""
        return self._forward_request("analyze_visio_diagram", {
            "file_path_or_content": file_path_or_content,
            "analysis_type": analysis_type
        })
    
    def modify_visio_diagram(self, file_path_or_content: str, modification_instructions: Dict[str, Any]) -> Dict[str, Any]:
        """Forward modify_visio_diagram request to local service."""
        return self._forward_request("modify_visio_diagram", {
            "file_path_or_content": file_path_or_content,
            "modification_instructions": modification_instructions
        })
    
    def get_active_document(self) -> Dict[str, Any]:
        """Forward get_active_document request to local service."""
        return self._forward_request("get_active_document", {})
    
    def verify_connections(self, file_path_or_content: str, connection_attempts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Forward verify_connections request to local service."""
        return self._forward_request("verify_connections", {
            "file_path_or_content": file_path_or_content,
            "connection_attempts": connection_attempts
        })
    
    def generate_visio_diagram(self, instructions: Dict[str, Any], template: Optional[str] = None) -> Dict[str, Any]:
        """Forward generate_visio_diagram request to local service."""
        return self._forward_request("generate_visio_diagram", {
            "instructions": instructions,
            "template": template
        })
    
    # Implement dummy methods for functions that shouldn't be forwarded
    def save_visio_file(self, file_content: str, file_path: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "message": "Docker environment: File operations are handled locally."
        }
    
    def load_visio_file(self, file_path: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "message": "Docker environment: File operations are handled locally."
        } 