#!/usr/bin/env python3
"""
Fix Component Themes - Update components to work with Valido theme system
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def fix_datatable_component():
    """Fix datatable component theme classes"""
    datatable_path = project_root / "templates" / "components" / "datatable.html"

    if not datatable_path.exists():
        print("❌ datatable.html not found")
        return False

    content = datatable_path.read_text(encoding='utf-8')

    # Fix @apply directives
    fixes = [
        ("@apply space-y-4;", "gap: 1rem;"),
        ("@apply bg-white p-4 rounded-lg border border-gray-200 shadow-sm;", """
            background-color: var(--valido-bg-primary, #ffffff);
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid var(--valido-border, #e5e7eb);
            box-shadow: var(--valido-shadow-sm, 0 1px 2px 0 rgba(0, 0, 0, 0.05));
        """),
        ("@apply w-full;", "width: 100%;"),
        ("@apply px-4 py-3 text-sm border-b border-gray-200;", """
            padding: 0.75rem 1rem;
            font-size: 0.875rem;
            border-bottom: 1px solid var(--valido-border, #e5e7eb);
        """),
    ]

    for old, new in fixes:
        content = content.replace(old, new)

    try:
        datatable_path.write_text(content, encoding='utf-8')
        print("✅ datatable.html updated")
        return True
    except Exception as e:
        print(f"❌ Error updating datatable.html: {e}")
        return False

def fix_other_components():
    """Fix other components with theme issues"""
    components_dir = project_root / "templates" / "components"
    components_to_fix = [
        "cards.html",
        "metric_card.html",
        "quick_action_card.html",
        "transaction_card.html",
        "notification_card.html"
    ]

    fixed = 0
    for component_file in components_to_fix:
        file_path = components_dir / component_file
        if not file_path.exists():
            continue

        try:
            content = file_path.read_text(encoding='utf-8')

            # Replace common theme classes
            replacements = [
                ("@apply bg-white", "background-color: var(--valido-bg-primary, #ffffff)"),
                ("@apply border-gray-200", "border: 1px solid var(--valido-border, #e5e7eb)"),
                ("@apply shadow-sm", "box-shadow: var(--valido-shadow-sm, 0 1px 2px 0 rgba(0, 0, 0, 0.05))"),
                ("@apply shadow-lg", "box-shadow: var(--valido-shadow-lg, 0 10px 15px -3px rgba(0, 0, 0, 0.1))"),
                ("@apply text-gray-900", "color: var(--valido-text-primary, #1e293b)"),
                ("@apply text-gray-600", "color: var(--valido-text-secondary, #64748b)"),
                ("@apply bg-gray-50", "background-color: var(--valido-bg-secondary, #f8fafc)"),
                ("@apply border-gray-300", "border-color: var(--valido-border, #e5e7eb)"),
            ]

            for old, new in replacements:
                content = content.replace(old, new)

            file_path.write_text(content, encoding='utf-8')
            print(f"✅ {component_file} updated")
            fixed += 1

        except Exception as e:
            print(f"❌ Error updating {component_file}: {e}")

    return fixed

def create_component_validation():
    """Create a component validation system"""
    validation_script = project_root / "scripts" / "validate_components.py"

    validation_code = '''#!/usr/bin/env python3
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
'''

    try:
        validation_script.write_text(validation_code, encoding='utf-8')
        print("✅ Component validation script created")
        return True
    except Exception as e:
        print(f"❌ Error creating validation script: {e}")
        return False

def main():
    """Run all component fixes"""
    print("🔧 Component Theme Fix System")
    print("=" * 50)

    tasks = [
        ("Fix datatable component", fix_datatable_component),
        ("Fix other components", fix_other_components),
        ("Create component validation", create_component_validation),
    ]

    results = []
    for task_name, task_func in tasks:
        print(f"\n🛠️ Running {task_name}...")
        try:
            result = task_func()
            results.append((task_name, result))
        except Exception as e:
            print(f"❌ {task_name} failed with error: {e}")
            results.append((task_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 COMPONENT FIX SUMMARY")
    print("=" * 50)

    passed = 0
    failed = 0

    for task_name, result in results:
        status = "✅ COMPLETED" if result else "❌ FAILED"
        print(f"{status} - {task_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n📈 Results: {passed} completed, {failed} failed")

    if failed == 0:
        print("🎉 All component fixes completed successfully!")
        return 0
    else:
        print("⚠️ Some component fixes failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
