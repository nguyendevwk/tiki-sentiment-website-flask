from flask import Blueprint, request, jsonify
from services.sentiment_service import analyze_sentiment

sentiment_bp = Blueprint('sentiment', __name__)

@sentiment_bp.route('/api/analyze-sentiment', methods=['POST'])
def api_analyze_sentiment():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided", "status": "error"}), 400

    results = analyze_sentiment(text)
    return jsonify({"results": results, "status": "success"})
