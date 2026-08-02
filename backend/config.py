"""
Configuration module for Automated Gmail Briefing Bot.
Loads environment variables and defines default constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# OAuth Scopes required for Gmail API read, modify labels, and send email
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
]

# API Keys & Auth Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
USER_EMAIL = os.getenv('USER_EMAIL', '')
CREDENTIALS_FILE = Path(os.getenv('CREDENTIALS_FILE', BASE_DIR / 'credentials.json'))
TOKEN_FILE = Path(os.getenv('TOKEN_FILE', BASE_DIR / 'token.json'))

# Model & Operational Settings
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
LOOKBACK_HOURS = int(os.getenv('LOOKBACK_HOURS', '24'))
MARK_AS_READ = os.getenv('MARK_AS_READ', 'true').lower() in ('true', '1', 't', 'yes')


def validate_config(require_gemini: bool = True, require_credentials: bool = True) -> list[str]:
    """
    Validates essential environment configuration.
    
    Args:
        require_gemini (bool): Whether to require GEMINI_API_KEY.
        require_credentials (bool): Whether to check for OAuth credentials.json.

    Returns:
        list[str]: A list of warning or error messages.
    """
    warnings = []
    if require_gemini and not GEMINI_API_KEY:
        warnings.append("GEMINI_API_KEY environment variable is not set.")

    if require_credentials and not CREDENTIALS_FILE.exists() and not TOKEN_FILE.exists():
        warnings.append(
            f"Google Cloud credentials file not found at '{CREDENTIALS_FILE}'. "
            "Please follow setup guide to download credentials.json."
        )

    return warnings
