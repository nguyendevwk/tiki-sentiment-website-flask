# from flask import Flask, render_template, request, jsonify
# import requests
# import json
# import pandas as pd
# import numpy as np
# import time
# from load_models import models  # Import models từ file riêng
# from tensorflow.keras.preprocessing.sequence import pad_sequences

# app = Flask(__name__)

# # --- API Configuration ---
# TIKI_API_BASE = "https://tiki.vn/api/v2"
# HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
#     'Accept': 'application/json, text/plain, */*',
#     'Origin': 'https://tiki.vn',
#     'Referer': 'https://tiki.vn/'
# }

# # Create a session object that will be reused
# tiki_session = requests.Session()
# tiki_session.headers.update(HEADERS)

# # Cache for product recommendations and reviews
# product_recommendations_cache = {}
# review_cache = {}

# def get_with_retry(url, params=None, max_retries=3, delay=1):
#     """Make a GET request with retry logic"""
#     for attempt in range(max_retries):
#         try:
#             response = tiki_session.get(url, params=params)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             if attempt == max_retries - 1:
#                 raise
#             print(f"Attempt {attempt+1} failed: {str(e)}. Retrying in {delay} seconds...")
#             time.sleep(delay)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/api/products', methods=['GET'])
# def get_products():
#     keyword = request.args.get('keyword', '')
#     page = int(request.args.get('page', 1))
#     limit = int(request.args.get('limit', 12))

#     url = f"{TIKI_API_BASE}/products"
#     params = {
#         'limit': limit,
#         'page': page
#     }

#     if keyword:
#         params['q'] = keyword
#     else:
#         params['sort'] = 'top_seller'

#     try:
#         data = get_with_retry(url, params)
#         return jsonify(data)
#     except Exception as e:
#         return jsonify({"error": str(e), "status": "error"}), 500

# @app.route('/api/product/<int:product_id>', methods=['GET'])
# def get_product_details(product_id):
#     url = f"{TIKI_API_BASE}/products/{product_id}"

#     try:
#         data = get_with_retry(url)
#         return jsonify(data)
#     except Exception as e:
#         return jsonify({"error": str(e), "status": "error"}), 500

# @app.route('/api/reviews/<int:product_id>', methods=['GET'])
# def get_reviews(product_id):
#     """Lấy đánh giá sản phẩm từ Tiki API"""
#     page = int(request.args.get('page', 1))
#     limit = int(request.args.get('limit', 10))
#     cache_key = f"{product_id}_{page}_{limit}"

#     if cache_key in review_cache:
#         print(f"Trả về đánh giá từ cache cho sản phẩm {product_id}")
#         return jsonify(review_cache[cache_key])

#     url = f"{TIKI_API_BASE}/reviews"
#     params = {
#         'product_id': product_id,
#         'page': page,
#         'limit': limit,
#         'include': 'comments,contribute_info,attribute_vote_summary',
#         'sort': 'score|desc,id|desc,stars|all'
#     }

#     try:
#         data = get_with_retry(url, params)
#         reviews = data.get('data', [])

#         review_cache[cache_key] = data
#         print(f"Lấy {len(reviews)} đánh giá cho sản phẩm {product_id}")
#         return jsonify(data)
#     except Exception as e:
#         print(f"Lỗi khi lấy đánh giá sản phẩm {product_id}: {e}")
#         return jsonify({"error": str(e), "status": "error", "data": []}), 500

# @app.route('/api/analyze-reviews/<int:product_id>', methods=['GET'])
# def analyze_reviews(product_id):
#     """Phân tích cảm xúc đánh giá sản phẩm"""
#     page = int(request.args.get('page', 1))
#     limit = int(request.args.get('limit', 10))
#     cache_key = f"analyzed_{product_id}_{page}_{limit}"

#     if cache_key in review_cache:
#         print(f"Trả về phân tích từ cache cho sản phẩm {product_id}")
#         return jsonify(review_cache[cache_key])

#     url = f"http://localhost:5000/api/reviews/{product_id}?page={page}&limit={limit}"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#         reviews = data.get('data', [])
#     except Exception as e:
#         print(f"Lỗi khi lấy đánh giá từ API nội bộ: {e}")
#         return jsonify({"error": str(e), "status": "error", "data": []}), 500

