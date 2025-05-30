from flask import Flask, request, jsonify, send_from_directory
import os
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def frontend():
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"message": "Frontend not found"})

@app.route("/api/health")
def health_check():
    return jsonify({"status": "healthy", "service": "adaptive-lut-app"})

@app.route("/api/process-lut", methods=["POST"])
def process_lut():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        file = request.files["image"]
        prompt = request.form.get("prompt", "")
        if file.filename == "" or not prompt:
            return jsonify({"error": "Missing file or prompt"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            lut_instructions = {"base_style": "Test", "adjustments": {"temperature": "+5", "contrast": "-2"}}
            try:
                from lut_generator import create_lut_from_json
                lut_path = f"static/luts/test_{timestamp}.cube"
                cube_file_path = create_lut_from_json(lut_instructions, output_path=lut_path)
                return jsonify({"message": "Success", "lut_instructions": lut_instructions, "download_url": f"/static/luts/test_{timestamp}.cube", "status": "success"})
            except Exception as e:
                return jsonify({"error": f"LUT error: {str(e)}"}), 500
        else:
            return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    os.makedirs("static/temp", exist_ok=True)
    os.makedirs("static/luts", exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
