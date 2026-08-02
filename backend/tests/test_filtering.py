"""
Unit tests for promotional email, newsletter, and spam header filtering.
"""

import pytest
from gmail_service import GmailService


def test_filter_newsletter_list_unsubscribe_header():
    headers = {"List-Unsubscribe": "<https://example.com/unsubscribe>", "From": "news@company.com"}
    assert GmailService.is_promotional_or_newsletter(headers) is True


def test_filter_bulk_precedence_header():
    headers = {"Precedence": "bulk", "From": "support@service.com"}
    assert GmailService.is_promotional_or_newsletter(headers) is True


def test_filter_automated_sender():
    headers = {"From": "noreply@github.com"}
    assert GmailService.is_promotional_or_newsletter(headers, sender="no-reply@service.io") is True


def test_filter_marketing_subject():
    headers = {"From": "deals@store.com", "Subject": "Special 50% Off Discount Today!"}
    assert GmailService.is_promotional_or_newsletter(headers, subject="50% Off Special Offer") is True


def test_allow_legitimate_primary_email():
    headers = {
        "From": "john.doe@company.com",
        "Subject": "Urgent: Architecture Review Meeting Notes",
        "Date": "Sat, 01 Aug 2026 12:00:00 GMT",
    }
    assert (
        GmailService.is_promotional_or_newsletter(
            headers, sender="john.doe@company.com", subject="Urgent: Architecture Review"
        )
        is False
    )
