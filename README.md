NetGuard AI

AI-Driven Multi-Vendor Network Security Compliance Auditor

NetGuard AI is a network security compliance auditing platform developed
for Smart India Hackathon (SIH) 2026. It analyzes network device
configuration files, converts vendor-specific syntax into a common
Security Baseline Model (SBM) using Google Gemini, evaluates the SBM
against security frameworks, generates remediation guidance, and
produces PDF compliance reports.

Problem Statement

Network devices from different vendors use different configuration
syntaxes. Manually checking these configurations against security
standards is time-consuming, difficult to scale, and prone to human
error.

Security teams also need to evaluate configurations against frameworks
such as:

CIS Benchmarks

NIST SP 800-53

DISA STIGs

ISO/IEC 27001

Custom security rules

NetGuard AI provides a common vendor-neutral representation and an
automated compliance workflow.

Solution

Network Configuration
        |
        v
Configuration Upload
        |
        v
AI Configuration Analysis
        |
        v
Security Baseline Model (SBM)
        |
        v
Compliance Engine
        |
        v
PASS / FAIL Findings
        |
        v
AI Remediation Guidance
        |
        v
PDF Compliance Report

The system also includes an AI Training Center for unfamiliar
vendor-specific configuration syntax.

Key Features

Configuration Upload

Plain-text configuration upload

Maximum 10 MB file size

SHA-256 hash generation

Duplicate configuration detection

Raw configuration preservation

AI-Based Configuration Parsing

Google Gemini analyzes uploaded configurations and extracts:

Vendor

Operating system

Hostname

Security controls

Configuration values

Confidence

Unknown configuration blocks

The parser is instructed not to invent missing values.

Security Baseline Model

Vendor-specific configuration is normalized into a common structure:

Security Baseline Model
├── authentication
├── services
├── firewall
├── logging
├── VPN
├── DNS
└── maintenance

Compliance Auditing

The compliance engine supports:

eq
neq
gte
lte
contains
not_contains
is_null
not_null

Each finding contains information such as:

Control ID

Title

Status

Severity

Actual value

Expected value

SBM field

Description

Remediation

Compliance score:

Score = (Passed Controls / Total Controls) × 100

AI Remediation

Failed controls can receive:

Risk explanation

Vendor-specific fix commands

Verification command

Caveat for unknown vendors

Remediation results are cached by vendor and control.

AI Training Center

When Gemini cannot confidently understand a vendor-specific line, it can
place the line in unknown_blocks.

An administrator can map:

Raw configuration line
        |
        v
SBM field path
        |
        v
Mapped value

Example:

Raw line:
xshield-policy account-control enabled

SBM path:
security_controls.authentication.account_management.enabled

Value:
true

The approved mapping is reused as a few-shot example during future
extraction.

PDF Reports

Reports contain:

Device information

Vendor and OS

Selected framework

Compliance score

Passed controls

Failed controls

Severity

Actual and expected values

Remediation commands

Verification commands

Web Dashboard

The frontend provides:

Dashboard

Configuration Upload

Audit

Report Viewer

SBM Viewer

Framework Management

AI Training Center

Architecture

                         +----------------------+
                         |      Web Browser     |
                         |    React Frontend    |
                         +----------+-----------+
                                    |
                                    | HTTP / REST
                                    v
                         +----------------------+
                         |    FastAPI Backend   |
                         +----------+-----------+
                                    |
              +---------------------+---------------------+
              |                     |                     |
              v                     v                     v
       +-------------+       +-------------+       +-------------+
       | AI Parser   |       | Compliance  |       | Training    |
       | + Gemini    |       | Engine      |       | Center      |
       +------+------+       +------+------+       +------+------+
              |                     |                     |
              +---------------------+---------------------+
                                    |
                                    v
                            +---------------+
                            | SQLite        |
                            | Database      |
                            +-------+-------+
                                    |
                                    v
                            +---------------+
                            | PDF Generator |
                            +---------------+

Technology Stack

Frontend

React

Vite

React Router

JavaScript

CSS

Backend

Python

FastAPI

SQLAlchemy

SQLite

Pydantic

Uvicorn

AI

Google Gemini API

Reporting

ReportLab

Development

Git

GitHub

VS Code

Project Structure

