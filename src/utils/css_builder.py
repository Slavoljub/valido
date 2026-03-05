"""
CSS Building System for ValidoAI Application
Automated CSS building, optimization, and processing
"""

import os
import sys
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import hashlib
import gzip
import time

logger = logging.getLogger(__name__)

class CSSBuilder:
    """Automated CSS building and optimization system"""
    
    def __init__(self, static_dir: str = "static", css_dir: str = "css"):
        self.static_dir = Path(static_dir)
        self.css_dir = self.static_dir / css_dir
        self.build_dir = self.static_dir / "build"
        self.temp_dir = self.static_dir / "temp"
        
        # Create directories
        self.css_dir.mkdir(parents=True, exist_ok=True)
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # CSS files to process
        self.css_files = {
            "main": self.css_dir / "main.css",
            "components": self.css_dir / "components.css",
            "input": self.css_dir / "input.css",
            "output": self.css_dir / "output.css"
        }
        
        # Build configuration
        self.config = {
            "minify": True,
            "purge": True,
            "source_maps": True,
            "compress": True,
            "watch": False,
            "hot_reload": False
        }
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are available"""
        dependencies = {
            "node": False,
            "npm": False,
            "tailwindcss": False,
            "postcss": False,
            "autoprefixer": False,
            "cssnano": False
        }
        
        # Check Node.js and npm
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            dependencies["node"] = result.returncode == 0
        except FileNotFoundError:
            pass
        
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            dependencies["npm"] = result.returncode == 0
        except FileNotFoundError:
            pass
        
        # Check if Tailwind CSS is installed
        try:
            result = subprocess.run(["npx", "tailwindcss", "--version"], capture_output=True, text=True)
            dependencies["tailwindcss"] = result.returncode == 0
        except FileNotFoundError:
            pass
        
        return dependencies
    
    def install_dependencies(self) -> bool:
        """Install required npm dependencies"""
        try:
            # Create package.json if it doesn't exist
            package_json = Path("package.json")
            if not package_json.exists():
                package_data = {
                    "name": "validoai-css",
                    "version": "1.0.0",
                    "description": "CSS build system for ValidoAI",
                    "scripts": {
                        "build": "tailwindcss -i ./static/css/tailwind.css -o ./static/build/tailwind.min.css --minify",
                        "watch": "tailwindcss -i ./static/css/tailwind.css -o ./static/build/tailwind.min.css --watch",
                        "dev": "tailwindcss -i ./static/css/tailwind.css -o ./static/build/tailwind.css"
                    },
                    "devDependencies": {
                        "tailwindcss": "^3.4.0",
                        "postcss": "^8.4.0",
                        "autoprefixer": "^10.4.0",
                        "cssnano": "^6.0.0"
                    }
                }
                
                with open(package_json, 'w') as f:
                    json.dump(package_data, f, indent=2)
            
            # Install dependencies
            subprocess.run(["npm", "install"], check=True)
            logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def create_tailwind_config(self) -> bool:
        """Create Tailwind CSS configuration file"""
        try:
            config = {
                "content": [
                    "./templates/**/*.html",
                    "./templates/**/*.jinja",
                    "./src/**/*.py",
                    "./static/**/*.js"
                ],
                "theme": {
                    "extend": {
                        "colors": {
                            "primary": {
                                "50": "#f0fdf4",
                                "100": "#dcfce7",
                                "200": "#bbf7d0",
                                "300": "#86efac",
                                "400": "#4ade80",
                                "500": "#22c55e",
                                "600": "#16a34a",
                                "700": "#15803d",
                                "800": "#166534",
                                "900": "#14532d"
                            }
                        }
                    }
                },
                "plugins": []
            }
            
            config_path = Path("tailwind.config.js")
            with open(config_path, 'w') as f:
                f.write("module.exports = " + json.dumps(config, indent=2))
            
            logger.info("Tailwind config created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Tailwind config: {e}")
            return False
    
    def create_postcss_config(self) -> bool:
        """Create PostCSS configuration file"""
        try:
            config = {
                "plugins": {
                    "tailwindcss": {},
                    "autoprefixer": {},
                    "cssnano": {
                        "preset": "default"
                    }
                }
            }
            
            config_path = Path("postcss.config.js")
            with open(config_path, 'w') as f:
                f.write("module.exports = " + json.dumps(config, indent=2))
            
            logger.info("PostCSS config created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create PostCSS config: {e}")
            return False
    
    def build_tailwind_css(self) -> bool:
        """Build Tailwind CSS"""
        try:
            # Create input CSS file if it doesn't exist
            input_file = self.css_files["tailwind"]
            if not input_file.exists():
                input_file.parent.mkdir(parents=True, exist_ok=True)
                with open(input_file, 'w') as f:
                    f.write("""@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles */
