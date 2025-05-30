from flask import Flask, request, jsonify, send_from_directory, send_file
import os
import base64
import json
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter
import io

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# OpenAI integration - REQUIRED (no fallback)
try:
    from openai import OpenAI
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    openai_client = OpenAI(api_key=api_key)
    OPENAI_AVAILABLE = True
    print("✅ OpenAI integration enabled - REAL AI MODE ONLY")
except ImportError as e:
    print(f"❌ CRITICAL ERROR: OpenAI package not available: {e}")
    print("Install with: pip install openai")
    OPENAI_AVAILABLE = False
    openai_client = None
except ValueError as e:
    print(f"❌ CRITICAL ERROR: {e}")
    print("Set your OpenAI API key in the .env file")
    OPENAI_AVAILABLE = False
    openai_client = None

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_path):
    """Encode image to base64 for OpenAI API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_openai(image_path, user_prompt):
    """Analyze image using OpenAI Vision API and generate LUT instructions - REAL AI ONLY"""
    if not OPENAI_AVAILABLE or not openai_client:
        raise Exception("OpenAI integration is not available. Real AI analysis cannot be performed. Please check your API key and installation.")
    
    try:
        base64_image = encode_image(image_path)
        
        print(f"🧠 Sending image to OpenAI GPT-4o Vision for analysis...")
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze this image and the user's request: "{user_prompt}"

Please provide specific color grading instructions that would achieve the desired look. Return a JSON object with these exact keys:
{{
    "base_style": "brief description of the overall look",
    "adjustments": {{
        "temperature": "value from -100 to +100 (negative=cooler, positive=warmer)",
        "tint": "value from -100 to +100 (negative=green, positive=magenta)",
        "exposure": "value from -2.0 to +2.0 (exposure adjustment)",
        "contrast": "value from -100 to +100 (contrast adjustment)",
        "highlights": "value from -100 to +100 (highlight recovery)",
        "shadows": "value from -100 to +100 (shadow lift)",
        "whites": "value from -100 to +100 (white point)",
        "blacks": "value from -100 to +100 (black point)",
        "saturation": "value from -100 to +100 (color intensity)",
        "vibrance": "value from -100 to +100 (selective saturation)"
    }},
    "color_wheels": {{
        "shadows": {{"red": 0.0, "green": 0.0, "blue": 0.0}},
        "midtones": {{"red": 0.0, "green": 0.0, "blue": 0.0}},
        "highlights": {{"red": 0.0, "green": 0.0, "blue": 0.0}}
    }},
    "description": "detailed explanation of the color grading approach"
}}

Analyze the image's current color temperature, contrast, and lighting conditions, then provide specific numeric adjustments to achieve the requested look."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1500
        )
        
        print(f"✅ OpenAI response received successfully")
        
        # Parse the JSON response
        content = response.choices[0].message.content
        try:
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_content = content[json_start:json_end]
            result = json.loads(json_content)
            print(f"🎨 Generated color grading: {result.get('base_style', 'Custom Look')}")
            return result
        except json.JSONDecodeError as e:
            raise Exception(f"OpenAI returned invalid JSON response: {e}")
            
    except Exception as e:
        error_msg = f"OpenAI API Error: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)

def create_test_image(original_image_path, lut_instructions, output_path):
    """Create a test image showing the LUT effect"""
    try:
        img = Image.open(original_image_path)
        img = img.convert('RGB')
        
        # Apply basic adjustments based on LUT instructions
        adjustments = lut_instructions.get('adjustments', {})
        
        # Apply contrast
        if 'contrast' in adjustments:
            contrast_val = float(str(adjustments['contrast']).replace('+', ''))
            if contrast_val != 0:
                contrast_factor = 1.0 + (contrast_val / 100.0)
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast_factor)
        
        # Apply saturation
        if 'saturation' in adjustments:
            sat_val = float(str(adjustments['saturation']).replace('+', ''))
            if sat_val != 0:
                sat_factor = 1.0 + (sat_val / 100.0)
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(sat_factor)
        
        # Apply brightness (approximating exposure)
        if 'exposure' in adjustments:
            exp_val = float(str(adjustments['exposure']).replace('+', ''))
            if exp_val != 0:
                brightness_factor = 1.0 + (exp_val / 2.0)
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness_factor)
        
        # Resize for web display (max 800px wide)
        if img.width > 800:
            ratio = 800 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)
        
        img.save(output_path, "JPEG", quality=85)
        return output_path
        
    except Exception as e:
        print(f"Test image creation error: {str(e)}")
        return None

@app.route("/")
def frontend():
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"message": "Frontend not found"})

@app.route("/api/health")
def health_check():
    openai_status = "enabled" if OPENAI_AVAILABLE else "disabled"
    return jsonify({
        "status": "healthy" if OPENAI_AVAILABLE else "openai_required", 
        "service": "adaptive-lut-app",
        "openai_integration": openai_status,
        "mode": "real_ai_only" if OPENAI_AVAILABLE else "openai_required"
    })

@app.route("/api/process-lut", methods=["POST"])
def process_lut():
    try:
        # Check OpenAI availability first
        if not OPENAI_AVAILABLE:
            return jsonify({
                "error": "OpenAI integration is required for real AI analysis",
                "message": "This app is configured for OpenAI-only mode. Please check your API key configuration.",
                "required_action": "Set OPENAI_API_KEY environment variable"
            }), 503
        
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files["image"]
        prompt = request.form.get("prompt", "")
        
        if file.filename == "" or not prompt:
            return jsonify({"error": "Missing file or prompt"}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save uploaded image
            upload_path = f"static/temp/upload_{timestamp}_{filename}"
            file.save(upload_path)
            
            try:
                # Analyze image with OpenAI (REAL AI ONLY)
                print(f"🚀 Starting OpenAI analysis for: '{prompt}'")
                lut_instructions = analyze_image_with_openai(upload_path, prompt)
                print(f"✅ OpenAI analysis completed successfully")
                
                # Generate LUT file
                from lut_generator import create_lut_from_json
                lut_filename = f"adaptive_lut_{timestamp}.cube"
                lut_path = f"static/luts/{lut_filename}"
                cube_file_path = create_lut_from_json(lut_instructions, output_path=lut_path)
                
                # Create test image
                test_image_filename = f"test_result_{timestamp}.jpg"
                test_image_path = f"static/temp/{test_image_filename}"
                test_image_created = create_test_image(upload_path, lut_instructions, test_image_path)
                
                response_data = {
                    "message": "LUT generated successfully with OpenAI analysis!",
                    "lut_instructions": lut_instructions,
                    "download_url": f"/download/lut/{lut_filename}",
                    "lut_file": lut_filename,
                    "status": "success",
                    "ai_mode": "openai_gpt4o_vision",
                    "analysis_type": "real_ai"
                }
                
                if test_image_created:
                    response_data["test_image_url"] = f"/static/temp/{test_image_filename}"
                
                return jsonify(response_data)
                
            except Exception as e:
                error_message = str(e)
                print(f"❌ OpenAI Analysis Error: {error_message}")
                
                # Clean up uploaded file
                try:
                    os.remove(upload_path)
                except:
                    pass
                
                return jsonify({
                    "error": "OpenAI analysis failed",
                    "message": error_message,
                    "ai_mode": "openai_required",
                    "suggestion": "Check your OpenAI API key and internet connection"
                }), 500
        else:
            return jsonify({"error": "Invalid file type. Please upload JPEG or PNG images."}), 400
            
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

@app.route("/download/lut/<filename>")
def download_lut(filename):
    """Download LUT file"""
    try:
        lut_path = f"static/luts/{filename}"
        if os.path.exists(lut_path):
            return send_file(lut_path, as_attachment=True, download_name=filename, mimetype='application/octet-stream')
        else:
            return jsonify({"error": "LUT file not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Download error: {str(e)}"}), 500

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    os.makedirs("static/temp", exist_ok=True)
    os.makedirs("static/luts", exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    print(f"🎨 Adaptive LUT Server starting on port {port}")
    print(f"📁 Static files directory: {os.path.abspath('static')}")
    if OPENAI_AVAILABLE:
        print(f"🤖 AI Mode: OpenAI GPT-4o Vision (REAL AI ONLY)")
        print(f"🧠 Ready to analyze images with real artificial intelligence!")
    else:
        print(f"❌ AI Mode: OpenAI Required - App will not process images without API key")
        print(f"🔧 Please set OPENAI_API_KEY in your .env file")
    app.run(host="0.0.0.0", port=port, debug=True)
