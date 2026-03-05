"""
API Endpoints
============

REST API endpoints for ValidoAI system.
"""

import json
from flask import Blueprint, request, jsonify
from src.core.decorators import handle_template_errors

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ============================================================================
# SYSTEM STATS API
# ============================================================================

@api_bp.route('/system/stats')
def api_system_stats():
    """Get comprehensive system statistics"""
    try:
        from src.database.connection import get_db_connection
        from src.database.operations import get_db_cursor
        from src.database.stats import get_database_stats

        conn = get_db_connection()
        cur = get_db_cursor(conn)

        stats = get_database_stats(conn, cur)

        # Add additional system stats
        from src.core.system_info import get_system_info
        system_info = get_system_info()

        stats.update(system_info)

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting system stats: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ANALYTICS API
# ============================================================================

@api_bp.route('/analytics/dashboard')
def get_dashboard_data():
    """Get dashboard analytics data"""
    try:
        from src.analytics.dashboard import get_dashboard_data

        data = get_dashboard_data()
        return jsonify({
            'success': True,
            'data': data
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/revenue-forecast')
def get_revenue_forecast():
    """Get revenue forecasting data"""
    try:
        from src.analytics.predictive import get_revenue_forecast

        forecast_data = get_revenue_forecast()
        return jsonify({
            'success': True,
            'data': forecast_data
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting revenue forecast: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/customer-insights')
def get_customer_insights():
    """Get customer insights and analytics"""
    try:
        from src.analytics.predictive import get_customer_insights

        insights = get_customer_insights()
        return jsonify({
            'success': True,
            'data': insights
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting customer insights: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/inventory-optimization')
def get_inventory_optimization():
    """Get inventory optimization recommendations"""
    try:
        from src.analytics.predictive import get_inventory_optimization

        optimization_data = get_inventory_optimization()
        return jsonify({
            'success': True,
            'data': optimization_data
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting inventory optimization: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CHAT API
# ============================================================================

@api_bp.route('/chat/message', methods=['POST'])
def send_chat_message():
    """Send a chat message"""
    try:
        from src.controllers.chat_controller import process_chat_message

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        session_id = data.get('session_id')

        response = process_chat_message(message, user_id, session_id)

        return jsonify({
            'success': True,
            'response': response
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error processing chat message: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/chat/history/<session_id>')
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        from src.controllers.chat_controller import get_chat_history

        history = get_chat_history(session_id)
        return jsonify({
            'success': True,
            'history': history
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting chat history: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CONTENT MANAGEMENT API
# ============================================================================

@api_bp.route('/content/upload', methods=['POST'])
def upload_content():
    """Upload content file"""
    try:
        from src.content.manager import upload_file

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400

        # Get form data
        user_id = request.form.get('user_id', 'anonymous')
        category = request.form.get('category', 'general')
        metadata = json.loads(request.form.get('metadata', '{}'))

        # Upload file
        result = upload_file(file, user_id, category, metadata)

        if result.get('success'):
            return jsonify({
                'success': True,
                'content_id': result['content_id'],
                'content': result['content'],
                'message': 'File uploaded successfully'
            }), 201
        else:
            return jsonify({'error': result.get('error', 'Upload failed')}), 400

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error uploading content: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/content/list', methods=['GET'])
def list_content():
    """List content files"""
    try:
        from src.content.manager import list_content

        user_id = request.args.get('user_id')
        category = request.args.get('category')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        result = list_content(user_id, category, limit, offset)

        return jsonify({
            'success': True,
            'content': result['content'],
            'total': result['total'],
            'limit': limit,
            'offset': offset,
            'has_more': result['has_more']
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error listing content: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/content/search', methods=['GET'])
def search_content():
    """Search content files"""
    try:
        from src.content.manager import search_content

        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Search query required'}), 400

        user_id = request.args.get('user_id')
        category = request.args.get('category')

        results = search_content(query, user_id, category)

        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total': len(results)
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error searching content: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/content/<content_id>', methods=['GET'])
def get_content_info(content_id):
    """Get content information"""
    try:
        from src.content.manager import get_content

        content = get_content(content_id)
        if not content:
            return jsonify({'error': 'Content not found'}), 404

        return jsonify({
            'success': True,
            'content': content
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting content {content_id}: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/content/<content_id>/download', methods=['GET'])
def download_content(content_id):
    """Download content file"""
    try:
        from src.content.manager import get_content_file
        from flask import send_file

        result = get_content_file(content_id)
        if not result:
            return jsonify({'error': 'Content not found'}), 404

        file_path, filename = result

        # Update download count (optional)
        # You might want to track downloads in the content record

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetypes.guess_type(filename)[0]
        )

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error downloading content {content_id}: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/content/<content_id>/view', methods=['GET'])
def view_content(content_id):
    """View content file inline"""
    try:
        from src.content.manager import get_content_file
        from flask import send_file

        result = get_content_file(content_id)
        if not result:
            return jsonify({'error': 'Content not found'}), 404

        file_path, filename = result

        return send_file(
            file_path,
            as_attachment=False,
            download_name=filename,
            mimetype=mimetypes.guess_type(filename)[0]
        )

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error viewing content {content_id}: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/content/<content_id>', methods=['DELETE'])
def delete_content_route(content_id):
    """Delete content file"""
    try:
        from src.content.manager import delete_content

        user_id = request.args.get('user_id')  # For permission checking
        result = delete_content(content_id, user_id)

        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Content deleted successfully',
                'content_id': content_id
            })
        else:
            return jsonify({'error': result.get('error', 'Delete failed')}), 400

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error deleting content {content_id}: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/content/stats', methods=['GET'])
def get_content_stats():
    """Get content statistics"""
    try:
        from src.content.manager import get_content_stats

        stats = get_content_stats()

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting content stats: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SENTIMENT ANALYSIS API
# ============================================================================

@api_bp.route('/sentiment/analyze', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment of text"""
    try:
        from src.ai.sentiment import sentiment_analyzer

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'Text is required'}), 400

        method = data.get('method', 'hybrid')
        include_details = data.get('include_details', False)

        # Analyze sentiment
        result = sentiment_analyzer.analyze_text(text, method=method, include_details=include_details)

        return jsonify({
            'success': True,
            'analysis': result,
            'input_text': text[:100] + '...' if len(text) > 100 else text,
            'method': method
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error analyzing sentiment: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sentiment/batch', methods=['POST'])
def analyze_sentiment_batch():
    """Analyze sentiment for multiple texts"""
    try:
        from src.ai.sentiment import sentiment_analyzer

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        texts = data.get('texts', [])
        if not texts:
            return jsonify({'error': 'Texts array is required'}), 400

        if len(texts) > 100:
            return jsonify({'error': 'Maximum 100 texts per batch'}), 400

        method = data.get('method', 'hybrid')

        # Analyze batch
        results = sentiment_analyzer.analyze_batch(texts, method=method)

        return jsonify({
            'success': True,
            'results': results,
            'total': len(results),
            'method': method
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error in batch sentiment analysis: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sentiment/stats', methods=['GET'])
def get_sentiment_stats():
    """Get sentiment analysis statistics"""
    try:
        from src.ai.sentiment import sentiment_analyzer

        stats = sentiment_analyzer.get_statistics()

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting sentiment stats: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sentiment/cache/clear', methods=['POST'])
def clear_sentiment_cache():
    """Clear sentiment analysis cache"""
    try:
        from src.ai.sentiment import sentiment_analyzer

        result = sentiment_analyzer.clear_cache()

        return jsonify(result)

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error clearing sentiment cache: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sentiment/methods', methods=['GET'])
def get_sentiment_methods():
    """Get available sentiment analysis methods"""
    try:
        methods = {
            'afinn': {
                'name': 'AFINN',
                'description': 'AFINN-165 lexicon-based sentiment analysis',
                'pros': ['Fast', 'Simple', 'Well-established'],
                'cons': ['Limited vocabulary', 'No context awareness']
            },
            'vader': {
                'name': 'VADER',
                'description': 'VADER (Valence Aware Dictionary and sEntiment Reasoner)',
                'pros': ['Handles punctuation', 'Emojis support', 'Slang handling'],
                'cons': ['English only', 'Limited customization']
            },
            'custom': {
                'name': 'Custom Business Lexicon',
                'description': 'Custom lexicon optimized for business and technical domains',
                'pros': ['Domain-specific', 'Business terminology', 'Customizable'],
                'cons': ['Limited coverage', 'Manual maintenance']
            },
            'hybrid': {
                'name': 'Hybrid Analysis',
                'description': 'Combines multiple methods for improved accuracy',
                'pros': ['Best accuracy', 'Multiple perspectives', 'Robust results'],
                'cons': ['Slower processing', 'More complex']
            }
        }

        return jsonify({
            'success': True,
            'methods': methods,
            'recommended': 'hybrid'
        })

    except Exception as e:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting sentiment methods: {e}")
        return jsonify({'error': str(e)}), 500