#     try:
#         if reviews:
#             texts = [review.get('content', '') for review in reviews]
#             valid_texts = [t for t in texts if t]
#             valid_indices = [i for i, t in enumerate(texts) if t]

#             if valid_texts:
#                 tfidf_vectors = models['tfidf'].transform(valid_texts)
#                 nb_preds = models['nb_model'].predict(tfidf_vectors)
#                 nb_probas = models['nb_model'].predict_proba(tfidf_vectors)
#                 svm_preds = models['svm_model'].predict(tfidf_vectors)
#                 svc_preds = models['svc_model'].predict(tfidf_vectors)
#                 svc_probas = models['svc_model'].predict_proba(tfidf_vectors) if hasattr(models['svc_model'], "predict_proba") else None

#                 sequences = models['tokenizer'].texts_to_sequences(valid_texts)
#                 padded = pad_sequences(sequences, maxlen=models['max_len'], padding='post', truncating='post')
#                 deep_probas = models['deep_model'].predict(padded)
#                 deep_preds = np.argmax(deep_probas, axis=1) if len(deep_probas.shape) > 1 else np.argmax(deep_probas)

#                 positive_sum = 0
#                 neutral_sum = 0
#                 negative_sum = 0
#                 valid_review_count = 0

#                 label_map = {
#                     "positive": "Tích cực",
#                     "neutral": "Trung lập",
#                     "negative": "Tiêu cực",
#                     "Tích cực": "Tích cực",
#                     "Trung lập": "Trung lập",
#                     "Tiêu cực": "Tiêu cực"
#                 }

#                 for idx, valid_idx in enumerate(valid_indices):
#                     nb_label_raw = models['label_encoder'].inverse_transform([nb_preds[idx]])[0]
#                     nb_confidence = float(np.max(nb_probas[idx]) * 100)
#                     svm_label_raw = models['label_encoder'].inverse_transform([svm_preds[idx]])[0]
#                     svc_label_raw = models['label_encoder'].inverse_transform([svc_preds[idx]])[0]
#                     svc_confidence = float(np.max(svc_probas[idx]) * 100) if svc_probas is not None else None
#                     deep_label_raw = models['label_encoder'].inverse_transform([deep_preds[idx] if len(deep_probas.shape) > 1 else deep_preds])[0]
#                     deep_confidence = float(deep_probas[idx][deep_preds[idx]] * 100) if len(deep_probas.shape) > 1 else float(deep_probas[deep_preds] * 100)

#                     nb_label = label_map.get(nb_label_raw, "Trung lập")
#                     svm_label = label_map.get(svm_label_raw, "Trung lập")
#                     svc_label = label_map.get(svc_label_raw, "Trung lập")
#                     deep_label = label_map.get(deep_label_raw, "Trung lập")

#                     sentiment_votes = {"Tích cực": 0, "Trung lập": 0, "Tiêu cực": 0}
#                     sentiment_votes[nb_label] += nb_confidence / 100
#                     sentiment_votes[svm_label] += 0.5
#                     sentiment_votes[svc_label] += svc_confidence / 100 if svc_confidence else 0.5
#                     sentiment_votes[deep_label] += deep_confidence / 100

#                     overall_sentiment = max(sentiment_votes, key=sentiment_votes.get)
#                     total_votes = sum(sentiment_votes.values()) or 1
#                     sentiment_percentages = {
#                         sentiment: (votes / total_votes) * 100
#                         for sentiment, votes in sentiment_votes.items()
#                     }

#                     reviews[valid_idx]['sentiment_analysis'] = {
#                         'models': {
#                             'naive_bayes': {'label': nb_label, 'confidence': nb_confidence},
#                             'svm': {'label': svm_label, 'confidence': None},
#                             'svc': {'label': svc_label, 'confidence': svc_confidence},
#                             'deep_learning': {'label': deep_label, 'confidence': deep_confidence}
#                         },
#                         'overall_sentiment': overall_sentiment,
#                         'sentiment_percentages': sentiment_percentages
#                     }

#                     positive_sum += sentiment_percentages["Tích cực"]
#                     neutral_sum += sentiment_percentages["Trung lập"]
#                     negative_sum += sentiment_percentages["Tiêu cực"]
#                     valid_review_count += 1

