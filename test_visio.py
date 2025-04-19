#!/usr/bin/env python3
"""
Test script for working with the Visio MPC server using a real Visio file.
"""
import json
import requests
import uuid
import os
from pathlib import Path
import sys

# Add the src directory to the path
sys.path.append(os.path.abspath("src"))

# Define the MPC server URL (using port 8060)
MPC_SERVER_URL = "http://localhost:8060/sse"

# Default Visio file path
DEFAULT_VISIO_FILE = "C:\\Programming\\MPC Servers\\examples\\test1.vsdx"

def send_mpc_request(method, params=None):
    """Send a request to the MPC server and return the response."""
    if params is None:
        params = {}
    
    # Create a request message with a unique ID
    request = {
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params
    }
    
    print(f"Sending request: {json.dumps(request, indent=2)}")
    
    try:
        response = requests.post(MPC_SERVER_URL, json=request)
        response.raise_for_status()
        
        # Parse the SSE response
        print(f"Response status code: {response.status_code}")
        
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                data = json.dumps(json.loads(line[6:]), indent=2)
                print(f"Response data:\n{data}")
                return json.loads(line[6:])
        
        return {"error": {"code": -32603, "message": "No data received"}}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": {"code": -32603, "message": f"Error: {str(e)}"}}

def main():
    """Main entry point."""
    # Use the default Visio file path
    visio_file_path = DEFAULT_VISIO_FILE
    
    # Make sure the file exists
    if not os.path.exists(visio_file_path):
        print(f"Default file {visio_file_path} does not exist.")
        print("Please enter the path to your Visio file:")
        visio_file_path = input("> ")
        
        if not os.path.exists(visio_file_path):
            print(f"Error: File {visio_file_path} does not exist.")
            return
    
    print(f"Testing with Visio file: {visio_file_path}")
    
    # 1. Analyze the Visio diagram structure
    print("\n=== Analyzing Visio Diagram Structure ===")
    result = send_mpc_request("analyze_visio_diagram", {
        "file_path_or_content": visio_file_path,
        "analysis_type": "structure"
    })
    
    if "error" in result:
        print(f"Error analyzing diagram structure: {result['error']['message']}")
        return
    
    # Extract shape information for later use
    diagram_result = result.get("result", {})
    pages = diagram_result.get("results", {}).get("pages", [])
    shapes_by_id = {}
    
    for page in pages:
        for shape in page.get("shapes", []):
            shapes_by_id[shape["id"]] = {
                "name": shape["name"],
                "page_name": page["name"]
            }
    
    # Print a summary of the structure analysis
    total_shapes = diagram_result.get("results", {}).get("total_shapes", 0)
    print(f"Diagram has {len(pages)} pages and {total_shapes} total shapes.")
    for page in pages:
        print(f"- Page '{page['name']}' has {page['shapes_count']} shapes:")
        for shape in page.get("shapes", []):
            print(f"  * {shape['name']} (ID: {shape['id']}, Type: {shape['type']})")
    
    # 2. Add text to shapes
    if total_shapes > 0:
        print("\n=== Adding Text to Shapes ===")
        
        # Prepare update instructions
        update_shapes = []
        for shape_id, shape_info in shapes_by_id.items():
            update_shapes.append({
                "page_name": shape_info["page_name"],
                "shape_id": shape_id,
                "text": f"Shape {shape_id}: {shape_info['name']}"
            })
        
        # Send the modification request
        result = send_mpc_request("modify_visio_diagram", {
            "file_path_or_content": visio_file_path,
            "modification_instructions": {
                "update_shapes": update_shapes
            }
        })
        
        if "error" in result:
            print(f"Error adding text to shapes: {result['error']['message']}")
        else:
            print("Text added to shapes successfully!")
    
    # 3. Add a connection between shapes (if we have at least 2 shapes)
    if total_shapes >= 2:
        print("\n=== Adding Connection Between Shapes ===")
        
        # Get the first two shape IDs
        shape_ids = list(shapes_by_id.keys())
        first_shape_id = shape_ids[0]
        second_shape_id = shape_ids[1]
        page_name = shapes_by_id[first_shape_id]["page_name"]
        
        # Send the modification request
        result = send_mpc_request("modify_visio_diagram", {
            "file_path_or_content": visio_file_path,
            "modification_instructions": {
                "add_connections": [
                    {
                        "page_name": page_name,
                        "from_shape_id": first_shape_id,
                        "to_shape_id": second_shape_id,
                        "text": f"Connection from {shapes_by_id[first_shape_id]['name']} to {shapes_by_id[second_shape_id]['name']}"
                    }
                ]
            }
        })
        
        # Check if there was an actual error (from the server response)
        if "error" in result:
            print(f"Error adding connection: {result['error']['message']}")
        # Check the status from the result object
        elif "result" in result and result["result"].get("status") == "error":
            error_msg = result["result"].get("message", "Unknown error")
            print(f"Failed to add connection: {error_msg}")
        else:
            # Check if the modify operation was actually successful
            modify_status = result.get("result", {}).get("status", "unknown")
            if modify_status == "success":
                print("Connection added successfully!")
            else:
                print(f"Connection creation status: {modify_status}")
                print("Note: To verify if the connection was actually added, check the connection analysis below.")
    
    # 4. Analyze the Visio diagram connections again
    print("\n=== Analyzing Visio Diagram After Connection Creation ===")
    # Re-analyze the diagram to see if connections were created
    result = send_mpc_request("analyze_visio_diagram", {
        "file_path_or_content": visio_file_path
    })
    
    if "error" in result:
        print(f"Error analyzing Visio diagram: {result['error']['message']}")
    else:
        analysis = result["result"]
        shapes = analysis.get("shapes", [])
        
        print(f"Found {len(shapes)} shapes in the diagram")
        for shape in shapes:
            print(f"Shape ID: {shape.get('id')}, Name: {shape.get('name')}, Text: {shape.get('text', 'No text')}")
        
        # Create a dictionary of shapes by their IDs for later use
        shapes_by_id = {shape.get('id'): shape for shape in shapes}
        
        # Now analyze connections
        connections = analysis.get("connections", [])
        
        print(f"Found {len(connections)} connections in the diagram")
        for idx, connection in enumerate(connections, 1):
            from_shape = connection.get("from_shape_id")
            to_shape = connection.get("to_shape_id")
            conn_text = connection.get("text", "No text")
            
            from_shape_name = shapes_by_id.get(from_shape, {}).get("name", "Unknown")
            to_shape_name = shapes_by_id.get(to_shape, {}).get("name", "Unknown")
            
            print(f"  Connection {idx}: From '{from_shape_name}' (ID: {from_shape}) to '{to_shape_name}' (ID: {to_shape})")
            print(f"    Text: {conn_text}")
            
        if not connections:
        # Extract shape information for later use
        diagram_result = result.get("result", {})
        pages = diagram_result.get("results", {}).get("pages", [])
        shapes_by_id = {}
        
        for page in pages:
            for shape in page.get("shapes", []):
                shapes_by_id[shape["id"]] = {
                    "name": shape["name"],
                    "page_name": page["name"]
                }
        
        # Print a summary of the structure analysis
        total_shapes = diagram_result.get("results", {}).get("total_shapes", 0)
        print(f"Diagram has {len(pages)} pages and {total_shapes} total shapes.")
        for page in pages:
            print(f"- Page '{page['name']}' has {page['shapes_count']} shapes:")
            for shape in page.get("shapes", []):
                print(f"  * {shape['name']} (ID: {shape['id']}, Type: {shape['type']})")
    
    # 5. Analyze the Visio diagram text after the modifications
    print("\n=== Analyzing Visio Diagram Text After Modifications ===")
    result = send_mpc_request("analyze_visio_diagram", {
        "file_path_or_content": visio_file_path,
        "analysis_type": "text"
    })
    
    if "error" in result:
        print(f"Error analyzing diagram text: {result['error']['message']}")
    else:
        # Print a summary of the text analysis
        diagram_result = result.get("result", {})
        pages = diagram_result.get("results", {}).get("pages", [])
        total_text_shapes = diagram_result.get("results", {}).get("total_text_shapes", 0)
        
        print(f"Diagram has {total_text_shapes} total shapes with text.")
        for page in pages:
            text_shapes = page.get("text_shapes", [])
            print(f"- Page '{page['name']}' has {len(text_shapes)} shapes with text.")
            for shape in text_shapes:
                print(f"  * Shape '{shape['name']}' (ID: {shape['id']}) has text: '{shape['text']}'")

if __name__ == "__main__":
    main() 