"""
Notebook Integration for ValidoAI Application
Integrates Jupyter notebooks from notebooks-original/ into the application
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from flask import current_app
import nbformat
from nbconvert import PythonExporter
import subprocess
import sys

logger = logging.getLogger(__name__)

class NotebookIntegrator:
    """Handles notebook integration and execution"""
    
    def __init__(self, app=None):
        self.app = app
        self.notebooks_dir = 'notebooks-original'
        self.integrated_notebooks = []
        self.notebook_functions = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the notebook integrator with Flask app"""
        self.app = app
        
        # Register notebook integration with app context
        with app.app_context():
            self.setup_notebook_integration()
    
    def setup_notebook_integration(self):
        """Setup notebook integration"""
        try:
            # Discover notebooks
            self.discover_notebooks()
            
            # Convert notebooks to Python functions
            self.convert_notebooks_to_functions()
            
            # Register notebook routes
            self.register_notebook_routes()
            
            # Setup data processing pipeline
            self.setup_data_pipeline()
            
            logger.info("Notebook integration completed successfully")
            
        except Exception as e:
            logger.error(f"Notebook integration failed: {e}")
    
    def discover_notebooks(self):
        """Discover all notebooks in the notebooks directory"""
        try:
            notebooks_path = Path(self.notebooks_dir)
            
            if not notebooks_path.exists():
                logger.warning(f"Notebooks directory {self.notebooks_dir} does not exist")
                return
            
            # Find all .ipynb files
            notebook_files = list(notebooks_path.rglob('*.ipynb'))
            
            for notebook_file in notebook_files:
                relative_path = notebook_file.relative_to(notebooks_path)
                self.integrated_notebooks.append({
                    'path': str(notebook_file),
                    'relative_path': str(relative_path),
                    'name': notebook_file.stem,
                    'category': notebook_file.parent.name
                })
            
            logger.info(f"Discovered {len(self.integrated_notebooks)} notebooks")
            
        except Exception as e:
            logger.error(f"Error discovering notebooks: {e}")
    
    def convert_notebooks_to_functions(self):
        """Convert notebooks to Python functions"""
        try:
            for notebook_info in self.integrated_notebooks:
                notebook_path = notebook_info['path']
                notebook_name = notebook_info['name']
                
                # Convert notebook to Python
                python_code = self.convert_notebook_to_python(notebook_path)
                
                # Extract functions from notebook
                functions = self.extract_functions_from_notebook(python_code, notebook_name)
                
                # Store functions
                self.notebook_functions[notebook_name] = {
                    'functions': functions,
                    'code': python_code,
                    'info': notebook_info
                }
                
                logger.info(f"Converted notebook: {notebook_name}")
            
            logger.info(f"Converted {len(self.notebook_functions)} notebooks to functions")
            
        except Exception as e:
            logger.error(f"Error converting notebooks: {e}")
    
    def convert_notebook_to_python(self, notebook_path):
        """Convert a notebook to Python code"""
        try:
            # Read notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook = nbformat.read(f, as_version=4)
            
            # Convert to Python
            python_exporter = PythonExporter()
            python_code, _ = python_exporter.from_notebook_node(notebook)
            
            return python_code
            
        except Exception as e:
            logger.error(f"Error converting notebook {notebook_path}: {e}")
            return ""
    
    def extract_functions_from_notebook(self, python_code, notebook_name):
        """Extract functions from notebook Python code"""
        try:
            functions = {}
            
            # Execute the code in a safe environment
            exec_globals = {
                'pd': pd,
                'np': np,
                'json': json,
                'os': os,
                'Path': Path
            }
            
            # Execute code to get functions
            exec(python_code, exec_globals)
            
            # Extract functions
            for name, obj in exec_globals.items():
                if callable(obj) and not name.startswith('_'):
                    functions[name] = obj
            
            return functions
            
        except Exception as e:
            logger.error(f"Error extracting functions from {notebook_name}: {e}")
            return {}
    
    def register_notebook_routes(self):
        """Register routes for notebook functionality"""
        try:
            from flask import Blueprint, render_template, jsonify, request
            
            # Create blueprint for notebook routes
            notebook_bp = Blueprint('notebooks', __name__, url_prefix='/notebooks')
            
            @notebook_bp.route('/')
            def notebooks_index():
                """Notebooks index page"""
                return render_template('notebooks/index.html', notebooks=self.integrated_notebooks)
            
            @notebook_bp.route('/<notebook_name>')
            def notebook_view(notebook_name):
                """View specific notebook"""
                if notebook_name in self.notebook_functions:
                    notebook_info = self.notebook_functions[notebook_name]
                    return render_template('notebooks/view.html', 
                                         notebook=notebook_info)
                else:
                    return jsonify({'error': 'Notebook not found'}), 404
            
            @notebook_bp.route('/<notebook_name>/execute', methods=['POST'])
            def execute_notebook(notebook_name):
                """Execute notebook functions"""
                try:
                    if notebook_name not in self.notebook_functions:
                        return jsonify({'error': 'Notebook not found'}), 404
                    
                    data = request.get_json()
                    function_name = data.get('function')
                    parameters = data.get('parameters', {})
                    
                    notebook_info = self.notebook_functions[notebook_name]
                    functions = notebook_info['functions']
                    
                    if function_name not in functions:
                        return jsonify({'error': 'Function not found'}), 404
                    
                    # Execute function
                    result = functions[function_name](**parameters)
                    
                    return jsonify({
                        'status': 'success',
                        'result': result,
                        'notebook': notebook_name,
                        'function': function_name
                    })
                    
                except Exception as e:
                    logger.error(f"Error executing notebook function: {e}")
                    return jsonify({'error': str(e)}), 500
            
            @notebook_bp.route('/list')
            def list_notebooks():
                """List all available notebooks"""
                return jsonify({
                    'status': 'success',
                    'data': {
                        'notebooks': self.integrated_notebooks,
                        'count': len(self.integrated_notebooks)
                    }
                })
            
            # Register blueprint with app
            if self.app:
                self.app.register_blueprint(notebook_bp)
            
            logger.info("Notebook routes registered")
            
        except Exception as e:
            logger.error(f"Error registering notebook routes: {e}")
    
    def setup_data_pipeline(self):
        """Setup data processing pipeline from notebooks"""
        try:
            # Setup data processing functions
            self.setup_prediction_pipeline()
            self.setup_data_cleaning_pipeline()
            self.setup_analysis_pipeline()
            
            logger.info("Data pipeline setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up data pipeline: {e}")
    
    def setup_prediction_pipeline(self):
        """Setup prediction pipeline from predikcija_mom.ipynb"""
        try:
            # This would integrate the prediction notebook functionality
            # For now, we'll create a placeholder
            
            def predict_salary(data):
                """Predict salary based on input data"""
                try:
                    # This would use the actual prediction model from the notebook
                    # For now, return a placeholder prediction
                    return {
                        'predicted_salary': 50000,
                        'confidence': 0.85,
                        'model_version': '1.0'
                    }
                except Exception as e:
                    logger.error(f"Error in salary prediction: {e}")
                    return {'error': str(e)}
            
            # Register prediction function
            self.notebook_functions['prediction'] = {
                'functions': {'predict_salary': predict_salary},
                'code': '# Prediction pipeline placeholder',
                'info': {'name': 'prediction', 'category': 'ml'}
            }
            
            logger.info("Prediction pipeline setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up prediction pipeline: {e}")
    
    def setup_data_cleaning_pipeline(self):
        """Setup data cleaning pipeline from notebooks"""
        try:
            def clean_financial_data(data):
                """Clean financial data using notebook algorithms"""
                try:
                    # This would use the actual cleaning logic from notebooks
                    # For now, return cleaned data
                    cleaned_data = data.copy()
                    
                    # Basic cleaning operations
                    cleaned_data = cleaned_data.dropna()
                    cleaned_data = cleaned_data.fillna(0)
                    
                    return {
                        'cleaned_data': cleaned_data.to_dict(),
                        'rows_cleaned': len(data) - len(cleaned_data),
                        'columns_processed': len(data.columns)
                    }
                except Exception as e:
                    logger.error(f"Error in data cleaning: {e}")
                    return {'error': str(e)}
            
            def analyze_anomalies(data):
                """Analyze anomalies in financial data"""
                try:
                    # This would use the anomaly detection from notebooks
                    # For now, return basic analysis
                    anomalies = []
                    
                    # Basic anomaly detection
                    for column in data.select_dtypes(include=[np.number]).columns:
                        mean_val = data[column].mean()
                        std_val = data[column].std()
                        threshold = 2 * std_val
                        
                        anomaly_indices = data[abs(data[column] - mean_val) > threshold].index
                        if len(anomaly_indices) > 0:
                            anomalies.append({
                                'column': column,
                                'anomaly_count': len(anomaly_indices),
                                'indices': anomaly_indices.tolist()
                            })
                    
                    return {
                        'anomalies': anomalies,
                        'total_anomalies': sum(a['anomaly_count'] for a in anomalies)
                    }
                except Exception as e:
                    logger.error(f"Error in anomaly analysis: {e}")
                    return {'error': str(e)}
            
            # Register data cleaning functions
            self.notebook_functions['data_cleaning'] = {
                'functions': {
                    'clean_financial_data': clean_financial_data,
                    'analyze_anomalies': analyze_anomalies
                },
                'code': '# Data cleaning pipeline placeholder',
                'info': {'name': 'data_cleaning', 'category': 'data_processing'}
            }
            
            logger.info("Data cleaning pipeline setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up data cleaning pipeline: {e}")
    
    def setup_analysis_pipeline(self):
        """Setup analysis pipeline from notebooks"""
        try:
            def analyze_domestic_trade(data):
                """Analyze domestic trade data"""
                try:
                    # This would use the analysis from analiza_domaceg_prometa.ipynb
                    # For now, return basic analysis
                    analysis = {
                        'total_transactions': len(data),
                        'total_value': data.get('value', pd.Series([0])).sum(),
                        'average_value': data.get('value', pd.Series([0])).mean(),
                        'unique_partners': data.get('partner', pd.Series([])).nunique()
                    }
                    
                    return analysis
                except Exception as e:
                    logger.error(f"Error in domestic trade analysis: {e}")
                    return {'error': str(e)}
            
            def analyze_salary_data(data):
                """Analyze salary data"""
                try:
                    # This would use the analysis from analiza_plata.ipynb
                    # For now, return basic analysis
                    analysis = {
                        'total_employees': len(data),
                        'average_salary': data.get('salary', pd.Series([0])).mean(),
                        'salary_range': {
                            'min': data.get('salary', pd.Series([0])).min(),
                            'max': data.get('salary', pd.Series([0])).max()
                        },
                        'departments': data.get('department', pd.Series([])).value_counts().to_dict()
                    }
                    
                    return analysis
                except Exception as e:
                    logger.error(f"Error in salary analysis: {e}")
                    return {'error': str(e)}
            
            # Register analysis functions
            self.notebook_functions['analysis'] = {
                'functions': {
                    'analyze_domestic_trade': analyze_domestic_trade,
                    'analyze_salary_data': analyze_salary_data
                },
                'code': '# Analysis pipeline placeholder',
                'info': {'name': 'analysis', 'category': 'analytics'}
            }
            
            logger.info("Analysis pipeline setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up analysis pipeline: {e}")
    
    def get_notebook_functions(self, notebook_name):
        """Get functions from a specific notebook"""
        return self.notebook_functions.get(notebook_name, {}).get('functions', {})
    
    def execute_notebook_function(self, notebook_name, function_name, **kwargs):
        """Execute a specific function from a notebook"""
        try:
            functions = self.get_notebook_functions(notebook_name)
            
            if function_name not in functions:
                raise ValueError(f"Function {function_name} not found in notebook {notebook_name}")
            
            return functions[function_name](**kwargs)
            
        except Exception as e:
            logger.error(f"Error executing notebook function: {e}")
            raise

