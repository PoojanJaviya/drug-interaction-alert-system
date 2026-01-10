import sqlite3
import json
from datetime import datetime

DB_NAME = "medical_history.db"

def init_db():
    """Creates the tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Patient History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS patient_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            medicines TEXT,
            risk_level TEXT,
            alert_message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Drug Reference Table (NEW)
    c.execute('''
        CREATE TABLE IF NOT EXISTS drug_reference (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            use TEXT,
            side_effects TEXT,
            caution TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Auto-seed if empty
    seed_drugs()

def seed_drugs():
    """Populates the drug database with initial data if empty."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('SELECT count(*) FROM drug_reference')
    if c.fetchone()[0] == 0:
        print("Seeding Drug Database...")
        drugs = [
            ("Amoxicillin", "Antibiotic", "Treats bacterial infections.", "Nausea, rash, diarrhea.", "Finish the full course even if feeling better."),
            ("Ibuprofen", "NSAID", "Relieves pain, fever, and inflammation.", "Stomach upset, heartburn.", "Take with food. Avoid if you have ulcers."),
            ("Warfarin", "Anticoagulant", "Prevents blood clots.", "Severe bleeding, bruising.", "Regular blood tests (INR) required. Watch Vitamin K intake."),
            ("Paracetamol", "Analgesic", "Treats mild pain and fever.", "Rare; liver damage in overdose.", "Do not exceed 4g per day."),
            ("Atorvastatin", "Statin", "Lowers cholesterol.", "Muscle pain, digestive issues.", "Avoid large amounts of grapefruit juice."),
            ("Metformin", "Antidiabetic", "Treats type 2 diabetes.", "Nausea, stomach upset.", "Take with meals to reduce side effects."),
            ("Aspirin", "Blood Thinner/NSAID", "Pain relief, heart attack prevention.", "Bleeding, stomach ulcers.", "Do not mix with other blood thinners without advice."),
            ("Lisinopril", "ACE Inhibitor", "Treats high blood pressure.", "Dry cough, dizziness.", "Drink plenty of water. Avoid potassium supplements.")
        ]
        c.executemany('INSERT INTO drug_reference (name, category, use, side_effects, caution) VALUES (?, ?, ?, ?, ?)', drugs)
        conn.commit()
    
    conn.close()

def search_drugs(query):
    """Searches for drugs by name or category."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if query:
        search_term = f"%{query}%"
        c.execute('SELECT * FROM drug_reference WHERE name LIKE ? OR category LIKE ?', (search_term, search_term))
    else:
        c.execute('SELECT * FROM drug_reference') # Return all if no query
        
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

# --- Existing History Functions ---

def save_report(patient_id, medicines, risk_level, alert_message=""):
    if not patient_id or not medicines: return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    meds_json = json.dumps(medicines)
    try:
        c.execute('INSERT INTO patient_history (patient_id, medicines, risk_level, alert_message) VALUES (?, ?, ?, ?)', 
                  (patient_id, meds_json, risk_level, alert_message))
    except:
        pass # Handle schema updates if needed
    conn.commit()
    conn.close()

def get_patient_history(patient_id):
    if not patient_id: return []
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT medicines FROM patient_history WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 10', (patient_id,))
    rows = c.fetchall()
    conn.close()
    history_meds = set()
    for row in rows:
        try:
            for m in json.loads(row[0]): history_meds.add(m)
        except: continue
    return list(history_meds)

def get_patient_reports(patient_id):
    if not patient_id: return []
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, timestamp, medicines, risk_level, alert_message FROM patient_history WHERE patient_id = ? ORDER BY timestamp DESC', (patient_id,))
    rows = c.fetchall()
    conn.close()
    reports = []
    for row in rows:
        try: meds = json.loads(row['medicines'])
        except: meds = []
        reports.append({
            "id": row['id'], "date": row['timestamp'], "meds": meds,
            "risk": row['risk_level'], "alert": row['alert_message'] or "No details available."
        })
    return reports

init_db()