#!/usr/bin/env python3
"""
Validate Components - Check if components work with theme system
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def validate_component(component_path):
    """Validate a single component file"""
    if not component_path.exists():
        return False, "File not found"

    try:
        content = component_path.read_text(encoding='utf-8')

        issues = []

        # Check for deprecated @apply directives
        if "@apply" in content:
            issues.append("Contains deprecated @apply directives")

        # Check for old theme classes
        old_classes = ["bg-theme", "text-theme", "border-theme"]
        for old_class in old_classes:
            if old_class in content:
                issues.append(f"Contains old theme class: {old_class}")

        # Check for missing Valido theme variables
        if "--valido-" in content:
            # Good, uses Valido theme variables
            pass
        elif not any(x in content for x in ["var(--", "@apply", "bg-", "text-"]):
            issues.append("May not use theme variables properly")

        return len(issues) == 0, issues

    except Exception as e:
        return False, f"Error reading file: {e}"

def validate_all_components():
    """Validate all component files"""
    components_dir = project_root / "templates" / "components"

    if not components_dir.exists():
        print("❌ Components directory not found")
        return 0, 0

    component_files = list(components_dir.glob("*.html"))
    passed = 0
    failed = 0

    print(f"🔍 Validating {len(component_files)} component files...")

    for component_file in component_files:
        is_valid, issues = validate_component(component_file)

        if is_valid:
            print(f"✅ {component_file.name}")
            passed += 1
        else:
            print(f"❌ {component_file.name}")
            for issue in issues:
                print(f"   - {issue}")
            failed += 1

    return passed, failed

if __name__ == "__main__":
    passed, failed = validate_all_components()
    print(f"\n📊 Validation Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All components validated successfully!")
    else:
        print("⚠️ Some components need attention.")
