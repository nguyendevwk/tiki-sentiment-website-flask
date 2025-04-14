from .main_routes import main_bp
from .product_routes import product_bp
from .review_routes import review_bp
from .sentiment_routes import sentiment_bp
from .debug_routes import debug_bp

def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(sentiment_bp)
    app.register_blueprint(debug_bp)
