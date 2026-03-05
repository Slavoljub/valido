#!/usr/bin/env python3
"""
Context Provider
Provides financial data context from the sample database to enhance AI responses
"""

import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

class FinancialContextProvider:
    """Provides financial data context for AI chat responses"""
    
    def __init__(self, db_path: str = "data/sqlite/sample.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_companies(self) -> List[Dict[str, Any]]:
        """Get list of companies"""
        try:
            conn = self.get_connection()
            query = """
                SELECT id, name, tax_number, address, phone, email, website, registration_date
                FROM companies
                ORDER BY name
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            return []
    
    def get_financial_summary(self, company_id: Optional[str] = None, period: str = "current_month") -> Dict[str, Any]:
        """Get financial summary for a company"""
        try:
            conn = self.get_connection()
            
            # Get date range
            date_range = self._get_date_range(period)
            
            # Base filters
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            date_filter = f"AND i.invoice_date BETWEEN '{date_range['start']}' AND '{date_range['end']}'"
            
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
            
            revenue_df = pd.read_sql_query(revenue_query, conn)
            revenue_data = revenue_df.iloc[0] if not revenue_df.empty else pd.Series([0, 0, 0, 0, 0])
            
            # Partner analysis
            partner_query = f"""
                SELECT 
                    p.name as partner_name,
                    p.partner_type,
                    COUNT(i.id) as invoice_count,
                    SUM(i.total_amount) as total_amount,
                    AVG(i.total_amount) as avg_amount
                FROM partners p
                JOIN companies c ON p.company_id = c.id
                LEFT JOIN invoices i ON p.id = i.partner_id AND i.invoice_date BETWEEN '{date_range['start']}' AND '{date_range['end']}'
                WHERE 1=1 {company_filter.replace('c.id', 'c.id')}
                GROUP BY p.id
                ORDER BY total_amount DESC
                LIMIT 10
            """
            
            partners_df = pd.read_sql_query(partner_query, conn)
            
            # Cash flow analysis
            cash_flow_query = f"""
                SELECT 
                    SUM(pay.amount) as total_payments,
                    COUNT(DISTINCT pay.invoice_id) as payment_count,
                    AVG(pay.amount) as avg_payment
                FROM payments pay
                JOIN invoices i ON pay.invoice_id = i.id
                JOIN companies c ON i.company_id = c.id
                WHERE pay.payment_date BETWEEN '{date_range['start']}' AND '{date_range['end']}' {company_filter}
            """
            
            cash_flow_df = pd.read_sql_query(cash_flow_query, conn)
            cash_flow_data = cash_flow_df.iloc[0] if not cash_flow_df.empty else pd.Series([0, 0, 0])
            
            conn.close()
            
            return {
                'period': period,
                'date_range': date_range,
                'revenue': {
                    'total': float(revenue_data['total_revenue'] or 0),
                    'net': float(revenue_data['net_revenue'] or 0),
                    'tax': float(revenue_data['total_tax'] or 0),
                    'invoice_count': int(revenue_data['invoice_count'] or 0),
                    'avg_invoice': float(revenue_data['avg_invoice_amount'] or 0)
                },
                'cash_flow': {
                    'total_payments': float(cash_flow_data['total_payments'] or 0),
                    'payment_count': int(cash_flow_data['payment_count'] or 0),
                    'avg_payment': float(cash_flow_data['avg_payment'] or 0)
                },
                'top_partners': partners_df.to_dict('records'),
                'net_income': float(revenue_data['total_revenue'] or 0) - float(cash_flow_data['total_payments'] or 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting financial summary: {e}")
            return {}
    
    def get_revenue_analysis(self, company_id: Optional[str] = None, months: int = 12) -> Dict[str, Any]:
        """Get detailed revenue analysis"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            
            # Monthly revenue trends
            monthly_query = f"""
                SELECT 
                    strftime('%Y-%m', i.invoice_date) as month,
                    SUM(i.total_amount) as revenue,
                    COUNT(*) as invoice_count,
                    AVG(i.total_amount) as avg_invoice
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                WHERE i.status IN ('sent', 'paid')
                AND i.invoice_date >= date('now', '-{months} months')
                {company_filter}
                GROUP BY month
                ORDER BY month DESC
            """
            
            monthly_df = pd.read_sql_query(monthly_query, conn)
            
            # Revenue by partner type
            partner_type_query = f"""
                SELECT 
                    p.partner_type,
                    SUM(i.total_amount) as revenue,
                    COUNT(*) as invoice_count
                FROM invoices i
                JOIN partners p ON i.partner_id = p.id
                JOIN companies c ON i.company_id = c.id
                WHERE i.status IN ('sent', 'paid')
                AND i.invoice_date >= date('now', '-{months} months')
                {company_filter}
                GROUP BY p.partner_type
                ORDER BY revenue DESC
            """
            
            partner_type_df = pd.read_sql_query(partner_type_query, conn)
            
            conn.close()
            
            return {
                'monthly_trends': monthly_df.to_dict('records'),
                'by_partner_type': partner_type_df.to_dict('records'),
                'total_revenue': float(monthly_df['revenue'].sum() if not monthly_df.empty else 0),
                'total_invoices': int(monthly_df['invoice_count'].sum() if not monthly_df.empty else 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue analysis: {e}")
            return {}
    
    def get_expense_analysis(self, company_id: Optional[str] = None, months: int = 12) -> Dict[str, Any]:
        """Get expense analysis"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            
            # Expense breakdown
            expense_query = f"""
                SELECT 
                    coa.account_name,
                    coa.account_type,
                    SUM(ft.amount) as total_amount,
                    COUNT(*) as transaction_count
                FROM financial_transactions ft
                JOIN companies c ON ft.company_id = c.id
                JOIN chart_of_accounts coa ON ft.credit_account_id = coa.id
                WHERE coa.account_type = 'expense'
                AND ft.transaction_date >= date('now', '-{months} months')
                {company_filter}
                GROUP BY coa.id
                ORDER BY total_amount DESC
            """
            
            expense_df = pd.read_sql_query(expense_query, conn)
            
            conn.close()
            
            return {
                'expense_breakdown': expense_df.to_dict('records'),
                'total_expenses': float(expense_df['total_amount'].sum() if not expense_df.empty else 0),
                'transaction_count': int(expense_df['transaction_count'].sum() if not expense_df.empty else 0)
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
                WHERE pay.payment_date >= date('now', '-{months} months')
                {company_filter}
                GROUP BY month
                ORDER BY month DESC
            """
            
            cash_flow_df = pd.read_sql_query(cash_flow_query, conn)
            
            # Outstanding invoices
            outstanding_query = f"""
                SELECT 
                    i.invoice_number,
                    i.invoice_date,
                    i.due_date,
                    i.total_amount,
                    COALESCE(SUM(pay.amount), 0) as paid_amount,
                    (i.total_amount - COALESCE(SUM(pay.amount), 0)) as outstanding_amount
                FROM invoices i
                JOIN companies c ON i.company_id = c.id
                LEFT JOIN payments pay ON i.id = pay.invoice_id
                WHERE i.status IN ('sent', 'paid')
                {company_filter}
                GROUP BY i.id
                HAVING (i.total_amount - COALESCE(SUM(pay.amount), 0)) > 0
                ORDER BY i.due_date
            """
            
            outstanding_df = pd.read_sql_query(outstanding_query, conn)
            
            conn.close()
            
            return {
                'monthly_cash_flow': cash_flow_df.to_dict('records'),
                'outstanding_invoices': outstanding_df.to_dict('records'),
                'total_cash_inflow': float(cash_flow_df['cash_inflow'].sum() if not cash_flow_df.empty else 0),
                'total_outstanding': float(outstanding_df['outstanding_amount'].sum() if not outstanding_df.empty else 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting cash flow analysis: {e}")
            return {}
    
    def get_partners(self, company_id: Optional[str] = None, partner_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get partners information"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            type_filter = f"AND p.partner_type = '{partner_type}'" if partner_type else ""
            
            query = f"""
                SELECT 
                    p.id,
                    p.name,
                    p.partner_type,
                    p.email,
                    p.phone,
                    p.address,
                    COUNT(i.id) as invoice_count,
                    SUM(i.total_amount) as total_amount,
                    AVG(i.total_amount) as avg_amount,
                    MAX(i.invoice_date) as last_invoice_date
                FROM partners p
                JOIN companies c ON p.company_id = c.id
                LEFT JOIN invoices i ON p.id = i.partner_id
                WHERE 1=1 {company_filter} {type_filter}
                GROUP BY p.id
                ORDER BY total_amount DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting partners: {e}")
            return []
    
    def get_employees(self, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get employees information"""
        try:
            conn = self.get_connection()
            
            company_filter = f"AND c.id = '{company_id}'" if company_id else ""
            
            query = f"""
                SELECT 
                    e.id,
                    e.name,
                    e.email,
                    e.phone,
                    e.position,
                    e.department,
                    e.hire_date,
                    e.salary
                FROM employees e
                JOIN companies c ON e.company_id = c.id
                WHERE 1=1 {company_filter}
                ORDER BY e.name
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting employees: {e}")
            return []
    
    def search_financial_data(self, query: str, company_id: Optional[str] = None) -> Dict[str, Any]:
        """Search financial data based on user query"""
        try:
            query_lower = query.lower()
            results = {}
            
            # Check for revenue-related queries
            if any(word in query_lower for word in ['revenue', 'income', 'sales', 'prihod']):
                results['revenue'] = self.get_revenue_analysis(company_id)
            
            # Check for expense-related queries
            if any(word in query_lower for word in ['expense', 'cost', 'trošak', 'rashod']):
                results['expenses'] = self.get_expense_analysis(company_id)
            
            # Check for cash flow queries
            if any(word in query_lower for word in ['cash flow', 'cashflow', 'novčani tok', 'payment']):
                results['cash_flow'] = self.get_cash_flow_analysis(company_id)
            
            # Check for partner/customer queries
            if any(word in query_lower for word in ['partner', 'customer', 'client', 'klijent', 'kupac']):
                results['partners'] = self.get_partners(company_id)
            
            # Check for employee queries
            if any(word in query_lower for word in ['employee', 'staff', 'zaposleni', 'osoblje']):
                results['employees'] = self.get_employees(company_id)
            
            # Always include financial summary
            results['summary'] = self.get_financial_summary(company_id)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching financial data: {e}")
            return {}
    
    def _get_date_range(self, period: str) -> Dict[str, str]:
        """Get date range for different periods"""
        today = datetime.now()
        
        if period == "current_month":
            start_date = today.replace(day=1)
            end_date = today
        elif period == "last_month":
            start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = today.replace(day=1) - timedelta(days=1)
        elif period == "current_quarter":
            quarter_start = today.replace(day=1, month=((today.month - 1) // 3) * 3 + 1)
            end_date = today
            start_date = quarter_start
        elif period == "current_year":
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif period == "last_year":
            start_date = today.replace(year=today.year-1, month=1, day=1)
            end_date = today.replace(year=today.year-1, month=12, day=31)
        else:
            # Default to current month
            start_date = today.replace(day=1)
            end_date = today
        
        return {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
