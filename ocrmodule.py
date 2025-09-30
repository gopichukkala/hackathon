import pytesseract
from PIL import Image
import re
import os
import tempfile

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Patterns for different report types
patterns_by_report_type = {
    "default": {
        "ph": r"pH\s*[:\-]?\s*(\d+\.?\d*)",
        "ec": r"EC\s*[:\-]?\s*(\d+\.?\d*)",
        "organic_carbon": r"Organic Carbon\s*[:\-]?\s*(\d+\.?\d*)",
        "available_n": r"Available N\s*[:\-]?\s*(\d+\.?\d*)",
        "available_p": r"Available P\s*[:\-]?\s*(\d+\.?\d*)",
        "available_k": r"Available K\s*[:\-]?\s*(\d+\.?\d*)"
    }
}

def detect_report_type(raw_text):
    text_lower = raw_text.lower()
    if "ph value" in text_lower or "electrical conductivity" in text_lower:
        return "labA"
    elif "ph level" in text_lower or "nitrogen" in text_lower:
        return "labB"
    else:
        return "default"

def extract_soil_values(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        file.save(temp_file.name)
        temp_filename = temp_file.name

    raw_text = ""
    try:
        with Image.open(temp_filename) as img:
            if img.format == "GIF":
                img.seek(0)
                img = img.convert("RGB")
            else:
                img = img.convert("RGB")
            img.save(temp_filename, format="PNG")
            raw_text = pytesseract.image_to_string(img)
    except Exception as e:
        print("OCR error:", e)
    finally:
        os.unlink(temp_filename)

    report_type = detect_report_type(raw_text)
    patterns = patterns_by_report_type.get(report_type, patterns_by_report_type["default"])

    values = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            try:
                values[key] = float(match.group(1))
            except ValueError:
                pass

    # Map OCR keys to model keys
    mapped_values = {
        "N": values.get("available_n", 0),
        "P": values.get("available_p", 0),
        "K": values.get("available_k", 0),
        "ph": values.get("ph", 0),
        "ec": values.get("ec", 0),
        "organic_carbon": values.get("organic_carbon", 0)
    }

    return {
        "raw_text": raw_text,
        "values": mapped_values,
        "report_type": report_type
    }
