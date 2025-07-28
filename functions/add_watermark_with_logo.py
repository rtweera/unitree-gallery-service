def add_watermark_with_logo(image_content, 
                           watermark_text="Snapped by Oxy at WSO2Con Asia",
                           output_path=None,
                           font_size=180,
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
                           preserve_logo_aspect=True,
                           logo_blur_background=True,
                           blur_radius=15,
                           blur_area_padding=30,
                           blur_opacity=180,
                           # New parameters for bottom-right image
                           bottom_right_image_path=None,
                           bottom_right_image_size=(300, 200),
                           bottom_right_margin=20,
                           bottom_right_opacity=255,
                           preserve_bottom_right_aspect=True,
                           add_watermark=False):  # Flag to control watermark text
    """
    Add a text watermark and logo to an image from byte content with optional background box.
    Preserves original image dimensions and aspect ratio.
    
    Args:
        // ...existing args...
        bottom_right_image_path (str, optional): Path to image to place in bottom-right
        bottom_right_image_size (tuple): Maximum size for bottom-right image (width, height)
        bottom_right_margin (int): Margin from edges for bottom-right image
        bottom_right_opacity (int): Opacity of bottom-right image (0-255)
        preserve_bottom_right_aspect (bool): Whether to preserve aspect ratio
        add_watermark (bool): Whether to add text watermark (set to False to skip)
    
    Returns:
        PIL.Image or str: Watermarked image object if output_path is None, else path to saved image
    """
    
    try:
        # Open image from byte content
        image_stream = BytesIO(image_content)
        original_image = Image.open(image_stream)
        original_size = original_image.size
        print(f"Original image dimensions: {original_size[0]}x{original_size[1]}")
        
        # Convert to RGBA for processing while maintaining original size
        working_image = original_image.convert('RGBA')
        
        # Create transparent overlay for watermark and logo
        overlay_layer = Image.new('RGBA', original_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay_layer)
        
        # Add logo if provided
        if logo_path is None:
            print("No logo path provided, skipping logo addition.")
        if logo_path and not os.path.exists(logo_path):
            print(f"Warning: Logo file '{logo_path}' does not exist. Skipping logo addition. OS path {os.getcwd()}")
        if logo_path and os.path.exists(logo_path):
            try:
                print("Logo function inside try")
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
                
                # Add blur background behind logo if enabled
                if logo_blur_background:
                    # Calculate blur area coordinates
                    blur_x1 = max(0, logo_x - blur_area_padding)
                    blur_y1 = max(0, logo_y - blur_area_padding)
                    blur_x2 = min(img_width, logo_x + logo_width + blur_area_padding)
                    blur_y2 = min(img_height, logo_y + logo_height + blur_area_padding)
                    
                    # Create blur area
                    blur_area = working_image.crop((blur_x1, blur_y1, blur_x2, blur_y2))
                    blurred_area = blur_area.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                    
                    # Create mask for the blur area with rounded corners
                    blur_mask = Image.new('L', (blur_x2 - blur_x1, blur_y2 - blur_y1), 0)
                    blur_mask_draw = ImageDraw.Draw(blur_mask)
                    
                    # Draw rounded rectangle mask for smooth blur edges
                    mask_corner_radius = min(20, (blur_x2 - blur_x1) // 4, (blur_y2 - blur_y1) // 4)
                    blur_mask_draw.rounded_rectangle(
                        [0, 0, blur_x2 - blur_x1, blur_y2 - blur_y1],
                        radius=mask_corner_radius,
                        fill=blur_opacity
                    )
                    
                    # Apply blur with opacity
                    blurred_with_opacity = Image.new('RGBA', blurred_area.size, (0, 0, 0, 0))
                    blurred_rgba = blurred_area.convert('RGBA')
                    
                    # Apply the mask to create smooth edges
                    for x in range(blurred_rgba.width):
                        for y in range(blurred_rgba.height):
                            r, g, b, a = blurred_rgba.getpixel((x, y))
                            mask_value = blur_mask.getpixel((x, y))
                            new_alpha = int(mask_value)
                            blurred_with_opacity.putpixel((x, y), (r, g, b, new_alpha))
                    
                    # Paste the blurred area onto the overlay
                    overlay_layer.paste(blurred_with_opacity, (blur_x1, blur_y1), blurred_with_opacity)
                
                # Apply opacity to logo
                if logo_opacity < 255:
                    logo_with_opacity = Image.new('RGBA', logo.size, (0, 0, 0, 0))
                    for x in range(logo.width):
                        for y in range(logo.height):
                            r, g, b, a = logo.getpixel((x, y))
                            new_alpha = int(a * (logo_opacity / 255))
                            logo_with_opacity.putpixel((x, y), (r, g, b, new_alpha))
                    logo = logo_with_opacity
                
                # Paste the logo
                overlay_layer.paste(logo, (logo_x, logo_y), logo)
                
            except Exception as logo_error:
                print(f"Warning: Could not add logo - {str(logo_error)}")
        if bottom_right_image_path and os.path.exists(bottom_right_image_path):
            try:
                print(f"Adding bottom-right image from: {bottom_right_image_path}")
                bottom_right_img = Image.open(bottom_right_image_path).convert('RGBA')
                original_br_size = bottom_right_img.size
                print(f"Original bottom-right image dimensions: {original_br_size[0]}x{original_br_size[1]}")
                
                # Resize bottom-right image while preserving aspect ratio
                if bottom_right_image_size and preserve_bottom_right_aspect:
                    br_aspect = original_br_size[0] / original_br_size[1]
                    target_width, target_height = bottom_right_image_size
                    
                    if target_width / target_height > br_aspect:
                        new_height = target_height
                        new_width = int(target_height * br_aspect)
                    else:
                        new_width = target_width
                        new_height = int(target_width / br_aspect)
                    
                    bottom_right_img = bottom_right_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    print(f"Bottom-right image resized to: {new_width}x{new_height}")
                elif bottom_right_image_size:
                    bottom_right_img = bottom_right_img.resize(bottom_right_image_size, Image.Resampling.LANCZOS)
                
                # Calculate bottom-right position
                img_width, img_height = original_size
                br_width, br_height = bottom_right_img.size
                
                br_x = img_width - br_width - bottom_right_margin
                br_y = img_height - br_height - bottom_right_margin
                
                # Apply opacity to bottom-right image
                if bottom_right_opacity < 255:
                    br_with_opacity = Image.new('RGBA', bottom_right_img.size, (0, 0, 0, 0))
                    for x in range(bottom_right_img.width):
                        for y in range(bottom_right_img.height):
                            r, g, b, a = bottom_right_img.getpixel((x, y))
                            new_alpha = int(a * (bottom_right_opacity / 255))
                            br_with_opacity.putpixel((x, y), (r, g, b, new_alpha))
                    bottom_right_img = br_with_opacity
                
                # Paste the bottom-right image
                overlay_layer.paste(bottom_right_img, (br_x, br_y), bottom_right_img)
                print(f"Bottom-right image placed at position: ({br_x}, {br_y})")
                
            except Exception as br_error:
                print(f"Warning: Could not add bottom-right image - {str(br_error)}")
        elif bottom_right_image_path:
            print(f"Warning: Bottom-right image file '{bottom_right_image_path}' does not exist.")
        
        # Add watermark text only if add_watermark is True
        if add_watermark and watermark_text:
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
            return save_image_watermark(final_image, output_path, original_size)
        else:
            return final_image
            
    except Exception as e:
        raise Exception(f"Error adding watermark: {str(e)}")
        # ...existing code...
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
            return save_image_watermark(final_image, output_path, original_size)
        else:
            return final_image
            
    except Exception as e:
        raise Exception(f"Error adding watermark: {str(e)}")

# if __name__ == "__main__":
#     try:
#         # Example with image byte content and logo blur
#         with open("../images/test.jpg", "rb") as f:
#             image_content = f.read()
        
#         result = add_watermark_with_logo(
#             image_content=image_content,
#             output_path="../images/watermarked_test.jpg",
#             logo_path="../static/logo.png",
#             logo_blur_background=True,
#             blur_radius=20,
#             blur_area_padding=40,
#             blur_opacity=150
#         )
#         print(f"Watermark with logo and blur saved to: {result}")
        
#     except Exception as e:
#         print(f"Error: {e}")