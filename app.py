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

# OpenAI integration - with fallback
try:
    import openai
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    OPENAI_AVAILABLE = True
    print("✅ OpenAI integration enabled")
except ImportError as e:
    print(f"⚠️  OpenAI not available (using simulated AI): {e}")
    OPENAI_AVAILABLE = False

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_path):
    """Encode image to base64 for OpenAI API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_openai(image_path, user_prompt):
    """Analyze image using OpenAI Vision API and generate LUT instructions"""
    if not OPENAI_AVAILABLE:
        return simulate_ai_analysis(user_prompt)
    
    try:
        base64_image = encode_image(image_path)
        
        response = openai.chat.completions.create(
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
        
        # Parse the JSON response
        content = response.choices[0].message.content
        try:
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_content = content[json_start:json_end]
            return json.loads(json_content)
        except:
            return simulate_ai_analysis(user_prompt)
            
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        return simulate_ai_analysis(user_prompt)

def simulate_ai_analysis(user_prompt):
    """Simulate AI analysis with intelligent responses based on common color grading requests"""
    prompt_lower = user_prompt.lower()
    
    # Analyze prompt for key terms and generate appropriate adjustments
    base_adjustments = {
        "temperature": 0,
        "tint": 0,
        "exposure": 0,
        "contrast": 0,
        "highlights": 0,
        "shadows": 0,
        "whites": 0,
        "blacks": 0,
        "saturation": 0,
        "vibrance": 0
    }
    
    style_name = "Adaptive AI Look"
    description = "AI-generated color grading based on your description"
    
    # Warm/Cool temperature adjustments
    if any(word in prompt_lower for word in ["warm", "golden", "sunset", "orange", "amber"]):
        base_adjustments["temperature"] = 25
        base_adjustments["tint"] = -5
        style_name = "Warm Cinematic Look"
        description = "Warm, golden color grading with enhanced orange tones"
    elif any(word in prompt_lower for word in ["cool", "blue", "teal", "cyan", "winter", "cold"]):
        base_adjustments["temperature"] = -20
        base_adjustments["tint"] = 10
        style_name = "Cool Modern Look"
        description = "Cool, modern color grading with blue-teal tones"
    
    # Cinematic styles
    if any(word in prompt_lower for word in ["cinematic", "film", "movie", "dramatic"]):
        base_adjustments["contrast"] = 20
        base_adjustments["shadows"] = -15
        base_adjustments["highlights"] = -10
        base_adjustments["saturation"] = 10
        style_name = "Cinematic Film Look"
        description = "Dramatic cinematic color grading with enhanced contrast"
    
    # Vintage/Film styles
    if any(word in prompt_lower for word in ["vintage", "retro", "film", "analog", "kodak", "fuji"]):
        base_adjustments["temperature"] = 15
        base_adjustments["contrast"] = -10
        base_adjustments["saturation"] = -5
        base_adjustments["vibrance"] = 15
        style_name = "Vintage Film Look"
        description = "Classic film emulation with vintage color characteristics"
    
    # High contrast/moody
    if any(word in prompt_lower for word in ["moody", "dark", "dramatic", "high contrast"]):
        base_adjustments["contrast"] = 30
        base_adjustments["shadows"] = -25
        base_adjustments["blacks"] = 15
        base_adjustments["saturation"] = 15
        style_name = "Moody Dramatic Look"
        description = "High contrast, moody color grading with deep shadows"
    
    # Bright/airy
    if any(word in prompt_lower for word in ["bright", "airy", "light", "clean", "fresh"]):
        base_adjustments["exposure"] = 0.3
        base_adjustments["highlights"] = -20
        base_adjustments["shadows"] = 20
        base_adjustments["whites"] = 10
        style_name = "Bright & Airy Look"
        description = "Light, airy color grading with lifted shadows"
    
    # Teal and Orange
    if any(word in prompt_lower for word in ["teal", "orange", "blockbuster", "hollywood"]):
        base_adjustments["temperature"] = 10
        base_adjustments["tint"] = 15
        base_adjustments["contrast"] = 25
        base_adjustments["saturation"] = 20
        style_name = "Teal & Orange Blockbuster"
        description = "Hollywood blockbuster style with teal highlights and orange skin tones"
    
    return {
        "base_style": style_name,
        "adjustments": base_adjustments,
        "color_wheels": {
            "shadows": {"red": 0.0, "green": 0.0, "blue": 0.0},
            "midtones": {"red": 0.0, "green": 0.0, "blue": 0.0},
            "highlights": {"red": 0.0, "green": 0.0, "blue": 0.0}
        },
        "description": description
    }

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
    openai_status = "enabled" if OPENAI_AVAILABLE else "simulated"
    return jsonify({
        "status": "healthy", 
        "service": "adaptive-lut-app",
        "openai_integration": openai_status
    })

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
            
            # Save uploaded image
            upload_path = f"static/temp/upload_{timestamp}_{filename}"
            file.save(upload_path)
            
            # Analyze image (with OpenAI or simulation)
            lut_instructions = analyze_image_with_openai(upload_path, prompt)
            
            # Generate LUT file
            try:
                from lut_generator import create_lut_from_json
                lut_filename = f"adaptive_lut_{timestamp}.cube"
                lut_path = f"static/luts/{lut_filename}"
                cube_file_path = create_lut_from_json(lut_instructions, output_path=lut_path)
                
                # Create test image
                test_image_filename = f"test_result_{timestamp}.jpg"
                test_image_path = f"static/temp/{test_image_filename}"
                test_image_created = create_test_image(upload_path, lut_instructions, test_image_path)
                
                response_data = {
                    "message": "LUT generated successfully!",
                    "lut_instructions": lut_instructions,
                    "download_url": f"/download/lut/{lut_filename}",
                    "lut_file": lut_filename,
                    "status": "success",
                    "ai_mode": "openai" if OPENAI_AVAILABLE else "simulated"
                }
                
                if test_image_created:
                    response_data["test_image_url"] = f"/static/temp/{test_image_filename}"
                
                return jsonify(response_data)
                
            except Exception as e:
                return jsonify({"error": f"LUT generation error: {str(e)}"}), 500
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
    print(f"🤖 AI Mode: {'OpenAI GPT-4o Vision' if OPENAI_AVAILABLE else 'Simulated Intelligence'}")
    app.run(host="0.0.0.0", port=port, debug=True)
