#!/usr/bin/env python3
"""
ValidoAI System Operations (DRY Implementation)
Consolidated system-level operations: SSL, PostgreSQL, services, etc.
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional
import urllib.parse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class SystemOperations:
    """Consolidated system operations manager"""

    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == 'windows'
        self.is_linux = self.system == 'linux'
        self.is_macos = self.system == 'darwin'

        # Project directories
        self.project_dir = Path.cwd()
        self.ssl_dir = self.project_dir / 'certs'
        self.ssl_dir.mkdir(exist_ok=True)

    def run_command(self, command: List[str], shell: bool = False,
                   capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Run system command with proper error handling"""
        try:
            if shell and isinstance(command, list):
                command = ' '.join(command)

            result = subprocess.run(
                command,
                shell=shell,
                capture_output=capture_output,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(command) if isinstance(command, list) else command}")
            print(f"Error: {e.stderr}")
            raise
        except FileNotFoundError as e:
            print(f"❌ Command not found: {command[0] if isinstance(command, list) else command.split()[0]}")
            raise

    def generate_ssl_certificate(self, domain: str = "validoai.test",
                               cert_dir: Optional[str] = None,
                               days: int = 365) -> Dict[str, str]:
        """Generate SSL certificate for domain"""
        print(f"🔐 Generating SSL certificate for {domain}")

        if cert_dir:
            ssl_path = Path(cert_dir)
        else:
            ssl_path = self.ssl_dir

        ssl_path.mkdir(exist_ok=True)

        cert_file = ssl_path / f"{domain}.crt"
        key_file = ssl_path / f"{domain}.key"

        # Generate private key
        print("Generating private key...")
        self.run_command([
            'openssl', 'genrsa', '-out', str(key_file), '2048'
        ])

        # Generate certificate signing request (CSR)
        print("Generating certificate signing request...")
        csr_file = ssl_path / f"{domain}.csr"
        self.run_command([
            'openssl', 'req', '-new', '-key', str(key_file),
            '-out', str(csr_file), '-subj',
            f'/C=US/ST=State/L=City/O=Organization/CN={domain}'
        ])

        # Generate self-signed certificate
        print("Generating self-signed certificate...")
        self.run_command([
            'openssl', 'x509', '-req', '-days', str(days),
            '-in', str(csr_file), '-signkey', str(key_file),
            '-out', str(cert_file)
        ])

        # Clean up CSR file
        if csr_file.exists():
            csr_file.unlink()

        print("✅ SSL certificate generated successfully"        print(f"   Certificate: {cert_file}")
        print(f"   Private Key: {key_file}")

        return {
            'certificate': str(cert_file),
            'private_key': str(key_file),
            'domain': domain,
            'expires_days': days
        }

    def setup_postgresql_extensions(self, database: str = "validoai",
                                  user: str = "validoai",
                                  host: str = "localhost",
                                  port: int = 5432):
        """Setup PostgreSQL with all extensions"""
        print("🐘 Setting up PostgreSQL with extensions")

        # PostgreSQL connection string
        conn_str = f"postgresql://{user}@{host}:{port}/{database}"

        # SQL commands to install all extensions
        extension_commands = [
            # Essential extensions
            "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
            "CREATE EXTENSION IF NOT EXISTS \"pg_stat_statements\";",
            "CREATE EXTENSION IF NOT EXISTS \"pg_buffercache\";",
            "CREATE EXTENSION IF NOT EXISTS \"pg_prewarm\";",

            # Vector and similarity extensions (AI/ML support)
            "CREATE EXTENSION IF NOT EXISTS \"pgvector\";",
            "CREATE EXTENSION IF NOT EXISTS \"pg_similarity\";",
            "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";",

            # Geospatial extensions
            "CREATE EXTENSION IF NOT EXISTS \"postgis\";",
            "CREATE EXTENSION IF NOT EXISTS \"postgis_topology\";",

            # Time-series extension
            "CREATE EXTENSION IF NOT EXISTS \"timescaledb\";",

            # Advanced indexing
            "CREATE EXTENSION IF NOT EXISTS \"btree_gist\";",
            "CREATE EXTENSION IF NOT EXISTS \"btree_gin\";",
            "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";",

            # Full-text search improvements
            "CREATE EXTENSION IF NOT EXISTS \"unaccent\";",
            "CREATE EXTENSION IF NOT EXISTS \"pg_freespacemap\";",

            # Monitoring extensions
            "CREATE EXTENSION IF NOT EXISTS \"pg_stat_monitor\";"
        ]

        print("Installing PostgreSQL extensions...")

        try:
            # Try using psql command line tool
            for sql in extension_commands:
                try:
                    self.run_command([
                        'psql', conn_str, '-c', sql
                    ], check=False)  # Don't fail if extension already exists
                except:
                    print(f"⚠️  Could not install extension: {sql.split()[3]}")

            print("✅ PostgreSQL extensions setup completed")

        except Exception as e:
            print(f"❌ Error setting up PostgreSQL extensions: {e}")
            print("Please ensure PostgreSQL is installed and running")
            print("Manual setup instructions:")
            print(f"1. Connect to database: psql {conn_str}")
            print("2. Run the following commands:")
            for sql in extension_commands:
                print(f"   {sql}")

    def compile_translations(self, languages: List[str] = None):
        """Compile translation files"""
        print("🌐 Compiling translations")

        if languages is None:
            # Auto-detect available languages
            translations_dir = self.project_dir / 'translations'
            if translations_dir.exists():
                languages = [d.name for d in translations_dir.iterdir() if d.is_dir()]
            else:
                languages = ['sr', 'en']

        print(f"Compiling translations for: {', '.join(languages)}")

        for lang in languages:
            po_file = self.project_dir / 'translations' / lang / 'LC_MESSAGES' / 'messages.po'
            mo_file = self.project_dir / 'translations' / lang / 'LC_MESSAGES' / 'messages.mo'

            if po_file.exists():
                try:
                    self.run_command([
                        'msgfmt', '-o', str(mo_file), str(po_file)
                    ])
                    print(f"✅ Compiled {lang} translations")
                except Exception as e:
                    print(f"⚠️  Could not compile {lang} translations: {e}")
            else:
                print(f"⚠️  Translation file not found: {po_file}")

    def setup_service_config(self, service_type: str = "flask",
                           port: int = 5000,
                           workers: int = 1,
                           environment: str = "production"):
        """Setup service configuration files"""
        print(f"⚙️  Setting up {service_type} service configuration")

        config_dir = self.project_dir / 'config'
        config_dir.mkdir(exist_ok=True)

        if service_type.lower() == "gunicorn":
            # Create Gunicorn configuration
            gunicorn_config = config_dir / 'gunicorn.conf.py'
            config_content = f'''
# Gunicorn configuration for ValidoAI
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes
workers = {workers}
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "/var/log/validoai/access.log"
errorlog = "/var/log/validoai/error.log"
logfile = "/var/log/validoai/gunicorn.log"

# Process naming
proc_name = "validoai"

# Server mechanics
daemon = False
pidfile = "/var/run/validoai.pid"
user = "validoai"
group = "validoai"

# SSL (uncomment if using SSL)
# keyfile = "/path/to/private.key"
# certfile = "/path/to/certificate.crt"
'''
            with open(gunicorn_config, 'w') as f:
                f.write(config_content)

            print(f"✅ Gunicorn config created: {gunicorn_config}")

        elif service_type.lower() == "nginx":
            # Create Nginx configuration
            nginx_config = config_dir / 'nginx.conf'
            config_content = f'''
# Nginx configuration for ValidoAI
upstream validoai {{
    server 127.0.0.1:{port};
}}

server {{
    listen 80;
    server_name _;

    location / {{
        proxy_pass http://validoai;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    # Static files
    location /static/ {{
        alias {self.project_dir}/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}}
'''
            with open(nginx_config, 'w') as f:
                f.write(config_content)

            print(f"✅ Nginx config created: {nginx_config}")

        elif service_type.lower() == "systemd":
            # Create SystemD service file
            systemd_config = config_dir / 'validoai.service'
            config_content = f'''
[Unit]
Description=ValidoAI Application
After=network.target
Wants=postgresql.service

[Service]
Type=simple
User=validoai
Group=validoai
WorkingDirectory={self.project_dir}
Environment=FLASK_ENV={environment}
ExecStart={self.project_dir}/.venv/bin/gunicorn app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=validoai

[Install]
WantedBy=multi-user.target
'''
            with open(systemd_config, 'w') as f:
                f.write(config_content)

            print(f"✅ SystemD service config created: {systemd_config}")

    def create_backup_config(self):
        """Create backup configuration"""
        print("📦 Creating backup configuration")

        backup_config = {
            'database': {
                'enabled': True,
                'schedule': '0 2 * * *',  # Daily at 2 AM
                'retention_days': 30,
                'compress': True,
                'encrypt': False
            },
            'files': {
                'enabled': True,
                'schedule': '0 3 * * *',  # Daily at 3 AM
                'retention_days': 7,
                'include': [
                    'data/',
                    'uploads/',
                    'logs/',
                    'config/'
                ],
                'exclude': [
                    'node_modules/',
                    '__pycache__/',
                    '*.log'
                ]
            },
            'remote': {
                'enabled': False,
                'provider': 's3',  # s3, gcp, azure
                'bucket': '',
                'access_key': '',
                'secret_key': ''
            }
        }

        config_file = self.project_dir / 'config' / 'backup.json'
        with open(config_file, 'w') as f:
            json.dump(backup_config, f, indent=2)

        print(f"✅ Backup configuration created: {config_file}")

    def generate_environment_template(self, domain: str = "validoai.test",
                                    database_type: str = "sqlite",
                                    ai_enabled: bool = True):
        """Generate environment template"""
        print("📝 Generating environment template")

        env_template = f'''# ValidoAI Environment Configuration
# Generated for domain: {domain}

# =============================================================================
# FLASK CONFIGURATION
# =============================================================================
FLASK_ENV=production
SECRET_KEY={self.generate_secret_key()}
DEBUG=false
TESTING=false

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_TYPE={database_type}
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=validoai
DATABASE_USER=validoai
DATABASE_PASSWORD=secure_password_change_me

# =============================================================================
# AI/ML CONFIGURATION
# =============================================================================
AI_ENABLED={str(ai_enabled).lower()}
AI_DEFAULT_MODEL=qwen-3
AI_MODEL_PATH=local_llm_models/
GPU_ENABLED=false

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
JWT_SECRET_KEY={self.generate_secret_key()}
BCRYPT_LOG_ROUNDS=12

# =============================================================================
# DOMAIN & SERVER CONFIGURATION
# =============================================================================
DOMAIN={domain}
PROJECT_DIR={self.project_dir}

# =============================================================================
# FILE UPLOAD CONFIGURATION
# =============================================================================
UPLOAD_FOLDER={self.project_dir}/uploads
MAX_CONTENT_LENGTH=50MB
ALLOWED_EXTENSIONS=pdf,doc,docx,xlsx,csv,jpg,jpeg,png

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL=INFO
LOG_FILE={self.project_dir}/logs/app.log

# =============================================================================
# EXTERNAL API KEYS (Optional)
# =============================================================================
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
# COHERE_API_KEY=your_cohere_key_here
# GOOGLE_API_KEY=your_google_key_here
# MISTRAL_API_KEY=your_mistral_key_here
# OLLAMA_API_KEY=your_ollama_key_here

# =============================================================================
# EMAIL CONFIGURATION (Optional)
# =============================================================================
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your_email@gmail.com
# SMTP_PASSWORD=your_app_password

# =============================================================================
# SSL CONFIGURATION (Optional)
# =============================================================================
# SSL_CERT_PATH={self.ssl_dir}/{domain}.crt
# SSL_KEY_PATH={self.ssl_dir}/{domain}.key
'''

        env_file = self.project_dir / '.env.example'
        with open(env_file, 'w') as f:
            f.write(env_template)

        print(f"✅ Environment template created: {env_file}")
        return env_file

    def generate_secret_key(self, length: int = 32) -> str:
        """Generate a secure secret key"""
        import secrets
        return secrets.token_urlsafe(length)

    def system_info(self):
        """Display system information"""
        print("🖥️  System Information")
        print("=" * 50)

        info = {
            'OS': platform.system(),
            'OS Version': platform.version(),
            'Architecture': platform.machine(),
            'Python Version': sys.version.split()[0],
            'Project Directory': str(self.project_dir),
            'SSL Directory': str(self.ssl_dir)
        }

        for key, value in info.items():
            print("<20")

    def cleanup_system(self):
        """Clean up system files and cache"""
        print("🧹 System cleanup")

        # Remove Python cache files
        cache_dirs = ['__pycache__', '*.pyc', '*.pyo']
        for pattern in cache_dirs:
            for path in self.project_dir.rglob(pattern):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    import shutil
                    shutil.rmtree(path)

        # Clean npm cache if node_modules exists
        if (self.project_dir / 'node_modules').exists():
            try:
                self.run_command(['npm', 'cache', 'clean', '--force'])
                print("✅ NPM cache cleaned")
            except:
                print("⚠️  Could not clean NPM cache")

        # Clean pip cache
        try:
            self.run_command(['pip', 'cache', 'purge'])
            print("✅ PIP cache cleaned")
        except:
            print("⚠️  Could not clean PIP cache")

        print("✅ System cleanup completed")

def main():
    parser = argparse.ArgumentParser(description='ValidoAI System Operations')
    parser.add_argument('action', choices=[
        'ssl', 'postgres', 'translate', 'service', 'backup', 'env', 'info', 'cleanup'
    ], help='Action to perform')

    # SSL options
    parser.add_argument('--domain', default='validoai.test', help='Domain for SSL certificate')
    parser.add_argument('--ssl-dir', help='SSL certificate directory')
    parser.add_argument('--ssl-days', type=int, default=365, help='SSL certificate validity days')

    # PostgreSQL options
    parser.add_argument('--db-name', default='validoai', help='Database name')
    parser.add_argument('--db-user', default='validoai', help='Database user')
    parser.add_argument('--db-host', default='localhost', help='Database host')
    parser.add_argument('--db-port', type=int, default=5432, help='Database port')

    # Service options
    parser.add_argument('--service-type', choices=['gunicorn', 'nginx', 'systemd'],
                       help='Service type for configuration')
    parser.add_argument('--port', type=int, default=5000, help='Service port')
    parser.add_argument('--workers', type=int, default=1, help='Number of workers')
    parser.add_argument('--environment', default='production', help='Environment setting')

    # Translation options
    parser.add_argument('--languages', nargs='*', help='Languages for translation compilation')

    # Environment options
    parser.add_argument('--database-type', default='sqlite', help='Database type for environment template')
    parser.add_argument('--ai-enabled', action='store_true', help='Enable AI in environment template')

    args = parser.parse_args()

    sys_ops = SystemOperations()

    try:
        if args.action == 'ssl':
            sys_ops.generate_ssl_certificate(args.domain, args.ssl_dir, args.ssl_days)

        elif args.action == 'postgres':
            sys_ops.setup_postgresql_extensions(
                args.db_name, args.db_user, args.db_host, args.db_port
            )

        elif args.action == 'translate':
            sys_ops.compile_translations(args.languages)

        elif args.action == 'service':
            if not args.service_type:
                print("❌ Please specify service type with --service-type")
                sys.exit(1)
            sys_ops.setup_service_config(
                args.service_type, args.port, args.workers, args.environment
            )

        elif args.action == 'backup':
            sys_ops.create_backup_config()

        elif args.action == 'env':
            sys_ops.generate_environment_template(
                args.domain, args.database_type, args.ai_enabled
            )

        elif args.action == 'info':
            sys_ops.system_info()

        elif args.action == 'cleanup':
            sys_ops.cleanup_system()

        print("🎉 System operation completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
