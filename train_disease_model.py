import os
import shutil
import random
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import json

print("📂 Splitting dataset into train/test...")

dataset_dir = "PlantVillage"  # Original dataset
output_dir = "dataset"
train_ratio = 0.8

train_dir = os.path.join(output_dir, "train")
test_dir = os.path.join(output_dir, "test")

os.makedirs(train_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

# Loop through each class folder
for class_name in os.listdir(dataset_dir):
    class_path = os.path.join(dataset_dir, class_name)
    if not os.path.isdir(class_path):
        continue

    images = [f for f in os.listdir(class_path) if os.path.isfile(os.path.join(class_path, f))]
    random.shuffle(images)

    split_index = int(len(images) * train_ratio)
    train_images = images[:split_index]
    test_images = images[split_index:]

    os.makedirs(os.path.join(train_dir, class_name), exist_ok=True)
    os.makedirs(os.path.join(test_dir, class_name), exist_ok=True)

    for img in train_images:
        src_path = os.path.join(class_path, img)
        dst_path = os.path.join(train_dir, class_name, img)
        try:
            shutil.copy(src_path, dst_path)
        except PermissionError:
            print(f"⚠️ Permission denied for {src_path}, skipping.")

    for img in test_images:
        src_path = os.path.join(class_path, img)
        dst_path = os.path.join(test_dir, class_name, img)
        try:
            shutil.copy(src_path, dst_path)
        except PermissionError:
            print(f"⚠️ Permission denied for {src_path}, skipping.")

print("✅ Dataset split complete!")

# Train CNN model
print("🤖 Training disease detection model...")

train_gen = ImageDataGenerator(rescale=1./255, horizontal_flip=True, rotation_range=20)
test_gen = ImageDataGenerator(rescale=1./255)

train_data = train_gen.flow_from_directory(
    train_dir, target_size=(128,128), batch_size=32, class_mode="categorical"
)
test_data = test_gen.flow_from_directory(
    test_dir, target_size=(128,128), batch_size=32, class_mode="categorical"
)

model = Sequential([
    Conv2D(32, (3,3), activation="relu", input_shape=(128,128,3)),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.5),
    Dense(train_data.num_classes, activation="softmax")
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

history = model.fit(train_data, validation_data=test_data, epochs=10)

# Save model
os.makedirs("models", exist_ok=True)
model.save("models/disease_detection_model.keras")
print("✅ Disease detection model saved as models/disease_detection_model.keras")

# Save class indices for mapping later
class_indices = train_data.class_indices
with open("models/disease_classes.json", "w") as f:
    json.dump(class_indices, f)
print("✅ Class indices saved as models/disease_classes.json")
