"""Weekly Content Email — sends Rahul platform-specific drafts to review and publish.

Runs every Sunday 8 PM IST via GitHub Actions.
Reads the publishing schedule, finds this week's content, assembles an email
with LinkedIn hook + newsletter draft + action items.
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCHEDULE_FILE = Path(__file__).parent / "publishing_schedule.json"
HOOKS_FILE = Path(__file__).parent / "content" / "linkedin_hooks" / "all_hooks.md"
SERIES_FILE = Path(__file__).parent / "content" / "enterprise_ai_transformation_series.md"

RECIPIENT = "rxj@google.com"
FROM_EMAIL = "Seven Conversations <content@rxjapps.in>"
REPLY_TO = "jindal.rahul@gmail.com"


def load_schedule():
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_this_weeks_content(schedule):
    """Find the content item for this week (next upcoming publish date)."""
    today = datetime.now().date()
    for item in schedule:
        pub_date = datetime.strptime(item["publish_date"], "%Y-%m-%d").date()
        # Find the item where publish_date is within 7 days from today
        if today <= pub_date <= today + timedelta(days=7):
            return item
    # If nothing upcoming this week, find the next future item
    for item in schedule:
        pub_date = datetime.strptime(item["publish_date"], "%Y-%m-%d").date()
        if pub_date >= today:
            return item
    return None


def extract_hook(hook_number):
    """Extract a specific hook from the all_hooks.md file."""
    if not HOOKS_FILE.exists():
        return None
    content = HOOKS_FILE.read_text(encoding="utf-8")
    # Split by ## Hook N:
    pattern = rf"## Hook {hook_number}:.*?\n\n(.*?)(?=\n---|\n## Hook|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_full_post(post_number):
    """Extract a specific post from the series file."""
    if not SERIES_FILE.exists():
        return None
    content = SERIES_FILE.read_text(encoding="utf-8")
    pattern = rf"## Post {post_number}:.*?\n(.*?)(?=\n## Post |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(0).strip().rstrip("-").strip()
    return None


def load_newsletter(filepath):
    """Load a newsletter draft if it exists."""
    if not filepath:
        return None
    path = Path(__file__).parent / filepath
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def build_email_html(item, hook_text, full_post, newsletter_text):
    """Build the HTML email with all content drafts."""
    pub_date = item["publish_date"]
    title = item["title"]
    week = item["week"]
    function = item["function"]
    status = item.get("status", "unknown")

    newsletter_section = ""
    if newsletter_text:
        # Convert markdown to basic HTML
        nl_html = newsletter_text.replace("\n\n", "</p><p>").replace("\n", "<br>")
        newsletter_section = f"""
        <div style="background:#1a1a2e; border-radius:8px; padding:20px; margin:16px 0; border-left:4px solid #10b981;">
            <h3 style="color:#10b981; margin:0 0 12px 0;">NEWSLETTER DRAFT (Substack)</h3>
            <p style="color:#94a3b8; font-size:13px; margin:0 0 8px 0;">Copy this into your Substack editor. Review, add personal anecdotes, then publish.</p>
            <div style="background:#0e1117; border-radius:6px; padding:16px; color:#e2e8f0; font-size:14px; line-height:1.7;">
                <p>{nl_html}</p>
            </div>
        </div>
        """
    else:
        newsletter_section = f"""
        <div style="background:#1a1a2e; border-radius:8px; padding:20px; margin:16px 0; border-left:4px solid #f59e0b;">
            <h3 style="color:#f59e0b; margin:0 0 8px 0;">NEWSLETTER DRAFT — NOT YET WRITTEN</h3>
            <p style="color:#94a3b8; font-size:14px;">Newsletter expansion for Week {week} hasn't been generated yet. Ask Claude Code to expand Post {item['post_number']} into newsletter format.</p>
        </div>
        """

    hook_section = ""
    if hook_text:
        hook_html = hook_text.replace("\n\n", "</p><p>").replace("\n", "<br>")
        hook_section = f"""
        <div style="background:#1a1a2e; border-radius:8px; padding:20px; margin:16px 0; border-left:4px solid #3b82f6;">
            <h3 style="color:#3b82f6; margin:0 0 12px 0;">LINKEDIN HOOK (Short Version)</h3>
            <p style="color:#94a3b8; font-size:13px; margin:0 0 8px 0;">Post this on LinkedIn. Put the newsletter link in the first comment.</p>
            <div style="background:#0e1117; border-radius:6px; padding:16px; color:#e2e8f0; font-size:14px; line-height:1.7;">
                <p>{hook_html}</p>
            </div>
        </div>
        """

    full_post_section = ""
    if full_post:
        fp_html = full_post.replace("\n\n", "</p><p>").replace("\n", "<br>")
        full_post_section = f"""
        <div style="background:#1a1a2e; border-radius:8px; padding:20px; margin:16px 0; border-left:4px solid #8b5cf6;">
            <h3 style="color:#8b5cf6; margin:0 0 12px 0;">FULL LINKEDIN POST (Standalone Version)</h3>
            <p style="color:#94a3b8; font-size:13px; margin:0 0 8px 0;">Alternative: use this as a standalone post if you haven't launched the newsletter yet.</p>
            <div style="background:#0e1117; border-radius:6px; padding:16px; color:#e2e8f0; font-size:14px; line-height:1.7;">
                <p>{fp_html}</p>
            </div>
        </div>
        """

    html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; max-width:700px; margin:0 auto; background:#0e1117; color:#e2e8f0; padding:24px; border-radius:12px;">

        <div style="text-align:center; margin-bottom:24px;">
            <h1 style="color:#06b6d4; margin:0; font-size:24px;">The Seven Conversations</h1>
            <p style="color:#64748b; font-size:14px; margin:4px 0 0 0;">Weekly Content Brief — Week {week} of 15</p>
        </div>

        <div style="background:#1a1a2e; border-radius:8px; padding:16px; margin-bottom:16px;">
            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="color:#94a3b8; font-size:13px; padding:4px 0;">Publish Date</td>
                    <td style="color:#e2e8f0; font-size:13px; font-weight:600; padding:4px 0; text-align:right;">{pub_date}</td>
                </tr>
                <tr>
                    <td style="color:#94a3b8; font-size:13px; padding:4px 0;">Topic</td>
                    <td style="color:#e2e8f0; font-size:13px; font-weight:600; padding:4px 0; text-align:right;">{title}</td>
                </tr>
                <tr>
                    <td style="color:#94a3b8; font-size:13px; padding:4px 0;">Function</td>
                    <td style="color:#06b6d4; font-size:13px; font-weight:600; padding:4px 0; text-align:right;">{function}</td>
                </tr>
                <tr>
                    <td style="color:#94a3b8; font-size:13px; padding:4px 0;">Status</td>
                    <td style="color:{'#10b981' if status == 'ready' else '#f59e0b'}; font-size:13px; font-weight:600; padding:4px 0; text-align:right;">{status.upper()}</td>
                </tr>
            </table>
        </div>

        <div style="background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.3); border-radius:8px; padding:16px; margin-bottom:16px;">
            <h3 style="color:#06b6d4; margin:0 0 8px 0; font-size:15px;">THIS WEEK'S ACTION ITEMS</h3>
            <ol style="color:#e2e8f0; font-size:14px; line-height:1.8; margin:0; padding-left:20px;">
                <li><strong>Review</strong> the drafts below. Add personal anecdotes, sharpen the hook.</li>
                <li><strong>Publish newsletter</strong> on Substack (Tuesday morning works best).</li>
                <li><strong>Post LinkedIn hook</strong> same day. Put newsletter link in first comment.</li>
                <li><strong>Reply to comments</strong> within 2 hours of posting for algorithm boost.</li>
            </ol>
        </div>

        {hook_section}
        {newsletter_section}
        {full_post_section}

        <div style="text-align:center; margin-top:24px; padding-top:16px; border-top:1px solid #1e293b;">
            <p style="color:#64748b; font-size:12px; margin:0;">
                Sent by The Seven Conversations Content OS<br>
                Week {week}/15 | {function} | {pub_date}
            </p>
        </div>
    </div>
    """
    return html


