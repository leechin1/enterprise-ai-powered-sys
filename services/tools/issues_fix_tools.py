"""
Issues Agent Fix Tools
Tools for proposing fixes, editing emails, and sending notifications.
"""

from langchain.tools import tool
from services.ai_issues_agent import AIIssuesAgent
from .issues_state import IssuesAgentState

# Import email service
try:
    from services.email_service import get_email_service
    EMAIL_SERVICE_AVAILABLE = True
except Exception:
    EMAIL_SERVICE_AVAILABLE = False


@tool
def propose_fix_for_issue(issue_number: int) -> str:
    """
    Generate a detailed fix proposal for a specific identified issue.
    Includes automated actions and email notifications to send.

    Args:
        issue_number: The issue number (1-based) from the identified issues list.
                     Use analyze_issues_from_results() first to see the list.

    Returns:
        Detailed fix proposal with actions, recipients, and email previews.
    """
    state = IssuesAgentState.get_instance()

    if not state.issues:
        return "❌ No issues identified. Run the full analysis first:\n1. generate_business_queries()\n2. execute_business_queries()\n3. analyze_issues_from_results()"

    idx = issue_number - 1
    if idx < 0 or idx >= len(state.issues):
        return f"❌ Invalid issue number. Choose between 1 and {len(state.issues)}."

    selected_issue = state.issues[idx]
    state.selected_issue_index = idx

    base_agent = AIIssuesAgent()
    result = base_agent.propose_fixes([selected_issue], state.query_results)

    if not result.get('success'):
        return f"❌ Fix proposal failed: {result.get('error', 'Unknown error')}"

    fixes = result.get('data', {}).get('fixes', [])
    state.proposed_fixes = fixes

    if not fixes:
        return "❌ Could not generate a fix for this issue."

    fix = fixes[0]

    response = f"## 🔧 Fix Proposal for Issue #{issue_number}\n\n"
    response += f"**Issue:** {selected_issue.get('title', 'Selected Issue')}\n\n"
    response += f"### {fix.get('fix_title', 'Proposed Fix')}\n"
    response += f"_{fix.get('fix_description', 'No description')}_\n\n"

    # Automated actions
    actions = fix.get('automated_actions', [])
    if actions:
        response += "### 📋 Automated Actions\n"
        for action in actions:
            response += f"- {action}\n"
        response += "\n"

    response += f"**Expected Outcome:** {fix.get('expected_outcome', 'Issue resolution')}\n"
    response += f"**Priority:** {fix.get('priority', 'scheduled').upper()}\n\n"

    # Recipients
    recipients = fix.get('recipients', [])
    if recipients:
        response += f"### 👥 Recipients ({len(recipients)})\n"
        for r in recipients:
            response += f"- **{r.get('name', 'Unknown')}** ({r.get('role', 'unknown')})\n"
            response += f"  Email: {r.get('email', 'N/A')} | Reason: {r.get('reason', 'N/A')}\n"
        response += "\n"

    # Email previews
    emails = fix.get('generated_emails', [])
    if emails:
        response += f"### 📧 Emails Ready to Send ({len(emails)})\n\n"

        for i, email in enumerate(emails, 1):
            recipient_list = ', '.join(email.get('recipient_emails', []))
            response += f"**Email {i}:** {email.get('subject', 'No Subject')}\n"
            response += f"To: {recipient_list}\n"
            response += f"```\n{email.get('body', 'No content')}\n```\n\n"

    response += "---\n"
    response += "**Next steps:**\n"
    response += "- Call `send_fix_emails()` to send the notification emails\n"
    response += "- Call `edit_email(email_number, field, new_value)` to modify an email first\n"
    response += "- Call `propose_fix_for_issue(N)` to see a different issue's fix"

    return response


@tool
def edit_email(email_number: int, field: str, new_value: str) -> str:
    """
    Edit a specific field of a generated email before sending.

    Args:
        email_number: Which email to edit (1-based index)
        field: Which field to edit - "subject" or "body"
        new_value: The new value for the field

    Returns:
        Confirmation of the edit with updated email preview.
    """
    state = IssuesAgentState.get_instance()

    if not state.proposed_fixes:
        return "❌ No fix proposed. Call `propose_fix_for_issue(issue_number)` first."

    fix = state.proposed_fixes[0]
    emails = fix.get('generated_emails', [])

    if not emails:
        return "❌ No emails in the current fix proposal."

    idx = email_number - 1
    if idx < 0 or idx >= len(emails):
        return f"❌ Invalid email number. Choose between 1 and {len(emails)}."

    field = field.lower().strip()
    if field not in ['subject', 'body']:
        return "❌ Invalid field. Use 'subject' or 'body'."

    # Apply edit
    old_value = emails[idx].get(field, '')
    emails[idx][field] = new_value

    response = f"✅ **Email {email_number} Updated**\n\n"
    response += f"**Field:** {field}\n"
    response += f"**Old value:** {old_value[:100]}{'...' if len(old_value) > 100 else ''}\n"
    response += f"**New value:** {new_value[:100]}{'...' if len(new_value) > 100 else ''}\n\n"
    response += f"**Updated Email Preview:**\n"
    response += f"Subject: {emails[idx].get('subject', 'No subject')}\n"
    response += f"To: {', '.join(emails[idx].get('recipient_emails', []))}\n"
    response += f"```\n{emails[idx].get('body', 'No content')[:300]}...\n```"

    return response


@tool
def send_fix_emails() -> str:
    """
    Send all the notification emails for the currently proposed fix.
    MUST call propose_fix_for_issue() first to generate the emails.

    In placebo mode, all emails are sent to the configured test email address.

    Returns:
        Confirmation of emails sent with details.
    """
    state = IssuesAgentState.get_instance()

    if not state.proposed_fixes:
        return "❌ No fix proposed. Call `propose_fix_for_issue(issue_number)` first."

    fix = state.proposed_fixes[0]
    emails = fix.get('generated_emails', [])
    recipients = fix.get('recipients', [])

    if not emails:
        return "ℹ️ No emails to send for this fix. The fix has been recorded."

    if not EMAIL_SERVICE_AVAILABLE:
        return "❌ Email service is not configured. Please set up EmailJS credentials in .env"

    try:
        email_service = get_email_service()
        result = email_service.send_fix_emails(emails, recipients)

        sent = result.get('sent', 0)
        failed = result.get('failed', 0)

        response = f"## 📬 Email Results\n\n"
        response += f"**Sent:** {sent} ✅\n"
        response += f"**Failed:** {failed} {'❌' if failed > 0 else ''}\n\n"

        if email_service.placebo_mode:
            response += f"🧪 **Placebo Mode Active**\n"
            response += f"All emails were sent to: `{email_service.placebo_email}`\n\n"
        else:
            response += f"📧 **All emails routed to:** `{email_service.default_external_email}`\n"
            response += f"Subject line includes intended recipient for tracking.\n\n"

        # Show what was sent
        response += "### Emails Sent:\n"
        for i, email in enumerate(emails, 1):
            response += f"{i}. **{email.get('subject', 'No subject')}**\n"
            response += f"   Intended for: {', '.join(email.get('recipient_emails', []))}\n"

        response += "\n✅ **Fix execution complete!**"

        return response

    except Exception as e:
        return f"❌ Error sending emails: {str(e)}"
