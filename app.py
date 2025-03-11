from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from cryptography.fernet import Fernet
import sqlite3
import json
import os
from io import BytesIO
from datetime import datetime

app = Flask(__name__)

# Simulated encryption key (store securely in production)
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

# Simulated physician signing key (replace with actual key management in production)
PHYSICIAN_KEY = "simulated-physician-key-123"

# Load simulated data
with open('medications.json') as f:
    MEDICATIONS = json.load(f)
with open('exams.json') as f:
    EXAMS = json.load(f)
with open('referrals.json') as f:
    REFERRALS = json.load(f)

def get_db_connection():
    db_path = '/app/emr.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Ensure directory exists
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS encounters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT,
            patient_name TEXT,
            cpf TEXT,
            annotations TEXT,
            diagnostic_hypothesis TEXT,
            treatment_plan BLOB
        );
        CREATE TABLE IF NOT EXISTS conducts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id INTEGER,
            type TEXT,
            details TEXT,
            FOREIGN KEY (encounter_id) REFERENCES encounters(id)
        );
    ''')
    conn.commit()
    conn.close()

# Initialize database on first request to ensure disk is mounted
@app.before_first_request
def initialize_database():
    init_db()

# Route to render the encounter form
@app.route('/encounter/new', methods=['GET'])
def new_encounter():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO encounters (status) VALUES ('draft')")
    encounter_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return render_template('encounter.html', encounter_id=encounter_id)

# API for autocomplete suggestions
@app.route('/api/suggestions/<type>', methods=['GET'])
def get_suggestions(type):
    query = request.args.get('q', '').lower()
    if type == 'medications':
        suggestions = [m for m in MEDICATIONS if query in m.lower()]
    elif type == 'exams':
        suggestions = [e for e in EXAMS if query in e.lower()]
    elif type == 'referrals':
        suggestions = [r for r in REFERRALS if query in r.lower()]
    else:
        return jsonify({'error': 'Invalid type'}), 400
    return jsonify(suggestions[:10])

# API to add a conduct
@app.route('/api/conduct/add', methods=['POST'])
def add_conduct():
    data = request.get_json()
    encounter_id = data.get('encounter_id')
    conduct_type = data.get('type')
    details = data.get('details')

    if not all([encounter_id, conduct_type, details]):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conducts (encounter_id, type, details) VALUES (?, ?, ?)",
        (encounter_id, conduct_type, json.dumps(details))
    )
    conn.commit()
    conduct_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': conduct_id, 'type': conduct_type, 'details': details})

# API to commit conducts
@app.route('/api/conduct/commit/<int:encounter_id>', methods=['POST'])
def commit_conducts(encounter_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch encounter and conducts
        cursor.execute("SELECT * FROM encounters WHERE id = ?", (encounter_id,))
        encounter = cursor.fetchone()
        if not encounter or encounter['status'] != 'draft':
            return jsonify({'error': 'Invalid or finalized encounter'}), 400

        # Update encounter details from form data
        data = request.get_json()
        patient_name = data.get('patient_name')
        cpf = data.get('cpf')
        annotations = data.get('annotations')
        diagnostic_hypothesis = data.get('diagnostic_hypothesis')

        cursor.execute("SELECT type, details FROM conducts WHERE encounter_id = ?", (encounter_id,))
        conducts = [{'type': row['type'], 'details': json.loads(row['details'])} for row in cursor.fetchall()]

        # Create treatment plan JSON (FHIR-compatible structure)
        treatment_plan = {
            'resourceType': 'Encounter',
            'id': str(encounter_id),
            'status': 'planned',
            'subject': {'display': patient_name, 'identifier': {'value': cpf}},
            'period': {'start': datetime.utcnow().isoformat() + 'Z'},
            'reasonCode': [{'text': diagnostic_hypothesis or 'Not specified'}],
            'serviceProvider': {'display': 'Physician'},
            'extension': [
                {
                    'url': 'http://example.com/treatmentPlan',
                    'valueCodeableConcept': {
                        'coding': [{'system': 'http://example.com/conducts', 'code': 'conducts'}],
                        'text': json.dumps(conducts)
                    }
                }
            ],
            'signature': {
                'type': [{'system': 'http://hl7.org/fhir/v3/ParticipationSignature', 'code': 'S'}],
                'when': datetime.utcnow().isoformat() + 'Z',
                'who': {'display': 'Physician'},
                'data': PHYSICIAN_KEY
            }
        }

        # Encrypt the treatment plan
        treatment_json = json.dumps(treatment_plan)
        encrypted_med = cipher.encrypt(treatment_json.encode())

        # Update encounter with treatment plan and details
        cursor.execute(
            "UPDATE encounters SET status = 'finalized', patient_name = ?, cpf = ?, annotations = ?, diagnostic_hypothesis = ?, treatment_plan = ? WHERE id = ?",
            (patient_name, cpf, annotations, diagnostic_hypothesis, encrypted_med, encounter_id)
        )
        conn.commit()
        conn.close()

        # Send encrypted file for download
        return send_file(
            BytesIO(encrypted_med),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'treatment_plan_{encounter_id}.med'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to list encounters
@app.route('/encounters', methods=['GET'])
def list_encounters():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, patient_name, cpf, status FROM encounters")
    encounters = cursor.fetchall()
    conn.close()
    return render_template('encounters.html', encounters=encounters)

# API to retrieve encounter .med file
@app.route('/api/encounter/<int:id>', methods=['GET'])
def get_encounter(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT treatment_plan FROM encounters WHERE id = ?", (id,))
    encounter = cursor.fetchone()
    conn.close()
    if encounter and encounter['treatment_plan']:
        return send_file(
            BytesIO(encounter['treatment_plan']),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'encounter_{id}.med'
        )
    return jsonify({'error': 'Encounter not found or no treatment plan available'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
