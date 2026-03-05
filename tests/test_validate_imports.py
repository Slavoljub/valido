#!/usr/bin/env python3
"""
Import Validation Script
=======================

Validates all module imports in ValidoAI to ensure they work correctly.
Identifies missing dependencies, circular imports, and import errors.
"""

import sys
import os
import importlib
import warnings
from pathlib import Path
from typing import Dict, List, Any, Set

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

def get_all_python_files() -> List[Path]:
    """Get all Python files in the project"""
    python_files = []

    # Skip certain directories
    exclude_dirs = {
        '__pycache__',
        'node_modules',
        'venv',
        'env',
        '.git',
        'htmlcov',
        'reports',
        'data',
        'static',
        'templates',
        'configuration_scripts'
    }

    for path in project_root.rglob('*.py'):
        # Skip excluded directories
        if any(part in exclude_dirs for part in path.parts):
            continue

        python_files.append(path)

    return python_files

def extract_imports_from_file(file_path: Path) -> Dict[str, List[str]]:
    """Extract all imports from a Python file"""
    imports = {
        'standard': [],
        'third_party': [],
        'local': [],
        'conditional': []
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Standard import statements
            if line.startswith('import '):
                module = line.split('import ')[1].split('.')[0].split(' as ')[0].strip()
                if module in sys.stdlib_module_names:
                    imports['standard'].append(module)
                else:
                    imports['third_party'].append(module)

            # From import statements
            elif line.startswith('from '):
                parts = line.split(' import ')
                if len(parts) >= 2:
                    module_path = parts[0].replace('from ', '').strip()
                    module = module_path.split('.')[0]

                    if module in sys.stdlib_module_names:
                        imports['standard'].append(module)
                    elif module_path.startswith('.'):
                        imports['local'].append(module_path)
                    else:
                        imports['third_party'].append(module)

            # Try/except imports (conditional)
            elif 'import ' in line and ('try:' in content or 'except ImportError' in content):
                if 'import ' in line:
                    module = line.split('import ')[-1].split(' as ')[0].split('.')[0].strip()
                    imports['conditional'].append(module)

    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")

    return imports

def test_import(module_name: str, import_type: str) -> Dict[str, Any]:
    """Test if a module can be imported"""
    result = {
        'module': module_name,
        'type': import_type,
        'success': False,
        'error': None,
        'warnings': []
    }

    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Handle local imports
            if import_type == 'local':
                if module_name.startswith('.'):
                    # Relative import - try to import from src
                    try:
                        module_name = module_name.replace('.', 'src', 1)
                    except:
                        pass

            # Try to import the module
            if '.' in module_name:
                # Handle submodules
                parts = module_name.split('.')
                parent_module = parts[0]

                # First import the parent
                importlib.import_module(parent_module)

                # Then try the full module
                importlib.import_module(module_name)
            else:
                importlib.import_module(module_name)

            result['success'] = True

            # Check for warnings
            for warning in w:
                result['warnings'].append(str(warning.message))

    except ImportError as e:
        result['error'] = f"ImportError: {e}"
    except ModuleNotFoundError as e:
        result['error'] = f"ModuleNotFoundError: {e}"
    except Exception as e:
        result['error'] = f"Other error: {e}"

    return result

def validate_project_imports():
    """Validate all imports in the project"""
    print("🔍 VALIDATING PROJECT IMPORTS")
    print("=" * 60)

    python_files = get_all_python_files()
    print(f"📁 Found {len(python_files)} Python files")

    all_imports = {
        'standard': set(),
        'third_party': set(),
        'local': set(),
        'conditional': set()
    }

    # Extract imports from all files
    print("\\n📖 Extracting imports from files...")
    for file_path in python_files:
        relative_path = file_path.relative_to(project_root)
        imports = extract_imports_from_file(file_path)

        for import_type, modules in imports.items():
            all_imports[import_type].update(modules)

        print(f"  📄 {relative_path}: {sum(len(modules) for modules in imports.values())} imports")

    # Test imports
    print("\\n🧪 Testing imports...")

    results = {
        'standard': [],
        'third_party': [],
        'local': [],
        'conditional': []
    }

    failed_imports = []
    warning_imports = []

    # Test standard library imports
    print("\\n📚 Testing standard library imports...")
    for module in sorted(all_imports['standard']):
        result = test_import(module, 'standard')
        results['standard'].append(result)

        if not result['success']:
            failed_imports.append(result)
            print(f"❌ {module}: {result['error']}")
        elif result['warnings']:
            warning_imports.append(result)
            print(f"⚠️  {module}: {len(result['warnings'])} warnings")

    # Test third-party imports
    print("\\n📦 Testing third-party imports...")
    for module in sorted(all_imports['third_party']):
        result = test_import(module, 'third_party')
        results['third_party'].append(result)

        if not result['success']:
            failed_imports.append(result)
            print(f"❌ {module}: {result['error']}")
        elif result['warnings']:
            warning_imports.append(result)
            print(f"⚠️  {module}: {len(result['warnings'])} warnings")

    # Test local imports
    print("\\n🏠 Testing local imports...")
    for module in sorted(all_imports['local']):
        result = test_import(module, 'local')
        results['local'].append(result)

        if not result['success']:
            failed_imports.append(result)
            print(f"❌ {module}: {result['error']}")
        elif result['warnings']:
            warning_imports.append(result)
            print(f"⚠️  {module}: {len(result['warnings'])} warnings")

    # Test conditional imports
    print("\\n🔄 Testing conditional imports...")
    for module in sorted(all_imports['conditional']):
        result = test_import(module, 'conditional')
        results['conditional'].append(result)

        if not result['success']:
            print(f"ℹ️  {module}: {result['error']} (conditional - may be expected)")
        elif result['warnings']:
            warning_imports.append(result)
            print(f"⚠️  {module}: {len(result['warnings'])} warnings")

    # Summary
    print("\\n" + "=" * 60)
    print("📊 IMPORT VALIDATION SUMMARY")
    print("=" * 60)

    total_tested = sum(len(results[category]) for category in results)
    total_successful = sum(len([r for r in results[category] if r['success']]) for category in results)
    total_warnings = len(warning_imports)
    total_failed = len(failed_imports)

    print(f"📈 Total imports tested: {total_tested}")
    print(f"✅ Successful imports: {total_successful}")
    print(f"⚠️  Imports with warnings: {total_warnings}")
    print(f"❌ Failed imports: {total_failed}")

    success_rate = (total_successful / total_tested * 100) if total_tested > 0 else 0
    print(f"🎯 Success rate: {success_rate:.1f}%")

    # Detailed results
    print("\\n📋 BREAKDOWN BY CATEGORY:")

    for category in ['standard', 'third_party', 'local', 'conditional']:
        category_results = results[category]
        successful = len([r for r in category_results if r['success']])
        print("12")

    if failed_imports:
        print("\\n❌ FAILED IMPORTS (need attention):")
        for result in failed_imports:
            print(f"  {result['module']} ({result['type']}): {result['error']}")

    if warning_imports:
        print("\\n⚠️  IMPORTS WITH WARNINGS:")
        for result in warning_imports:
            print(f"  {result['module']} ({result['type']}): {len(result['warnings'])} warnings")

    # Recommendations
    print("\\n💡 RECOMMENDATIONS:")

    if failed_imports:
        print("  🔧 Fix failed imports by:")
        print("     - Installing missing packages: pip install <package>")
        print("     - Checking import paths for local modules")
        print("     - Updating requirements.txt with missing dependencies")

    if warning_imports:
        print("  ⚠️  Review imports with warnings:")
        print("     - Update deprecated packages")
        print("     - Check for version compatibility issues")

    if success_rate >= 95:
        print("  ✅ Import validation successful!")
    elif success_rate >= 80:
        print("  🟡 Import validation mostly successful")
    else:
        print("  ❌ Import validation needs attention")

    return {
        'success_rate': success_rate,
        'total_tested': total_tested,
        'successful': total_successful,
        'warnings': total_warnings,
        'failed': total_failed,
        'failed_imports': failed_imports,
        'warning_imports': warning_imports
    }

def create_import_report(results: Dict[str, Any]):
    """Create a detailed import report"""
    report_file = Path("import_validation_report.md")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# ValidoAI Import Validation Report\\n\\n")
        f.write("Generated by validate_imports.py\\n\\n")

        f.write("## 📊 Summary\\n\\n")
        f.write(f"- **Total imports tested**: {results['total_tested']}\\n")
        f.write(f"- **Successful imports**: {results['successful']}\\n")
        f.write(f"- **Imports with warnings**: {results['warnings']}\\n")
        f.write(f"- **Failed imports**: {results['failed']}\\n")
        f.write(f"- **Success rate**: {results['success_rate']:.1f}%\\n\\n")

        if results['failed_imports']:
            f.write("## ❌ Failed Imports\\n\\n")
            for result in results['failed_imports']:
                f.write(f"- **{result['module']}** ({result['type']}): {result['error']}\\n")

        if results['warning_imports']:
            f.write("\\n## ⚠️  Imports with Warnings\\n\\n")
            for result in results['warning_imports']:
                f.write(f"- **{result['module']}** ({result['type']}): {len(result['warnings'])} warnings\\n")

        f.write("\\n## 🎯 Recommendations\\n\\n")

        if results['failed_imports']:
            f.write("### Critical Issues:\\n")
            f.write("- Install missing packages with: `pip install <package>`\\n")
            f.write("- Fix import paths for local modules\\n")
            f.write("- Update requirements.txt\\n\\n")

        if results['warning_imports']:
            f.write("### Warning Issues:\\n")
            f.write("- Update deprecated packages\\n")
            f.write("- Check version compatibility\\n\\n")

        f.write(f"Report generated: {Path(__file__).name}\\n")

    print(f"📄 Detailed report saved: {report_file}")

def main():
    """Main function"""
    try:
        results = validate_project_imports()
        create_import_report(results)

        print(f"\\n🎉 Import validation completed!")
        print(f"📊 Success rate: {results['success_rate']:.1f}%")

    except Exception as e:
        print(f"❌ Error during import validation: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
