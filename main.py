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