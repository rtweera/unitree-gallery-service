import os
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from datetime import datetime
import pytz
from .services import get_images, save_image, get_image_path, generate_qr_code, get_basename_images, get_qr_path, get_qr_files, get_image_stats, get_qr_stats
from .constants import IMG_EXT, QR_EXT

load_dotenv(verbose=True, override=True)

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
    qr_files = get_qr_files()
    total_images = len(image_files)
    total_qr_codes = len(qr_files)
    image_stats = []
    qr_stats = []
    for image_path in image_files:
        try:
            image_stats.append(get_image_stats(image_path))
        except FileNotFoundError:
            image_stats.append({
                "filename": os.path.basename(image_path),
                "last_modified": "N/A",
                "size_in_bytes": -1,
                "error": "error fetching file stats"
            })
    for qr_path in qr_files:
        try:
            qr_stats.append(get_qr_stats(qr_path))
        except FileNotFoundError:
            qr_stats.append({
                "filename": os.path.basename(qr_path),
                "last_modified": "N/A",
                "size_in_bytes": -1,
                "error": "error fetching file stats"
            })
    return {
        "images_exist": bool(image_files),
        "total_images": total_images,
        "image_files": image_files,
        "image_stats": image_stats,
        "total_qr_codes": total_qr_codes,
        "qr_files": qr_files,
        "qr_stats": qr_stats
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
        image_id = save_image(content)
        if not image_id:
            raise HTTPException(status_code=500, detail="Failed to save image")
        return {
            "status": "Image captured and uploaded successfully",
            "id": image_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

@router.get("/images/latest", response_class=FileResponse)
async def serve_latest_image():
    """Serve the saved image"""
    image_files = get_images()
    if not image_files:
        raise HTTPException(status_code=404, detail="No image found")
    return FileResponse(image_files[0], media_type="image/jpeg")

@router.get("/images/{image_id}", response_class=FileResponse)
async def serve_image(image_id: str):
    """Serve the saved image"""
    return FileResponse(get_image_path(image_id + IMG_EXT), media_type="image/jpeg")

@router.get("/download/{image_id}")
async def download_image(image_id: str, rename_file: bool = True):
    """Download the image file directly"""
    image_path = get_image_path(image_id + IMG_EXT)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    if rename_file:
        now = datetime.now(pytz.timezone("Asia/Colombo"))
        timestamp = now.strftime("%Y%m%d_%H%M%S_%Z")
        file_name = f"Oxys adventures_{timestamp}{IMG_EXT}"
    else:
        file_name = f"{image_id}{IMG_EXT}"

    print(f"Downloading image: {image_path} as {file_name}")
    return FileResponse(
        path=image_path,
        media_type='application/octet-stream',  # use 'image/jpeg' if you prefer
        filename=file_name,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'}
    )

@router.delete("/images/all")
async def delete_all_images():
    """Delete all images"""
    if not os.getenv("ENABLE_DELETE_ALL", "False").lower() == "true":
        raise HTTPException(status_code=503, detail="This endpoint has been disabled")
    image_files = get_images()
    qr_files = get_qr_files()
    for image_path in image_files:
        os.remove(image_path)
    for qr_path in qr_files:
        os.remove(qr_path)
    return {"status": "success", "message": "All images deleted successfully"}

@router.delete("/images/{image_id}")
async def delete_image(image_id: str):
    """Delete the image file"""
    image_path = get_image_path(image_id + IMG_EXT)
    qr_path = get_qr_path(image_id + QR_EXT)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found")

    os.remove(image_path)
    if os.path.exists(qr_path):
        os.remove(qr_path)
    return {"status": "success", "message": "Image deleted successfully"}


@router.get("/qr/{image_id}")
async def get_qr_code(image_id: str):
    """Get the QR code for a specific image"""
    image_path = get_image_path(image_id + IMG_EXT)
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
    """Redirect to the gallery images page"""
    return RedirectResponse(url="/gallery", status_code=302)


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