@layer components {
    .btn-primary {
        @apply bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded;
    }
    
    .card {
        @apply bg-white rounded-lg shadow-md p-6;
    }
    
    .nav-link {
        @apply text-gray-700 hover:text-primary-600 transition-colors duration-200;
    }
}""")
            
            # Build command
            output_file = self.build_dir / "tailwind.min.css"
            cmd = [
                "npx", "tailwindcss",
                "-i", str(input_file),
                "-o", str(output_file),
                "--minify"
            ]
            
            if self.config["source_maps"]:
                cmd.extend(["--source-map"])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Tailwind CSS built successfully: {output_file}")
                return True
            else:
                logger.error(f"Tailwind CSS build failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error building Tailwind CSS: {e}")
            return False
    
    def build_custom_css(self) -> bool:
        """Build custom CSS files"""
        try:
            # Process main.css
            main_css = self.css_files["main"]
            if main_css.exists():
                output_file = self.build_dir / "main.min.css"
                self._process_css_file(main_css, output_file)
            
            # Process components.css
            components_css = self.css_files["components"]
            if components_css.exists():
                output_file = self.build_dir / "components.min.css"
                self._process_css_file(components_css, output_file)
            
            return True
            
        except Exception as e:
            logger.error(f"Error building custom CSS: {e}")
            return False
    
    def _process_css_file(self, input_file: Path, output_file: Path) -> bool:
        """Process individual CSS file"""
        try:
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # Minify if enabled
            if self.config["minify"]:
                css_content = self._minify_css(css_content)
            
            # Write output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            # Compress if enabled
            if self.config["compress"]:
                self._compress_file(output_file)
            
            logger.info(f"CSS file processed: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing CSS file {input_file}: {e}")
            return False
    
    def _minify_css(self, css_content: str) -> str:
        """Basic CSS minification"""
        # Remove comments
        import re
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove extra whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        css_content = re.sub(r';\s*}', '}', css_content)
        css_content = re.sub(r'{\s*', '{', css_content)
        css_content = re.sub(r'}\s*', '}', css_content)
        
        return css_content.strip()
    
    def _compress_file(self, file_path: Path) -> bool:
        """Compress file with gzip"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            gzip_path = file_path.with_suffix(file_path.suffix + '.gz')
            with gzip.open(gzip_path, 'wb') as f:
                f.write(content)
            
            logger.info(f"File compressed: {gzip_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error compressing file {file_path}: {e}")
            return False
    
    def generate_css_manifest(self) -> str:
        """Generate CSS manifest file"""
        try:
            manifest = {
                "version": "1.0.0",
                "timestamp": time.time(),
                "files": {},
                "hashes": {}
            }
            
            # Add built CSS files
            for css_file in self.build_dir.glob("*.css"):
                file_hash = self._get_file_hash(css_file)
                manifest["files"][css_file.name] = {
                    "path": str(css_file),
                    "size": css_file.stat().st_size,
                    "hash": file_hash
                }
                manifest["hashes"][css_file.name] = file_hash
            
            manifest_path = self.build_dir / "css-manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            return str(manifest_path)
            
        except Exception as e:
            logger.error(f"Error generating CSS manifest: {e}")
            return ""
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def watch_css(self) -> bool:
        """Watch CSS files for changes"""
        try:
            input_file = self.css_files["tailwind"]
            output_file = self.build_dir / "tailwind.min.css"
            
            cmd = [
                "npx", "tailwindcss",
                "-i", str(input_file),
                "-o", str(output_file),
                "--watch"
            ]
            
            logger.info("Starting CSS watch mode...")
            subprocess.run(cmd)
            return True
            
        except Exception as e:
            logger.error(f"Error starting CSS watch: {e}")
            return False
    
    def cleanup_build(self):
        """Clean up build directory"""
        try:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            self.build_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Build directory cleaned")
        except Exception as e:
            logger.error(f"Error cleaning build directory: {e}")
    
    def build_all(self) -> Dict[str, any]:
        """Build all CSS files"""
        logger.info("Starting CSS build process...")
        
        # Check dependencies
        dependencies = self.check_dependencies()
        if not dependencies["node"] or not dependencies["npm"]:
            logger.warning("Node.js and npm are required for CSS building")
            return {
                "success": False, 
                "error": "Missing Node.js/npm",
                "warning": "CSS optimization disabled - using existing CSS files"
            }
        
        try:
            # Use npm script to build CSS
            cmd = ["npm", "run", "build-prod"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                logger.info("CSS build completed successfully")
                return {
                    "success": True,
                    "message": "CSS built successfully using npm script"
                }
            else:
                logger.error(f"CSS build failed: {result.stderr}")
                return {
                    "success": False,
                    "error": f"Build failed: {result.stderr}",
                    "warning": "CSS optimization disabled - using existing CSS files"
                }
                
        except Exception as e:
            logger.error(f"Error building CSS: {e}")
            return {
                "success": False,
                "error": str(e),
                "warning": "CSS optimization disabled - using existing CSS files"
            }

# Global CSS builder instance
css_builder = CSSBuilder()

def build_css():
    """Build all CSS files"""
    return css_builder.build_all()

def watch_css():
    """Watch CSS files for changes"""
    return css_builder.watch_css()

def check_css_dependencies():
    """Check CSS build dependencies"""
    return css_builder.check_dependencies()
