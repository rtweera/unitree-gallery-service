from PIL import Image, ImageDraw
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.image_utils import load_font, save_image, draw_rounded_rectangle, draw_rounded_rectangle_border

def add_watermark_with_logo(image_path, 
                           watermark_text="Snapped by Oxy's at WSO2Con Asia",
                           output_path=None,
                           font_size=30,
                           font_color=(255, 255, 255),
                           add_box=True,
                           box_color=(0, 0, 0),
                           box_opacity=120,
                           box_padding=20,
                           box_border=True,
                           border_color=(200, 200, 200),
                           border_width=1,
                           box_rounded=True,
                           corner_radius=8,
                           position='bottom-right',
                           logo_path=None,
                           logo_position='top-left',
                           logo_size=(400, 400),
                           logo_opacity=255,
                           logo_margin=20,
                           preserve_logo_aspect=True):
    """
    Add a text watermark and logo to an image with optional background box.
    Preserves original image dimensions and aspect ratio.
    
    Args:
        image_path (str): Path to the input image
        watermark_text (str): Text to use as watermark
        output_path (str, optional): Path to save the watermarked image
        font_size (int): Size of the watermark font
        font_color (tuple): RGB color of the watermark text
        add_box (bool): Whether to add a background box behind text
        box_color (tuple): RGB color of the background box
        box_opacity (int): Transparency of background box (0-255)
        box_padding (int): Padding around text inside the box
        box_border (bool): Whether to add a border around the box
        border_color (tuple): RGB color of the border
        border_width (int): Width of the border in pixels
        box_rounded (bool): Whether to use rounded corners
        corner_radius (int): Radius for rounded corners
        position (str): Position of watermark ('top-left', 'top-right', 'bottom-left', 'bottom-right', 'center')
        logo_path (str, optional): Path to logo image file
        logo_position (str): Position of logo
        logo_size (tuple): Maximum size to resize logo to (width, height)
        logo_opacity (int): Transparency of logo (0-255)
        logo_margin (int): Margin from edges for logo placement
        preserve_logo_aspect (bool): Whether to preserve logo aspect ratio when resizing
    
    Returns:
        PIL.Image or str: Watermarked image object if output_path is None, else path to saved image
    """
    
    try:
        # Open and prepare the image
        original_image = Image.open(image_path)
        original_size = original_image.size
        print(f"Original image dimensions: {original_size[0]}x{original_size[1]}")
        
        # Convert to RGBA for processing while maintaining original size
        working_image = original_image.convert('RGBA')
        
        # Create transparent overlay for watermark and logo
        overlay_layer = Image.new('RGBA', original_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay_layer)
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path).convert('RGBA')
                original_logo_size = logo.size
                print(f"Original logo dimensions: {original_logo_size[0]}x{original_logo_size[1]}")
                
                # Resize logo while preserving aspect ratio
                if logo_size and preserve_logo_aspect:
                    logo_aspect = original_logo_size[0] / original_logo_size[1]
                    target_width, target_height = logo_size
                    
                    if target_width / target_height > logo_aspect:
                        new_height = target_height
                        new_width = int(target_height * logo_aspect)
                    else:
                        new_width = target_width
                        new_height = int(target_width / logo_aspect)
                    
                    logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    print(f"Logo resized to: {new_width}x{new_height} (aspect ratio preserved)")
                elif logo_size:
                    logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
                
                # Apply opacity to logo
                if logo_opacity < 255:
                    logo_with_opacity = Image.new('RGBA', logo.size, (0, 0, 0, 0))
                    for x in range(logo.width):
                        for y in range(logo.height):
                            pixel = logo.getpixel((x, y))
                            if isinstance(pixel, tuple) and len(pixel) == 4:
                                r, g, b, a = pixel
                            else:
                                r, g, b, a = 0, 0, 0, 0  # Default to fully transparent if invalid
                            new_alpha = int(a * (logo_opacity / 255))
                            logo_with_opacity.putpixel((x, y), (r, g, b, new_alpha))
                    logo = logo_with_opacity
                
                # Calculate logo position
                img_width, img_height = original_size
                logo_width, logo_height = logo.size
                
                logo_position_map = {
                    'top-left': (logo_margin, logo_margin),
                    'top-right': (img_width - logo_width - logo_margin, logo_margin),
                    'bottom-left': (logo_margin, img_height - logo_height - logo_margin),
                    'bottom-right': (img_width - logo_width - logo_margin, img_height - logo_height - logo_margin),
                    'center': ((img_width - logo_width) // 2, (img_height - logo_height) // 2)
                }
                
                logo_x, logo_y = logo_position_map.get(logo_position, logo_position_map['top-left'])
                overlay_layer.paste(logo, (logo_x, logo_y), logo)
                
            except Exception as logo_error:
                print(f"Warning: Could not add logo - {str(logo_error)}")
        
        # Load font
        font = load_font(font_size)
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate positions
        img_width, img_height = original_size
        margin = 20
        
        if add_box:
            box_width = text_width + (box_padding * 2)
            box_height = text_height + (box_padding * 2)
        else:
            box_width = text_width
            box_height = text_height
            box_padding = 0
        
        position_map = {
            'top-left': (margin, margin),
            'top-right': (img_width - box_width - margin, margin),
            'bottom-left': (margin, img_height - box_height - margin),
            'bottom-right': (img_width - box_width - margin, img_height - box_height - margin),
            'center': ((img_width - box_width) // 2, (img_height - box_height) // 2)
        }
        
        box_x, box_y = position_map.get(position, position_map['bottom-right'])
        
        # Draw background box
        if add_box:
            box_color_with_opacity = (*box_color, box_opacity)
            
            if box_rounded:
                draw_rounded_rectangle(draw, box_x, box_y, box_x + box_width, 
                                     box_y + box_height, corner_radius, box_color_with_opacity)
            else:
                draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], 
                             fill=box_color_with_opacity)
            
            # Draw border
            if box_border:
                border_color_with_opacity = (*border_color, 255)
                if box_rounded:
                    draw_rounded_rectangle_border(draw, box_x, box_y, box_x + box_width, 
                                                box_y + box_height, corner_radius, 
                                                border_color_with_opacity, border_width)
                else:
                    for i in range(border_width):
                        draw.rectangle([box_x - i, box_y - i, box_x + box_width + i, 
                                      box_y + box_height + i], 
                                     outline=border_color_with_opacity, width=1)
        
        # Draw watermark text
        text_x = box_x + box_padding
        text_y = box_y + box_padding
        watermark_color = (*font_color, 255)
        draw.text((text_x, text_y), watermark_text, font=font, fill=watermark_color)
        
        # Composite the overlay onto the original image
        final_image = Image.alpha_composite(working_image, overlay_layer)
        print(f"Final image dimensions: {final_image.size[0]}x{final_image.size[1]} (preserved)")
        
        # Save or return the image
        if output_path:
            return save_image(final_image, output_path, original_size)
        else:
            return final_image
            
    except Exception as e:
        raise Exception(f"Error adding watermark: {str(e)}")

if __name__ == "__main__":
    try:
        # Example with logo
        result = add_watermark_with_logo(
            image_path="../images/test.jpg",
            
            logo_path="../static/logo.png"
        )
        print(f"Watermark with logo saved to: {result}")
        
        # Example without logo
        result2 = add_watermark_with_logo(
            image_path="../images/test.jpg",
          
        )
        print(f"Text-only watermark saved to: {result2}")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")