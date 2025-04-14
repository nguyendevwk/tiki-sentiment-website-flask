from flask import Blueprint, jsonify
from utils.tiki_api import tiki_session, TIKI_API_BASE
import time

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/api-test')
def api_test():
    results = {}
    try:
        response = tiki_session.get(f"{TIKI_API_BASE}/products", params={'limit': 5})
        response.raise_for_status()
        results['products_api'] = {
            'status': 'success',
            'status_code': response.status_code
        }
    except Exception as e:
        results['products_api'] = {"status": "error", "error": str(e)}

    return jsonify({
        'test_results': results,
        'timestamp': time.time()
    })
