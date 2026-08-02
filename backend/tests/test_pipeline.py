"""
Unit and integration tests for full dry-run briefing pipeline execution.
"""

from unittest.mock import MagicMock, patch
import pytest
from ai_service import AIService
from gmail_service import GmailService
from main import run_pipeline


def test_dry_run_pipeline_execution():
    with patch("ai_service.AIService.generate_briefing") as mock_generate:
        mock_generate.return_value = (
            "### EXECUTIVE SUMMARY\nDry run successful.\n\n"
            "### ACTION ITEMS\n- [LOW] None\n\n"
            "### EMAIL BREAKDOWNS\nNo emails."
        )

        mock_gmail = MagicMock(spec=GmailService)
        mock_ai = AIService(api_key="mock_key")

        res = run_pipeline(
            dry_run=True,
            hours=24,
            recipient_email="testuser@example.com",
            gmail_svc=mock_gmail,
            ai_svc=mock_ai,
        )

        assert res["total_processed"] == 1  # filtered sample email
        assert res["recipient"] == "testuser@example.com"
        assert res["dry_run"] is True
