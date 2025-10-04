from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from crop_model import recommend_crop
from disease_model import detect_disease
from ocrmodule import extract_soil_values
from deep_translator import GoogleTranslator
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===================== MULTILINGUAL CHATBOT RESPONSES =====================
chat_responses = {
    # ---- GREETINGS ----
    "hello": {
        "en": "Hello! How can I help you today?",
        "hi": "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?",
        "te": "హలో! నేను మీకు ఎలా సహాయం చేయగలను?",
        "ta": "வணக்கம்! உங்களுக்கு எப்படி உதவலாம்?",
        "kn": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
    },
    "hi": {
        "en": "Hi there, farmer! 🌱",
        "hi": "हाय किसान भाई! 🌱",
        "te": "హాయ్ రైతు బంధువులారా! 🌱",
        "ta": "ஹாய் விவசாயி! 🌱",
        "kn": "ಹಾಯ್ ರೈತ ಸ್ನೇಹಿತರೆ! 🌱"
    },
    "how are you": {
        "en": "I am fine! How are you?",
        "hi": "मैं अच्छा हूँ! आप कैसे हैं?",
        "te": "నేను బాగున్నాను! మీరు ఎలా ఉన్నారు?",
        "ta": "நான் நலமாக இருக்கிறேன்! நீங்கள் எப்படி?",
        "kn": "ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ! ನೀವು ಹೇಗಿದ್ದೀರಿ?"
    },

    # ---- CROP INFORMATION ----
    "best crop for rice field": {
        "en": "Rice grows best in clayey soil with standing water.",
        "hi": "चावल चिकनी मिट्टी और पानी भरे खेत में अच्छा उगता है।",
        "te": "వరి మట్టి మరియు నీటి నిల్వలో బాగా పెరుగుతుంది.",
        "ta": "அரிசி களிமண் மண்ணில் மற்றும் தண்ணீர் நிறைந்த வயலில் சிறப்பாக வளரும்.",
        "kn": "ಅಕ್ಕಿ ಮಣ್ಣು ಮತ್ತು ನೀರಿನಿಂದ ತುಂಬಿದ ಹೊಲದಲ್ಲಿ ಉತ್ತಮವಾಗಿ ಬೆಳೆಯುತ್ತದೆ."
    },
    "best fertilizer for wheat": {
        "en": "Urea and DAP are commonly used for wheat growth.",
        "hi": "गेहूँ की वृद्धि के लिए यूरिया और डीएपी का उपयोग होता है।",
        "te": "గోధుమలకు యూరియా మరియు డీఏపీ వాడతారు.",
        "ta": "கோதுமை வளர்ச்சிக்கு யூரியா மற்றும் டி.ஏ.பி பயன்படுத்தப்படுகின்றன.",
        "kn": "ಗೋಧಿ ಬೆಳವಣಿಗೆಗೆ ಯೂರಿಯಾ ಮತ್ತು ಡಿಎಪಿ ಬಳಸಲಾಗುತ್ತದೆ."
    },
    "best crop for sandy soil": {
        "en": "Groundnut, watermelon, and potato grow well in sandy soil.",
        "hi": "रेतीली मिट्टी में मूंगफली, तरबूज और आलू अच्छे उगते हैं।",
        "te": "ఇసుక మట్టిలో పల్లీలు, పుచ్చకాయ, బంగాళదుంపలు బాగా పెరుగుతాయి.",
        "ta": "மணல் மண்ணில் கடலை, தர்பூசணி, உருளைக்கிழங்கு நல்லது.",
        "kn": "ಮರಳು ಮಣ್ಣಿನಲ್ಲಿ ಕಡಲೆಕಾಯಿ, ಕಲ್ಲಂಗಡಿ, ಆಲೂಗಡ್ಡೆ ಚೆನ್ನಾಗಿ ಬೆಳೆಯುತ್ತವೆ."
    },

    # ---- FERTILIZER / SOIL ----
    "what is npk fertilizer": {
        "en": "NPK fertilizer contains Nitrogen (N), Phosphorus (P), and Potassium (K).",
        "hi": "एनपीके खाद में नाइट्रोजन, फॉस्फोरस और पोटैशियम होते हैं।",
        "te": "ఎన్‌పీకే ఎరువులో నైట్రోజన్, ఫాస్పరస్, పొటాషియం ఉంటాయి.",
        "ta": "என்என்பிகே உரத்தில் நைட்ரஜன், பாஸ்பரஸ், பொட்டாசியம் உள்ளன.",
        "kn": "ಎನ್‌ಪಿಕೆ ರಸಗೊಬ್ಬರದಲ್ಲಿ ನೈಸರ್ಗಿಕ, ಫಾಸ್ಪರಸ್ ಮತ್ತು ಪೊಟ್ಯಾಸಿಯಂ ಇವೆ."
    },
    "improve soil fertility": {
        "en": "Add organic compost, green manure, and crop rotation to improve soil.",
        "hi": "जैविक खाद, हरी खाद और फसल चक्र से मिट्टी की उर्वरता बढ़ाएँ।",
        "te": "సేంద్రీయ ఎరువు, గ్రీన్ మాన్యూర్, పంట మార్పిడి వాడాలి.",
        "ta": "செயற்கை உரம், பச்சை உரம், பயிர் மாறுதல் மூலம் மண் வளம் அதிகரிக்கும்.",
        "kn": "ಸೇಂದ್ರೀಯ ಗೊಬ್ಬರ, ಹಸಿರು ಗೊಬ್ಬರ ಮತ್ತು ಬೆಳೆ ಬದಲಾವಣೆ ಬಳಸಬೇಕು."
    },

    # ---- DISEASES ----
    "leaf spots in rice": {
        "en": "Brown spot disease – spray fungicide like Mancozeb.",
        "hi": "ब्राउन स्पॉट रोग – मैनकोजेब का छिड़काव करें।",
        "te": "బ్రౌన్ స్పాట్ వ్యాధి – మాంకోజెబ్ పిచికారీ చేయాలి.",
        "ta": "பழுப்பு புள்ளி நோய் – மான்கோசெப் தெளிக்கவும்.",
        "kn": "ಬ್ರೌನ್ ಸ್ಪಾಟ್ ರೋಗ – ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ."
    },
    "yellow leaves in maize": {
        "en": "It may be nitrogen deficiency. Apply urea.",
        "hi": "यह नाइट्रोजन की कमी है। यूरिया डालें।",
        "te": "ఇది నైట్రోజన్ లోపం. యూరియా వేయాలి.",
        "ta": "இது நைட்ரஜன் குறைபாடு. யூரியா போடவும்.",
        "kn": "ಇದು ನೈಟ್ರೋಜನ್ ಕೊರತೆ. ಯೂರಿಯಾ ಹಾಕಿ."
    },

    # ---- MARKET & SCHEMES ----
    "government schemes": {
        "en": "PM-Kisan, Soil Health Card, and Crop Insurance are available schemes.",
        "hi": "पीएम-किसान, मिट्टी स्वास्थ्य कार्ड, फसल बीमा उपलब्ध योजनाएँ हैं।",
        "te": "పీఎం-కిసాన్, మట్టి ఆరోగ్య కార్డు, పంట బీమా అందుబాటులో ఉన్నాయి.",
        "ta": "பிரதமர்-கிசான், மண் ஆரோக்கிய அட்டை, பயிர் காப்பீடு உள்ளன.",
        "kn": "ಪಿಎಂ-ಕಿಸಾನ್, ಮಣ್ಣು ಆರೋಗ್ಯ ಕಾರ್ಡ್ ಮತ್ತು ಬೆಳೆ ವಿಮೆ ಲಭ್ಯವಿದೆ."
    },
    "market price of rice": {
        "en": "Rice price is around ₹2300 per quintal.",
        "hi": "चावल का दाम लगभग ₹2300 प्रति क्विंटल है।",
        "te": "బియ్యం ధర సుమారు ₹2300 క్వింటాల్.",
        "ta": "அரிசி விலை குவின்டல் ஒன்றுக்கு ₹2300.",
        "kn": "ಅಕ್ಕಿ ಬೆಲೆ ಕ್ವಿಂಟಲ್‌ಗೆ ₹2300."
    }
}

