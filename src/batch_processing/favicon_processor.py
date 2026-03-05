#!/usr/bin/env python3
"""
Batch Favicon Processing Module
==============================
Advanced batch processor for favicons and icons with multi-format support.
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    import numpy as np
    from tqdm import tqdm
    IMAGING_AVAILABLE = True
except ImportError:
    IMAGING_AVAILABLE = False
    print("⚠️ Imaging libraries not available. Install: pip install Pillow numpy tqdm")

try:
    import rembg
    BACKGROUND_REMOVAL_AVAILABLE = True
except ImportError:
    BACKGROUND_REMOVAL_AVAILABLE = False

class BatchFaviconProcessor:
    """Advanced batch processor for favicons and icons"""
    
    def __init__(self, output_dir="favicon_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Standard favicon sizes
        self.favicon_sizes = {
            'ico': [16, 32, 48],
            'web': [16, 32, 96, 192],
            'apple': [57, 60, 72, 76, 114, 120, 144, 152, 180],
            'android': [36, 48, 72, 96, 144, 192, 256, 384, 512],
            'windows': [70, 150, 310]
        }
        
        # Supported formats
        self.supported_formats = {
            'input': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.svg'],
            'output': ['.png', '.ico', '.webp', '.avif']
        }
        
        # Processing statistics
        self.stats = {
            'processed': 0,
            'errors': 0,
            'skipped': 0,
            'total_size_reduction': 0,
            'processing_time': 0
        }
        
        # Initialize background removal model if available
        self.bg_remover = None
        if BACKGROUND_REMOVAL_AVAILABLE:
            try:
                self.bg_remover = rembg.new_session('u2net')
            except:
                pass
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> List[Path]:
        """Scan directory for supported image files"""
        if not IMAGING_AVAILABLE:
            print("❌ Imaging libraries not available")
            return []
            
        image_files = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats['input']:
                image_files.append(file_path)
        
        return sorted(image_files)
    
    def get_image_info(self, image_path: Path) -> Dict:
        """Get comprehensive image information"""
        if not IMAGING_AVAILABLE:
            return {'error': 'Imaging libraries not available'}
            
        try:
            with Image.open(image_path) as img:
                info = {
                    'filename': image_path.name,
                    'path': str(image_path),
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'file_size': image_path.stat().st_size,
                    'has_transparency': img.mode in ('RGBA', 'LA', 'P'),
                    'is_square': img.width == img.height,
                    'aspect_ratio': img.width / img.height
                }
                
                # Get color information
                if img.mode == 'RGB':
                    colors = img.getcolors(maxcolors=256*256*256)
                    if colors:
                        info['color_count'] = len(colors)
                        info['dominant_color'] = max(colors, key=lambda x: x[0])[1]
                
                return info
        except Exception as e:
            return {'error': str(e), 'path': str(image_path)}
    
    def create_square_canvas(self, image: Image.Image, size: int, bg_color: tuple = (255, 255, 255, 0)) -> Image.Image:
        """Create square canvas and center image"""
        if not IMAGING_AVAILABLE:
            return image
            
        # Create square canvas
        canvas = Image.new('RGBA', (size, size), bg_color)
        
        # Calculate scaling to fit within canvas while maintaining aspect ratio
        img_ratio = image.width / image.height
        if img_ratio > 1:  # Wider than tall
            new_width = size
            new_height = int(size / img_ratio)
        else:  # Taller than wide
            new_width = int(size * img_ratio)
            new_height = size
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center on canvas
        x = (size - new_width) // 2
        y = (size - new_height) // 2
        canvas.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)
        
        return canvas
    
    def create_favicon_set(self, source_image: Image.Image, output_name: str) -> Dict[str, List[str]]:
        """Create complete favicon set from source image"""
        if not IMAGING_AVAILABLE:
            return {}
            
        generated_files = {
            'ico': [],
            'png': [],
            'apple': [],
            'android': [],
            'windows': []
        }
        
        # Ensure source is RGBA for transparency support
        if source_image.mode != 'RGBA':
            source_image = source_image.convert('RGBA')
        
        try:
            # Create ICO file with multiple sizes
            ico_images = []
            for size in self.favicon_sizes['ico']:
                favicon = self.create_square_canvas(source_image, size)
                ico_images.append(favicon)
            
            ico_path = self.output_dir / f"{output_name}.ico"
            ico_images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
            generated_files['ico'].append(str(ico_path))
            
            # Create standard web favicons
            for size in self.favicon_sizes['web']:
                favicon = self.create_square_canvas(source_image, size)
                png_path = self.output_dir / f"{output_name}-{size}x{size}.png"
                favicon.save(png_path, format='PNG', optimize=True)
                generated_files['png'].append(str(png_path))
            
            # Create Apple touch icons
            apple_dir = self.output_dir / "apple"
            apple_dir.mkdir(exist_ok=True)
            for size in self.favicon_sizes['apple']:
                favicon = self.create_square_canvas(source_image, size)
                apple_path = apple_dir / f"apple-touch-icon-{size}x{size}.png"
                favicon.save(apple_path, format='PNG', optimize=True)
                generated_files['apple'].append(str(apple_path))
            
            # Create Android icons
            android_dir = self.output_dir / "android"
            android_dir.mkdir(exist_ok=True)
            for size in self.favicon_sizes['android']:
                favicon = self.create_square_canvas(source_image, size)
                android_path = android_dir / f"android-chrome-{size}x{size}.png"
                favicon.save(android_path, format='PNG', optimize=True)
                generated_files['android'].append(str(android_path))
            
            # Create Windows tiles
            windows_dir = self.output_dir / "windows"
            windows_dir.mkdir(exist_ok=True)
            for size in self.favicon_sizes['windows']:
                favicon = self.create_square_canvas(source_image, size)
                windows_path = windows_dir / f"mstile-{size}x{size}.png"
                favicon.save(windows_path, format='PNG', optimize=True)
                generated_files['windows'].append(str(windows_path))
        
        except Exception as e:
            print(f"Error creating favicon set: {e}")
        
        return generated_files
    
    def generate_manifest(self, name: str, generated_files: Dict) -> str:
        """Generate web app manifest"""
        manifest = {
            "name": name,
            "short_name": name[:12],
            "theme_color": "#ffffff",
            "background_color": "#ffffff",
            "display": "standalone",
            "scope": "/",
            "start_url": "/",
            "icons": []
        }
        
        # Add Android icons to manifest
        for icon_path in generated_files.get('android', []):
            import re
            size_match = re.search(r'(\d+)x(\d+)', icon_path)
            if size_match:
                size = size_match.group(1)
                manifest["icons"].append({
                    "src": f"/android/android-chrome-{size}x{size}.png",
                    "sizes": f"{size}x{size}",
                    "type": "image/png"
                })
        
        manifest_path = self.output_dir / "site.webmanifest"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return str(manifest_path)
    
    def generate_html_snippet(self, name: str) -> str:
        """Generate HTML code snippet for favicons"""
        html = f'''<!-- Favicon and Icon Links for {name} -->
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/{name}-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/{name}-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple/apple-touch-icon-180x180.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#ffffff">
<meta name="msapplication-TileColor" content="#ffffff">
<meta name="msapplication-TileImage" content="/windows/mstile-150x150.png">
'''
        
        html_path = self.output_dir / "favicon_html.txt"
        with open(html_path, 'w') as f:
            f.write(html)
        
        return html
    
    def process_single_image(self, image_path: Path, remove_bg: bool = False) -> Dict:
        """Process a single image into favicon set"""
        if not IMAGING_AVAILABLE:
            return {'success': False, 'error': 'Imaging libraries not available'}
            
        try:
            start_time = time.time()
            
            # Load image
            with Image.open(image_path) as img:
                # Convert to RGBA for consistency
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Remove background if requested and available
                if remove_bg and self.bg_remover:
                    try:
                        import io
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        
                        output = rembg.remove(img_bytes.read(), session=self.bg_remover)
                        img = Image.open(io.BytesIO(output))
                    except Exception as e:
                        print(f"Background removal failed: {e}")
                
                # Create output name
                output_name = image_path.stem
                
                # Create favicon set
                generated_files = self.create_favicon_set(img, output_name)
                
                # Generate manifest and HTML
                manifest_path = self.generate_manifest(output_name, generated_files)
                html_snippet = self.generate_html_snippet(output_name)
                
                processing_time = time.time() - start_time
                
                self.stats['processed'] += 1
                self.stats['processing_time'] += processing_time
                
                return {
                    'success': True,
                    'source': str(image_path),
                    'output_name': output_name,
                    'generated_files': generated_files,
                    'manifest': manifest_path,
                    'html_snippet': html_snippet,
                    'processing_time': processing_time,
                    'total_files_created': sum(len(files) for files in generated_files.values())
                }
        
        except Exception as e:
            self.stats['errors'] += 1
            return {
                'success': False,
                'source': str(image_path),
                'error': str(e)
            }
    
    def batch_process_directory(self, input_dir: Path, recursive: bool = True, 
                              remove_bg: bool = False, max_workers: int = 4) -> List[Dict]:
        """Batch process all images in directory"""
        if not IMAGING_AVAILABLE:
            print("❌ Imaging libraries not available")
            return []
            
        # Scan for images
        image_files = self.scan_directory(input_dir, recursive)
        
        if not image_files:
            print(f"No supported image files found in {input_dir}")
            return []
        
        print(f"Found {len(image_files)} images to process")
        
        # Reset statistics
        self.stats = {key: 0 for key in self.stats}
        
        results = []
        
        # Process with progress bar
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for image_path in image_files:
                future = executor.submit(self.process_single_image, image_path, remove_bg)
                futures.append(future)
            
            # Collect results with progress bar
            if IMAGING_AVAILABLE:
                try:
                    for future in tqdm(futures, desc="Processing images"):
                        result = future.result()
                        results.append(result)
                except ImportError:
                    # Fallback without progress bar
                    for future in futures:
                        result = future.result()
                        results.append(result)
            else:
                for future in futures:
                    result = future.result()
                    results.append(result)
        
        return results
    
    def generate_processing_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive processing report"""
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        total_files_created = sum(r.get('total_files_created', 0) for r in successful)
        avg_processing_time = sum(r.get('processing_time', 0) for r in successful) / len(successful) if successful else 0
        
        report = {
            'summary': {
                'total_processed': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': len(successful) / len(results) * 100 if results else 0,
                'total_files_created': total_files_created,
                'average_processing_time': avg_processing_time,
                'total_processing_time': self.stats['processing_time']
            },
            'successful_files': [r['source'] for r in successful],
            'failed_files': [(r['source'], r.get('error', 'Unknown error')) for r in failed],
            'statistics': self.stats
        }
        
        # Save report to file
        report_path = self.output_dir / "processing_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report

