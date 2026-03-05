"""
Favicon and Icon Generation System for ValidoAI Application
Generates comprehensive icon sets from SVG logos
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import base64

try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False

logger = logging.getLogger(__name__)

class FaviconGenerator:
    """Comprehensive favicon and icon generation system"""
    
    def __init__(self, static_dir: str = "static"):
        self.static_dir = Path(static_dir)
        self.favicon_dir = self.static_dir / "favicons"
        self.icons_dir = self.static_dir / "icons"
        self.logo_dir = self.static_dir / "img"
        
        # Create directories if they don't exist
        self.favicon_dir.mkdir(parents=True, exist_ok=True)
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        
        # Icon sizes for different purposes
        self.favicon_sizes = [16, 32, 48, 64, 128, 256]
        self.apple_touch_sizes = [180, 152, 144, 120, 114, 76, 72, 60, 57]
        self.android_sizes = [192, 144, 96, 72, 48, 36]
        self.windows_tile_sizes = [310, 310, 150, 150, 70, 70]
        self.social_media_sizes = [1200, 600, 300]
        
        # Logo file paths
        self.primary_logo = self.logo_dir / "logo-horizontal-primary.svg"
        self.white_logo = self.logo_dir / "logo-horizontal-white.svg"
        
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        if not PILLOW_AVAILABLE:
            logger.error("Pillow (PIL) is required for icon generation")
            return False
        
        if not CAIROSVG_AVAILABLE:
            logger.warning("CairoSVG not available, using fallback methods")
        
        return True
    
    def svg_to_png(self, svg_path: Path, output_path: Path, size: Tuple[int, int], 
                   background_color: str = None) -> bool:
        """Convert SVG to PNG with specified size"""
        try:
            if CAIROSVG_AVAILABLE:
                # Use CairoSVG for better quality
                cairosvg.svg2png(
                    url=str(svg_path),
                    write_to=str(output_path),
                    output_width=size[0],
                    output_height=size[1],
                    background_color=background_color
                )
            else:
                # Fallback using PIL (limited SVG support)
                self._svg_to_png_fallback(svg_path, output_path, size, background_color)
            
            return True
        except Exception as e:
            logger.error(f"Error converting SVG to PNG: {e}")
            return False
    
    def _svg_to_png_fallback(self, svg_path: Path, output_path: Path, 
                            size: Tuple[int, int], background_color: str = None):
        """Fallback method for SVG to PNG conversion"""
        try:
            # Create a simple colored square as fallback
            img = Image.new('RGBA', size, background_color or (255, 255, 255, 255))
            
            # Add text overlay
            draw = ImageDraw.Draw(img)
            try:
                # Try to use a system font
                font = ImageFont.truetype("arial.ttf", size[0] // 4)
            except:
                font = ImageFont.load_default()
            
            text = "V"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            draw.text((x, y), text, fill=(0, 0, 0, 255), font=font)
            img.save(output_path, 'PNG')
            
        except Exception as e:
            logger.error(f"Fallback SVG conversion failed: {e}")
            # Create a simple colored square
            img = Image.new('RGBA', size, (52, 211, 153, 255))  # ValidoAI green
            img.save(output_path, 'PNG')
    
    def generate_favicons(self) -> Dict[str, str]:
        """Generate comprehensive favicon set"""
        if not self.check_dependencies():
            return {}
        
        generated_files = {}
        
        # Generate standard favicons
        for size in self.favicon_sizes:
            filename = f"favicon-{size}x{size}.png"
            output_path = self.favicon_dir / filename
            
            if self.svg_to_png(self.primary_logo, output_path, (size, size)):
                generated_files[filename] = str(output_path)
        
        # Generate ICO file (multi-size)
        ico_path = self.favicon_dir / "favicon.ico"
        if self._generate_ico_file(ico_path):
            generated_files["favicon.ico"] = str(ico_path)
        
        # Generate Apple touch icons
        for size in self.apple_touch_sizes:
            filename = f"apple-touch-icon-{size}x{size}.png"
            output_path = self.favicon_dir / filename
            
            if self.svg_to_png(self.primary_logo, output_path, (size, size)):
                generated_files[filename] = str(output_path)
        
        # Generate Android icons
        for size in self.android_sizes:
            filename = f"android-chrome-{size}x{size}.png"
            output_path = self.favicon_dir / filename
            
            if self.svg_to_png(self.primary_logo, output_path, (size, size)):
                generated_files[filename] = str(output_path)
        
        # Generate Windows tiles
        for size in self.windows_tile_sizes:
            filename = f"mstile-{size}x{size}.png"
            output_path = self.favicon_dir / filename
            
            if self.svg_to_png(self.primary_logo, output_path, (size, size)):
                generated_files[filename] = str(output_path)
        
        # Generate social media icons
        for size in self.social_media_sizes:
            filename = f"social-{size}x{size}.png"
            output_path = self.favicon_dir / filename
            
            if self.svg_to_png(self.primary_logo, output_path, (size, size)):
                generated_files[filename] = str(output_path)
        
        return generated_files
    
    def _generate_ico_file(self, output_path: Path) -> bool:
        """Generate ICO file with multiple sizes"""
        try:
            images = []
            for size in [16, 32, 48]:
                png_path = self.favicon_dir / f"favicon-{size}x{size}.png"
                if png_path.exists():
                    img = Image.open(png_path)
                    images.append(img)
            
            if images:
                images[0].save(
                    output_path,
                    format='ICO',
                    sizes=[(img.width, img.height) for img in images],
                    append_images=images[1:]
                )
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error generating ICO file: {e}")
            return False
    
    def generate_web_app_manifest(self) -> str:
        """Generate web app manifest with icons"""
        manifest = {
            "name": "ValidoAI - Financial Analysis Platform",
            "short_name": "ValidoAI",
            "description": "Advanced financial analysis and AI-powered insights platform",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#34d399",
            "orientation": "portrait-primary",
            "icons": []
        }
        
        # Add icons to manifest
        icon_sizes = [192, 512]  # PWA recommended sizes
        for size in icon_sizes:
            icon_path = f"/static/favicons/android-chrome-{size}x{size}.png"
            manifest["icons"].append({
                "src": icon_path,
                "sizes": f"{size}x{size}",
                "type": "image/png",
                "purpose": "any maskable"
            })
        
        manifest_path = self.favicon_dir / "site.webmanifest"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        return str(manifest_path)
    
    def generate_html_head_tags(self) -> str:
        """Generate HTML head tags for favicons"""
        tags = []
        
        # Standard favicon
        tags.append('<link rel="icon" type="image/x-icon" href="/static/favicons/favicon.ico">')
        tags.append('<link rel="icon" type="image/png" sizes="32x32" href="/static/favicons/favicon-32x32.png">')
        tags.append('<link rel="icon" type="image/png" sizes="16x16" href="/static/favicons/favicon-16x16.png">')
        
        # Apple touch icons
        tags.append('<link rel="apple-touch-icon" sizes="180x180" href="/static/favicons/apple-touch-icon-180x180.png">')
        tags.append('<link rel="apple-touch-icon" sizes="152x152" href="/static/favicons/apple-touch-icon-152x152.png">')
        tags.append('<link rel="apple-touch-icon" sizes="144x144" href="/static/favicons/apple-touch-icon-144x144.png">')
        tags.append('<link rel="apple-touch-icon" sizes="120x120" href="/static/favicons/apple-touch-icon-120x120.png">')
        tags.append('<link rel="apple-touch-icon" sizes="114x114" href="/static/favicons/apple-touch-icon-114x114.png">')
        tags.append('<link rel="apple-touch-icon" sizes="76x76" href="/static/favicons/apple-touch-icon-76x76.png">')
        tags.append('<link rel="apple-touch-icon" sizes="72x72" href="/static/favicons/apple-touch-icon-72x72.png">')
        tags.append('<link rel="apple-touch-icon" sizes="60x60" href="/static/favicons/apple-touch-icon-60x60.png">')
        tags.append('<link rel="apple-touch-icon" sizes="57x57" href="/static/favicons/apple-touch-icon-57x57.png">')
        
        # Android icons
        tags.append('<link rel="icon" type="image/png" sizes="192x192" href="/static/favicons/android-chrome-192x192.png">')
        tags.append('<link rel="icon" type="image/png" sizes="512x512" href="/static/favicons/android-chrome-512x512.png">')
        
        # Windows tiles
        tags.append('<meta name="msapplication-TileColor" content="#34d399">')
        tags.append('<meta name="msapplication-TileImage" content="/static/favicons/mstile-144x144.png">')
        tags.append('<meta name="msapplication-config" content="/static/favicons/browserconfig.xml">')
        
        # Web app manifest
        tags.append('<link rel="manifest" href="/static/favicons/site.webmanifest">')
        
        # Theme colors
        tags.append('<meta name="theme-color" content="#34d399">')
        tags.append('<meta name="msapplication-TileColor" content="#34d399">')
        tags.append('<meta name="apple-mobile-web-app-status-bar-style" content="default">')
        tags.append('<meta name="apple-mobile-web-app-capable" content="yes">')
        
        return '\n    '.join(tags)
    
    def generate_browserconfig_xml(self) -> str:
        """Generate browserconfig.xml for Windows tiles"""
        config = f"""<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
    <msapplication>
        <tile>
            <square150x150logo src="/static/favicons/mstile-150x150.png"/>
            <TileColor>#34d399</TileColor>
        </tile>
    </msapplication>
