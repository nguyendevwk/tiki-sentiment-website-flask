import time
import requests
from config import TIKI_API_BASE, HEADERS
from flask import jsonify

tiki_session = requests.Session()
tiki_session.headers.update(HEADERS)

cache = {}

def get_with_retry(url, params=None, retries=3):
    for i in range(retries):
        try:
            r = tiki_session.get(url, params=params)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            time.sleep(1)
    raise Exception(f"Lỗi gọi API: {url}")

def get_product_list(request):
    keyword = request.args.get('keyword', 'all')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 30))
    url = f"{TIKI_API_BASE}/products"
    params = {'limit': limit, 'page': page}
    if keyword: params['q'] = keyword
    try:
        return jsonify(get_with_retry(url, params))
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

def get_product_details(product_id):
    try:
        return jsonify(get_with_retry(f"{TIKI_API_BASE}/products/{product_id}"))
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

def get_reviews_data(product_id, models):
    try:
        params = {
            'product_id': product_id,
            'page': 1,
            'limit': 20,
            'include': 'comments'
        }
        data = get_with_retry(f"{TIKI_API_BASE}/reviews", params)
        reviews = data.get('data', [])
        summary = {"Tích cực": 0, "Trung lập": 0, "Tiêu cực": 0}
        count = 0
        for r in reviews:
            content = r.get('content', '')
            if content.strip():
                result = analyze_sentiment(content, models)
                sentiment = result.get("overall_sentiment")
                summary[sentiment] += 1
                r["sentiment_analysis"] = result
                count += 1

        if count:
            percent = {k: round((v / count) * 100, 2) for k, v in summary.items()}
        else:
            percent = {}

        return jsonify({
            'reviews': data,
            'sentiment_summary': percent,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

def get_recommendations_data(product_id):
    if product_id in cache:
        return jsonify(cache[product_id])
    try:
        data = get_with_retry(f"{TIKI_API_BASE}/products/{product_id}/recommendations")
        cache[product_id] = data
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500
