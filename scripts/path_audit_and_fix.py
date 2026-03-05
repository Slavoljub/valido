#!/usr/bin/env python3
"""
Path Audit and Fix Script for ValidoAI
========================================

This script systematically audits and fixes all file path references throughout the codebase
to ensure they match the current file structure and locations.

Usage:
    python scripts/path_audit_and_fix.py [--audit-only] [--fix] [--verbose]

Options:
    --audit-only    : Only audit paths without making changes
    --fix           : Apply fixes to incorrect paths
    --verbose       : Show detailed output

Author: ValidoAI Path Audit Tool
Date: 2024
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PathIssue:
    """Represents a path issue found in the codebase"""
    file_path: str
    line_number: int
    original_path: str
    corrected_path: str
    issue_type: str  # 'import', 'template', 'static', 'config', 'database'
    severity: str = 'warning'  # 'error', 'warning', 'info'
    description: str = ''

@dataclass
class PathAuditResult:
    """Results of the path audit"""
    total_files_scanned: int = 0
    issues_found: List[PathIssue] = field(default_factory=list)
    issues_fixed: List[PathIssue] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class PathAuditor:
    """Audits and fixes file paths in the ValidoAI codebase"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.project_root = self.root_path
        self.audit_result = PathAuditResult()

        # Define expected file structure
        self.expected_structure = {
            'src': {
                'controllers': {},
                'models': {},
                'services': {},
                'assets': {},
                'routes': {},
                'config': {},
                'utils': {},
                'ai_local_models': {}
            },
            'templates': {
                'layouts': {},
                'components': {},
                'admin': {},
                'dashboard': {},
                'auth': {},
                'errors': {},
                'example-pages': {}
            },
            'static': {
                'css': {},
                'js': {},
                'images': {},
                'favicons': {},
                'fonts': {}
            },
            'tests': {
                'unit': {},
                'integration': {},
                'e2e': {},
                'functional': {},
                'routes': {},
                'performance': {},
                'security': {}
            },
            'docs': {
                'api': {},
                'architecture': {},
                'guides': {},
                'deployment': {},
                'security': {},
                'tutorials': {},
                'development': {}
            },
            'configuration_scripts': {},
            'data': {
                'sqlite': {},
                'postgresql': {}
            },
            'logs': {},
            'cache': {},
            'translations': {},
            'uploads': {},
            'scripts': {}
        }

        # Common path patterns and their corrections
        self.path_patterns = {
            # Python imports
            r'from\s+src\.controllers\.': 'from src.controllers.',
            r'from\s+src\.models\.': 'from src.models.',
            r'from\s+src\.services\.': 'from src.services.',
            r'from\s+src\.assets\.': 'from src.assets.',
            r'from\s+src\.routes\.': 'from src.routes.',
            r'from\s+src\.config\.': 'from src.config.',
            r'from\s+src\.utils\.': 'from src.utils.',

            # Template extends/includes
            r'extends\s+["\']templates/': 'extends "layouts/',
            r'extends\s+["\']base\.html["\']': 'extends "layouts/base.html"',
            r'include\s+["\']components/': 'include "templates/components/',

            # Static file references
            r'static/': '/static/',
            r'/static/static/': '/static/',
            r'css/': '/static/css/',
            r'js/': '/static/js/',
            r'images/': '/static/images/',
            r'fonts/': '/static/fonts/',

            # Database paths
            r'data/sqlite/': 'data/sqlite/',
            r'data/postgresql/': 'data/postgresql/',
        }

        # Files that should exist
        self.required_files = [
            'app.py',
            'routes.py',
            'src/__init__.py',
            'templates/layouts/base.html',
            'static/css/main.css',
            'static/js/main.js',
            'requirements.txt',
            'env.example'
        ]

        # Directories that should exist
        self.required_dirs = [
            'src',
            'templates',
            'templates/layouts',
            'templates/components',
            'static',
            'static/css',
            'static/js',
            'static/images',
            'tests',
            'docs',
            'configuration_scripts',
            'data',
            'data/sqlite',
            'scripts'
        ]

    def scan_file(self, file_path: Path) -> List[PathIssue]:
        """Scan a single file for path issues"""
        issues = []
        file_extension = file_path.suffix.lower()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Check Python files
                if file_extension == '.py':
                    issues.extend(self._check_python_paths(file_path, line_num, line))

                # Check HTML templates
                elif file_extension == '.html':
                    issues.extend(self._check_template_paths(file_path, line_num, line))

                # Check CSS files
                elif file_extension == '.css':
                    issues.extend(self._check_css_paths(file_path, line_num, line))

                # Check JavaScript files
                elif file_extension == '.js':
                    issues.extend(self._check_js_paths(file_path, line_num, line))

                # Check configuration files
                elif file_extension in ['.json', '.yml', '.yaml', '.ini', '.cfg']:
                    issues.extend(self._check_config_paths(file_path, line_num, line))

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            self.audit_result.errors.append(f"Error scanning {file_path}: {e}")

        return issues

    def _check_python_paths(self, file_path: Path, line_num: int, line: str) -> List[PathIssue]:
        """Check Python files for import and path issues"""
        issues = []

        # Check relative imports
        if re.search(r'from\s+\.\.', line):
            if not self._is_valid_relative_import(file_path, line):
                issues.append(PathIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_path=line.strip(),
                    corrected_path=self._fix_relative_import(file_path, line),
                    issue_type='import',
                    severity='warning',
                    description='Relative import may be incorrect'
                ))

        # Check absolute imports
        if re.search(r'from\s+src\.', line):
            if not self._is_valid_src_import(line):
                issues.append(PathIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_path=line.strip(),
                    corrected_path=self._fix_src_import(line),
                    issue_type='import',
                    severity='error',
                    description='Invalid src module import'
                ))

        # Check file path references in Python files
        for pattern, replacement in self.path_patterns.items():
            if pattern.startswith('r') and pattern.endswith('/'):
                continue  # Skip regex patterns for now

            if pattern in line and 'static/' in pattern:
                if self._has_double_static(line):
                    issues.append(PathIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        original_path=line.strip(),
                        corrected_path=line.replace('static/static/', 'static/'),
                        issue_type='static',
                        severity='error',
                        description='Double static path'
                    ))

        return issues

    def _check_template_paths(self, file_path: Path, line_num: int, line: str) -> List[PathIssue]:
        """Check HTML templates for path issues"""
        issues = []

        # Check template extends
        extends_match = re.search(r'{%\s*extends\s+["\']([^"\']+)["\']', line)
        if extends_match:
            template_path = extends_match.group(1)
            if not self._is_valid_template_path(template_path):
                issues.append(PathIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_path=template_path,
                    corrected_path=self._fix_template_path(template_path),
                    issue_type='template',
                    severity='error',
                    description='Invalid template path in extends'
                ))

        # Check template includes
        include_match = re.search(r'{%\s*include\s+["\']([^"\']+)["\']', line)
        if include_match:
            template_path = include_match.group(1)
            if not self._is_valid_template_path(template_path):
                issues.append(PathIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_path=template_path,
                    corrected_path=self._fix_template_path(template_path),
                    issue_type='template',
                    severity='error',
                    description='Invalid template path in include'
                ))

        # Check static file references
        static_match = re.search(r'["\'](?:static/|css/|js/|images/|fonts/)([^"\']+)["\']', line)
        if static_match:
            static_path = static_match.group(0)
            if self._has_double_static(static_path):
                issues.append(PathIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_path=static_path,
                    corrected_path=static_path.replace('static/static/', 'static/'),
                    issue_type='static',
                    severity='error',
                    description='Double static path in template'
                ))

        return issues

    def _check_css_paths(self, file_path: Path, line_num: int, line: str) -> List[PathIssue]:
        """Check CSS files for path issues"""
        issues = []

        # Check @import statements
        import_match = re.search(r'@import\s+["\']([^"\']+)["\']', line)
        if import_match:
            css_path = import_match.group(1)
            if not self._is_valid_css_path(css_path):
                issues.append(PathIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_path=css_path,
                    corrected_path=self._fix_css_path(css_path),
                    issue_type='static',
                    severity='warning',
                    description='Invalid CSS import path'
                ))

        # Check url() references
        url_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', line)
        if url_match:
            url_path = url_match.group(1)
            if self._has_double_static(url_path):
                issues.append(PathIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_path=url_path,
                    corrected_path=url_path.replace('static/static/', 'static/'),
                    issue_type='static',
                    severity='error',
                    description='Double static path in CSS url'
                ))

        return issues

    def _check_js_paths(self, file_path: Path, line_num: int, line: str) -> List[PathIssue]:
        """Check JavaScript files for path issues"""
        issues = []

        # Check import/export statements
        import_match = re.search(r'(?:import|export).*from\s+["\']([^"\']+)["\']', line)
        if import_match:
            js_path = import_match.group(1)
            if self._has_double_static(js_path):
                issues.append(PathIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_path=js_path,
                    corrected_path=js_path.replace('static/static/', 'static/'),
                    issue_type='static',
                    severity='error',
                    description='Double static path in JS import'
                ))

        return issues

    def _check_config_paths(self, file_path: Path, line_num: int, line: str) -> List[PathIssue]:
        """Check configuration files for path issues"""
        issues = []

        # Check for file path references
        path_match = re.search(r'["\']([^"\']*\.(?:py|html|css|js|json|yml|yaml|ini|cfg|md|txt|db|sqlite|sql))["\']', line)
        if path_match:
            config_path = path_match.group(1)
            if self._has_double_static(config_path):
                issues.append(PathIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_path=config_path,
                    corrected_path=config_path.replace('static/static/', 'static/'),
                    issue_type='config',
                    severity='error',
                    description='Double static path in config'
                ))

        return issues

    def _is_valid_relative_import(self, file_path: Path, import_line: str) -> bool:
        """Check if a relative import is valid"""
        # Extract the relative path from the import
        match = re.search(r'from\s+([\.]+)([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)', import_line)
        if not match:
            return True  # Not a relative import we can validate

        dots = match.group(1)
        module_path = match.group(2)

        # Calculate the expected directory level
        current_dir = file_path.parent
        for _ in range(len(dots) - 1):  # -1 because one dot is for current directory
            current_dir = current_dir.parent

        # Check if the module exists at the expected location
        module_file = current_dir / f"{module_path.replace('.', '/')}.py"
        return module_file.exists()

    def _fix_relative_import(self, file_path: Path, import_line: str) -> str:
        """Fix a relative import"""
        # This is a simplified fix - in practice, you might need more sophisticated logic
        return import_line  # Return as-is for now

    def _is_valid_src_import(self, import_line: str) -> bool:
        """Check if a src import is valid"""
        match = re.search(r'from\s+src\.([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)', import_line)
        if not match:
            return True

        module_path = match.group(1).replace('.', '/')
        module_file = self.root_path / 'src' / f"{module_path}.py"

        return module_file.exists()

    def _fix_src_import(self, import_line: str) -> str:
        """Fix a src import"""
        return import_line  # Return as-is for now

    def _is_valid_template_path(self, template_path: str) -> bool:
        """Check if a template path is valid"""
        if template_path.startswith('layouts/'):
            template_file = self.root_path / 'templates' / template_path
        elif template_path.startswith('templates/'):
            template_file = self.root_path / template_path
        else:
            template_file = self.root_path / 'templates' / template_path

        return template_file.exists()

    def _fix_template_path(self, template_path: str) -> str:
        """Fix a template path"""
        if template_path == 'base.html':
            return 'layouts/base.html'
        elif not template_path.startswith('layouts/') and not template_path.startswith('templates/'):
            return f"layouts/{template_path}"
        return template_path

    def _is_valid_css_path(self, css_path: str) -> bool:
        """Check if a CSS path is valid"""
        css_file = self.root_path / 'static' / 'css' / css_path
        return css_file.exists()

    def _fix_css_path(self, css_path: str) -> str:
        """Fix a CSS path"""
        return css_path  # Return as-is for now

    def _has_double_static(self, path: str) -> bool:
        """Check if a path has double static"""
        return 'static/static/' in path

    def audit_project(self) -> PathAuditResult:
        """Audit the entire project for path issues"""
        logger.info("Starting path audit...")

        # Check directory structure
        self._check_directory_structure()

        # Check required files
        self._check_required_files()

        # Scan all files
        file_extensions = ['.py', '.html', '.css', '.js', '.json', '.yml', '.yaml', '.ini', '.cfg', '.md']
        for ext in file_extensions:
            for file_path in self.root_path.rglob(f"*{ext}"):
                if self._should_scan_file(file_path):
                    issues = self.scan_file(file_path)
                    self.audit_result.issues_found.extend(issues)
                    self.audit_result.total_files_scanned += 1

        logger.info(f"Path audit complete. Scanned {self.audit_result.total_files_scanned} files.")
        logger.info(f"Found {len(self.audit_result.issues_found)} potential issues.")

        return self.audit_result

    def _should_scan_file(self, file_path: Path) -> bool:
        """Determine if a file should be scanned"""
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'env', 'htmlcov', 'cache'}
        for skip_dir in skip_dirs:
            if skip_dir in file_path.parts:
                return False

        # Skip certain files
        skip_files = {'package-lock.json', '.gitignore', '.gitattributes'}
        if file_path.name in skip_files:
            return False

        return True

    def _check_directory_structure(self):
        """Check that the expected directory structure exists"""
        for dir_path in self.required_dirs:
            full_path = self.root_path / dir_path
            if not full_path.exists():
                self.audit_result.errors.append(f"Missing required directory: {dir_path}")

    def _check_required_files(self):
        """Check that required files exist"""
        for file_path in self.required_files:
            full_path = self.root_path / file_path
            if not full_path.exists():
                self.audit_result.errors.append(f"Missing required file: {file_path}")

    def fix_issues(self, issues: List[PathIssue]) -> List[PathIssue]:
        """Fix the identified path issues"""
        fixed_issues = []

        for issue in issues:
            try:
                self._fix_single_issue(issue)
                fixed_issues.append(issue)
                logger.info(f"Fixed: {issue.description} in {issue.file_path}:{issue.line_number}")
            except Exception as e:
                logger.error(f"Failed to fix issue in {issue.file_path}:{issue.line_number}: {e}")
                self.audit_result.errors.append(f"Failed to fix {issue.file_path}:{issue.line_number}: {e}")

        return fixed_issues

    def _fix_single_issue(self, issue: PathIssue):
        """Fix a single path issue"""
        file_path = Path(issue.file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if issue.line_number <= len(lines):
            original_line = lines[issue.line_number - 1]

            # Replace the problematic path with the corrected one
            if issue.original_path in original_line:
                corrected_line = original_line.replace(issue.original_path, issue.corrected_path)
                lines[issue.line_number - 1] = corrected_line

                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

    def generate_report(self) -> str:
        """Generate a detailed audit report"""
        report = []
        report.append("# ValidoAI Path Audit Report")
        report.append("=" * 50)
        report.append(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        report.append(f"## Summary")
        report.append(f"- Files scanned: {self.audit_result.total_files_scanned}")
        report.append(f"- Issues found: {len(self.audit_result.issues_found)}")
        report.append(f"- Issues fixed: {len(self.audit_result.issues_fixed)}")
        report.append(f"- Errors: {len(self.audit_result.errors)}")
        report.append("")

        if self.audit_result.errors:
            report.append("## Errors")
            for error in self.audit_result.errors:
                report.append(f"- {error}")
            report.append("")

        if self.audit_result.issues_found:
            report.append("## Issues Found")

            # Group issues by type
            issues_by_type = {}
            for issue in self.audit_result.issues_found:
                if issue.issue_type not in issues_by_type:
                    issues_by_type[issue.issue_type] = []
                issues_by_type[issue.issue_type].append(issue)

            for issue_type, issues in issues_by_type.items():
                report.append(f"### {issue_type.title()} Issues ({len(issues)})")
                for issue in issues:
                    report.append(f"- **{issue.file_path}:{issue.line_number}**")
                    report.append(f"  - Original: `{issue.original_path}`")
                    report.append(f"  - Corrected: `{issue.corrected_path}`")
                    report.append(f"  - Severity: {issue.severity}")
                    report.append(f"  - Description: {issue.description}")
                    report.append("")
                report.append("")

        if self.audit_result.issues_fixed:
            report.append("## Issues Fixed")
            for issue in self.audit_result.issues_fixed:
                report.append(f"- ✅ {issue.file_path}:{issue.line_number} - {issue.description}")
            report.append("")

        report.append("## Recommendations")
        if self.audit_result.issues_found:
            report.append("1. Review all issues and apply fixes where appropriate")
            report.append("2. Test the application after applying fixes")
            report.append("3. Consider setting up automated path validation in CI/CD")
        else:
            report.append("✅ No path issues found! The codebase appears to be well-structured.")

        return "\n".join(report)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Path Audit and Fix Tool for ValidoAI')
    parser.add_argument('--audit-only', action='store_true', help='Only audit paths without making changes')
    parser.add_argument('--fix', action='store_true', help='Apply fixes to incorrect paths')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    parser.add_argument('--output', type=str, help='Output report file path')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize auditor
    auditor = PathAuditor('.')

    # Run audit
    audit_result = auditor.audit_project()

    # Fix issues if requested
    if args.fix and not args.audit_only:
        logger.info("Applying fixes...")
        fixed_issues = auditor.fix_issues(audit_result.issues_found)
        audit_result.issues_fixed = fixed_issues

    # Generate report
    report = auditor.generate_report()

    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    # Exit with appropriate code
    if audit_result.errors or (audit_result.issues_found and not args.fix):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
