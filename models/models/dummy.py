import os, pickle, joblib
from keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
import numpy as np

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

