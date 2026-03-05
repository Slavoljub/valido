#!/usr/bin/env python3
"""
Minimal Hypercorn ASGI test to verify HTTP/HTTPS functionality
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from flask import Flask
    from asgiref.wsgi import WsgiToAsgi
    from hypercorn.config import Config as HypercornConfig
    from hypercorn.asyncio import serve as hypercorn_serve
    
    # Create minimal Flask app
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ValidoAI - Hypercorn Test</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .status { color: #28a745; font-weight: bold; }
                .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 ValidoAI - Hypercorn ASGI Server</h1>
                <p class="status">✅ Server is running successfully!</p>
                <div class="info">
                    <h3>🔧 Configuration</h3>
                    <ul>
                        <li><strong>Server:</strong> Hypercorn ASGI</li>
                        <li><strong>HTTP:</strong> http://localhost:5000</li>
                        <li><strong>HTTPS:</strong> https://localhost:5001</li>
                        <li><strong>HTTP/2:</strong> Enabled</li>
                        <li><strong>HTTP/3:</strong> Enabled</li>
                    </ul>
                </div>
                <p>🎯 Ready for production deployment!</p>
            </div>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "server": "hypercorn", "protocol": "asgi"}
    
    # Convert Flask app to ASGI
    asgi_app = WsgiToAsgi(app)
    
    async def run_server():
        """Run Hypercorn ASGI server with HTTP and HTTPS"""
        try:
            # Server configuration
            host = os.environ.get('HOST', '0.0.0.0')
            http_port = int(os.environ.get('HTTP_PORT', '5000'))
            https_port = int(os.environ.get('HTTPS_PORT', '5001'))
            use_https = os.environ.get('USE_HTTPS', 'true').lower() == 'true'
            
            # Hypercorn configuration
            config = HypercornConfig()
            config.bind = [f"{host}:{http_port}"]
            config.worker_class = "asyncio"
            config.workers = 1
            config.h2 = True  # HTTP/2 support
            config.h3 = True  # HTTP/3 support
            config.access_log_format = '%(h)s %(r)s %(s)s %(b)s'
            config.accesslog = '-'
            config.errorlog = '-'
            
            logger.info(f"🌐 Starting HTTP server on {host}:{http_port}")
            
            # Add HTTPS if enabled and certificates exist
            if use_https:
                cert_file = os.environ.get('SSL_CERT_FILE', 'certs/localhost-cert.crt')
                key_file = os.environ.get('SSL_KEY_FILE', 'certs/localhost-key.pem')
                
                if os.path.exists(cert_file) and os.path.exists(key_file):
                    config.certfile = cert_file
                    config.keyfile = key_file
                    config.bind.append(f"{host}:{https_port}")
                    logger.info(f"🔒 Starting HTTPS server on {host}:{https_port}")
                    logger.info(f"   Certificate: {cert_file}")
                    logger.info(f"   Private Key: {key_file}")
                else:
                    logger.warning(f"⚠️ SSL certificates not found: {cert_file}, {key_file}")
                    logger.info("🌐 Running HTTP only")
            
            logger.info("🚀 Starting Hypercorn ASGI server...")
            await hypercorn_serve(asgi_app, config)
            
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
            raise
    
    if __name__ == '__main__':
        try:
            asyncio.run(run_server())
        except KeyboardInterrupt:
            logger.info("👋 Server stopped by user")
        except Exception as e:
            logger.error(f"❌ Startup error: {e}")
            sys.exit(1)

except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("📦 Install with: pip install flask hypercorn asgiref python-dotenv")
    sys.exit(1)
