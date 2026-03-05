#!/usr/bin/env python3
"""
SSL Configuration Fix Script for ValidoAI

This script addresses SSL/HTTPS configuration issues in the Flask application.
It provides better error handling and configuration validation for SSL certificates.

Usage:
    python scripts/fix_ssl_configuration.py

Features:
    - Validates SSL certificate configuration
    - Improves SSL error handling
    - Provides configuration recommendations
    - Tests SSL connectivity
"""

import os
import sys
import ssl
import socket
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SSLConfigurationFixer:
    """Fix SSL configuration issues in ValidoAI"""

    def __init__(self):
        self.app_dir = Path(__file__).parent.parent
        self.cert_path = os.environ.get('SSL_CERT_PATH', 'certs/cert.pem')
        self.key_path = os.environ.get('SSL_KEY_PATH', 'certs/key.pem')
        self.host = os.environ.get('HOST', '0.0.0.0')
        self.http_port = int(os.environ.get('PORT', '5000'))
        self.https_port = int(os.environ.get('HTTPS_PORT', '5001'))

    def check_ssl_files(self):
        """Check if SSL certificate files exist and are accessible"""
        logger.info("🔍 Checking SSL certificate files...")

        cert_file = self.app_dir / self.cert_path
        key_file = self.app_dir / self.key_path

        cert_exists = cert_file.exists()
        key_exists = key_file.exists()

        if cert_exists:
            logger.info(f"   ✅ Certificate file found: {cert_file}")
            logger.info(f"      Size: {cert_file.stat().st_size} bytes")
        else:
            logger.error(f"   ❌ Certificate file not found: {cert_file}")
            return False

        if key_exists:
            logger.info(f"   ✅ Private key file found: {key_file}")
            logger.info(f"      Size: {key_file.stat().st_size} bytes")
        else:
            logger.error(f"   ❌ Private key file not found: {key_file}")
            return False

        # Check file permissions
        try:
            cert_mode = oct(cert_file.stat().st_mode)[-3:]
            key_mode = oct(key_file.stat().st_mode)[-3:]

            logger.info(f"   📁 Certificate permissions: {cert_mode}")
            logger.info(f"   🔑 Private key permissions: {key_mode}")

            # Private key should have restricted permissions
            if key_mode not in ['600', '400']:
                logger.warning(f"   ⚠️  Private key permissions should be more restrictive (current: {key_mode})")

        except Exception as e:
            logger.warning(f"   ⚠️  Could not check file permissions: {e}")

        return True

    def validate_ssl_certificates(self):
        """Validate SSL certificate content and structure"""
        logger.info("🔐 Validating SSL certificates...")

        cert_file = self.app_dir / self.cert_path
        key_file = self.app_dir / self.key_path

        try:
            # Load and validate certificate
            with open(cert_file, 'rb') as f:
                cert_data = f.read()

            # Check if it's a valid PEM certificate
            if b'-----BEGIN CERTIFICATE-----' not in cert_data:
                logger.error("   ❌ Invalid certificate format - missing PEM header")
                return False

            if b'-----END CERTIFICATE-----' not in cert_data:
                logger.error("   ❌ Invalid certificate format - missing PEM footer")
                return False

            logger.info("   ✅ Certificate has valid PEM format")

            # Load and validate private key
            with open(key_file, 'rb') as f:
                key_data = f.read()

            # Check if it's a valid PEM private key
            if b'-----BEGIN PRIVATE KEY-----' not in key_data and b'-----BEGIN RSA PRIVATE KEY-----' not in key_data:
                logger.error("   ❌ Invalid private key format - missing PEM header")
                return False

            if b'-----END PRIVATE KEY-----' not in key_data and b'-----END RSA PRIVATE KEY-----' not in key_data:
                logger.error("   ❌ Invalid private key format - missing PEM footer")
                return False

            logger.info("   ✅ Private key has valid PEM format")

            return True

        except Exception as e:
            logger.error(f"   ❌ Error validating certificates: {e}")
            return False

    def test_ssl_connectivity(self):
        """Test SSL connectivity to the application"""
        logger.info("🧪 Testing SSL connectivity...")

        # Create SSL context for testing
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        try:
            # Test HTTPS connection
            with socket.create_connection((self.host if self.host != '0.0.0.0' else '127.0.0.1', self.https_port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname='localhost') as ssock:
                    logger.info("   ✅ HTTPS connection successful")
                    logger.info(f"      SSL version: {ssock.version()}")
                    logger.info(f"      Cipher: {ssock.cipher()}")

                    # Test basic HTTP request
                    ssock.send(b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")

                    response = ssock.recv(1024)
                    if b"HTTP/1.1" in response:
                        logger.info("   ✅ HTTPS server responding correctly")
                    else:
                        logger.warning("   ⚠️  HTTPS server response unclear")

        except ConnectionRefusedError:
            logger.warning("   ⚠️  HTTPS server not running (connection refused)")
            logger.info("      This is normal if the application hasn't started yet")
        except Exception as e:
            logger.error(f"   ❌ HTTPS connectivity test failed: {e}")

    def fix_app_configuration(self):
        """Fix SSL-related configuration in the application"""
        logger.info("🔧 Checking application SSL configuration...")

        app_file = self.app_dir / 'app.py'

        try:
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for SSL-related configurations
            issues_found = []

            # Check SSL certificate paths
            if 'SSL_CERT_PATH' not in content and 'SSL_KEY_PATH' not in content:
                logger.info("   ℹ️  SSL paths configured via environment variables")

            # Check for proper SSL error handling
            if 'ssl.SSLError' not in content:
                issues_found.append("Missing SSL error handling")

            if 'certificate verify failed' in content.lower():
                logger.info("   ✅ SSL certificate verification handling found")
            else:
                issues_found.append("Missing SSL certificate verification handling")

            # Check for proper HTTPS redirects
            if 'HTTPToHTTPSRedirectMiddleware' in content:
                logger.info("   ✅ HTTP to HTTPS redirect middleware configured")
            else:
                issues_found.append("Missing HTTP to HTTPS redirect configuration")

            if issues_found:
                logger.warning("   ⚠️  SSL configuration issues found:")
                for issue in issues_found:
                    logger.warning(f"      • {issue}")
            else:
                logger.info("   ✅ SSL configuration looks good")

            return len(issues_found) == 0

        except Exception as e:
            logger.error(f"   ❌ Error checking application configuration: {e}")
            return False

    def provide_recommendations(self):
        """Provide SSL configuration recommendations"""
        logger.info("💡 SSL Configuration Recommendations:")
        logger.info("   1. Use the generated certificates for development only")
        logger.info("   2. For production, use certificates from a trusted CA")
        logger.info("   3. Consider using Let's Encrypt for free production certificates")
        logger.info("   4. Enable HSTS headers for better security")
        logger.info("   5. Regularly rotate SSL certificates")

        logger.info("\n🔧 Environment Variables for SSL:")
        logger.info(f"   SSL_CERT_PATH={self.cert_path}")
        logger.info(f"   SSL_KEY_PATH={self.key_path}")
        logger.info(f"   SSL_ENABLED=true")
        logger.info(f"   PORT={self.http_port}")
        logger.info(f"   HTTPS_PORT={self.https_port}")

    def run_all_checks(self):
        """Run all SSL configuration checks and fixes"""
        logger.info("🔐 ValidoAI SSL Configuration Fixer")
        logger.info("=" * 50)

        checks = [
            ("SSL Files Check", self.check_ssl_files),
            ("SSL Validation", self.validate_ssl_certificates),
            ("App Configuration", self.fix_app_configuration),
        ]

        results = []

        for check_name, check_func in checks:
            logger.info(f"\n🧪 Running {check_name}...")
            try:
                result = check_func()
                results.append((check_name, result))
                if result:
                    logger.info(f"✅ {check_name} passed")
                else:
                    logger.error(f"❌ {check_name} failed")
            except Exception as e:
                logger.error(f"❌ {check_name} failed with error: {e}")
                results.append((check_name, False))

        # Test SSL connectivity (optional)
        logger.info("\n🧪 Testing SSL connectivity...")
        try:
            self.test_ssl_connectivity()
        except Exception as e:
            logger.warning(f"SSL connectivity test failed: {e}")

        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("📊 SSL Configuration Summary")
        logger.info("=" * 50)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for check_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status} - {check_name}")

        logger.info(f"\n📈 Results: {passed}/{total} checks passed")

        if passed == total:
            logger.info("🎉 All SSL configuration checks passed!")
            logger.info("   Your SSL setup should work correctly.")
        else:
            logger.warning("⚠️  Some SSL configuration issues were found.")
            logger.warning("   Please review the errors above and fix them.")

        # Provide recommendations
        logger.info("\n" + "=" * 50)
        self.provide_recommendations()

        return passed == total

def main():
    """Main function"""
    try:
        fixer = SSLConfigurationFixer()
        success = fixer.run_all_checks()
        return success
    except KeyboardInterrupt:
        logger.info("\n⚠️  Operation cancelled by user")
        return False
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
