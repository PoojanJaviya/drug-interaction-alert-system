from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from services import analyze_prescription_image
import database 
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/manifest.json')
def serve_manifest():
    return app.send_static_file('manifest.json')

@app.route('/logo medimatch.png')
def serve_logo():
    return app.send_static_file('logo medimatch.png')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Hash the password for security
    hashed_pw = generate_password_hash(password)
    
    if database.create_user(username, hashed_pw):
        return jsonify({"status": "success", "message": "User created"})
    else:
        return jsonify({"error": "Username already exists"}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    stored_hash = database.get_user_password(username)
    
    if stored_hash and check_password_hash(stored_hash, password):
        return jsonify({"status": "success", "username": username})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# --- HISTORY ENDPOINT ---
@app.route('/api/history', methods=['GET'])
def get_history():
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return jsonify({"error": "Patient ID required"}), 400
    
    history_data = database.get_patient_reports(patient_id)
    return jsonify({"status": "success", "data": history_data})

# --- NEW: DRUG REFERENCE ENDPOINT ---
@app.route('/api/drugs', methods=['GET'])
def get_drugs():
    query = request.args.get('search', '')
    drugs = database.search_drugs(query)
    return jsonify({"status": "success", "data": drugs})

# --- ANALYZE ENDPOINT ---
@app.route('/api/analyze', methods=['POST'])
def analyze():
    use_mock = request.args.get('mock', '').lower() == 'true'
    
    user_text = request.form.get('description', '')
    language = request.form.get('language', 'English')
    conditions = request.form.get('conditions', '')
    patient_id = request.form.get('patient_id', '').strip()

    past_history = []
    if patient_id:
        past_history = database.get_patient_history(patient_id)
        print(f"Found history for {patient_id}: {past_history}")

    saved_file_paths = []

    try:
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)

        if 'image' in request.files:
            files = request.files.getlist('image')
            for file in files:
                if file.filename != '':
                    file_path = os.path.join(temp_dir, file.filename)
                    file.save(file_path)
                    saved_file_paths.append(file_path)
        
        if not saved_file_paths and not user_text:
             return jsonify({"error": "Please provide an image or a description."}), 400

        result = analyze_prescription_image(
            saved_file_paths, 
            user_text, 
            language=language, 
            conditions=conditions, 
            past_history=past_history, 
            use_mock=use_mock
        )

        if patient_id and result.get("medicines_found"):
            database.save_report(
                patient_id, 
                result["medicines_found"], 
                result.get("risk_level", "Unknown"),
                result.get("alert_message", "")
            )

        for path in saved_file_paths:
            if os.path.exists(path):
                os.remove(path)

        return jsonify({
            "status": "success",
            "data": result
        })

    except Exception as e:
        for path in saved_file_paths:
            if os.path.exists(path):
                os.remove(path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # CHANGED: host='0.0.0.0' allows access from other devices on the network
    app.run(debug=True, port=5000, host='0.0.0.0')
    