"""
Ollama service for interacting with local LLMs for AI-powered features.
"""

import json
import logging
import os
import requests
from typing import Dict, List, Any, Optional, Union, Generator

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for interacting with Ollama API for AI-powered features."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama service.
        
        Args:
            base_url: Base URL for the Ollama API, defaults to http://localhost:11434
        """
        self.base_url = base_url
        self.api_generate = f"{self.base_url}/api/generate"
        self.api_chat = f"{self.base_url}/api/chat"
        self.default_model = "llama3"
    
    def check_ollama_available(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def ask_about_visio(self, 
                        question: str, 
                        diagram_analysis: Dict[str, Any],
                        model: Optional[str] = None, 
                        temperature: float = 0.7) -> Dict[str, Any]:
        """
        Ask a question about a Visio diagram and get a response.
        
        Args:
            question: The user's question about the diagram
            diagram_analysis: Analysis of the diagram to provide context
            model: The model to use (defaults to self.default_model)
            temperature: Temperature parameter for generation
            
        Returns:
            Dict containing the response from the model
        """
        try:
            model = model or self.default_model
            
            # Format the diagram analysis as context
            context = json.dumps(diagram_analysis, indent=2)
            
            prompt = f"""
You are an AI assistant specialized in Microsoft Visio diagrams.
I'll provide you with an analysis of a Visio diagram and a question about it.
Please analyze the diagram information and answer the question with accurate and helpful insights.

DIAGRAM ANALYSIS:
{context}

USER QUESTION:
{question}

Please provide a detailed and informative answer based solely on the information present in the diagram analysis.
"""
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature
            }
            
            response = requests.post(self.api_generate, json=payload)
            response.raise_for_status()
            result = response.json()
            
            return {
                "status": "success",
                "answer": result.get("response", ""),
                "model": model
            }
            
        except Exception as e:
            logger.exception(f"Error asking about Visio diagram: {e}")
            return {
                "status": "error",
                "message": f"Failed to get response from AI: {str(e)}"
            }
    
    def ask_about_visio_stream(self, 
                              question: str, 
                              diagram_analysis: Dict[str, Any],
                              model: Optional[str] = None, 
                              temperature: float = 0.7) -> Generator[Dict[str, Any], None, None]:
        """
        Ask a question about a Visio diagram and stream the response.
        
        Args:
            question: The user's question about the diagram
            diagram_analysis: Analysis of the diagram to provide context
            model: The model to use (defaults to self.default_model)
            temperature: Temperature parameter for generation
            
        Yields:
            Dict containing chunks of the response from the model
        """
        try:
            model = model or self.default_model
            
            # Format the diagram analysis as context
            context = json.dumps(diagram_analysis, indent=2)
            
            prompt = f"""
You are an AI assistant specialized in Microsoft Visio diagrams.
I'll provide you with an analysis of a Visio diagram and a question about it.
Please analyze the diagram information and answer the question with accurate and helpful insights.

DIAGRAM ANALYSIS:
{context}

USER QUESTION:
{question}

