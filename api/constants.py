import os

IMG_EXT = ".jpg"
QR_EXT = ".png"
IMAGES_DIR = "images"
QR_DIR = "qr"

IMG_QTY = 20  # Number of images to show in the gallery
IMG_QTY_BUFFER = -1  # Number of additional images to keep in the directory

# Ensure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)
