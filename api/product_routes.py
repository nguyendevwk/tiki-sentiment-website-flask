# api/product_routes.py
# -*- coding: utf-8 -*-
''''
Created on 2023-10-01 12:00:00
author: nguyendevwk
'''
from flask import Blueprint, request, jsonify, send_from_directory
import time
from services.product_history_manager import ProductHistoryManager

history_manager = ProductHistoryManager()
DEFAULT_USER_ID = 'anonymous'

# Create blueprint
def create_product_blueprint(tiki_service):
    product_bp = Blueprint('product', __name__)

    @product_bp.route('/products', methods=['GET'])
    def get_products():
        keyword = request.args.get('keyword', 'all')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 30))
        user_id = request.args.get('user_id', 'anonymous')
        # user_id = request.args.get('user_id', DEFAULT_USER_ID)

        try:
            data = tiki_service.get_products(keyword, page, limit)
            # Lưu keyword vào lịch sử
            history_manager.log_keyword(user_id, keyword)
            # Lưu lịch sử truy cập sản phẩm

            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e), "status": "error"}), 500

    @product_bp.route('/product/<int:product_id>', methods=['GET'])
    def get_product_details(product_id):
        try:
            data = tiki_service.get_product_details(product_id)
            history_manager.log_keyword(DEFAULT_USER_ID, data.get('name', ''))
            if not data or 'error' in data:
                return jsonify({"error": "Product not found", "status": "error"}), 404

            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e), "status": "error"}), 500

    @product_bp.route('/debug/api-test', methods=['GET'])
    def api_test():
        """Test endpoint to check API connectivity"""
        test_results = tiki_service.test_api_connectivity()

        return jsonify({
            'test_results': test_results,
            'headers_used': dict(tiki_service.session.headers),
            'timestamp': time.time()
        })
    @product_bp.route('/user/<user_id>/history', methods=['GET'])
    def get_user_history(user_id):
        user_history = history_manager.get_user_history(user_id)
        return jsonify({
            "user_id": user_id,
            "history": user_history,
            "status": "success"
        })

    return product_bp