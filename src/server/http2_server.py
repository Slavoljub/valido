import ssl
import os
import time
from datetime import datetime
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class HTTP2Handler(WSGIRequestHandler):
    """HTTP/2 request handler"""
    
    def setup(self):
        """Setup HTTP/2 handler"""
        super().setup()
        self.protocol_version = 'HTTP/2.0'
    
    def send_header(self, keyword, value):
        """Send HTTP/2 headers"""
        if keyword.lower() == 'server':
            value = 'ValidoAI-HTTP2/1.0'
        super().send_header(keyword, value)

class HTTP2Server:
    """HTTP/2 server with SSL support"""
    
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.ssl_context = self.create_ssl_context()
        self.monitor = ServerMonitor()
    
    def create_ssl_context(self):
        """Create SSL context with certificates"""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        cert_file = self.config.get('SSL_CERT_FILE', 'certs/validoai.crt')
        key_file = self.config.get('SSL_KEY_FILE', 'certs/validoai.key')
        
        if os.path.exists(cert_file) and os.path.exists(key_file):
            context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        else:
            print("Certificate files not found. Generating self-signed certificate...")
            self.generate_self_signed_cert()
            context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        
        return context
    
    def generate_self_signed_cert(self):
        """Generate self-signed certificate for development"""
        cert_dir = 'certs'
        cert_file = os.path.join(cert_dir, 'validoai.crt')
        key_file = os.path.join(cert_dir, 'validoai.key')
        
        # Create certs directory if it doesn't exist
        os.makedirs(cert_dir, exist_ok=True)
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "RS"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Serbia"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Belgrade"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ValidoAI"),
            x509.NameAttribute(NameOID.COMMON_NAME, "ai.valido.online"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("ai.valido.online"),
                x509.DNSName("localhost"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Save certificate and key
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print(f"Self-signed certificate generated: {cert_file}")
        print(f"Private key generated: {key_file}")
    
    def run_server(self):
        """Run HTTP/2 server"""
        host = self.config.get('HOST', '0.0.0.0')
        port = self.config.get('PORT', 443)
        
        server = WSGIServer(
            (host, port),
            self.app,
            ssl_context=self.ssl_context,
            handler_class=HTTP2Handler
        )
        
        print(f"Starting HTTP/2 server on https://{host}:{port}")
        print(f"Certificate: {self.config.get('SSL_CERT_FILE', 'certs/validoai.crt')}")
        print(f"Private Key: {self.config.get('SSL_KEY_FILE', 'certs/validoai.key')}")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down HTTP/2 server...")
        except Exception as e:
            print(f"Error running HTTP/2 server: {e}")

class ServerMonitor:
    """Monitor server health and metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'requests_total': 0,
            'requests_per_second': 0,
            'response_time_avg': 0,
            'error_rate': 0,
            'memory_usage': 0,
            'cpu_usage': 0
        }
    
    def update_metrics(self, request_time, status_code):
        """Update server metrics"""
        self.metrics['requests_total'] += 1
        self.metrics['response_time_avg'] = (
            (self.metrics['response_time_avg'] * (self.metrics['requests_total'] - 1) + request_time) /
            self.metrics['requests_total']
        )
        
        if status_code >= 400:
            self.metrics['error_rate'] = (
                (self.metrics['error_rate'] * (self.metrics['requests_total'] - 1) + 1) /
                self.metrics['requests_total']
            )
    
    def get_health_status(self):
        """Get server health status"""
        try:
            import psutil
            process = psutil.Process()
            self.metrics['memory_usage'] = process.memory_info().rss / 1024 / 1024  # MB
            self.metrics['cpu_usage'] = process.cpu_percent()
        except ImportError:
            pass
        
        return {
            'status': 'healthy' if self.metrics['error_rate'] < 0.05 else 'degraded',
            'metrics': self.metrics,
            'uptime': time.time() - self.start_time
        }

# Configuration
HTTP2_CONFIG = {
    'HOST': '0.0.0.0',
    'PORT': 443,
    'SSL_CERT_FILE': 'certs/validoai.crt',
    'SSL_KEY_FILE': 'certs/validoai.key',
    'SSL_CA_FILE': 'certs/ca-bundle.crt',
    'WORKERS': 4,
    'THREADS': 2,
    'MAX_REQUESTS': 1000,
    'TIMEOUT': 30,
    'KEEPALIVE': 5,
    'COMPRESSION': True,
    'CACHE_CONTROL': True,
    'SECURITY_HEADERS': True
}

# Security Headers
SECURITY_HEADERS = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
}

