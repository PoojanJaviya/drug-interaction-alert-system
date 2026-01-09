from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from services import analyze_prescription_image

load_dotenv()

# CONFIGURATION:
# 1. static_folder='../frontend': Tells Flask where your HTML/CSS/JS files are.
# 2. static_url_path='': Allows accessing files directly (e.g., /style.css instead of /static/style.css)
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# --- SERVE FRONTEND (Root URL) ---
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze endpoint.
    Payload: 
    - image (File)
    - description (String, optional) - User notes
    """
    # Check for mock flag
    use_mock = request.args.get('mock', '').lower() == 'true'

    # Get optional user description (e.g., "Patient takes aspirin daily")
    user_text = request.form.get('description', '')

    file_path = None

    try:
        # Handle Image
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)
        
        # Validation: We need at least an image OR text
        if not file_path and not user_text:
             return jsonify({"error": "Please provide an image or a description."}), 400

        # Process
        result = analyze_prescription_image(file_path, user_text, use_mock=use_mock)

        # Cleanup
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            "status": "success",
            "data": result
        })

    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)