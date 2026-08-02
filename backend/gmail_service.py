"""
Gmail API Service Module.
Provides high-level interfaces for querying, parsing, filtering, sanitizing,
sending emails, and managing label state via the Gmail API.
"""

import base64
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup
from googleapiclient.discovery import Resource


class GmailService:
    """Class handling all Gmail API interactions and email data transformations."""

    # Keywords commonly associated with automated marketing or newsletter senders
    AUTOMATED_SENDER_KEYWORDS = [
        "noreply", "no-reply", "newsletter", "marketing", "promotions",
        "notifications", "updates", "digest", "info@", "news@", "bounce", "alert"
    ]

    def __init__(self, service: Optional[Resource] = None):
        """
        Initialize GmailService.

        Args:
            service (Optional[Resource]): Authenticated Gmail API resource object.
        """
        self.service = service

    def get_user_profile_email(self) -> str:
        """Retrieves the email address of the authenticated Gmail user profile."""
        if not self.service:
            return ""
        try:
            profile = self.service.users().getProfile(userId="me").execute()
            return profile.get("emailAddress", "")
        except Exception:
            return ""

    @staticmethod
    def sanitize_email_body(raw_html_or_text: str) -> str:
        """
        Strips HTML tags, scripts, inline styles, and redundant whitespace from raw text/html.

        Args:
            raw_html_or_text (str): Raw string content of email payload.

        Returns:
            str: Cleaned plain text representation.
        """
        if not raw_html_or_text:
            return ""

        # Use BeautifulSoup to parse HTML if tags are present
        if "<html" in raw_html_or_text.lower() or "<div" in raw_html_or_text.lower() or "<p" in raw_html_or_text.lower():
            soup = BeautifulSoup(raw_html_or_text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "head", "title", "meta"]):
                element.decompose()

            # Extract plain text with space separators
            text = soup.get_text(separator=" ")
        else:
            text = raw_html_or_text

        # Normalize line breaks and multiple spaces
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)

        # Remove excessive blank lines
        clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)
        return clean_text.strip()

    @classmethod
    def is_promotional_or_newsletter(
        cls,
        headers: Dict[str, str],
        sender: str = "",
        subject: str = "",
        custom_keywords: Optional[List[str]] = None,
    ) -> bool:
        """
        Determines whether an email is a promotional email, newsletter, or automated bulk mail.
        If custom_keywords is explicitly provided, uses custom_keywords rules.
        """
        headers_lower = {k.lower(): v for k, v in headers.items()}
        sender_lower = (sender or headers_lower.get("from", "")).lower()
        subject_lower = (subject or headers_lower.get("subject", "")).lower()

        # If user explicitly passed custom filter keywords (e.g. from Web UI)
        if custom_keywords is not None:
            if not custom_keywords:
                # User removed ALL filter tags -> Do not filter out any email!
                return False

            # Filter based on user's active keyword tags
            for kw in custom_keywords:
                kw_lower = kw.lower().strip()
                if kw_lower and (kw_lower in sender_lower or kw_lower in subject_lower):
                    return True
            return False

        # Default header and keyword checks
        if "list-unsubscribe" in headers_lower or "list-id" in headers_lower:
            return True

        precedence = headers_lower.get("precedence", "").lower()
        if precedence in ("bulk", "list", "junk"):
            return True

        auto_submitted = headers_lower.get("auto-submitted", "").lower()
        if auto_submitted and auto_submitted != "no":
            return True

        # Sender email check against default keywords
        for kw in cls.AUTOMATED_SENDER_KEYWORDS:
            if kw in sender_lower:
                return True

        # Subject keywords check for common marketing blasts
        marketing_subject_keywords = ["off %", "discount", "unsubscribe", "special offer", "deal of the day"]
        for kw in marketing_subject_keywords:
            if kw in subject_lower:
                return True

        return False

    def _extract_payload_body(self, payload: Dict[str, Any]) -> str:
        """
        Recursively parses MIME payload parts to extract body text.
        Prefers plain text, falls back to HTML.
        """
        body_text = ""
        body_html = ""

        def parse_part(part: Dict[str, Any]):
            nonlocal body_text, body_html
            mime_type = part.get("mimeType", "")
            body = part.get("body", {})
            data = body.get("data", "")

            if data:
                try:
                    decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                    if mime_type == "text/plain" and not body_text:
                        body_text = decoded
                    elif mime_type == "text/html" and not body_html:
                        body_html = decoded
                except Exception:
                    pass

            parts = part.get("parts", [])
            for p in parts:
                parse_part(p)

        parse_part(payload)
        raw_body = body_text if body_text else body_html
        return self.sanitize_email_body(raw_body)

    def fetch_unread_emails(
        self, max_results: int = 100, hours: int = 24, custom_keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries the Gmail API for unread emails within the specifies hours window.

        Args:
            max_results (int): Maximum emails to retrieve (default: 100).
            hours (int): Lookback window in hours.
            custom_keywords (Optional[List[str]]): Active filter keywords.

        Returns:
            List[Dict[str, Any]]: List of email data dictionaries.
        """
        if not self.service:
            raise RuntimeError("Gmail API service is not initialized.")

        if hours >= 24 and hours % 24 == 0:
            query = f"is:unread newer_than:{hours // 24}d"
        else:
            query = f"is:unread newer_than:{hours}h"

        response = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )

        messages = response.get("messages", [])
        unread_emails = []

        for msg_stub in messages:
            msg_id = msg_stub["id"]
            full_msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )

            payload = full_msg.get("payload", {})
            raw_headers = payload.get("headers", [])
            headers_dict = {h["name"]: h["value"] for h in raw_headers if "name" in h and "value" in h}

            sender = headers_dict.get("From", "Unknown Sender")
            subject = headers_dict.get("Subject", "No Subject")
            date_str = headers_dict.get("Date", "")

            # Filter out promotional / newsletter emails using custom_keywords if provided
            if self.is_promotional_or_newsletter(
                headers_dict, sender=sender, subject=subject, custom_keywords=custom_keywords
            ):
                continue

            cleaned_body = self._extract_payload_body(payload)
            if not cleaned_body:
                cleaned_body = self.sanitize_email_body(full_msg.get("snippet", ""))

            unread_emails.append(
                {
                    "id": msg_id,
                    "threadId": full_msg.get("threadId", ""),
                    "sender": sender,
                    "subject": subject,
                    "date": date_str,
                    "body": cleaned_body,
                    "headers": headers_dict,
                    "snippet": full_msg.get("snippet", ""),
                }
            )

        return unread_emails

    @staticmethod
    def create_mime_message(
        to_email: str, subject: str, html_content: str, plain_content: str
    ) -> Dict[str, str]:
        """
        Constructs a MIME multipart email message (HTML and Plain text) encoded in base64url.

        Args:
            to_email (str): Target recipient email address.
            subject (str): Email subject.
            html_content (str): Rendered HTML email body.
            plain_content (str): Fallback plain text body.

        Returns:
            Dict[str, str]: Dictionary formatted for Gmail API send call (`{'raw': '...'}`).
        """
        mime_msg = MIMEMultipart("alternative")
        mime_msg["To"] = to_email
        mime_msg["Subject"] = subject

        # Attach plain text and HTML parts
        part1 = MIMEText(plain_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        mime_msg.attach(part1)
        mime_msg.attach(part2)

        raw_bytes = mime_msg.as_bytes()
        encoded_raw = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
        return {"raw": encoded_raw}

    def send_briefing_email(
        self, to_email: str, subject: str, html_content: str, plain_content: str
    ) -> Dict[str, Any]:
        """
        Sends the briefing email using Gmail API `messages.send`.

        Args:
            to_email (str): Target recipient email address.
            subject (str): Email subject.
            html_content (str): Rendered HTML content.
            plain_content (str): Plain text content.

        Returns:
            Dict[str, Any]: Gmail API response payload.
        """
        if not self.service:
            raise RuntimeError("Gmail API service is not initialized.")

        message_body = self.create_mime_message(to_email, subject, html_content, plain_content)
        result = (
            self.service.users()
            .messages()
            .send(userId="me", body=message_body)
            .execute()
        )
        return result

    def mark_as_read(self, message_ids: List[str]) -> bool:
        """
        Removes the 'UNREAD' label from processed email messages.

        Args:
            message_ids (List[str]): List of Gmail message IDs to modify.

        Returns:
            bool: True if successful.
        """
        if not message_ids:
            return True

        if not self.service:
            raise RuntimeError("Gmail API service is not initialized.")

        body = {
            "ids": message_ids,
            "removeLabelIds": ["UNREAD"],
        }
        self.service.users().messages().batchModify(userId="me", body=body).execute()
        return True
