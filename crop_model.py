import joblib
import pandas as pd
import os

model_path = os.path.join("models", "crop_recommendation_model.joblib")
model = joblib.load(model_path)

# Fix: match feature names from training data
feature_names = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

def recommend_crop(values, top_n=3):
    try:
        features = {
            "N": values.get("N", 0),
            "P": values.get("P", 0),
            "K": values.get("K", 0),
            "temperature": values.get("temperature", 0),
            "humidity": values.get("humidity", 0),
            "ph": values.get("ph", 0),
            "rainfall": values.get("rainfall", 0)
        }

        df = pd.DataFrame([features], columns=feature_names)
        probs = model.predict_proba(df)[0]
        classes = model.classes_
        top_indices = probs.argsort()[::-1][:top_n]
        recommended = [classes[i] for i in top_indices]
        return recommended
    except Exception as e:
        return ["Could not predict: " + str(e)]
