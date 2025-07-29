import os
from datetime import datetime
from uuid import uuid4
import qrcode 
from dotenv import load_dotenv
import pytz
from .constants import IMG_EXT, QR_EXT, IMAGES_DIR, QR_DIR, IMG_QTY, IMG_QTY_BUFFER


load_dotenv(verbose=True, override=True)

def get_image_stats(image_path: str) -> dict:
    """Get image file name and last modified time"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file {image_path} does not exist")
    
    last_modified = os.path.getmtime(image_path)

    return {
        "filename": os.path.basename(image_path),
        "last_modified": datetime.fromtimestamp(last_modified, tz=pytz.timezone("Asia/Colombo")).strftime('%Y-%m-%d %H:%M:%S'),
        "size_in_bytes": os.path.getsize(image_path)
    }

def get_qr_stats(qr_path: str) -> dict:
    """Get QR code file name and last modified time"""
    if not os.path.exists(qr_path):
        raise FileNotFoundError(f"QR code file {qr_path} does not exist")

    last_modified = os.path.getmtime(qr_path)

    return {
        "filename": os.path.basename(qr_path),
        "last_modified": datetime.fromtimestamp(last_modified, tz=pytz.timezone("Asia/Colombo")).strftime('%Y-%m-%d %H:%M:%S'),
        "size_in_bytes": os.path.getsize(qr_path)
    }

def get_images(images_dir: str = IMAGES_DIR):
    """Get a path list of all uploaded images"""
    image_files = sorted(
        [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith(IMG_EXT)],
        key=lambda x: os.path.getmtime(x),
        reverse=True
    )
    return image_files

def get_qr_files(qr_dir: str = QR_DIR):
    """Get a path list of all generated QR codes"""
    qr_files = sorted(
        [os.path.join(qr_dir, f) for f in os.listdir(qr_dir) if f.endswith(QR_EXT)],
        key=lambda x: os.path.getmtime(x),
        reverse=True
    )
    return qr_files

def get_basename_images(images_dir: str = IMAGES_DIR):
    """Get a list of image filenames without paths (latest 20 only)"""
    image_files = sorted(
        [os.path.splitext(f)[0] for f in os.listdir(images_dir) if f.endswith(IMG_EXT)],
        key=lambda x: os.path.getmtime(os.path.join(images_dir, x + IMG_EXT)),
        reverse=True
    )[:IMG_QTY]  
    return image_files

def save_image(image_data: bytes, images_dir: str = IMAGES_DIR) -> str:
    """Save an image to the images directory"""
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    image_id = f"img_{uuid4()}"
    image_file_name = f"{image_id}{IMG_EXT}"
    image_path = os.path.join(images_dir, image_file_name)
    
    with open(image_path, "wb") as f:
        f.write(image_data)
    
    return str(image_id)

def get_image_path(image_id: str, images_dir: str = IMAGES_DIR) -> str:
    """Get the full path of an image by its ID"""
    return os.path.join(images_dir, image_id)

def get_qr_path(image_id: str, qr_dir: str = QR_DIR) -> str:
    """Get the full path of a QR code image by its ID"""
    return os.path.join(qr_dir, f"{image_id}")

def generate_qr_code(image_id: str, deployed_url: str = os.getenv("DEPLOYED_URL", ""), download_endpoint: str = "/download", qr_dir: str = QR_DIR, qr_ext: str = QR_EXT) -> str:
    """Generate a QR code pointing to the download URL"""
    if not deployed_url:
        raise ValueError("DEPLOYED_URL environment variable is not set")
    qr_path = os.path.join(qr_dir, f"{image_id}{qr_ext}")

    # Avoid regenerating if already exists
    # if not os.path.exists(qr_path):
    download_url = f"{deployed_url}{download_endpoint}/{image_id}"
    qr_img = qrcode.make(download_url)
    with open(qr_path, "wb") as qr_file:
        qr_img.save(qr_file)
    return qr_path

def delete_old_images(images_dir: str = IMAGES_DIR, img_qty: int = IMG_QTY, img_qty_buffer: int = IMG_QTY_BUFFER):
    """Delete old images to maintain a maximum number of images"""
    image_files = get_images(images_dir)
    qr_files = get_qr_files(QR_DIR)
    if len(image_files) > img_qty + img_qty_buffer:
        for file_path in image_files[img_qty + img_qty_buffer:]:
            os.remove(file_path)
            print(f"Deleted old image: {file_path}")
    if len(qr_files) > img_qty + img_qty_buffer:
        for file_path in qr_files[img_qty + img_qty_buffer:]:
            os.remove(file_path)
            print(f"Deleted old QR code: {file_path}")