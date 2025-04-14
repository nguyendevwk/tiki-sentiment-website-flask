from flask import Blueprint, request, jsonify
from utils.tiki_api import get_with_retry, TIKI_API_BASE, product_recommendations_cache

product_bp = Blueprint('product', __name__)

@product_bp.route('/api/products')
def get_products():
    keyword = request.args.get('keyword', 'all')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 30))

    params = {'limit': limit, 'page': page}
    if keyword:
        params['q'] = keyword
    else:
        params['sort'] = 'top_seller'

    try:
        data = get_with_retry(f"{TIKI_API_BASE}/products", params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@product_bp.route('/api/product/<int:product_id>')
def get_product_details(product_id):
    try:
        data = get_with_retry(f"{TIKI_API_BASE}/products/{product_id}")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@product_bp.route('/api/recommendations/<int:product_id>')
def get_recommendations(product_id):
    if product_id in product_recommendations_cache:
        return jsonify(product_recommendations_cache[product_id])
    try:
        data = get_with_retry(f"{TIKI_API_BASE}/products/{product_id}/recommendations")
        product_recommendations_cache[product_id] = data
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500
