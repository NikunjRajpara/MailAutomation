"""
FastAPI REST API Backend Server for Automated Gmail Briefing Bot.
Exposes REST endpoints for the React Frontend Dashboard.
"""

import os
import sys
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from auth import get_gmail_credentials
from gmail_service import GmailService
from ai_service import AIService
from main import run_pipeline
from briefing_formatter import BriefingFormatter

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

app = FastAPI(
    title="Gmail Briefing Bot API",
    description="REST API server backing the React Dashboard.",
    version="1.0.0",
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount React static build if available
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/", response_class=HTMLResponse)
    def serve_frontend_index():
        return FileResponse(FRONTEND_DIST / "index.html")

# In-memory cache for latest briefing run
LATEST_BRIEFING_CACHE: Dict[str, Any] = {
    "html": "",
    "plain": "",
    "total_processed": 0,
    "recipient": "",
    "dry_run": False,
    "hours": 24,
    "timestamp": None,
}


class RunBriefingRequest(BaseModel):
    dry_run: bool = False
    hours: int = 24
    recipient_email: Optional[str] = None
    no_mark_read: bool = False
    custom_keywords: Optional[List[str]] = None


@app.get("/api/status")
def get_system_status() -> Dict[str, Any]:
    """Returns the current system health, credential state, and model details."""
    has_credentials = config.CREDENTIALS_FILE.exists()
    has_token = config.TOKEN_FILE.exists()
    has_gemini = bool(config.GEMINI_API_KEY)

    detected_email = ""
    if has_token and has_credentials:
        try:
            creds = get_gmail_credentials()
            svc = GmailService(service=build_service(creds))
            detected_email = svc.get_user_profile_email()
        except Exception:
            pass

    return {
        "status": "online",
        "has_credentials": has_credentials,
        "has_token": has_token,
        "has_gemini_key": has_gemini,
        "user_email": detected_email if detected_email else "Active Workspace Account",
        "model": config.GEMINI_MODEL,
        "lookback_hours": LATEST_BRIEFING_CACHE.get("hours", config.LOOKBACK_HOURS),
        "mark_as_read": config.MARK_AS_READ,
    }


def build_service(creds):
    from googleapiclient.discovery import build
    return build("gmail", "v1", credentials=creds)


@app.post("/api/run-briefing")
def trigger_briefing(req: RunBriefingRequest) -> Dict[str, Any]:
    """Triggers the briefing pipeline and updates cache."""
    try:
        recipient = req.recipient_email or config.USER_EMAIL or "user@example.com"
        result = run_pipeline(
            dry_run=req.dry_run,
            hours=req.hours,
            recipient_email=recipient,
            mark_read=not req.no_mark_read,
            custom_keywords=req.custom_keywords,
        )

        html_out = result.get("html_content", "")
        plain_out = result.get("plain_content", "")

        LATEST_BRIEFING_CACHE["html"] = html_out
        LATEST_BRIEFING_CACHE["plain"] = plain_out
        LATEST_BRIEFING_CACHE["total_processed"] = result.get("total_processed", 0)
        LATEST_BRIEFING_CACHE["recipient"] = result.get("recipient", recipient)
        LATEST_BRIEFING_CACHE["dry_run"] = req.dry_run
        LATEST_BRIEFING_CACHE["hours"] = req.hours

        return {
            "success": True,
            "metrics": result,
            "preview_html": html_out,
            "preview_plain": plain_out,
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@app.get("/api/preview")
def get_latest_preview() -> Dict[str, Any]:
    """Returns the cached briefing preview."""
    if not LATEST_BRIEFING_CACHE["html"]:
        sample_raw = (
            "### EXECUTIVE SUMMARY\nDashboard ready. Click 'Generate & Dispatch Daily Briefing' to ingest and summarize your unread Gmail messages.\n\n"
            "### ACTION ITEMS\n- [LOW] None\n\n"
            "### EMAIL BREAKDOWNS\nNo briefings dispatched yet."
        )
        html_out, plain_out = BriefingFormatter.format_briefing(sample_raw, total_fetched=0, filtered_count=0)
        LATEST_BRIEFING_CACHE["html"] = html_out
        LATEST_BRIEFING_CACHE["plain"] = plain_out

    return LATEST_BRIEFING_CACHE


@app.get("/api/run-tests")
def run_unit_tests() -> Dict[str, Any]:
    """Runs pytest test suite and returns parsed test output."""
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            capture_output=True,
            text=True,
            cwd=str(config.BASE_DIR),
        )
        return {
            "passed": res.returncode == 0,
            "exit_code": res.returncode,
            "output": res.stdout or res.stderr,
        }
    except Exception as err:
        return {"passed": False, "exit_code": 1, "output": str(err)}


@app.get("/api/keywords")
def get_filter_keywords() -> Dict[str, Any]:
    """Returns standard automated filter keywords."""
    return {
        "keywords": GmailService.AUTOMATED_SENDER_KEYWORDS,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
