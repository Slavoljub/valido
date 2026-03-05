#!/usr/bin/env python3
"""
SSL Certificate Permissions Fix Script for ValidoAI

This script fixes SSL certificate file permissions to ensure security best practices.
Private keys should have restrictive permissions (600) while certificates can be world-readable (644).

Usage:
    python scripts/fix_ssl_permissions.py

Requirements:
    - Python 3.6+
    - Appropriate permissions to modify files
"""

import os
import sys
import stat
from pathlib import Path

def fix_ssl_permissions():
    """Fix SSL certificate file permissions"""

    certs_dir = Path('certs')
    if not certs_dir.exists():
        print("❌ certs directory not found")
        return False

    files_to_check = [
        ('cert.pem', 0o644),      # Certificate: readable by all, writable by owner
        ('key.pem', 0o600),       # Private key: readable/writable by owner only
        ('certificate.pem', 0o644),
        ('private.key', 0o600),
        ('key.rsa', 0o600)
    ]

    success_count = 0
    total_count = 0

    print("🔐 Fixing SSL certificate permissions...")
    print("=" * 50)

    for filename, desired_mode in files_to_check:
        file_path = certs_dir / filename

        if not file_path.exists():
            print(f"⚠️  File not found: {filename}")
            continue

        total_count += 1

        try:
            # Get current permissions
            current_mode = file_path.stat().st_mode
            current_perms = oct(current_mode)[-3:]

            # Set new permissions
            file_path.chmod(desired_mode)
            new_mode = file_path.stat().st_mode
            new_perms = oct(new_mode)[-3:]

            print(f"✅ {filename}")
            print(f"   Changed permissions: {current_perms} → {new_perms}")

            if new_perms == oct(desired_mode)[-3:]:
                success_count += 1
                print("   ✅ Permissions set correctly")
            else:
                print("   ❌ Failed to set correct permissions")
        except PermissionError:
            print(f"❌ {filename}")
            print(f"   Permission denied - run as administrator")
        except Exception as e:
            print(f"❌ {filename}")
            print(f"   Error: {e}")

    print("\n" + "=" * 50)
    print("📊 Permission Fix Summary")
    print("=" * 50)
    print(f"Files processed: {total_count}")
    print(f"Successfully fixed: {success_count}")

    if success_count == total_count and total_count > 0:
        print("🎉 All SSL certificate permissions fixed!")
        print("\nSecurity recommendations:")
        print("• Private keys (key.pem, private.key, key.rsa): 600 (owner read/write only)")
        print("• Certificates (cert.pem, certificate.pem): 644 (world readable)")
        return True
    elif total_count == 0:
        print("⚠️  No SSL certificate files found")
        print("   Run 'python scripts/generate_ssl_certificates.py' first")
        return False
    else:
        print("⚠️  Some permissions could not be fixed")
        print("   You may need to run this script as administrator")
        return False

def verify_permissions():
    """Verify that SSL certificate permissions are correct"""

    certs_dir = Path('certs')
    if not certs_dir.exists():
        print("❌ certs directory not found")
        return False

    print("🔍 Verifying SSL certificate permissions...")
    print("=" * 50)

    expected_permissions = {
        'cert.pem': '644',
        'key.pem': '600',
        'certificate.pem': '644',
        'private.key': '600',
        'key.rsa': '600'
    }

    all_correct = True

    for filename, expected_perms in expected_permissions.items():
        file_path = certs_dir / filename

        if not file_path.exists():
            print(f"⚠️  {filename}: File not found")
            continue

        try:
            current_mode = file_path.stat().st_mode
            current_perms = oct(current_mode)[-3:]

            if current_perms == expected_perms:
                print(f"✅ {filename}: {current_perms} (correct)")
            else:
                print(f"❌ {filename}: {current_perms} (expected: {expected_perms})")
                all_correct = False

        except Exception as e:
            print(f"❌ {filename}: Error checking permissions - {e}")
            all_correct = False

    if all_correct:
        print("🎉 All SSL certificate permissions are correct!")
    else:
        print("⚠️  Some SSL certificate permissions need fixing")

    return all_correct

def main():
    """Main function"""
    print("🔐 ValidoAI SSL Certificate Permissions Manager")
    print("=" * 50)

    # First verify current permissions
    if verify_permissions():
        print("\n✅ All permissions are already correct")
        return True

    print("\n🔧 Fixing permissions...\n")

    # Fix permissions
    success = fix_ssl_permissions()

    if success:
        print("\n✅ SSL certificate permissions have been fixed!")
        print("\nTo verify the fixes, run this script again or check manually:")
        print("   ls -la certs/")
    else:
        print("\n❌ Failed to fix all SSL certificate permissions")
        print("   You may need to run this script as administrator (sudo)")

    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
