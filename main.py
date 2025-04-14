# # import joblib
# # import numpy as np
# # from tensorflow.keras.preprocessing.sequence import pad_sequences
# # import pickle
# # from sklearn.feature_extraction.text import TfidfVectorizer
# # from keras.models import load_model
# # import os
# # os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# # max_len = 100
# # # --- Load mô hình đã lưu ---
# # nb_model = joblib.load('models/naive_bayes_model.pkl')
# # svm_model = joblib.load('models/linear_svc_model.pkl')
# # svc_model = joblib.load('models/svc_model.pkl')
# # tfidf = joblib.load('models/tfidf_vectorizer.pkl')
# # label_encoder = joblib.load('models/label_encoder.pkl')

# # # --- Văn bản mới cần phân loại ---
# # new_texts = [
# #     "Sản phẩm này rất tệ",
# #     "Dịch vụ tuyệt vời và nhanh chóng",
# #     "Chất lượng trung bình, không quá đặc biệt"
# # ]

# # # --- Vector hóa văn bản ---
# # new_tfidf = tfidf.transform(new_texts)

# # # --- Dự đoán ---
# # pred_nb = nb_model.predict(new_tfidf)
# # pred_svm = svm_model.predict(new_tfidf)
# # pred_svc = svc_model.predict(new_tfidf)

# # # --- Giải mã nhãn ---
# # decoded_nb = label_encoder.inverse_transform(pred_nb)
# # decoded_svm = label_encoder.inverse_transform(pred_svm)
# # decoded_svc = label_encoder.inverse_transform(pred_svc)

# # # --- In kết quả ---
# # for i in range(len(new_texts)):
# #     print(f"\n📄 Văn bản: {new_texts[i]}")

# #     # Naive Bayes (có hỗ trợ predict_proba)
# #     prob_nb = nb_model.predict_proba(new_tfidf[i])[0]
# #     confidence_nb = np.max(prob_nb) * 100
# #     print(f"  🤖 Naive Bayes → {decoded_nb[i]} ({confidence_nb:.2f}%)")

# #     # Linear SVC không hỗ trợ xác suất — ta chỉ hiển thị nhãn
# #     print(f"  🧠 Linear SVC  → {decoded_svm[i]} (không có xác suất)")

# #     # SVC với xác suất
# #     if hasattr(svc_model, "predict_proba"):
# #         prob_svc = svc_model.predict_proba(new_tfidf[i])[0]
# #         confidence_svc = np.max(prob_svc) * 100
# #         print(f"  🚀 SVC         → {decoded_svc[i]} ({confidence_svc:.2f}%)")
# #     else:
# #         print(f"  🚀 SVC         → {decoded_svc[i]} (không có xác suất)")


# # import tensorflow as tf

# # print("TensorFlow version:", tf.__version__)
# # print("Num GPUs Available:", len(tf.config.list_physical_devices('GPU')))
# # # tf.debugging.set_log_device_placement(True)

# # # Load mô hình
# # model = load_model("models/text_classification_model.h5")

# # # Load tokenizer
# # with open("models/tokenizer.pkl", "rb") as f:
# #     tokenizer = pickle.load(f)

# # # Tiền xử lý dữ liệu mới (ví dụ)
# # new_texts = ["sản phẩm cực bình thường nhưng dùng rất tốt và hiệu quả đáng tiền"]
# # new_sequences = tokenizer.texts_to_sequences(new_texts)
# # new_pad = pad_sequences(new_sequences, maxlen=max_len, padding='post', truncating='post')

# # # Dự đoán
# # predictions = model.predict(new_pad)
# # predicted_class = predictions.argmax(axis=-1)
# # print(f"Dự đoán nhãn: {predicted_class}")
# from flask import Flask, render_template, send_from_directory
# import os
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# # Import models
# from models.loaders import load_sentiment_models

# # Import services
# from services.sentiment_service import SentimentService
# from services.search_service import integrate_with_flask_app

# # Import blueprints
# from api.product_routes import product_bp
# from api.review_routes import review_bp, set_sentiment_service as set_review_sentiment_service
# from api.sentiment_routes import sentiment_bp, set_sentiment_service as set_sentiment_routes_service

# # Import config
# from config import DEBUG

# # Initialize Flask app
# app = Flask(__name__)

# # Register blueprints
# app.register_blueprint(product_bp, url_prefix='/api')
# app.register_blueprint(review_bp, url_prefix='/api')
# app.register_blueprint(sentiment_bp, url_prefix='/api')

