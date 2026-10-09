from flask import Flask, jsonify, render_template, request
import pytesseract
from PIL import Image
import io
import re

app = Flask(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    # 1. Check if file is uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # 2. Check if file format is valid
    if not is_allowed_file(file.filename):
        return jsonify({"error": "Invalid file format. Please upload a PDF, PNG, or JPG document."}), 400

    # 3. Read file data
    file_data = file.read()
    file_size_kb = len(file_data) / 1024

    flags = []
    score = 100

    # Basic Document Health Checks
    if file_size_kb < 10:
        score -= 10
        flags.append("Document image size is too small or resolution is very low.")

    # --- ASLI AI/OCR WORKFLOW (BINA EASYOCR KE ERROR KE) ---
    try:
        # File data ko image me badlein aur pytesseract se text padhein
        image = Image.open(io.BytesIO(file_data))
        full_text = pytesseract.image_to_string(image).upper()
        
        # --- RULE 1: 'NULL' Ya 'MISSING' Text Ki Janch ---
        null_keywords = ['NULL', 'MISSING VALUES', 'IMPROPER VALUE']
        found_nulls = [kw for kw in null_keywords if kw in full_text]
        if found_nulls:
            score -= 30
            flags.append("Critical Compliance Failure: Missing/Blank fields found in data text.")

        # --- RULE 2: Umar Me Minus Value (-ve Age) Ki Janch ---
        negative_ages = re.findall(r'-\s*\d+', full_text)
        if negative_ages:
            score -= 40
            flags.append(f"Severe Integrity Violation: Negative age values detected (Found: {', '.join(negative_ages)}).")

        # --- RULE 3: Health Symptoms Mismatch Check ---
        if 'YES' in full_text and ('HEALTH' in full_text or 'SYMPTOM' in full_text):
            if 'NULL' in full_text:
                score -= 20
                flags.append("Labour Welfare Risk: Health symptoms flagged 'Yes' but full review logs are incomplete.")

    except Exception as e:
        # Agar OCR fail ho jaye toh safe fallback ho
        flags.append(f"OCR Reader Warning: Could not process deep text inspection. ({str(e)})")
        score -= 20

    # Final score 0 se kam nahi ho sakta
    if score < 0:
        score = 0

    # Determine Risk Level based on updated smart score
    if score >= 85:
        risk_level = "LOW RISK"
    elif score >= 50:
        risk_level = "MEDIUM RISK"
    else:
        risk_level = "HIGH RISK"

    # Agar HIGH RISK hai, toh inspector alert true hoga
    inspector_alert = True if risk_level == "HIGH RISK" else False

    return jsonify({
        "score": score, 
        "risk": risk_level, 
        "flags": flags,
        "inspector_alert_triggered": inspector_alert
    })

if __name__ == "__main__":
    app.run(debug=True)