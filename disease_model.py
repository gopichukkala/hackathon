import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import json

# Load model
model_path = os.path.join("models", "disease_detection_model.keras")
model = tf.keras.models.load_model(model_path)

# Load class indices
with open("models/disease_classes.json", "r") as f:
    class_indices = json.load(f)

# Reverse mapping to get class index → disease name
index_to_class = {v: k for k, v in class_indices.items()}

def detect_disease(file):
    filepath = os.path.join("static/uploads", file.filename)
    file.save(filepath)

    img = image.load_img(filepath, target_size=(128, 128))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    preds = model.predict(img_array)[0]  # shape = (num_classes,)
    class_idx = np.argmax(preds)         # highest confidence index
    disease_name = index_to_class.get(class_idx, "Unknown Disease")

    os.remove(filepath)
    return disease_name
 