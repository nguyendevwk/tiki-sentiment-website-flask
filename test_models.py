import joblib
import pickle
import numpy as np
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# ===== LOAD MODELS =====
print("[INFO] Đang load mô hình...")

model = load_model('models/text_classification_model.h5')
nb_model = joblib.load('models/naive_bayes_model.pkl')
svm_model = joblib.load('models/linear_svc_model.pkl')  # phải là CalibratedClassifierCV
svc_model = joblib.load('models/svc_model.pkl')
tfidf = joblib.load('models/tfidf_vectorizer.pkl')
label_encoder = joblib.load('models/label_encoder.pkl')

with open('models/tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

# ===== TEST INPUTS =====
test_samples = [
    "Tôi rất thích sản phẩm này, chất lượng tuyệt vời.",
    "Dịch vụ quá tệ, nhân viên không hỗ trợ gì cả.",
    "Giao hàng nhanh, đóng gói cẩn thận, sẽ mua lần sau.",
    "Sản phẩm không giống mô tả, rất thất vọng.",
    "Giá hợp lý, sẽ giới thiệu cho bạn bè."
]

maxlen = 100  # dùng để pad cho Keras
print("\n========== DỰ ĐOÁN NHÃN ==========")

# ===== TF-IDF cho các model truyền thống =====
X_test_tfidf = tfidf.transform(test_samples)

# ===== Dự đoán và in nhãn =====
def predict_and_print_labels(model, name, X_input, is_keras=False):
    if is_keras:
        probs = model.predict(X_input)
        y_pred = np.argmax(probs, axis=1)
    else:
        y_pred = model.predict(X_input)
    print(f"\n[{name}]")
    for text, pred in zip(test_samples, y_pred):
        print(f"- \"{text}\" ➜ {label_encoder.inverse_transform([pred])[0]}")
    return y_pred

# Naive Bayes
y_pred_nb = predict_and_print_labels(nb_model, "Naive Bayes", X_test_tfidf)

# Linear SVC (calibrated)
y_pred_svm = predict_and_print_labels(svm_model, "Linear SVC", X_test_tfidf)

# SVC với kernel RBF
y_pred_svc = predict_and_print_labels(svc_model, "SVC (Kernel)", X_test_tfidf)

# Mạng nơ-ron Keras
sequence = tokenizer.texts_to_sequences(test_samples)
padded_seq = pad_sequences(sequence, maxlen=maxlen)
y_pred_keras = predict_and_print_labels(model, "Keras Neural Network", padded_seq, is_keras=True)

# ===== Hiển thị xác suất =====
def print_probabilities(name, probs, test_samples):
    print(f"\n[{name} - Xác suất dự đoán]")
    for text, prob in zip(test_samples, probs):
        prob_str = ", ".join(f"{cls}: {p*100:.2f}%" for cls, p in zip(label_encoder.classes_, prob))
        print(f"- \"{text}\" ➜ {prob_str}")

print_probabilities("Naive Bayes", nb_model.predict_proba(X_test_tfidf), test_samples)
print_probabilities("Linear SVC", svm_model.predict_proba(X_test_tfidf), test_samples)
print_probabilities("SVC", svc_model.predict_proba(X_test_tfidf), test_samples)
print_probabilities("Keras Neural Net", model.predict(padded_seq), test_samples)
