"""
Microsoft Visio service for interacting with Visio files.
"""

import base64
import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Import win32com for Visio automation
import win32com.client

logger = logging.getLogger(__name__)

class VisioService:
    """Service for working with Microsoft Visio files."""
    
    def __init__(self):
        """Initialize the Visio service."""
        self.visio_app = None
        
    def _ensure_visio_app(self):
        """Ensure the Visio application is running."""
        if self.visio_app is None:
            try:
                logger.info("Starting Microsoft Visio application...")
                self.visio_app = win32com.client.GetObject("Visio.Application")
                logger.info("Connected to existing Microsoft Visio application.")
                # Make sure Visio is visible
                self.visio_app.Visible = 1
            except:
                try:
                    logger.info("No existing Visio application found. Starting a new one...")
                    self.visio_app = win32com.client.Dispatch("Visio.Application")
                    # Make Visio visible
                    self.visio_app.Visible = 1
                    logger.info("Microsoft Visio application started successfully.")
                except Exception as e:
                    logger.error(f"Failed to start Microsoft Visio application: {e}")
                    raise RuntimeError(f"Failed to start Microsoft Visio application: {e}")
        else:
            # Ensure Visio is visible even if we already have a reference
            self.visio_app.Visible = 1
    
    def _close_visio_app(self):
        """Close the Visio application."""
        if self.visio_app is not None:
            try:
                self.visio_app.Quit()
                self.visio_app = None
                logger.info("Microsoft Visio application closed.")
            except Exception as e:
                logger.error(f"Error closing Microsoft Visio application: {e}")
    
    def _get_active_document(self):
        """Get the active document if available."""
        self._ensure_visio_app()
        
        if self.visio_app.Documents.Count > 0:
            try:
                return self.visio_app.ActiveDocument
            except:
                return None
        return None
    
    def _get_document_by_name(self, file_name):
        """Get a document by its file name if it's open."""
        self._ensure_visio_app()
        
        if self.visio_app.Documents.Count > 0:
            for i in range(1, self.visio_app.Documents.Count + 1):
                doc = self.visio_app.Documents.Item(i)
                if doc.Name == os.path.basename(file_name):
                    return doc
        return None
    
    def _get_or_open_document(self, file_path):
        """Get an open document or open it if it's not already open."""
        # First check if the document is already open
        doc = self._get_document_by_name(file_path)
        if doc:
            logger.info(f"Using already open document: {file_path}")
            return doc, False
        
        # If not open, open it
        self._ensure_visio_app()
        doc = self.visio_app.Documents.Open(file_path)
        logger.info(f"Opened document: {file_path}")
        return doc, True
    
    def save_visio_file(self, file_content: str, file_path: str) -> Dict[str, Any]:
        """
        Save Visio file content to the specified path.
        
        Args:
            file_content: Base64 encoded Visio file content
            file_path: Path where to save the file
            
        Returns:
            Dict with status and file path
        """
        try:
            # Decode base64 content
            binary_content = base64.b64decode(file_content)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write to file
            with open(file_path, 'wb') as f:
                f.write(binary_content)
            
            return {
                "status": "success",
                "file_path": file_path,
                "message": f"Visio file saved to {file_path}"
            }
            
        except Exception as e:
            logger.exception(f"Error saving Visio file: {e}")
            return {
                "status": "error",
                "message": f"Failed to save Visio file: {str(e)}"
            }
    
    def load_visio_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load a Visio file from the specified path.
        
        Args:
            file_path: Path to the Visio file
            
        Returns:
            Dict with status and file content (base64 encoded)
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "message": f"File not found: {file_path}"
                }
            
            # Read file content
            with open(file_path, 'rb') as f:
                binary_content = f.read()
            
            # Encode to base64
            b64_content = base64.b64encode(binary_content).decode('utf-8')
            
            return {
                "status": "success",
                "file_path": file_path,
                "file_content": b64_content,
                "message": f"Visio file loaded from {file_path}"
            }
            
        except Exception as e:
            logger.exception(f"Error loading Visio file: {e}")
            return {
                "status": "error",
                "message": f"Failed to load Visio file: {str(e)}"
            }
    
    def analyze_visio_diagram(self, file_path_or_content: str, analysis_type: str = "structure") -> Dict[str, Any]:
        """
        Analyze a Visio diagram.
        
        Args:
            file_path_or_content: Path to the Visio file or base64-encoded content
            analysis_type: Type of analysis to perform (structure, connections, etc.)
            
        Returns:
            Dict with analysis results
        """
        temp_file = None
        doc = None
        should_close_doc = False
        
        try:
            self._ensure_visio_app()
            
            # Determine if input is a path or content
            if os.path.exists(file_path_or_content):
                file_path = file_path_or_content
                # Try to get an already open document
                doc, should_close_doc = self._get_or_open_document(file_path)
                # Make Visio visible in case it's not
                self.visio_app.Visible = 1
                # No Activate() call - it's not needed and can cause errors
            else:
                # Assume it's base64 content and save to temp file
                binary_content = base64.b64decode(file_path_or_content)
                temp_file = tempfile.NamedTemporaryFile(suffix='.vsdx', delete=False)
                temp_file.write(binary_content)
                temp_file.close()
                file_path = temp_file.name
                
                # Open the document
                doc = self.visio_app.Documents.Open(file_path)
                should_close_doc = True
                # Make Visio visible
                self.visio_app.Visible = 1
            
            analysis_results = {}
            
            # Perform analysis based on type
            if analysis_type == "structure":
                analysis_results = self._analyze_diagram_structure(doc)
            elif analysis_type == "connections":
                analysis_results = self._analyze_diagram_connections(doc)
            elif analysis_type == "text":
                analysis_results = self._analyze_diagram_text(doc)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown analysis type: {analysis_type}"
                }
            
            return {
                "status": "success",
                "analysis_type": analysis_type,
                "results": analysis_results
            }
            
        except Exception as e:
            logger.exception(f"Error analyzing Visio diagram: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze Visio diagram: {str(e)}"
            }
            
        finally:
            # Clean up temp files, but don't close the document if it was already open
            if temp_file is not None:
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            
            # Only close the document if it was opened by this function call
            if doc is not None and should_close_doc and temp_file is not None:
                try:
                    doc.Close()
                except:
                    pass
    
    def _analyze_diagram_structure(self, doc) -> Dict[str, Any]:
        """Analyze the structure of a Visio diagram."""
        structure = {
            "pages": [],
            "total_shapes": 0
        }
        
        # Analyze each page
        for i in range(1, doc.Pages.Count + 1):
            page = doc.Pages.Item(i)
            page_info = {
                "name": page.Name,
                "shapes_count": page.Shapes.Count,
                "shapes": []
            }
            
            # Analyze shapes on this page
            for j in range(1, page.Shapes.Count + 1):
                shape = page.Shapes.Item(j)
                shape_info = {
                    "name": shape.Name,
                    "text": shape.Text if hasattr(shape, "Text") else "",
                    "type": shape.Type,
                    "id": shape.ID
                }
                page_info["shapes"].append(shape_info)
            
            structure["total_shapes"] += page_info["shapes_count"]
            structure["pages"].append(page_info)
        
        return structure
    
    def _analyze_diagram_connections(self, doc) -> Dict[str, Any]:
        """Analyze the connections in a Visio diagram."""
        connections = {
            "pages": [],
            "total_connections": 0
        }
        
        # Analyze each page
        for i in range(1, doc.Pages.Count + 1):
            page = doc.Pages.Item(i)
            page_info = {
                "name": page.Name,
                "connections": []
            }
            
            # Find connector shapes
            for j in range(1, page.Shapes.Count + 1):
                shape = page.Shapes.Item(j)
                
                # Check if shape is a connector
                if shape.Connects.Count > 0:
                    connection_info = {
                        "connector_id": shape.ID,
                        "connector_name": shape.Name,
                        "text": shape.Text if hasattr(shape, "Text") else "",
                        "connects_from": None,
                        "connects_to": None
                    }
                    
                    # Get connection info
                    for k in range(1, shape.Connects.Count + 1):
                        connect = shape.Connects.Item(k)
                        from_sheet = connect.FromSheet
                        to_sheet = connect.ToSheet
                        
                        if from_sheet.ID != shape.ID:
                            connection_info["connects_from"] = {
                                "id": from_sheet.ID,
                                "name": from_sheet.Name
                            }
                        
                        if to_sheet.ID != shape.ID:
                            connection_info["connects_to"] = {
                                "id": to_sheet.ID,
                                "name": to_sheet.Name
                            }
                    
                    if connection_info["connects_from"] or connection_info["connects_to"]:
                        page_info["connections"].append(connection_info)
                        connections["total_connections"] += 1
            
            connections["pages"].append(page_info)
        
        return connections
    
    def _analyze_diagram_text(self, doc) -> Dict[str, Any]:
        """Extract text content from a Visio diagram."""
        text_content = {
            "pages": [],
            "total_text_shapes": 0
        }
        
        # Analyze each page
        for i in range(1, doc.Pages.Count + 1):
            page = doc.Pages.Item(i)
            page_info = {
                "name": page.Name,
                "text_shapes": []
            }
            
            # Extract text from shapes
            for j in range(1, page.Shapes.Count + 1):
                shape = page.Shapes.Item(j)
                
                # Check if shape has text
                if hasattr(shape, "Text") and shape.Text.strip():
                    text_shape = {
                        "id": shape.ID,
                        "name": shape.Name,
                        "text": shape.Text.strip()
                    }
                    page_info["text_shapes"].append(text_shape)
                    text_content["total_text_shapes"] += 1
            
            text_content["pages"].append(page_info)
        
        return text_content
    
    def modify_visio_diagram(self, file_path_or_content: str, modification_instructions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify a Visio diagram based on instructions.
        
        Args:
            file_path_or_content: Path to the Visio file or base64-encoded content
            modification_instructions: Instructions for modifying the diagram
            
        Returns:
            Dict with modified diagram content (base64 encoded)
        """
        temp_file = None
        doc = None
        should_close_doc = False
        
        try:
            self._ensure_visio_app()
            
            # Determine if input is a path or content
            is_content = False
            if os.path.exists(file_path_or_content):
                file_path = file_path_or_content
                # Try to get an already open document
                doc, should_close_doc = self._get_or_open_document(file_path)
                # Make Visio visible in case it's not
                self.visio_app.Visible = 1
                # No Activate() call - it's not needed and can cause errors
            else:
                # Assume it's base64 content and save to temp file
                is_content = True
                binary_content = base64.b64decode(file_path_or_content)
                temp_file = tempfile.NamedTemporaryFile(suffix='.vsdx', delete=False)
                temp_file.write(binary_content)
                temp_file.close()
                file_path = temp_file.name
                
                # Open the document
                doc = self.visio_app.Documents.Open(file_path)
                should_close_doc = True
                # Make Visio visible
                self.visio_app.Visible = 1
            
            # Apply modifications based on instructions
            if "add_shapes" in modification_instructions:
                self._add_shapes(doc, modification_instructions["add_shapes"])
            
            if "update_shapes" in modification_instructions:
                self._update_shapes(doc, modification_instructions["update_shapes"])
            
            if "delete_shapes" in modification_instructions:
                self._delete_shapes(doc, modification_instructions["delete_shapes"])
            
            if "add_connections" in modification_instructions:
                self._add_connections(doc, modification_instructions["add_connections"])
            
            # Save the document
            doc.Save()
            
            # Only use SaveAs if we're working with a temp file
            output_path = temp_file.name if temp_file else file_path
            if temp_file:
                doc.SaveAs(output_path)
            
            result = {
                "status": "success",
                "message": "Diagram modified successfully"
            }
            
            # If input was content, return modified content
            if is_content or modification_instructions.get("return_content", False):
                with open(output_path, 'rb') as f:
                    binary_content = f.read()
                
                # Encode to base64
                b64_content = base64.b64encode(binary_content).decode('utf-8')
                result["file_content"] = b64_content
            
            if not is_content:
                result["file_path"] = file_path
            
            return result
            
        except Exception as e:
            logger.exception(f"Error modifying Visio diagram: {e}")
            return {
                "status": "error",
                "message": f"Failed to modify Visio diagram: {str(e)}"
            }
            
        finally:
            # Clean up temp files, but don't close the document if it was already open
            if temp_file is not None:
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            
            # Only close the document if it was opened by this function call
            if doc is not None and should_close_doc and temp_file is not None:
                try:
                    doc.Close()
                except:
                    pass
    
    def _add_shapes(self, doc, shapes_info: List[Dict[str, Any]]):
        """Add shapes to a Visio document."""
        for shape_info in shapes_info:
            page_name = shape_info.get("page_name")
            page_index = shape_info.get("page_index", 1)
            
            # Get the page
            page = None
            if page_name:
                for i in range(1, doc.Pages.Count + 1):
                    if doc.Pages.Item(i).Name == page_name:
                        page = doc.Pages.Item(i)
                        break
            else:
                page = doc.Pages.Item(page_index)
            
            if not page:
                logger.warning(f"Page not found: {page_name or page_index}")
                continue
            
            # Add shape
            shape_master = shape_info.get("master")
            x = shape_info.get("x", 4)
            y = shape_info.get("y", 4)
            text = shape_info.get("text", "")
            
            if shape_master:
                # Find the master by name
                for i in range(1, doc.Masters.Count + 1):
                    master = doc.Masters.Item(i)
                    if master.Name == shape_master:
                        shape = page.Drop(master, x, y)
                        if text:
                            shape.Text = text
                        break
            else:
                # Add a basic shape
                shape = page.DrawRectangle(x, y, x + 2, y + 1)
                if text:
                    shape.Text = text
    
    def _update_shapes(self, doc, shapes_info: List[Dict[str, Any]]):
        """Update shapes in a Visio document."""
        for shape_info in shapes_info:
            page_name = shape_info.get("page_name")
            page_index = shape_info.get("page_index", 1)
            shape_id = shape_info.get("shape_id")
            shape_name = shape_info.get("shape_name")
            
            # Get the page
            page = None
            if page_name:
                for i in range(1, doc.Pages.Count + 1):
                    if doc.Pages.Item(i).Name == page_name:
                        page = doc.Pages.Item(i)
                        break
            else:
                page = doc.Pages.Item(page_index)
            
            if not page:
                logger.warning(f"Page not found: {page_name or page_index}")
                continue
            
            # Find the shape
            shape = None
            if shape_id:
                for j in range(1, page.Shapes.Count + 1):
                    if page.Shapes.Item(j).ID == shape_id:
                        shape = page.Shapes.Item(j)
                        break
            elif shape_name:
                for j in range(1, page.Shapes.Count + 1):
                    if page.Shapes.Item(j).Name == shape_name:
                        shape = page.Shapes.Item(j)
                        break
            
            if not shape:
                logger.warning(f"Shape not found: {shape_id or shape_name}")
                continue
            
            # Update shape properties
            if "text" in shape_info:
                shape.Text = shape_info["text"]
            
            if "position" in shape_info:
                x = shape_info["position"].get("x")
                y = shape_info["position"].get("y")
                if x is not None and y is not None:
                    shape.XYPosition(x, y)
    
    def _delete_shapes(self, doc, shapes_info: List[Dict[str, Any]]):
        """Delete shapes from a Visio document."""
        for shape_info in shapes_info:
            page_name = shape_info.get("page_name")
            page_index = shape_info.get("page_index", 1)
            shape_id = shape_info.get("shape_id")
            shape_name = shape_info.get("shape_name")
            
            # Get the page
            page = None
            if page_name:
                for i in range(1, doc.Pages.Count + 1):
                    if doc.Pages.Item(i).Name == page_name:
                        page = doc.Pages.Item(i)
                        break
            else:
                page = doc.Pages.Item(page_index)
            
            if not page:
                logger.warning(f"Page not found: {page_name or page_index}")
                continue
            
            # Find the shape
            shape = None
            if shape_id:
                for j in range(1, page.Shapes.Count + 1):
                    if page.Shapes.Item(j).ID == shape_id:
                        shape = page.Shapes.Item(j)
                        break
            elif shape_name:
                for j in range(1, page.Shapes.Count + 1):
                    if page.Shapes.Item(j).Name == shape_name:
                        shape = page.Shapes.Item(j)
                        break
            
            if not shape:
                logger.warning(f"Shape not found: {shape_id or shape_name}")
                continue
            
            # Delete the shape
            shape.Delete()
    
    def _add_connections(self, doc, connections_info: List[Dict[str, Any]]):
        """Add connections between shapes in a Visio document."""
        for connection_info in connections_info:
            page_name = connection_info.get("page_name")
            page_index = connection_info.get("page_index", 1)
            from_shape_id = connection_info.get("from_shape_id")
            to_shape_id = connection_info.get("to_shape_id")
            from_shape_name = connection_info.get("from_shape_name")
            to_shape_name = connection_info.get("to_shape_name")
            
            # Get the page
            page = None
            if page_name:
                for i in range(1, doc.Pages.Count + 1):
                    if doc.Pages.Item(i).Name == page_name:
                        page = doc.Pages.Item(i)
                        break
            else:
                page = doc.Pages.Item(page_index)
            
            if not page:
                logger.warning(f"Page not found: {page_name or page_index}")
                continue
            
            # Find the from shape
            from_shape = None
            if from_shape_id:
                for j in range(1, page.Shapes.Count + 1):
                    if page.Shapes.Item(j).ID == from_shape_id:
                        from_shape = page.Shapes.Item(j)
                        break
            elif from_shape_name:
                for j in range(1, page.Shapes.Count + 1):
                    if page.Shapes.Item(j).Name == from_shape_name:
                        from_shape = page.Shapes.Item(j)
                        break
            
            if not from_shape:
                logger.warning(f"From shape not found: {from_shape_id or from_shape_name}")
                continue
            
            # Find the to shape
            to_shape = None
            if to_shape_id:
                for j in range(1, page.Shapes.Count + 1):
                    if page.Shapes.Item(j).ID == to_shape_id:
                        to_shape = page.Shapes.Item(j)
                        break
            elif to_shape_name:
                for j in range(1, page.Shapes.Count + 1):
                    if page.Shapes.Item(j).Name == to_shape_name:
                        to_shape = page.Shapes.Item(j)
                        break
            
            if not to_shape:
                logger.warning(f"To shape not found: {to_shape_id or to_shape_name}")
                continue
            
            # Connect the shapes
            connector = page.Drop(
                doc.Masters.ItemU("Dynamic connector"), 
                (from_shape.Cells("PinX").Result("") + to_shape.Cells("PinX").Result("")) / 2,
                (from_shape.Cells("PinY").Result("") + to_shape.Cells("PinY").Result("")) / 2
            )
            
            # Connect endpoints
            connector.CellsU("BeginX").GlueTo(from_shape.CellsSRC(1, 1, 0))
            connector.CellsU("EndX").GlueTo(to_shape.CellsSRC(1, 1, 0))
            
            # Set connector text if provided
            if "text" in connection_info:
                connector.Text = connection_info["text"]
    
    def generate_visio_diagram(self, instructions: Dict[str, Any], template: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a Visio diagram based on instructions.
        
        Args:
            instructions: Instructions for generating the diagram
            template: Optional template file path
            
        Returns:
            Dict with generated diagram content (base64 encoded)
        """
        doc = None
        temp_file = None
        
        try:
            self._ensure_visio_app()
            
            # Create a new document or use template
            if template and os.path.exists(template):
                doc = self.visio_app.Documents.Open(template)
            else:
                # Use default template
                doc = self.visio_app.Documents.Add("")
            
            # Generate diagram based on instructions
            if "title" in instructions:
                doc.Title = instructions["title"]
            
            if "pages" in instructions:
                self._generate_pages(doc, instructions["pages"])
            
            # Create temp file to save the result
            temp_file = tempfile.NamedTemporaryFile(suffix='.vsdx', delete=False)
            temp_file.close()
            
            # Save the document
            doc.SaveAs(temp_file.name)
            
            # Read the file content
            with open(temp_file.name, 'rb') as f:
                binary_content = f.read()
            
            # Encode to base64
            b64_content = base64.b64encode(binary_content).decode('utf-8')
            
            return {
                "status": "success",
                "message": "Diagram generated successfully",
                "file_content": b64_content
            }
            
        except Exception as e:
            logger.exception(f"Error generating Visio diagram: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate Visio diagram: {str(e)}"
            }
            
        finally:
            # Clean up
            if doc is not None:
                doc.Close()
            
            if temp_file is not None:
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def _generate_pages(self, doc, pages_info: List[Dict[str, Any]]):
        """Generate pages in a Visio document."""
        # Remove existing pages except the first one
        while doc.Pages.Count > 1:
            doc.Pages.Item(doc.Pages.Count).Delete()
        
        # Rename first page if exists
        if doc.Pages.Count > 0 and len(pages_info) > 0:
            doc.Pages.Item(1).Name = pages_info[0]["name"]
            
            # Add shapes to first page
            if "shapes" in pages_info[0]:
                self._add_shapes(doc, pages_info[0]["shapes"])
            
            # Add connections to first page
            if "connections" in pages_info[0]:
                self._add_connections(doc, pages_info[0]["connections"])
        
        # Add additional pages
        for i in range(1, len(pages_info)):
            page_info = pages_info[i]
            page = doc.Pages.Add()
            page.Name = page_info["name"]
            
            # Add shapes to this page
            if "shapes" in page_info:
                self._add_shapes(doc, page_info["shapes"])
            
            # Add connections to this page
            if "connections" in page_info:
                self._add_connections(doc, page_info["connections"])
    
    def get_active_document(self) -> Dict[str, Any]:
        """
        Get the active Visio document if available.
        
        Returns:
            Dict with status and active document information
        """
        try:
            self._ensure_visio_app()
            
            doc = self._get_active_document()
            if doc is None:
                return {
                    "status": "error",
                    "message": "No active Visio document found."
                }
            
            # Make sure Visio is visible
            self.visio_app.Visible = 1
            
            # Get information about the document without activating it
            doc_info = {
                "status": "success",
                "file_path": doc.FullName,
                "name": doc.Name,
                "pages_count": doc.Pages.Count,
                "message": f"Active document: {doc.Name}"
            }
            
            # Get basic information about pages
            doc_info["pages"] = []
            for i in range(1, doc.Pages.Count + 1):
                page = doc.Pages.Item(i)
                doc_info["pages"].append({
                    "name": page.Name,
                    "shapes_count": page.Shapes.Count
                })
            
            return doc_info
            
        except Exception as e:
            logger.exception(f"Error getting active document: {e}")
            return {
                "status": "error",
                "message": f"Failed to get active document: {str(e)}"
            }
    
    def verify_connections(self, file_path_or_content: str, connection_attempts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify if specific connections exist or can be created in a Visio diagram.
        
        Args:
            file_path_or_content: Path to the Visio file or base64-encoded content
            connection_attempts: List of connections to verify (with from_shape_id, to_shape_id, page_name)
            
        Returns:
            Dict with verification results
        """
        temp_file = None
        doc = None
        should_close_doc = False
        
        try:
            self._ensure_visio_app()
            
            # Determine if input is a path or content
            if os.path.exists(file_path_or_content):
                file_path = file_path_or_content
                # Try to get an already open document
                doc, should_close_doc = self._get_or_open_document(file_path)
                # Make Visio visible in case it's not
                self.visio_app.Visible = 1
                # No Activate() call - it's not needed and can cause errors
            else:
                # Assume it's base64 content and save to temp file
                binary_content = base64.b64decode(file_path_or_content)
                temp_file = tempfile.NamedTemporaryFile(suffix='.vsdx', delete=False)
                temp_file.write(binary_content)
                temp_file.close()
                file_path = temp_file.name
                
                # Open the document
                doc = self.visio_app.Documents.Open(file_path)
                should_close_doc = True
                # Make Visio visible
                self.visio_app.Visible = 1
            
            # Get connections analysis
            connections_analysis = self._analyze_diagram_connections(doc)
            existing_connections = connections_analysis.get("connections", [])
            
            verification_results = []
            
            for attempt in connection_attempts:
                from_shape_id = attempt.get("from_shape_id")
                to_shape_id = attempt.get("to_shape_id")
                page_name = attempt.get("page_name")
                
                # Check if the connection already exists
                connection_exists = False
                for conn in existing_connections:
                    if (conn.get("from_shape_id") == from_shape_id and 
                        conn.get("to_shape_id") == to_shape_id and
                        conn.get("page_name") == page_name):
                        connection_exists = True
                        break
                
                # Check if shapes exist and are on the same page
                shape_validation = self._validate_shapes_for_connection(doc, from_shape_id, to_shape_id, page_name)
                
                verification_results.append({
                    "from_shape_id": from_shape_id,
                    "to_shape_id": to_shape_id,
                    "page_name": page_name,
                    "connection_exists": connection_exists,
                    "shapes_valid": shape_validation.get("valid", False),
                    "validation_message": shape_validation.get("message", "")
                })
            
            return {
                "status": "success",
                "verification_results": verification_results
            }
            
        except Exception as e:
            logger.exception(f"Error verifying connections: {e}")
            return {
                "status": "error",
                "message": f"Failed to verify connections: {str(e)}"
            }
            
        finally:
            # Clean up temp files, but don't close the document if it was already open
            if temp_file is not None:
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            
            # Only close the document if it was opened by this function call
            if doc is not None and should_close_doc and temp_file is not None:
                try:
                    doc.Close()
                except:
                    pass
    
    def _validate_shapes_for_connection(self, doc, from_shape_id, to_shape_id, page_name) -> Dict[str, Any]:
        """Validate if shapes exist and can be connected."""
        try:
            # Find the page
            page = None
            for i in range(1, doc.Pages.Count + 1):
                p = doc.Pages.Item(i)
                if p.Name == page_name:
                    page = p
                    break
            
            if page is None:
                return {
                    "valid": False,
                    "message": f"Page '{page_name}' not found"
                }
            
            # Find the shapes
            from_shape = None
            to_shape = None
            
            for i in range(1, page.Shapes.Count + 1):
                shape = page.Shapes.Item(i)
                shape_id = str(shape.ID)
                
                if shape_id == from_shape_id:
                    from_shape = shape
                elif shape_id == to_shape_id:
                    to_shape = shape
                
                if from_shape is not None and to_shape is not None:
                    break
            
            if from_shape is None:
                return {
                    "valid": False,
                    "message": f"Source shape with ID '{from_shape_id}' not found on page '{page_name}'"
                }
                
            if to_shape is None:
                return {
                    "valid": False,
                    "message": f"Target shape with ID '{to_shape_id}' not found on page '{page_name}'"
                }
            
            return {
                "valid": True,
                "message": "Shapes are valid for connection"
            }
            
        except Exception as e:
            logger.exception(f"Error validating shapes for connection: {e}")
            return {
                "valid": False,
                "message": f"Error validating shapes: {str(e)}"
            } 