#                 sentiment_summary = {
#                     "positive": positive_sum / valid_review_count if valid_review_count > 0 else 0,
#                     "neutral": neutral_sum / valid_review_count if valid_review_count > 0 else 0,
#                     "negative": negative_sum / valid_review_count if valid_review_count > 0 else 0,
#                     "total_reviews_analyzed": valid_review_count
#                 }
#                 data['sentiment_summary'] = sentiment_summary

#         review_cache[cache_key] = data
#         print(f"Phân tích {len(reviews)} đánh giá cho sản phẩm {product_id}")
#         return jsonify(data)
#     except Exception as e:
#         print(f"Lỗi khi phân tích đánh giá sản phẩm {product_id}: {e}")
#         return jsonify({"error": str(e), "status": "error", "data": []}), 500

# @app.route('/api/recommendations/<int:product_id>', methods=['GET'])
# def get_recommendations(product_id):
#     if product_id in product_recommendations_cache:
#         return jsonify(product_recommendations_cache[product_id])

#     url = f"{TIKI_API_BASE}/products/{product_id}/recommendations"
#     try:
#         data = get_with_retry(url)
#         product_recommendations_cache[product_id] = data
#         return jsonify(data)
#     except Exception as e:
#         return jsonify({"error": str(e), "status": "error"}), 500

# @app.route('/api/analyze-sentiment', methods=['POST'])
# def api_analyze_sentiment():
#     data = request.get_json()
#     text = data.get('text', '')

#     if not text:
#         return jsonify({"error": "No text provided", "status": "error"}), 400

#     results = analyze_sentiment(text)
#     return jsonify({"results": results, "status": "success"})

# def analyze_sentiment(text):
#     """Analyze sentiment using all available models"""
#     results = {}
#     label_map = {
#         "Tích cực": "positive",
#         "Trung lập": "neutral",
#         "Tiêu cực": "negative"
#     }

#     try:
#         tfidf_vector = models['tfidf'].transform([text])
#         nb_pred = models['nb_model'].predict(tfidf_vector)[0]
#         nb_proba = models['nb_model'].predict_proba(tfidf_vector)[0]
#         nb_confidence = float(np.max(nb_proba) * 100)
#         nb_label_vi = models['label_encoder'].inverse_transform([nb_pred])[0]
#         nb_label = label_map[nb_label_vi]

#         svm_pred = models['svm_model'].predict(tfidf_vector)[0]
#         svm_label_vi = models['label_encoder'].inverse_transform([svm_pred])[0]
#         svm_label = label_map[svm_label_vi]

#         svc_pred = models['svc_model'].predict(tfidf_vector)[0]
#         svc_label_vi = models['label_encoder'].inverse_transform([svc_pred])[0]
#         svc_label = label_map[svc_label_vi]
#         svc_confidence = float(np.max(models['svc_model'].predict_proba(tfidf_vector)[0]) * 100) if hasattr(models['svc_model'], "predict_proba") else None

#         sequence = models['tokenizer'].texts_to_sequences([text])
#         padded = pad_sequences(sequence, maxlen=models['max_len'], padding='post', truncating='post')
#         deep_pred_proba = models['deep_model'].predict(padded)[0]
#         deep_pred = np.argmax(deep_pred_proba)
#         deep_confidence = float(deep_pred_proba[deep_pred] * 100)
#         deep_label_vi = models['label_encoder'].inverse_transform([deep_pred])[0]
#         deep_label = label_map[deep_label_vi]

#         results["models"] = {
#             "naive_bayes": {"label": nb_label, "confidence": nb_confidence},
#             "svm": {"label": svm_label, "confidence": None},
#             "svc": {"label": svc_label, "confidence": svc_confidence},
#             "deep_learning": {"label": deep_label, "confidence": deep_confidence}
#         }

#         sentiment_votes = {"positive": 0, "neutral": 0, "negative": 0}
#         sentiment_votes[nb_label] += nb_confidence / 100
#         sentiment_votes[svm_label] += 0.5
#         sentiment_votes[svc_label] += svc_confidence / 100 if svc_confidence else 0.5
#         sentiment_votes[deep_label] += deep_confidence / 100

#         overall_sentiment = max(sentiment_votes, key=sentiment_votes.get)
#         total_votes = sum(sentiment_votes.values())
#         sentiment_percentages = {
#             sentiment: (votes / total_votes) * 100
#             for sentiment, votes in sentiment_votes.items()
#         }

#         results["overall_sentiment"] = overall_sentiment
#         results["sentiment_percentages"] = sentiment_percentages