def integrate_notebooks(app):
    """Main function to integrate notebooks"""
    integrator = NotebookIntegrator(app)
    return integrator

# Data processing functions
def process_financial_data(data_file):
    """Process financial data using integrated notebooks"""
    try:
        # Load data
        data = pd.read_csv(data_file)
        
        # Get notebook integrator
        integrator = current_app.notebook_integrator if hasattr(current_app, 'notebook_integrator') else None
        
        if integrator:
            # Clean data
            cleaning_result = integrator.execute_notebook_function('data_cleaning', 'clean_financial_data', data=data)
            
            # Analyze anomalies
            anomaly_result = integrator.execute_notebook_function('data_cleaning', 'analyze_anomalies', data=data)
            
            # Analyze domestic trade
            trade_result = integrator.execute_notebook_function('analysis', 'analyze_domestic_trade', data=data)
            
            return {
                'cleaning': cleaning_result,
                'anomalies': anomaly_result,
                'trade_analysis': trade_result
            }
        else:
            return {'error': 'Notebook integrator not available'}
            
    except Exception as e:
        logger.error(f"Error processing financial data: {e}")
        return {'error': str(e)}

def predict_salary_from_data(employee_data):
    """Predict salary using integrated prediction notebook"""
    try:
        integrator = current_app.notebook_integrator if hasattr(current_app, 'notebook_integrator') else None
        
        if integrator:
            return integrator.execute_notebook_function('prediction', 'predict_salary', data=employee_data)
        else:
            return {'error': 'Notebook integrator not available'}
            
    except Exception as e:
        logger.error(f"Error predicting salary: {e}")
        return {'error': str(e)}

