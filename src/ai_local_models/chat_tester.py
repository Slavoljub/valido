#!/usr/bin/env python3
"""
AI Chat Question Testing System
Tests all sample questions against database data with real AI responses
"""

import os
import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import time

from .database_manager import db_manager
from .chat_engine import AdvancedChatEngine
from .data_integrator import DataIntegrator
from .env_loader import get_env_config

logger = logging.getLogger(__name__)

@dataclass
class QuestionTestResult:
    """Result of testing a single question"""
    question_id: str
    question_text: str
    category: str
    expected_response_type: str
    actual_response: str
    response_time: float
    database_used: str
    data_found: bool
    ai_processing_success: bool
    error_message: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class QuestionTestSuite:
    """Complete test suite for AI chat questions"""
    test_id: str
    total_questions: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_response_time: float
    database_connections_tested: List[str]
    test_results: List[QuestionTestResult]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_questions == 0:
            return 0.0
        return (self.passed_tests / self.total_questions) * 100

    @property
    def average_response_time(self) -> float:
        """Calculate average response time"""
        if self.passed_tests == 0:
            return 0.0
        return self.total_response_time / self.passed_tests

class AIChatTester:
    """Advanced AI Chat Question Testing System"""

    def __init__(self):
        """Initialize the AI chat tester"""
        self.env_config = get_env_config()
        self.chat_engine = AdvancedChatEngine()
        self.data_integrator = DataIntegrator()
        self.sample_questions = self._load_sample_questions()
        self.test_history: List[QuestionTestSuite] = []

    def _load_sample_questions(self) -> List[Dict[str, Any]]:
        """Load sample questions from database"""
        try:
            from .question_manager import question_manager
            return question_manager.get_questions_for_chat("all", 50)
        except Exception as e:
            logger.error(f"Error loading questions from database: {e}")
            # Fallback to empty list if database is not available
            return []

    def load_database_context(self, database_name: str) -> Dict[str, Any]:
        """Load relevant data from specified database for AI context"""
        try:
            context = {
                "database_name": database_name,
                "tables": [],
                "sample_data": {},
                "schema_info": {},
                "connection_status": "unknown"
            }

            # Test connection
            connection = db_manager.get_connection(database_name)
            if not connection:
                context["connection_status"] = "failed"
                return context

            context["connection_status"] = "connected"

            # Get table information based on database type
            if database_name in ['main', 'sqlite']:
                # SQLite database
                tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
                tables = connection.query(tables_query)

                for table in tables:
                    table_name = table['name'] if isinstance(table, dict) else table[0]
                    context["tables"].append(table_name)

                    # Get sample data (first 5 rows)
                    try:
                        sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                        sample_data = connection.query(sample_query)
                        context["sample_data"][table_name] = sample_data

                        # Get schema info
                        schema_query = f"PRAGMA table_info({table_name})"
                        schema_info = connection.query(schema_query)
                        context["schema_info"][table_name] = schema_info
                    except Exception as e:
                        logger.warning(f"Error getting data for table {table_name}: {e}")

            elif database_name in ['postgresql', 'embeddings']:
                # PostgreSQL database
                tables_query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                tables = connection.query(tables_query)

                for table in tables:
                    table_name = table['tablename'] if isinstance(table, dict) else table[0]
                    context["tables"].append(table_name)

                    # Get sample data
                    try:
                        sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                        sample_data = connection.query(sample_query)
                        context["sample_data"][table_name] = sample_data

                        # Get schema info
                        schema_query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
                        schema_info = connection.query(schema_query)
                        context["schema_info"][table_name] = schema_info
                    except Exception as e:
                        logger.warning(f"Error getting data for table {table_name}: {e}")

            return context

        except Exception as e:
            logger.error(f"Error loading database context for {database_name}: {e}")
            return {"database_name": database_name, "connection_status": "error", "error": str(e)}

    def generate_ai_response(self, question: Dict[str, Any], database_contexts: Dict[str, Dict]) -> str:
        """Generate AI response based on question and database context"""
        try:
            question_text = question['text']
            category = question['category']

            # Build context from all databases
            combined_context = {
                "question": question_text,
                "category": category,
                "databases": database_contexts,
                "available_data": {}
            }

            # Extract relevant data based on question category
            if category == "financial":
                combined_context["available_data"] = self._extract_financial_data(database_contexts)
            elif category == "business":
                combined_context["available_data"] = self._extract_business_data(database_contexts)
            elif category == "database":
                combined_context["available_data"] = self._extract_database_data(database_contexts)
            elif category == "system":
                combined_context["available_data"] = self._extract_system_data(database_contexts)

            # Generate response using the chat engine
            response = self.chat_engine.generate_response_with_context(question_text, combined_context)

            return response

        except Exception as e:
            logger.error(f"Error generating AI response for question {question['id']}: {e}")
            return f"Error generating response: {str(e)}"

    def _extract_financial_data(self, database_contexts: Dict[str, Dict]) -> Dict[str, Any]:
        """Extract financial data from database contexts"""
        financial_data = {
            "revenue_data": [],
            "invoice_data": [],
            "payment_data": [],
            "client_data": [],
            "tax_data": []
        }

        for db_name, context in database_contexts.items():
            if context.get("connection_status") != "connected":
                continue

            sample_data = context.get("sample_data", {})

            # Look for financial tables
            for table_name, data in sample_data.items():
                table_lower = table_name.lower()
                if any(keyword in table_lower for keyword in ['invoice', 'payment', 'revenue', 'sale']):
                    if 'invoice' in table_lower:
                        financial_data["invoice_data"].extend(data)
                    elif 'payment' in table_lower:
                        financial_data["payment_data"].extend(data)
                    elif 'revenue' in table_lower or 'sale' in table_lower:
                        financial_data["revenue_data"].extend(data)

                if any(keyword in table_lower for keyword in ['client', 'customer', 'partner']):
                    financial_data["client_data"].extend(data)

                if any(keyword in table_lower for keyword in ['tax', 'vat', 'pdv']):
                    financial_data["tax_data"].extend(data)

        return financial_data

    def _extract_business_data(self, database_contexts: Dict[str, Dict]) -> Dict[str, Any]:
        """Extract business data from database contexts"""
        business_data = {
            "client_data": [],
            "product_data": [],
            "sales_data": [],
            "warehouse_data": []
        }

        for db_name, context in database_contexts.items():
            if context.get("connection_status") != "connected":
                continue

            sample_data = context.get("sample_data", {})

            for table_name, data in sample_data.items():
                table_lower = table_name.lower()
                if any(keyword in table_lower for keyword in ['client', 'customer', 'partner']):
                    business_data["client_data"].extend(data)
                elif any(keyword in table_lower for keyword in ['product', 'item', 'service']):
                    business_data["product_data"].extend(data)
                elif any(keyword in table_lower for keyword in ['sale', 'order', 'invoice']):
                    business_data["sales_data"].extend(data)
                elif any(keyword in table_lower for keyword in ['warehouse', 'stock', 'inventory']):
                    business_data["warehouse_data"].extend(data)

        return business_data

    def _extract_database_data(self, database_contexts: Dict[str, Dict]) -> Dict[str, Any]:
        """Extract database metadata from contexts"""
        database_data = {
            "schema_info": {},
            "table_counts": {},
            "connection_status": {}
        }

        for db_name, context in database_contexts.items():
            database_data["connection_status"][db_name] = context.get("connection_status", "unknown")
            database_data["schema_info"][db_name] = context.get("schema_info", {})
            database_data["table_counts"][db_name] = len(context.get("tables", []))

        return database_data

    def _extract_system_data(self, database_contexts: Dict[str, Dict]) -> Dict[str, Any]:
        """Extract system-related data from contexts"""
        system_data = {
            "database_health": {},
            "table_statistics": {},
            "connection_info": {}
        }

        for db_name, context in database_contexts.items():
            system_data["database_health"][db_name] = context.get("connection_status", "unknown")
            system_data["table_statistics"][db_name] = {
                "table_count": len(context.get("tables", [])),
                "tables": context.get("tables", [])
            }
            system_data["connection_info"][db_name] = {
                "status": context.get("connection_status", "unknown"),
                "type": db_manager.configs.get(db_name, {}).get("type", "unknown") if db_name in db_manager.configs else "unknown"
            }

        return system_data

    def test_single_question(self, question: Dict[str, Any], database_contexts: Dict[str, Dict]) -> QuestionTestResult:
        """Test a single question against the AI system"""
        start_time = time.time()

        try:
            # Generate AI response
            response = self.generate_ai_response(question, database_contexts)

            # Check if response is meaningful
            has_data = len(response) > 50 and not response.startswith("Error")
            processing_success = not response.startswith("Error")

            response_time = time.time() - start_time

            return QuestionTestResult(
                question_id=question['id'],
                question_text=question['text'],
                category=question['category'],
                expected_response_type=question['expected_type'],
                actual_response=response,
                response_time=response_time,
                database_used=", ".join(database_contexts.keys()),
                data_found=has_data,
                ai_processing_success=processing_success
            )

        except Exception as e:
            response_time = time.time() - start_time
            return QuestionTestResult(
                question_id=question['id'],
                question_text=question['text'],
                category=question['category'],
                expected_response_type=question['expected_type'],
                actual_response="",
                response_time=response_time,
                database_used=", ".join(database_contexts.keys()),
                data_found=False,
                ai_processing_success=False,
                error_message=str(e)
            )

    def run_complete_test_suite(self, databases_to_test: List[str] = None) -> QuestionTestSuite:
        """Run complete test suite for all questions"""
        if databases_to_test is None:
            databases_to_test = ['main', 'sqlite']  # Default to main databases

        logger.info(f"Starting AI Chat Question Test Suite with databases: {databases_to_test}")

        # Load database contexts
        database_contexts = {}
        for db_name in databases_to_test:
            logger.info(f"Loading context for database: {db_name}")
            context = self.load_database_context(db_name)
            database_contexts[db_name] = context

        # Test each question
        test_results = []
        total_response_time = 0.0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0

        for question in self.sample_questions:
            logger.info(f"Testing question: {question['id']}")

            result = self.test_single_question(question, database_contexts)
            test_results.append(result)

            total_response_time += result.response_time

            if result.ai_processing_success and result.data_found:
                passed_tests += 1
            elif result.error_message:
                failed_tests += 1
            else:
                skipped_tests += 1

        # Create test suite result
        test_suite = QuestionTestSuite(
            test_id=f"ai_chat_test_{int(time.time())}",
            total_questions=len(self.sample_questions),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            total_response_time=total_response_time,
            database_connections_tested=databases_to_test,
            test_results=test_results
        )

        # Store in history
        self.test_history.append(test_suite)

        logger.info(".2f"
        return test_suite

    def generate_test_report(self, test_suite: QuestionTestSuite) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        report = {
            "test_suite": asdict(test_suite),
            "summary": {
                "success_rate": test_suite.success_rate,
                "average_response_time": test_suite.average_response_time,
                "total_questions": test_suite.total_questions,
                "passed": test_suite.passed_tests,
                "failed": test_suite.failed_tests,
                "skipped": test_suite.skipped_tests
            },
            "category_breakdown": {},
            "failed_questions": [],
            "successful_questions": []
        }

        # Category breakdown
        for result in test_suite.test_results:
            if result.category not in report["category_breakdown"]:
                report["category_breakdown"][result.category] = {
                    "total": 0, "passed": 0, "failed": 0, "avg_time": 0.0
                }

            cat_stats = report["category_breakdown"][result.category]
            cat_stats["total"] += 1
            if result.ai_processing_success and result.data_found:
                cat_stats["passed"] += 1
            else:
                cat_stats["failed"] += 1
            cat_stats["avg_time"] += result.response_time

        # Calculate average times
        for cat_stats in report["category_breakdown"].values():
            if cat_stats["total"] > 0:
                cat_stats["avg_time"] /= cat_stats["total"]

        # Separate failed and successful questions
        for result in test_suite.test_results:
            if result.ai_processing_success and result.data_found:
                report["successful_questions"].append(asdict(result))
            else:
                report["failed_questions"].append(asdict(result))

        return report

    def save_test_report(self, test_suite: QuestionTestSuite, output_path: str = "data/test_reports"):
        """Save test report to file"""
        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            report = self.generate_test_report(test_suite)

            # Save JSON report
            json_path = output_dir / f"ai_chat_test_{test_suite.test_id}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            # Save HTML report
            html_path = output_dir / f"ai_chat_test_{test_suite.test_id}.html"
            html_report = self._generate_html_report(report)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_report)

            logger.info(f"Test reports saved: {json_path}, {html_path}")
            return str(json_path)

        except Exception as e:
            logger.error(f"Error saving test report: {e}")
            return None

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML test report"""
        html = ".2f"".2f"f"""
        <html>
        <head>
            <title>AI Chat Question Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f0f0f0; padding: 20px; margin: 20px 0; }}
                .category {{ background: #e8f4f8; padding: 15px; margin: 10px 0; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
                .question {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>AI Chat Question Test Report</h1>

            <div class="summary">
                <h2>Test Summary</h2>
                <p><strong>Test ID:</strong> {report['test_suite']['test_id']}</p>
                <p><strong>Success Rate:</strong> <span class="{'success' if report['summary']['success_rate'] >= 80 else 'failure'}">{report['summary']['success_rate']:.2f}%</span></p>
                <p><strong>Total Questions:</strong> {report['summary']['total_questions']}</p>
                <p><strong>Passed:</strong> <span class="success">{report['summary']['passed']}</span></p>
                <p><strong>Failed:</strong> <span class="failure">{report['summary']['failed']}</span></p>
                <p><strong>Average Response Time:</strong> {report['summary']['average_response_time']:.2f}s</p>
                <p><strong>Databases Tested:</strong> {', '.join(report['test_suite']['database_connections_tested'])}</p>
            </div>

            <h2>Category Breakdown</h2>
            <table>
                <tr>
                    <th>Category</th>
                    <th>Total</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Avg Time (s)</th>
                    <th>Success Rate</th>
                </tr>
        """

        for category, stats in report["category_breakdown"].items():
            success_rate = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            html += ".2f"".2f"f"""
                <tr>
                    <td>{category.title()}</td>
                    <td>{stats['total']}</td>
                    <td class="success">{stats['passed']}</td>
                    <td class="failure">{stats['failed']}</td>
                    <td>{stats['avg_time']:.2f}</td>
                    <td><span class="{'success' if success_rate >= 80 else 'failure'}">{success_rate:.2f}%</span></td>
                </tr>
            """

        html += """
            </table>

            <h2>Failed Questions</h2>
        """

        for question in report["failed_questions"]:
            html += ".2f"".2f"f"""
            <div class="question failure">
                <h3>{question['question_id']} - {question['category']}</h3>
                <p><strong>Question:</strong> {question['question_text']}</p>
                <p><strong>Error:</strong> {question.get('error_message', 'Unknown error')}</p>
                <p><strong>Response Time:</strong> {question['response_time']:.2f}s</p>
                <p><strong>Database Used:</strong> {question['database_used']}</p>
            </div>
        """

        html += """
            <h2>Successful Questions</h2>
        """

        for question in report["successful_questions"]:
            html += ".2f"".2f"f"""
            <div class="question success">
                <h3>{question['question_id']} - {question['category']}</h3>
                <p><strong>Question:</strong> {question['question_text']}</p>
                <p><strong>Response:</strong> {question['actual_response'][:200]}{'...' if len(question['actual_response']) > 200 else ''}</p>
                <p><strong>Response Time:</strong> {question['response_time']:.2f}s</p>
                <p><strong>Database Used:</strong> {question['database_used']}</p>
            </div>
        """

        html += """
        </body>
        </html>
        """

        return html

# Global instance
chat_tester = AIChatTester()