#     except Exception as e:
#         results["error"] = str(e)

#     return results

# @app.route('/debug/api-test', methods=['GET'])
# def api_test():
#     """Test endpoint to check API connectivity"""
#     test_results = {}

#     try:
#         url = f"{TIKI_API_BASE}/products"
#         params = {'limit': 5, 'sort': 'top_seller'}
#         response = tiki_session.get(url, params=params)
#         response.raise_for_status()
#         test_results['products_api'] = {
#             'status': 'success',
#             'status_code': response.status_code,
#             'items_count': len(response.json().get('data', []))
#         }
#     except Exception as e:
#         test_results['products_api'] = {
#             'status': 'error',
#             'error': str(e)
#         }

#     try:
#         test_product_id = 187046435
#         url = f"{TIKI_API_BASE}/reviews"
#         params = {'product_id': test_product_id, 'limit': 5}
#         response = tiki_session.get(url, params=params)
#         response.raise_for_status()
#         test_results['reviews_api'] = {
#             'status': 'success',
#             'status_code': response.status_code,
#             'items_count': len(response.json().get('data', [])),
#             'product_id': test_product_id
#         }
#     except Exception as e:
#         test_results['reviews_api'] = {
#             'status': 'error',
#             'error': str(e)
#         }

#     return jsonify({
#         'test_results': test_results,
#         'headers_used': dict(HEADERS),
#         'timestamp': time.time()
#     })

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import requests
import json
import pandas as pd
import numpy as np
import time
from load_models import models  # Import models từ file riêng
from tensorflow.keras.preprocessing.sequence import pad_sequences  # Thêm import này

app = Flask(__name__)

# --- API Configuration ---
TIKI_API_BASE = "https://tiki.vn/api/v2"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://tiki.vn',
    'Referer': 'https://tiki.vn/'
}

tiki_session = requests.Session()
tiki_session.headers.update(HEADERS)

product_recommendations_cache = {}
review_cache = {}

