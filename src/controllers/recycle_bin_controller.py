"""
Recycle Bin Controller for ValidoAI
Handles API endpoints for recycle bin operations
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from src.crud.recycle_bin_crud import recycle_bin_crud
from src.utils.error_logger import log_error

logger = logging.getLogger(__name__)

recycle_bin_bp = Blueprint('recycle_bin', __name__)

@recycle_bin_bp.route('/api/recycle-bin', methods=['GET'])
def get_recycle_bin_contents():
    """Get recycle bin contents with optional filtering"""
    try:
        table_name = request.args.get('table_name')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        search = request.args.get('search')

        if search:
            success, results = recycle_bin_crud.search_recycle_bin(search, table_name)
        else:
            success, results = recycle_bin_crud.get_recycle_bin_contents(table_name, limit, offset)

        if success:
            return jsonify({
                'success': True,
                'data': results,
                'meta': {
                    'table_filter': table_name,
                    'limit': limit,
                    'offset': offset,
                    'search': search
                }
            })
        else:
            return jsonify({'success': False, 'error': results}), 400

    except Exception as e:
        log_error(e, 'recycle_bin.get_recycle_bin_contents')
        return jsonify({'success': False, 'error': str(e)}), 500

@recycle_bin_bp.route('/api/recycle-bin/stats', methods=['GET'])
def get_recycle_bin_stats():
    """Get recycle bin statistics"""
    try:
        success, stats = recycle_bin_crud.get_recycle_bin_stats()

        if success:
            return jsonify({'success': True, 'data': stats})
        else:
            return jsonify({'success': False, 'error': stats}), 400

    except Exception as e:
        log_error(e, 'recycle_bin.get_recycle_bin_stats')
        return jsonify({'success': False, 'error': str(e)}), 500

@recycle_bin_bp.route('/api/recycle-bin/restore/<recycle_bin_id>', methods=['POST'])
def restore_from_recycle_bin(recycle_bin_id):
    """Restore a record from recycle bin"""
    try:
        data = request.get_json() or {}
        restored_by = data.get('restored_by')
        restore_reason = data.get('restore_reason')

        success, result = recycle_bin_crud.restore_from_recycle_bin(
            recycle_bin_id, restored_by, restore_reason
        )

        if success:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'error': result}), 400

    except Exception as e:
        log_error(e, 'recycle_bin.restore_from_recycle_bin')
        return jsonify({'success': False, 'error': str(e)}), 500

@recycle_bin_bp.route('/api/recycle-bin/bulk-restore', methods=['POST'])
def bulk_restore_from_recycle_bin():
    """Bulk restore multiple records from recycle bin"""
    try:
        data = request.get_json()
        recycle_bin_ids = data.get('recycle_bin_ids', [])
        restored_by = data.get('restored_by')
        restore_reason = data.get('restore_reason')

        if not recycle_bin_ids:
            return jsonify({'success': False, 'error': 'No recycle bin IDs provided'}), 400

        success, result = recycle_bin_crud.bulk_restore(
            recycle_bin_ids, restored_by, restore_reason
        )

        if success:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'error': result}), 400

    except Exception as e:
        log_error(e, 'recycle_bin.bulk_restore_from_recycle_bin')
        return jsonify({'success': False, 'error': str(e)}), 500

@recycle_bin_bp.route('/api/recycle-bin/permanent-delete/<recycle_bin_id>', methods=['DELETE'])
def permanently_delete_from_recycle_bin(recycle_bin_id):
    """Permanently delete a record from recycle bin"""
    try:
        data = request.get_json() or {}
        delete_reason = data.get('delete_reason', 'Permanently deleted via API')

        success, result = recycle_bin_crud.permanently_delete(recycle_bin_id, delete_reason)

        if success:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'error': result}), 400

    except Exception as e:
        log_error(e, 'recycle_bin.permanently_delete_from_recycle_bin')
        return jsonify({'success': False, 'error': str(e)}), 500

@recycle_bin_bp.route('/api/recycle-bin/bulk-permanent-delete', methods=['DELETE'])
def bulk_permanent_delete_from_recycle_bin():
    """Bulk permanently delete multiple records from recycle bin"""
    try:
        data = request.get_json()
        recycle_bin_ids = data.get('recycle_bin_ids', [])
        delete_reason = data.get('delete_reason', 'Bulk permanently deleted via API')

        if not recycle_bin_ids:
            return jsonify({'success': False, 'error': 'No recycle bin IDs provided'}), 400

        success, result = recycle_bin_crud.bulk_permanent_delete(recycle_bin_ids, delete_reason)

        if success:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'error': result}), 400

    except Exception as e:
        log_error(e, 'recycle_bin.bulk_permanent_delete_from_recycle_bin')
        return jsonify({'success': False, 'error': str(e)}), 500

@recycle_bin_bp.route('/api/recycle-bin/empty', methods=['DELETE'])
def empty_recycle_bin():
    """Permanently delete all records in recycle bin"""
    try:
        success, result = recycle_bin_crud.empty_recycle_bin()

        if success:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'error': result}), 400

    except Exception as e:
        log_error(e, 'recycle_bin.empty_recycle_bin')
        return jsonify({'success': False, 'error': str(e)}), 500

@recycle_bin_bp.route('/api/recycle-bin/cleanup', methods=['POST'])
def cleanup_old_records():
    """Clean up old records from recycle bin"""
    try:
        data = request.get_json() or {}
        days_old = data.get('days_old', 90)

        success, result = recycle_bin_crud.cleanup_old_records(days_old)

        if success:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'error': result}), 400

    except Exception as e:
        log_error(e, 'recycle_bin.cleanup_old_records')
        return jsonify({'success': False, 'error': str(e)}), 500

@recycle_bin_bp.route('/api/recycle-bin/<recycle_bin_id>', methods=['GET'])
def get_recycle_bin_record(recycle_bin_id):
    """Get a specific record from recycle bin"""
    try:
        success, result = recycle_bin_crud.read(recycle_bin_id)

        if success and result:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'error': 'Record not found'}), 404

    except Exception as e:
        log_error(e, 'recycle_bin.get_recycle_bin_record')
        return jsonify({'success': False, 'error': str(e)}), 500

@recycle_bin_bp.route('/api/recycle-bin/tables', methods=['GET'])
def get_available_tables():
    """Get list of tables that have records in recycle bin"""
    try:
        success, stats = recycle_bin_crud.get_recycle_bin_stats()

        if success and 'records_by_table' in stats:
            tables = [record['table_name'] for record in stats['records_by_table']]
            return jsonify({'success': True, 'data': sorted(list(set(tables)))})
        else:
            return jsonify({'success': False, 'error': 'Unable to fetch table list'}), 400

    except Exception as e:
        log_error(e, 'recycle_bin.get_available_tables')
        return jsonify({'success': False, 'error': str(e)}), 500
