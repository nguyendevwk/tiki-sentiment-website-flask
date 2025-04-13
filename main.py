import joblib
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from keras.models import load_model
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

max_len = 100
# --- Load mô hình đã lưu ---
nb_model = joblib.load('models/naive_bayes_model.pkl')
svm_model = joblib.load('models/linear_svc_model.pkl')
svc_model = joblib.load('models/svc_model.pkl')
tfidf = joblib.load('models/tfidf_vectorizer.pkl')
label_encoder = joblib.load('models/label_encoder.pkl')

# --- Văn bản mới cần phân loại ---
new_texts = [
    "Sản phẩm này rất tệ",
    "Dịch vụ tuyệt vời và nhanh chóng",
    "Chất lượng trung bình, không quá đặc biệt"
]

# --- Vector hóa văn bản ---
new_tfidf = tfidf.transform(new_texts)

# --- Dự đoán ---
pred_nb = nb_model.predict(new_tfidf)
pred_svm = svm_model.predict(new_tfidf)
pred_svc = svc_model.predict(new_tfidf)

# --- Giải mã nhãn ---
decoded_nb = label_encoder.inverse_transform(pred_nb)
decoded_svm = label_encoder.inverse_transform(pred_svm)
decoded_svc = label_encoder.inverse_transform(pred_svc)

# --- In kết quả ---
for i in range(len(new_texts)):
    print(f"\n📄 Văn bản: {new_texts[i]}")

    # Naive Bayes (có hỗ trợ predict_proba)
    prob_nb = nb_model.predict_proba(new_tfidf[i])[0]
    confidence_nb = np.max(prob_nb) * 100
    print(f"  🤖 Naive Bayes → {decoded_nb[i]} ({confidence_nb:.2f}%)")

    # Linear SVC không hỗ trợ xác suất — ta chỉ hiển thị nhãn
    print(f"  🧠 Linear SVC  → {decoded_svm[i]} (không có xác suất)")

    # SVC với xác suất
    if hasattr(svc_model, "predict_proba"):
        prob_svc = svc_model.predict_proba(new_tfidf[i])[0]
        confidence_svc = np.max(prob_svc) * 100
        print(f"  🚀 SVC         → {decoded_svc[i]} ({confidence_svc:.2f}%)")
    else:
        print(f"  🚀 SVC         → {decoded_svc[i]} (không có xác suất)")


import tensorflow as tf

print("TensorFlow version:", tf.__version__)
print("Num GPUs Available:", len(tf.config.list_physical_devices('GPU')))
# tf.debugging.set_log_device_placement(True)

# Load mô hình
model = load_model("models/text_classification_model.h5")

# Load tokenizer
with open("models/tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

# Tiền xử lý dữ liệu mới (ví dụ)
new_texts = ["sản phẩm cực bình thường nhưng dùng rất tốt và hiệu quả đáng tiền"]
new_sequences = tokenizer.texts_to_sequences(new_texts)
new_pad = pad_sequences(new_sequences, maxlen=max_len, padding='post', truncating='post')

# Dự đoán
predictions = model.predict(new_pad)
predicted_class = predictions.argmax(axis=-1)
print(f"Dự đoán nhãn: {predicted_class}")