def send_email(subject, html_body):
    """Send email via Resend API."""
    import httpx

    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print("ERROR: RESEND_API_KEY not set")
        sys.exit(1)

    resp = httpx.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": FROM_EMAIL,
            "to": [RECIPIENT],
            "reply_to": REPLY_TO,
            "subject": subject,
            "html": html_body,
        },
        timeout=30,
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"Email sent successfully. ID: {data.get('id', 'unknown')}")
        return True
    else:
        print(f"Email failed: {resp.status_code} — {resp.text}")
        return False


def main():
    test_mode = "--test" in sys.argv

    schedule = load_schedule()
    item = get_this_weeks_content(schedule)

    if not item:
        print("No upcoming content found in schedule.")
        return

    print(f"Week {item['week']}: {item['title']}")
    print(f"Publish date: {item['publish_date']}")
    print(f"Status: {item.get('status', 'unknown')}")

    hook_text = extract_hook(item["linkedin_hook_number"])
    full_post = extract_full_post(item["post_number"])
    newsletter_text = load_newsletter(item.get("newsletter_file"))

    html = build_email_html(item, hook_text, full_post, newsletter_text)

    subject = f"[7C Week {item['week']}] {item['title']} — drafts ready for review"

    if test_mode:
        # Write HTML to file for preview
        out = Path(__file__).parent / "test_email_preview.html"
        out.write_text(html, encoding="utf-8")
        print(f"Test mode: email HTML written to {out}")
        print(f"Subject: {subject}")
        print(f"To: {RECIPIENT}")
        return

    send_email(subject, html)


if __name__ == "__main__":
    main()
