#!/usr/bin/env python3
"""
Question Manager for AI Chat System
Manages example questions stored in SQLite database with categories
"""

import os
import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class Question:
    """Question data structure"""
    id: Optional[int] = None
    text: str = ""
    category: str = ""
    expected_response_type: str = ""
    priority: int = 0
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


class QuestionManager:
    """Manages example questions in SQLite database"""

    def __init__(self, db_path: str = "data/sqlite/app.db"):
        """Initialize question manager"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize the database and create tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS question_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    color VARCHAR(20) DEFAULT '#007bff',
                    icon VARCHAR(50) DEFAULT 'fas fa-question-circle',
                    priority INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS example_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    category_id INTEGER,
                    expected_response_type VARCHAR(50) DEFAULT 'analysis',
                    priority INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES question_categories (id) ON DELETE CASCADE
                )
            """)

            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_category ON example_questions(category_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_active ON example_questions(is_active)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_categories_active ON question_categories(is_active)")

            conn.commit()

        # Initialize with default categories and questions if database is empty
        self._init_default_data()

    def _init_default_data(self):
        """Initialize database with default categories and questions"""
        if not self.get_all_categories():
            # Create default categories
            default_categories = [
                {
                    "name": "Financial Analysis",
                    "description": "Questions related to financial analysis, revenue, costs, and profitability",
                    "color": "#28a745",
                    "icon": "fas fa-chart-line",
                    "priority": 1
                },
                {
                    "name": "Business Intelligence",
                    "description": "Questions about clients, products, sales, and business insights",
                    "color": "#007bff",
                    "icon": "fas fa-business-time",
                    "priority": 2
                },
                {
                    "name": "Database Management",
                    "description": "Questions about database health, schema, and optimization",
                    "color": "#6f42c1",
                    "icon": "fas fa-database",
                    "priority": 3
                },
                {
                    "name": "System & AI Management",
                    "description": "Questions about system status, AI models, and performance",
                    "color": "#e83e8c",
                    "icon": "fas fa-cogs",
                    "priority": 4
                },
                {
                    "name": "Customer Service",
                    "description": "Questions about customer support and service optimization",
                    "color": "#fd7e14",
                    "icon": "fas fa-headset",
                    "priority": 5
                },
                {
                    "name": "Marketing & Sales",
                    "description": "Questions about marketing campaigns and sales strategies",
                    "color": "#20c997",
                    "icon": "fas fa-bullhorn",
                    "priority": 6
                },
                {
                    "name": "Operations",
                    "description": "Questions about operational efficiency and processes",
                    "color": "#6c757d",
                    "icon": "fas fa-cog",
                    "priority": 7
                },
                {
                    "name": "Human Resources",
                    "description": "Questions about employee management and HR processes",
                    "color": "#17a2b8",
                    "icon": "fas fa-users",
                    "priority": 8
                }
            ]

            for category in default_categories:
                self.create_category(category["name"], category["description"],
                                   category["color"], category["icon"], category["priority"])

            # Create default questions
            self._init_default_questions()

    def _init_default_questions(self):
        """Initialize database with comprehensive default questions"""
        default_questions = [
            # Financial Analysis (Category 1)
            ("📊 Analyze my revenue trends and provide insights", 1, "analysis", 10),
            ("💰 Show cash flow analysis for the last quarter", 1, "analysis", 9),
            ("🧾 Analyze VAT and tax implications", 1, "analysis", 8),
            ("📈 Calculate profit margins and identify opportunities", 1, "calculation", 7),
            ("⚖️ Calculate break-even analysis", 1, "calculation", 6),
            ("📊 Calculate key financial ratios", 1, "calculation", 5),
            ("💹 Show monthly revenue growth rate", 1, "analysis", 4),
            ("💰 Analyze expense patterns and cost optimization", 1, "analysis", 3),
            ("📋 Generate quarterly financial summary", 1, "report", 2),
            ("🔍 Identify financial anomalies and outliers", 1, "analysis", 1),

            # Business Intelligence (Category 2)
            ("🏆 What are the best clients and selling products?", 2, "analysis", 10),
            ("👥 Analyze client performance and trends", 2, "analysis", 9),
            ("🔄 Analyze sales pipeline and conversion rates", 2, "analysis", 8),
            ("💰 Calculate customer lifetime value", 2, "calculation", 7),
            ("🏷️ Calculate brand value and equity", 2, "analysis", 6),
            ("📊 Identify top performing product categories", 2, "analysis", 5),
            ("👥 Segment customers by purchasing behavior", 2, "analysis", 4),
            ("📈 Analyze seasonal sales patterns", 2, "analysis", 3),
            ("🎯 Calculate customer acquisition cost", 2, "calculation", 2),
            ("💼 Generate client portfolio analysis", 2, "report", 1),

            # Database Management (Category 3)
            ("🗄️ Check database connection health", 3, "status", 10),
            ("📋 Show database schema and tables", 3, "schema", 9),
            ("⚡ Optimize database performance", 3, "optimization", 8),
            ("🔒 Review database security settings", 3, "security", 7),
            ("🔍 Analyze query performance and bottlenecks", 3, "analysis", 6),
            ("💾 Check database backup status and schedule", 3, "status", 5),
            ("📊 Monitor database growth and storage usage", 3, "analysis", 4),
            ("🔄 Check data synchronization status", 3, "status", 3),
            ("🛠️ Identify and suggest database indexing improvements", 3, "optimization", 2),
            ("📈 Generate database performance report", 3, "report", 1),

            # System & AI Management (Category 4)
            ("🖥️ Show system status and resource usage", 4, "status", 10),
            ("🤖 Check AI model loading and status", 4, "status", 9),
            ("🧠 Analyze memory usage and optimization", 4, "analysis", 8),
            ("💾 Check cache performance and hit rates", 4, "performance", 7),
            ("🔍 Analyze system errors and logs", 4, "analysis", 6),
            ("⚡ Monitor CPU and GPU utilization", 4, "status", 5),
            ("🌐 Check network connectivity and latency", 4, "status", 4),
            ("📊 Generate system performance metrics", 4, "report", 3),
            ("🔧 Analyze disk usage and I/O performance", 4, "analysis", 2),
            ("⚠️ Monitor system alerts and notifications", 4, "status", 1),

            # Customer Service (Category 5)
            ("📞 Analyze customer service response times", 5, "analysis", 10),
            ("⭐ Calculate customer satisfaction scores", 5, "calculation", 9),
            ("📋 Identify common customer issues and solutions", 5, "analysis", 8),
            ("⏱️ Monitor customer support ticket resolution rates", 5, "analysis", 7),
            ("📊 Generate customer service performance report", 5, "report", 6),
            ("🎯 Identify customer service training needs", 5, "analysis", 5),
            ("📈 Analyze customer feedback trends", 5, "analysis", 4),
            ("💬 Calculate average customer conversation length", 5, "calculation", 3),
            ("🔄 Monitor customer service channel performance", 5, "analysis", 2),
            ("🏆 Identify top customer service representatives", 5, "analysis", 1),

            # Marketing & Sales (Category 6)
            ("📢 Analyze marketing campaign performance", 6, "analysis", 10),
            ("🎯 Calculate marketing ROI and attribution", 6, "calculation", 9),
            ("📊 Identify best performing marketing channels", 6, "analysis", 8),
            ("💰 Calculate sales conversion funnel metrics", 6, "calculation", 7),
            ("📈 Analyze lead generation and nurturing", 6, "analysis", 6),
            ("🎨 Monitor brand awareness and sentiment", 6, "analysis", 5),
            ("📋 Generate marketing and sales pipeline report", 6, "report", 4),
            ("🔍 Identify marketing content engagement rates", 6, "analysis", 3),
            ("💎 Calculate customer acquisition cost by channel", 6, "calculation", 2),
            ("🎪 Analyze promotional campaign effectiveness", 6, "analysis", 1),

            # Operations (Category 7)
            ("⚙️ Analyze operational efficiency metrics", 7, "analysis", 10),
            ("🔄 Monitor supply chain performance", 7, "analysis", 9),
            ("📦 Calculate inventory turnover and optimization", 7, "calculation", 8),
            ("🏭 Analyze production line efficiency", 7, "analysis", 7),
            ("🚚 Monitor delivery and logistics performance", 7, "analysis", 6),
            ("📊 Generate operational performance dashboard", 7, "report", 5),
            ("🔧 Identify process bottlenecks and improvements", 7, "analysis", 4),
            ("⚡ Calculate operational cost per unit", 7, "calculation", 3),
            ("📈 Analyze quality control and defect rates", 7, "analysis", 2),
            ("🏆 Monitor key performance indicators (KPIs)", 7, "analysis", 1),

            # Human Resources (Category 8)
            ("👥 Analyze employee performance metrics", 8, "analysis", 10),
            ("📊 Calculate employee engagement and satisfaction", 8, "calculation", 9),
            ("🎓 Monitor training and development effectiveness", 8, "analysis", 8),
            ("💰 Analyze compensation and benefits structure", 8, "analysis", 7),
            ("📈 Calculate employee retention and turnover rates", 8, "calculation", 6),
            ("🔄 Monitor recruitment and hiring pipeline", 8, "analysis", 5),
            ("📋 Generate HR performance and compliance report", 8, "report", 4),
            ("⚖️ Analyze workplace diversity and inclusion", 8, "analysis", 3),
            ("🏥 Monitor employee health and wellness programs", 8, "analysis", 2),
            ("🎯 Calculate training ROI and effectiveness", 8, "calculation", 1)
        ]

        for text, category_id, response_type, priority in default_questions:
            self.create_question(text, category_id, response_type, priority)

    # Category CRUD Operations
    def create_category(self, name: str, description: str = "", color: str = "#007bff",
                       icon: str = "fas fa-question-circle", priority: int = 0) -> int:
        """Create a new question category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO question_categories (name, description, color, icon, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (name, description, color, icon, priority))
            conn.commit()
            return cursor.lastrowid

    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all question categories"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM question_categories
                WHERE is_active = 1
                ORDER BY priority ASC, name ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_category(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific category by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM question_categories WHERE id = ?
            """, (category_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_category(self, category_id: int, name: str, description: str = "",
                       color: str = "#007bff", icon: str = "fas fa-question-circle",
                       priority: int = 0) -> bool:
        """Update a category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE question_categories
                SET name = ?, description = ?, color = ?, icon = ?, priority = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, description, color, icon, priority, category_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_category(self, category_id: int) -> bool:
        """Soft delete a category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE question_categories
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (category_id,))
            conn.commit()
            return cursor.rowcount > 0

    # Question CRUD Operations
    def create_question(self, text: str, category_id: int, expected_response_type: str = "analysis",
                       priority: int = 0) -> int:
        """Create a new question"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO example_questions (text, category_id, expected_response_type, priority)
                VALUES (?, ?, ?, ?)
            """, (text, category_id, expected_response_type, priority))
            conn.commit()
            return cursor.lastrowid

    def get_all_questions(self) -> List[Dict[str, Any]]:
        """Get all questions with category information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT q.*, c.name as category_name, c.color as category_color,
                       c.icon as category_icon
                FROM example_questions q
                JOIN question_categories c ON q.category_id = c.id
                WHERE q.is_active = 1 AND c.is_active = 1
                ORDER BY c.priority ASC, q.priority DESC, q.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_questions_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        """Get questions for a specific category"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT q.*, c.name as category_name, c.color as category_color,
                       c.icon as category_icon
                FROM example_questions q
                JOIN question_categories c ON q.category_id = c.id
                WHERE q.category_id = ? AND q.is_active = 1 AND c.is_active = 1
                ORDER BY q.priority DESC, q.created_at DESC
            """, (category_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific question by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT q.*, c.name as category_name, c.color as category_color,
                       c.icon as category_icon
                FROM example_questions q
                JOIN question_categories c ON q.category_id = c.id
                WHERE q.id = ? AND q.is_active = 1 AND c.is_active = 1
            """, (question_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_question(self, question_id: int, text: str, category_id: int,
                       expected_response_type: str = "analysis", priority: int = 0) -> bool:
        """Update a question"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE example_questions
                SET text = ?, category_id = ?, expected_response_type = ?, priority = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (text, category_id, expected_response_type, priority, question_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_question(self, question_id: int) -> bool:
        """Soft delete a question"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE example_questions
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (question_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_questions_for_chat(self, category: str = "all", limit: int = 50) -> List[Dict[str, Any]]:
        """Get questions formatted for chat interface"""
        if category == "all":
            questions = self.get_all_questions()
        else:
            # Find category by name
            categories = self.get_all_categories()
            category_id = None
            for cat in categories:
                if cat['name'].lower() == category.lower():
                    category_id = cat['id']
                    break

            if category_id:
                questions = self.get_questions_by_category(category_id)
            else:
                questions = []

        # Limit results and format for chat
        return [
            {
                "id": q['id'],
                "text": q['text'],
                "category": q['category_name'],
                "expected_type": q['expected_response_type'],
                "priority": q['priority']
            }
            for q in questions[:limit]
        ]

    def get_category_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for each category"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT c.id, c.name, c.color, c.icon, c.description,
                       COUNT(q.id) as question_count
                FROM question_categories c
                LEFT JOIN example_questions q ON c.id = q.category_id AND q.is_active = 1
                WHERE c.is_active = 1
                GROUP BY c.id, c.name, c.color, c.icon, c.description
                ORDER BY c.priority ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def search_questions(self, search_term: str, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search questions by text"""
        query = """
            SELECT q.*, c.name as category_name, c.color as category_color,
                   c.icon as category_icon
            FROM example_questions q
            JOIN question_categories c ON q.category_id = c.id
            WHERE q.is_active = 1 AND c.is_active = 1
            AND LOWER(q.text) LIKE LOWER(?)
        """
        params = [f"%{search_term}%"]

        if category_id:
            query += " AND q.category_id = ?"
            params.append(category_id)

        query += " ORDER BY q.priority DESC, q.created_at DESC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def bulk_import_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk import questions from a list"""
        success_count = 0
        error_count = 0
        errors = []

        with sqlite3.connect(self.db_path) as conn:
            for question in questions:
                try:
                    self.create_question(
                        text=question['text'],
                        category_id=question['category_id'],
                        expected_response_type=question.get('expected_response_type', 'analysis'),
                        priority=question.get('priority', 0)
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"Error importing '{question.get('text', 'Unknown')}': {str(e)}")

            conn.commit()

        return {
            "success": success_count,
            "errors": error_count,
            "error_messages": errors
        }


# Global instance
question_manager = QuestionManager()
