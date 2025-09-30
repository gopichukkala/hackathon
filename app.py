from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from crop_model import recommend_crop
from disease_model import detect_disease
from ocrmodule import extract_soil_values
from deep_translator import GoogleTranslator
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===== CHATBOT SETUP =====
chatbot = ChatBot(
    "FarmBot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri="sqlite:///database.sqlite3"
)

trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train(
    "chatterbot.corpus.english",
    "./chatterbot_corpus/data/agriculture.yml"
)

users = {}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
    if username in users:
        return jsonify({"error": "Username already exists."}), 400
    users[username] = password
    return jsonify({"message": "Signup successful! Please login."})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if username in users and users[username] == password:
        return jsonify({"message": f"Welcome {username}!"})
    return jsonify({"error": "Invalid credentials."}), 401


@app.route("/upload_soil_report", methods=["POST"])
def upload_soil_report():
    if "soil_report" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["soil_report"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        ocr_result = extract_soil_values(file)
        values = ocr_result["values"]

        recommended_crops = recommend_crop(values)

        return jsonify({
            "raw_text": ocr_result["raw_text"],
            "values": values,
            "report_type": ocr_result["report_type"],
            "recommended_crops": recommended_crops
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recommend_crop", methods=["POST"])
def recommend_crop_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        recommended_crops = recommend_crop(data)
        return jsonify({"recommended_crops": recommended_crops})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/detect_disease", methods=["POST"])
def detect_disease_route():
    if "leaf_image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["leaf_image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    try:
        result = detect_disease(file)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/market_prices")
def market_prices():
    prices = {"Rice": 2300, "Wheat": 1900, "Maize": 1700}
    return jsonify(prices)


@app.route("/chat_assistant", methods=["POST"])
def chat_assistant():
    data = request.get_json()
    query = data.get("message", "")
    if not query:
        return jsonify({"error": "No message provided"}), 400

    try:
        reply = chatbot.get_response(query).text
        return jsonify({"reply": reply})
    except Exception as e:
        print("Chatbot Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json()
        text = data.get("text")
        lang = data.get("lang")
        if not text or not lang:
            return jsonify({"error": "Missing text or language"}), 400

        lang_map = {
            "english": "en",
            "hindi": "hi",
            "telugu": "te",
            "tamil": "ta",
            "kannada": "kn"
        }
        target_lang = lang_map.get(lang.lower(), "en")
        translated = GoogleTranslator(source="auto", target=target_lang).translate(text)
        return jsonify({"translation": translated})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
