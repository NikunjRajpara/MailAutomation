# MailAutomation: Automated Gmail Executive Briefing Bot

A full-stack enterprise automation system that connects to **Google Workspace (Gmail API)** and **Google Gemini AI**, ingests unread inbox messages, filters promotional marketing clutter, extracts priority action items (`[HIGH]`, `[MEDIUM]`, `[LOW]`), and dispatches a responsive HTML Daily Briefing email. Features a modern **React Web Dashboard** backed by a **FastAPI REST API**.

---

## 🏗️ Repository Architecture

```text
MailAutomation/
├── backend/                  # FastAPI REST API & Python Processing Core
│   ├── app.py                # FastAPI REST Endpoints & Embedded Server
│   ├── main.py               # Pipeline Controller & CLI Entry Point
│   ├── gmail_service.py      # Gmail API Ingestion, MIME Parsing & Filtering
│   ├── ai_service.py         # Google Gemini 2.0 AI Processing & Fallback Summaries
│   ├── auth.py               # Google OAuth 2.0 Authentication & Token Refresh
│   ├── briefing_formatter.py # Modern HTML & Plain Text Briefing Formatter
│   ├── config.py             # Environment Variable Configuration
│   ├── requirements.txt      # Python Dependencies
│   └── tests/                # Pytest Test Suite (15 Unit Tests)
│
├── frontend/                 # React Web Dashboard (Vite + React)
│   ├── src/                  # Glassmorphic UI Components & Styles
│   ├── package.json          # Node.js Dependencies
│   └── dist/                 # Production Build Static Bundle
│
├── README.md                 # Complete Installation & Setup Documentation
├── execution_report.md       # Architecture & Design Decisions Report
└── .gitignore                # Excludes secrets (credentials.json, token.json, .env)
```

---

## 🔑 Prerequisites & Initial Setup

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root or `backend/` directory:

```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# User configuration
USER_EMAIL=your.email@gmail.com

# OAuth Credentials & Token Paths
CREDENTIALS_FILE=credentials.json
TOKEN_FILE=token.json

# Model Settings
GEMINI_MODEL=gemini-2.0-flash
LOOKBACK_HOURS=24
MARK_AS_READ=true
```

---

## 🖥️ Running the Application

### Option A: Production Web Dashboard (Single Command)
Run the FastAPI backend server; it serves the pre-built React frontend directly:

```bash
cd backend
python app.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

---

### Option B: Full-Stack React Development Mode
For live React frontend development with hot-reloading:

1. **Start FastAPI Backend**:
   ```bash
   cd backend
   python app.py
   ```

2. **Start React Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
Open **[http://localhost:5173](http://localhost:5173)** in your browser!

---

## 🧪 Unit Testing

Run the full backend test suite:

```bash
cd backend
python -m pytest -v
```

---

## 🌐 Cloud Deployment Options

### 1. Render.com / Railway.app (Recommended Full-Stack Hosting)
1. Push your repository to GitHub (`NikunjRajpara/MailAutomation`).
2. Create a **New Web Service** on Render.com or Railway.app.
3. Connect your GitHub repository.
4. Set Build Command: `cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt`
5. Set Start Command: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables (`GEMINI_API_KEY`, etc.).

### 2. Google Cloud Run (Containerized Deployment)
Deploy as a Docker container to Google Cloud Run using the `gcloud` CLI for scalable serverless execution.

---

## 📄 License & PEP 8 Compliance

Adheres strictly to PEP 8 standards, complete inline docstrings, and clean multi-tenant OAuth user detection.
