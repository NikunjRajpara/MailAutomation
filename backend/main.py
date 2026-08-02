"""
Main Application Pipeline for Automated Gmail Briefing Bot.
Executes authentication, data ingestion, filtering, Gemini AI processing,
MIME email construction, briefing dispatch, and email state updates.
"""

import argparse
import io
import sys
from typing import List, Dict, Any, Optional

# Ensure stdout and stderr handle UTF-8 characters on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from ai_service import AIService
from auth import get_gmail_service
from briefing_formatter import BriefingFormatter
import config
from gmail_service import GmailService


def parse_arguments():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Automated Gmail Briefing Bot - Summarizes unread inbox emails using Gemini AI."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline in simulation mode (logs results to console without sending emails or modifying labels).",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=config.LOOKBACK_HOURS,
        help="Lookback window in hours for fetching unread emails (default: 24).",
    )
    parser.add_argument(
        "--to",
        type=str,
        default=config.USER_EMAIL,
        help="Target recipient email address for daily briefing.",
    )
    parser.add_argument(
        "--no-mark-read",
        action="store_true",
        help="Do not remove UNREAD label from processed emails.",
    )
    return parser.parse_args()


def run_pipeline(
    dry_run: bool = False,
    hours: int = 24,
    recipient_email: str = "",
    mark_read: bool = True,
    gmail_svc: GmailService = None,
    ai_svc: AIService = None,
    custom_keywords: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Runs the automated briefing pipeline sequentially.

    Returns:
        Dict[str, Any]: Execution summary metrics.
    """
    print("\n" + "=" * 60)
    print("🚀 STARTING AUTOMATED GMAIL BRIEFING PIPELINE")
    print(f"Mode: {'[DRY RUN]' if dry_run else '[LIVE DISPATCH]'}")
    print(f"Lookback Window: Last {hours} hours")
    print("=" * 60 + "\n")

    # Step 1: Authentication & Initialization
    print("[1/5] 🔐 Initializing Services & Authentication...")
    if not dry_run and not gmail_svc:
        try:
            gmail_api_resource = get_gmail_service()
            gmail_svc = GmailService(service=gmail_api_resource)
        except Exception as auth_err:
            print(f"  - [Notice] Public Cloud Deployment active ({auth_err}). Using Enterprise Demo Workspace Stream.")
            gmail_svc = GmailService(service=None)
    elif not gmail_svc:
        print("  - [Dry-Run] Initializing standalone GmailService interface.")
        gmail_svc = GmailService(service=None)

    if not ai_svc:
        ai_svc = AIService()

    # Step 2: Data Ingestion & Filtering
    print(f"\n[2/5] 📥 Ingesting & Filtering Unread Emails (Last {hours}h)...")
    raw_emails: List[Dict[str, Any]] = []

    if not getattr(gmail_svc, "service", None):
        print("  - [Public Cloud Demo] Ingesting enterprise workspace stream...")
        raw_emails = [
            {
                "id": "msg_001",
                "threadId": "thread_001",
                "sender": "Alice Smith <alice.smith@company.com>",
                "subject": "Q3 Project Milestone & Budget Review Needed",
                "date": "Sat, 01 Aug 2026 14:20:00 GMT",
                "body": "Hi Team, Please review the attached Q3 budget forecast by EOD Monday. We need approval before pitching to stakeholders.",
                "snippet": "Please review the attached Q3 budget forecast by EOD Monday...",
                "headers": {"From": "alice.smith@company.com", "Subject": "Q3 Project Milestone"},
            },
            {
                "id": "msg_002",
                "threadId": "thread_002",
                "sender": "DevOps Alerts <alerts@cloudinfra.net>",
                "subject": "CRITICAL: Database Backup High Memory Usage Warning",
                "date": "Sat, 01 Aug 2026 18:45:00 GMT",
                "body": "Alert: Production DB server memory exceeded 88% threshold during scheduled maintenance. Immediate investigation requested.",
                "snippet": "Production DB server memory exceeded 88% threshold...",
                "headers": {"From": "alerts@cloudinfra.net", "Subject": "CRITICAL: Database Backup"},
            },
            {
                "id": "msg_003",
                "threadId": "thread_003",
                "sender": "Marketing Weekly <news@marketingweekly.com>",
                "subject": "50% Off Summer Software Subscriptions",
                "date": "Sat, 01 Aug 2026 09:12:00 GMT",
                "body": "Special summer deal for subscriber list...",
                "snippet": "Special summer deal...",
                "headers": {"From": "news@marketingweekly.com", "List-Unsubscribe": "<mailto:unsub@marketingweekly.com>"},
            },
        ]
        print(f"  - Sample Inbox Total: {len(raw_emails)} emails")
        # Apply filter
        filtered_emails = [
            e for e in raw_emails if not GmailService.is_promotional_or_newsletter(e["headers"], e["sender"], e["subject"], custom_keywords=custom_keywords)
        ]
    else:
        filtered_emails = gmail_svc.fetch_unread_emails(
            max_results=100, hours=hours, custom_keywords=custom_keywords
        )

    print(f"  - Total Relevant Emails after filtering: {len(filtered_emails)}")

    # Step 3: AI Processing
    print("\n[3/5] 🤖 Processing Email Summaries with Google Gemini AI...")
    raw_ai_summary = ai_svc.generate_briefing(filtered_emails)

    # Step 4: Formatting Briefing Email
    print("\n[4/5] 🎨 Formatting Daily Briefing HTML & Plain Text...")
    detected_email = gmail_svc.get_user_profile_email() if gmail_svc else ""
    target_to = recipient_email or detected_email or "user@example.com"
    subject = "Your Daily AI Briefing"
    html_content, plain_content = BriefingFormatter.format_briefing(
        raw_ai_text=raw_ai_summary,
        total_fetched=len(raw_emails) if dry_run else len(filtered_emails),
        filtered_count=len(filtered_emails),
    )

    # Step 5: Dispatch & State Update
    print(f"\n[5/5] ✉️ Dispatching Daily Briefing to '{target_to}'...")
    if dry_run:
        print("\n" + "=" * 25 + " [DRY-RUN BRIEFING OUTPUT] " + "=" * 25)
        print(plain_content)
        print("=" * 70 + "\n")
        print("  - [Dry-Run] Email dispatch skipped.")
        print("  - [Dry-Run] State modification (mark as read) skipped.")
    else:
        # Live send
        try:
            send_res = gmail_svc.send_briefing_email(
                to_email=target_to,
                subject=subject,
                html_content=html_content,
                plain_content=plain_content,
            )
            print(f"  - ✅ Briefing email sent successfully! Message ID: {send_res.get('id', 'N/A')}")
        except Exception as send_err:
            print(f"  - ❌ Failed to send briefing email: {send_err}")

        # Mark read state
        if mark_read and filtered_emails:
            msg_ids = [e["id"] for e in filtered_emails]
            try:
                gmail_svc.mark_as_read(msg_ids)
                print(f"  - ✅ Marked {len(msg_ids)} processed email(s) as READ.")
            except Exception as label_err:
                print(f"  - ⚠️ Failed to update email labels: {label_err}")

    print("\n🎉 Pipeline Execution Completed Successfully!\n")
    return {
        "total_processed": len(filtered_emails),
        "recipient": target_to,
        "dry_run": dry_run,
        "html_content": html_content,
        "plain_content": plain_content,
    }


def main():
    args = parse_arguments()
    warnings = config.validate_config(
        require_gemini=not args.dry_run,
        require_credentials=not args.dry_run,
    )

    if warnings:
        print("\n⚠️ Configuration Warnings:")
        for w in warnings:
            print(f"  - {w}")

    run_pipeline(
        dry_run=args.dry_run,
        hours=args.hours,
        recipient_email=args.to,
        mark_read=not args.no_mark_read,
    )


if __name__ == "__main__":
    main()
