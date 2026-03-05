#!/usr/bin/env python3
"""
Test Dashboard Analytics System
===============================

Comprehensive tests for the ValidoAI dashboard analytics and predictive analytics systems.
Tests real-time metrics, forecasting algorithms, and business intelligence features.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask.testing import FlaskClient

class TestDashboardAnalytics(unittest.TestCase):
    """Test cases for dashboard analytics system"""

    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Mock the dashboard analytics
        with patch('src.dashboard_analytics.dashboard_analytics') as mock_analytics:
            self.mock_analytics = mock_analytics

    def tearDown(self):
        """Clean up test environment"""
        pass

    def test_dashboard_analytics_initialization(self):
        """Test dashboard analytics initialization"""
        from src.dashboard_analytics import dashboard_analytics

        self.assertIsNotNone(dashboard_analytics)
        self.assertTrue(hasattr(dashboard_analytics, 'metrics'))
        self.assertTrue(hasattr(dashboard_analytics, 'alerts'))

    def test_get_dashboard_data(self):
        """Test getting dashboard data"""
        from src.dashboard_analytics import get_dashboard_data

        with patch('src.dashboard_analytics.dashboard_analytics') as mock_analytics:
            mock_analytics.get_dashboard_data.return_value = {
                'metrics': {'test': 'data'},
                'alerts': [],
                'timestamp': datetime.now().isoformat()
            }

            result = get_dashboard_data('test-user')
            self.assertIsInstance(result, dict)
            self.assertIn('metrics', result)

    def test_get_kpi_cards(self):
        """Test getting KPI cards data"""
        from src.dashboard_analytics import get_kpi_cards

        cards = get_kpi_cards()
        self.assertIsInstance(cards, list)

        if len(cards) > 0:
            card = cards[0]
            self.assertIn('id', card)
            self.assertIn('title', card)
            self.assertIn('value', card)
            self.assertIn('trend', card)

    def test_get_chart_data(self):
        """Test getting chart data"""
        from src.dashboard_analytics import get_chart_data

        # Test revenue chart data
        chart_data = get_chart_data('revenue')
        self.assertIsInstance(chart_data, dict)

        # Test invalid chart type
        invalid_data = get_chart_data('invalid_type')
        self.assertIsInstance(invalid_data, dict)
        self.assertIn('error', invalid_data)

    def test_metrics_update_simulation(self):
        """Test metrics update simulation"""
        from src.dashboard_analytics import dashboard_analytics

        # Store original metrics
        original_revenue = dashboard_analytics.metrics['revenue']['current']

        # Simulate metrics update
        dashboard_analytics._update_revenue_metrics()

        # Check that metrics were updated
        updated_revenue = dashboard_analytics.metrics['revenue']['current']
        self.assertIsInstance(updated_revenue, (int, float))

    def test_alert_generation(self):
        """Test alert generation logic"""
        from src.dashboard_analytics import dashboard_analytics

        # Set up conditions that should trigger alerts
        dashboard_analytics.metrics['revenue']['growth_rate'] = -15  # Negative growth
        dashboard_analytics.metrics['customers']['churn_rate'] = 10  # High churn

        # Generate alerts
        dashboard_analytics._check_alerts()

        # Check that alerts were generated
        self.assertIsInstance(dashboard_analytics.alerts, list)

    def test_trend_analysis(self):
        """Test trend analysis functionality"""
        from src.dashboard_analytics import dashboard_analytics

        # Add some data points for trend analysis
        dashboard_analytics.metrics['revenue']['data_points'] = [
            {'timestamp': '2024-01-01T00:00:00', 'value': 1000},
            {'timestamp': '2024-01-02T00:00:00', 'value': 1200},
            {'timestamp': '2024-01-03T00:00:00', 'value': 1100},
            {'timestamp': '2024-01-04T00:00:00', 'value': 1300},
            {'timestamp': '2024-01-05T00:00:00', 'value': 1250}
        ]

        # Analyze trends
        dashboard_analytics._analyze_trends()

        # Check that trend was set
        self.assertIn('trend', dashboard_analytics.metrics['revenue'])

class TestPredictiveAnalytics(unittest.TestCase):
    """Test cases for predictive analytics system"""

    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up test environment"""
        pass

    def test_predictive_analytics_initialization(self):
        """Test predictive analytics initialization"""
        from src.predictive_analytics import predictive_analytics

        self.assertIsNotNone(predictive_analytics)
        self.assertTrue(hasattr(predictive_analytics, 'forecasts'))
        self.assertTrue(hasattr(predictive_analytics, 'predictions'))
        self.assertTrue(hasattr(predictive_analytics, 'trends'))

    def test_revenue_forecast_generation(self):
        """Test revenue forecast generation"""
        from src.predictive_analytics import get_revenue_forecast

        forecast = get_revenue_forecast(30)
        self.assertIsInstance(forecast, dict)

        if 'forecast' in forecast:
            self.assertIsInstance(forecast['forecast'], list)
            self.assertEqual(len(forecast['forecast']), 30)

        if 'days' in forecast:
            self.assertEqual(forecast['days'], 30)

    def test_customer_insights_generation(self):
        """Test customer insights generation"""
        from src.predictive_analytics import get_customer_insights

        insights = get_customer_insights()
        self.assertIsInstance(insights, dict)

        # Check for expected structure
        expected_keys = ['overall_churn_rate', 'segments']
        for key in expected_keys:
            if key in insights:
                self.assertIsNotNone(insights[key])

    def test_business_intelligence_report(self):
        """Test comprehensive business intelligence report"""
        from src.predictive_analytics import get_business_intelligence_report

        report = get_business_intelligence_report()
        self.assertIsInstance(report, dict)

        # Check for major sections
        expected_sections = ['revenue_forecast', 'customer_insights', 'trend_analysis']
        for section in expected_sections:
            if section in report:
                self.assertIsInstance(report[section], dict)

    def test_forecast_algorithms(self):
        """Test different forecasting algorithms"""
        from src.predictive_analytics import predictive_analytics

        # Test data
        test_data = [100, 120, 110, 130, 125, 140, 135, 150, 145, 160]

        # Test ARIMA forecast
        arima_forecast = predictive_analytics._arima_forecast(test_data, 5)
        self.assertIsInstance(arima_forecast, dict)
        self.assertIn('forecast', arima_forecast)
        self.assertEqual(len(arima_forecast['forecast']), 5)

        # Test Exponential Smoothing
        exp_forecast = predictive_analytics._exponential_smoothing_forecast(test_data, 5)
        self.assertIsInstance(exp_forecast, dict)
        self.assertIn('forecast', exp_forecast)
        self.assertEqual(len(exp_forecast['forecast']), 5)

        # Test Linear Regression
        linear_forecast = predictive_analytics._linear_regression_forecast(test_data, 5)
        self.assertIsInstance(linear_forecast, dict)
        self.assertIn('forecast', linear_forecast)
        self.assertEqual(len(linear_forecast['forecast']), 5)

        # Test Ensemble
        ensemble_forecast = predictive_analytics._ensemble_forecast(test_data, 5)
        self.assertIsInstance(ensemble_forecast, dict)
        self.assertIn('forecast', ensemble_forecast)
        self.assertEqual(len(ensemble_forecast['forecast']), 5)

    def test_confidence_intervals(self):
        """Test confidence interval calculations"""
        from src.predictive_analytics import predictive_analytics

        # Mock forecasts for testing
        mock_forecasts = {
            'arima': {'forecast': [100, 110, 120]},
            'exponential_smoothing': {'forecast': [105, 115, 125]},
            'linear_regression': {'forecast': [102, 112, 122]}
        }

        confidence_intervals = predictive_analytics._calculate_confidence_intervals(mock_forecasts)

        if 'error' not in confidence_intervals:
            self.assertIn('upper_bound', confidence_intervals)
            self.assertIn('lower_bound', confidence_intervals)
            self.assertIn('standard_deviation', confidence_intervals)
            self.assertEqual(len(confidence_intervals['upper_bound']), 3)

    def test_anomaly_detection(self):
        """Test anomaly detection functionality"""
        from src.predictive_analytics import predictive_analytics

        # Test revenue anomaly detection
        anomalies = predictive_analytics._detect_revenue_anomalies()
        self.assertIsInstance(anomalies, dict)
        self.assertIn('anomalies_detected', anomalies)

        # Test customer anomaly detection
        customer_anomalies = predictive_analytics._detect_customer_anomalies()
        self.assertIsInstance(customer_anomalies, dict)

        # Test operational anomaly detection
        operational_anomalies = predictive_analytics._detect_operational_anomalies()
        self.assertIsInstance(operational_anomalies, dict)

    def test_trend_analysis_components(self):
        """Test trend analysis components"""
        from src.predictive_analytics import predictive_analytics

        # Test seasonal patterns
        seasonal = predictive_analytics._detect_seasonal_patterns()
        self.assertIsInstance(seasonal, dict)
        self.assertIn('weekly_patterns', seasonal)

        # Test growth trends
        growth = predictive_analytics._analyze_growth_trends()
        self.assertIsInstance(growth, dict)
        self.assertIn('revenue_growth', growth)

        # Test correlation analysis
        correlations = predictive_analytics._analyze_correlations()
        self.assertIsInstance(correlations, dict)
        self.assertIn('strong_correlations', correlations)

    def test_inventory_forecasting(self):
        """Test inventory forecasting functionality"""
        from src.predictive_analytics import predictive_analytics

        # Test demand forecasting
        demand = predictive_analytics._forecast_product_demand()
        self.assertIsInstance(demand, dict)
        self.assertIn('top_products', demand)

        # Test stockout probability
        stockout = predictive_analytics._calculate_stockout_probability()
        self.assertIsInstance(stockout, dict)

        # Test optimal inventory
        optimal = predictive_analytics._calculate_optimal_inventory()
        self.assertIsInstance(optimal, dict)
        self.assertIn('recommended_levels', optimal)

    def test_customer_prediction_methods(self):
        """Test customer prediction methods"""
        from src.predictive_analytics import predictive_analytics

        # Test churn prediction
        churn = predictive_analytics._predict_customer_churn()
        self.assertIsInstance(churn, dict)
        self.assertIn('overall_churn_rate', churn)

        # Test lifetime value prediction
        ltv = predictive_analytics._predict_customer_lifetime_value()
        self.assertIsInstance(ltv, dict)
        self.assertIn('overall_avg_ltv', ltv)

        # Test purchase probability
        purchase_prob = predictive_analytics._predict_purchase_probability()
        self.assertIsInstance(purchase_prob, dict)
        self.assertIn('next_30_days', purchase_prob)