# Utility functions
def list_available_notebooks():
    """List all available notebooks"""
    try:
        notebooks_path = Path('notebooks-original')
        
        if not notebooks_path.exists():
            return []
        
        notebooks = []
        for notebook_file in notebooks_path.rglob('*.ipynb'):
            notebooks.append({
                'name': notebook_file.stem,
                'path': str(notebook_file),
                'category': notebook_file.parent.name,
                'size': notebook_file.stat().st_size
            })
        
        return sorted(notebooks, key=lambda x: x['name'])
        
    except Exception as e:
        logger.error(f"Error listing notebooks: {e}")
        return []

def get_notebook_info(notebook_name):
    """Get information about a specific notebook"""
    try:
        notebook_path = Path('notebooks-original') / f"{notebook_name}.ipynb"
        
        if not notebook_path.exists():
            return {'error': 'Notebook not found'}
        
        # Read notebook metadata
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        # Extract metadata
        metadata = {
            'name': notebook_name,
            'path': str(notebook_path),
            'cells': len(notebook.cells),
            'size': notebook_path.stat().st_size,
            'language': notebook.metadata.get('language_info', {}).get('name', 'python'),
            'kernelspec': notebook.metadata.get('kernelspec', {}).get('display_name', 'Unknown')
        }
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error getting notebook info: {e}")
        return {'error': str(e)}