# ===================== USER MANAGEMENT =====================
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

# ===================== SOIL OCR UPLOAD =====================
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

# ===================== CROP RECOMMENDATION =====================
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

# ===================== DISEASE DETECTION =====================
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

# ===================== MARKET PRICES =====================
@app.route("/market_prices")
def market_prices():
    prices = {"Rice": 2300, "Wheat": 1900, "Maize": 1700}
    return jsonify(prices)

# ===================== CHATBOT =====================
@app.route("/chat_assistant", methods=["POST"])
def chat_assistant():
    data = request.get_json()
    query = data.get("message", "").lower()
    lang = data.get("lang", "en").lower()

    if not query:
        return jsonify({"error": "No message provided"}), 400

    response = None
    for q, ans in chat_responses.items():
        if q in query:
            response = ans.get(lang, ans["en"])
            break

    if not response:
        response = {
            "en": "Sorry, I don't understand. Please try again.",
            "hi": "माफ़ कीजिए, मुझे समझ नहीं आया।",
            "te": "క్షమించండి, నాకు అర్థం కాలేదు.",
            "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை.",
            "kn": "ಕ್ಷಮಿಸಿ, ನನಗೆ ಅರ್ಥವಾಗಲಿಲ್ಲ."
        }.get(lang, "Sorry, I don't understand.")

    return jsonify({"reply": response})

# ===================== TRANSLATION =====================
@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json()
        text = data.get("text")
        lang = data.get("lang")
        if not text or not lang:
            return jsonify({"error": "Missing text or language"}), 400

        lang_map = {"english": "en", "hindi": "hi", "telugu": "te", "tamil": "ta", "kannada": "kn"}
        target_lang = lang_map.get(lang.lower(), "en")
        translated = GoogleTranslator(source="auto", target=target_lang).translate(text)
        return jsonify({"translation": translated})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway sets PORT dynamically
    app.run(host="0.0.0.0", port=port, debug=True)