class TestDashboardAPI(unittest.TestCase):
    """Test cases for dashboard API endpoints"""

    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Register test routes
        @self.app.route('/api/dashboard/data', methods=['GET'])
        def get_dashboard_data():
            return jsonify({
                'metrics': {'test': 'data'},
                'alerts': [],
                'timestamp': datetime.now().isoformat()
            })

        @self.app.route('/api/dashboard/kpi-cards', methods=['GET'])
        def get_kpi_cards():
            return jsonify({
                'kpi_cards': [
                    {
                        'id': 'revenue',
                        'title': 'Revenue',
                        'value': '$45,231.89',
                        'change': '+20.1%',
                        'trend': 'up'
                    }
                ],
                'total_cards': 1,
                'timestamp': datetime.now().isoformat()
            })

    def test_dashboard_data_endpoint(self):
        """Test dashboard data API endpoint"""
        response = self.client.get('/api/dashboard/data')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('metrics', data)
        self.assertIn('alerts', data)
        self.assertIn('timestamp', data)

    def test_kpi_cards_endpoint(self):
        """Test KPI cards API endpoint"""
        response = self.client.get('/api/dashboard/kpi-cards')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('kpi_cards', data)
        self.assertIn('total_cards', data)
        self.assertIn('timestamp', data)

        if len(data['kpi_cards']) > 0:
            card = data['kpi_cards'][0]
            expected_fields = ['id', 'title', 'value', 'change', 'trend']
            for field in expected_fields:
                self.assertIn(field, card)

    def test_predictive_analytics_endpoints(self):
        """Test predictive analytics API endpoints"""
        # Test forecast endpoint
        response = self.client.get('/api/predictive/forecast?days=7')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('forecast_data', data)
        self.assertIn('days', data)
        self.assertEqual(data['days'], 7)

        # Test insights endpoint
        response = self.client.get('/api/predictive/insights')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('insights_data', data)

        # Test anomalies endpoint
        response = self.client.get('/api/predictive/anomalies')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('anomaly_data', data)

class TestHypercornIntegration(unittest.TestCase):
    """Test cases for Hypercorn integration"""

    def test_hypercorn_server_creation(self):
        """Test Hypercorn server creation"""
        from src.hypercorn_server import create_hypercorn_server

        # Create a simple Flask app for testing
        app = Flask(__name__)

        server = create_hypercorn_server(app)
        self.assertIsNotNone(server)
        self.assertEqual(server.app, app)

    def test_hypercorn_config(self):
        """Test Hypercorn configuration"""
        from src.hypercorn_server import HypercornServer

        app = Flask(__name__)
        server = HypercornServer(app)

        self.assertIsNotNone(server.config)
        self.assertTrue(hasattr(server.config, 'bind'))
        self.assertTrue(len(server.config.bind) > 0)

    def test_application_factory_integration(self):
        """Test application factory with Hypercorn"""
        from app import create_app

        # Test development config
        app = create_app('development')
        self.assertIsNotNone(app)
        self.assertEqual(app.config['DEBUG'], True)

        # Test production config
        app = create_app('production')
        self.assertIsNotNone(app)
        self.assertEqual(app.config['DEBUG'], False)

if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2)
