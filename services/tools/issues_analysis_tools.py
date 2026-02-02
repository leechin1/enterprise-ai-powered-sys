"""
Issues Agent Analysis Tools
Tools for analyzing query results and getting issue details.
"""

from langchain.tools import tool
from services.ai_issues_agent import AIIssuesAgent
from .issues_state import IssuesAgentState


def _format_metrics_dashboard(query_results: list, focus_areas: list) -> str:
    """Format a comprehensive dashboard view of all analyzed data."""
    focus_str = ", ".join(focus_areas) if focus_areas and "all" not in focus_areas else "all areas"

    dashboard = f"\n---\n## 📊 DATA DASHBOARD: {focus_str.upper()}\n\n"

    # Calculate totals
    total_rows = sum(res.get('row_count', 0) for res in query_results)
    successful_queries = sum(1 for res in query_results if res.get('success'))
    total_queries = len(query_results)

    # KPI Summary Box
    dashboard += "### 📈 Analysis Summary\n"
    dashboard += f"- **Queries Executed:** {successful_queries}/{total_queries}\n"
    dashboard += f"- **Total Records Analyzed:** {total_rows}\n"
    dashboard += f"- **Focus Area:** {focus_str}\n\n"

    # Query execution overview
    dashboard += "### 🔍 Queries Executed\n"
    dashboard += "| # | Purpose | Status | Records |\n"
    dashboard += "|---|---------|--------|--------|\n"

    for res in query_results:
        status = "✅" if res.get('success') else "❌"
        row_count = res.get('row_count', 0)
        purpose = res.get('purpose', 'Query')[:45]
        dashboard += f"| {res.get('query_id', '?')} | {purpose} | {status} | {row_count} |\n"

    dashboard += "\n"

    # Show ALL data from each query (not just samples)
    for res in query_results:
        if res.get('success') and res.get('data'):
            data = res.get('data', [])
            if data:
                dashboard += f"### 📋 {res.get('purpose', 'Query Results')}\n"
                dashboard += f"*{res.get('explanation', '')}*\n\n"

                # Show up to 10 rows with up to 6 columns
                preview_rows = data[:10]
                if preview_rows and isinstance(preview_rows[0], dict):
                    cols = list(preview_rows[0].keys())[:6]
                    # Clean column names for display
                    col_headers = [c.replace('_', ' ').title()[:20] for c in cols]
                    dashboard += "| " + " | ".join(col_headers) + " |\n"
                    dashboard += "|" + "|".join(["---"] * len(cols)) + "|\n"

                    for row in preview_rows:
                        values = []
                        for c in cols:
                            val = row.get(c, '')
                            # Format values for readability
                            if isinstance(val, float):
                                val = f"{val:.2f}"
                            elif val is None:
                                val = "-"
                            values.append(str(val)[:25])
                        dashboard += "| " + " | ".join(values) + " |\n"

                    if len(data) > 10:
                        dashboard += f"\n*Showing 10 of {len(data)} records*\n"

                dashboard += "\n"

        elif res.get('success') and not res.get('data'):
            dashboard += f"### 📋 {res.get('purpose', 'Query')}\n"
            dashboard += f"*{res.get('explanation', '')}*\n\n"
            dashboard += "✅ Query returned 0 records (no items match this criteria)\n\n"

        elif not res.get('success'):
            dashboard += f"### ❌ {res.get('purpose', 'Query')} - FAILED\n"
            dashboard += f"Error: {res.get('error', 'Unknown error')}\n\n"

    return dashboard


@tool
def analyze_issues_from_results() -> str:
    """
    Analyze the query results to identify business issues.
    MUST call execute_business_queries() first.

    Returns:
        Detailed list of identified issues with severity, category, and descriptions,
        plus a metrics summary showing what data was analyzed.
    """
    state = IssuesAgentState.get_instance()

    if not state.query_results:
        return "❌ No query results to analyze. Call `execute_business_queries()` first."

    base_agent = AIIssuesAgent()
    # Pass focus_areas to filter issue identification
    result = base_agent.identify_business_issues(state.query_results, focus_areas=state.focus_areas)

    if not result.get('success'):
        return f"❌ Issue analysis failed: {result.get('error', 'Unknown error')}"

    issues = result.get('data', {}).get('issues', [])
    state.issues = issues

    # Build metrics summary for visibility
    metrics_summary = _format_metrics_dashboard(state.query_results, state.focus_areas)

    if not issues:
        focus_str = ", ".join(state.focus_areas) if state.focus_areas and "all" not in state.focus_areas else "all areas"
        response = f"✅ **No significant issues found in {focus_str}!**\n\n"
        response += "The business metrics look healthy based on the data analyzed.\n\n"
        response += metrics_summary
        return response

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
    response += "Example: `propose_fix_for_issue(1)` for the first issue.\n\n"

    # Add metrics summary at the end
    response += metrics_summary

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
