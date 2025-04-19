#!/usr/bin/env python3
"""
Simple test script to verify the MPC server and Visio service are working properly.
"""
import json
import requests
import sys
import time

# Define the MPC server URL
MPC_SERVER_URL = "http://localhost:8050/sse"
VISIO_SERVICE_URL = "http://localhost:8051/health"

def print_colored(message, color="green"):
    """Print colored text."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{message}{colors['reset']}")

def test_visio_service():
    """Test the Visio service."""
    print_colored("\n=== Testing Visio Service ===", "blue")
    
    try:
        response = requests.get(VISIO_SERVICE_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_colored(f"✅ Visio Service is UP: {json.dumps(data, indent=2)}")
            return True
        else:
            print_colored(f"❌ Visio Service responded with status code: {response.status_code}", "red")
            return False
    except Exception as e:
        print_colored(f"❌ Error connecting to Visio Service: {e}", "red")
        print_colored("   Make sure the Visio Service is running on port 8051", "yellow")
        return False

def test_mpc_server():
    """Test the MPC server."""
    print_colored("\n=== Testing MPC Server ===", "blue")
    
    try:
        # Create a health check request
        request = {
            "id": "test-health",
            "method": "health",
            "params": {}
        }
        
        response = requests.post(MPC_SERVER_URL, json=request, timeout=5)
        
        if response.status_code == 200:
            # Parse the SSE response
            data = None
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    break
            
            if data and "result" in data:
                print_colored(f"✅ MPC Server is UP: {json.dumps(data, indent=2)}")
                return True
            else:
                print_colored("❌ MPC Server responded but with invalid data", "red")
                print_colored(f"Response: {response.text}", "yellow")
                return False
        else:
            print_colored(f"❌ MPC Server responded with status code: {response.status_code}", "red")
            return False
    except Exception as e:
        print_colored(f"❌ Error connecting to MPC Server: {e}", "red")
        print_colored("   Make sure the MPC Server is running on port 8050", "yellow")
        return False

def test_ping():
    """Test the MPC server ping method."""
    print_colored("\n=== Testing Ping Method ===", "blue")
    
    try:
        # Create a ping request
        request = {
            "id": "test-ping",
            "method": "ping",
            "params": {}
        }
        
        response = requests.post(MPC_SERVER_URL, json=request, timeout=5)
        
        if response.status_code == 200:
            # Parse the SSE response
            data = None
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    break
            
            if data and "result" in data and data["result"] == "pong":
                print_colored(f"✅ Ping successful: {json.dumps(data, indent=2)}")
                return True
            else:
                print_colored("❌ Ping failed", "red")
                print_colored(f"Response: {response.text}", "yellow")
                return False
        else:
            print_colored(f"❌ MPC Server responded with status code: {response.status_code}", "red")
            return False
    except Exception as e:
        print_colored(f"❌ Error connecting to MPC Server: {e}", "red")
        return False

def main():
    """Main entry point."""
    print_colored("MPC Docker Setup Test", "blue")
    print_colored("====================\n", "blue")
    
    # Test the Visio service
    visio_ok = test_visio_service()
    
    # Test the MPC server
    mpc_ok = test_mpc_server()
    
    # Test ping method if MPC server is up
    ping_ok = test_ping() if mpc_ok else False
    
    # Print summary
    print_colored("\n=== Test Summary ===", "blue")
    print_colored(f"Visio Service: {'✅ PASS' if visio_ok else '❌ FAIL'}", "green" if visio_ok else "red")
    print_colored(f"MPC Server: {'✅ PASS' if mpc_ok else '❌ FAIL'}", "green" if mpc_ok else "red")
    print_colored(f"Ping Test: {'✅ PASS' if ping_ok else '❌ FAIL'}", "green" if ping_ok else "red")
    
    if visio_ok and mpc_ok and ping_ok:
        print_colored("\n🎉 All tests passed! Your MPC Docker setup is working correctly.", "green")
        return 0
    else:
        print_colored("\n⚠️ Some tests failed. Check the logs above for details.", "yellow")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 