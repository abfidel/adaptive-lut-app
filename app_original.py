from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "message": "Welcome to the Adaptive LUT App",
        "status": "running",
        "endpoints": {
            "/": "Home",
            "/api/health": "Health check",
            "/api/process-lut": "Process LUT data"
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "adaptive-lut-app"
    })

@app.route('/api/process-lut', methods=['POST'])
def process_lut():
    """Endpoint to process LUT data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # TODO: Implement LUT processing logic here
        # This is where you'll integrate with OpenAI and LUT processing
        
        return jsonify({
            "message": "LUT processing endpoint ready",
            "received_data": data,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    ) 