netguard-ai/
│
├── backend/
│   ├── api/
│   │   ├── upload.py
│   │   ├── audit.py
│   │   ├── frameworks.py
│   │   ├── sbm.py
│   │   ├── reports.py
│   │   └── training.py
│   │
│   ├── core/
│   │   ├── ai_parser.py
│   │   ├── gemini_client.py
│   │   ├── compliance_engine.py
│   │   ├── remediation_engine.py
│   │   └── pdf_generator.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── seed_frameworks.py
│   │
│   ├── schemas/
│   │   ├── sbm.py
│   │   └── remediation.py
│   │
│   ├── frameworks/
│   │   ├── cis_benchmark.json
│   │   ├── nist_sp800_53.json
│   │   ├── disa_stigs.json
│   │   └── iso_27001.json
│   │
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── App.jsx
│       ├── main.jsx
│       └── index.css
│
└── README.md

Requirements

Python 3.10+

Node.js 18+

npm

Git

Gemini API key

Backend Setup

cd netguard-ai/backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

Create backend/.env:

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_available_gemini_model

Start FastAPI:

uvicorn main:app --reload

Backend:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

Expected response:

{
  "status": "ok"
}

Frontend Setup

Open another terminal:

cd netguard-ai/frontend
npm install
npm run dev

Frontend:

http://localhost:5173

Make sure FastAPI is running before using the frontend.

Application Workflow

1. Upload configuration
          ↓
2. Validate + SHA-256
          ↓
3. Gemini extracts SBM
          ↓
4. Select compliance framework
          ↓
5. Run compliance audit
          ↓
6. Generate remediation
          ↓
7. Review findings
          ↓
8. Download PDF report

AI Training Workflow

Example unknown syntax:

xshield-policy account-control enabled

The system can show this as an unknown block when confidence is below
the configured training threshold.

The administrator maps it to:

SBM:
security_controls.authentication.account_management.enabled

Value:
true

After re-analysis, the approved mapping is provided to Gemini as a
few-shot example.

The training example teaches the meaning of the syntax, not a
permanent value. A future configuration may contain a different actual
value.

API Overview

GET  /health
POST /api/upload
GET  /api/frameworks
GET  /api/config/{file_id}/sbm
POST /api/audit
GET  /api/audit/{audit_id}
GET  /api/reports
GET  /api/audit/{audit_id}/pdf
GET  /api/training/pending
POST /api/training/label
POST /api/training/reanalyze/{config_file_id}
GET  /api/training/labels

Database

SQLite is used for the SIH prototype.

Main entities include:

ConfigFile
SecurityBaselineModel
Framework
FrameworkRule
Audit
TrainingLabel
RemediationCache

Testing

The backend can be checked using:

curl http://127.0.0.1:8000/health

Swagger API documentation:

http://127.0.0.1:8000/docs

The compliance engine has been tested with:

eq
neq
gte
lte
contains
not_contains
is_null
not_null

The upload workflow has also been tested for successful upload,
duplicate detection, file-size validation, SHA-256 generation, and
AI-based SBM extraction.

SIH Demo Flow

Dashboard
   ↓
Upload Cisco / sample configuration
   ↓
Show extracted SBM
   ↓
Select CIS / NIST framework
   ↓
Run Audit
   ↓
Show PASS / FAIL findings
   ↓
Show remediation commands
   ↓
Open Training Center
   ↓
Map an unknown vendor-specific line
   ↓
Re-analyze
   ↓
Show updated SBM
   ↓
Download PDF report

Project Highlights

Vendor Agnostic

The system uses a common SBM rather than requiring a separate hardcoded
parser for every vendor.

Exact Value Fidelity

The AI is instructed to use values explicitly present in the
configuration and avoid inventing missing values.

Explainable Compliance

Each finding exposes:

Control
Actual Value
Expected Value
Status
Severity
SBM Field
Description
Remediation

Human-in-the-Loop Learning

Administrators can teach the system how to interpret unfamiliar
vendor-specific configuration syntax.

Actionable Output

The system goes beyond a compliance score by providing remediation and
verification guidance for failed controls.

Scope Limitations

The current SIH prototype does not include:

Live device connections

Real-time monitoring

SIEM integration

Mobile applications

Cloud deployment

Multi-user authentication

Security Note

Use dummy configuration values for demonstrations. Do not upload real
production credentials, passwords, API keys, or other sensitive secrets
into the development/demo environment.

Framework Note

The framework JSON files included in this repository are starter/sample
rules for the SIH prototype and demonstration. They are not complete
official copies of the referenced security standards.

Team

Team DBIT Bangalore

Project: NetGuard AI --- AI-Driven Multi-Vendor Network Security
Compliance Auditor

Smart India Hackathon 2026