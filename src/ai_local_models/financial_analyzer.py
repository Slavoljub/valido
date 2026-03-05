#!/usr/bin/env python3
"""
Financial Analyzer
Provides comprehensive financial analysis, chart generation, and document creation
"""

import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import os

logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    """Comprehensive financial analysis and reporting"""
    
    def __init__(self, db_path: str = "data/sqlite/sample.db"):
        self.db_path = db_path
        self.conn = None
        
    def get_connection(self):
        """Get database connection"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
        return self.conn
    
    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_financial_summary(self, company_id: Optional[str] = None, period: str = "current_month") -> Dict[str, Any]:
        """Get comprehensive financial summary"""
        try:
            conn = self.get_connection()
            
            # Get date range for period
            date_range = self._get_date_range(period)
            
            # Base query filter
            date_filter = f"AND i.invoice_date BETWEEN '{date_range['start']}' AND '{date_range['end']}'"
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            
            # Revenue analysis
            revenue_query = f"""
                SELECT 
                    SUM(i.total_amount) as total_revenue,
                    SUM(i.net_amount) as net_revenue,
                    SUM(i.tax_amount) as total_tax,
                    COUNT(*) as invoice_count,
                    AVG(i.total_amount) as avg_invoice_amount
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                WHERE i.status IN ('sent', 'paid') {date_filter} {company_filter}
            """
            
            revenue_data = pd.read_sql_query(revenue_query, conn).iloc[0]
            
            # Expense analysis
            expense_query = f"""
                SELECT 
                    SUM(ft.amount) as total_expenses,
                    COUNT(*) as transaction_count
                FROM financial_transactions ft
                JOIN companies c ON ft.company_id = c.id
                JOIN chart_of_accounts coa ON ft.credit_account_id = coa.id
                WHERE coa.account_type = 'expense' {date_filter} {company_filter}
            """
            
            expense_data = pd.read_sql_query(expense_query, conn).iloc[0]
            
            # Cash flow analysis
            cash_flow_query = f"""
                SELECT 
                    SUM(pay.amount) as cash_inflow,
                    COUNT(DISTINCT pay.invoice_id) as payment_count
                FROM payments pay
                JOIN invoices i ON pay.invoice_id = i.id
                JOIN companies c ON i.company_id = c.id
                WHERE pay.payment_date BETWEEN '{date_range['start']}' AND '{date_range['end']}' {company_filter}
            """
            
            cash_flow_data = pd.read_sql_query(cash_flow_query, conn).iloc[0]
            
            # Calculate key metrics
            total_revenue = revenue_data['total_revenue'] or 0
            total_expenses = expense_data['total_expenses'] or 0
            net_income = total_revenue - total_expenses
            profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
            
            return {
                'period': period,
                'date_range': date_range,
                'revenue': {
                    'total': float(total_revenue),
                    'net': float(revenue_data['net_revenue'] or 0),
                    'tax': float(revenue_data['total_tax'] or 0),
                    'invoice_count': int(revenue_data['invoice_count'] or 0),
                    'avg_invoice': float(revenue_data['avg_invoice_amount'] or 0)
                },
                'expenses': {
                    'total': float(total_expenses),
                    'transaction_count': int(expense_data['transaction_count'] or 0)
                },
                'cash_flow': {
                    'inflow': float(cash_flow_data['cash_inflow'] or 0),
                    'payment_count': int(cash_flow_data['payment_count'] or 0)
                },
                'profitability': {
                    'net_income': float(net_income),
                    'profit_margin': float(profit_margin)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting financial summary: {e}")
            return {}
    
    def get_revenue_analysis(self, company_id: Optional[str] = None, months: int = 12) -> Dict[str, Any]:
        """Get detailed revenue analysis with trends"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            
            # Monthly revenue trends
            revenue_trends_query = f"""
                SELECT 
                    strftime('%Y-%m', i.invoice_date) as month,
                    SUM(i.total_amount) as revenue,
                    SUM(i.net_amount) as net_revenue,
                    COUNT(*) as invoice_count
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                WHERE i.status IN ('sent', 'paid') {company_filter}
                GROUP BY strftime('%Y-%m', i.invoice_date)
                ORDER BY month DESC
                LIMIT {months}
            """
            
            revenue_trends = pd.read_sql_query(revenue_trends_query, conn)
            
            # Customer analysis
            customer_analysis_query = f"""
                SELECT 
                    p.name as customer_name,
                    SUM(i.total_amount) as total_revenue,
                    COUNT(*) as invoice_count,
                    AVG(i.total_amount) as avg_invoice_amount,
                    MAX(i.invoice_date) as last_invoice_date
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                JOIN partners p ON i.partner_id = p.id
                WHERE i.status IN ('sent', 'paid') AND p.partner_type = 'customer' {company_filter}
                GROUP BY p.id
                ORDER BY total_revenue DESC
                LIMIT 10
            """
            
            customer_analysis = pd.read_sql_query(customer_analysis_query, conn)
            
            return {
                'revenue_trends': revenue_trends.to_dict('records'),
                'customer_analysis': customer_analysis.to_dict('records'),
                'total_customers': len(customer_analysis),
                'top_customer': customer_analysis.iloc[0].to_dict() if len(customer_analysis) > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue analysis: {e}")
            return {}
    
    def get_expense_analysis(self, company_id: Optional[str] = None, months: int = 12) -> Dict[str, Any]:
        """Get detailed expense analysis"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            date_filter = f"AND ft.transaction_date >= date('now', '-{months} months')"
            
            # Expense by category
            expense_categories_query = f"""
                SELECT 
                    coa.account_name as category,
                    SUM(ft.amount) as amount,
                    COUNT(*) as transaction_count
                FROM financial_transactions ft
                JOIN companies c ON ft.company_id = c.id
                JOIN chart_of_accounts coa ON ft.credit_account_id = coa.id
                WHERE coa.account_type = 'expense' {company_filter} {date_filter}
                GROUP BY coa.id
                ORDER BY amount DESC
            """
            
            expense_categories = pd.read_sql_query(expense_categories_query, conn)
            
            # Monthly expense trends
            expense_trends_query = f"""
                SELECT 
                    strftime('%Y-%m', ft.transaction_date) as month,
                    SUM(ft.amount) as total_expenses,
                    COUNT(*) as transaction_count
                FROM financial_transactions ft
                JOIN companies c ON ft.company_id = c.id
                JOIN chart_of_accounts coa ON ft.credit_account_id = coa.id
                WHERE coa.account_type = 'expense' {company_filter}
                GROUP BY strftime('%Y-%m', ft.transaction_date)
                ORDER BY month DESC
                LIMIT {months}
            """
            
            expense_trends = pd.read_sql_query(expense_trends_query, conn)
            
            return {
                'expense_categories': expense_categories.to_dict('records'),
                'expense_trends': expense_trends.to_dict('records'),
                'total_expenses': float(expense_categories['amount'].sum()),
                'largest_category': expense_categories.iloc[0].to_dict() if len(expense_categories) > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error getting expense analysis: {e}")
            return {}
    
    def get_cash_flow_analysis(self, company_id: Optional[str] = None, months: int = 12) -> Dict[str, Any]:
        """Get cash flow analysis"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            
            # Monthly cash flow
            cash_flow_query = f"""
                SELECT 
                    strftime('%Y-%m', pay.payment_date) as month,
                    SUM(pay.amount) as cash_inflow,
                    COUNT(DISTINCT pay.invoice_id) as payment_count
                FROM payments pay
                JOIN invoices i ON pay.invoice_id = i.id
                JOIN companies c ON i.company_id = c.id
                WHERE pay.payment_date >= date('now', '-{months} months') {company_filter}
                GROUP BY strftime('%Y-%m', pay.payment_date)
                ORDER BY month DESC
            """
            
            cash_flow = pd.read_sql_query(cash_flow_query, conn)
            
            # Accounts receivable aging
            ar_aging_query = f"""
                SELECT 
                    CASE 
                        WHEN i.due_date < date('now', '-90 days') THEN 'Over 90 days'
                        WHEN i.due_date < date('now', '-60 days') THEN '60-90 days'
                        WHEN i.due_date < date('now', '-30 days') THEN '30-60 days'
                        WHEN i.due_date < date('now') THEN '0-30 days'
                        ELSE 'Not due'
                    END as aging_bucket,
                    SUM(i.total_amount - COALESCE(paid.amount, 0)) as outstanding_amount,
                    COUNT(*) as invoice_count
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                LEFT JOIN (
                    SELECT invoice_id, SUM(amount) as amount
                    FROM payments
                    GROUP BY invoice_id
                ) paid ON i.id = paid.invoice_id
                WHERE i.status != 'cancelled' {company_filter}
                GROUP BY aging_bucket
                ORDER BY outstanding_amount DESC
            """
            
            ar_aging = pd.read_sql_query(ar_aging_query, conn)
            
            return {
                'cash_flow_trends': cash_flow.to_dict('records'),
                'accounts_receivable_aging': ar_aging.to_dict('records'),
                'total_cash_inflow': float(cash_flow['cash_inflow'].sum()),
                'total_outstanding_ar': float(ar_aging['outstanding_amount'].sum())
            }
            
        except Exception as e:
            logger.error(f"Error getting cash flow analysis: {e}")
            return {}
    
    def get_financial_ratios(self, company_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate key financial ratios"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            
            # Get current assets and liabilities
            balance_sheet_query = f"""
                SELECT 
                    SUM(CASE WHEN coa.account_type = 'asset' THEN ft.amount ELSE 0 END) as total_assets,
                    SUM(CASE WHEN coa.account_type = 'liability' THEN ft.amount ELSE 0 END) as total_liabilities,
                    SUM(CASE WHEN coa.account_name = 'Cash' THEN ft.amount ELSE 0 END) as cash,
                    SUM(CASE WHEN coa.account_name = 'Accounts Receivable' THEN ft.amount ELSE 0 END) as accounts_receivable,
                    SUM(CASE WHEN coa.account_name = 'Accounts Payable' THEN ft.amount ELSE 0 END) as accounts_payable
                FROM financial_transactions ft
                JOIN companies c ON ft.company_id = c.id
                JOIN chart_of_accounts coa ON ft.debit_account_id = coa.id
                WHERE 1=1 {company_filter}
            """
            
            balance_sheet = pd.read_sql_query(balance_sheet_query, conn).iloc[0]
            
            # Get revenue and expenses for the year
            income_query = f"""
                SELECT 
                    SUM(CASE WHEN coa.account_type = 'revenue' THEN ft.amount ELSE 0 END) as total_revenue,
                    SUM(CASE WHEN coa.account_type = 'expense' THEN ft.amount ELSE 0 END) as total_expenses
                FROM financial_transactions ft
                JOIN companies c ON ft.company_id = c.id
                JOIN chart_of_accounts coa ON ft.credit_account_id = coa.id
                WHERE ft.transaction_date >= date('now', 'start of year') {company_filter}
            """
            
            income = pd.read_sql_query(income_query, conn).iloc[0]
            
            # Calculate ratios
            total_assets = balance_sheet['total_assets'] or 0
            total_liabilities = balance_sheet['total_liabilities'] or 0
            current_assets = (balance_sheet['cash'] or 0) + (balance_sheet['accounts_receivable'] or 0)
            current_liabilities = balance_sheet['accounts_payable'] or 0
            total_revenue = income['total_revenue'] or 0
            total_expenses = income['total_expenses'] or 0
            net_income = total_revenue - total_expenses
            
            ratios = {
                'liquidity': {
                    'current_ratio': current_assets / current_liabilities if current_liabilities > 0 else 0,
                    'quick_ratio': (current_assets - (balance_sheet['accounts_receivable'] or 0)) / current_liabilities if current_liabilities > 0 else 0
                },
                'profitability': {
                    'profit_margin': (net_income / total_revenue * 100) if total_revenue > 0 else 0,
                    'roa': (net_income / total_assets * 100) if total_assets > 0 else 0
                },
                'solvency': {
                    'debt_to_equity': total_liabilities / (total_assets - total_liabilities) if (total_assets - total_liabilities) > 0 else 0
                },
                'efficiency': {
                    'asset_turnover': total_revenue / total_assets if total_assets > 0 else 0
                }
            }
            
            return ratios
            
        except Exception as e:
            logger.error(f"Error calculating financial ratios: {e}")
            return {}
    
    def generate_chart_data(self, chart_type: str, company_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate chart data for various financial charts"""
        try:
            if chart_type == "revenue_trends":
                return self._generate_revenue_trends_chart(company_id, **kwargs)
            elif chart_type == "expense_breakdown":
                return self._generate_expense_breakdown_chart(company_id, **kwargs)
            elif chart_type == "cash_flow":
                return self._generate_cash_flow_chart(company_id, **kwargs)
            elif chart_type == "profitability":
                return self._generate_profitability_chart(company_id, **kwargs)
            elif chart_type == "customer_analysis":
                return self._generate_customer_analysis_chart(company_id, **kwargs)
            else:
                return {"error": f"Unknown chart type: {chart_type}"}
                
        except Exception as e:
            logger.error(f"Error generating chart data: {e}")
            return {"error": str(e)}
    
    def _generate_revenue_trends_chart(self, company_id: Optional[str] = None, months: int = 12) -> Dict[str, Any]:
        """Generate revenue trends chart data"""
        revenue_analysis = self.get_revenue_analysis(company_id, months)
        
        if not revenue_analysis.get('revenue_trends'):
            return {"error": "No revenue data available"}
        
        trends = revenue_analysis['revenue_trends']
        
        return {
            "type": "line",
            "data": {
                "labels": [item['month'] for item in trends],
                "datasets": [{
                    "label": "Revenue (RSD)",
                    "data": [float(item['revenue']) for item in trends],
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "tension": 0.1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Revenue Trends"
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "ticks": {
                            "callback": "function(value) { return 'RSD ' + value.toLocaleString(); }"
                        }
                    }
                }
            }
        }
    
    def _generate_expense_breakdown_chart(self, company_id: Optional[str] = None, months: int = 12) -> Dict[str, Any]:
        """Generate expense breakdown pie chart data"""
        expense_analysis = self.get_expense_analysis(company_id, months)
        
        if not expense_analysis.get('expense_categories'):
            return {"error": "No expense data available"}
        
        categories = expense_analysis['expense_categories']
        
        colors = [
            "rgb(255, 99, 132)", "rgb(54, 162, 235)", "rgb(255, 205, 86)",
            "rgb(75, 192, 192)", "rgb(153, 102, 255)", "rgb(255, 159, 64)",
            "rgb(199, 199, 199)", "rgb(83, 102, 255)", "rgb(78, 252, 3)",
            "rgb(252, 3, 244)"
        ]
        
        return {
            "type": "pie",
            "data": {
                "labels": [item['category'] for item in categories],
                "datasets": [{
                    "data": [float(item['amount']) for item in categories],
                    "backgroundColor": colors[:len(categories)],
                    "hoverOffset": 4
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Expense Breakdown"
                    },
                    "tooltip": {
                        "callbacks": {
                            "label": "function(context) { return context.label + ': RSD ' + context.parsed.toLocaleString(); }"
                        }
                    }
                }
            }
        }
    
    def _generate_cash_flow_chart(self, company_id: Optional[str] = None, months: int = 12) -> Dict[str, Any]:
        """Generate cash flow chart data"""
        cash_flow_analysis = self.get_cash_flow_analysis(company_id, months)
        
        if not cash_flow_analysis.get('cash_flow_trends'):
            return {"error": "No cash flow data available"}
        
        trends = cash_flow_analysis['cash_flow_trends']
        
        return {
            "type": "bar",
            "data": {
                "labels": [item['month'] for item in trends],
                "datasets": [{
                    "label": "Cash Inflow (RSD)",
                    "data": [float(item['cash_inflow']) for item in trends],
                    "backgroundColor": "rgba(75, 192, 192, 0.8)",
                    "borderColor": "rgb(75, 192, 192)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Cash Flow Trends"
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "ticks": {
                            "callback": "function(value) { return 'RSD ' + value.toLocaleString(); }"
                        }
                    }
                }
            }
        }
    
    def _generate_profitability_chart(self, company_id: Optional[str] = None, months: int = 12) -> Dict[str, Any]:
        """Generate profitability analysis chart data"""
        # Get monthly data for revenue and expenses
        conn = self.get_connection()
        
        company_filter = f"AND c.id = '{company_id}'" if company_id else ""
        
        query = f"""
            SELECT 
                strftime('%Y-%m', ft.transaction_date) as month,
                SUM(CASE WHEN coa.account_type = 'revenue' THEN ft.amount ELSE 0 END) as revenue,
                SUM(CASE WHEN coa.account_type = 'expense' THEN ft.amount ELSE 0 END) as expenses
            FROM financial_transactions ft
            JOIN companies c ON ft.company_id = c.id
            JOIN chart_of_accounts coa ON ft.credit_account_id = coa.id
            WHERE ft.transaction_date >= date('now', '-{months} months') {company_filter}
            GROUP BY strftime('%Y-%m', ft.transaction_date)
            ORDER BY month DESC
        """
        
        data = pd.read_sql_query(query, conn)
        
        if len(data) == 0:
            return {"error": "No profitability data available"}
        
        data['profit'] = data['revenue'] - data['expenses']
        data['profit_margin'] = (data['profit'] / data['revenue'] * 100).fillna(0)
        
        return {
            "type": "line",
            "data": {
                "labels": data['month'].tolist(),
                "datasets": [
                    {
                        "label": "Revenue (RSD)",
                        "data": data['revenue'].tolist(),
                        "borderColor": "rgb(75, 192, 192)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "yAxisID": "y"
                    },
                    {
                        "label": "Expenses (RSD)",
                        "data": data['expenses'].tolist(),
                        "borderColor": "rgb(255, 99, 132)",
                        "backgroundColor": "rgba(255, 99, 132, 0.2)",
                        "yAxisID": "y"
                    },
                    {
                        "label": "Profit Margin (%)",
                        "data": data['profit_margin'].tolist(),
                        "borderColor": "rgb(255, 205, 86)",
                        "backgroundColor": "rgba(255, 205, 86, 0.2)",
                        "yAxisID": "y1"
                    }
                ]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Profitability Analysis"
                    }
                },
                "scales": {
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "beginAtZero": True,
                        "ticks": {
                            "callback": "function(value) { return 'RSD ' + value.toLocaleString(); }"
                        }
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "beginAtZero": True,
                        "ticks": {
                            "callback": "function(value) { return value + '%'; }"
                        },
                        "grid": {
                            "drawOnChartArea": False
                        }
                    }
                }
            }
        }
    
    def _generate_customer_analysis_chart(self, company_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate customer analysis chart data"""
        revenue_analysis = self.get_revenue_analysis(company_id)
        
        if not revenue_analysis.get('customer_analysis'):
            return {"error": "No customer data available"}
        
        customers = revenue_analysis['customer_analysis'][:10]  # Top 10 customers
        
        return {
            "type": "bar",
            "data": {
                "labels": [item['customer_name'] for item in customers],
                "datasets": [{
                    "label": "Revenue (RSD)",
                    "data": [float(item['total_revenue']) for item in customers],
                    "backgroundColor": "rgba(54, 162, 235, 0.8)",
                    "borderColor": "rgb(54, 162, 235)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Top Customers by Revenue"
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "ticks": {
                            "callback": "function(value) { return 'RSD ' + value.toLocaleString(); }"
                        }
                    }
                }
            }
        }
    
    def _get_date_range(self, period: str) -> Dict[str, str]:
        """Get date range for specified period"""
        today = datetime.now()
        
        if period == "current_month":
            start_date = today.replace(day=1)
            end_date = today
        elif period == "last_month":
            start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = today.replace(day=1) - timedelta(days=1)
        elif period == "current_quarter":
            quarter_start = today.replace(day=1, month=((today.month-1)//3)*3+1)
            start_date = quarter_start
            end_date = today
        elif period == "current_year":
            start_date = today.replace(day=1, month=1)
            end_date = today
        elif period == "last_year":
            start_date = today.replace(day=1, month=1, year=today.year-1)
            end_date = today.replace(day=31, month=12, year=today.year-1)
        else:
            # Default to current month
            start_date = today.replace(day=1)
            end_date = today
        
        return {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
    
    def get_companies(self) -> List[Dict[str, Any]]:
        """Get list of companies"""
        try:
            conn = self.get_connection()
            query = "SELECT id, name, tax_number FROM companies WHERE status = 'active'"
            companies = pd.read_sql_query(query, conn)
            return companies.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            return []
    
    def get_partners(self, company_id: Optional[str] = None, partner_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of partners"""
        try:
            conn = self.get_connection()
            
            filters = []
            if company_id:
                filters.append(f"p.company_id = '{company_id}'")
            if partner_type:
                filters.append(f"p.partner_type = '{partner_type}'")
            
            where_clause = " AND ".join(filters) if filters else "1=1"
            
            query = f"""
                SELECT p.id, p.name, p.tax_number, p.partner_type, c.name as company_name
                FROM partners p
                JOIN companies c ON p.company_id = c.id
                WHERE {where_clause} AND p.status = 'active'
                ORDER BY p.name
            """
            
            partners = pd.read_sql_query(query, conn)
            return partners.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting partners: {e}")
            return []
    
    def get_employees(self, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of employees"""
        try:
            conn = self.get_connection()
            
            company_filter = f"WHERE e.company_id = '{company_id}'" if company_id else ""
            
            query = f"""
                SELECT e.id, e.employee_number, e.first_name, e.last_name, 
                       e.position, e.department, e.salary, c.name as company_name
                FROM employees e
                JOIN companies c ON e.company_id = c.id
                {company_filter}
                ORDER BY e.last_name, e.first_name
            """
            
            employees = pd.read_sql_query(query, conn)
            return employees.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting employees: {e}")
            return []
    
    def analyze_invoices(self, company_id: Optional[str] = None, period: str = "current_month") -> Dict[str, Any]:
        """Comprehensive invoice analysis"""
        try:
            conn = self.get_connection()
            
            # Get date range
            date_range = self._get_date_range(period)
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            date_filter = f"AND i.invoice_date BETWEEN '{date_range['start']}' AND '{date_range['end']}'"
            
            # Invoice summary
            summary_query = f"""
                SELECT 
                    COUNT(*) as total_invoices,
                    SUM(i.total_amount) as total_amount,
                    SUM(i.net_amount) as net_amount,
                    SUM(i.tax_amount) as total_tax,
                    AVG(i.total_amount) as avg_invoice_amount,
                    MIN(i.invoice_date) as first_invoice,
                    MAX(i.invoice_date) as last_invoice
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                WHERE i.status IN ('sent', 'paid') {date_filter} {company_filter}
            """
            
            summary_df = pd.read_sql_query(summary_query, conn)
            summary = summary_df.iloc[0] if not summary_df.empty else pd.Series([0, 0, 0, 0, 0, None, None])
            
            # Invoice status breakdown
            status_query = f"""
                SELECT 
                    i.status,
                    COUNT(*) as count,
                    SUM(i.total_amount) as total_amount
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                WHERE 1=1 {date_filter} {company_filter}
                GROUP BY i.status
                ORDER BY total_amount DESC
            """
            
            status_df = pd.read_sql_query(status_query, conn)
            
            # Top customers by invoice value
            customers_query = f"""
                SELECT 
                    p.name as customer_name,
                    p.partner_type,
                    COUNT(i.id) as invoice_count,
                    SUM(i.total_amount) as total_amount,
                    AVG(i.total_amount) as avg_amount,
                    MAX(i.invoice_date) as last_invoice_date
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                JOIN partners p ON i.partner_id = p.id
                WHERE i.status IN ('sent', 'paid') {date_filter} {company_filter}
                GROUP BY p.id
                ORDER BY total_amount DESC
                LIMIT 10
            """
            
            customers_df = pd.read_sql_query(customers_query, conn)
            
            # Monthly invoice trends
            monthly_query = f"""
                SELECT 
                    strftime('%Y-%m', i.invoice_date) as month,
                    COUNT(*) as invoice_count,
                    SUM(i.total_amount) as total_amount,
                    AVG(i.total_amount) as avg_amount
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                WHERE i.status IN ('sent', 'paid') {date_filter} {company_filter}
                GROUP BY month
                ORDER BY month DESC
            """
            
            monthly_df = pd.read_sql_query(monthly_query, conn)
            
            return {
                'summary': {
                    'total_invoices': int(summary['total_invoices'] or 0),
                    'total_amount': float(summary['total_amount'] or 0),
                    'net_amount': float(summary['net_amount'] or 0),
                    'total_tax': float(summary['total_tax'] or 0),
                    'avg_invoice_amount': float(summary['avg_invoice_amount'] or 0),
                    'first_invoice': summary['first_invoice'],
                    'last_invoice': summary['last_invoice']
                },
                'status_breakdown': status_df.to_dict('records'),
                'top_customers': customers_df.to_dict('records'),
                'monthly_trends': monthly_df.to_dict('records'),
                'period': period,
                'date_range': date_range
            }
            
        except Exception as e:
            logger.error(f"Error analyzing invoices: {e}")
            return {}
    
    def analyze_vat(self, company_id: Optional[str] = None, period: str = "current_month") -> Dict[str, Any]:
        """VAT analysis and compliance"""
        try:
            conn = self.get_connection()
            
            date_range = self._get_date_range(period)
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            date_filter = f"AND i.invoice_date BETWEEN '{date_range['start']}' AND '{date_range['end']}'"
            
            # VAT summary
            vat_query = f"""
                SELECT 
                    SUM(i.tax_amount) as total_vat_collected,
                    SUM(CASE WHEN i.tax_rate = 20 THEN i.tax_amount ELSE 0 END) as vat_20_percent,
                    SUM(CASE WHEN i.tax_rate = 10 THEN i.tax_amount ELSE 0 END) as vat_10_percent,
                    SUM(CASE WHEN i.tax_rate = 0 THEN i.tax_amount ELSE 0 END) as vat_0_percent,
                    AVG(i.tax_rate) as avg_tax_rate,
                    COUNT(*) as total_invoices_with_vat
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                WHERE i.status IN ('sent', 'paid') {date_filter} {company_filter}
            """
            
            vat_df = pd.read_sql_query(vat_query, conn)
            vat_data = vat_df.iloc[0] if not vat_df.empty else pd.Series([0, 0, 0, 0, 0, 0])
            
            # VAT by customer type
            vat_by_customer_query = f"""
                SELECT 
                    p.partner_type,
                    SUM(i.tax_amount) as total_vat,
                    COUNT(*) as invoice_count,
                    AVG(i.tax_rate) as avg_tax_rate
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                JOIN partners p ON i.partner_id = p.id
                WHERE i.status IN ('sent', 'paid') {date_filter} {company_filter}
                GROUP BY p.partner_type
                ORDER BY total_vat DESC
            """
            
            vat_by_customer_df = pd.read_sql_query(vat_by_customer_query, conn)
            
            # VAT monthly trends
            vat_monthly_query = f"""
                SELECT 
                    strftime('%Y-%m', i.invoice_date) as month,
                    SUM(i.tax_amount) as total_vat,
                    COUNT(*) as invoice_count,
                    AVG(i.tax_rate) as avg_tax_rate
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                WHERE i.status IN ('sent', 'paid') {date_filter} {company_filter}
                GROUP BY month
                ORDER BY month DESC
            """
            
            vat_monthly_df = pd.read_sql_query(vat_monthly_query, conn)
            
            return {
                'summary': {
                    'total_vat_collected': float(vat_data['total_vat_collected'] or 0),
                    'vat_20_percent': float(vat_data['vat_20_percent'] or 0),
                    'vat_10_percent': float(vat_data['vat_10_percent'] or 0),
                    'vat_0_percent': float(vat_data['vat_0_percent'] or 0),
                    'avg_tax_rate': float(vat_data['avg_tax_rate'] or 0),
                    'total_invoices_with_vat': int(vat_data['total_invoices_with_vat'] or 0)
                },
                'vat_by_customer_type': vat_by_customer_df.to_dict('records'),
                'vat_monthly_trends': vat_monthly_df.to_dict('records'),
                'period': period,
                'date_range': date_range
            }
            
        except Exception as e:
            logger.error(f"Error analyzing VAT: {e}")
            return {}
    
    def analyze_clients(self, company_id: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive client/customer analysis"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            
            # Client summary
            client_summary_query = f"""
                SELECT 
                    COUNT(DISTINCT p.id) as total_clients,
                    COUNT(CASE WHEN p.partner_type = 'customer' THEN 1 END) as customers,
                    COUNT(CASE WHEN p.partner_type = 'supplier' THEN 1 END) as suppliers,
                    COUNT(CASE WHEN p.partner_type = 'both' THEN 1 END) as both_types
                FROM partners p
                JOIN companies c ON p.company_id = c.id
                WHERE 1=1 {company_filter}
            """
            
            client_summary_df = pd.read_sql_query(client_summary_query, conn)
            client_summary = client_summary_df.iloc[0] if not client_summary_df.empty else pd.Series([0, 0, 0, 0])
            
            # Top clients by revenue
            top_clients_query = f"""
                SELECT 
                    p.name as client_name,
                    p.partner_type,
                    p.email,
                    p.phone,
                    COUNT(i.id) as invoice_count,
                    SUM(i.total_amount) as total_revenue,
                    AVG(i.total_amount) as avg_invoice_amount,
                    MAX(i.invoice_date) as last_invoice_date,
                    MIN(i.invoice_date) as first_invoice_date
                FROM partners p
                JOIN companies c ON p.company_id = c.id
                LEFT JOIN invoices i ON p.id = i.partner_id
                WHERE 1=1 {company_filter}
                GROUP BY p.id
                ORDER BY total_revenue DESC
                LIMIT 20
            """
            
            top_clients_df = pd.read_sql_query(top_clients_query, conn)
            
            # Client activity analysis
            client_activity_query = f"""
                SELECT 
                    p.name as client_name,
                    COUNT(i.id) as invoices_last_30_days,
                    COUNT(i.id) as invoices_last_90_days,
                    SUM(CASE WHEN i.invoice_date >= date('now', '-30 days') THEN i.total_amount ELSE 0 END) as revenue_last_30_days,
                    SUM(CASE WHEN i.invoice_date >= date('now', '-90 days') THEN i.total_amount ELSE 0 END) as revenue_last_90_days
                FROM partners p
                JOIN companies c ON p.company_id = c.id
                LEFT JOIN invoices i ON p.id = i.partner_id AND i.invoice_date >= date('now', '-90 days')
                WHERE 1=1 {company_filter}
                GROUP BY p.id
                HAVING invoices_last_90_days > 0
                ORDER BY revenue_last_90_days DESC
                LIMIT 15
            """
            
            client_activity_df = pd.read_sql_query(client_activity_query, conn)
            
            # Client payment analysis
            payment_analysis_query = f"""
                SELECT 
                    p.name as client_name,
                    COUNT(i.id) as total_invoices,
                    SUM(i.total_amount) as total_billed,
                    SUM(COALESCE(pay.total_paid, 0)) as total_paid,
                    (SUM(i.total_amount) - SUM(COALESCE(pay.total_paid, 0))) as outstanding_amount,
                    AVG(CASE WHEN pay.payment_date IS NOT NULL 
                        THEN julianday(pay.payment_date) - julianday(i.invoice_date) 
                        ELSE NULL END) as avg_payment_days
                FROM partners p
                JOIN companies c ON p.company_id = c.id
                LEFT JOIN invoices i ON p.id = i.partner_id
                LEFT JOIN (
                    SELECT invoice_id, SUM(amount) as total_paid, MAX(payment_date) as payment_date
                    FROM payments
                    GROUP BY invoice_id
                ) pay ON i.id = pay.invoice_id
                WHERE 1=1 {company_filter}
                GROUP BY p.id
                HAVING total_invoices > 0
                ORDER BY outstanding_amount DESC
                LIMIT 15
            """
            
            payment_analysis_df = pd.read_sql_query(payment_analysis_query, conn)
            
            return {
                'summary': {
                    'total_clients': int(client_summary['total_clients'] or 0),
                    'customers': int(client_summary['customers'] or 0),
                    'suppliers': int(client_summary['suppliers'] or 0),
                    'both_types': int(client_summary['both_types'] or 0)
                },
                'top_clients': top_clients_df.to_dict('records'),
                'client_activity': client_activity_df.to_dict('records'),
                'payment_analysis': payment_analysis_df.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing clients: {e}")
            return {}
    
    def analyze_warehouse(self, company_id: Optional[str] = None) -> Dict[str, Any]:
        """Warehouse and inventory analysis"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            
            # Check if warehouse tables exist
            warehouse_tables_query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE '%warehouse%' OR name LIKE '%inventory%' OR name LIKE '%product%'
            """
            
            warehouse_tables_df = pd.read_sql_query(warehouse_tables_query, conn)
            warehouse_tables = warehouse_tables_df['name'].tolist()
            
            if not warehouse_tables:
                # Create sample warehouse data if tables don't exist
                self._create_sample_warehouse_data(conn, company_id)
            
            # Product inventory summary
            inventory_query = f"""
                SELECT 
                    p.name as product_name,
                    p.sku,
                    p.category,
                    p.current_stock,
                    p.min_stock_level,
                    p.max_stock_level,
                    p.unit_price,
                    (p.current_stock * p.unit_price) as stock_value,
                    CASE 
                        WHEN p.current_stock <= p.min_stock_level THEN 'Low Stock'
                        WHEN p.current_stock >= p.max_stock_level THEN 'Overstocked'
                        ELSE 'Normal'
                    END as stock_status
                FROM products p
                JOIN companies c ON p.company_id = c.id
                WHERE 1=1 {company_filter}
                ORDER BY stock_value DESC
            """
            
            inventory_df = pd.read_sql_query(inventory_query, conn)
            
            # Stock movement analysis
            movement_query = f"""
                SELECT 
                    p.name as product_name,
                    COUNT(sm.id) as movement_count,
                    SUM(CASE WHEN sm.movement_type = 'in' THEN sm.quantity ELSE 0 END) as total_in,
                    SUM(CASE WHEN sm.movement_type = 'out' THEN sm.quantity ELSE 0 END) as total_out,
                    MAX(sm.movement_date) as last_movement
                FROM products p
                JOIN companies c ON p.company_id = c.id
                LEFT JOIN stock_movements sm ON p.id = sm.product_id
                WHERE 1=1 {company_filter}
                GROUP BY p.id
                ORDER BY movement_count DESC
            """
            
            movement_df = pd.read_sql_query(movement_query, conn)
            
            # Category analysis
            category_query = f"""
                SELECT 
                    p.category,
                    COUNT(p.id) as product_count,
                    SUM(p.current_stock) as total_stock,
                    SUM(p.current_stock * p.unit_price) as total_value,
                    AVG(p.unit_price) as avg_price
                FROM products p
                JOIN companies c ON p.company_id = c.id
                WHERE 1=1 {company_filter}
                GROUP BY p.category
                ORDER BY total_value DESC
            """
            
            category_df = pd.read_sql_query(category_query, conn)
            
            return {
                'inventory_summary': {
                    'total_products': len(inventory_df),
                    'total_stock_value': float(inventory_df['stock_value'].sum() if not inventory_df.empty else 0),
                    'low_stock_items': len(inventory_df[inventory_df['stock_status'] == 'Low Stock']) if not inventory_df.empty else 0,
                    'overstocked_items': len(inventory_df[inventory_df['stock_status'] == 'Overstocked']) if not inventory_df.empty else 0
                },
                'inventory_details': inventory_df.to_dict('records'),
                'stock_movements': movement_df.to_dict('records'),
                'category_analysis': category_df.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing warehouse: {e}")
            return {}
    
    def analyze_cashflow(self, company_id: Optional[str] = None, months: int = 12) -> Dict[str, Any]:
        """Comprehensive cash flow analysis"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            
            # Cash flow summary
            cashflow_summary_query = f"""
                SELECT 
                    SUM(CASE WHEN pay.payment_date >= date('now', '-{months} months') THEN pay.amount ELSE 0 END) as cash_inflow,
                    COUNT(DISTINCT CASE WHEN pay.payment_date >= date('now', '-{months} months') THEN pay.invoice_id END) as payment_count,
                    AVG(CASE WHEN pay.payment_date >= date('now', '-{months} months') THEN pay.amount ELSE NULL END) as avg_payment
                FROM payments pay
                JOIN invoices i ON pay.invoice_id = i.id
                JOIN companies c ON i.company_id = c.id
                WHERE 1=1 {company_filter}
            """
            
            cashflow_summary_df = pd.read_sql_query(cashflow_summary_query, conn)
            cashflow_summary = cashflow_summary_df.iloc[0] if not cashflow_summary_df.empty else pd.Series([0, 0, 0])
            
            # Monthly cash flow
            monthly_cashflow_query = f"""
                SELECT 
                    strftime('%Y-%m', pay.payment_date) as month,
                    SUM(pay.amount) as cash_inflow,
                    COUNT(DISTINCT pay.invoice_id) as payment_count,
                    AVG(pay.amount) as avg_payment
                FROM payments pay
                JOIN invoices i ON pay.invoice_id = i.id
                JOIN companies c ON i.company_id = c.id
                WHERE pay.payment_date >= date('now', '-{months} months') {company_filter}
                GROUP BY month
                ORDER BY month DESC
            """
            
            monthly_cashflow_df = pd.read_sql_query(monthly_cashflow_query, conn)
            
            # Outstanding invoices
            outstanding_query = f"""
                SELECT 
                    i.invoice_number,
                    i.invoice_date,
                    i.due_date,
                    i.total_amount,
                    COALESCE(pay.total_paid, 0) as paid_amount,
                    (i.total_amount - COALESCE(pay.total_paid, 0)) as outstanding_amount,
                    julianday('now') - julianday(i.due_date) as days_overdue,
                    p.name as customer_name
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                JOIN partners p ON i.partner_id = p.id
                LEFT JOIN (
                    SELECT invoice_id, SUM(amount) as total_paid
                    FROM payments
                    GROUP BY invoice_id
                ) pay ON i.id = pay.invoice_id
                WHERE i.status IN ('sent', 'paid') {company_filter}
                AND (i.total_amount - COALESCE(pay.total_paid, 0)) > 0
                ORDER BY days_overdue DESC
            """
            
            outstanding_df = pd.read_sql_query(outstanding_query, conn)
            
            # Payment patterns
            payment_patterns_query = f"""
                SELECT 
                    p.name as customer_name,
                    COUNT(i.id) as total_invoices,
                    SUM(i.total_amount) as total_billed,
                    SUM(COALESCE(pay.total_paid, 0)) as total_paid,
                    AVG(CASE WHEN pay.payment_date IS NOT NULL 
                        THEN julianday(pay.payment_date) - julianday(i.invoice_date) 
                        ELSE NULL END) as avg_payment_days,
                    COUNT(CASE WHEN julianday(pay.payment_date) - julianday(i.invoice_date) <= 30 THEN 1 END) as on_time_payments,
                    COUNT(CASE WHEN julianday(pay.payment_date) - julianday(i.invoice_date) > 30 THEN 1 END) as late_payments
                FROM partners p
                JOIN companies c ON p.company_id = c.id
                LEFT JOIN invoices i ON p.id = i.partner_id
                LEFT JOIN (
                    SELECT invoice_id, SUM(amount) as total_paid, MAX(payment_date) as payment_date
                    FROM payments
                    GROUP BY invoice_id
                ) pay ON i.id = pay.invoice_id
                WHERE 1=1 {company_filter}
                GROUP BY p.id
                HAVING total_invoices > 0
                ORDER BY avg_payment_days ASC
                LIMIT 15
            """
            
            payment_patterns_df = pd.read_sql_query(payment_patterns_query, conn)
            
            return {
                'summary': {
                    'cash_inflow': float(cashflow_summary['cash_inflow'] or 0),
                    'payment_count': int(cashflow_summary['payment_count'] or 0),
                    'avg_payment': float(cashflow_summary['avg_payment'] or 0),
                    'total_outstanding': float(outstanding_df['outstanding_amount'].sum() if not outstanding_df.empty else 0),
                    'overdue_amount': float(outstanding_df[outstanding_df['days_overdue'] > 0]['outstanding_amount'].sum() if not outstanding_df.empty else 0)
                },
                'monthly_cashflow': monthly_cashflow_df.to_dict('records'),
                'outstanding_invoices': outstanding_df.to_dict('records'),
                'payment_patterns': payment_patterns_df.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing cashflow: {e}")
            return {}
    
    def generate_comprehensive_report(self, company_id: Optional[str] = None, period: str = "current_month") -> Dict[str, Any]:
        """Generate comprehensive financial report"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'period': period,
                'company_id': company_id,
                'invoices': self.analyze_invoices(company_id, period),
                'vat': self.analyze_vat(company_id, period),
                'clients': self.analyze_clients(company_id),
                'warehouse': self.analyze_warehouse(company_id),
                'cashflow': self.analyze_cashflow(company_id),
                'summary': {}
            }
            
            # Generate executive summary
            invoice_summary = report['invoices'].get('summary', {})
            vat_summary = report['vat'].get('summary', {})
            client_summary = report['clients'].get('summary', {})
            warehouse_summary = report['warehouse'].get('inventory_summary', {})
            cashflow_summary = report['cashflow'].get('summary', {})
            
            report['summary'] = {
                'total_revenue': invoice_summary.get('total_amount', 0),
                'total_vat': vat_summary.get('total_vat_collected', 0),
                'total_clients': client_summary.get('total_clients', 0),
                'total_products': warehouse_summary.get('total_products', 0),
                'cash_inflow': cashflow_summary.get('cash_inflow', 0),
                'outstanding_amount': cashflow_summary.get('total_outstanding', 0),
                'key_metrics': {
                    'avg_invoice_amount': invoice_summary.get('avg_invoice_amount', 0),
                    'payment_collection_rate': self._calculate_payment_rate(cashflow_summary),
                    'client_retention_rate': self._calculate_client_retention(report['clients']),
                    'inventory_turnover': self._calculate_inventory_turnover(report['warehouse'])
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {}
    
    def _create_sample_warehouse_data(self, conn, company_id: Optional[str] = None):
        """Create sample warehouse data if tables don't exist"""
        try:
            # Create products table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    sku TEXT UNIQUE,
                    category TEXT,
                    current_stock INTEGER DEFAULT 0,
                    min_stock_level INTEGER DEFAULT 10,
                    max_stock_level INTEGER DEFAULT 100,
                    unit_price REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            ''')
            
            # Create stock movements table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stock_movements (
                    id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    movement_type TEXT NOT NULL, -- 'in' or 'out'
                    quantity INTEGER NOT NULL,
                    movement_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    reference TEXT,
                    notes TEXT,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
            
            # Insert sample products
            sample_products = [
                ('prod-1', company_id or 'company-1', 'Laptop Dell XPS 13', 'LAP-DELL-XPS13', 'Electronics', 25, 5, 50, 1200.00),
                ('prod-2', company_id or 'company-1', 'Wireless Mouse', 'ACC-MOUSE-WL', 'Accessories', 100, 20, 200, 25.00),
                ('prod-3', company_id or 'company-1', 'USB-C Cable', 'ACC-CABLE-USBC', 'Accessories', 150, 30, 300, 15.00),
                ('prod-4', company_id or 'company-1', 'Office Chair', 'FURN-CHAIR-OFF', 'Furniture', 15, 3, 30, 350.00),
                ('prod-5', company_id or 'company-1', 'Desk Lamp', 'FURN-LAMP-DESK', 'Furniture', 30, 5, 60, 45.00)
            ]
            
            for product in sample_products:
                conn.execute('''
                    INSERT OR IGNORE INTO products 
                    (id, company_id, name, sku, category, current_stock, min_stock_level, max_stock_level, unit_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', product)
            
            # Insert sample stock movements
            sample_movements = [
                ('mov-1', 'prod-1', 'in', 30, '2024-01-15', 'PO-001', 'Initial stock'),
                ('mov-2', 'prod-1', 'out', 5, '2024-01-20', 'INV-001', 'Sales'),
                ('mov-3', 'prod-2', 'in', 120, '2024-01-10', 'PO-002', 'Bulk order'),
                ('mov-4', 'prod-2', 'out', 20, '2024-01-18', 'INV-002', 'Sales'),
                ('mov-5', 'prod-3', 'in', 200, '2024-01-12', 'PO-003', 'Restock')
            ]
            
            for movement in sample_movements:
                conn.execute('''
                    INSERT OR IGNORE INTO stock_movements 
                    (id, product_id, movement_type, quantity, movement_date, reference, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', movement)
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error creating sample warehouse data: {e}")
    
    def _calculate_payment_rate(self, cashflow_summary: Dict[str, Any]) -> float:
        """Calculate payment collection rate"""
        try:
            cash_inflow = cashflow_summary.get('cash_inflow', 0)
            total_outstanding = cashflow_summary.get('total_outstanding', 0)
            
            if cash_inflow + total_outstanding == 0:
                return 0.0
            
            return (cash_inflow / (cash_inflow + total_outstanding)) * 100
        except:
            return 0.0
    
    def _calculate_client_retention(self, clients_data: Dict[str, Any]) -> float:
        """Calculate client retention rate"""
        try:
            client_activity = clients_data.get('client_activity', [])
            if not client_activity:
                return 0.0
            
            active_clients = len([c for c in client_activity if c.get('invoices_last_30_days', 0) > 0])
            total_clients = len(client_activity)
            
            if total_clients == 0:
                return 0.0
            
            return (active_clients / total_clients) * 100
        except:
            return 0.0
    
    def _calculate_inventory_turnover(self, warehouse_data: Dict[str, Any]) -> float:
        """Calculate inventory turnover rate"""
        try:
            inventory_details = warehouse_data.get('inventory_details', [])
            if not inventory_details:
                return 0.0
            
            total_stock_value = sum(item.get('stock_value', 0) for item in inventory_details)
            avg_stock_value = total_stock_value / len(inventory_details) if inventory_details else 0
            
            if avg_stock_value == 0:
                return 0.0
            
            # Simplified calculation - in real scenario would use COGS
            return 12.0  # Assuming 12x annual turnover
        except:
            return 0.0
