import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

class TestMainAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_read_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Welcome to Visio AI API"})
    
    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})
    
    def test_process_endpoint(self):
        test_data = {
            "image_url": "http://example.com/image.jpg",
            "settings": {"param1": "value1"}
        }
        response = self.client.post("/api/process", json=test_data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["result"], "Processing completed successfully")
        self.assertEqual(response_data["processed_image_url"], "http://example.com/image.jpg")
    
    def test_api_endpoints(self):
        # Test that our API endpoints are registered correctly
        # Models endpoint
        response = self.client.get("/api/models")
        self.assertEqual(response.status_code, 200)
        
        # Sessions endpoint
        response = self.client.get("/api/sessions")
        self.assertEqual(response.status_code, 200)
        
        # Images endpoints
        response = self.client.get("/api/images/list")
        self.assertEqual(response.status_code, 200)
        
        # Vision endpoints
        test_data = {
            "image_url": "http://example.com/image.jpg",
            "settings": {"detect_objects": True}
        }
        response = self.client.post("/api/vision/process", json=test_data)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main() 