def create_sample_images(output_dir="sample_images"):
    """Create sample images for testing"""
    if not IMAGING_AVAILABLE:
        print("❌ Cannot create sample images - imaging libraries not available")
        return []
    
    sample_dir = Path(output_dir)
    sample_dir.mkdir(exist_ok=True)
    
    # Create different types of sample images
    samples = [
        {'name': 'logo_circle', 'shape': 'circle', 'color': (52, 152, 219)},
        {'name': 'logo_square', 'shape': 'square', 'color': (231, 76, 60)},
        {'name': 'logo_diamond', 'shape': 'diamond', 'color': (46, 204, 113)},
        {'name': 'logo_star', 'shape': 'star', 'color': (155, 89, 182)},
        {'name': 'logo_hexagon', 'shape': 'hexagon', 'color': (230, 126, 34)}
    ]
    
    created_files = []
    
    for sample in samples:
        # Create 512x512 canvas
        img = Image.new('RGBA', (512, 512), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        center = 256
        size = 200
        color = sample['color'] + (255,)  # Add alpha
        
        if sample['shape'] == 'circle':
            draw.ellipse([center-size//2, center-size//2, center+size//2, center+size//2], fill=color)
        
        elif sample['shape'] == 'square':
            draw.rectangle([center-size//2, center-size//2, center+size//2, center+size//2], fill=color)
        
        elif sample['shape'] == 'diamond':
            points = [
                (center, center-size//2),  # top
                (center+size//2, center),  # right
                (center, center+size//2),  # bottom
                (center-size//2, center)   # left
            ]
            draw.polygon(points, fill=color)
        
        elif sample['shape'] == 'star':
            points = []
            for i in range(10):
                angle = i * np.pi / 5
                radius = size//2 if i % 2 == 0 else size//4
                x = center + radius * np.cos(angle - np.pi/2)
                y = center + radius * np.sin(angle - np.pi/2)
                points.append((x, y))
            draw.polygon(points, fill=color)
        
        elif sample['shape'] == 'hexagon':
            points = []
            for i in range(6):
                angle = i * np.pi / 3
                x = center + size//2 * np.cos(angle)
                y = center + size//2 * np.sin(angle)
                points.append((x, y))
            draw.polygon(points, fill=color)
        
        # Add text label
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text = sample['name'].split('_')[1].upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = center - text_width // 2
        text_y = center + size//2 + 20
        
        draw.text((text_x, text_y), text, fill=(50, 50, 50, 255), font=font)
        
        # Save image
        file_path = sample_dir / f"{sample['name']}.png"
        img.save(file_path, 'PNG')
        created_files.append(file_path)
    
    return created_files

if __name__ == "__main__":
    # Demo usage
    if IMAGING_AVAILABLE:
        print("🚀 Favicon Processor Demo")
        print("=" * 30)
        
        # Create sample images
        sample_files = create_sample_images()
        print(f"✅ Created {len(sample_files)} sample images")
        
        # Initialize processor
        processor = BatchFaviconProcessor()
        
        # Process sample images
        results = processor.batch_process_directory(Path("sample_images"))
        
        # Generate report
        report = processor.generate_processing_report(results)
        
        print(f"\n📊 Processing completed:")
        print(f"   • Processed: {report['summary']['successful']}/{report['summary']['total_processed']}")
        print(f"   • Files created: {report['summary']['total_files_created']}")
        print(f"   • Success rate: {report['summary']['success_rate']:.1f}%")
        print(f"   • Output directory: {processor.output_dir}")
    else:
        print("❌ Please install required packages: pip install Pillow numpy tqdm")
