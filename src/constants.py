#!/usr/bin/env python3
"""
Constants for ValidoAI Application
Centralized location for all application constants
"""

# Example questions for different categories
EXAMPLE_QUESTIONS = {
    "financial_analysis": [
        "What is my total revenue for the last quarter?",
        "Show me a breakdown of expenses by category",
        "What are my top 5 customers by revenue?",
        "Calculate my profit margin for this year",
        "Which products are performing best?",
        "What is my cash flow trend over the last 6 months?",
        "Show me overdue invoices and their aging",
        "What is my monthly recurring revenue?",
        "Analyze my cost structure and suggest optimizations",
        "What are the seasonal trends in my business?"
    ],
    "business_insights": [
        "What are the main drivers of my business growth?",
        "Identify potential cost savings opportunities",
        "What are the risks in my current financial position?",
        "Suggest ways to improve cash flow",
        "What pricing strategy would maximize my profits?",
        "Analyze my customer acquisition costs",
        "What are the most profitable customer segments?",
        "How can I optimize my inventory management?",
        "What are the key performance indicators I should track?",
        "Suggest strategies for business expansion"
    ],
    "reporting": [
        "Generate a monthly financial summary",
        "Create a profit and loss statement",
        "Show me a balance sheet analysis",
        "Generate a cash flow report",
        "Create a customer profitability report",
        "Show me vendor payment analysis",
        "Generate a tax summary for this year",
        "Create a budget vs actual comparison",
        "Show me a trend analysis for key metrics",
        "Generate a financial forecast for next quarter"
    ],
    "technical": [
        "Explain how to interpret these financial ratios",
        "What does this balance sheet tell me about my business?",
        "How do I calculate return on investment?",
        "What are the key differences between cash and accrual accounting?",
        "Explain the concept of working capital",
        "How do I analyze my break-even point?",
        "What are the implications of these financial trends?",
        "How do I calculate and interpret EBITDA?",
        "What do these cash flow patterns indicate?",
        "How do I assess the financial health of my business?"
    ]
}

# File upload constants
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}

# Database paths
SAMPLE_DB_PATH = "data/sqlite/sample.db"
CHAT_DB_PATH = "data/sqlite/chat-local.db"

# Default model configuration
DEFAULT_MODEL = "qwen3-4b-gguf"
FALLBACK_MODEL = "llama2-7b-chat-gguf"

# API constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Upload paths
UPLOAD_BASE_PATH = "uploads"
CHAT_UPLOAD_PATH = "uploads/chat-local"
TICKET_UPLOAD_PATH = "uploads/tickets"

# Session constants
SESSION_TIMEOUT = 3600  # 1 hour
UUID_PREFIX = "valido-ai-"