# # Serve static files
# @app.route('/css/<path:filename>')
# def serve_css(filename):
#     return send_from_directory('templates/css', filename)

# @app.route('/js/<path:filename>')
# def serve_js(filename):
#     return send_from_directory('templates/js', filename)

# # Main route
# @app.route('/')
# def index():
#     return render_template('index.html')

# def integrate_with_flask_app(app):
#     """Tích hợp SearchService với Flask app"""
#     logger.debug("--- Integrating SearchService with Flask app ---")
#     search_service = SearchService()

#     @app.route('/api/recommendations/<int:product_id>', methods=['GET'])
#     def get_recommendations(product_id):
#         logger.debug(f"--- Processing request for /api/recommendations/{product_id} ---")
#         if search_service.index is None or search_service.df is None or search_service.product_ids is None:
#             logger.error("Vector database not initialized")
#             return jsonify({
#                 "error": "Vector database not initialized",
#                 "status": "error"
#             }), 500

#         try:
#             limit = int(request.args.get('limit', 10))
#             if limit < 1 or limit > 50:
#                 logger.warning(f"Invalid limit value: {limit}. Using default limit of 10.")
#                 limit = 10
#             logger.debug(f"Limit set to: {limit}")

#             similar_products = search_service.get_similar_products_by_id(product_id, top_k=limit)
#             logger.debug(f"get_similar_products_by_id returned {len(similar_products)} products")

#             if not similar_products:
#                 logger.warning(f"No similar products found for product_id: {product_id}")
#                 if search_service.df is not None and len(search_service.df) > 0:
#                     logger.debug("Falling back to random products")
#                     random_products = search_service.df.sample(n=min(limit, len(search_service.df)), replace=False).to_dict('records')
#                     logger.debug(f"Selected {len(random_products)} random products")
#                     return jsonify({
#                         "data": random_products,
#                         "status": "success",
#                         "note": "random_fallback"
#                     }), 200
#                 else:
#                     logger.debug("No products available for fallback")
#                     return jsonify({
#                         "data": [],
#                         "status": "success",
#                         "note": "no_data_available"
#                     }), 200

#             logger.debug("Preparing response with similar products")
#             response = {
#                 "data": similar_products,
#                 "status": "success"
#             }
#             logger.debug(f"Response data: {response}")
#             logger.debug(f"--- Completed request for /api/recommendations/{product_id} ---")
#             return jsonify(response), 200
#         except Exception as e:
#             logger.error(f"Error in /api/recommendations/{product_id}: {str(e)}")
#             return jsonify({
#                 "error": f"Failed to fetch recommendations: {str(e)}",
#                 "status": "error"
#             }), 500

#     @app.route('/api/search', methods=['GET'])
#     def search_products():
#         logger.debug("--- Processing request for /api/search ---")
#         try:
#             query = request.args.get('q', '')
#             limit = int(request.args.get('limit', 10))
#             if limit < 1 or limit > 50:
#                 logger.warning(f"Invalid limit value: {limit}. Using default limit of 10.")
#                 limit = 10
#             logger.debug(f"Query: {query}, Limit: {limit}")

#             if not query:
#                 logger.warning("Empty search query received")
#                 return jsonify({
#                     "error": "No search query provided",
#                     "status": "error"
#                 }), 400

#             if search_service.index is None or search_service.df is None or search_service.product_ids is None:
#                 logger.error("Vector database not initialized")
#                 return jsonify({
#                     "error": "Vector database not initialized",
#                     "status": "error"
#                 }), 500

#             result_products = search_service.search_products_by_text(query, top_k=limit)
#             logger.debug(f"search_products_by_text returned {len(result_products)} products")

#             response = {
#                 "data": result_products,
#                 "status": "success"
#             }
#             logger.debug(f"Response data: {response}")
#             logger.debug("--- Completed request for /api/search ---")
#             return jsonify(response), 200
#         except Exception as e:
#             logger.error(f"Error in /api/search: {str(e)}")
#             return jsonify({
#                 "error": f"Failed to fetch search results: {str(e)}",
#                 "status": "error"
#             }), 500

# # Initialize application
# def init_app():
#     # Load models
#     models = load_sentiment_models()

#     # Initialize sentiment service
#     sentiment_service = SentimentService(models)

