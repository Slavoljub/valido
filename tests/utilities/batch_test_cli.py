#!/usr/bin/env python3
"""
ValidoAI Batch Testing CLI
Provides a beautiful command-line interface for running comprehensive tests
with progress tracking, reporting, and analysis.
"""

import os
import sys
import time
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import requests
from urllib.parse import urljoin
import platform
import psutil
import json as json_lib

# Third-party imports
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn, TaskProgressColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.columns import Columns
    from rich.align import Align
    from rich.tree import Tree
    from rich.markdown import Markdown
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    import lighthouse
except ImportError:
    print("❌ Required packages not installed. Install with:")
    print("   pip install rich plotly pandas selenium webdriver-manager psutil requests lighthouse")
    sys.exit(1)

class ValidoAITestCLI:
    """Main CLI class for ValidoAI testing."""

    def __init__(self):
        self.console = Console()
        self.test_results = []
        self.db_path = Path("data/sqlite/app.db")
        self.reports_dir = Path("tests/reports")
        self.reports_dir.mkdir(exist_ok=True)

        # Test categories and their configurations
        self.test_categories = {
            "ui": {
                "name": "UI/UX Tests",
                "description": "User interface and experience validation",
                "script": "test_ui_comprehensive.py",
                "weight": 25,
                "parallel": True,
                "requires_internet": False
            },
            "performance": {
                "name": "Performance Tests",
                "description": "Load time, memory usage, theme switching",
                "script": "test_performance.py",
                "weight": 20,
                "parallel": False,
                "requires_internet": True
            },
            "accessibility": {
                "name": "Accessibility Tests",
                "description": "WCAG compliance and inclusive design",
                "script": "test_accessibility.py",
                "weight": 15,
                "parallel": True,
                "requires_internet": False
            },
            "functional": {
                "name": "Functional Tests",
                "description": "Core functionality verification",
                "script": "test_functional.py",
                "weight": 20,
                "parallel": True,
                "requires_internet": False
            },
            "regression": {
                "name": "Regression Tests",
                "description": "Visual regression and compatibility",
                "script": "test_regression.py",
                "weight": 10,
                "parallel": False,
                "requires_internet": True
            },
            "security": {
                "name": "Security Tests",
                "description": "Security vulnerabilities and compliance",
                "script": "test_security.py",
                "weight": 5,
                "parallel": True,
                "requires_internet": True
            },
            "lighthouse": {
                "name": "Lighthouse Tests",
                "description": "Google Lighthouse performance audit",
                "script": "test_lighthouse.py",
                "weight": 5,
                "parallel": False,
                "requires_internet": True
            }
        }

        # System information
        self.system_info = self.get_system_info()
        self.internet_status = self.check_internet_connection()

    def setup_database(self):
        """Initialize SQLite database for test results."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    category TEXT,
                    test_name TEXT,
                    status TEXT,
                    duration REAL,
                    error_message TEXT,
                    screenshot_path TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    category TEXT,
                    progress REAL,
                    eta REAL,
                    status TEXT
                )
            ''')

            conn.commit()

    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "memory_total": round(psutil.virtual_memory().total / (1024**3), 2),  # GB
            "memory_available": round(psutil.virtual_memory().available / (1024**3), 2),  # GB
            "cpu_count": psutil.cpu_count(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "disk_total": round(psutil.disk_usage('/').total / (1024**3), 2),  # GB
            "disk_free": round(psutil.disk_usage('/').free / (1024**3), 2),  # GB
            "network_interfaces": len(psutil.net_if_addrs()),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }

    def check_internet_connection(self) -> Dict[str, Any]:
        """Check internet connection status and speed."""
        status = {
            "connected": False,
            "speed": "N/A",
            "latency": "N/A",
            "download_speed": "N/A",
            "upload_speed": "N/A"
        }

        try:
            # Check basic connectivity
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            status["connected"] = True

            # Test latency
            start_time = time.time()
            requests.get("https://www.google.com", timeout=5)
            status["latency"] = f"{round((time.time() - start_time) * 1000)}ms"

            # Basic speed test (simple download)
            test_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
            start_time = time.time()
            response = requests.get(test_url, timeout=10)
            download_time = time.time() - start_time
            if response.status_code == 200:
                size_kb = len(response.content) / 1024
                speed_mbps = round((size_kb * 8) / download_time, 2)
                status["download_speed"] = f"{speed_mbps} Mbps"

        except Exception as e:
            status["error"] = str(e)

        return status

    def save_test_result(self, category: str, test_name: str, status: str,
                        duration: float, error_message: str = None,
                        screenshot_path: str = None):
        """Save individual test result to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO test_runs (category, test_name, status, duration, error_message, screenshot_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (category, test_name, status, duration, error_message, screenshot_path))
            conn.commit()

    def update_progress(self, category: str, progress: float, eta: float, status: str):
        """Update test progress in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO test_progress (category, progress, eta, status)
                VALUES (?, ?, ?, ?)
            ''', (category, progress, eta, status))
            conn.commit()

    def show_header(self):
        """Display CLI header with branding and system information."""
        # System status
        internet_icon = "🟢" if self.internet_status.get("connected") else "🔴"
        memory_usage = f"{self.system_info['memory_available']}/{self.system_info['memory_total']}GB"
        cpu_usage = f"{self.system_info['cpu_usage']}%"

        header = Panel.fit(
            Align.center(
                Text("🚀 ValidoAI Test Suite", style="bold blue"),
                Text("\nComprehensive Testing Framework", style="dim"),
                Text("\nTheme System • UI/UX • Performance • Accessibility", style="dim blue"),
                Text(f"\n{internet_icon} Internet: {self.internet_status.get('latency', 'N/A')} • 💾 RAM: {memory_usage} • ⚡ CPU: {cpu_usage}", style="dim cyan")
            ),
            title="[bold blue]ValidoAI[/bold blue]",
            border_style="blue"
        )
        self.console.print(header)
        self.console.print()

    def show_system_info(self):
        """Display detailed system information."""
        info_table = Table(title="🖥️ System Information", show_header=True, header_style="bold blue")
        info_table.add_column("Component", style="cyan", no_wrap=True)
        info_table.add_column("Details", style="white")

        info_table.add_row("Platform", f"{self.system_info['platform']} {self.system_info['platform_version']}")
        info_table.add_row("Architecture", self.system_info['architecture'])
        info_table.add_row("Python Version", self.system_info['python_version'])
        info_table.add_row("Processor", self.system_info['processor'] or "Unknown")
        info_table.add_row("CPU Cores", str(self.system_info['cpu_count']))
        info_table.add_row("Memory", f"{self.system_info['memory_available']}/{self.system_info['memory_total']} GB available")
        info_table.add_row("Disk Space", f"{self.system_info['disk_free']}/{self.system_info['disk_total']} GB free")
        info_table.add_row("Boot Time", self.system_info['boot_time'])

        # Network status
        net_status = "🟢 Connected" if self.internet_status.get("connected") else "🔴 Disconnected"
        info_table.add_row("Internet Status", f"{net_status} ({self.internet_status.get('latency', 'N/A')})")
        if self.internet_status.get("download_speed"):
            info_table.add_row("Download Speed", self.internet_status['download_speed'])

        self.console.print(info_table)
        self.console.print()

    def show_test_categories(self):
        """Display available test categories in a table."""
        table = Table(title="🧪 Available Test Categories", show_header=True, header_style="bold blue")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Weight", justify="right", style="yellow")
        table.add_column("Status", justify="center", style="green")

        for key, config in self.test_categories.items():
            table.add_row(
                config["name"],
                config["description"],
                f"{config['weight']}%",
                "✅ Ready"
            )

        self.console.print(table)
        self.console.print()

    def run_single_test(self, category: str) -> Dict[str, Any]:
        """Run a single test category."""
        config = self.test_categories[category]
        script_path = Path("tests") / config["script"]

        # Check if test script exists
        if not script_path.exists():
            return {
                "status": "error",
                "error": f"Test script not found: {script_path}",
                "duration": 0
            }

        start_time = time.time()

        try:
            # Run the test script
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, timeout=300)

            duration = time.time() - start_time

            if result.returncode == 0:
                return {
                    "status": "success",
                    "output": result.stdout,
                    "duration": duration
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "output": result.stdout,
                    "duration": duration
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Test execution timed out (5 minutes)",
                "duration": 300
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "duration": time.time() - start_time
            }

    def run_batch_tests(self, categories: List[str] = None, parallel: bool = False, max_parallel: int = 3) -> Dict[str, Any]:
        """Run multiple test categories with progress tracking and smart parallelization."""
        if categories is None:
            categories = list(self.test_categories.keys())

        # Filter categories based on internet requirements
        if not self.internet_status.get("connected"):
            self.console.print("⚠️  [yellow]No internet connection detected. Skipping internet-dependent tests.[/yellow]")
            categories = [cat for cat in categories if not self.test_categories[cat].get("requires_internet", False)]
            if not categories:
                self.console.print("❌ [red]No tests can run without internet connection.[/red]")
                return {}

        results = {}
        total_weight = sum(self.test_categories[cat]["weight"] for cat in categories)

        # Separate parallel and sequential tests
        parallel_categories = [cat for cat in categories if self.test_categories[cat].get("parallel", False)]
        sequential_categories = [cat for cat in categories if not self.test_categories[cat].get("parallel", False)]

        # Progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TaskProgressColumn(),
            console=self.console,
            transient=False
        ) as progress:

            overall_task = progress.add_task("🚀 Running ValidoAI Test Suite", total=100)

            # Run parallel tests first
            if parallel_categories:
                self.console.print(f"🔄 Running {len(parallel_categories)} tests in parallel (max {max_parallel} concurrent)")
                with ThreadPoolExecutor(max_workers=min(len(parallel_categories), max_parallel)) as executor:
                    futures = {
                        executor.submit(self.run_single_test, cat): cat
                        for cat in parallel_categories
                    }

                    completed_parallel = 0
                    for future in as_completed(futures):
                        category = futures[future]
                        try:
                            result = future.result()
                            results[category] = result
                            completed_parallel += 1

                            # Update progress
                            progress.update(overall_task,
                                          completed=(completed_parallel / len(categories)) * 100)

                            # Save result to database
                            self.save_test_result(
                                category=category,
                                test_name=self.test_categories[category]["name"],
                                status=result["status"],
                                duration=result.get("duration", 0),
                                error_message=result.get("error")
                            )

                        except Exception as e:
                            results[category] = {
                                "status": "error",
                                "error": str(e),
                                "duration": 0
                            }

            # Run sequential tests
            completed_weight = sum(self.test_categories[cat]["weight"] for cat in parallel_categories)

            for category in sequential_categories:
                task = progress.add_task(
                    f"🧪 {self.test_categories[category]['name']}",
                    total=100
                )

                # Simulate sub-progress for individual test
                for i in range(20):
                    time.sleep(0.05)
                    progress.update(task, advance=5)

                # Run actual test
                result = self.run_single_test(category)
                results[category] = result

                # Update overall progress
                completed_weight += self.test_categories[category]["weight"]
                overall_progress = (completed_weight / total_weight) * 100
                progress.update(overall_task, completed=overall_progress)

                # Save result to database
                self.save_test_result(
                    category=category,
                    test_name=self.test_categories[category]["name"],
                    status=result["status"],
                    duration=result.get("duration", 0),
                    error_message=result.get("error")
                )

        return results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive test report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"test_report_{timestamp}.html"

        # Calculate statistics
        total_tests = len(results)
        passed = sum(1 for r in results.values() if r["status"] == "success")
        failed = sum(1 for r in results.values() if r["status"] == "error")
        total_duration = sum(r.get("duration", 0) for r in results.values())

        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ValidoAI Test Report - {timestamp}</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f8fafc; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
                .stat-card {{ background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
                .stat-number {{ font-size: 2rem; font-weight: bold; }}
                .stat-label {{ color: #64748b; margin-top: 0.5rem; }}
                .test-result {{ background: white; margin-bottom: 1rem; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .success {{ border-left: 4px solid #10b981; }}
                .error {{ border-left: 4px solid #ef4444; }}
                .warning {{ border-left: 4px solid #f59e0b; }}
                .duration {{ color: #64748b; font-size: 0.875rem; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 ValidoAI Test Report</h1>
                    <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number" style="color: #10b981;">{passed}</div>
                        <div class="stat-label">Passed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: #ef4444;">{failed}</div>
                        <div class="stat-label">Failed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: #3b82f6;">{total_tests}</div>
                        <div class="stat-label">Total Tests</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: #8b5cf6;">{total_duration:.1f}s</div>
                        <div class="stat-label">Duration</div>
                    </div>
                </div>

                <div class="test-results">
                    <h2>📋 Test Results</h2>
        """

        for category, result in results.items():
            status_class = "success" if result["status"] == "success" else "error"
            status_emoji = "✅" if result["status"] == "success" else "❌"
            duration = result.get("duration", 0)

            html_content += f"""
                    <div class="test-result {status_class}">
                        <h3>{status_emoji} {self.test_categories[category]['name']}</h3>
                        <p><strong>Status:</strong> {result['status'].title()}</p>
                        <p><strong>Duration:</strong> {duration:.2f}s</p>
            """

            if result.get("error"):
                html_content += f'<p><strong>Error:</strong> <code>{result["error"]}</code></p>'

            if result.get("output"):
                html_content += f'<p><strong>Output:</strong> <pre>{result["output"][:500]}...</pre></p>'

            html_content += "</div>"

        html_content += """
                </div>
            </div>
        </body>
        </html>
        """

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(report_path)

    def show_results_summary(self, results: Dict[str, Any]):
        """Display test results summary."""
        total_tests = len(results)
        passed = sum(1 for r in results.values() if r["status"] == "success")
        failed = sum(1 for r in results.values() if r["status"] == "error")
        total_duration = sum(r.get("duration", 0) for r in results.values())

        # Create summary table
        summary_table = Table(title="📊 Test Results Summary", show_header=True, header_style="bold blue")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white", justify="right")
        summary_table.add_column("Status", justify="center")

        summary_table.add_row(
            "Total Tests",
            str(total_tests),
            "📊"
        )
        summary_table.add_row(
            "Passed",
            str(passed),
            "✅" if passed > 0 else "❌"
        )
        summary_table.add_row(
            "Failed",
            str(failed),
            "❌" if failed > 0 else "✅"
        )
        summary_table.add_row(
            "Success Rate",
            f"{(passed/total_tests)*100:.1f}%",
            "🟢" if (passed/total_tests) > 0.8 else "🟡" if (passed/total_tests) > 0.6 else "🔴"
        )
        summary_table.add_row(
            "Total Duration",
            f"{total_duration:.2f}s",
            "⚡"
        )

        self.console.print(summary_table)
        self.console.print()

        # Show detailed results
        if failed > 0:
            error_table = Table(title="❌ Failed Tests", show_header=True, header_style="bold red")
            error_table.add_column("Test", style="red")
            error_table.add_column("Error", style="white")
            error_table.add_column("Duration", justify="right", style="yellow")

            for category, result in results.items():
                if result["status"] == "error":
                    error_table.add_row(
                        self.test_categories[category]["name"],
                        result.get("error", "Unknown error")[:50] + "...",
                        f"{result.get('duration', 0):.2f}s"
                    )

            self.console.print(error_table)
            self.console.print()

    def interactive_mode(self):
        """Run interactive testing mode."""
        self.show_header()
        self.show_test_categories()

        while True:
            self.console.print("\n[bold blue]Choose an action:[/bold blue]")
            self.console.print("1. 🧪 Run all tests")
            self.console.print("2. 🔍 Run specific test category")
            self.console.print("3. 📊 Generate report")
            self.console.print("4. 📈 Show test history")
            self.console.print("5. 🚪 Exit")

            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == "1":
                self.console.print("\n🚀 Running all tests...")
                results = self.run_batch_tests()
                self.show_results_summary(results)
                report_path = self.generate_report(results)
                self.console.print(f"\n📄 Report generated: {report_path}")

            elif choice == "2":
                self.console.print("\nAvailable categories:")
                for i, (key, config) in enumerate(self.test_categories.items(), 1):
                    self.console.print(f"{i}. {config['name']}")

                cat_choice = input("\nEnter category number: ").strip()
                try:
                    category = list(self.test_categories.keys())[int(cat_choice) - 1]
                    results = self.run_batch_tests([category])
                    self.show_results_summary(results)
                except (ValueError, IndexError):
                    self.console.print("❌ Invalid choice")

            elif choice == "3":
                # Generate report from last run
                self.console.print("📊 Report generation feature coming soon!")

            elif choice == "4":
                # Show test history
                self.console.print("📈 Test history feature coming soon!")

            elif choice == "5":
                self.console.print("👋 Goodbye!")
                break

            else:
                self.console.print("❌ Invalid choice. Please try again.")

    def main(self):
        """Main entry point."""
        parser = argparse.ArgumentParser(description="ValidoAI Test CLI")
        parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
        parser.add_argument("--categories", "-c", nargs="+", help="Specific test categories to run")
        parser.add_argument("--parallel", "-p", action="store_true", help="Run tests with smart parallelization")
        parser.add_argument("--max-parallel", type=int, default=3, help="Maximum parallel workers (default: 3)")
        parser.add_argument("--report", "-r", action="store_true", help="Generate HTML report")
        parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output with system info")
        parser.add_argument("--system-info", action="store_true", help="Show detailed system information")

        args = parser.parse_args()

        # Setup database
        self.setup_database()

        if args.interactive:
            self.interactive_mode()
        else:
            # Run tests based on arguments
            categories = args.categories if args.categories else list(self.test_categories.keys())

            self.show_header()

            if args.system_info:
                self.show_system_info()
                return

            if args.verbose:
                self.show_system_info()
                self.show_test_categories()

            # Display internet status
            if not self.internet_status.get("connected"):
                self.console.print("⚠️  [yellow]Internet connection required for some tests[/yellow]")

            self.console.print(f"🚀 Running tests: {', '.join(categories)}")
            self.console.print(f"📊 Parallel execution: {'Smart' if args.parallel else 'Sequential'}")
            self.console.print()

            results = self.run_batch_tests(categories, args.parallel, getattr(args, 'max_parallel', 3))
            self.show_results_summary(results)

            if args.report:
                report_path = self.generate_report(results)
                self.console.print(f"\n📄 Report generated: {report_path}")

            # Exit with appropriate code
            failed = sum(1 for r in results.values() if r["status"] == "error")
            sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    cli = ValidoAITestCLI()
    cli.main()
