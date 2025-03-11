# Medical Encounter Module

## Description

The **Medical Encounter Module** is a standalone component of an Electronic Medical Record (EMR) system designed to efficiently record and manage patient visits. Built with Python and Flask, it provides healthcare providers with a simple, HIPAA-compliant tool to document critical encounter details, ensuring data privacy and authenticity.

### Features

#### Patient Visit Recording
- Captures essential information for a single patient encounter, including:
  - Patient Name
  - CPF (Brazilian 11-digit identifier)
  - Annotations (e.g., patient history or anamnesis)
  - Diagnostic Hypothesis
  - Medical Conduct (treatment plan)
- Data is input via an intuitive web form.

#### Data Security
- Encrypts all sensitive data using an application-managed key, meeting HIPAA standards for protecting Protected Health Information (PHI).
- Stores encrypted data in a SQLite database for reliable, portable record-keeping.

#### Physician Action Authentication
- Requires the physician to sign the encounter with a personal signing key, generating a unique signature for the encrypted `.med` file (a JSON-based encounter report).
- This "entangles" the physician’s authority to the record, ensuring authenticity and accountability.

#### Confirmation and Access
- After submission and signing, displays a decrypted preview of the `.med` file for immediate physician review.
- Offers an API endpoint (`/api/encounter/<id>`) to retrieve the encrypted `.med` file and signature, enabling integration with other EMR modules.

#### Medical Conduct
- Allows adding multiple medical conducts per encounter:
  - **Medication Prescription**: Select generic name (e.g., amitriptyline), dose, and administration periods.
  - **Exam Request**: Autocomplete options (e.g., "Magnetic Resonance") with an observations field.
  - **Referral to Professionals/Services**: Autocomplete options (e.g., "Cardiology") with an observations field.
- Conducts are displayed in a list and can be committed with the "Commit Conducts" button, generating a `.med` file.

#### Encounters List
- After finishing an encounter, the user is redirected to `/encounters`, which lists all encounters with an option to download the associated `.med` file.
- Includes a "New Encounter" button to initiate a new record.

### Requirements
- Python 3.x
- Libraries: `flask`, `cryptography`
- Simulated JSON files (`medications.json`, `exams.json`, `referrals.json`)

### Installation
1. Clone the repository: git clone https://github.com/[your-username]/medical-encounter-module.git
   - Navigate to the directory: cd medical-encounter-module
2. Install dependencies: pip install flask cryptography
3. Run the application: python app.py
4. Access `http://localhost:5000/encounter/new` in your browser.

### Project Structure
- medical_encounter_module/
  - app.py                # Flask application
  - templates/
    - encounter.html    # Encounter form
    - encounters.html   # Encounters list
  - static/
    - style.css         # Basic styling
  - medications.json      # Simulated medication database
  - exams.json            # Simulated exam database
  - referrals.json        # Simulated referral database
  - emr.db                # SQLite database (generated)

### Usage
1. Visit `/encounter/new` to create a new encounter.
2. Fill in patient details and add medical conducts.
3. Click "Commit Conducts" to finalize, download the `.med` file, and choose to edit or finish.
4. Upon finishing, view the encounters list at `/encounters` and download `.med` files as needed.

### Compliance
- **HIPAA**: Sensitive data is encrypted before storage.
- **FHIR**: The `.med` file is structured to facilitate conversion to FHIR protocols.

### Next Steps
- Implement user authentication.
- Replace JSON files with real database tables.
- Add support for editing encounters before finalization.

### License
This project is open-source under the MIT License.

---

**Author**: André Millet  
**Date**: March 10, 2025
