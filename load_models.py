import os
import joblib
import numpy as np
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Tắt tối ưu hóa oneDNN để tránh lỗi nếu cần
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Constants
MAX_LEN = 100  # Độ dài tối đa cho deep learning model

def initialize_dummy_models():
    """Khởi tạo các mô hình giả lập để test khi không load được mô hình thật"""
    class DummyModel:
        def predict(self, X):
            # Dự đoán ngẫu nhiên (0, 1, 2) cho negative, neutral, positive
            if isinstance(X, (list, np.ndarray)):
                return np.random.randint(0, 3, len(X))
            else:  # Cho sparse matrices
                return np.random.randint(0, 3, X.shape[0])

        def predict_proba(self, X):
            # Trả về xác suất ngẫu nhiên
            if isinstance(X, (list, np.ndarray)):
                probas = np.random.random((len(X), 3))
            else:  # Cho sparse matrices
                probas = np.random.random((X.shape[0], 3))
            # Chuẩn hóa để tổng bằng 1
            return probas / probas.sum(axis=1, keepdims=True)

    class DummyVectorizer:
        def transform(self, X):
            # Trả về đối tượng giống sparse matrix
            from scipy.sparse import csr_matrix
            return csr_matrix((len(X), 100))

    class DummyLabelEncoder:
        def inverse_transform(self, X):
            # Ánh xạ 0, 1, 2 sang nhãn cảm xúc
            sentiment_map = {0: "Tiêu cực", 1: "Trung lập", 2: "Tích cực"}
            return [sentiment_map[x] for x in X]

    class DummyTokenizer:
        def texts_to_sequences(self, texts):
            # Trả về chuỗi ngẫu nhiên
            return [[np.random.randint(1, 1000) for _ in range(np.random.randint(5, 20))] for _ in texts]

    # Trả về dictionary chứa các mô hình giả lập
    return {
        'nb_model': DummyModel(),
        'svm_model': DummyModel(),
        'svc_model': DummyModel(),
        'tfidf': DummyVectorizer(),
        'label_encoder': DummyLabelEncoder(),
        'deep_model': DummyModel(),
        'tokenizer': DummyTokenizer()
    }

def load_models(model_dir='models'):
    """Load các mô hình thật hoặc dùng dummy models nếu lỗi"""
    # Kiểm tra và tạo thư mục models nếu chưa tồn tại
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    try:
        # Load các mô hình truyền thống
        nb_model = joblib.load(os.path.join(model_dir, 'naive_bayes_model.pkl'))
        svm_model = joblib.load(os.path.join(model_dir, 'linear_svc_model.pkl'))
        svc_model = joblib.load(os.path.join(model_dir, 'svc_model.pkl'))
        tfidf = joblib.load(os.path.join(model_dir, 'tfidf_vectorizer.pkl'))
        label_encoder = joblib.load(os.path.join(model_dir, 'label_encoder.pkl'))

        # Load mô hình deep learning
        deep_model = load_model(os.path.join(model_dir, 'text_classification_model.h5'))

        # Load tokenizer
        with open(os.path.join(model_dir, 'tokenizer.pkl'), 'rb') as f:
            tokenizer = pickle.load(f)

        models = {
            'nb_model': nb_model,
            'svm_model': svm_model,
            'svc_model': svc_model,
            'tfidf': tfidf,
            'label_encoder': label_encoder,
            'deep_model': deep_model,
            'tokenizer': tokenizer,
            'max_len': MAX_LEN
        }

        print("All models loaded successfully!")
        return models

    except Exception as e:
        print(f"Error loading models: {e}")
        print("Using dummy models for testing purposes...")
        return initialize_dummy_models()

# Load models khi file được import
models = load_models()