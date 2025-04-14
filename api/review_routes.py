from flask import Blueprint, request, jsonify
from services.tiki_service import TikiService
from services.sentiment_service import SentimentService

# Create blueprint
review_bp = Blueprint('review', __name__)
tiki_service = TikiService()

# This will be initialized in app.py after loading models
sentiment_service = None

def set_sentiment_service(service):
    global sentiment_service
    sentiment_service = service

@review_bp.route('/reviews/<int:product_id>', methods=['GET'])
def get_reviews(product_id):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))

    try:
        data = tiki_service.get_reviews(product_id, page, limit)

        reviews = data.get('data', [])
        sentiment_count = {"Tích cực": 0, "Trung lập": 0, "Tiêu cực": 0}
        total_with_sentiment = 0

        # Apply sentiment analysis if sentiment_service is available
        if sentiment_service:
            for review in reviews:
                content = review.get('content', '')
                if content.strip():
                    sentiment_results = sentiment_service.analyze_sentiment(content)
                    review['sentiment_analysis'] = sentiment_results

                    # Tăng bộ đếm
                    overall_sentiment = sentiment_results.get('overall_sentiment')
                    if overall_sentiment in sentiment_count:
                        sentiment_count[overall_sentiment] += 1
                        total_with_sentiment += 1

            # Tính tỷ lệ phần trăm
            sentiment_summary = {}
            if total_with_sentiment > 0:
                sentiment_summary = {
                    key: round((value / total_with_sentiment) * 100, 2)
                    for key, value in sentiment_count.items()
                }
        else:
            sentiment_summary = {}

        return jsonify({
            "reviews": data,
            "sentiment_summary": sentiment_summary,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500