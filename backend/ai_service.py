"""
AI Integration Service Module using Google GenAI API (Gemini).
Handles prompt construction, email batch summarization, action item extraction,
and error handling for rate limits / token bounds.
"""

import logging
import time
from typing import Any, Dict, List, Optional

import config

logger = logging.getLogger(__name__)


class AIService:
    """Service wrapper for Google GenAI API (Gemini)."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize the AIService.

        Args:
            api_key (Optional[str]): Gemini API key.
            model_name (Optional[str]): Gemini model name (e.g. gemini-2.5-flash).
        """
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initializes the GenAI client SDK."""
        if not self.api_key:
            logger.warning("No Gemini API Key provided to AIService.")
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except ImportError:
            try:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                self.client = legacy_genai
            except Exception as err:
                logger.error(f"Failed to initialize legacy google.generativeai SDK: {err}")
        except Exception as err:
            logger.error(f"Failed to initialize google.genai Client: {err}")

    def build_prompt(self, emails: List[Dict[str, Any]]) -> str:
        """
        Constructs a structured system and user prompt for Gemini.

        Args:
            emails (List[Dict[str, Any]]): Processed email objects.

        Returns:
            str: Formatted prompt string.
        """
        prompt_lines = [
            "You are an executive AI Assistant generating a Daily Email Briefing.",
            "Analyze the following unread emails from the user's inbox.",
            "Generate a structured briefing adhering strictly to the required layout below:\n",
            "### EXECUTIVE SUMMARY",
            "Provide a concise 1 to 2 sentence overview of the inbox activity and critical priorities.\n",
            "### ACTION ITEMS",
            "List all concrete tasks or responses needed. Format as bullet points with priority indicators ([HIGH], [MEDIUM], [LOW]). If no action items exist, state 'None'.\n",
            "### EMAIL BREAKDOWNS",
            "For each email provided below, output:",
            "- **From**: [Sender]",
            "- **Subject**: [Subject]",
            "- **Priority**: [High/Medium/Low]",
            "- **Summary**: Exactly 2 sentences summarizing the core message and key context.",
            "- **Action Item**: Immediate action needed or 'None'.\n",
            "--- EMAIL DATA START ---"
        ]

        for idx, email_item in enumerate(emails, start=1):
            sender = email_item.get("sender", "Unknown")
            subject = email_item.get("subject", "No Subject")
            date = email_item.get("date", "")
            body = email_item.get("body", "")[:1500]  # Cap length per email for token limits

            prompt_lines.append(f"\n[Email #{idx}]")
            prompt_lines.append(f"From: {sender}")
            prompt_lines.append(f"Subject: {subject}")
            prompt_lines.append(f"Date: {date}")
            prompt_lines.append(f"Body Content:\n{body}")
            prompt_lines.append("-" * 30)

        prompt_lines.append("\n--- EMAIL DATA END ---")
        prompt_lines.append("\nPlease output the response now following the exact sections above.")
        return "\n".join(prompt_lines)

    def generate_briefing(self, emails: List[Dict[str, Any]], retries: int = 3) -> str:
        """
        Calls the Gemini API to generate the briefing summary.

        Args:
            emails (List[Dict[str, Any]]): List of cleaned email objects.
            retries (int): Retry attempts for rate limits (429).

        Returns:
            str: Raw markdown/text response from Gemini API.
        """
        if not emails:
            return (
                "### EXECUTIVE SUMMARY\n"
                "Your inbox is clear! No unread messages found within the selected lookback window.\n\n"
                "### ACTION ITEMS\n"
                "- [LOW] None\n\n"
                "### EMAIL BREAKDOWNS\n"
                "No unread emails to process."
            )

        if not self.client:
            logger.warning("AIService client is not initialized. Using fallback mock summary.")
            return self._generate_fallback_briefing(emails)

        prompt = self.build_prompt(emails)

        for attempt in range(1, retries + 1):
            try:
                # Check for google.genai Client format
                if hasattr(self.client, "models") and hasattr(self.client.models, "generate_content"):
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt
                    )
                    return response.text
                # Fallback for google.generativeai module
                elif hasattr(self.client, "GenerativeModel"):
                    model_obj = self.client.GenerativeModel(self.model_name)
                    res = model_obj.generate_content(prompt)
                    return res.text
                else:
                    raise RuntimeError("Unrecognized GenAI client interface.")

            except Exception as err:
                err_str = str(err)
                logger.warning(f"Gemini API call attempt {attempt}/{retries} failed: {err_str}")
                if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                    if attempt < retries:
                        sleep_time = attempt * 2
                        time.sleep(sleep_time)
                        continue
                if attempt == retries:
                    logger.error("Exhausted Gemini API retries. Falling back to local summary generator.")
                    return self._generate_fallback_briefing(emails, error_msg=err_str)

        return self._generate_fallback_briefing(emails)

    @staticmethod
    def _generate_fallback_briefing(emails: List[Dict[str, Any]], error_msg: Optional[str] = None) -> str:
        """
        Generates a structured fallback summary if AI API is unreachable or rate limited.
        """
        if error_msg:
            logger.info(f"Using smart local briefing generator due to API notice: {error_msg}")

        summary_lines = []
        summary_lines.append("### EXECUTIVE SUMMARY")
        summary_lines.append(f"Ingested and analyzed {len(emails)} unread primary email message(s). Below are your priority action items and key updates.\n")

        summary_lines.append("### ACTION ITEMS")
        for email_item in emails:
            subj = email_item.get("subject", "No Subject")
            sender = email_item.get("sender", "Unknown")
            summary_lines.append(f"- [MEDIUM] Review email: '{subj}' from {sender}")
        summary_lines.append("")

        summary_lines.append("### EMAIL BREAKDOWNS")
        for email_item in emails:
            sender = email_item.get("sender", "Unknown")
            subj = email_item.get("subject", "No Subject")
            snippet = email_item.get("snippet", email_item.get("body", "")[:120])
            summary_lines.append(f"- **From**: {sender}")
            summary_lines.append(f"- **Subject**: {subj}")
            summary_lines.append("- **Priority**: Medium")
            summary_lines.append(f"- **Summary**: This email was received from {sender}. Snippet preview: {snippet}")
            summary_lines.append(f"- **Action Item**: Review message '{subj}'.\n")

        return "\n".join(summary_lines)
