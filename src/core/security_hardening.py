"""
Security Hardening Module
========================

Enterprise-grade security enhancements for ValidoAI.
Provides secure secret key generation, security headers, and hardening features.
"""

import os
import secrets
import hashlib
import sys
from typing import Optional, Dict, Any
from pathlib import Path

# Import standard logging without conflict
import logging as std_logging
logger = std_logging.getLogger(__name__)

class SecurityHardener:
    """Security hardening utilities"""

    @staticmethod
    def generate_secure_secret_key(length: int = 64) -> str:
        """Generate a cryptographically secure secret key"""
        return secrets.token_hex(length // 2)  # token_hex generates 2 chars per byte

    @staticmethod
    def validate_secret_key(secret_key: str) -> bool:
        """Validate secret key strength"""
        if not secret_key:
            return False

        # Check length (minimum 32 characters for security)
        if len(secret_key) < 32:
            return False

        # Check for entropy (should not be all same character)
        if len(set(secret_key)) < len(secret_key) * 0.1:
            return False

        # Check for common weak patterns
        weak_patterns = [
            'secret', 'key', 'password', '123', 'abc',
            'dev', 'test', 'default', 'change'
        ]

        secret_lower = secret_key.lower()
        for pattern in weak_patterns:
            if pattern in secret_lower:
                return False

        return True

    @staticmethod
    def generate_env_file(env_file: str = ".env.secure") -> None:
        """Generate a secure .env file with strong secrets"""
        env_path = Path(env_file)

        if env_path.exists():
            logger.warning(f"Environment file {env_file} already exists. Skipping generation.")
            return

        # Generate secure secrets
        flask_secret = SecurityHardener.generate_secure_secret_key(64)
        jwt_secret = SecurityHardener.generate_secure_secret_key(64)
        encryption_key = SecurityHardener.generate_secure_secret_key(32)

        # Generate random database credentials
        db_user = f"valido_{secrets.token_hex(4)}"
        db_password = SecurityHardener.generate_secure_secret_key(32)

        # Create secure environment file
        env_content = f"""# ValidoAI Secure Environment Configuration
# Generated on {os.environ.get('COMPUTERNAME', 'Unknown')} at {os.environ.get('USERNAME', 'Unknown')}
# WARNING: Keep this file secure and never commit to version control

# =============================================================================
# SECURITY CONFIGURATION (CRITICAL)
# =============================================================================
SECRET_KEY={flask_secret}
JWT_SECRET={jwt_secret}
ENCRYPTION_KEY={encryption_key}

# Database Security
DB_USER={db_user}
DB_PASSWORD={db_password}

# API Keys (Add your actual keys here)
OPENAI_API_KEY=your-openai-api-key-here
COHERE_API_KEY=your-cohere-api-key-here

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
FLASK_APP=app.py
FLASK_ENV=production
DEBUG=False

# Server Configuration
HOST=0.0.0.0
HTTP_PORT=5000
HTTPS_PORT=5001

# Database Configuration
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_valido_online
POSTGRES_USER={db_user}
POSTGRES_PASSWORD={db_password}

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD={SecurityHardener.generate_secure_secret_key(32)}

# =============================================================================
# SECURITY HEADERS
# =============================================================================
# Content Security Policy
CSP_DEFAULT_SRC=self
CSP_SCRIPT_SRC=self 'unsafe-inline' 'unsafe-eval'
CSP_STYLE_SRC=self 'unsafe-inline'

# Security Headers
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=True
HSTS_PRELOAD=True

# =============================================================================
# MONITORING & LOGGING
# =============================================================================
LOG_LEVEL=INFO
ENABLE_ACCESS_LOG=True
ENABLE_ERROR_LOG=True

# Sentry Configuration (for error tracking)
SENTRY_DSN=your-sentry-dsn-here

# =============================================================================
# FEATURE FLAGS
# =============================================================================
ENABLE_AI_FEATURES=True
ENABLE_GPU_ACCELERATION=True
ENABLE_CACHING=True
ENABLE_RATE_LIMITING=True
ENABLE_HTTPS=True
"""

        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)

        logger.info(f"✅ Secure environment file generated: {env_file}")
        logger.info("⚠️  WARNING: Move this file to .env and secure it!")
        logger.info("⚠️  Never commit .env files to version control!")

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get comprehensive security headers"""
        return {
            # Content Security Policy
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; media-src 'self'; object-src 'none'; child-src 'self'; worker-src 'self'; frame-ancestors 'none'; form-action 'self'; upgrade-insecure-requests; block-all-mixed-content",

            # Security Headers
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',

            # Additional Security
            'X-Permitted-Cross-Domain-Policies': 'none',
            'Expect-CT': 'max-age=86400, enforce',
        }

    @staticmethod
    def validate_environment_security() -> Dict[str, Any]:
        """Validate environment security settings"""
        issues = []
        warnings = []
        recommendations = []

        # Check secret key
        secret_key = os.getenv('SECRET_KEY', '')
        if not secret_key:
            issues.append("SECRET_KEY not set")
        elif not SecurityHardener.validate_secret_key(secret_key):
            issues.append("SECRET_KEY is weak or contains common patterns")

        # Check debug mode
        debug_mode = os.getenv('FLASK_ENV', '').lower() == 'development' or os.getenv('DEBUG', '').lower() == 'true'
        if debug_mode:
            warnings.append("Application is running in debug mode")

        # Check HTTPS
        if not os.getenv('ENABLE_HTTPS', '').lower() == 'true':
            recommendations.append("Consider enabling HTTPS for production")

        # Check database security
        if os.getenv('DATABASE_TYPE', '').lower() == 'sqlite':
            warnings.append("Using SQLite in production - consider PostgreSQL/MySQL")

        # Check if sensitive data is in environment
        sensitive_vars = ['API_KEY', 'SECRET', 'PASSWORD', 'TOKEN']
        for key, value in os.environ.items():
            if any(sensitive in key.upper() for sensitive in sensitive_vars):
                if len(value) < 16:
                    warnings.append(f"Weak {key} detected")

        return {
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'overall_security_score': 'high' if not issues else ('medium' if not warnings else 'low')
        }

    @staticmethod
    def generate_security_report() -> str:
        """Generate comprehensive security report"""
        report = []
        report.append("=" * 60)
        report.append("VALIDOAI SECURITY HARDENING REPORT")
        report.append("=" * 60)

        # Environment validation
        env_security = SecurityHardener.validate_environment_security()

        report.append(f"\\n🔐 Overall Security Score: {env_security['overall_security_score'].upper()}")

        if env_security['issues']:
            report.append("\\n❌ CRITICAL ISSUES:")
            for issue in env_security['issues']:
                report.append(f"  - {issue}")

        if env_security['warnings']:
            report.append("\\n⚠️  WARNINGS:")
            for warning in env_security['warnings']:
                report.append(f"  - {warning}")

        if env_security['recommendations']:
            report.append("\\n💡 RECOMMENDATIONS:")
            for rec in env_security['recommendations']:
                report.append(f"  - {rec}")

        # Generate secure configuration if issues found
        if env_security['issues']:
            report.append("\\n🔧 GENERATING SECURE CONFIGURATION...")
            SecurityHardener.generate_env_file()

        report.append("\\n" + "=" * 60)
        return "\\n".join(report)

def main():
    """Main function for security hardening"""
    print(SecurityHardener.generate_security_report())

if __name__ == "__main__":
    main()
