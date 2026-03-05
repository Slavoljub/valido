#!/usr/bin/env python3
"""
Production ASGI Server Runner for ValidoAI Application
Supports multiple ASGI servers: Hypercorn, Uvicorn, and Gunicorn with Uvicorn workers
"""

import os
import sys
import asyncio
import logging
from typing import Optional
import argparse

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionServerRunner:
    """Production server runner with multiple ASGI server options"""

    def __init__(self):
        self.app = None
        self.server_type = os.getenv('SERVER_TYPE', 'hypercorn').lower()

    def load_app(self):
        """Load the Flask application"""
        try:
            from app import create_app

            # Create application instance
            config_name = os.getenv('FLASK_ENV', 'production')
            self.app = create_app(config_name)

            # Initialize database and perform startup checks
            with self.app.app_context():
                from app import init_db, perform_startup_checks
                init_db()
                perform_startup_checks()

            logger.info("Flask application loaded successfully")
            return self.app

        except Exception as e:
            logger.error(f"Failed to load Flask application: {e}")
            raise

    def run_hypercorn(self):
        """Run with Hypercorn ASGI server"""
        try:
            from asgiref.wsgi import WsgiToAsgi
            from hypercorn.asyncio import serve as hypercorn_serve
            from hypercorn.config import Config as HypercornConfig

            # Import helper from app to build config consistently
            try:
                from app import build_hypercorn_config  # type: ignore
            except ImportError as e:
                logger.error(f"Failed to import build_hypercorn_config from app: {e}")
                raise

            host = os.getenv('HOST', '0.0.0.0')
            http_port = int(os.getenv('HTTP_PORT', '5000'))
            https_port = int(os.getenv('HTTPS_PORT', '5001'))
            use_https = os.getenv('USE_HTTPS', 'true').lower() == 'true'

            cfg, binds = build_hypercorn_config(host, http_port, https_port, use_https)

            logger.info("Starting Hypercorn...")
            for b in binds:
                proto = 'HTTPS' if str(https_port) in b else 'HTTP'
                logger.info(f"   {proto}: {b}")

            # Convert Flask (WSGI) to ASGI
            asgi_app = WsgiToAsgi(self.app)

            asyncio.run(hypercorn_serve(asgi_app, cfg))

        except ImportError:
            logger.error("Hypercorn not installed. Install with: pip install hypercorn[h3]")
            raise
        except Exception as e:
            logger.error(f"Failed to start Hypercorn server: {e}")
            raise

    def run_uvicorn(self):
        """Run with Uvicorn ASGI server"""
        try:
            import uvicorn

            host = os.getenv('HOST', '0.0.0.0')
            port = int(os.getenv('PORT', '5000'))
            workers = int(os.getenv('WORKERS', '1'))

            logger.info(f"Starting Uvicorn server on {host}:{port} with {workers} workers")

            # Convert Flask app to ASGI app using asgiref
            from asgiref.wsgi import WsgiToAsgi
            asgi_app = WsgiToAsgi(self.app)

            uvicorn.run(
                asgi_app,
                host=host,
                port=port,
                workers=workers,
                log_level="info",
                access_log=True,
                server_header=False,
                date_header=False
            )

        except ImportError:
            logger.error("Uvicorn not installed. Install with: pip install uvicorn")
            raise
        except Exception as e:
            logger.error(f"Failed to start Uvicorn server: {e}")
            raise

    def run_gunicorn_uvicorn(self):
        """Run with Gunicorn using Uvicorn workers"""
        try:
            # This would typically be run via command line gunicorn
            # but we can prepare the configuration
            host = os.getenv('HOST', '0.0.0.0')
            port = int(os.getenv('PORT', '5000'))
            workers = int(os.getenv('WORKERS', '4'))

            logger.info(f"Starting Gunicorn with Uvicorn workers on {host}:{port}")

            # For Gunicorn, we need to use subprocess or prepare the command
            import subprocess

            cmd = [
                "gunicorn",
                "-k", "uvicorn.workers.UvicornWorker",
                "-w", str(workers),
                "-b", f"{host}:{port}",
                "--log-level", "info",
                "--access-logfile", "-",
                "app:create_app('production')"
            ]

            logger.info(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)

        except ImportError:
            logger.error("Gunicorn not installed. Install with: pip install gunicorn")
            raise
        except Exception as e:
            logger.error(f"Failed to start Gunicorn server: {e}")
            raise

    def run(self):
        """Run the selected server"""
        try:
            self.load_app()

            if self.server_type == 'hypercorn':
                self.run_hypercorn()
            elif self.server_type == 'uvicorn':
                self.run_uvicorn()
            elif self.server_type == 'gunicorn':
                self.run_gunicorn_uvicorn()
            else:
                logger.error(f"Unknown server type: {self.server_type}")
                logger.info("Available servers: hypercorn, uvicorn, gunicorn")
                raise ValueError(f"Unsupported server type: {self.server_type}")

        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server failed: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run ValidoAI with production ASGI server')
    parser.add_argument(
        '--server',
        choices=['hypercorn', 'uvicorn', 'gunicorn'],
        default=os.getenv('SERVER_TYPE', 'hypercorn'),
        help='ASGI server to use (default: hypercorn)'
    )
    parser.add_argument(
        '--host',
        default=os.getenv('HOST', '0.0.0.0'),
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv('PORT', '5000')),
        help='Port to bind to (default: 5000)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=int(os.getenv('WORKERS', '1')),
        help='Number of worker processes (default: 1)'
    )
    parser.add_argument(
        '--https-port',
        type=int,
        default=int(os.getenv('HTTPS_PORT', '5001')),
        help='HTTPS port for Hypercorn (default: 5001)'
    )

    args = parser.parse_args()

    # Set environment variables from args
    os.environ['SERVER_TYPE'] = args.server
    os.environ['HOST'] = args.host
    os.environ['PORT'] = str(args.port)
    os.environ['WORKERS'] = str(args.workers)
    os.environ['HTTPS_PORT'] = str(args.https_port)

    # Run the server
    runner = ProductionServerRunner()
    runner.run()

if __name__ == '__main__':
    main()
