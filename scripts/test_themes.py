#!/usr/bin/env python3
"""
Test Valido Themes - Verify theme loading and functionality
"""

import os
import sys
import requests
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_theme_files():
    """Test if theme files exist and are accessible"""
    themes_dir = project_root / "static" / "themes"

    required_themes = [
        "valido-white.css",
        "valido-dark.css",
        "valido-high-contrast.css",
        "valido-minimal.css"
    ]

    print("🔍 Checking theme files...")
    all_exist = True

    for theme_file in required_themes:
        theme_path = themes_dir / theme_file
        if theme_path.exists():
            size = theme_path.stat().st_size
            print(f"✅ {theme_file} - {size:,} bytes")
        else:
            print(f"❌ {theme_file} - NOT FOUND")
            all_exist = False

    return all_exist

def test_theme_css_content():
    """Test theme CSS content for basic structure"""
    themes_dir = project_root / "static" / "themes"

    print("\n🎨 Checking theme CSS content...")
    all_valid = True

    for theme_file in themes_dir.glob("valido-*.css"):
        try:
            content = theme_file.read_text(encoding='utf-8')

            # Check for required CSS custom properties
            required_props = [
                "--valido-primary:",
                "--valido-bg-primary:",
                "--valido-text-primary:"
            ]

            missing_props = []
            for prop in required_props:
                if prop not in content:
                    missing_props.append(prop)

            if missing_props:
                print(f"❌ {theme_file.name} - Missing properties: {missing_props}")
                all_valid = False
            else:
                print(f"✅ {theme_file.name} - Valid CSS structure")

        except Exception as e:
            print(f"❌ {theme_file.name} - Error reading file: {e}")
            all_valid = False

    return all_valid

def test_base_template():
    """Test if base template includes theme support"""
    base_template = project_root / "templates" / "base.html"

    print("\n📄 Checking base template...")
    if not base_template.exists():
        print("❌ base.html not found")
        return False

    try:
        content = base_template.read_text(encoding='utf-8')

        required_elements = [
            "valido-white.css",
            "valido-dark.css",
            "ValidoThemeManager",
            "theme-valido-white",
            "theme-valido-dark"
        ]

        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)

        if missing_elements:
            print(f"❌ base.html missing: {missing_elements}")
            return False
        else:
            print("✅ base.html includes all theme support")
            return True

    except Exception as e:
        print(f"❌ Error reading base.html: {e}")
        return False

def test_asset_manager():
    """Test if asset manager includes new themes"""
    asset_manager = project_root / "src" / "assets" / "asset_manager.py"

    print("\n⚙️ Checking asset manager...")
    if not asset_manager.exists():
        print("❌ asset_manager.py not found")
        return False

    try:
        content = asset_manager.read_text(encoding='utf-8')

        required_themes = [
            "valido_white_css",
            "valido_dark_css",
            "valido_high_contrast_css",
            "valido_minimal_css"
        ]

        missing_themes = []
        for theme in required_themes:
            if theme not in content:
                missing_themes.append(theme)

        if missing_themes:
            print(f"❌ asset_manager.py missing themes: {missing_themes}")
            return False
        else:
            print("✅ asset_manager.py includes all Valido themes")
            return True

    except Exception as e:
        print(f"❌ Error reading asset_manager.py: {e}")
        return False

def main():
    """Run all theme tests"""
    print("🚀 Valido Theme System Test Suite")
    print("=" * 50)

    tests = [
        ("Theme Files", test_theme_files),
        ("Theme CSS Content", test_theme_css_content),
        ("Base Template", test_base_template),
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
    print("📊 TEST SUMMARY")
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
        print("🎉 All theme tests passed! Valido theme system is ready.")
        return 0
    else:
        print("⚠️ Some theme tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
