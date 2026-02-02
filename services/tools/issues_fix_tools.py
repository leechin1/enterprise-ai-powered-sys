"""
Issues Agent Fix Tools
Tools for proposing fixes, editing emails, and sending notifications.
Uses templates from services/tools_templates/ for email generation.
"""

from pathlib import Path
from langchain.tools import tool
from services.ai_issues_agent import AIIssuesAgent
from .issues_state import IssuesAgentState

# Import email service
try:
    from services.email_service import get_email_service
    EMAIL_SERVICE_AVAILABLE = True
except Exception:
    EMAIL_SERVICE_AVAILABLE = False

# Path to templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "tools_templates"


def _load_template(template_name: str) -> str:
    """Load a template file from tools_templates directory."""
    try:
        filepath = TEMPLATES_DIR / template_name
        if filepath.exists():
            return filepath.read_text()
        return None
    except Exception:
        return None


# HARDCODED: All emails go to hi@mistyrecords.com - this is the ONLY valid recipient
# The EmailService will then route to placebo or production email based on mode
DEFAULT_EMAIL_RECIPIENT = "hi@mistyrecords.com"

# Email type configurations with template mappings
# ALL types use the same hardcoded recipient for safety
EMAIL_TYPE_CONFIG = {
    "management": {
        "template": "management_notification_template.txt",
        "default_recipient": DEFAULT_EMAIL_RECIPIENT,
        "subject_prefix": "[{severity}] Business Issue Alert: "
    },
    "supplier": {
        "template": "supplier_notification_template.txt",
        "default_recipient": DEFAULT_EMAIL_RECIPIENT,
        "subject_prefix": "[Action Required] Inventory Issue: "
    },
    "customer": {
        "template": "customer_notification_template.txt",
        "default_recipient": DEFAULT_EMAIL_RECIPIENT,
        "subject_prefix": "Update from Misty Jazz Records: "
    },
    "team": {
        "template": "team_notification_template.txt",
        "default_recipient": DEFAULT_EMAIL_RECIPIENT,
        "subject_prefix": "[Internal] {severity} Priority: "
    }
}


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
    response += "**Status:** Fix proposal ready. Emails can be sent upon approval."

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
        return "❌ No fix or email has been proposed yet. Please propose a fix or generate an email for an issue first."

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
def generate_email_for_issue(issue_number: int, email_type: str = "management") -> str:
    """
    Generate an email on-demand for a specific issue using templates from tools_templates/.
    Use this when no fix proposal exists or when you need a different type of email.

    Args:
        issue_number: The issue number (1-based) from the identified issues list.
        email_type: Type of email to generate:
                   - "management" - Notify management about the issue
                   - "supplier" - Contact supplier about inventory/stock issues
                   - "customer" - Notify customers about issues affecting them
                   - "team" - Alert internal team members

    Returns:
        Generated email preview ready to send with send_fix_emails().
    """
    state = IssuesAgentState.get_instance()

    if not state.issues:
        return "❌ No issues identified. Run the analysis first."

    idx = issue_number - 1
    if idx < 0 or idx >= len(state.issues):
        return f"❌ Invalid issue number. Choose between 1 and {len(state.issues)}."

    issue = state.issues[idx]
    severity = issue.get('severity', 'medium').upper()
    category = issue.get('category', 'operations')
    title = issue.get('title', 'Business Issue')
    description = issue.get('description', 'No description available')

    # Get email type configuration
    email_type_lower = email_type.lower()
    if email_type_lower not in EMAIL_TYPE_CONFIG:
        email_type_lower = "management"

    config = EMAIL_TYPE_CONFIG[email_type_lower]

    # Load template from file
    template_content = _load_template(config["template"])

    if template_content:
        # Format the template with issue data
        try:
            email_body = template_content.format(
                recipient_email=config["default_recipient"],
                severity=severity,
                title=title,
                category=category.title(),
                description=description
            )
            # Extract just the body (between the header lines)
            lines = email_body.split('\n')
            body_lines = []
            in_body = False
            for line in lines:
                if line.startswith('Dear') or line.startswith('Hi '):
                    in_body = True
                if in_body and not line.startswith('==='):
                    body_lines.append(line)
            email_body = '\n'.join(body_lines).strip()
        except KeyError as e:
            # Fallback if template has missing placeholders
            email_body = f"Issue: {title}\nSeverity: {severity}\nCategory: {category}\n\n{description}"
    else:
        # Fallback inline template if file not found
        email_body = f"""Dear Team,

This is an automated notification regarding a business issue.

**Issue:** {title}
**Severity:** {severity}
**Category:** {category.title()}

**Description:**
{description}

Please review and take appropriate action.

Best regards,
Misty Jazz Records Business Intelligence System"""

    # Build subject with severity if applicable
    subject_prefix = config["subject_prefix"].format(severity=severity)
    subject = f"{subject_prefix}{title}"

    # Create email object
    generated_email = {
        "subject": subject,
        "recipient_emails": [config["default_recipient"]],
        "body": email_body
    }

    # Store in state for sending
    if not state.proposed_fixes:
        state.proposed_fixes = [{"generated_emails": [generated_email], "recipients": []}]
    else:
        if not state.proposed_fixes[0].get('generated_emails'):
            state.proposed_fixes[0]['generated_emails'] = []
        state.proposed_fixes[0]['generated_emails'].append(generated_email)

    response = f"## 📧 Email Generated for Issue #{issue_number}\n\n"
    response += f"**Type:** {email_type.title()} Notification\n"
    response += f"**Subject:** {subject}\n"
    response += f"**To:** {config['default_recipient']}\n\n"
    response += f"**Preview:**\n```\n{email_body[:500]}{'...' if len(email_body) > 500 else ''}\n```\n\n"
    response += "✅ **Email ready to send!**"

    return response


@tool
def send_fix_emails() -> str:
    """
    Send all the notification emails for the currently proposed fix.
    Call propose_fix_for_issue() or generate_email_for_issue() first to create emails.

    In placebo mode, all emails are sent to the configured test email address.

    Returns:
        Confirmation of emails sent with details.
    """
    state = IssuesAgentState.get_instance()

    if not state.proposed_fixes:
        return "❌ No fix or email has been proposed yet. Please propose a fix or generate an email for an issue first."

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
