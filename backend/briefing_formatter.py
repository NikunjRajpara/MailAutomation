"""
Briefing Formatter Module.
Converts raw markdown/text summaries into responsive, modern HTML emails and plain text fallbacks.
"""

import datetime
import html
import re
from typing import Dict, List, Tuple


class BriefingFormatter:
    """Formats raw AI outputs and email statistics into HTML and Plain Text email payloads."""

    @staticmethod
    def _parse_sections(raw_ai_text: str) -> Dict[str, str]:
        """
        Parses raw markdown text from Gemini into distinct sections.
        Returns dictionary with keys: executive_summary, action_items, breakdowns.
        """
        sections = {
            "executive_summary": "No summary generated.",
            "action_items": "No action items extracted.",
            "breakdowns": "No email breakdowns available."
        }

        # Extract Executive Summary
        exec_match = re.search(
            r"###\s*EXECUTIVE\s*SUMMARY\s*\n(.*?)(?=\n###|\Z)", raw_ai_text, re.DOTALL | re.IGNORECASE
        )
        if exec_match:
            sections["executive_summary"] = exec_match.group(1).strip()

        # Extract Action Items
        action_match = re.search(
            r"###\s*ACTION\s*ITEMS\s*\n(.*?)(?=\n###|\Z)", raw_ai_text, re.DOTALL | re.IGNORECASE
        )
        if action_match:
            sections["action_items"] = action_match.group(1).strip()

        # Extract Email Breakdowns
        breakdown_match = re.search(
            r"###\s*EMAIL\s*BREAKDOWNS\s*\n(.*?)(?=\Z)", raw_ai_text, re.DOTALL | re.IGNORECASE
        )
        if breakdown_match:
            sections["breakdowns"] = breakdown_match.group(1).strip()
        elif not exec_match and not action_match:
            # Fallback if markdown headers were omitted
            sections["executive_summary"] = raw_ai_text.strip()

        return sections

    @staticmethod
    def _render_action_items_html(action_items_text: str) -> str:
        """Converts plain text bulleted action items into styled HTML list items."""
        lines = [line.strip() for line in action_items_text.splitlines() if line.strip()]
        if not lines or action_items_text.lower() == "none":
            return "<p style='color: #64748B; font-style: italic; margin: 0;'>No urgent action items for today.</p>"

        html_items = []
        for line in lines:
            # Clean leading dashes or bullets
            clean_line = re.sub(r"^[\-\*\u2022]\s*", "", line)
            
            # Badge rendering for priorities
            badge_html = ""
            if "[HIGH]" in clean_line.upper():
                badge_html = "<span style='background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; margin-right: 6px;'>HIGH</span>"
                clean_line = re.sub(r"\[HIGH\]", "", clean_line, flags=re.IGNORECASE)
            elif "[MEDIUM]" in clean_line.upper():
                badge_html = "<span style='background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; margin-right: 6px;'>MEDIUM</span>"
                clean_line = re.sub(r"\[MEDIUM\]", "", clean_line, flags=re.IGNORECASE)
            elif "[LOW]" in clean_line.upper():
                badge_html = "<span style='background-color: #E0E7FF; color: #4338CA; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; margin-right: 6px;'>LOW</span>"
                clean_line = re.sub(r"\[LOW\]", "", clean_line, flags=re.IGNORECASE)

            escaped_text = html.escape(clean_line.strip())
            html_items.append(
                f"<li style='margin-bottom: 8px; line-height: 1.5;'>{badge_html}{escaped_text}</li>"
            )

        return f"<ul style='margin: 0; padding-left: 20px; color: #1E293B; font-size: 14px;'>{''.join(html_items)}</ul>"

    @staticmethod
    def _render_breakdowns_html(breakdowns_text: str) -> str:
        """Converts raw email breakdown section into styled card elements."""
        if not breakdowns_text or breakdowns_text.lower() == "no emails to process.":
            return "<p style='color: #64748B; font-style: italic;'>No individual email breakdowns.</p>"

        # Render markdown bold formatting (**text**) to HTML <strong>
        formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", breakdowns_text)
        
        # Split by email blocks (e.g. lines starting with '- **From**' or '[Email #')
        lines = formatted_text.splitlines()
        cards_html = []
        current_card_lines = []

        def flush_card(lines_list):
            if not lines_list:
                return
            card_content = "<br>".join(lines_list)
            cards_html.append(
                f"<div style='background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #4F46E5; border-radius: 8px; padding: 14px 16px; margin-bottom: 14px; font-size: 13px; color: #334155; line-height: 1.6;'>"
                f"{card_content}</div>"
            )

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("- <strong>From</strong>") or line_str.startswith("---"):
                if current_card_lines and line_str.startswith("- <strong>From</strong>"):
                    flush_card(current_card_lines)
                    current_card_lines = []
            if not line_str.startswith("---"):
                clean_l = line_str.lstrip("- ").strip()
                current_card_lines.append(clean_l)

        flush_card(current_card_lines)
        return "".join(cards_html) if cards_html else f"<div style='font-size: 13px; color: #334155;'>{html.escape(breakdowns_text)}</div>"

    @classmethod
    def format_briefing(
        cls, raw_ai_text: str, total_fetched: int = 0, filtered_count: int = 0
    ) -> Tuple[str, str]:
        """
        Formats the raw AI output into both HTML and Plain Text representations.

        Args:
            raw_ai_text (str): Output text from Gemini API.
            total_fetched (int): Total unread emails retrieved.
            filtered_count (int): Total relevant emails processed after filtering.

        Returns:
            Tuple[str, str]: (html_content, plain_text_content)
        """
        today_date = datetime.date.today().strftime("%A, %B %d, %Y")
        sections = cls._parse_sections(raw_ai_text)

        exec_summary_html = html.escape(sections["executive_summary"]).replace("\n", "<br>")
        action_items_html = cls._render_action_items_html(sections["action_items"])
        breakdowns_html = cls._render_breakdowns_html(sections["breakdowns"])

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Daily AI Briefing</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #F1F5F9; margin: 0; padding: 20px 10px;">
    <div style="max-width: 640px; margin: 0 auto; background-color: #FFFFFF; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
        
        <!-- Header Banner -->
        <div style="background: linear-gradient(135deg, #1E293B 0%, #312E81 100%); padding: 28px 24px; color: #FFFFFF;">
            <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; tracking: 1px; color: #818CF8; margin-bottom: 4px;">AUTOMATED GMAIL BRIEFING</div>
            <h1 style="margin: 0; font-size: 24px; font-weight: 700; color: #FFFFFF;">Your Daily AI Briefing</h1>
            <div style="font-size: 13px; color: #94A3B8; margin-top: 6px;">{today_date}</div>
            
            <div style="display: inline-block; margin-top: 16px; background-color: rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 6px 14px; font-size: 12px; color: #E2E8F0;">
                📊 <strong>{filtered_count}</strong> Key Emails Analyzed (from {total_fetched} unread)
            </div>
        </div>

        <!-- Body Content -->
        <div style="padding: 24px;">
            
            <!-- Executive Summary Card -->
            <div style="margin-bottom: 24px; background-color: #EFF6FF; border-left: 4px solid #2563EB; border-radius: 6px; padding: 16px;">
                <h2 style="margin: 0 0 8px 0; font-size: 15px; font-weight: 700; color: #1E40AF; text-transform: uppercase; letter-spacing: 0.5px;">Executive Summary</h2>
                <div style="font-size: 14px; color: #1E3A8A; line-height: 1.6;">{exec_summary_html}</div>
            </div>

            <!-- Action Items Card -->
            <div style="margin-bottom: 28px;">
                <h2 style="margin: 0 0 12px 0; font-size: 16px; font-weight: 700; color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 6px;">⚡ Priority Action Items</h2>
                {action_items_html}
            </div>

            <!-- Email Breakdowns -->
            <div style="margin-bottom: 20px;">
                <h2 style="margin: 0 0 14px 0; font-size: 16px; font-weight: 700; color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 6px;">📥 Key Email Summaries</h2>
                {breakdowns_html}
            </div>

        </div>

        <!-- Footer -->
        <div style="background-color: #F8FAFC; border-top: 1px solid #E2E8F0; padding: 16px 24px; text-align: center; font-size: 12px; color: #64748B;">
            <strong>Automated Gmail Executive Briefing</strong> • Enterprise Workspace Intelligence
        </div>

    </div>
</body>
</html>
"""

        plain_text = f"""==================================================
YOUR DAILY AI BRIEFING - {today_date}
==================================================
Emails Processed: {filtered_count} relevant emails (from {total_fetched} unread)

EXECUTIVE SUMMARY
--------------------------------------------------
{sections['executive_summary']}

PRIORITY ACTION ITEMS
--------------------------------------------------
{sections['action_items']}

KEY EMAIL SUMMARIES
--------------------------------------------------
{sections['breakdowns']}

==================================================
Automated Gmail Briefing Bot • Powered by Gemini AI
"""

        return html_content, plain_text
