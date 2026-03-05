#!/usr/bin/env python3
"""
Test Asset Loading - Verify CSS, JS, fonts, and images load properly
"""

import os
import sys
import requests
import json
from pathlib import Path
from urllib.parse import urljoin

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_static_files():
    """Test static file structure and accessibility"""
    static_dir = project_root / "static"

    print("🔍 Checking static file structure...")

    # Required directories
    required_dirs = [
        "css",
        "js",
        "images",
        "fonts",
        "themes",
        "favicons",
        "icons"
    ]

    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = static_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            file_count = len(list(dir_path.rglob("*")))
            print(f"✅ {dir_name}/ - {file_count} files")
        else:
            print(f"❌ {dir_name}/ - NOT FOUND")
            missing_dirs.append(dir_name)

    return len(missing_dirs) == 0

def test_css_files():
    """Test CSS file loading and syntax"""
    css_dir = project_root / "static" / "css"

    print("\n🎨 Checking CSS files...")

    css_files = [
        "main.css",
        "modal.css",
        "table.css",
        "form.css",
        "toast.css",
        "captcha.css"
    ]

    all_valid = True
    for css_file in css_files:
        file_path = css_dir / css_file
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                size = len(content)
                print(f"✅ {css_file} - {size:,} bytes")

                # Basic syntax check
                if content.count('{') != content.count('}'):
                    print(f"   ⚠️  Warning: Unmatched braces in {css_file}")
                    all_valid = False

            except Exception as e:
                print(f"❌ {css_file} - Error reading: {e}")
                all_valid = False
        else:
            print(f"❌ {css_file} - NOT FOUND")
            all_valid = False

    return all_valid

def test_js_files():
    """Test JavaScript file loading and syntax"""
    js_dir = project_root / "static" / "js"

    print("\n📜 Checking JavaScript files...")

    js_files = [
        "main.js",
        "alpine.js",
        "htmx.js",
        "theme-manager.js",
        "form-validation.js"
    ]

    all_valid = True
    for js_file in js_files:
        file_path = js_dir / js_file
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                size = len(content)
                print(f"✅ {js_file} - {size:,} bytes")

                # Basic syntax checks
                if content.count('{') != content.count('}'):
                    print(f"   ⚠️  Warning: Unmatched braces in {js_file}")
                    all_valid = False

                if content.count('(') != content.count(')'):
                    print(f"   ⚠️  Warning: Unmatched parentheses in {js_file}")
                    all_valid = False

            except Exception as e:
                print(f"❌ {js_file} - Error reading: {e}")
                all_valid = False
        else:
            print(f"⚠️  {js_file} - NOT FOUND (may be generated)")

    return all_valid

def test_theme_files():
    """Test theme files loading"""
    themes_dir = project_root / "static" / "themes"

    print("\n🎨 Checking theme files...")

    theme_files = [
        "valido-white.css",
        "valido-dark.css",
        "valido-high-contrast.css",
        "valido-minimal.css"
    ]

    all_valid = True
    for theme_file in theme_files:
        file_path = themes_dir / theme_file
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                size = len(content)
                print(f"✅ {theme_file} - {size:,} bytes")

                # Check for required CSS custom properties
                required_props = ["--valido-primary:", "--valido-bg-primary:"]
                for prop in required_props:
                    if prop not in content:
                        print(f"   ⚠️  Warning: Missing {prop} in {theme_file}")
                        all_valid = False

            except Exception as e:
                print(f"❌ {theme_file} - Error reading: {e}")
                all_valid = False
        else:
            print(f"❌ {theme_file} - NOT FOUND")
            all_valid = False

    return all_valid

def test_font_files():
    """Test font file accessibility"""
    fonts_dir = project_root / "static" / "fonts"

    print("\n🔤 Checking font files...")

    if not fonts_dir.exists():
        print("⚠️  fonts/ directory not found")
        return True  # Not critical

    font_files = list(fonts_dir.rglob("*.woff2")) + list(fonts_dir.rglob("*.woff")) + list(fonts_dir.rglob("*.ttf"))

    if not font_files:
        print("⚠️  No font files found")
        return True  # Not critical

    all_valid = True
    for font_file in font_files[:5]:  # Check first 5 files
        try:
            size = font_file.stat().st_size
            print(f"✅ {font_file.name} - {size:,} bytes")
        except Exception as e:
            print(f"❌ {font_file.name} - Error: {e}")
            all_valid = False

    if len(font_files) > 5:
        print(f"   ... and {len(font_files) - 5} more font files")

    return all_valid

