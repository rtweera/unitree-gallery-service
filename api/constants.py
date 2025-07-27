import os

IMG_EXT = ".jpg"
QR_EXT = ".png"
IMAGES_DIR = "images"
QR_DIR = "qr"

# Ensure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)
