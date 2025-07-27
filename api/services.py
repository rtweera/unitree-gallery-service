import os
from uuid import uuid4
import qrcode
from dotenv import load_dotenv


load_dotenv(verbose=True, override=True)

# Ensure directories exist
IMAGES_DIR = "images"
QR_DIR = "qr"
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)

def get_images(images_dir: str = IMAGES_DIR):
    """Get a path list of all uploaded images"""
    image_files = sorted(
        [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith(".jpg")],
        key=lambda x: os.path.getmtime(x),
        reverse=True
    )
    return image_files

def get_basename_images(images_dir: str = IMAGES_DIR):
    """Get a list of image filenames without paths"""
    image_files = sorted(
        [f for f in os.listdir(images_dir) if f.endswith(".jpg")],
        key=lambda x: os.path.getmtime(os.path.join(images_dir, x)),
        reverse=True
    )
    return image_files

def save_image(image_data: bytes, images_dir: str = IMAGES_DIR) -> str:
    """Save an image to the images directory"""
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    image_id = uuid4()
    image_file_name = f"img_{image_id}.jpg"
    image_path = os.path.join(images_dir, image_file_name)
    
    with open(image_path, "wb") as f:
        f.write(image_data)
    
    return image_path

def get_image_path(image_id: str, images_dir: str = IMAGES_DIR) -> str:
    """Get the full path of an image by its ID"""
    return os.path.join(images_dir, image_id)


def generate_qr_code(image_id: str, image_extension: str = ".jpg", deployed_url: str = os.getenv("DEPLOYED_URL", ""), download_endpoint: str = "/download", qr_dir: str = QR_DIR) -> str:
    """Generate a QR code pointing to the download URL"""
    if not deployed_url:
        raise ValueError("DEPLOYED_URL environment variable is not set")
    qr_path = os.path.join(qr_dir, f"{image_id}.png")

    # Avoid regenerating if already exists
    # if not os.path.exists(qr_path):
    download_url = f"{deployed_url}{download_endpoint}/{image_id}{image_extension}"
    qr_img = qrcode.make(download_url)
    with open(qr_path, "wb") as qr_file:
        qr_img.save(qr_file)

    return os.path.join(qr_dir, f"{image_id}.png")
