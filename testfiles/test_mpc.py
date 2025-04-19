#!/usr/bin/env python3
"""
Simple test script to send a request to the MPC server.
"""
import json
import requests
import uuid

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
    
    # Send the request to the MPC server
    print(f"Sending request: {json.dumps(request, indent=2)}")
    
    try:
        response = requests.post(MPC_SERVER_URL, json=request)
        response.raise_for_status()
        
        # Parse the SSE response
        # The response is in SSE format: "data: {...}"
        print(f"Response status code: {response.status_code}")
        print(f"Raw response:\n{response.text}")
        
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                data = json.loads(line[6:])
                return data
        
        return {"error": {"code": -32603, "message": "No data received"}}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": {"code": -32603, "message": f"Error: {str(e)}"}}

def main():
    """Main entry point."""
    # Send a health check request
    result = send_mpc_request("health")
    print(f"Health check result: {json.dumps(result, indent=2)}")
    
    # Send a ping request
    result = send_mpc_request("ping")
    print(f"Ping result: {json.dumps(result, indent=2)}")
    
    # Try an invalid method
    result = send_mpc_request("invalid_method")
    print(f"Invalid method result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main() 