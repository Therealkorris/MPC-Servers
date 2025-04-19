#!/usr/bin/env python3
"""
Example MPC client that connects to the MPC Visio server.
"""
import json
import requests
import uuid
import sys

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
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                data = json.loads(line[6:])
                return data
        
        return {"error": {"code": -32603, "message": "No data received"}}
    except Exception as e:
        return {"error": {"code": -32603, "message": f"Error: {str(e)}"}}

def analyze_visio_diagram(file_path, analysis_type="structure"):
    """Analyze a Visio diagram using the MPC server."""
    return send_mpc_request("analyze_visio_diagram", {
        "file_path_or_content": file_path,
        "analysis_type": analysis_type
    })

def ask_ai_about_visio(messages, model="llama3"):
    """Ask AI a question about a Visio diagram."""
    return send_mpc_request("ask_ai_about_visio", {
        "messages": messages,
        "model": model
    })

def main():
    """Main entry point for the example client."""
    if len(sys.argv) < 2:
        print("Usage: python mpc_client.py <command> [arguments...]")
        print("Commands:")
        print("  analyze <file_path> [analysis_type]")
        print("  ask <file_path> <question>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: python mpc_client.py analyze <file_path> [analysis_type]")
            sys.exit(1)
        
        file_path = sys.argv[2]
        analysis_type = sys.argv[3] if len(sys.argv) > 3 else "structure"
        
        result = analyze_visio_diagram(file_path, analysis_type)
        print(json.dumps(result, indent=2))
    
    elif command == "ask":
        if len(sys.argv) < 4:
            print("Usage: python mpc_client.py ask <file_path> <question>")
            sys.exit(1)
        
        file_path = sys.argv[2]
        question = sys.argv[3]
        
        # First analyze the diagram
        analyze_result = analyze_visio_diagram(file_path)
        
        if "error" in analyze_result:
            print(json.dumps(analyze_result, indent=2))
            sys.exit(1)
        
        # Then ask the question
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that helps with analyzing Visio diagrams."
            },
            {
                "role": "user",
                "content": f"I have a Visio diagram with the following structure: {json.dumps(analyze_result.get('result', {}))}. {question}"
            }
        ]
        
        result = ask_ai_about_visio(messages)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        print("Commands:")
        print("  analyze <file_path> [analysis_type]")
        print("  ask <file_path> <question>")
        sys.exit(1)

if __name__ == "__main__":
    main() 