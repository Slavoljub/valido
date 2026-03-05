"""
RESTful API Endpoints for ValidoAI Models
This file contains RESTful API endpoints for various AI and financial models
"""

from flask import Blueprint, request, jsonify, session, current_app
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import json
import time
import logging
from functools import wraps

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Initialize extensions
cache = Cache()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# Setup logging
logger = logging.getLogger(__name__)

# Decorators for optimization
def cache_response(timeout=300):
    """Cache decorator for API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create cache key based on function name and arguments
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            return result
        return decorated_function
    return decorator

def rate_limit(limit_string):
    """Rate limiting decorator"""
    def decorator(f):
        @limiter.limit(limit_string)
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json(*required_fields):
    """JSON validation decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Content-Type must be application/json',
                    'status': 'error'
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'Invalid JSON data',
                    'status': 'error'
                }), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}',
                    'status': 'error'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def handle_errors(f):
    """Error handling decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error',
                'message': str(e) if current_app.debug else 'An error occurred'
            }), 500
    return decorated_function

# ============================================================================
# Financial Analysis Endpoints
# ============================================================================

@api_bp.route('/financial/ai-sveska', methods=['GET'])
@cache_response(timeout=300)
@handle_errors
def get_ai_sveska():
    """Get AI financial notebook analysis"""
    try:
        from src.models.ai_finansije import (
            generisi_ai_svesku_sa_trendom,
            ucitaj_dobavljace_putanja,
            ucitaj_plate_putanja
        )
        
        # Get paths from query parameters or use defaults
        dobavljaci_path = request.args.get(
            'dobavljaci_path', 
            'data/mom21/specifikacija_dobavljaca/specifikacija_dobavljaca_ai.csv'
        )
        plate_path = request.args.get(
            'plate_path', 
            'data/mom21/plate/plate_2024.csv'
        )
        godina = request.args.get('godina', '2024')
        
        # Load data
        df_dobavljaci = ucitaj_dobavljace_putanja(dobavljaci_path)
        df_plate = ucitaj_plate_putanja(plate_path)
        
        # Generate analysis
        result = generisi_ai_svesku_sa_trendom(df_dobavljaci, df_plate, godina)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in get_ai_sveska: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/financial/cashflow', methods=['GET'])
@cache_response(timeout=300)
@handle_errors
def get_cashflow_analysis():
    """Get cashflow analysis"""
    try:
        from src.models.cashflow import obradi_fakture_2024
        
        # Generate analysis
        result = obradi_fakture_2024()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in get_cashflow_analysis: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/financial/bilans', methods=['POST'])
@rate_limit("10 per hour")
@validate_json('csv_path')
@handle_errors
def analyze_bilans():
    """Analyze balance sheet"""
    try:
        from src.models.valido_bilans_ai import prepare_bilans_stanja_pregled, gpt_komentar_bilansa
        
        data = request.get_json()
        csv_path = data['csv_path']
        api_key = data.get('api_key', os.getenv('OPENAI_API_KEY'))
        
        # Prepare and analyze data
        df = prepare_bilans_stanja_pregled(csv_path)
        komentar = gpt_komentar_bilansa(df, api_key)
        
        # Convert DataFrame to dict for JSON serialization
        df_dict = {
            'columns': df.columns.tolist(),
            'data': df.values.tolist()
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'dataframe': df_dict,
                'komentar': komentar
            }
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_bilans: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/financial/zakljucni-list', methods=['GET'])
@cache_response(timeout=300)
@handle_errors
def get_zakljucni_list_analysis():
    """Get zakljucni list analysis"""
    try:
        from src.models.zakljucni_analysis import parse_zakljucni_list, generate_financial_commentary
        
        # Parse data
        rezultati = parse_zakljucni_list()
        
        # Generate commentary
        komentar = generate_financial_commentary(rezultati)
        
        return jsonify({
            'status': 'success',
            'data': {
                'rezultati': rezultati,
                'komentar': komentar
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_zakljucni_list_analysis: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# Salary Analysis Endpoints
# ============================================================================

@api_bp.route('/salary/details', methods=['GET'])
@cache_response(timeout=60)
@handle_errors
def get_salary_details():
    """Get salary details for an employee"""
    try:
        from src.models.get_salary_details import obracun_zarade
        
        zaposleni = request.args.get('zaposleni')
        mesec = request.args.get('mesec')
        
        if not zaposleni or not mesec:
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameters: zaposleni, mesec'
            }), 400
        
        # Get salary details
        result = obracun_zarade(None, zaposleni, mesec)
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in get_salary_details: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/salary/trends', methods=['GET'])
@cache_response(timeout=300)
@handle_errors
def analyze_salary_trends():
    """Analyze salary trends"""
    try:
        from src.models.get_salary_details import analyze_bruto2_trends
        
        csv_path = request.args.get(
            'csv_path', 
            'data/mom21/plate/mom21_plate_2024_bruto2_sorted.csv'
        )
        firma_tip = request.args.get('firma_tip', 'mala firma')
        
        # Analyze trends
        result = analyze_bruto2_trends(csv_path, firma_tip)
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_salary_trends: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/salary/anomalies', methods=['GET'])
@cache_response(timeout=300)
@handle_errors
def detect_salary_anomalies():
    """Detect anomalies in salary data"""
    try:
        from src.models.anomaly_analysis import analiziraj_anomalije
        
        csv_path = request.args.get(
            'csv_path', 
            'data/mom21/plate/mom21_plate_2024.csv'
        )
        xml_folder_path = request.args.get(
            'xml_folder_path', 
            'data/mom21/pppd/'
        )
        
        # Analyze anomalies
        result = analiziraj_anomalije(csv_path, xml_folder_path)
        
        # Convert DataFrame to dict for JSON serialization
        result_dict = {
            'columns': result.columns.tolist(),
            'data': result.values.tolist()
        }
        
        return jsonify({
            'status': 'success',
            'data': result_dict
        })
        
    except Exception as e:
        logger.error(f"Error in detect_salary_anomalies: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/salary/etl', methods=['POST'])
@rate_limit("5 per hour")
@validate_json('pdf_folder')
@handle_errors
def etl_salary_data():
    """Extract, transform and load salary data from PDF files"""
    try:
        from src.models.etl_plate import etl_plate_folder
        
        data = request.get_json()
        folder_path = data['pdf_folder']
        output_csv = data.get('output_csv', 'mom21_plate_2024_bruto2_sorted.csv')
        save_csv = data.get('save_csv', True)
        
        # Process PDF files
        result = etl_plate_folder(folder_path, save_csv, output_csv)
        
        # Convert DataFrame to dict for JSON serialization
        result_dict = {
            'columns': result.columns.tolist(),
            'data': result.values.tolist(),
            'output_csv': output_csv if save_csv else None
        }
        
        return jsonify({
            'status': 'success',
            'data': result_dict
        })
        
    except Exception as e:
        logger.error(f"Error in etl_salary_data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# AI Provider Endpoints
# ============================================================================

@api_bp.route('/ai/providers', methods=['GET'])
@cache_response(timeout=300)
@handle_errors
def get_ai_providers():
    """Get available AI providers"""
    try:
        from src.models.ai_providers import AIProviderManager
        
        provider_manager = AIProviderManager()
        providers = provider_manager.get_available_providers()
        
        return jsonify({
            'status': 'success',
            'data': providers
        })
        
    except Exception as e:
        logger.error(f"Error in get_ai_providers: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/ai/providers/status', methods=['GET'])
@cache_response(timeout=60)
@handle_errors
def get_ai_providers_status():
    """Get status of all AI providers"""
    try:
        from src.models.ai_providers import AIProviderManager
        
        provider_manager = AIProviderManager()
        status = provider_manager.get_provider_status()
        
        return jsonify({
            'status': 'success',
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error in get_ai_providers_status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/ai/providers/<provider>/test', methods=['POST'])
@rate_limit("5 per hour")
@handle_errors
def test_ai_provider(provider):
    """Test specific AI provider"""
    try:
        from src.models.ai_providers import AIProviderManager
        
        provider_manager = AIProviderManager()
        result = provider_manager.test_provider(provider)
        
        return jsonify({
            'status': 'success',
            'data': {
                'provider': provider,
                'test_result': result
            }
        })
        
    except Exception as e:
        logger.error(f"Error in test_ai_provider: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/ai/providers/<provider>/models', methods=['GET'])
@cache_response(timeout=600)
@handle_errors
def get_provider_models(provider):
    """Get available models for specific AI provider"""
    try:
        from src.models.ai_providers import AIProviderManager
        
        provider_manager = AIProviderManager()
        models = provider_manager.get_provider_models(provider)
        
        return jsonify({
            'status': 'success',
            'data': {
                'provider': provider,
                'models': models
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_provider_models: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/ai/providers', methods=['POST'])
@rate_limit("5 per hour")
@validate_json('provider', 'api_key')
@handle_errors
def add_ai_provider():
    """Add or update AI provider configuration"""
    try:
        from src.models.ai_providers import AIProviderManager
        
        data = request.get_json()
        provider = data['provider']
        api_key = data['api_key']
        config = data.get('config', {})
        
        provider_manager = AIProviderManager()
        result = provider_manager.add_provider(provider, api_key, config)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in add_ai_provider: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# Financial Models Endpoints
# ============================================================================

@api_bp.route('/financial/analysis', methods=['POST'])
@rate_limit("10 per hour")
@validate_json('message')
@handle_errors
def financial_analysis():
    """Get financial analysis using AI models"""
    try:
        from src.models.financial_models import FinancialAnalyzer
        from src.models.ai_models import OpenAIWrapper
        
        data = request.get_json()
        message = data['message']
        
        # Initialize components
        openai_wrapper = OpenAIWrapper()
        financial_analyzer = FinancialAnalyzer(openai_wrapper)
        
        # Process request
        result = financial_analyzer.process_request(message)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in financial_analysis: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/financial/salary-analysis', methods=['POST'])
@rate_limit("10 per hour")
@validate_json('message')
@handle_errors
def salary_analysis():
    """Get salary analysis using AI models"""
    try:
        from src.models.financial_models import SalaryAnalyzer
        from src.models.ai_models import OpenAIWrapper
        
        data = request.get_json()
        message = data['message']
        
        # Initialize components
        openai_wrapper = OpenAIWrapper()
        salary_analyzer = SalaryAnalyzer(openai_wrapper)
        
        # Process request
        result = salary_analyzer.process_request(message)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in salary_analysis: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# OpenAI Models Endpoints
# ============================================================================

@api_bp.route('/openai/search-suppliers', methods=['POST'])
@rate_limit("10 per hour")
@validate_json('supplier_name')
@handle_errors
def search_similar_suppliers():
    """Find similar suppliers using OpenAI embeddings"""
    try:
        from src.models.openai_models import find_similar_suppliers_gpt
        
        data = request.get_json()
        supplier_name = data['supplier_name']
        top_n = data.get('top_n', 5)
        
        # Search for similar suppliers
        result = find_similar_suppliers_gpt(supplier_name, top_n)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in search_similar_suppliers: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/openai/predict-revenue', methods=['GET'])
@cache_response(timeout=300)
@handle_errors
def predict_revenue():
    """Predict revenue using OpenAI models"""
    try:
        from src.models.openai_models import predikcija_domaceg_prometa
        
        # Generate prediction
        result = predikcija_domaceg_prometa()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in predict_revenue: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/openai/analyze-month', methods=['POST'])
@rate_limit("20 per hour")
@validate_json('month')
@handle_errors
def analyze_month():
    """Analyze revenue for a specific month"""
    try:
        from src.models.openai_models import generisi_analizu
        
        data = request.get_json()
        month = int(data['month'])
        
        if month < 1 or month > 12:
            return jsonify({
                'status': 'error',
                'message': 'Month must be between 1 and 12'
            }), 400
        
        # Generate analysis
        result = generisi_analizu(month)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_month: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/openai/tax-analysis', methods=['POST'])
@rate_limit("10 per hour")
@validate_json('message')
@handle_errors
def analyze_tax_regulations():
    """Analyze tax regulations using OpenAI models"""
    try:
        from src.models.openai_models import analyze_poreski_propisi
        
        data = request.get_json()
        message = data['message']
        
        # Generate analysis
        result = analyze_poreski_propisi(message)
        
        return jsonify({
            'status': 'success',
            'data': {
                'analysis': result
            }
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_tax_regulations: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def register_api_endpoints(app):
    """Register API endpoints with the Flask app"""
    app.register_blueprint(api_bp)
    
    # Initialize extensions
    cache.init_app(app)
    limiter.init_app(app)
