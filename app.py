# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import json
import pandas as pd
import numpy as np
import joblib
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

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



# Create a session object that will be reused
tiki_session = requests.Session()
tiki_session.headers.update(HEADERS)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('templates/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('templates/js', filename)

# --- Load models ---
# Check if models directory exists
if not os.path.exists('models'):
    os.makedirs('models')

# Function to initialize models (use this for testing without actual models)
def initialize_dummy_models():
    class DummyModel:
        def predict(self, X):
            # Return random predictions (0, 1, 2) for negative, neutral, positive
            if isinstance(X, (list, np.ndarray)):
                return np.random.randint(0, 3, len(X))
            else:  # For sparse matrices
                return np.random.randint(0, 3, X.shape[0])

        def predict_proba(self, X):
            # Return random probabilities
            if isinstance(X, (list, np.ndarray)):
                probas = np.random.random((len(X), 3))
            else:  # For sparse matrices
                probas = np.random.random((X.shape[0], 3))
            # Normalize to sum to 1
            return probas / probas.sum(axis=1, keepdims=True)

    class DummyVectorizer:
        def transform(self, X):
            # Return a sparse-like object
            from scipy.sparse import csr_matrix
            return csr_matrix((len(X), 100))

    class DummyLabelEncoder:
        def inverse_transform(self, X):
            # Map 0, 1, 2 to sentiment labels
            sentiment_map = {0: "Tiêu cực", 1: "Trung lập", 2: "Tích cực"}
            return [sentiment_map[x] for x in X]

    class DummyTokenizer:
        def texts_to_sequences(self, texts):
            # Return random sequences
            return [[np.random.randint(1, 1000) for _ in range(np.random.randint(5, 20))] for _ in texts]

    # Create and return dummy models
    return {
        'nb_model': DummyModel(),
        'svm_model': DummyModel(),
        'svc_model': DummyModel(),
        'tfidf': DummyVectorizer(),
        'label_encoder': DummyLabelEncoder(),
        'deep_model': DummyModel(),
        'tokenizer': DummyTokenizer()
    }

# Try to load real models, fallback to dummy models
try:
    nb_model = joblib.load('models/naive_bayes_model.pkl')
    svm_model = joblib.load('models/linear_svc_model.pkl')
    svc_model = joblib.load('models/svc_model.pkl')
    tfidf = joblib.load('models/tfidf_vectorizer.pkl')
    label_encoder = joblib.load('models/label_encoder.pkl')

    # Load deep learning model
    deep_model = load_model('models/text_classification_model.h5')

    # Load tokenizer
    with open('models/tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)

    models = {
        'nb_model': nb_model,
        'svm_model': svm_model,
        'svc_model': svc_model,
        'tfidf': tfidf,
        'label_encoder': label_encoder,
        'deep_model': deep_model,
        'tokenizer': tokenizer
    }

    print("All models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    print("Using dummy models for testing purposes...")
    models = initialize_dummy_models()

# Constants
MAX_LEN = 100  # For deep learning model

# Cache for product recommendations
product_recommendations_cache = {}

def get_with_retry(url, params=None, max_retries=3, delay=1):
    """Make a GET request with retry logic"""
    for attempt in range(max_retries):
        try:
            response = tiki_session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed, re-raise the exception
                raise
            print(f"Attempt {attempt+1} failed: {str(e)}. Retrying in {delay} seconds...")
            time.sleep(delay)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    keyword = request.args.get('keyword', 'all')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 30))

    # Build URL and parameters
    url = f"{TIKI_API_BASE}/products"
    params = {
        'limit': limit,
        'page': page
    }

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
        print(f"Product details for ID {product_id}: {data}")
        # Check if the product is available
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/reviews/<int:product_id>', methods=['GET'])
def get_reviews(product_id):
    page = int(request.args.get('page', 10))
    limit = int(request.args.get('limit', 20))

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
        sentiment_count = {"Tích cực": 0, "Trung Tính": 0, "Tiêu Cực": 0}
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



@app.route('/api/recommendations/<int:product_id>', methods=['GET'])
def get_recommendations(product_id):
    # Check if we have cached recommendations
    if product_id in product_recommendations_cache:
        return jsonify(product_recommendations_cache[product_id])

    # If not in cache, get recommendations from Tiki API
    url = f"{TIKI_API_BASE}/products/{product_id}/recommendations"

    try:
        data = get_with_retry(url)
        # Cache the results
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

    try:
        # Preprocessing for traditional models
        tfidf_vector = models['tfidf'].transform([text])

            # Naive Bayes prediction
        nb_pred = models['nb_model'].predict(tfidf_vector)[0]
        nb_proba = models['nb_model'].predict_proba(tfidf_vector)[0]
        nb_confidence = float(np.max(nb_proba) * 100)
        nb_label = models['label_encoder'].inverse_transform([nb_pred])[0]

        # SVM
        svm_pred = models['svm_model'].predict(tfidf_vector)[0]
        svm_label = models['label_encoder'].inverse_transform([svm_pred])[0]

        # SVC
        svc_pred = models['svc_model'].predict(tfidf_vector)[0]
        svc_label = models['label_encoder'].inverse_transform([svc_pred])[0]
        svc_confidence = (
            float(np.max(models['svc_model'].predict_proba(tfidf_vector)[0]) * 100)
            if hasattr(models['svc_model'], "predict_proba")
            else None
        )

        # Map label nếu cần
        label_map = {
            "positive": "Tích cực",
            "neutral": "Trung lập",
            "negative": "Tiêu cực"
        }
        nb_label = label_map.get(nb_label, nb_label)
        svm_label = label_map.get(svm_label, svm_label)
        svc_label = label_map.get(svc_label, svc_label)

        # Deep model
        sequence = models['tokenizer'].texts_to_sequences([text])
        padded = pad_sequences(sequence, maxlen=MAX_LEN, padding='post', truncating='post')
        deep_pred_proba = models['deep_model'].predict(padded)[0]
        deep_pred = np.argmax(deep_pred_proba)
        deep_confidence = float(deep_pred_proba[deep_pred] * 100)
        deep_label_map = {0: "Tiêu cực", 1: "Trung lập", 2: "Tích cực"}
        deep_label = deep_label_map.get(deep_pred, "Trung lập")


        # Store individual model results
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

        # Determine overall sentiment by weighted voting
        # Give more weight to models with confidence scores
        sentiment_votes = {"Tích cực": 0, "Trung lập": 0, "Tiêu cực": 0}

        # Add weighted votes for Naive Bayes
        sentiment_votes[nb_label] += nb_confidence / 100

        # Add smaller weight for SVM (no confidence)
        sentiment_votes[svm_label] += 0.5

        # Add weighted votes for SVC if confidence is available
        if svc_confidence is not None:
            sentiment_votes[svc_label] += svc_confidence / 100
        else:
            sentiment_votes[svc_label] += 0.5

        # Add weighted votes for deep learning
        sentiment_votes[deep_label] += deep_confidence / 100

        # Get the sentiment with highest weighted votes
        overall_sentiment = max(sentiment_votes, key=sentiment_votes.get)

        # Calculate percentage for each sentiment
        total_votes = sum(sentiment_votes.values())
        # Trả về bằng tiếng Anh
        sentiment_label_map = {
            "Tích cực": "positive",
            "Trung lập": "neutral",
            "Tiêu cực": "negative"
        }

        sentiment_percentages = {
            sentiment_label_map[sentiment]: (votes / total_votes) * 100
            for sentiment, votes in sentiment_votes.items()
        }

        results["overall_sentiment"] = overall_sentiment
        results["sentiment_percentages"] = sentiment_percentages

    except Exception as e:
        results["error"] = str(e)

    return results


@app.route('/debug/api-test', methods=['GET'])
def api_test():
    """Test endpoint to check API connectivity"""
    test_results = {}

    # Test products API
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
        test_results['products_api'] = {
            'status': 'error',
            'error': str(e)
        }

    # Test reviews API
    try:
        # Use a common product ID for testing
        test_product_id = 187046435  # You may need to update this with a valid product ID
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
        test_results['reviews_api'] = {
            'status': 'error',
            'error': str(e)
        }

    return jsonify({
        'test_results': test_results,
        'headers_used': dict(HEADERS),
        'timestamp': time.time()
    })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)