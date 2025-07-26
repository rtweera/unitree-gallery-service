import os
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from .services import get_images, save_image, get_image_path, generate_qr_code, get_basename_images

# from .service import ImageService

router = APIRouter()
templates = Jinja2Templates(directory="templates")
# Add custom filter
def basename_filter(path):
    return os.path.splitext(os.path.basename(path))[0]
templates.env.filters['basename'] = basename_filter


# STAT ENDPOINTS
# =========================
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Unitree Gallery Service is running"}

@router.get("/stats")
async def get_stats():
    """Get gallery statistics"""
    image_files = get_images()
    total_images = len(image_files)

    return {
        "images_exist": bool(image_files),
        "total_images": total_images,
        "image_files": image_files
    }
# =======================

# CONTROL ENDPOINTS
# =========================
@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file and save it locally in images folder"""
    try:
        # Read the uploaded file content
        content = await file.read()
        
        # Save the image to the images directory
        image_path = save_image(content)
        if not image_path:
            raise HTTPException(status_code=500, detail="Failed to save image")        
        return {
            "status": "Image captured and uploaded successfully",
            "path": image_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

@router.get("/image", response_class=FileResponse)
async def serve_latest_image():
    """Serve the saved image"""
    image_files = get_images()
    if not image_files:
        raise HTTPException(status_code=404, detail="No image found")
    return FileResponse(image_files[0], media_type="image/jpeg")


@router.get("/images/{image_id}", response_class=FileResponse)
async def serve_image(image_id: str):
    """Serve the saved image"""
    return FileResponse(get_image_path(image_id), media_type="image/jpeg")

@router.get("/download/{image_id}")
async def download_image(image_id: str):
    """Download the image file directly"""
    image_path = get_image_path(image_id)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(
        path=image_path,
        media_type='application/octet-stream',  # use 'image/jpeg' if you prefer
        filename=image_id,
        headers={"Content-Disposition": f'attachment; filename="{image_id}"'}
    )

@router.delete("/delete/{image_id}")
async def delete_image(image_id: str):
    """Delete the image file"""
    image_path = get_image_path(image_id)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    os.remove(image_path)
    return {"status": "success", "message": "Image deleted successfully"}

@router.delete("/delete")
async def delete_all_images():
    """Delete all images"""
    image_files = get_images()
    for image_path in image_files:
        os.remove(image_path)
    return {"status": "success", "message": "All images deleted successfully"}

@router.get("/qr/{image_id}")
async def get_qr_code(image_id: str):
    """Get the QR code for a specific image"""
    image_path = get_image_path(image_id + ".jpg")
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found")

    # Generate QR code pointing to the download URL
    qr_code_path = generate_qr_code(image_id)
    return FileResponse(qr_code_path, media_type="image/png")


# ====================


# SERVING ENDPOINTS 
# =================
@router.get("/")
async def redirect_to_latest():
    """Redirect to the latest image page"""
    return RedirectResponse(url="/latest", status_code=302)


@router.get("/latest", response_class=HTMLResponse)
async def single_photo_page(request: Request):
    """Serve the latest photo HTML page with the saved image"""
    # Check if image exists
    image_exists = bool(get_images())
    print(get_images())
    
    return templates.TemplateResponse("latest_image.html", {
        "request": request, 
        "image_exists": image_exists
    })


@router.get("/old-gallery", response_class=HTMLResponse)
async def old_gallery_page(request: Request):
    """Show all images in a gallery"""
    image_files = get_images()
    
    return templates.TemplateResponse("old_gallery.html", {
        "request": request,
        "image_urls": image_files,
        "images_exist": bool(image_files)
    })

@router.get("/gallery", response_class=HTMLResponse)
async def gallery_page(request: Request):
    """Show all images in a gallery"""
    image_files = get_basename_images()
    
    return templates.TemplateResponse("gallery.html", {
        "request": request,
        "image_urls": image_files,
        "images_exist": bool(image_files)
    })

# ====================