</browserconfig>"""
        
        config_path = self.favicon_dir / "browserconfig.xml"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config)
        
        return str(config_path)
    
    def validate_generated_icons(self) -> Dict[str, bool]:
        """Validate generated icons for quality and compatibility"""
        validation_results = {}
        
        required_files = [
            "favicon.ico",
            "favicon-16x16.png",
            "favicon-32x32.png",
            "apple-touch-icon-180x180.png",
            "android-chrome-192x192.png",
            "android-chrome-512x512.png",
            "site.webmanifest",
            "browserconfig.xml"
        ]
        
        for filename in required_files:
            file_path = self.favicon_dir / filename
            validation_results[filename] = file_path.exists()
            
            if file_path.exists():
                # Check file size
                file_size = file_path.stat().st_size
                if file_size == 0:
                    validation_results[filename] = False
                    logger.warning(f"Empty file: {filename}")
        
        return validation_results
    
    def cleanup_old_icons(self):
        """Clean up old icon files"""
        try:
            # Remove old favicon files
            old_patterns = ["*.ico", "*.png"]
            for pattern in old_patterns:
                for file_path in self.favicon_dir.glob(pattern):
                    if file_path.name.startswith("favicon") or file_path.name.startswith("apple-touch") or file_path.name.startswith("android-chrome"):
                        file_path.unlink()
                        logger.info(f"Removed old icon: {file_path.name}")
        except Exception as e:
            logger.error(f"Error cleaning up old icons: {e}")
    
    def check_existing_icons(self) -> bool:
        """Check if all required icons already exist"""
        required_files = [
            "favicon.ico",
            "favicon-16x16.png",
            "favicon-32x32.png",
            "apple-touch-icon-180x180.png",
            "android-chrome-192x192.png",
            "android-chrome-512x512.png",
            "site.webmanifest",
            "browserconfig.xml"
        ]
        
        for filename in required_files:
            file_path = self.favicon_dir / filename
            if not file_path.exists() or file_path.stat().st_size == 0:
                return False
        return True
    
    def generate_all(self) -> Dict[str, any]:
        """Generate all favicons and related files"""
        logger.info("Starting favicon generation...")
        
        # Check if icons already exist
        if self.check_existing_icons():
            logger.info("Favicons already exist, skipping generation")
            validation_results = self.validate_generated_icons()
            return {
                "generated_files": {},
                "manifest_path": str(self.favicon_dir / "site.webmanifest"),
                "browserconfig_path": str(self.favicon_dir / "browserconfig.xml"),
                "html_tags": self.generate_html_head_tags(),
                "html_tags_path": str(self.favicon_dir / "favicon_tags.html"),
                "validation_results": validation_results,
                "success": all(validation_results.values()),
                "skipped": True
            }
        
        # Clean up old icons
        self.cleanup_old_icons()
        
        # Generate favicons
        generated_files = self.generate_favicons()
        
        # Generate manifest
        manifest_path = self.generate_web_app_manifest()
        
        # Generate browser config
        browserconfig_path = self.generate_browserconfig_xml()
        
        # Generate HTML tags
        html_tags = self.generate_html_head_tags()
        
        # Validate generated files
        validation_results = self.validate_generated_icons()
        
        # Save HTML tags to file for easy inclusion
        html_tags_path = self.favicon_dir / "favicon_tags.html"
        with open(html_tags_path, 'w', encoding='utf-8') as f:
            f.write(html_tags)
        
        results = {
            "generated_files": generated_files,
            "manifest_path": manifest_path,
            "browserconfig_path": browserconfig_path,
            "html_tags": html_tags,
            "html_tags_path": str(html_tags_path),
            "validation_results": validation_results,
            "success": all(validation_results.values())
        }
        
        logger.info(f"Favicon generation completed. Generated {len(generated_files)} files.")
        return results

# Global favicon generator instance
favicon_generator = FaviconGenerator()

def generate_favicons():
    """Generate all favicons"""
    return favicon_generator.generate_all()

def get_favicon_html_tags():
    """Get HTML head tags for favicons"""
    return favicon_generator.generate_html_head_tags()

def validate_favicons():
    """Validate existing favicons"""
    return favicon_generator.validate_generated_icons()
