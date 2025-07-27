from PIL import Image, ImageDraw, ImageFont
import os


def load_font(font_size):
    """Load font with fallback options"""
    font_options = [
        "arial.ttf", "Arial.ttf", "calibri.ttf", "Calibri.ttf",
        "helvetica.ttf", "Helvetica.ttf", "verdana.ttf", "Verdana.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "C:/Windows/Fonts/arial.ttf"  # Windows
    ]
    
    for font_option in font_options:
        try:
            return ImageFont.truetype(font_option, font_size)
        except (OSError, IOError):
            continue
    
    return ImageFont.load_default()


def save_image_watermark(image, output_path, original_size):
    """Save image with appropriate format conversion"""
    output_extension = os.path.splitext(output_path)[1].lower()
    
    if output_extension in ['.jpg', '.jpeg']:
        output_image = image.convert('RGB')
        save_format = 'JPEG'
    elif output_extension == '.png':
        output_image = image
        save_format = 'PNG'
    elif output_extension in ['.bmp', '.tiff', '.tif']:
        output_image = image.convert('RGB')
        save_format = output_extension[1:].upper()
    elif output_extension == '.webp':
        output_image = image
        save_format = 'WebP'
    elif output_extension == '.gif':
        output_image = image.convert('P', palette=Image.Palette.ADAPTIVE)
        save_format = 'GIF'
    else:
        output_image = image
        save_format = 'PNG'
    
    try:
        output_image.save(output_path, format=save_format, quality=95)
        print(f"Image saved with preserved dimensions: {original_size[0]}x{original_size[1]}")
        return output_path
    except Exception:
        png_path = os.path.splitext(output_path)[0] + '.png'
        image.save(png_path, format='PNG')
        print(f"Image saved as PNG with preserved dimensions: {original_size[0]}x{original_size[1]}")
        return png_path


def draw_rounded_rectangle(draw, x1, y1, x2, y2, radius, fill):
    """Draw a rounded rectangle"""
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    
    draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill)


def draw_rounded_rectangle_border(draw, x1, y1, x2, y2, radius, outline, width):
    """Draw a rounded rectangle border"""
    for i in range(width):
        offset = i
        draw.line([x1 + radius, y1 - offset, x2 - radius, y1 - offset], fill=outline, width=1)
        draw.line([x1 + radius, y2 + offset, x2 - radius, y2 + offset], fill=outline, width=1)
        draw.line([x1 - offset, y1 + radius, x1 - offset, y2 - radius], fill=outline, width=1)
        draw.line([x2 + offset, y1 + radius, x2 + offset, y2 - radius], fill=outline, width=1)
        
        draw.arc([x1 - offset, y1 - offset, x1 + 2*radius + offset, y1 + 2*radius + offset], 
                180, 270, fill=outline, width=1)
        draw.arc([x2 - 2*radius - offset, y1 - offset, x2 + offset, y1 + 2*radius + offset], 
                270, 360, fill=outline, width=1)
        draw.arc([x1 - offset, y2 - 2*radius - offset, x1 + 2*radius + offset, y2 + offset], 
                90, 180, fill=outline, width=1)
        draw.arc([x2 - 2*radius - offset, y2 - 2*radius - offset, x2 + offset, y2 + offset], 
                0, 90, fill=outline, width=1)