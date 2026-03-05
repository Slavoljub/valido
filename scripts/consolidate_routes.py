#!/usr/bin/env python3
"""
Consolidate Routes - Move all scattered routes into main routes.py
Follows Cursor rules: "All routes only in routes.py - no routes duplication"
"""

import sys
import os
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def find_route_files():
    """Find all files containing Flask routes"""
    route_files = []

    # Search for @app.route, @main_bp.route, etc. patterns
    route_patterns = [
        r'@.*\.route\(.*\)',
        r'@.*_bp\.route\(.*\)',
        r'def .*route.*\(.*\):',
        r'app\.add_url_rule\(.*\)'
    ]

    # Directories to search
    search_dirs = [
        'src',
        'scripts',
        '.'
    ]

    for search_dir in search_dirs:
        search_path = project_root / search_dir
        if search_path.exists():
            for file_path in search_path.rglob('*.py'):
                if file_path.name in ['routes.py', '__init__.py', 'consolidate_routes.py']:
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    has_routes = False
                    for pattern in route_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            has_routes = True
                            break

                    if has_routes:
                        route_files.append(file_path)

                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return route_files

def extract_routes_from_file(file_path):
    """Extract routes from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

    routes = []

    # Find route definitions with their decorators and functions
    route_pattern = r'(@.*\.route\([^\)]+\)\s*)+def\s+(\w+)\s*\([^)]*\):'
    matches = re.finditer(route_pattern, content, re.MULTILINE | re.DOTALL)

    for match in matches:
        # Get the full route definition with decorators
        start_pos = match.start()

        # Find the end of the function (next function definition or end of file)
        func_content = content[start_pos:]

        # Simple approach: find the next function definition
        next_func = re.search(r'\n@.*\.route\(|^\s*def\s+\w+\s*\(', func_content[1:], re.MULTILINE)
        if next_func:
            func_content = func_content[:next_func.start() + 1]
        else:
            # Find the end by looking for proper indentation
            lines = func_content.split('\n')
            func_lines = []
            base_indent = None

            for i, line in enumerate(lines):
                if line.strip().startswith('@') or line.strip().startswith('def'):
                    if base_indent is None:
                        # Count leading spaces for the function definition
                        base_indent = len(line) - len(line.lstrip())
                        func_lines.append(line)
                    elif len(line) - len(line.lstrip()) <= base_indent:
                        break
                    else:
                        func_lines.append(line)
                elif base_indent is not None:
                    func_lines.append(line)

            func_content = '\n'.join(func_lines)

        routes.append({
            'file': file_path,
            'content': func_content.strip(),
            'function_name': match.group(2)
        })

    return routes

def consolidate_routes():
    """Main function to consolidate all routes"""
    print("🔄 Consolidating Routes - Following Cursor Rules")
    print("=" * 60)
    print("Rule: All routes only in routes.py - no routes duplication")

    # Find all files with routes
    print("\n🔍 Searching for route files...")
    route_files = find_route_files()

    print(f"📋 Found {len(route_files)} files with routes:")
    for file_path in route_files:
        print(f"  - {file_path.relative_to(project_root)}")

    # Extract routes from each file
    print("\n📝 Extracting routes...")
    all_routes = []

    for file_path in route_files:
        print(f"  Processing {file_path.relative_to(project_root)}...")
        routes = extract_routes_from_file(file_path)
        all_routes.extend(routes)
        print(f"    Found {len(routes)} routes")

    print(f"\n📊 Total routes found: {len(all_routes)}")

    if not all_routes:
        print("✅ No scattered routes found - already consolidated!")
        return

    # Show routes by file
    print("\n📋 Routes by file:")
    file_routes = {}
    for route in all_routes:
        file_path = route['file'].relative_to(project_root)
        if file_path not in file_routes:
            file_routes[file_path] = []
        file_routes[file_path].append(route['function_name'])

    for file_path, functions in file_routes.items():
        print(f"  {file_path}: {len(functions)} routes")
        for func in functions[:3]:  # Show first 3
            print(f"    - {func}")
        if len(functions) > 3:
            print(f"    ... and {len(functions) - 3} more")

    # Generate consolidation report
    print("\n📋 CONSOLIDATION REPORT")
    print("=" * 40)

    consolidation_plan = []
    consolidation_plan.append("# Route Consolidation Plan")
    consolidation_plan.append("")
    consolidation_plan.append("## Files with Routes to Consolidate:")
    consolidation_plan.append("")

    for file_path, functions in file_routes.items():
        consolidation_plan.append(f"### {file_path}")
        consolidation_plan.append(f"- **Routes:** {len(functions)}")
        consolidation_plan.append("- **Action:** Move to routes.py")
        consolidation_plan.append("- **Functions:**")
        for func in functions:
            consolidation_plan.append(f"  - {func}")
        consolidation_plan.append("")

    consolidation_plan.append("## Implementation Steps:")
    consolidation_plan.append("1. Review each route for conflicts")
    consolidation_plan.append("2. Move routes to appropriate sections in routes.py")
    consolidation_plan.append("3. Update imports and dependencies")
    consolidation_plan.append("4. Test all routes after consolidation")
    consolidation_plan.append("5. Remove route definitions from original files")

    # Save report
    report_path = project_root / "logs" / "route_consolidation_report.md"
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(consolidation_plan))

    print(f"💾 Report saved to: {report_path}")

    # Show summary
    print("\n🎯 SUMMARY")
    print("-" * 30)
    print(f"📁 Files with routes: {len(file_routes)}")
    print(f"🔄 Routes to consolidate: {len(all_routes)}")
    print("📝 Report: logs/route_consolidation_report.md")
    print("\n🚨 IMPORTANT: Manual review required before consolidation!")
    print("   - Check for route conflicts")
    print("   - Verify dependencies")
    print("   - Test after consolidation")

if __name__ == "__main__":
    consolidate_routes()
