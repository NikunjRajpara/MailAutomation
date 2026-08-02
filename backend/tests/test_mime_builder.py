"""
Unit tests for MIME email construction and HTML/Plain text rendering.
"""

import base64
import email
import pytest
from briefing_formatter import BriefingFormatter
from gmail_service import GmailService


def test_create_mime_message_structure():
    to_email = "user@example.com"
    subject = "Your Daily AI Briefing"
    html_content = "<h1>Daily Briefing</h1>"
    plain_content = "Daily Briefing"

    mime_payload = GmailService.create_mime_message(to_email, subject, html_content, plain_content)
    assert "raw" in mime_payload

    # Decode raw base64 string back to MIME message object
    raw_bytes = base64.urlsafe_b64decode(mime_payload["raw"])
    parsed_msg = email.message_from_bytes(raw_bytes)

    assert parsed_msg["To"] == to_email
    assert parsed_msg["Subject"] == subject
    assert parsed_msg.is_multipart() is True


def test_briefing_formatter_renders_html_and_plain():
    raw_ai_text = (
        "### EXECUTIVE SUMMARY\nAll servers operational.\n\n"
        "### ACTION ITEMS\n- [HIGH] Deploy patch to production.\n\n"
        "### EMAIL BREAKDOWNS\n- **From**: sysadmin@cloud.com\n- **Subject**: Patch\n- **Summary**: Summary line. Second line."
    )

    html_out, plain_out = BriefingFormatter.format_briefing(raw_ai_text, total_fetched=5, filtered_count=1)

    assert "Your Daily AI Briefing" in html_out
    assert "Executive Summary" in html_out
    assert "Deploy patch to production." in html_out
    assert "HIGH" in html_out

    assert "YOUR DAILY AI BRIEFING" in plain_out
    assert "All servers operational." in plain_out
