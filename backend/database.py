import sqlite3
import json
import csv
import os
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

    # 2. Drug Reference Table
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
    """Populates the drug database from CSV or default data."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Check if empty
        c.execute('SELECT count(*) FROM drug_reference')
        if c.fetchone()[0] == 0:
            csv_path = "drugs.csv" 
            
            # Try finding CSV in current folder or backend folder
            if not os.path.exists(csv_path):
                csv_path = os.path.join("backend", "drugs.csv")

            if os.path.exists(csv_path):
                print(f"Seeding Drug Database from {csv_path}...")
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        to_db = []
                        for row in reader:
                            # Clean keys (strip spaces)
                            r = {k.strip(): v.strip() for k, v in row.items()}
                            to_db.append((
                                r.get('name', ''), 
                                r.get('category', ''), 
                                r.get('use', ''), 
                                r.get('side_effects', ''), 
                                r.get('caution', '')
                            ))
                        
                        c.executemany('INSERT INTO drug_reference (name, category, use, side_effects, caution) VALUES (?, ?, ?, ?, ?)', to_db)
                        conn.commit()
                        print(f"Successfully imported {len(to_db)} drugs.")
                except Exception as e:
                    print(f"CSV Import Error: {e}")
            else:
                print("CSV not found. Seeding with default small set...")
                drugs = [
                    ("Amoxicillin", "Antibiotic", "Treats bacterial infections.", "Nausea, rash.", "Finish full course."),
                    ("Ibuprofen", "NSAID", "Pain relief.", "Stomach upset.", "Take with food."),
                    ("Paracetamol", "Analgesic", "Pain relief.", "Liver toxicity.", "Max 4g/day.")
                ]
                c.executemany('INSERT INTO drug_reference (name, category, use, side_effects, caution) VALUES (?, ?, ?, ?, ?)', drugs)
                conn.commit()
    except Exception as e:
        print(f"Database Seeding Error: {e}")
    
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

def save_report(patient_id, medicines, risk_level, alert_message=""):
    """Saves the result of an analysis."""
    if not patient_id or not medicines:
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    meds_json = json.dumps(medicines)
    
    try:
        c.execute('INSERT INTO patient_history (patient_id, medicines, risk_level, alert_message) VALUES (?, ?, ?, ?)', 
                  (patient_id, meds_json, risk_level, alert_message))
    except sqlite3.OperationalError:
        # Fallback for old DB schemas if necessary
        pass

    conn.commit()
    conn.close()

def get_patient_history(patient_id):
    """
    Fetches unique medicines for AI context.
    """
    if not patient_id:
        return []

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('SELECT medicines FROM patient_history WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 10', (patient_id,))
        rows = c.fetchall()
        
        history_meds = set()
        for row in rows:
            try:
                meds = json.loads(row[0])
                for m in meds:
                    history_meds.add(m)
            except:
                continue
        conn.close()
        return list(history_meds)
    except Exception as e:
        print(f"DB Error get_history: {e}")
        conn.close()
        return []

def get_patient_reports(patient_id):
    """
    Fetches full report history for the Frontend UI.
    """
    if not patient_id:
        return []

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute('SELECT id, timestamp, medicines, risk_level, alert_message FROM patient_history WHERE patient_id = ? ORDER BY timestamp DESC', (patient_id,))
        rows = c.fetchall()
        conn.close()

        reports = []
        for row in rows:
            try:
                meds = json.loads(row['medicines'])
            except:
                meds = []
                
            reports.append({
                "id": row['id'],
                "date": row['timestamp'],
                "meds": meds,
                "risk": row['risk_level'],
                "alert": row['alert_message'] or "No details available."
            })
            
        return reports
    except Exception as e:
        print(f"DB Error get_reports: {e}")
        conn.close()
        return []

# Initialize immediately when imported
init_db()