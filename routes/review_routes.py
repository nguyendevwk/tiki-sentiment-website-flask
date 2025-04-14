from flask import Blueprint, request, jsonify, current_app
from app.utils.api_helpers import get_with_retry
from app.utils.sentiment import analyze_sentiment

review_bp = Blueprint('review', __name__)

@review_bp.route('/api/reviews/<int:product_id>', methods=['GET'])
def get_reviews(product_id):
    page = int(request.args.get('page', 10))
    limit = int(request.args.get('limit', 20))

    url = f"https://tiki.vn/api/v2/reviews"
    params = {
        'product_id': product_id,
        'page': page,
        'limit': limit,
        'include': 'comments,contribute_info,attribute_vote_summary'
    }

    try:
        data = get_with_retry(url, params)
        reviews = data.get('data', [])
        sentiment_summary = {"Tích cực": 0, "Trung lập": 0, "Tiêu cực": 0}
        models = current_app.config['MODELS']

        for review in reviews:
            content = review.get('content', '')
            if content.strip():
                result = analyze_sentiment(content, models)
                review['sentiment_analysis'] = result
                label = result.get('overall_sentiment')
                if label in sentiment_summary:
                    sentiment_summary[label] += 1

        return jsonify({
            "reviews": data,
            "sentiment_summary": sentiment_summary,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500