#     # Set sentiment service for review and sentiment routes
#     set_review_sentiment_service(sentiment_service)
#     set_sentiment_routes_service(sentiment_service)
#     integrate_with_flask_app(app)
#     # Initialize vector database for product recommendations

#     return app

# # Create app instance
# app = init_app()

# # Run the app
# if __name__ == '__main__':
#     app.run(debug=DEBUG)

# from flask import Flask, render_template, send_from_directory
# import os
# from models.loaders import load_sentiment_models
# from services.sentiment_service import SentimentService
# from api.product_routes import product_bp
# from api.review_routes import review_bp, set_sentiment_service as set_review_sentiment_service
# from api.sentiment_routes import sentiment_bp, set_sentiment_service as set_sentiment_routes_service
# from api.search_routes import search_bp
# import logging

# # Thiết lập logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Vô hiệu hóa oneDNN để tránh warning TensorFlow
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# # Khởi tạo Flask app
# app = Flask(__name__)

# # Định nghĩa các route tĩnh
# @app.route('/css/<path:filename>')
# def serve_css(filename):
#     return send_from_directory('templates/css', filename)

# @app.route('/js/<path:filename>')
# def serve_js(filename):
#     return send_from_directory('templates/js', filename)

# @app.route('/')
# def index():
#     return render_template('index.html')

# # Khởi tạo ứng dụng
# def init_app():
#     logger.debug("--- Initializing Flask application ---")

#     # Load sentiment models
#     try:
#         logger.debug("Loading sentiment models")
#         models = load_sentiment_models()
#     except Exception as e:
#         logger.error(f"Failed to load sentiment models: {str(e)}")
#         models = None

#     # Initialize sentiment service
#     try:
#         logger.debug("Initializing SentimentService")
#         sentiment_service = SentimentService(models)
#         set_review_sentiment_service(sentiment_service)
#         set_sentiment_routes_service(sentiment_service)
#     except Exception as e:
#         logger.error(f"Failed to initialize SentimentService: {str(e)}")
#         sentiment_service = None

#     # Register blueprints
#     logger.debug("Registering blueprints")
#     app.register_blueprint(product_bp, url_prefix='/api')
#     app.register_blueprint(review_bp, url_prefix='/api')
#     app.register_blueprint(sentiment_bp, url_prefix='/api')
#     app.register_blueprint(search_bp, url_prefix='/api')

#     return app

# # Tạo app instance
# app = init_app()

# # Chạy ứng dụng
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, render_template, send_from_directory
import os
from models.loaders import load_sentiment_models
from services.sentiment_service import SentimentService
from services.tiki_service import TikiService
from api.product_routes import create_product_blueprint
from api.review_routes import review_bp, set_sentiment_service as set_review_sentiment_service
from api.sentiment_routes import sentiment_bp, set_sentiment_service as set_sentiment_routes_service
from api.search_routes import create_search_blueprint
import logging

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Vô hiệu hóa oneDNN để tránh warning TensorFlow
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Khởi tạo Flask app
app = Flask(__name__)

# Định nghĩa các route tĩnh
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('templates/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('templates/js', filename)

@app.route('/')
def index():
    return render_template('index.html')

# Khởi tạo ứng dụng
def init_app():
    logger.debug("--- Initializing Flask application ---")

    # Khởi tạo TikiService chung
    logger.debug("Initializing TikiService")
    tiki_service = TikiService()

    # Load sentiment models
    try:
        logger.debug("Loading sentiment models")
        models = load_sentiment_models()
    except Exception as e:
        logger.error(f"Failed to load sentiment models: {str(e)}")
        models = None

    # Initialize sentiment service
    try:
        logger.debug("Initializing SentimentService")
        sentiment_service = SentimentService(models)
        set_review_sentiment_service(sentiment_service)
        set_sentiment_routes_service(sentiment_service)
    except Exception as e:
        logger.error(f"Failed to initialize SentimentService: {str(e)}")
        sentiment_service = None

    # Register blueprints
    logger.debug("Registering blueprints")
    app.register_blueprint(create_product_blueprint(tiki_service), url_prefix='/api')
    app.register_blueprint(review_bp, url_prefix='/api')
    app.register_blueprint(sentiment_bp, url_prefix='/api')
    app.register_blueprint(create_search_blueprint(tiki_service), url_prefix='/api')

    return app

# Tạo app instance
app = init_app()

# Chạy ứng dụng
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)