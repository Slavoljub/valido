#!/usr/bin/env python3
"""
AI Safety Manager
Provides comprehensive AI safety, guard rails, and context management
"""

import os
import json
import logging
import hashlib
import re
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import sqlite3

logger = logging.getLogger(__name__)

@dataclass
class SafetyViolation:
    """Represents a safety violation"""
    violation_type: str  # 'content_filter', 'rate_limit', 'data_isolation', etc.
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class AIContext:
    """AI context configuration"""
    user_id: Optional[str] = None
    company_id: Optional[str] = None
    session_id: Optional[str] = None
    allowed_topics: List[str] = None
    blocked_topics: List[str] = None
    data_sources: List[str] = None
    custom_rules: List[str] = None
    max_response_length: int = 2048
    temperature: float = 0.7

    def __post_init__(self):
        if self.allowed_topics is None:
            self.allowed_topics = []
        if self.blocked_topics is None:
            self.blocked_topics = []
        if self.data_sources is None:
            self.data_sources = []
        if self.custom_rules is None:
            self.custom_rules = []

class AISafetyManager:
    """Comprehensive AI safety and context management system"""

    def __init__(self, db_path: str = "data/sqlite/app.db"):
        self.db_path = db_path
        self._init_database()

        # Load configuration from environment
        self.safety_enabled = os.getenv('AI_SAFETY_ENABLED', 'true').lower() == 'true'
        self.guard_rails_enabled = os.getenv('AI_GUARD_RAILS_ENABLED', 'true').lower() == 'true'
        self.data_isolation_enabled = os.getenv('AI_DATA_ISOLATION_ENABLED', 'true').lower() == 'true'

        # Content filtering settings
        self.filter_sensitive_data = os.getenv('AI_FILTER_SENSITIVE_DATA', 'true').lower() == 'true'
        self.filter_personal_data = os.getenv('AI_FILTER_PERSONAL_DATA', 'true').lower() == 'true'
        self.filter_financial_data = os.getenv('AI_FILTER_FINANCIAL_DATA', 'false').lower() == 'true'

        # Rate limiting
        self.rate_limit_enabled = os.getenv('AI_RATE_LIMIT_ENABLED', 'true').lower() == 'true'
        self.rate_limit_requests = int(os.getenv('AI_RATE_LIMIT_REQUESTS', '50'))
        self.rate_limit_window = int(os.getenv('AI_RATE_LIMIT_WINDOW', '3600'))

        # Response limits
        self.max_response_length = int(os.getenv('AI_MAX_RESPONSE_LENGTH', '2048'))
        self.max_responses_per_hour = int(os.getenv('AI_MAX_RESPONSES_PER_HOUR', '100'))

        # Load default configurations
        self._load_default_configs()

    def _init_database(self):
        """Initialize safety database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # AI Safety Violations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_safety_violations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        violation_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        message TEXT NOT NULL,
                        details TEXT,
                        user_id TEXT,
                        company_id TEXT,
                        session_id TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # AI Contexts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_contexts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        context_id TEXT UNIQUE NOT NULL,
                        user_id TEXT,
                        company_id TEXT,
                        session_id TEXT,
                        allowed_topics TEXT,  -- JSON array
                        blocked_topics TEXT,  -- JSON array
                        data_sources TEXT,    -- JSON array
                        custom_rules TEXT,    -- JSON array
                        max_response_length INTEGER DEFAULT 2048,
                        temperature REAL DEFAULT 0.7,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # AI Prompts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_prompts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_id TEXT UNIQUE NOT NULL,
                        prompt_type TEXT NOT NULL,  -- 'system', 'greeting', 'rules', 'context'
                        name TEXT NOT NULL,
                        content TEXT NOT NULL,
                        description TEXT,
                        is_default BOOLEAN DEFAULT FALSE,
                        is_active BOOLEAN DEFAULT TRUE,
                        user_id TEXT,
                        company_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # AI Response Logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_response_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_id TEXT,
                        company_id TEXT,
                        model_used TEXT,
                        prompt_tokens INTEGER,
                        response_tokens INTEGER,
                        total_tokens INTEGER,
                        response_time REAL,
                        safety_checks_passed BOOLEAN DEFAULT TRUE,
                        violations_found TEXT,  -- JSON array
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Rate limiting table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_rate_limits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        identifier TEXT NOT NULL,  -- user_id or session_id
                        request_count INTEGER DEFAULT 0,
                        window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(identifier, window_start)
                    );
                """)

                conn.commit()
                logger.info("✅ AI Safety database tables initialized")

        except Exception as e:
            logger.error(f"❌ Error initializing AI Safety database: {e}")

    def _load_default_configs(self):
        """Load default safety configurations"""
        # Default prompts
        self.default_prompts = {
            'system': {
                'name': 'Default System Prompt',
                'content': os.getenv('DEFAULT_PROMPT',
                    'You are a helpful AI assistant specialized in financial analysis and business intelligence for Serbian businesses. You have access to company-specific data and can provide insights, analysis, and recommendations based on the available information. Always maintain confidentiality and provide accurate, relevant information only.'),
                'description': 'Default system prompt for AI assistant',
                'is_default': True
            },
            'greeting': {
                'name': 'Default Greeting',
                'content': os.getenv('DEFAULT_GREETING',
                    '👋 Hello! I\'m your AI financial assistant, powered by local LLM models. I\'m here to help you with financial analysis, business insights, and data-driven recommendations. What would you like to explore today?'),
                'description': 'Default greeting message',
                'is_default': True
            },
            'rules': {
                'name': 'Default Rules',
                'content': os.getenv('AI_RULES',
                    'Be helpful and accurate, maintain data privacy, provide relevant financial insights, use available data sources, protect sensitive information, give actionable recommendations, explain complex topics clearly, ask for clarification when needed, respect Serbian business context and regulations.'),
                'description': 'Default AI behavior rules',
                'is_default': True
            }
        }

        # Default content filters
        self.allowed_topics = os.getenv('AI_ALLOWED_TOPICS', 'finance,accounting,business,intelligence,analysis,reporting').split(',')
        self.blocked_topics = os.getenv('AI_BLOCKED_TOPICS', 'politics,religion,gambling,illegal_activities').split(',')

        # Sensitive data patterns
        self.sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'bank_account': r'\b\d{8,12}\b',
            'address': r'\b\d+\s+[A-Za-z0-9\s,.-]+\b'
        }

    # ==========================================
    # CONTEXT MANAGEMENT
    # ==========================================

    def create_context(self, context_id: str, context_data: Dict[str, Any]) -> bool:
        """Create a new AI context"""
        try:
            context = AIContext(**context_data)
            context_dict = asdict(context)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO ai_contexts
                    (context_id, user_id, company_id, session_id, allowed_topics, blocked_topics,
                     data_sources, custom_rules, max_response_length, temperature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    context_id,
                    context.user_id,
                    context.company_id,
                    context.session_id,
                    json.dumps(context.allowed_topics),
                    json.dumps(context.blocked_topics),
                    json.dumps(context.data_sources),
                    json.dumps(context.custom_rules),
                    context.max_response_length,
                    context.temperature
                ))
                conn.commit()

            return True

        except Exception as e:
            logger.error(f"Error creating context: {e}")
            return False

    def get_context(self, context_id: str) -> Optional[AIContext]:
        """Get AI context by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM ai_contexts WHERE context_id = ?
                """, (context_id,))

                row = cursor.fetchone()
                if row:
                    return AIContext(
                        user_id=row[2],
                        company_id=row[3],
                        session_id=row[4],
                        allowed_topics=json.loads(row[5]) if row[5] else [],
                        blocked_topics=json.loads(row[6]) if row[6] else [],
                        data_sources=json.loads(row[7]) if row[7] else [],
                        custom_rules=json.loads(row[8]) if row[8] else [],
                        max_response_length=row[9],
                        temperature=row[10]
                    )

            return None

        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return None

    def update_context(self, context_id: str, updates: Dict[str, Any]) -> bool:
        """Update AI context"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Build dynamic update query
                update_fields = []
                values = []

                for field, value in updates.items():
                    if field in ['allowed_topics', 'blocked_topics', 'data_sources', 'custom_rules']:
                        value = json.dumps(value)
                    update_fields.append(f"{field} = ?")
                    values.append(value)

                values.append(context_id)

                query = f"""
                    UPDATE ai_contexts
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE context_id = ?
                """

                cursor.execute(query, values)
                conn.commit()

            return True

        except Exception as e:
            logger.error(f"Error updating context: {e}")
            return False

    # ==========================================
    # PROMPT MANAGEMENT
    # ==========================================

    def create_prompt(self, prompt_data: Dict[str, Any]) -> bool:
        """Create a new AI prompt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ai_prompts
                    (prompt_id, prompt_type, name, content, description, is_default, is_active,
                     user_id, company_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prompt_data['prompt_id'],
                    prompt_data['prompt_type'],
                    prompt_data['name'],
                    prompt_data['content'],
                    prompt_data.get('description', ''),
                    prompt_data.get('is_default', False),
                    prompt_data.get('is_active', True),
                    prompt_data.get('user_id'),
                    prompt_data.get('company_id')
                ))
                conn.commit()

            return True

        except Exception as e:
            logger.error(f"Error creating prompt: {e}")
            return False

    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get AI prompt by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM ai_prompts WHERE prompt_id = ? AND is_active = 1
                """, (prompt_id,))

                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'prompt_id': row[1],
                        'prompt_type': row[2],
                        'name': row[3],
                        'content': row[4],
                        'description': row[5],
                        'is_default': bool(row[6]),
                        'is_active': bool(row[7]),
                        'user_id': row[8],
                        'company_id': row[9],
                        'created_at': row[10],
                        'updated_at': row[11]
                    }

            return None

        except Exception as e:
            logger.error(f"Error getting prompt: {e}")
            return None

    def get_default_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Get default prompts"""
        return self.default_prompts.copy()

    def get_system_prompt(self, user_id: Optional[str] = None, company_id: Optional[str] = None) -> str:
        """Get system prompt for user/company"""
        try:
            # Try to get user-specific system prompt
            if user_id:
                user_prompt = self.get_prompt(f"system_{user_id}")
                if user_prompt:
                    return user_prompt['content']

            # Try to get company-specific system prompt
            if company_id:
                company_prompt = self.get_prompt(f"system_{company_id}")
                if company_prompt:
                    return company_prompt['content']

            # Return default system prompt
            return self.default_prompts['system']['content']

        except Exception as e:
            logger.error(f"Error getting system prompt: {e}")
            return self.default_prompts['system']['content']

    def get_greeting_message(self, user_id: Optional[str] = None, company_id: Optional[str] = None) -> str:
        """Get greeting message for user/company"""
        try:
            # Try to get user-specific greeting
            if user_id:
                user_greeting = self.get_prompt(f"greeting_{user_id}")
                if user_greeting:
                    return user_greeting['content']

            # Try to get company-specific greeting
            if company_id:
                company_greeting = self.get_prompt(f"greeting_{company_id}")
                if company_greeting:
                    return company_greeting['content']

            # Return default greeting
            return self.default_prompts['greeting']['content']

        except Exception as e:
            logger.error(f"Error getting greeting: {e}")
            return self.default_prompts['greeting']['content']

    # ==========================================
    # SAFETY & GUARD RAILS
    # ==========================================

    def validate_input(self, input_text: str, context: Optional[AIContext] = None) -> Tuple[bool, List[SafetyViolation]]:
        """Validate user input for safety violations"""
        violations = []

        if not self.safety_enabled:
            return True, violations

        # Check for content filtering
        if self.filter_sensitive_data:
            sensitive_violations = self._check_sensitive_data(input_text)
            violations.extend(sensitive_violations)

        # Check for blocked topics
        if context and context.blocked_topics:
            topic_violations = self._check_blocked_topics(input_text, context.blocked_topics)
            violations.extend(topic_violations)

        # Check rate limits
        if self.rate_limit_enabled and context:
            rate_limit_violations = self._check_rate_limits(context)
            violations.extend(rate_limit_violations)

        # Check for prompt injection
        if os.getenv('AI_PROMPT_INJECTION_PROTECTION', 'true').lower() == 'true':
            injection_violations = self._check_prompt_injection(input_text)
            violations.extend(injection_violations)

        return len(violations) == 0, violations

    def validate_output(self, output_text: str, context: Optional[AIContext] = None) -> Tuple[bool, List[SafetyViolation]]:
        """Validate AI output for safety violations"""
        violations = []

        if not self.guard_rails_enabled:
            return True, violations

        # Check response length
        if len(output_text) > self.max_response_length:
            violations.append(SafetyViolation(
                violation_type='response_length',
                severity='medium',
                message=f'Response length {len(output_text)} exceeds limit {self.max_response_length}'
            ))

        # Check for data isolation
        if self.data_isolation_enabled and context:
            isolation_violations = self._check_data_isolation(output_text, context)
            violations.extend(isolation_violations)

        # Check content filtering on output
        if self.filter_financial_data:
            financial_violations = self._check_financial_data_leakage(output_text)
            violations.extend(financial_violations)

        return len(violations) == 0, violations

    def _check_sensitive_data(self, text: str) -> List[SafetyViolation]:
        """Check for sensitive data patterns"""
        violations = []

        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                violations.append(SafetyViolation(
                    violation_type='sensitive_data',
                    severity='high',
                    message=f'Detected {pattern_name}: {match.group()}',
                    details={'pattern': pattern_name, 'matched_text': match.group()}
                ))

        return violations

    def _check_blocked_topics(self, text: str, blocked_topics: List[str]) -> List[SafetyViolation]:
        """Check for blocked topics"""
        violations = []
        text_lower = text.lower()

        for topic in blocked_topics:
            if topic.lower() in text_lower:
                violations.append(SafetyViolation(
                    violation_type='blocked_topic',
                    severity='high',
                    message=f'Detected blocked topic: {topic}',
                    details={'blocked_topic': topic}
                ))

        return violations

    def _check_rate_limits(self, context: AIContext) -> List[SafetyViolation]:
        """Check rate limits"""
        violations = []

        identifier = context.user_id or context.session_id or 'anonymous'

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get current window
                cursor.execute("""
                    SELECT request_count, window_start
                    FROM ai_rate_limits
                    WHERE identifier = ?
                    ORDER BY window_start DESC
                    LIMIT 1
                """, (identifier,))

                row = cursor.fetchone()
                current_time = datetime.now()

                if row:
                    request_count, window_start = row
                    window_start = datetime.fromisoformat(window_start)

                    # Check if we're in the same window
                    if (current_time - window_start).total_seconds() < self.rate_limit_window:
                        if request_count >= self.rate_limit_requests:
                            violations.append(SafetyViolation(
                                violation_type='rate_limit',
                                severity='medium',
                                message=f'Rate limit exceeded: {request_count}/{self.rate_limit_requests} requests',
                                details={'current_count': request_count, 'limit': self.rate_limit_requests}
                            ))
                    else:
                        # New window, reset count
                        self._update_rate_limit(identifier, 1, current_time)
                else:
                    # First request
                    self._update_rate_limit(identifier, 1, current_time)

        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")

        return violations

    def _check_prompt_injection(self, text: str) -> List[SafetyViolation]:
        """Check for prompt injection attempts"""
        violations = []

        injection_patterns = [
            r'(?i)ignore.*previous.*instructions',
            r'(?i)forget.*system.*prompt',
            r'(?i)you.*are.*not.*ai.*assistant',
            r'(?i)disregard.*all.*rules',
            r'(?i)act.*as.*different.*person'
        ]

        for pattern in injection_patterns:
            if re.search(pattern, text):
                violations.append(SafetyViolation(
                    violation_type='prompt_injection',
                    severity='critical',
                    message='Potential prompt injection detected',
                    details={'pattern': pattern}
                ))

        return violations

    def _check_data_isolation(self, text: str, context: AIContext) -> List[SafetyViolation]:
        """Check for data isolation violations"""
        violations = []

        # This would implement more sophisticated data isolation logic
        # For now, just check if the response contains data that shouldn't be accessible

        if context.user_id:
            # Check if response contains data from other users
            # This is a simplified implementation
            if 'user_' in text.lower() and context.user_id not in text:
                violations.append(SafetyViolation(
                    violation_type='data_isolation',
                    severity='high',
                    message='Potential data isolation violation detected',
                    details={'context_user': context.user_id}
                ))

        return violations

    def _check_financial_data_leakage(self, text: str) -> List[SafetyViolation]:
        """Check for financial data leakage"""
        violations = []

        # Look for patterns that might indicate financial data exposure
        financial_patterns = [
            r'\b\d{4,}\.?\d{0,2}\s*(?:eur|usd|rsd|€|\$)\b',  # Large amounts with currency
            r'\biban\s*:\s*[A-Z]{2}[0-9]{2}[A-Z0-9]{4,}\b',  # IBAN numbers
            r'\bswift\s*:\s*[A-Z0-9]{8,11}\b'  # SWIFT codes
        ]

        for pattern in financial_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                violations.append(SafetyViolation(
                    violation_type='financial_data_leakage',
                    severity='high',
                    message=f'Potential financial data exposure: {match.group()}',
                    details={'pattern': pattern, 'matched_text': match.group()}
                ))

        return violations

    def _update_rate_limit(self, identifier: str, count: int, window_start: datetime):
        """Update rate limit counter"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO ai_rate_limits
                    (identifier, request_count, window_start, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (identifier, count, window_start.isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating rate limit: {e}")

    def log_violation(self, violation: SafetyViolation, context: Optional[AIContext] = None):
        """Log a safety violation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ai_safety_violations
                    (violation_type, severity, message, details, user_id, company_id, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    violation.violation_type,
                    violation.severity,
                    violation.message,
                    json.dumps(violation.details) if violation.details else None,
                    context.user_id if context else None,
                    context.company_id if context else None,
                    context.session_id if context else None
                ))
                conn.commit()

        except Exception as e:
            logger.error(f"Error logging violation: {e}")

    def log_response(self, session_id: str, model_used: str, prompt_tokens: int,
                    response_tokens: int, response_time: float,
                    safety_checks_passed: bool, violations: List[SafetyViolation],
                    context: Optional[AIContext] = None):
        """Log AI response for monitoring"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ai_response_logs
                    (session_id, user_id, company_id, model_used, prompt_tokens,
                     response_tokens, total_tokens, response_time, safety_checks_passed, violations_found)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    context.user_id if context else None,
                    context.company_id if context else None,
                    model_used,
                    prompt_tokens,
                    response_tokens,
                    prompt_tokens + response_tokens,
                    response_time,
                    safety_checks_passed,
                    json.dumps([asdict(v) for v in violations]) if violations else None
                ))
                conn.commit()

        except Exception as e:
            logger.error(f"Error logging response: {e}")

    def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get violation statistics
                cursor.execute("""
                    SELECT violation_type, severity, COUNT(*) as count
                    FROM ai_safety_violations
                    WHERE timestamp >= datetime('now', '-30 days')
                    GROUP BY violation_type, severity
                """)

                violations = cursor.fetchall()

                # Get response statistics
                cursor.execute("""
                    SELECT COUNT(*) as total_responses,
                           AVG(response_time) as avg_response_time,
                           SUM(CASE WHEN safety_checks_passed THEN 1 ELSE 0 END) as safe_responses
                    FROM ai_response_logs
                    WHERE timestamp >= datetime('now', '-24 hours')
                """)

                response_stats = cursor.fetchone()

                return {
                    'violations': [
                        {
                            'type': v[0],
                            'severity': v[1],
                            'count': v[2]
                        } for v in violations
                    ],
                    'response_stats': {
                        'total_responses': response_stats[0] if response_stats else 0,
                        'avg_response_time': response_stats[1] if response_stats else 0,
                        'safe_responses': response_stats[2] if response_stats else 0
                    }
                }

        except Exception as e:
            logger.error(f"Error getting safety stats: {e}")
            return {'error': str(e)}

    def create_default_prompts(self):
        """Create default prompts in database if they don't exist"""
        try:
            for prompt_type, prompt_data in self.default_prompts.items():
                prompt_id = f"default_{prompt_type}"

                # Check if prompt exists
                if not self.get_prompt(prompt_id):
                    prompt_data_copy = prompt_data.copy()
                    prompt_data_copy['prompt_id'] = prompt_id
                    prompt_data_copy['prompt_type'] = prompt_type

                    self.create_prompt(prompt_data_copy)

            logger.info("✅ Default prompts created")

        except Exception as e:
            logger.error(f"Error creating default prompts: {e}")

# Global instance
ai_safety_manager = AISafetyManager()
