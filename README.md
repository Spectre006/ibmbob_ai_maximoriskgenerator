# AI-Powered Risk Assessment Generator for IBM Maximo

An AI-enabled Risk Assessment Generator that evaluates IBM Maximo work orders and automatically generates Job Hazard Analysis (JHA) reports — in multiple languages, with professional PDF output and a modern IBM Carbon-style interface.

**IBM BoB Hackathon Submission**

---

## 🎯 Use Case

Maximo technicians often lack the time or expertise to prepare JHA reports before starting work, which can create serious safety risks. This tool automatically generates comprehensive, multilingual JHA reports from any Maximo work order using IBM Watsonx.ai — reducing preparation time from hours to seconds.

---

## ✨ Features

### Core
- 🤖 **AI-Powered Hazard Analysis** — IBM Watsonx.ai identifies physical, chemical, biological, and ergonomic hazards
- 📋 **Automated JHA Reports** — Complete risk assessments with controls and PPE requirements
- 🔗 **Maximo Integration** — Fetches live work order data (description, location, equipment, priority, status, assigned technician) directly from IBM Maximo via REST API
- 💾 **Report Storage** — All reports persisted in IBM Cloudant with full audit trail

### Multilingual Support
- 🌍 **3 Languages** — English, French, and Hindi
- 📄 **End-to-End Translation** — AI analysis, PDF output, HTML view, and UI result card all rendered in the selected language
- 🔤 **Unicode PDF Fonts** — Arial Unicode MS (Devanagari) for Hindi; Helvetica (Latin Extended) for French — no boxes or missing characters
- 🏷️ **Translated Labels** — Every section heading, field label, and disclaimer is localised

### Report Output
- 📥 **Download PDF** — Professional IBM-styled PDF with blue header table, alternating row colours, colour-coded hazard cards (red/amber/green by risk level), and localised disclaimer
- 👁️ **View PDF** — Full HTML report rendered in a modal preview with the correct language, fonts, and labels
- 🎨 **Styled Hazard Cards** — High / Medium / Low risk visually distinguished throughout

### UI / UX
- 🖥️ **IBM Carbon Dashboard** — Dark top header with logo, white sidebar, and spacious content area
- 📂 **Two-Panel Navigation** — "Generate Report" and "View Previous Reports" sidebar links
- 📊 **Real-time Progress Bar** — Step-by-step status (fetching → analysing → building)
- 🕐 **History Table** — Previous reports sorted newest-first, with WO status badge, high-risk count badge, View PDF and Download buttons per row
- 🔍 **Search & Filter** — Instant filter across Report ID, Work Order, and description
- 🔄 **Retry on Error** — Failed generations show an inline Retry button
- ⌨️ **Keyboard Shortcut** — `Ctrl/Cmd + Enter` to generate

---

## 🏗️ Architecture

