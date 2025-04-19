#!/usr/bin/env python3
"""
Script to edit a Visio file using the MPC Visio implementation.
This script will:
1. Connect to an open Visio file
2. Analyze the structure of the diagram
3. Add connections between shapes
"""
import json
import requests
import uuid
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.abspath("src"))

# Define the MPC server URL
MPC_SERVER_URL = "http://localhost:8050/sse"

# Default Visio file path
DEFAULT_VISIO_FILE = os.path.abspath("examples/test1.vsdx")

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
                data = json.loads(line[6:])
                print(f"Response data:\n{json.dumps(data, indent=2)}")
                return data
        
        return {"error": {"code": -32603, "message": "No data received"}}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": {"code": -32603, "message": f"Error: {str(e)}"}}

def get_active_document():
    """Get the currently active Visio document.
    
    First tries to get any active document through the API,
    then falls back to using the default test file,
    and finally asks the user for a file path.
    """
    print("Trying to get active Visio document...")
    
    # Try getting the active document through the API
    result = send_mpc_request("get_active_document")
    if "error" not in result and result.get("result", {}).get("status") == "success":
        file_path = result.get("result", {}).get("file_path")
        print(f"Found active Visio document: {file_path}")
        print(f"Document has {result.get('result', {}).get('pages_count', 0)} pages")
        return file_path
    
    # If no active document, try using the default test file
    if os.path.exists(DEFAULT_VISIO_FILE):
        print(f"Using default test file: {DEFAULT_VISIO_FILE}")
        return DEFAULT_VISIO_FILE
    
    # Finally, ask the user for a file path
    print("No active document found. Please enter the path to your Visio file:")
    file_path = input("> ")
    
    if os.path.exists(file_path):
        return file_path
    else:
        print(f"Error: File {file_path} does not exist.")
        return None

def analyze_visio_diagram(file_path):
    """Analyze the structure of the Visio diagram."""
    print("\n=== Analyzing Visio Diagram Structure ===")
    result = send_mpc_request("analyze_visio_diagram", {
        "file_path_or_content": file_path,
        "analysis_type": "structure"
    })
    
    if "error" in result:
        print(f"Error analyzing diagram structure: {result['error']['message']}")
        return None
    
    return result.get("result", {})

def analyze_connections(file_path):
    """Analyze the connections in the Visio diagram."""
    print("\n=== Analyzing Visio Diagram Connections ===")
    result = send_mpc_request("analyze_visio_diagram", {
        "file_path_or_content": file_path,
        "analysis_type": "connections"
    })
    
    if "error" in result:
        print(f"Error analyzing connections: {result['error']['message']}")
        return None
    
    return result.get("result", {})

def add_connection(file_path, from_shape_id, to_shape_id, page_name, connection_text="Connection"):
    """Add a connection between two shapes."""
    print(f"\n=== Adding Connection: {from_shape_id} -> {to_shape_id} ===")
    result = send_mpc_request("modify_visio_diagram", {
        "file_path_or_content": file_path,
        "modification_instructions": {
            "add_connections": [
                {
                    "page_name": page_name,
                    "from_shape_id": from_shape_id,
                    "to_shape_id": to_shape_id,
                    "text": connection_text
                }
            ]
        }
    })
    
    if "error" in result:
        print(f"Error adding connection: {result['error']['message']}")
        return False
    
    modify_status = result.get("result", {}).get("status", "unknown")
    if modify_status == "success":
        print("Connection added successfully!")
        return True
    else:
        print(f"Connection creation status: {modify_status}")
        return False

def add_text_to_shapes(file_path, shapes_by_id):
    """Add text to shapes in the diagram."""
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
        "file_path_or_content": file_path,
        "modification_instructions": {
            "update_shapes": update_shapes
        }
    })
    
    if "error" in result:
        print(f"Error adding text to shapes: {result['error']['message']}")
        return False
    
    print("Text added to shapes successfully!")
    return True

def main():
    """Main entry point."""
    # Check if the MPC server is running
    print("Checking MPC server health...")
    result = send_mpc_request("health")
    if "error" in result:
        print(f"MPC server not responding: {result['error']['message']}")
        print("Please make sure the MPC server is running on port 8050")
        return
    
    # Get the active document or prompt for a file path
    file_path = get_active_document()
    if not file_path:
        return
    
    print(f"Working with Visio file: {file_path}")
    
    # Analyze the diagram structure
    diagram_result = analyze_visio_diagram(file_path)
    if not diagram_result:
        return
    
    # Extract shape information
    pages = diagram_result.get("results", {}).get("pages", [])
    shapes_by_id = {}
    
    for page in pages:
        for shape in page.get("shapes", []):
            shapes_by_id[shape["id"]] = {
                "name": shape["name"],
                "page_name": page["name"],
                "type": shape["type"]
            }
    
    # Print a summary of the structure analysis
    total_shapes = diagram_result.get("results", {}).get("total_shapes", 0)
    print(f"Diagram has {len(pages)} pages and {total_shapes} total shapes.")
    for page in pages:
        print(f"- Page '{page['name']}' has {page['shapes_count']} shapes:")
        for shape in page.get("shapes", []):
            print(f"  * {shape['name']} (ID: {shape['id']}, Type: {shape['type']})")
    
    # Add text to shapes if requested
    add_text = input("\nWould you like to add text to shapes? (y/n): ")
    if add_text.lower() == 'y':
        add_text_to_shapes(file_path, shapes_by_id)
    
    # Add connections if there are at least 2 shapes
    if total_shapes >= 2:
        add_conn = input("\nWould you like to add connections between shapes? (y/n): ")
        if add_conn.lower() == 'y':
            shape_ids = list(shapes_by_id.keys())
            
            while True:
                print("\nAvailable shapes:")
                for i, shape_id in enumerate(shape_ids, 1):
                    print(f"{i}. {shapes_by_id[shape_id]['name']} (ID: {shape_id})")
                
                try:
                    from_idx = int(input("\nSelect the source shape (number): ")) - 1
                    to_idx = int(input("Select the target shape (number): ")) - 1
                    
                    if 0 <= from_idx < len(shape_ids) and 0 <= to_idx < len(shape_ids):
                        from_shape_id = shape_ids[from_idx]
                        to_shape_id = shape_ids[to_idx]
                        page_name = shapes_by_id[from_shape_id]["page_name"]
                        
                        conn_text = input("Enter text for the connection (or press Enter for default): ")
                        if not conn_text:
                            conn_text = f"Connection from {shapes_by_id[from_shape_id]['name']} to {shapes_by_id[to_shape_id]['name']}"
                        
                        add_connection(file_path, from_shape_id, to_shape_id, page_name, conn_text)
                    else:
                        print("Invalid selection. Please choose valid shape numbers.")
                except ValueError:
                    print("Invalid input. Please enter numbers.")
                
                another = input("\nAdd another connection? (y/n): ")
                if another.lower() != 'y':
                    break
    
    # Analyze connections after modifications
    analyze_connections(file_path)
    
    print("\nVisio editing complete!")

if __name__ == "__main__":
    main() 