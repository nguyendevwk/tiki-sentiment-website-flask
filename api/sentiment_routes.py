from flask import Blueprint, request, jsonify

# Create blueprint
sentiment_bp = Blueprint('sentiment', __name__)

# This will be initialized in app.py after loading models
sentiment_service = None

def set_sentiment_service(service):
    global sentiment_service
    sentiment_service = service

@sentiment_bp.route('/analyze-sentiment', methods=['POST'])
def api_analyze_sentiment():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided", "status": "error"}), 400

    if not sentiment_service:
        return jsonify({"error": "Sentiment service not initialized", "status": "error"}), 500

    results = sentiment_service.analyze_sentiment(text)
    return jsonify({"results": results, "status": "success"})