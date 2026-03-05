#!/usr/bin/env python3
"""
Report Generator - Comprehensive Test Report Generation Framework
================================================================

This module provides comprehensive report generation capabilities including:
- HTML reports with interactive charts
- PDF reports with embedded graphs
- JSON data exports
- Chart generation using Plotly
- Performance trend analysis
- Security vulnerability summaries
- Integration test flow diagrams
- Custom dashboard reports

Author: ValidoAI Development Team
Version: 2.0.0
"""

import os
import sys
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: Plotly not available. Chart generation disabled.")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: ReportLab not available. PDF generation disabled.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: Pandas not available. Advanced data analysis disabled.")

class ReportGenerator:
    """Comprehensive test report generator"""

    def __init__(self):
        self.reports_dir = Path("tests/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.charts_dir = Path("tests/reports/charts")
        self.charts_dir.mkdir(parents=True, exist_ok=True)

        self.chart_themes = {
            'default': {
                'background': '#ffffff',
                'text': '#333333',
                'primary': '#007bff',
                'success': '#28a745',
                'warning': '#ffc107',
                'danger': '#dc3545',
                'info': '#17a2b8'
            },
            'dark': {
                'background': '#2c3e50',
                'text': '#ecf0f1',
                'primary': '#3498db',
                'success': '#2ecc71',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'info': '#9b59b6'
            }
        }

    def generate_html_report(self, test_results: Dict[str, Any], theme: str = 'default') -> str:
        """Generate comprehensive HTML report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"comprehensive_test_report_{timestamp}.html"

        # Generate charts
        charts = self._generate_all_charts(test_results, theme)

        # Create HTML content
        html_content = self._create_html_template(test_results, charts, theme)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(report_path)

    def generate_pdf_report(self, test_results: Dict[str, Any]) -> str:
        """Generate PDF report"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"comprehensive_test_report_{timestamp}.pdf"

        # Create PDF document
        doc = SimpleDocTemplate(str(report_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#007bff')
        )

        story.append(Paragraph("ValidoAI Comprehensive Test Report", title_style))
        story.append(Spacer(1, 20))

        # Add metadata
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666')
        )

        metadata_text = f"""
        Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br/>
        Total Tests: {test_results['summary']['total_tests']}<br/>
        Passed: {test_results['summary']['passed']}<br/>
        Failed: {test_results['summary']['failed']}<br/>
        Success Rate: {test_results['summary']['success_rate']}%<br/>
        Duration: {test_results['summary']['duration']:.2f} seconds
        """

        story.append(Paragraph(metadata_text, metadata_style))
        story.append(Spacer(1, 20))

        # Add summary table
        summary_data = [
            ['Category', 'Total Tests', 'Passed', 'Failed', 'Success Rate'],
        ]

        for category_name, category_data in test_results['categories'].items():
            total = len(category_data['tests'])
            passed = category_data['passed']
            failed = category_data['failed']
            success_rate = f"{(passed / total * 100):.1f}%" if total > 0 else "N/A"
            category_display = category_name.replace('_', ' ').title()
            summary_data.append([category_display, str(total), str(passed), str(failed), success_rate])

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Add detailed results for each category
        for category_name, category_data in test_results['categories'].items():
            if category_data['tests']:
                story.append(Paragraph(f"{category_name.replace('_', ' ').title()} Tests", styles['Heading2']))
                story.append(Spacer(1, 10))

                # Create detailed test table
                test_data = [['Test Name', 'Status', 'Duration', 'Details']]

                for test in category_data['tests']:
                    status = test.get('status', 'unknown')
                    name = test.get('name', 'Unknown Test')
                    duration = test.get('duration', 0)
                    details = test.get('message', test.get('error', ''))

                    # Color coding for status
                    if status == 'passed':
                        status_display = '✓ PASSED'
                    elif status == 'failed':
                        status_display = '✗ FAILED'
                    else:
                        status_display = status.upper()

                    test_data.append([
                        name[:50] + '...' if len(name) > 50 else name,
                        status_display,
                        f"{duration:.2f}s" if duration else "N/A",
                        details[:100] + '...' if len(details) > 100 else details
                    ])

                test_table = Table(test_data)
                test_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))

                story.append(test_table)
                story.append(Spacer(1, 15))

        # Build PDF
        doc.build(story)
        return str(report_path)

    def generate_json_report(self, test_results: Dict[str, Any]) -> str:
        """Generate JSON report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"comprehensive_test_report_{timestamp}.json"

        # Add metadata
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'ValidoAI Report Generator v2.0.0',
                'test_framework_version': '2.0.0'
            },
            'test_results': test_results
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(report_path)

    def generate_charts(self, test_results: Dict[str, Any], theme: str = 'default') -> Dict[str, str]:
        """Generate comprehensive charts"""
        if not PLOTLY_AVAILABLE:
            return {}

        charts = {}
        theme_colors = self.chart_themes.get(theme, self.chart_themes['default'])

        # 1. Test Results Overview Pie Chart
        summary = test_results['summary']
        labels = ['Passed', 'Failed', 'Skipped']
        values = [summary['passed'], summary['failed'], summary.get('skipped', 0)]
        colors = [theme_colors['success'], theme_colors['danger'], theme_colors['warning']]

        fig_pie = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            textinfo='label+percent',
            textfont_size=14
        )])

        fig_pie.update_layout(
            title='Test Results Overview',
            font=dict(color=theme_colors['text']),
            paper_bgcolor=theme_colors['background'],
            plot_bgcolor=theme_colors['background']
        )

        charts['test_overview'] = self._save_chart_as_base64(fig_pie, 'test_overview')

        # 2. Test Categories Bar Chart
        categories = []
        passed_counts = []
        failed_counts = []

        for category_name, category_data in test_results['categories'].items():
            categories.append(category_name.replace('_', ' ').title())
            passed_counts.append(category_data['passed'])
            failed_counts.append(category_data['failed'])

        fig_bar = go.Figure()

        fig_bar.add_trace(go.Bar(
            name='Passed',
            x=categories,
            y=passed_counts,
            marker_color=theme_colors['success']
        ))

        fig_bar.add_trace(go.Bar(
            name='Failed',
            x=categories,
            y=failed_counts,
            marker_color=theme_colors['danger']
        ))

        fig_bar.update_layout(
            title='Test Results by Category',
            barmode='stack',
            font=dict(color=theme_colors['text']),
            paper_bgcolor=theme_colors['background'],
            plot_bgcolor=theme_colors['background'],
            xaxis_title='Test Categories',
            yaxis_title='Number of Tests'
        )

        charts['category_results'] = self._save_chart_as_base64(fig_bar, 'category_results')

        # 3. Success Rate Gauge Chart
        success_rate = summary['success_rate']

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=success_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Success Rate"},
            delta={'reference': 85},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': theme_colors['success'] if success_rate >= 80 else theme_colors['danger']},
                'steps': [
                    {'range': [0, 50], 'color': theme_colors['danger']},
                    {'range': [50, 80], 'color': theme_colors['warning']},
                    {'range': [80, 100], 'color': theme_colors['success']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig_gauge.update_layout(
            font=dict(color=theme_colors['text']),
            paper_bgcolor=theme_colors['background']
        )

        charts['success_rate'] = self._save_chart_as_base64(fig_gauge, 'success_rate')

        # 4. Performance Timeline Chart (if performance data available)
        if 'performance_metrics' in test_results and test_results['performance_metrics'].get('load_times'):
            load_times = test_results['performance_metrics']['load_times']

            if load_times:
                times = [item['load_time'] for item in load_times]
                routes = [item['route'] for item in load_times]

                fig_timeline = go.Figure()

                fig_timeline.add_trace(go.Scatter(
                    x=routes,
                    y=times,
                    mode='lines+markers',
                    name='Load Time',
                    line=dict(color=theme_colors['primary']),
                    marker=dict(size=8)
                ))

                fig_timeline.update_layout(
                    title='Page Load Times',
                    font=dict(color=theme_colors['text']),
                    paper_bgcolor=theme_colors['background'],
                    plot_bgcolor=theme_colors['background'],
                    xaxis_title='Routes',
                    yaxis_title='Load Time (seconds)'
                )

                charts['performance_timeline'] = self._save_chart_as_base64(fig_timeline, 'performance_timeline')

        # 5. Vulnerability Summary (for security tests)
        if 'vulnerabilities' in test_results:
            vulnerabilities = test_results['vulnerabilities']
            severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}

            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'Medium')
                if severity in severity_counts:
                    severity_counts[severity] += 1

            severities = list(severity_counts.keys())
            counts = list(severity_counts.values())

            fig_vuln = go.Figure()

            fig_vuln.add_trace(go.Bar(
                x=severities,
                y=counts,
                marker_color=[theme_colors['danger'], theme_colors['warning'], theme_colors['info'], theme_colors['success']],
                text=counts,
                textposition='auto'
            ))

            fig_vuln.update_layout(
                title='Security Vulnerabilities by Severity',
                font=dict(color=theme_colors['text']),
                paper_bgcolor=theme_colors['background'],
                plot_bgcolor=theme_colors['background'],
                xaxis_title='Severity Level',
                yaxis_title='Number of Vulnerabilities'
            )

            charts['vulnerability_summary'] = self._save_chart_as_base64(fig_vuln, 'vulnerability_summary')

        return charts

    def _generate_all_charts(self, test_results: Dict[str, Any], theme: str = 'default') -> Dict[str, str]:
        """Generate all available charts"""
        charts = {}

        try:
            charts.update(self.generate_charts(test_results, theme))
        except Exception as e:
            print(f"Chart generation failed: {str(e)}")

        return charts

    def _save_chart_as_base64(self, fig, filename: str) -> str:
        """Save chart as base64 encoded image"""
        try:
            # Convert to PNG image in memory
            img_bytes = fig.to_image(format="png", width=800, height=600, scale=1)

            # Encode as base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')

            return f"data:image/png;base64,{img_base64}"

        except Exception as e:
            print(f"Failed to save chart {filename}: {str(e)}")
            return ""

    def _create_html_template(self, test_results: Dict[str, Any], charts: Dict[str, str], theme: str = 'default') -> str:
        """Create HTML template for the report"""
        theme_colors = self.chart_themes.get(theme, self.chart_themes['default'])

        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ValidoAI Comprehensive Test Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}

                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: {theme_colors['background']};
                    color: {theme_colors['text']};
                    line-height: 1.6;
                }}

                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 20px;
                }}

                .header {{
                    background: linear-gradient(135deg, {theme_colors['primary']} 0%, {theme_colors['info']} 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    text-align: center;
                }}

                .header h1 {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}

                .header p {{
                    font-size: 1.2em;
                    opacity: 0.9;
                }}

                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}

                .summary-card {{
                    background: white;
                    padding: 25px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    transition: transform 0.2s;
                }}

                .summary-card:hover {{
                    transform: translateY(-5px);
                }}

                .summary-card .number {{
                    font-size: 2.5em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}

                .summary-card .label {{
                    color: #666;
                    font-size: 0.9em;
                }}

                .passed {{ color: {theme_colors['success']}; }}
                .failed {{ color: {theme_colors['danger']}; }}
                .skipped {{ color: {theme_colors['warning']}; }}
                .total {{ color: {theme_colors['primary']}; }}

                .charts-section {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 25px;
                    margin-bottom: 30px;
                }}

                .chart-container {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}

                .chart-container h3 {{
                    text-align: center;
                    margin-bottom: 20px;
                    color: {theme_colors['primary']};
                }}

                .chart-container img {{
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 0 auto;
                }}

                .details-section {{
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                    margin-bottom: 20px;
                }}

                .category-header {{
                    background: {theme_colors['primary']};
                    color: white;
                    padding: 15px 20px;
                    font-size: 1.2em;
                    font-weight: bold;
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}

                .category-content {{
                    display: none;
                    padding: 0;
                }}

                .category-content.show {{
                    display: block;
                }}

                .test-item {{
                    padding: 15px 20px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: background-color 0.2s;
                }}

                .test-item:hover {{
                    background-color: #f8f9fa;
                }}

                .test-item:last-child {{
                    border-bottom: none;
                }}

                .test-name {{
                    font-weight: 600;
                    flex: 1;
                }}

                .test-status {{
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 0.85em;
                    font-weight: 600;
                    text-transform: uppercase;
                }}

                .status-passed {{
                    background: #d4edda;
                    color: #155724;
                }}

                .status-failed {{
                    background: #f8d7da;
                    color: #721c24;
                }}

                .status-error {{
                    background: #fff3cd;
                    color: #856404;
                }}

                .duration {{
                    font-size: 0.9em;
                    color: #666;
                    margin-left: 10px;
                }}

                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 0.9em;
                }}

                .toggle-btn {{
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.2em;
                    cursor: pointer;
                }}

                .vulnerability-item {{
                    background: #fff3cd;
                    border-left: 4px solid {theme_colors['warning']};
                    padding: 15px 20px;
                    margin: 10px 20px;
                    border-radius: 0 5px 5px 0;
                }}

                .vulnerability-severity {{
                    font-weight: bold;
                    color: {theme_colors['danger']};
                }}

                @media (max-width: 768px) {{
                    .container {{
                        padding: 10px;
                    }}

                    .header h1 {{
                        font-size: 2em;
                    }}

                    .summary-grid {{
                        grid-template-columns: 1fr;
                    }}

                    .charts-section {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 ValidoAI Comprehensive Test Report</h1>
                    <p>Generated on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S")}</p>
                    <p>Complete testing results for all application components</p>
                </div>

                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="number total">{test_results['summary']['total_tests']}</div>
                        <div class="label">Total Tests</div>
                    </div>
                    <div class="summary-card">
                        <div class="number passed">{test_results['summary']['passed']}</div>
                        <div class="label">Passed</div>
                    </div>
                    <div class="summary-card">
                        <div class="number failed">{test_results['summary']['failed']}</div>
                        <div class="label">Failed</div>
                    </div>
                    <div class="summary-card">
                        <div class="number skipped">{test_results['summary'].get('skipped', 0)}</div>
                        <div class="label">Skipped</div>
                    </div>
                    <div class="summary-card">
                        <div class="number total">{test_results['summary']['success_rate']:.1f}%</div>
                        <div class="label">Success Rate</div>
                    </div>
                    <div class="summary-card">
                        <div class="number total">{test_results['summary']['duration']:.2f}s</div>
                        <div class="label">Duration</div>
                    </div>
                </div>

                <div class="charts-section">
        """

        # Add charts
        if 'test_overview' in charts:
            html_template += f"""
                    <div class="chart-container">
                        <h3>Test Results Overview</h3>
                        <img src="{charts['test_overview']}" alt="Test Results Overview">
                    </div>
            """

        if 'success_rate' in charts:
            html_template += f"""
                    <div class="chart-container">
                        <h3>Success Rate Gauge</h3>
                        <img src="{charts['success_rate']}" alt="Success Rate Gauge">
                    </div>
            """

        if 'category_results' in charts:
            html_template += f"""
                    <div class="chart-container">
                        <h3>Test Results by Category</h3>
                        <img src="{charts['category_results']}" alt="Test Results by Category">
                    </div>
            """

        if 'vulnerability_summary' in charts and 'vulnerabilities' in test_results and test_results['vulnerabilities']:
            html_template += f"""
                    <div class="chart-container">
                        <h3>Security Vulnerabilities</h3>
                        <img src="{charts['vulnerability_summary']}" alt="Security Vulnerabilities">
                    </div>
            """

        html_template += """
                </div>

                <div class="details-section">
        """

        # Add detailed test results
        for category_name, category_data in test_results['categories'].items():
            if category_data['tests']:
                category_display = category_name.replace('_', ' ').title()
                test_count = len(category_data['tests'])
                passed_count = category_data['passed']
                failed_count = category_data['failed']

                html_template += f"""
                    <div class="category-header" onclick="toggleCategory('{category_name}')">
                        <span>{category_display} Tests ({test_count})</span>
                        <span style="font-size: 0.9em;">
                            ✅ {passed_count} | ❌ {failed_count}
                        </span>
                        <button class="toggle-btn">▼</button>
                    </div>
                    <div class="category-content" id="{category_name}">
                """

                for test in category_data['tests']:
                    status_class = f"status-{test.get('status', 'unknown')}"
                    duration = test.get('duration', 0)
                    duration_text = f"<span class='duration'>{duration:.2f}s</span>" if duration else ""

                    html_template += f"""
                        <div class="test-item">
                            <div class="test-name">{test.get('name', 'Unknown Test')}</div>
                            <div class="test-status {status_class}">{test.get('status', 'unknown').upper()}</div>
                            {duration_text}
                        </div>
                    """

                html_template += """
                    </div>
                """

        # Add vulnerabilities section if present
        if 'vulnerabilities' in test_results and test_results['vulnerabilities']:
            html_template += """
                <div class="category-header" onclick="toggleCategory('vulnerabilities')">
                    <span>🔒 Security Vulnerabilities</span>
                    <span style="font-size: 0.9em;">
                        ⚠️ {len(test_results['vulnerabilities'])} issues found
                    </span>
                    <button class="toggle-btn">▼</button>
                </div>
                <div class="category-content" id="vulnerabilities">
            """

            for vuln in test_results['vulnerabilities']:
                html_template += f"""
                    <div class="vulnerability-item">
                        <div class="vulnerability-severity">{vuln.get('severity', 'Medium')} Severity</div>
                        <div><strong>{vuln.get('type', 'Unknown Vulnerability')}</strong></div>
                        <div>{vuln.get('description', vuln.get('evidence', 'No description available'))}</div>
                        <div><em>Recommendation: {vuln.get('recommendation', 'No specific recommendation available')}</em></div>
                    </div>
                """

            html_template += """
                </div>
            """

        html_template += """
                </div>

                <div class="footer">
                    <p>Report generated by ValidoAI Test Suite v2.0.0</p>
                    <p>For detailed information about test failures, check the console logs or generated JSON report.</p>
                </div>
            </div>

            <script>
                function toggleCategory(categoryId) {{
                    const content = document.getElementById(categoryId);
                    const button = content.previousElementSibling.querySelector('.toggle-btn');

                    if (content.classList.contains('show')) {{
                        content.classList.remove('show');
                        button.textContent = '▼';
                    }} else {{
                        content.classList.add('show');
                        button.textContent = '▲';
                    }}
                }}

                // Auto-expand failed test categories
                document.addEventListener('DOMContentLoaded', function() {{
                    const categories = document.querySelectorAll('.category-content');
                    categories.forEach(content => {{
                        const testItems = content.querySelectorAll('.test-item');
                        let hasFailures = false;

                        testItems.forEach(item => {{
                            if (item.querySelector('.status-failed')) {{
                                hasFailures = true;
                            }}
                        }});

                        if (hasFailures) {{
                            content.classList.add('show');
                            const button = content.previousElementSibling.querySelector('.toggle-btn');
                            button.textContent = '▲';
                        }}
                    }});
                }});
            </script>
        </body>
        </html>
        """

        return html_template

if __name__ == "__main__":
    # Example usage
    report_gen = ReportGenerator()

    # Mock test results for demonstration
    mock_results = {
        'summary': {
            'total_tests': 100,
            'passed': 85,
            'failed': 15,
            'skipped': 0,
            'success_rate': 85.0,
            'duration': 120.5,
            'start_time': datetime.now(),
            'end_time': datetime.now()
        },
        'categories': {
            'ui_tests': {'tests': [], 'passed': 20, 'failed': 5},
            'api_tests': {'tests': [], 'passed': 25, 'failed': 5},
            'security_tests': {'tests': [], 'passed': 40, 'failed': 5}
        }
    }

    # Generate reports
    html_report = report_gen.generate_html_report(mock_results)
    json_report = report_gen.generate_json_report(mock_results)

    print(f"HTML Report: {html_report}")
    print(f"JSON Report: {json_report}")

    if REPORTLAB_AVAILABLE:
        try:
            pdf_report = report_gen.generate_pdf_report(mock_results)
            print(f"PDF Report: {pdf_report}")
        except Exception as e:
            print(f"PDF generation failed: {str(e)}")
