#!/usr/bin/env python3
"""
Test script for working with files in the Docker container.
"""
import json
import requests
import uuid
import os
import sys
from pathlib import Path

# Define the MPC server URL
MPC_SERVER_URL = "http://localhost:8050/sse"

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

def main():
    """Main function to test Docker file access."""
    print("Testing Docker file access...")
    
    # Use a path in the Docker container's mounted volume
    docker_file_path = "/app/examples/test1.vsdx"
    print(f"Using Docker file path: {docker_file_path}")
    
    # First analyze the document
    print("\nAnalyzing diagram structure using Docker path...")
    result = send_mpc_request("analyze_visio_diagram", {
        "file_path_or_content": docker_file_path,
        "analysis_type": "structure"
    })
    
    if "error" in result:
        print(f"Error analyzing diagram: {result['error']['message']}")
        return
    
    # Get the shape IDs
    shapes = []
    pages = result.get("result", {}).get("results", {}).get("pages", [])
    for page in pages:
        page_name = page["name"]
        for shape in page.get("shapes", []):
            shapes.append({
                "id": shape["id"],
                "name": shape["name"],
                "page_name": page_name
            })
    
    if len(shapes) < 2:
        print("Need at least 2 shapes to create a connection.")
        return
    
    # Select the first two shapes that are not already connectors
    regular_shapes = [s for s in shapes if not s["name"].startswith("Dynamisk kobling")]
    if len(regular_shapes) < 2:
        print("Need at least 2 non-connector shapes.")
        return
    
    from_shape = regular_shapes[0]
    to_shape = regular_shapes[1]
    
    # Add a connection between the shapes
    print(f"\nAdding connection from {from_shape['name']} to {to_shape['name']} using Docker path...")
    result = send_mpc_request("modify_visio_diagram", {
        "file_path_or_content": docker_file_path,
        "modification_instructions": {
            "add_connections": [
                {
                    "page_name": from_shape["page_name"],
                    "from_shape_id": from_shape["id"],
                    "to_shape_id": to_shape["id"],
                    "text": f"Docker connection from {from_shape['name']} to {to_shape['name']}"
                }
            ]
        }
    })
    
    if "error" in result:
        print(f"Error adding connection: {result['error']['message']}")
    else:
        status = result.get("result", {}).get("status")
        print(f"Connection status: {status}")
        print("The connection should now be visible in the Visio application.")

if __name__ == "__main__":
    main() 