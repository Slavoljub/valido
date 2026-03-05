"""
Favicon Generator for ValidoAI Application
Generates various favicon sizes and formats for web and mobile applications
"""

import os
import logging
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from pathlib import Path

logger = logging.getLogger(__name__)

class FaviconGenerator:
    """Generates favicons in various sizes and formats"""
    
    def __init__(self, app=None):
        self.app = app
        self.icons_dir = Path("static/icons")
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        
        # Standard favicon sizes
        self.sizes = {
            'favicon.ico': [(16, 16), (32, 32), (48, 48)],
            'favicon-16x16.png': [(16, 16)],
            'favicon-32x32.png': [(32, 32)],
            'apple-touch-icon.png': [(180, 180)],
            'android-chrome-192x192.png': [(192, 192)],
            'android-chrome-512x512.png': [(512, 512)],
            'mstile-150x150.png': [(150, 150)],
            'safari-pinned-tab.svg': [(16, 16)],
            'browserconfig.xml': None,
            'site.webmanifest': None
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        self.icons_dir = Path(app.static_folder) / "icons"
        self.icons_dir.mkdir(parents=True, exist_ok=True)
    
    def create_text_icon(self, text="V", size=(512, 512), bg_color="#3B82F6", text_color="#FFFFFF"):
        """Create a text-based icon with the given parameters"""
        try:
            # Create image with background
            img = Image.new('RGBA', size, bg_color)
            draw = ImageDraw.Draw(img)
            
            # Calculate font size (approximately 60% of image height)
            font_size = int(size[1] * 0.6)
            
            # Try to use a system font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position to center text
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            # Draw text
            draw.text((x, y), text, fill=text_color, font=font)
            
            return img
            
        except Exception as e:
            logger.error(f"Error creating text icon: {e}")
            # Fallback: create a simple colored square
            img = Image.new('RGBA', size, bg_color)
            return img
    
    def create_gradient_icon(self, size=(512, 512), colors=None):
        """Create a gradient icon"""
        if colors is None:
            colors = ["#3B82F6", "#1D4ED8", "#1E40AF"]
        
        try:
            img = Image.new('RGBA', size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Create gradient effect
            for i in range(size[1]):
                # Calculate gradient color
                ratio = i / size[1]
                if ratio < 0.5:
                    color_ratio = ratio * 2
                    r1, g1, b1 = tuple(int(colors[0][i:i+2], 16) for i in (1, 3, 5))
                    r2, g2, b2 = tuple(int(colors[1][i:i+2], 16) for i in (1, 3, 5))
                else:
                    color_ratio = (ratio - 0.5) * 2
                    r1, g1, b1 = tuple(int(colors[1][i:i+2], 16) for i in (1, 3, 5))
                    r2, g2, b2 = tuple(int(colors[2][i:i+2], 16) for i in (1, 3, 5))
                
                r = int(r1 + (r2 - r1) * color_ratio)
                g = int(g1 + (g2 - g1) * color_ratio)
                b = int(b1 + (b2 - b1) * color_ratio)
                
                draw.line([(0, i), (size[0], i)], fill=(r, g, b, 255))
            
            return img
            
        except Exception as e:
            logger.error(f"Error creating gradient icon: {e}")
            return self.create_text_icon("V", size)
    
    def generate_favicon(self, icon_type="text", text="V", bg_color="#3B82F6", text_color="#FFFFFF", 
                        gradient_colors=None, custom_image_path=None):
        """Generate all favicon files"""
        try:
            generated_files = []
            
            for filename, sizes in self.sizes.items():
                if sizes is None:
                    # Generate XML/JSON files
                    if filename == 'browserconfig.xml':
                        self.generate_browserconfig_xml()
                    elif filename == 'site.webmanifest':
                        self.generate_webmanifest()
                    continue
                
                # Generate image files
                for size in sizes:
                    if icon_type == "text":
                        icon = self.create_text_icon(text, size, bg_color, text_color)
                    elif icon_type == "gradient":
                        icon = self.create_gradient_icon(size, gradient_colors)
                    elif icon_type == "custom" and custom_image_path:
                        icon = self.resize_custom_image(custom_image_path, size)
                    else:
                        icon = self.create_text_icon(text, size, bg_color, text_color)
                    
                    # Save icon
                    filepath = self.icons_dir / filename
                    if filename.endswith('.ico'):
                        # Save as ICO with multiple sizes
                        icons = []
                        for ico_size in sizes:
                            if icon_type == "text":
                                ico_icon = self.create_text_icon(text, ico_size, bg_color, text_color)
                            elif icon_type == "gradient":
                                ico_icon = self.create_gradient_icon(ico_size, gradient_colors)
                            elif icon_type == "custom" and custom_image_path:
                                ico_icon = self.resize_custom_image(custom_image_path, ico_size)
                            else:
                                ico_icon = self.create_text_icon(text, ico_size, bg_color, text_color)
                            icons.append(ico_icon)
                        
                        icons[0].save(filepath, format='ICO', sizes=[(s[0], s[1]) for s in sizes])
                    else:
                        icon.save(filepath, 'PNG')
                    
                    generated_files.append(str(filepath))
                    logger.info(f"Generated {filename} ({size[0]}x{size[1]})")
            
            return {
                'status': 'success',
                'files': generated_files,
                'message': f'Generated {len(generated_files)} favicon files'
            }
            
        except Exception as e:
            logger.error(f"Error generating favicons: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def resize_custom_image(self, image_path, size):
        """Resize a custom image to the specified size"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGBA if necessary
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Resize with high quality
                img = img.resize(size, Image.Resampling.LANCZOS)
                return img
        except Exception as e:
            logger.error(f"Error resizing custom image: {e}")
            return self.create_text_icon("V", size)
    
    def generate_browserconfig_xml(self):
        """Generate browserconfig.xml for Windows tiles"""
        content = '''<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
    <msapplication>
        <tile>
            <square150x150logo src="/static/icons/mstile-150x150.png"/>
            <TileColor>#3B82F6</TileColor>
        </tile>
    </msapplication>
</browserconfig>'''
        
        filepath = self.icons_dir / 'browserconfig.xml'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_webmanifest(self):
        """Generate site.webmanifest for PWA support"""
        content = '''{
    "name": "ValidoAI",
    "short_name": "ValidoAI",
    "description": "AI-powered financial management system",
    "icons": [
        {
            "src": "/static/icons/android-chrome-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/static/icons/android-chrome-512x512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ],
    "theme_color": "#3B82F6",
    "background_color": "#ffffff",
    "display": "standalone",
    "start_url": "/"
}'''
        
        filepath = self.icons_dir / 'site.webmanifest'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def get_generated_icons(self):
        """Get list of all generated icons"""
        try:
            icons = []
            for filename in self.sizes.keys():
                filepath = self.icons_dir / filename
                if filepath.exists():
                    # Get file info
                    stat = filepath.stat()
                    icons.append({
                        'filename': filename,
                        'path': str(filepath),
                        'url': f'/static/icons/{filename}',
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
            
            return icons
        except Exception as e:
            logger.error(f"Error getting generated icons: {e}")
            return []
    
    def delete_icon(self, filename):
        """Delete a specific icon file"""
        try:
            filepath = self.icons_dir / filename
            if filepath.exists():
                filepath.unlink()
                return {'status': 'success', 'message': f'Deleted {filename}'}
            else:
                return {'status': 'error', 'error': f'File {filename} not found'}
        except Exception as e:
            logger.error(f"Error deleting icon {filename}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def delete_all_icons(self):
        """Delete all generated icons"""
        try:
            deleted_count = 0
            for filename in self.sizes.keys():
                filepath = self.icons_dir / filename
                if filepath.exists():
                    filepath.unlink()
                    deleted_count += 1
            
            return {
                'status': 'success',
                'message': f'Deleted {deleted_count} icon files'
            }
        except Exception as e:
            logger.error(f"Error deleting all icons: {e}")
            return {'status': 'error', 'error': str(e)}

def setup_favicon_generator(app):
    """Setup favicon generator for the application"""
    try:
        generator = FaviconGenerator(app)
        app.favicon_generator = generator
        return generator
    except Exception as e:
        logger.error(f"Favicon generator setup failed: {e}")
        raise

# Utility functions
def get_favicon_generator():
    """Get favicon generator from Flask app context"""
    from flask import current_app
    return getattr(current_app, 'favicon_generator', None)
