#!/usr/bin/env python3
"""
Test script to verify that the Docker setup is working correctly.
This will test connectivity to both the MPC server and the Visio service.
"""
import json
import requests
import time
import sys

# Define the service URLs
MPC_SERVER_URL = "http://localhost:8050/sse"
VISIO_SERVICE_URL = "http://localhost:8051/health"

def test_mpc_server():
    """Test connection to the MPC server."""
    print("\n=== Testing MPC Server (port 8050) ===")
    
    try:
        # Create a simple health check request
        request = {
            "id": "test-docker-setup",
            "method": "health",
            "params": {}
        }
        
        print(f"Sending request to {MPC_SERVER_URL}...")
        response = requests.post(MPC_SERVER_URL, json=request, timeout=10)
        
        if response.status_code == 200:
            # Parse the SSE response
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    print(f"Response data: {json.dumps(data, indent=2)}")
                    
                    if "result" in data and data["result"].get("status") == "healthy":
                        print("✅ MPC Server is healthy and responding correctly!")
                        return True
                    else:
                        print("❌ MPC Server responded but may not be fully functional")
                        return False
            
            print("❌ MPC Server responded but returned no data")
            return False
        else:
            print(f"❌ MPC Server returned status code: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to MPC Server: {e}")
        return False

def test_visio_service():
    """Test connection to the Visio service."""
    print("\n=== Testing Visio Service (port 8051) ===")
    
    try:
        print(f"Sending request to {VISIO_SERVICE_URL}...")
        response = requests.get(VISIO_SERVICE_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            if data.get("status") == "healthy":
                print("✅ Visio Service is healthy and responding correctly!")
                return True
            else:
                print("❌ Visio Service responded but may not be fully functional")
                return False
        else:
            print(f"❌ Visio Service returned status code: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Visio Service: {e}")
        return False

def test_integration():
    """Test that the MPC server can communicate with the Visio service."""
    print("\n=== Testing MPC Server to Visio Service Integration ===")
    
    try:
        # Create a request to get active Visio document, which requires communication between services
        request = {
            "id": "test-integration",
            "method": "get_active_document",
            "params": {}
        }
        
        print(f"Sending integration test request to {MPC_SERVER_URL}...")
        response = requests.post(MPC_SERVER_URL, json=request, timeout=10)
        
        if response.status_code == 200:
            # Parse the SSE response
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    print(f"Response data: {json.dumps(data, indent=2)}")
                    
                    if "error" not in data:
                        print("✅ Integration test passed! MPC Server can communicate with Visio Service.")
                        return True
                    else:
                        print("❌ Integration test failed. MPC Server cannot communicate with Visio Service.")
                        print(f"Error: {data.get('error', {}).get('message', 'Unknown error')}")
                        return False
            
            print("❌ MPC Server responded but returned no data")
            return False
        else:
            print(f"❌ MPC Server returned status code: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        return False

def main():
    """Main entry point."""
    print("=== Docker Setup Test ===")
    print("Testing connectivity to services...")
    
    # Wait a bit for services to be fully up
    print("Waiting 3 seconds for services to initialize...")
    time.sleep(3)
    
    # Test MPC Server
    mpc_server_ok = test_mpc_server()
    
    # Test Visio Service
    visio_service_ok = test_visio_service()
    
    # Test integration between services
    if mpc_server_ok and visio_service_ok:
        integration_ok = test_integration()
    else:
        integration_ok = False
        print("\n❌ Skipping integration test because one or both services are not responding")
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"MPC Server (port 8050): {'✅ OK' if mpc_server_ok else '❌ Failed'}")
    print(f"Visio Service (port 8051): {'✅ OK' if visio_service_ok else '❌ Failed'}")
    print(f"Integration between services: {'✅ OK' if integration_ok else '❌ Failed'}")
    
    if mpc_server_ok and visio_service_ok and integration_ok:
        print("\n🎉 SUCCESS! The Docker setup is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 