"""
Issues Agent Analysis Tools
Tools for analyzing query results and getting issue details.
"""

from langchain.tools import tool
from services.ai_issues_agent import AIIssuesAgent
from .issues_state import IssuesAgentState


@tool
def analyze_issues_from_results() -> str:
    """
    Analyze the query results to identify business issues.
    MUST call execute_business_queries() first.

    Returns:
        Detailed list of identified issues with severity, category, and descriptions.
    """
    state = IssuesAgentState.get_instance()

    if not state.query_results:
        return "❌ No query results to analyze. Call `execute_business_queries()` first."

    base_agent = AIIssuesAgent()
    result = base_agent.identify_business_issues(state.query_results)

    if not result.get('success'):
        return f"❌ Issue analysis failed: {result.get('error', 'Unknown error')}"

    issues = result.get('data', {}).get('issues', [])
    state.issues = issues

    if not issues:
        return "✅ **No significant issues found!** The business metrics look healthy."

    severity_icons = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
    category_icons = {
        'inventory': '📦', 'payments': '💳', 'customers': '👥',
        'revenue': '💰', 'operations': '⚙️', 'data_quality': '📊', 'financial': '💵'
    }

    response = f"⚠️ **Identified {len(issues)} Business Issues**\n\n"

    for i, issue in enumerate(issues, 1):
        sev = issue.get('severity', 'medium')
        cat = issue.get('category', 'operations')
        sev_icon = severity_icons.get(sev, '⚪')
        cat_icon = category_icons.get(cat, '📋')

        response += f"### {i}. {cat_icon} {issue.get('title', 'Issue')}\n"
        response += f"**Severity:** {sev_icon} {sev.upper()} | **Category:** {cat}\n\n"
        response += f"{issue.get('description', 'No description')}\n\n"
        response += "---\n\n"

    response += "**Next step:** Call `propose_fix_for_issue(issue_number)` to get a fix proposal.\n"
    response += "Example: `propose_fix_for_issue(1)` for the first issue."

    return response


def _format_issue_details(issue: dict, issue_number: int) -> str:
    """Helper to format issue details consistently."""
    severity_icons = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
    sev = issue.get('severity', 'medium')

    response = f"## Issue #{issue_number} Details\n\n"
    response += f"### {issue.get('title', 'Issue')}\n\n"
    response += f"**Severity:** {severity_icons.get(sev, '⚪')} {sev.upper()}\n"
    response += f"**Category:** {issue.get('category', 'unknown')}\n\n"
    response += f"**Description:**\n{issue.get('description', 'No description')}\n\n"

    # Show affected data if available
    if issue.get('affected_records'):
        response += f"**Affected Records:** {issue.get('affected_records')}\n"
    if issue.get('impact'):
        response += f"**Business Impact:** {issue.get('impact')}\n"

    response += f"\n**To fix this issue:** Call `propose_fix_for_issue({issue_number})`"
    return response


def _get_issue_by_number(issue_number: int) -> str:
    """Internal function to get issue by number."""
    state = IssuesAgentState.get_instance()

    if not state.issues:
        return "❌ No issues identified yet. Run the analysis first."

    idx = issue_number - 1
    if idx < 0 or idx >= len(state.issues):
        return f"❌ Invalid issue number. Choose between 1 and {len(state.issues)}."

    return _format_issue_details(state.issues[idx], issue_number)


@tool
def get_issue_details(issue_number: int) -> str:
    """
    Get detailed information about a specific identified issue by its number.

    Args:
        issue_number: The issue number (1-based) to get details for.

    Returns:
        Full details of the specified issue.
    """
    return _get_issue_by_number(issue_number)


@tool
def get_issue_detail(issue_number: int) -> str:
    """
    Get detailed information about a specific identified issue by its number.
    This is an alias for get_issue_details.

    Args:
        issue_number: The issue number (1-based) to get details for.

    Returns:
        Full details of the specified issue.
    """
    return _get_issue_by_number(issue_number)


@tool
def find_issue_by_keyword(keyword: str) -> str:
    """
    Search for an issue by keyword in the title or description.
    Use this when you know part of the issue name but not the number.

    Args:
        keyword: A word or phrase to search for in issue titles/descriptions.

    Returns:
        Details of matching issues, or a list of all issues if no match found.
    """
    state = IssuesAgentState.get_instance()

    if not state.issues:
        return "❌ No issues identified yet. Run the analysis first."

    keyword_lower = keyword.lower()
    matches = []

    for i, issue in enumerate(state.issues, 1):
        title = issue.get('title', '').lower()
        description = issue.get('description', '').lower()

        if keyword_lower in title or keyword_lower in description:
            matches.append((i, issue))

    if not matches:
        # List all issues to help the user find the right one
        response = f"❌ No issues found matching '{keyword}'.\n\n"
        response += "**Available issues:**\n"
        for i, issue in enumerate(state.issues, 1):
            response += f"  {i}. {issue.get('title', 'Issue')}\n"
        return response

    if len(matches) == 1:
        issue_num, issue = matches[0]
        return _format_issue_details(issue, issue_num)

    # Multiple matches - list them
    response = f"🔍 **Found {len(matches)} issues matching '{keyword}':**\n\n"
    for issue_num, issue in matches:
        sev = issue.get('severity', 'medium')
        severity_icons = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
        response += f"{issue_num}. {severity_icons.get(sev, '⚪')} **{issue.get('title', 'Issue')}**\n"

    response += f"\nCall `get_issue_details(N)` to see full details for a specific issue."
    return response