```
Browser (IBM Carbon UI)
        ↓
FastAPI Application
        ↓
┌───────────────┬──────────────────┬────────────────┐
│  Maximo REST  │  IBM Watsonx.ai  │  IBM Cloudant  │
│  (Work Orders)│  (AI Analysis)   │  (Storage)     │
└───────────────┴──────────────────┴────────────────┘
        ↓
  ReportLab PDF  /  python-docx  /  Jinja2 HTML
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- IBM Watsonx.ai API credentials
- IBM Maximo REST API access
- IBM Cloudant database
- **macOS**: Arial Unicode MS font at `/Library/Fonts/Arial Unicode.ttf` (for Hindi PDF rendering)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/maximo_riskassessement_generator.git
cd maximo_riskassessement_generator
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

| Variable | Description |
|---|---|
| `MAXIMO_BASE_URL` | IBM Maximo base URL |
| `MAXIMO_USERNAME` | Maximo API username |
| `MAXIMO_PASSWORD` | Maximo API password |
| `WATSONX_API_KEY` | IBM Watsonx.ai API key |
| `WATSONX_PROJECT_ID` | Watsonx project ID |
| `WATSONX_URL` | Watsonx service URL |
| `CLOUDANT_URL` | IBM Cloudant instance URL |
| `CLOUDANT_API_KEY` | Cloudant API key |
| `CLOUDANT_DB_NAME` | Cloudant database name |

5. **Run the application**
```bash
python app.py
```

6. **Open in browser**
```
http://localhost:8000
```

---

## 📖 Usage

### Generating a Report

1. Enter a Maximo work order number (e.g. `6455`) in the **Work Order Number** field
2. Select the **Language** — English, French, or Hindi
3. Click **Generate JHA Report** (or press `Ctrl/Cmd + Enter`)
4. The progress bar tracks each step:
   - Fetching work order from Maximo
   - Analysing hazards with Watsonx.ai
   - Building the report
5. The generated report appears below with:
   - Work order summary table (description, location, equipment, priority, WO status, assigned to)
   - All identified hazards with risk level, controls, and PPE
   - Emergency contacts
   - Additional safety notes
6. Click **View PDF** to preview the report in a modal, or **Download PDF** to save it

### Viewing Previous Reports

- Click **View Previous Reports** in the sidebar
- Reports are listed newest-first with WO status and high-risk hazard count
- Use the search box to filter by Report ID or Work Order number
- Each row has **View PDF** and **Download** buttons
- Click **Refresh** to reload the latest reports from the database

---

## 🌍 Multilingual Details

| Language | AI Prompt | PDF Font | UI Labels | HTML View |
|---|---|---|---|---|
| English | ✅ | Helvetica | ✅ | ✅ |
| French | ✅ | Helvetica (Latin Extended) | ✅ | ✅ |
| Hindi | ✅ | Arial Unicode MS (Devanagari) | ✅ | ✅ Noto Sans Devanagari |

Risk levels returned by the AI in any language variant (e.g. *Élevé*, *उच्च*, *HIGH*) are automatically normalised to the canonical `High / Medium / Low` values before storage.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI |
| AI | IBM Watsonx.ai |
| Database | IBM Cloudant (NoSQL) |
| Maximo | IBM Maximo REST API (OSLC) |
| Frontend | HTML5, Bootstrap 5, Vanilla JS |
| PDF | ReportLab (TTFont Unicode support) |
| Word | python-docx |
| Templating | Jinja2 |
| Styling | IBM Carbon Design System tokens |

---

## 📁 Project Structure

```
maximo_riskassessement_generator/
├── app.py                      # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
│
├── config/
│   ├── settings.py             # Pydantic settings management
│   └── constants.py            # Enums, prompt templates, label translations
│
├── models/
│   ├── work_order.py           # WorkOrder Pydantic model
│   └── jha_report.py           # JHAReport, Hazard, EmergencyContacts models
│
├── routes/
│   └── jha_routes.py           # All /api/jha/* endpoints
│
├── services/
│   ├── maximo_service.py       # Maximo REST API client
│   ├── ai_service.py           # Watsonx.ai integration
│   ├── cloudant_service.py     # Cloudant read/write operations
│   ├── jha_generator.py        # Report orchestration
│   ├── pdf_generator.py        # ReportLab PDF generation (multilingual)
│   └── docx_generator.py       # Word document generation
│
├── utils/
│   ├── logger.py               # Structured logging
│   ├── validators.py           # Input validation helpers
│   └── formatters.py           # Data formatting utilities
│
├── templates/
│   ├── index.html              # Main app UI (IBM Carbon layout)
│   └── report.html             # HTML report view (multilingual)
│
└── static/
    ├── css/styles.css          # IBM Carbon Design System styles
    ├── js/app.js               # Frontend logic
    └── logo.jpg                # Product logo
```

---

## 🔌 API Endpoints

### JHA Reports

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/jha/generate` | Generate a new JHA report |
| `GET` | `/api/jha/history` | List all reports (paginated, newest-first) |
| `GET` | `/api/jha/{report_id}` | Retrieve a specific report |
| `GET` | `/api/jha/{report_id}/download?format=pdf\|docx` | Download report as PDF |
| `GET` | `/api/jha/{report_id}/view` | View report as HTML (multilingual) |
| `DELETE` | `/api/jha/{report_id}` | Soft-delete a report |

**Generate request body:**
```json
{
  "work_order_id": "6455",
  "language": "en"
}
```
Supported language codes: `en` (English), `fr` (French), `hi` (Hindi)

### Health

```http
GET /health
GET /api/health
GET /api/health/detailed
```

Full interactive API docs available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.

---

## 📊 Performance

| Step | Typical Time |
|---|---|
| Work order fetch from Maximo | < 2 s |
| AI hazard analysis (Watsonx.ai) | 5–10 s |
| PDF generation | < 1 s |
| **Total end-to-end** | **< 15 s** |

---

## 🔒 Security

- All credentials stored in environment variables — never hardcoded
- Input validation on all user-supplied fields
- HTTPS for all external API calls
- Full audit trail: every generated report stored with timestamp and metadata

---

## 🐛 Troubleshooting

**Hindi text shows boxes in PDF**
- Ensure Arial Unicode MS is installed: `/Library/Fonts/Arial Unicode.ttf`
- The font is standard on macOS; on Linux install the `ttf-mscorefonts-installer` package

**French / Hindi report returns HTTP 400**
- Only `en`, `fr`, and `hi` are accepted language codes

**Risk level validation error**
- The AI may return native-language risk strings (e.g. *Élevé*, *उच्च*)
- These are automatically normalised via `normalise_risk_level()` in `models/jha_report.py`

**Work order not found**
- Confirm the WONUM exists in Maximo and the API user has read access
- Check `MAXIMO_BASE_URL` includes the correct site path

**Database errors**
- Verify Cloudant credentials and that the target database exists
- Check Cloudant API key has `_reader` + `_writer` permissions

**Enable debug logging**
```bash
# .env
LOG_LEVEL=DEBUG
```
```bash
tail -f logs/app.log
```

---

## 👥 Team

IBM BoB Hackathon Team — Spectre

---

## 🙏 Acknowledgments

- IBM Watsonx.ai — AI hazard analysis
- IBM Maximo — Work order management
- IBM Cloudant — Report storage
- IBM Carbon Design System — UI components and tokens
- IBM BoB Hackathon organizers

---

**Built with ❤️ for IBM BoB Hackathon**
