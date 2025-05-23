import os
import joblib
import pickle
import numpy as np
from keras.models import load_model
from config import MODELS_DIR

def initialize_dummy_models():
    """Initialize dummy models for testing purposes"""
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

def load_sentiment_models():
    """Load sentiment analysis models"""
    # Check if models directory exists
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    # Try to load real models, fallback to dummy models
    try:
        nb_model = joblib.load(f'{MODELS_DIR}/naive_bayes_model.pkl')
        svm_model = joblib.load(f'{MODELS_DIR}/linear_svc_model.pkl')
        svc_model = joblib.load(f'{MODELS_DIR}/svc_model.pkl')
        tfidf = joblib.load(f'{MODELS_DIR}/tfidf_vectorizer.pkl')
        label_encoder = joblib.load(f'{MODELS_DIR}/label_encoder.pkl')

        # Load deep learning model
        deep_model = load_model(f'{MODELS_DIR}/text_classification_model.h5')

        # Load tokenizer
        with open(f'{MODELS_DIR}/tokenizer.pkl', 'rb') as f:
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
        return models
    except Exception as e:
        print(f"Error loading models: {e}")
        print("Using dummy models for testing purposes...")
        return initialize_dummy_models()