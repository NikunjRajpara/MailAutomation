"""
Unit tests for email text sanitization and HTML stripping logic.
"""

import pytest
from gmail_service import GmailService


def test_sanitize_plain_text():
    raw_text = "   Hello World!  \n\n  This is a clean test message.  "
    sanitized = GmailService.sanitize_email_body(raw_text)
    assert "Hello World!" in sanitized
    assert "This is a clean test message." in sanitized
    assert not sanitized.startswith(" ")


def test_sanitize_html_tags():
    raw_html = """
    <html>
        <head><title>Test Email</title></head>
        <body>
            <h1>Project Update</h1>
            <p>Here is the <strong>quarterly report</strong> data.</p>
            <script>alert('malicious code');</script>
            <style>body { background: red; }</style>
        </body>
    </html>
    """
    sanitized = GmailService.sanitize_email_body(raw_html)
    assert "Project Update" in sanitized
    assert "quarterly report" in sanitized
    assert "alert('malicious code')" not in sanitized
    assert "background: red" not in sanitized


def test_sanitize_empty_and_none():
    assert GmailService.sanitize_email_body("") == ""
    assert GmailService.sanitize_email_body(None) == ""


def test_sanitize_excessive_newlines():
    raw_text = "Line 1\n\n\n\n\nLine 2"
    sanitized = GmailService.sanitize_email_body(raw_text)
    assert "\n\n\n" not in sanitized
    assert "Line 1" in sanitized and "Line 2" in sanitized
