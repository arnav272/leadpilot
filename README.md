# LeadPilot AI — Business Intelligence Audit Generator

LeadPilot AI is an asynchronous lead capture and business evaluation automation pipeline. The system enriches incoming lead domains, triggers a Groq-powered Llama-3 evaluation engine to run deep corporate mapping, generates an editorial-grade, minimalist PDF audit report, and delivers it instantly to client inboxes using Resend.

## 🚀 Key Features

- **Asynchronous Data Stream:** Emits real-time processing events via FastAPI StreamingResponse directly to the frontend.
- **Premium Editorial Engine:** Generates minimalist PDF business audits prioritizing whitespace and unbordered typographic stacks (no boxes or tables).
- **Automated Mailroom Pipeline:** Attaches and delivers compiled PDF files directly to user inboxes using the Resend email engine.
- **Google Workspace Sync:** Progressively updates a centralized Google Sheets CRM index and archives generated PDFs to an explicit Google Drive destination folder.

## 📁 Repository Directory Map

```text
leadpilot/ (Project Root)
├── services/               # Core Application Directory
│   ├── main.py             # FastAPI App Engine & Routing Core
│   ├── ai_report.py        # Evaluation Pipeline Logic
│   ├── email_sender.py     # Resend Transaction Engine 
│   ├── enrichment.py       # Domain Scraper & Deep Metadata Worker
│   ├── google_services.py  # Google CRM & Drive Archive Connections
│   └── pdf_generator.py    # Premium FPDF2 Typographic Layout Builder
├── templates/              # Production UI Pages served by FastAPI
│   ├── form.html           # Inbound Customer Intake Portal
│   └── report_template.html# Live Dynamic Interactive Report Layout
├── .env                    # System Local Environment File
├── credentials.json        # Google Cloud Service Account Matrix
└── requirements.txt        # Unified Application Dependencies