Please provide a detailed and informative answer based solely on the information present in the diagram analysis.
"""
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "temperature": temperature
            }
            
            with requests.post(self.api_generate, json=payload, stream=True) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            # Yield each chunk of the streamed response
                            yield {
                                "status": "success",
                                "answer_chunk": chunk.get("response", ""),
                                "done": chunk.get("done", False),
                                "model": model
                            }
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode JSON from stream: {line}")
                            continue
                
                # Final chunk indicating completion if not already sent
                yield {
                    "status": "success",
                    "answer_chunk": "",
                    "done": True,
                    "model": model
                }
                
        except Exception as e:
            logger.exception(f"Error streaming response about Visio diagram: {e}")
            yield {
                "status": "error",
                "message": f"Failed to stream response from AI: {str(e)}",
                "done": True
            }
    
    def generate_diagram_instructions(self, 
                                     description: str, 
                                     diagram_type: str = "flowchart",
                                     model: Optional[str] = None,
                                     temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate structured instructions for creating a Visio diagram based on a description.
        
        Args:
            description: Description of the diagram to generate
            diagram_type: Type of diagram to generate (flowchart, org chart, network, etc.)
            model: The model to use (defaults to self.default_model)
            temperature: Temperature parameter for generation
            
        Returns:
            Dict containing structured instructions for generating a Visio diagram
        """
        try:
            model = model or self.default_model
            
            prompt = f"""
You are an AI assistant specialized in Microsoft Visio diagrams.
I'll provide you with a description of a diagram I want to create.
Please generate structured JSON instructions that can be used to programmatically create this diagram.

DIAGRAM TYPE: {diagram_type}
DESCRIPTION: {description}

Output a JSON object that follows this structure:
{{
  "title": "Diagram title",
  "pages": [
    {{
      "name": "Page Name",
      "shapes": [
        {{
          "master": "Shape master name (if applicable)",
          "text": "Text content for shape",
          "x": X position (number),
          "y": Y position (number)
        }}
      ],
      "connections": [
        {{
          "from_shape_name": "Name of source shape",
          "to_shape_name": "Name of target shape",
          "text": "Optional text for connector"
        }}
      ]
    }}
  ]
}}

Ensure the instructions are detailed enough to create a complete diagram that matches the description.
"""
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature
            }
            
            response = requests.post(self.api_generate, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Extract and parse the JSON from the response
            response_text = result.get("response", "")
            # Find JSON content in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = response_text[json_start:json_end]
                try:
                    diagram_instructions = json.loads(json_content)
                    return {
                        "status": "success",
                        "instructions": diagram_instructions,
                        "model": model
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from model response: {e}")
                    return {
                        "status": "error",
                        "message": f"Failed to parse diagram instructions: {str(e)}",
                        "raw_response": response_text
                    }
            else:
                return {
                    "status": "error",
                    "message": "No valid JSON found in the model response",
                    "raw_response": response_text
                }
            
        except Exception as e:
            logger.exception(f"Error generating diagram instructions: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate diagram instructions: {str(e)}"
            }
    
    def modify_diagram_instructions(self, 
                                   current_analysis: Dict[str, Any],
                                   modification_request: str,
                                   model: Optional[str] = None,
                                   temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate instructions to modify an existing Visio diagram based on a request.
        
        Args:
            current_analysis: Analysis of the current diagram
            modification_request: Description of the requested modifications
            model: The model to use (defaults to self.default_model)
            temperature: Temperature parameter for generation
            
        Returns:
            Dict containing structured instructions for modifying a Visio diagram
        """
        try:
            model = model or self.default_model
            
            # Format the current diagram analysis as context
            context = json.dumps(current_analysis, indent=2)
            
            prompt = f"""
You are an AI assistant specialized in Microsoft Visio diagrams.
I'll provide you with an analysis of my current diagram and a description of modifications I want to make.
Please generate structured JSON instructions that can be used to programmatically modify this diagram.

CURRENT DIAGRAM:
{context}

REQUESTED MODIFICATIONS:
{modification_request}

Output a JSON object that follows this structure:
{{
  "add_shapes": [
    {{
      "page_name": "Name of the page to add shape to",
      "master": "Shape master name (if applicable)",
      "text": "Text content for shape",
      "x": X position (number),
      "y": Y position (number)
    }}
  ],
  "update_shapes": [
    {{
      "page_name": "Name of the page containing the shape",
      "shape_id": Shape ID to update (number),
      "shape_name": "Or shape name to update (string)",
      "text": "New text content (if changing)",
      "position": {{
        "x": New X position (number),
        "y": New Y position (number)
      }}
    }}
  ],
  "delete_shapes": [
    {{
      "page_name": "Name of the page containing the shape",
      "shape_id": Shape ID to delete (number),
      "shape_name": "Or shape name to delete (string)"
    }}
  ],
  "add_connections": [
    {{
      "page_name": "Name of the page to add connection to",
      "from_shape_id": From shape ID (number),
      "to_shape_id": To shape ID (number),
      "from_shape_name": "Or from shape name (string)",
      "to_shape_name": "Or to shape name (string)",
      "text": "Optional text for connector"
    }}
  ]
}}

Only include elements that need to be modified. For example, if no shapes need to be deleted, omit the "delete_shapes" element.
Ensure the instructions are detailed enough to make the requested modifications to the diagram.
"""
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature
            }
            
            response = requests.post(self.api_generate, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Extract and parse the JSON from the response
            response_text = result.get("response", "")
            # Find JSON content in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = response_text[json_start:json_end]
                try:
                    modification_instructions = json.loads(json_content)
                    return {
                        "status": "success",
                        "instructions": modification_instructions,
                        "model": model
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from model response: {e}")
                    return {
                        "status": "error",
                        "message": f"Failed to parse modification instructions: {str(e)}",
                        "raw_response": response_text
                    }
            else:
                return {
                    "status": "error",
                    "message": "No valid JSON found in the model response",
                    "raw_response": response_text
                }
            
        except Exception as e:
            logger.exception(f"Error generating modification instructions: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate modification instructions: {str(e)}"
            } 