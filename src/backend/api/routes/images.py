from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
import os
import aiofiles
from pathlib import Path

router = APIRouter(prefix="/images", tags=["images"])

# Ensure uploads directory exists
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file."""
    try:
        # Validate file is an image
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        file_location = f"uploads/{file.filename}"
        
        async with aiofiles.open(file_location, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
        
        return {
            "status": "success",
            "filename": file.filename, 
            "file_path": f"/uploads/{file.filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")

@router.get("/list")
async def list_images():
    """List all uploaded images."""
    try:
        images = []
        for file in os.listdir("uploads"):
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
                images.append({
                    "filename": file,
                    "path": f"/uploads/{file}",
                    "size": os.path.getsize(f"uploads/{file}")
                })
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")

@router.get("/{filename}")
async def get_image_info(filename: str):
    """Get information about a specific image."""
    try:
        file_path = f"uploads/{filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
            
        return {
            "filename": filename,
            "path": f"/uploads/{filename}",
            "size": os.path.getsize(file_path),
            "created": os.path.getctime(file_path),
            "modified": os.path.getmtime(file_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving image info: {str(e)}")

@router.delete("/{filename}")
async def delete_image(filename: str):
    """Delete a specific image."""
    try:
        file_path = f"uploads/{filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
            
        os.remove(file_path)
        return {"status": "success", "message": f"Image {filename} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}") 