def test_image_files():
    """Test image file accessibility"""
    images_dir = project_root / "static" / "images"

    print("\n🖼️ Checking image files...")

    if not images_dir.exists():
        print("⚠️  images/ directory not found")
        return True  # Not critical

    image_files = list(images_dir.rglob("*.png")) + list(images_dir.rglob("*.jpg")) + list(images_dir.rglob("*.jpeg")) + list(images_dir.rglob("*.svg"))

    if not image_files:
        print("⚠️  No image files found")
        return True  # Not critical

    all_valid = True
    for image_file in image_files[:5]:  # Check first 5 files
        try:
            size = image_file.stat().st_size
            print(f"✅ {image_file.name} - {size:,} bytes")
        except Exception as e:
            print(f"❌ {image_file.name} - Error: {e}")
            all_valid = False

    if len(image_files) > 5:
        print(f"   ... and {len(image_files) - 5} more image files")

    return all_valid

def test_favicon_files():
    """Test favicon accessibility"""
    favicons_dir = project_root / "static" / "favicons"

    print("\n⭐ Checking favicon files...")

    if not favicons_dir.exists():
        print("⚠️  favicons/ directory not found")
        return True  # Not critical

    favicon_files = list(favicons_dir.rglob("*"))

    if not favicon_files:
        print("⚠️  No favicon files found")
        return True  # Not critical

    all_valid = True
    for favicon_file in favicon_files[:5]:  # Check first 5 files
        try:
            size = favicon_file.stat().st_size
            print(f"✅ {favicon_file.name} - {size:,} bytes")
        except Exception as e:
            print(f"❌ {favicon_file.name} - Error: {e}")
            all_valid = False

    if len(favicon_files) > 5:
        print(f"   ... and {len(favicon_files) - 5} more favicon files")

    return all_valid

def test_asset_references():
    """Test asset references in templates"""
    templates_dir = project_root / "templates"

    print("\n📄 Checking asset references in templates...")

    template_files = [
        "base.html",
        "companies/index.html",
        "dashboard/index.html"
    ]

    all_valid = True
    for template_file in template_files:
        file_path = templates_dir / template_file
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')

                # Check for asset references
                asset_patterns = [
                    "static/css/",
                    "static/js/",
                    "static/themes/",
                    "static/images/",
                    "static/fonts/"
                ]

                for pattern in asset_patterns:
                    if pattern in content:
                        print(f"✅ {template_file} - Contains {pattern} references")

                # Check for broken references
                if "static/nonexistent" in content:
                    print(f"⚠️  {template_file} - Contains potentially broken asset references")
                    all_valid = False

            except Exception as e:
                print(f"❌ {template_file} - Error reading: {e}")
                all_valid = False
        else:
            print(f"⚠️  {template_file} - NOT FOUND")

    return all_valid

def test_asset_manager():
    """Test asset manager configuration"""
    asset_manager = project_root / "src" / "assets" / "asset_manager.py"

    print("\n⚙️ Checking asset manager configuration...")

    if not asset_manager.exists():
        print("❌ asset_manager.py not found")
        return False

    try:
        content = asset_manager.read_text(encoding='utf-8')

        # Check for required assets
        required_assets = [
            "tailwind_css",
            "main_css",
            "alpine_js",
            "htmx_js",
            "valido_white_css",
            "valido_dark_css"
        ]

        missing_assets = []
        for asset in required_assets:
            if asset not in content:
                missing_assets.append(asset)

        if missing_assets:
            print(f"❌ Missing assets in asset manager: {missing_assets}")
            return False
        else:
            print("✅ All required assets configured in asset manager")
            return True

    except Exception as e:
        print(f"❌ Error reading asset manager: {e}")
        return False

def main():
    """Run all asset loading tests"""
    print("🔍 Asset Loading Test Suite")
    print("=" * 50)

    tests = [
        ("Static File Structure", test_static_files),
        ("CSS Files", test_css_files),
        ("JavaScript Files", test_js_files),
        ("Theme Files", test_theme_files),
        ("Font Files", test_font_files),
        ("Image Files", test_image_files),
        ("Favicon Files", test_favicon_files),
        ("Asset References", test_asset_references),
        ("Asset Manager", test_asset_manager)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 ASSET LOADING TEST SUMMARY")
    print("=" * 50)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n📈 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All asset loading tests passed! Static assets are properly configured.")
        return 0
    else:
        print("⚠️ Some asset loading tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
