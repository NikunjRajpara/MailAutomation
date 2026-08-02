"""
Unit tests for AI Service prompt construction and Gemini API mocking.
"""

from unittest.mock import MagicMock, patch
import pytest
from ai_service import AIService


def test_build_prompt_formatting():
    ai_svc = AIService(api_key="mock_key")
    emails = [
        {
            "sender": "boss@company.com",
            "subject": "Important Roadmap Sync",
            "date": "Sat, 01 Aug 2026 10:00:00 GMT",
            "body": "Please review the Q4 roadmap presentation before our meeting tomorrow.",
        }
    ]

    prompt = ai_svc.build_prompt(emails)
    assert "EXECUTIVE SUMMARY" in prompt
    assert "ACTION ITEMS" in prompt
    assert "EMAIL BREAKDOWNS" in prompt
    assert "boss@company.com" in prompt
    assert "Important Roadmap Sync" in prompt


def test_generate_briefing_empty_emails():
    ai_svc = AIService(api_key="mock_key")
    result = ai_svc.generate_briefing([])
    assert "EXECUTIVE SUMMARY" in result
    assert "Your inbox is clear!" in result


@patch("ai_service.AIService._init_client")
def test_generate_briefing_with_mocked_gemini_client(mock_init):
    ai_svc = AIService(api_key="mock_key")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = (
        "### EXECUTIVE SUMMARY\nSummary of inbox.\n\n"
        "### ACTION ITEMS\n- [HIGH] Task 1\n\n"
        "### EMAIL BREAKDOWNS\n- **From**: boss@company.com"
    )
    mock_client.models.generate_content.return_value = mock_response
    ai_svc.client = mock_client

    emails = [{"sender": "boss@company.com", "subject": "Task", "body": "Body"}]
    output = ai_svc.generate_briefing(emails)

    assert "Summary of inbox." in output
    assert "Task 1" in output
