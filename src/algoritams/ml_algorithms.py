"""
ML Algorithms Module for ValidoAI
Comprehensive collection of machine learning algorithms for financial analysis
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.svm import SVR, SVC
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
import joblib
import os
from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MLAlgorithmManager:
    """Manager for ML algorithms with financial focus"""
    
    def __init__(self):
        self.algorithms = {}
        self.models = {}
        self.scalers = {}
        self.algorithm_configs = self._load_algorithm_configs()
    
    def _load_algorithm_configs(self) -> Dict[str, Dict]:
        """Load algorithm configurations"""
        return {
            'revenue_prediction': {
                'name': 'Revenue Prediction',
                'description': 'Predict future revenue based on historical data',
                'algorithms': ['random_forest', 'linear_regression', 'gradient_boosting', 'neural_network'],
                'input_features': ['month', 'year', 'previous_revenue', 'seasonality', 'market_conditions'],
                'output': 'predicted_revenue',
                'metrics': ['mse', 'r2', 'mae']
            },
            'expense_forecasting': {
                'name': 'Expense Forecasting',
                'description': 'Forecast future expenses and costs',
                'algorithms': ['random_forest', 'linear_regression', 'svr'],
                'input_features': ['month', 'year', 'previous_expenses', 'inflation_rate', 'business_volume'],
                'output': 'predicted_expenses',
                'metrics': ['mse', 'r2', 'mae']
            },
            'customer_segmentation': {
                'name': 'Customer Segmentation',
                'description': 'Segment customers based on behavior and spending patterns',
                'algorithms': ['kmeans', 'dbscan'],
                'input_features': ['total_spent', 'frequency', 'recency', 'avg_order_value'],
                'output': 'customer_segment',
                'metrics': ['silhouette_score', 'inertia']
            },
            'fraud_detection': {
                'name': 'Fraud Detection',
                'description': 'Detect fraudulent transactions',
                'algorithms': ['random_forest', 'logistic_regression', 'neural_network'],
                'input_features': ['amount', 'time', 'location', 'merchant_type', 'user_history'],
                'output': 'fraud_probability',
                'metrics': ['accuracy', 'precision', 'recall', 'f1']
            },
            'stock_price_prediction': {
                'name': 'Stock Price Prediction',
                'description': 'Predict stock prices using technical indicators',
                'algorithms': ['lstm', 'random_forest', 'linear_regression'],
                'input_features': ['price', 'volume', 'ma_5', 'ma_20', 'rsi', 'macd'],
                'output': 'predicted_price',
                'metrics': ['mse', 'r2', 'mae']
            },
            'credit_risk_assessment': {
                'name': 'Credit Risk Assessment',
                'description': 'Assess credit risk for loan applications',
                'algorithms': ['random_forest', 'logistic_regression', 'gradient_boosting'],
                'input_features': ['income', 'credit_score', 'debt_ratio', 'payment_history', 'employment_length'],
                'output': 'credit_risk_score',
                'metrics': ['accuracy', 'precision', 'recall', 'f1']
            },
            'market_trend_analysis': {
                'name': 'Market Trend Analysis',
                'description': 'Analyze market trends and patterns',
                'algorithms': ['pca', 'kmeans', 'time_series'],
                'input_features': ['price_data', 'volume_data', 'market_indicators'],
                'output': 'trend_pattern',
                'metrics': ['explained_variance', 'silhouette_score']
            },
            'budget_optimization': {
                'name': 'Budget Optimization',
                'description': 'Optimize budget allocation across departments',
                'algorithms': ['linear_programming', 'genetic_algorithm'],
                'input_features': ['department_budgets', 'performance_metrics', 'constraints'],
                'output': 'optimized_allocation',
                'metrics': ['efficiency_score', 'roi']
            }
        }
    
    def get_available_algorithms(self) -> Dict[str, Dict]:
        """Get all available algorithms"""
        return self.algorithm_configs
    
    def create_algorithm(self, algorithm_type: str, **kwargs) -> Any:
        """Create and configure an ML algorithm"""
        algorithms = {
            'random_forest': {
                'regressor': lambda: RandomForestRegressor(n_estimators=100, random_state=42, **kwargs),
                'classifier': lambda: RandomForestClassifier(n_estimators=100, random_state=42, **kwargs)
            },
            'linear_regression': {
                'regressor': lambda: LinearRegression(**kwargs),
                'classifier': lambda: LogisticRegression(random_state=42, **kwargs)
            },
            'gradient_boosting': {
                'regressor': lambda: GradientBoostingRegressor(n_estimators=100, random_state=42, **kwargs),
                'classifier': lambda: GradientBoostingRegressor(n_estimators=100, random_state=42, **kwargs)
            },
            'svr': {
                'regressor': lambda: SVR(kernel='rbf', **kwargs),
                'classifier': lambda: SVC(kernel='rbf', random_state=42, **kwargs)
            },
            'neural_network': {
                'regressor': lambda: MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42, **kwargs),
                'classifier': lambda: MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42, **kwargs)
            },
            'kmeans': {
                'clusterer': lambda: KMeans(n_clusters=3, random_state=42, **kwargs)
            },
            'dbscan': {
                'clusterer': lambda: DBSCAN(eps=0.5, min_samples=5, **kwargs)
            },
            'pca': {
                'decomposer': lambda: PCA(n_components=2, random_state=42, **kwargs)
            }
        }
        
        if algorithm_type not in algorithms:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")
        
        return algorithms[algorithm_type]
    
    def train_model(self, algorithm_name: str, task_type: str, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Train a model with the specified algorithm"""
        try:
            # Create algorithm
            algorithm_config = self.create_algorithm(algorithm_name)
            
            if task_type == 'regression':
                model = algorithm_config['regressor']()
            elif task_type == 'classification':
                model = algorithm_config['classifier']()
            elif task_type == 'clustering':
                model = algorithm_config['clusterer']()
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Scale features if needed
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            if task_type in ['regression', 'classification']:
                model.fit(X_scaled, y)
                
                # Make predictions
                y_pred = model.predict(X_scaled)
                
                # Calculate metrics
                if task_type == 'regression':
                    metrics = {
                        'mse': mean_squared_error(y, y_pred),
                        'r2': r2_score(y, y_pred),
                        'mae': np.mean(np.abs(y - y_pred))
                    }
                else:
                    metrics = {
                        'accuracy': accuracy_score(y, y_pred),
                        'classification_report': classification_report(y, y_pred, output_dict=True)
                    }
            else:  # clustering
                model.fit(X_scaled)
                y_pred = model.labels_
                metrics = {
                    'n_clusters': len(set(y_pred)) - (1 if -1 in y_pred else 0),
                    'silhouette_score': self._calculate_silhouette_score(X_scaled, y_pred)
                }
            
            # Store model and scaler
            model_key = f"{algorithm_name}_{task_type}_{len(self.models)}"
            self.models[model_key] = model
            self.scalers[model_key] = scaler
            
            return {
                'model_key': model_key,
                'algorithm': algorithm_name,
                'task_type': task_type,
                'metrics': metrics,
                'predictions': y_pred.tolist(),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def predict(self, model_key: str, X: np.ndarray) -> Dict[str, Any]:
        """Make predictions using a trained model"""
        try:
            if model_key not in self.models:
                raise ValueError(f"Model {model_key} not found")
            
            model = self.models[model_key]
            scaler = self.scalers[model_key]
            
            # Scale input
            X_scaled = scaler.transform(X)
            
            # Make prediction
            predictions = model.predict(X_scaled)
            
            return {
                'predictions': predictions.tolist(),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _calculate_silhouette_score(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score for clustering"""
        try:
            from sklearn.metrics import silhouette_score
            return silhouette_score(X, labels)
        except:
            return 0.0
    
    def generate_sample_data(self, algorithm_name: str) -> Dict[str, Any]:
        """Generate sample data for algorithm demonstration"""
        np.random.seed(42)
        
        sample_data = {
            'revenue_prediction': {
                'description': 'Sample revenue data for prediction',
                'data': {
                    'months': list(range(1, 25)),
                    'revenue': [10000, 12000, 11000, 13000, 14000, 13500, 15000, 16000, 
                               15500, 17000, 18000, 17500, 19000, 20000, 19500, 21000,
                               22000, 21500, 23000, 24000, 23500, 25000, 26000, 25500],
                    'features': ['month', 'previous_revenue', 'seasonality']
                }
            },
            'customer_segmentation': {
                'description': 'Sample customer data for segmentation',
                'data': {
                    'customers': list(range(1, 101)),
                    'total_spent': np.random.normal(5000, 2000, 100).tolist(),
                    'frequency': np.random.poisson(15, 100).tolist(),
                    'recency': np.random.exponential(30, 100).tolist(),
                    'avg_order_value': np.random.normal(300, 100, 100).tolist()
                }
            },
            'fraud_detection': {
                'description': 'Sample transaction data for fraud detection',
                'data': {
                    'transactions': list(range(1, 201)),
                    'amount': np.random.exponential(100, 200).tolist(),
                    'time': np.random.uniform(0, 24, 200).tolist(),
                    'location': np.random.choice(['domestic', 'international'], 200).tolist(),
                    'merchant_type': np.random.choice(['retail', 'online', 'service'], 200).tolist(),
                    'is_fraud': np.random.choice([0, 1], 200, p=[0.95, 0.05]).tolist()
                }
            },
            'stock_price_prediction': {
                'description': 'Sample stock price data for prediction',
                'data': {
                    'days': list(range(1, 101)),
                    'price': np.cumsum(np.random.normal(0, 1, 100)).tolist(),
                    'volume': np.random.poisson(1000000, 100).tolist(),
                    'ma_5': [],
                    'ma_20': [],
                    'rsi': np.random.uniform(20, 80, 100).tolist()
                }
            }
        }
        
        # Calculate moving averages for stock data
        if algorithm_name == 'stock_price_prediction':
            prices = sample_data['stock_price_prediction']['data']['price']
            for i in range(len(prices)):
                if i >= 4:
                    sample_data['stock_price_prediction']['data']['ma_5'].append(
                        np.mean(prices[i-4:i+1])
                    )
                else:
                    sample_data['stock_price_prediction']['data']['ma_5'].append(prices[i])
                
                if i >= 19:
                    sample_data['stock_price_prediction']['data']['ma_20'].append(
                        np.mean(prices[i-19:i+1])
                    )
                else:
                    sample_data['stock_price_prediction']['data']['ma_20'].append(prices[i])
        
        return sample_data.get(algorithm_name, {
            'description': 'Sample data not available',
            'data': {}
        })
    
    def save_model(self, model_key: str, filepath: str) -> bool:
        """Save a trained model to disk"""
        try:
            if model_key not in self.models:
                return False
            
            model_data = {
                'model': self.models[model_key],
                'scaler': self.scalers[model_key]
            }
            
            joblib.dump(model_data, filepath)
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, filepath: str) -> str:
        """Load a trained model from disk"""
        try:
            model_data = joblib.load(filepath)
            
            model_key = f"loaded_model_{len(self.models)}"
            self.models[model_key] = model_data['model']
            self.scalers[model_key] = model_data['scaler']
            
            return model_key
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None

# Global instance
ml_manager = MLAlgorithmManager()
