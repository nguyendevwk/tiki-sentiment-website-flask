# from flask import Blueprint, request, jsonify, send_from_directory
# import time
# from services.tiki_service import TikiService

# # Create blueprint
# product_bp = Blueprint('product', __name__)
# tiki_service = TikiService()

# @product_bp.route('/products', methods=['GET'])
# def get_products():
#     keyword = request.args.get('keyword', 'all')
#     page = int(request.args.get('page', 1))
#     limit = int(request.args.get('limit', 30))

#     try:
#         data = tiki_service.get_products(keyword, page, limit)
#         return jsonify(data)
#     except Exception as e:
#         return jsonify({"error": str(e), "status": "error"}), 500

# @product_bp.route('/product/<int:product_id>', methods=['GET'])
# def get_product_details(product_id):
#     try:
#         data = tiki_service.get_product_details(product_id)
#         return jsonify(data)
#     except Exception as e:
#         return jsonify({"error": str(e), "status": "error"}), 500

# @product_bp.route('/recommendations/<int:product_id>', methods=['GET'])
# def get_recommendations(product_id):
#     # Đây là hàm get_recommendations cũ, sẽ được thay thế bởi vector_db trong file riêng
#     # Nhưng chúng ta giữ nó ở đây để tương thích ngược
#     try:
#         # Giả lập dữ liệu gợi ý
#         data = {
#             "data": [],
#             "status": "success"
#         }
#         return jsonify(data)
#     except Exception as e:
#         return jsonify({"error": str(e), "status": "error"}), 500

# @product_bp.route('/debug/api-test', methods=['GET'])
# def api_test():
#     """Test endpoint to check API connectivity"""
#     test_results = tiki_service.test_api_connectivity()

#     return jsonify({
#         'test_results': test_results,
#         'headers_used': dict(tiki_service.session.headers),
#         'timestamp': time.time()
#     })


from flask import Blueprint, request, jsonify, send_from_directory
import time

# Create blueprint
def create_product_blueprint(tiki_service):
    product_bp = Blueprint('product', __name__)

    @product_bp.route('/products', methods=['GET'])
    def get_products():
        keyword = request.args.get('keyword', 'all')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 30))

        try:
            data = tiki_service.get_products(keyword, page, limit)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e), "status": "error"}), 500

    @product_bp.route('/product/<int:product_id>', methods=['GET'])
    def get_product_details(product_id):
        try:
            data = tiki_service.get_product_details(product_id)
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

    return product_bp