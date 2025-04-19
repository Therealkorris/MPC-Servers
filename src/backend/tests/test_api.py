import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Create test uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
    
    def test_models_endpoint(self):
        # Test the models list endpoint
        response = self.client.get("/api/models")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))
        
        # Test getting a specific model
        response = self.client.get("/api/models/model1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], "model1")
    
    def test_sessions_endpoint(self):
        # Test sessions list endpoint
        response = self.client.get("/api/sessions")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))
        
        # Test creating a session
        response = self.client.post("/api/sessions?model_id=model1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["model_id"], "model1")
        self.assertEqual(response.json()["status"], "created")
        
        # Test getting a specific session
        session_id = "session1"  # Using a predefined session ID for testing
        response = self.client.get(f"/api/sessions/{session_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], session_id)
    
    def test_upload_endpoint(self):
        # Test the file upload endpoint
        # Create a simple test file
        with open("test_file.txt", "w") as f:
            f.write("test content")
        
        # Test the upload endpoint with the test file
        with open("test_file.txt", "rb") as f:
            response = self.client.post("/api/upload", files={"file": ("test_file.txt", f)})
            self.assertEqual(response.status_code, 200)
            self.assertIn("filename", response.json())
            self.assertEqual(response.json()["filename"], "test_file.txt")
        
        # Clean up the test file
        if os.path.exists("test_file.txt"):
            os.remove("test_file.txt")
    
    def test_vision_endpoints(self):
        # Test vision process endpoint
        test_data = {
            "image_url": "http://example.com/image.jpg",
            "settings": {"detect_objects": True, "extract_text": True}
        }
        response = self.client.post("/api/vision/process", json=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], "Image processed successfully")
        self.assertIn("data", response.json())
        self.assertIn("objects", response.json()["data"])
        self.assertIn("text", response.json()["data"])
        
        # Test vision analyze endpoint
        test_data = {
            "image_url": "http://example.com/image.jpg",
            "analysis_type": "general"
        }
        response = self.client.post("/api/vision/analyze", json=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertIn("result", response.json())
        
        # Test with OCR analysis type
        test_data["analysis_type"] = "ocr"
        response = self.client.post("/api/vision/analyze", json=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("text", response.json()["result"])

if __name__ == "__main__":
    unittest.main() 