def get_with_retry(url, params=None, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            response = tiki_session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt+1} failed: {str(e)}. Retrying in {delay} seconds...")
            time.sleep(delay)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 12))

    url = f"{TIKI_API_BASE}/products"
    params = {'limit': limit, 'page': page}
    if keyword:
        params['q'] = keyword
    else:
        params['sort'] = 'top_seller'

    try:
        data = get_with_retry(url, params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/product/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    url = f"{TIKI_API_BASE}/products/{product_id}"
    try:
        data = get_with_retry(url)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route('/api/reviews/<int:product_id>', methods=['GET'])
def get_reviews(product_id):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    url = f"{TIKI_API_BASE}/reviews"
    params = {
        'product_id': product_id,
        'page': page,
        'limit': limit,
        'include': 'comments,contribute_info,attribute_vote_summary'
    }

    try:
        data = get_with_retry(url, params)

        reviews = data.get('data', [])
        sentiment_count = {"positive": 0, "neutral": 0, "negative": 0}
        total_with_sentiment = 0

        # Apply sentiment analysis
        for review in reviews:
            content = review.get('content', '')
            if content.strip():
                sentiment_results = analyze_sentiment(content)
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

        return jsonify({
            "reviews": data,
            "sentiment_summary": sentiment_summary,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

MAX_LEN = 100  # Độ dài tối đa của chuỗi đầu vào cho mô hình deep learning

@app.route('/api/recommendations/<int:product_id>', methods=['GET'])
def get_recommendations(product_id):
    if product_id in product_recommendations_cache:
        return jsonify(product_recommendations_cache[product_id])

    url = f"{TIKI_API_BASE}/products/{product_id}/recommendations"
    try:
        data = get_with_retry(url)
        product_recommendations_cache[product_id] = data
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/analyze-sentiment', methods=['POST'])
def api_analyze_sentiment():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided", "status": "error"}), 400

    results = analyze_sentiment(text)
    return jsonify({"results": results, "status": "success"})

def analyze_sentiment(text):
    """Analyze sentiment using all available models"""
    results = {}

    # Map Vietnamese sentiment labels to English for frontend compatibility
    label_map = {
        "Tích cực": "positive",
        "Trung lập": "neutral",
        "Tiêu cực": "negative"
    }

    try:
        # Preprocessing for traditional models
        tfidf_vector = models['tfidf'].transform([text])

        # Naive Bayes prediction
        nb_pred = models['nb_model'].predict(tfidf_vector)[0]
        nb_proba = models['nb_model'].predict_proba(tfidf_vector)[0]
        nb_confidence = float(np.max(nb_proba) * 100)
        nb_label_vi = models['label_encoder'].inverse_transform([nb_pred])[0]
        nb_label = label_map[nb_label_vi]

        # SVM prediction
        svm_pred = models['svm_model'].predict(tfidf_vector)[0]
        svm_label_vi = models['label_encoder'].inverse_transform([svm_pred])[0]
        svm_label = label_map[svm_label_vi]

        # SVC prediction (with probability if available)
        svc_pred = models['svc_model'].predict(tfidf_vector)[0]
        svc_label_vi = models['label_encoder'].inverse_transform([svc_pred])[0]
        svc_label = label_map[svc_label_vi]
        if hasattr(models['svc_model'], "predict_proba"):
            svc_proba = models['svc_model'].predict_proba(tfidf_vector)[0]
            svc_confidence = float(np.max(svc_proba) * 100)
        else:
            svc_confidence = None

        # Deep learning model prediction
        sequence = models['tokenizer'].texts_to_sequences([text])
        padded = pad_sequences(sequence, maxlen=MAX_LEN, padding='post', truncating='post')
        deep_pred_proba = models['deep_model'].predict(padded)[0]
        deep_pred = np.argmax(deep_pred_proba)
        deep_confidence = float(deep_pred_proba[deep_pred] * 100)
        deep_label_vi = models['label_encoder'].inverse_transform([deep_pred])[0]
        deep_label = label_map[deep_label_vi]

        # Store individual model results with English labels
        results["models"] = {
            "naive_bayes": {
                "label": nb_label,
                "confidence": nb_confidence
            },
            "svm": {
                "label": svm_label,
                "confidence": None  # SVM doesn't provide confidence scores
            },
            "svc": {
                "label": svc_label,
                "confidence": svc_confidence
            },
            "deep_learning": {
                "label": deep_label,
                "confidence": deep_confidence
            }
        }

        # Determine overall sentiment by weighted voting (using English labels)
        sentiment_votes = {"positive": 0, "neutral": 0, "negative": 0}

        # Add weighted votes
        sentiment_votes[nb_label] += nb_confidence / 100
        sentiment_votes[svm_label] += 0.5

        if svc_confidence is not None:
            sentiment_votes[svc_label] += svc_confidence / 100
        else:
            sentiment_votes[svc_label] += 0.5

        sentiment_votes[deep_label] += deep_confidence / 100

        # Get the sentiment with highest weighted votes
        overall_sentiment = max(sentiment_votes, key=sentiment_votes.get)

        # Calculate percentage for each sentiment
        total_votes = sum(sentiment_votes.values())
        sentiment_percentages = {
            sentiment: (votes / total_votes) * 100
            for sentiment, votes in sentiment_votes.items()
        }

        results["overall_sentiment"] = overall_sentiment
        results["sentiment_percentages"] = sentiment_percentages

    except Exception as e:
        results["error"] = str(e)

@app.route('/debug/api-test', methods=['GET'])
def api_test():
    test_results = {}
    try:
        url = f"{TIKI_API_BASE}/products"
        params = {'limit': 5, 'sort': 'top_seller'}
        response = tiki_session.get(url, params=params)
        response.raise_for_status()
        test_results['products_api'] = {
            'status': 'success',
            'status_code': response.status_code,
            'items_count': len(response.json().get('data', []))
        }
    except Exception as e:
        test_results['products_api'] = {'status': 'error', 'error': str(e)}

    try:
        test_product_id = 187046435
        url = f"{TIKI_API_BASE}/reviews"
        params = {'product_id': test_product_id, 'limit': 5}
        response = tiki_session.get(url, params=params)
        response.raise_for_status()
        test_results['reviews_api'] = {
            'status': 'success',
            'status_code': response.status_code,
            'items_count': len(response.json().get('data', [])),
            'product_id': test_product_id
        }
    except Exception as e:
        test_results['reviews_api'] = {'status': 'error', 'error': str(e)}

    return jsonify({
        'test_results': test_results,
        'headers_used': dict(HEADERS),
        'timestamp': time.time()
    })

if __name__ == '__main__':
    app.run(debug=True)