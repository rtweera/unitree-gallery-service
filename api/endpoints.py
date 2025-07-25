import os
from typing import List
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
# from .service import ImageService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Ensure images directory exists
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file and save it locally in images folder"""
    try:
        # Read the uploaded file content
        content = await file.read()
        
        # Save the image to the images directory
        image_path = os.path.join(IMAGES_DIR, "img.jpg")
        with open(image_path, "wb") as f:
            f.write(content)
        
        return {
            "status": "Image captured and uploaded successfully",
            "path": image_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")
    
@router.get("/image")
async def serve_image():
    """Serve the saved image"""
    image_path = os.path.join(IMAGES_DIR, "img.jpg")
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="No image found")
    
    from fastapi.responses import FileResponse
    return FileResponse(image_path, media_type="image/jpeg")

@router.get("/", response_class=HTMLResponse)
async def gallery_page(request: Request):
    """Serve the gallery HTML page with the saved image"""
    # Check if image exists
    image_path = os.path.join(IMAGES_DIR, "img.jpg")
    image_exists = os.path.exists(image_path)
    
    return templates.TemplateResponse("simple_gallery.html", {
        "request": request, 
        "image_exists": image_exists
    })

