import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from config import MAX_LEN

class SentimentService:
    def __init__(self, models):
        self.models = models

    def analyze_sentiment(self, text):
        """Analyze sentiment using all available models"""
        results = {}

        try:
            # Preprocessing for traditional models
            tfidf_vector = self.models['tfidf'].transform([text])

            # Naive Bayes prediction
            nb_pred = self.models['nb_model'].predict(tfidf_vector)[0]
            nb_proba = self.models['nb_model'].predict_proba(tfidf_vector)[0]
            nb_confidence = float(np.max(nb_proba) * 100)
            nb_label = self.models['label_encoder'].inverse_transform([nb_pred])[0]

            # SVM
            svm_pred = self.models['svm_model'].predict(tfidf_vector)[0]
            svm_label = self.models['label_encoder'].inverse_transform([svm_pred])[0]

            # SVC
            svc_pred = self.models['svc_model'].predict(tfidf_vector)[0]
            svc_label = self.models['label_encoder'].inverse_transform([svc_pred])[0]
            svc_confidence = (
                float(np.max(self.models['svc_model'].predict_proba(tfidf_vector)[0]) * 100)
                if hasattr(self.models['svc_model'], "predict_proba")
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
            sequence = self.models['tokenizer'].texts_to_sequences([text])
            padded = pad_sequences(sequence, maxlen=MAX_LEN, padding='post', truncating='post')
            deep_pred_proba = self.models['deep_model'].predict(padded)[0]
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