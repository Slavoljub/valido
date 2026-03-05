#!/usr/bin/env python3
"""
Hypercorn ASGI Server Configuration for ValidoAI
=================================================

Production-ready ASGI server configuration with HTTP/2 and HTTP/3 support.
Supports SSL/TLS encryption with automatic certificate handling.

Features:
- HTTP/2.0 and HTTP/3.0 support
- SSL/TLS encryption
- Production security settings
- WebSocket support
- Performance optimization
"""

import os
import ssl
import asyncio
import logging
from typing import Optional
import hypercorn
from hypercorn.config import Config
from hypercorn.asyncio import serve

logger = logging.getLogger(__name__)

class HypercornServer:
    """Production Hypercorn ASGI server for ValidoAI"""

    def __init__(self, app):
        self.app = app
        self.config = self._create_config()

    def _create_config(self) -> Config:
        """Create Hypercorn configuration"""
        config = Config()

        # Basic server configuration
        config.bind = [f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('HTTP_PORT', '5000')}"]
        config.worker_class = "asyncio"
        config.workers = int(os.getenv('WORKERS', '1'))
        config.worker_connections = int(os.getenv('WORKER_CONNECTIONS', '1000'))

        # SSL/TLS configuration
        if os.getenv('SSL_ENABLED', 'false').lower() == 'true':
            ssl_enabled = self._configure_ssl(config)
            if ssl_enabled:
                https_bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('HTTPS_PORT', '5001')}"
                config.bind.append(https_bind)
                logger.info(f"✅ SSL enabled for {https_bind}")

        # Performance configuration
        config.keep_alive_timeout = float(os.getenv('KEEP_ALIVE_TIMEOUT', '30'))
        config.graceful_timeout = float(os.getenv('GRACEFUL_TIMEOUT', '30'))
        config.request_timeout = float(os.getenv('REQUEST_TIMEOUT', '30'))

        # Security configuration
        config.server_names = ["ValidoAI"]
        config.access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
        config.error_log_format = '%(t)s %(l)s %(m)s'

        # HTTP/2 and HTTP/3 configuration
        config.h2 = True  # Enable HTTP/2
        config.h3 = True  # Enable HTTP/3 (if supported)

        return config

    def _configure_ssl(self, config: Config) -> bool:
        """Configure SSL/TLS settings"""
        try:
            cert_file = os.getenv('SSL_CERT_FILE', 'certs/certificate.pem')
            key_file = os.getenv('SSL_KEY_FILE', 'certs/private.key')

            # Check if certificate files exist
            if not os.path.exists(cert_file) or not os.path.exists(key_file):
                logger.warning(f"⚠️ SSL certificate files not found: {cert_file}, {key_file}")
                logger.info("💡 SSL will be disabled. Generate certificates or set SSL_ENABLED=false")
                return False

            # Configure SSL context
            config.certfile = cert_file
            config.keyfile = key_file

            # SSL security settings
            config.ssl_options = {
                'ssl_version': ssl.PROTOCOL_TLSv1_2,
                'ciphers': 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256',
                'options': ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            }

            logger.info(f"✅ SSL configured with cert: {cert_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error configuring SSL: {e}")
            return False

    async def serve(self):
        """Start the Hypercorn server"""
        try:
            logger.info("🚀 Starting Hypercorn ASGI server...")
            logger.info(f"📊 Server configuration: {len(self.config.bind)} bindings")

            for bind_addr in self.config.bind:
                logger.info(f"🌐 Listening on: {bind_addr}")

            await serve(self.app, self.config)

        except Exception as e:
            logger.error(f"❌ Error starting Hypercorn server: {e}")
            raise

def create_hypercorn_server(app) -> HypercornServer:
    """Create Hypercorn server instance"""
    return HypercornServer(app)

async def run_hypercorn_server(app, host: str = '0.0.0.0',
                              http_port: int = 5000,
                              https_port: int = 5001):
    """Run Hypercorn server with the Flask app"""
    try:
        # Set environment variables
        os.environ['HOST'] = host
        os.environ['HTTP_PORT'] = str(http_port)
        os.environ['HTTPS_PORT'] = str(https_port)

        # Create server instance
        server = create_hypercorn_server(app)

        logger.info("🚀 Starting ValidoAI with Hypercorn ASGI server...")
        logger.info(f"📊 Host: {host}")
        logger.info(f"🌐 HTTP Port: {http_port}")
        if https_port and os.getenv('SSL_ENABLED', 'false').lower() == 'true':
            logger.info(f"🔒 HTTPS Port: {https_port}")
        logger.info(f"⚙️ Workers: {server.config.workers}")

        # Start the server
        await server.serve()

    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        raise

# For direct execution
if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    async def main():
        """Main entry point for direct execution"""
        try:
            from app import create_app

            # Create Flask app
            app = create_app('production')

            # Get configuration from environment
            host = os.getenv('HOST', '0.0.0.0')
            http_port = int(os.getenv('HTTP_PORT', '5000'))
            https_port = int(os.getenv('HTTPS_PORT', '5001'))

            # Run server
            await run_hypercorn_server(app, host, http_port, https_port)

        except Exception as e:
            logger.error(f"❌ Error in main: {e}")
            sys.exit(1)

    # Run the server
    asyncio.run(main())