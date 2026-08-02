"""
Authentication module for Google Gmail API using OAuth 2.0 flow.
Handles token retrieval, refresh, and persistence.
"""

import os
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

import config


def get_gmail_credentials(
    credentials_path: Optional[Path] = None,
    token_path: Optional[Path] = None,
    scopes: Optional[list[str]] = None,
) -> Credentials:
    """
    Acquires and returns valid Google OAuth 2.0 Credentials.
    Attempts to load cached credentials from token_path. If expired, refreshes them.
    If unavailable, launches the OAuth desktop consent flow.

    Args:
        credentials_path (Optional[Path]): Path to credentials.json file.
        token_path (Optional[Path]): Path to cached token.json file.
        scopes (Optional[list[str]]): List of Gmail API OAuth scopes.

    Returns:
        Credentials: Authenticated Google OAuth credentials object.
    """
    creds_file = credentials_path or config.CREDENTIALS_FILE
    tok_file = token_path or config.TOKEN_FILE
    target_scopes = scopes or config.GMAIL_SCOPES

    creds = None

    # Load existing token if available
    if os.path.exists(tok_file):
        try:
            creds = Credentials.from_authorized_user_file(str(tok_file), target_scopes)
        except Exception as err:
            print(f"[Warning] Failed to load token file ({err}). Initiating new login flow.")
            creds = None

    # Refresh or create credentials if not valid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as refresh_err:
                print(f"[Warning] Token refresh failed ({refresh_err}). Re-authenticating...")
                creds = None

        if not creds:
            if not os.path.exists(creds_file):
                raise FileNotFoundError(
                    f"OAuth credentials file not found at '{creds_file}'. "
                    "Please download credentials.json from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), target_scopes)
            creds = flow.run_local_server(port=0)

        # Save credentials for future execution
        with open(tok_file, "w", encoding="utf-8") as token_out:
            token_out.write(creds.to_json())

    return creds


def get_gmail_service(creds: Optional[Credentials] = None) -> Resource:
    """
    Constructs and returns the Gmail API Resource client.

    Args:
        creds (Optional[Credentials]): Pre-authenticated credentials object.

    Returns:
        Resource: Gmail API service object.
    """
    if creds is None:
        creds = get_gmail_credentials()
    return build("gmail", "v1", credentials=creds)
