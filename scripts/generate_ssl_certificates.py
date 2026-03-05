#!/usr/bin/env python3
"""
SSL Certificate Generation Script for ValidoAI

This script generates self-signed SSL certificates for development and testing purposes.
It creates the necessary certificate files that the application expects.

Usage:
    python scripts/generate_ssl_certificates.py

Environment Variables:
    SSL_CERT_PATH: Path for the certificate file (default: certs/cert.pem)
    SSL_KEY_PATH: Path for the private key file (default: certs/key.pem)
    SSL_COMMON_NAME: Common name for the certificate (default: localhost)
    SSL_ORGANIZATION: Organization name (default: ValidoAI Development)
    SSL_VALID_DAYS: Certificate validity in days (default: 365)

Requirements:
    - Python 3.6+
    - cryptography library (pip install cryptography)
"""

import os
import sys
import ipaddress
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_ssl_certificates():
    """Generate SSL certificates for the application"""

    # Get configuration from environment variables
    cert_path = os.environ.get('SSL_CERT_PATH', 'certs/cert.pem')
    key_path = os.environ.get('SSL_KEY_PATH', 'certs/key.pem')
    common_name = os.environ.get('SSL_COMMON_NAME', 'localhost')
    organization = os.environ.get('SSL_ORGANIZATION', 'ValidoAI Development')
    valid_days = int(os.environ.get('SSL_VALID_DAYS', '365'))

    logger.info("🔐 Generating SSL certificates...")
    logger.info(f"   Certificate path: {cert_path}")
    logger.info(f"   Key path: {key_path}")
    logger.info(f"   Common name: {common_name}")
    logger.info(f"   Organization: {organization}")
    logger.info(f"   Valid days: {valid_days}")

    try:
        # Create certs directory if it doesn't exist
        os.makedirs(os.path.dirname(cert_path), exist_ok=True)
        os.makedirs(os.path.dirname(key_path), exist_ok=True)

        # Generate private key
        logger.info("   🔑 Generating private key...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # Generate certificate
        logger.info("   📄 Generating certificate...")

        # Certificate subject and issuer
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Development"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        ])

        # Certificate details
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
            datetime.utcnow() + timedelta(days=valid_days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.DNSName("0.0.0.0"),
                x509.IPAddress(x509.IPAddress(ipaddress.ip_address("127.0.0.1"))),
                x509.IPAddress(x509.IPAddress(ipaddress.ip_address("0.0.0.0"))),
            ]),
            critical=False,
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())

        # Save private key
        logger.info(f"   💾 Saving private key to {key_path}")
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Save certificate
        logger.info(f"   💾 Saving certificate to {cert_path}")
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Set proper permissions (more secure on Unix systems)
        try:
            os.chmod(key_path, 0o600)  # Private key should be readable only by owner
            os.chmod(cert_path, 0o644)  # Certificate can be world readable
        except OSError:
            logger.warning("   ⚠️  Could not set file permissions (this is normal on Windows)")

        logger.info("   ✅ SSL certificates generated successfully!")
        logger.info(f"   📄 Certificate file: {cert_path}")
        logger.info(f"   🔑 Private key file: {key_path}")
        logger.info(f"   📅 Valid until: {(datetime.utcnow() + timedelta(days=valid_days)).strftime('%Y-%m-%d')}")

        return True

    except Exception as e:
        logger.error(f"   ❌ Failed to generate SSL certificates: {e}")
        return False

def check_existing_certificates():
    """Check if SSL certificates already exist and are valid"""

    cert_path = os.environ.get('SSL_CERT_PATH', 'certs/cert.pem')
    key_path = os.environ.get('SSL_KEY_PATH', 'certs/key.pem')

    logger.info("🔍 Checking existing SSL certificates...")

    # Check if files exist
    cert_exists = os.path.exists(cert_path)
    key_exists = os.path.exists(key_path)

    if not cert_exists or not key_exists:
        logger.info("   📄 Certificate files not found")
        return False

    logger.info(f"   ✅ Certificate file found: {cert_path}")
    logger.info(f"   ✅ Private key file found: {key_path}")

    # Try to load and validate the certificate
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import serialization

        # Load certificate
        with open(cert_path, "rb") as f:
            cert_data = f.read()

        certificate = x509.load_pem_x509_certificate(cert_data)

        # Load private key
        with open(key_path, "rb") as f:
            key_data = f.read()

        private_key = serialization.load_pem_private_key(key_data, password=None)

        # Check if certificate is still valid
        now = datetime.utcnow()
        if certificate.not_valid_after < now:
            logger.warning("   ⚠️  Certificate has expired!")
            return False

        if certificate.not_valid_before > now:
            logger.warning("   ⚠️  Certificate is not yet valid!")
            return False

        logger.info("   ✅ Certificate is valid")
        logger.info(f"   📅 Valid from: {certificate.not_valid_before.strftime('%Y-%m-%d')}")
        logger.info(f"   📅 Valid until: {certificate.not_valid_after.strftime('%Y-%m-%d')}")

        # Check if certificate matches private key
        cert_public_key = certificate.public_key()
        key_public_key = private_key.public_key()

        if cert_public_key.public_numbers() == key_public_key.public_numbers():
            logger.info("   ✅ Certificate matches private key")
        else:
            logger.error("   ❌ Certificate does not match private key!")
            return False

        logger.info("   ✅ SSL certificates are valid and ready to use")
        return True

    except Exception as e:
        logger.error(f"   ❌ Error validating SSL certificates: {e}")
        return False

def main():
    """Main function to generate or validate SSL certificates"""

    print("🔐 ValidoAI SSL Certificate Management")
    print("=" * 50)

    # Check if certificates already exist and are valid
    if check_existing_certificates():
        print("\n🎉 SSL certificates are already valid!")
        print("   You can skip certificate generation.")
        print("\nTo regenerate certificates, delete the existing files and run this script again.")
        return True

    print("\n📄 SSL certificates not found or invalid.")
    print("   Generating new certificates...\n")

    # Generate new certificates
    success = generate_ssl_certificates()

    if success:
        print("\n🎉 SSL certificates generated successfully!")
        print("\nNext steps:")
        print("1. Restart your application to use the new certificates")
        print("2. Access your application via HTTPS: https://localhost:5001")
        print("3. Accept the self-signed certificate in your browser")
        print("\nNote: These are development certificates and should not be used in production!")
        return True
    else:
        print("\n❌ Failed to generate SSL certificates!")
        print("Please check the error messages above and try again.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
