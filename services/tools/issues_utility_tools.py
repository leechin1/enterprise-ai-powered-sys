"""
Issues Agent Utility Tools
Tools for checking analysis state and resetting.
"""

from langchain.tools import tool
from .issues_state import IssuesAgentState


@tool
def get_current_analysis_state() -> str:
    """
    Get a summary of the current analysis state.
    Use this to check what has been done so far in the analysis.

    Returns:
        Summary of current queries, results, issues, and proposed fixes.
        If no analysis has been done, suggests starting one.
    """
    state = IssuesAgentState.get_instance()

    # Check if any analysis has been done
    has_any_state = state.queries or state.query_results or state.issues or state.proposed_fixes

    if not has_any_state:
        return """## 📊 Current Analysis State

**Status:** No analysis in progress.

No queries have been generated or executed yet. This is a fresh session.

**To start an analysis, you can:**
- Say "Run a full business analysis" for comprehensive analysis
- Say "Check inventory issues" to focus on stock problems
- Say "Look for payment problems" to focus on transactions
- Or describe any specific business concern you have

I'll automatically generate SQL queries, execute them, and identify any issues."""

    response = "## 📊 Current Analysis State\n\n"

    # Queries
    if state.queries:
        response += f"**Queries Generated:** {len(state.queries)} ✅\n"
    else:
        response += "**Queries Generated:** None ❌\n"

    # Results
    if state.query_results:
        response += f"**Queries Executed:** {len(state.query_results)} results ✅\n"
    else:
        response += "**Queries Executed:** Not yet ❌\n"

    # Issues
    if state.issues:
        response += f"**Issues Identified:** {len(state.issues)} ✅\n"
        for i, issue in enumerate(state.issues, 1):
            response += f"  {i}. [{issue.get('severity', 'medium').upper()}] {issue.get('title', 'Issue')}\n"
    else:
        response += "**Issues Identified:** Not yet ❌\n"

    # Fixes
    if state.proposed_fixes:
        response += f"**Fix Proposed:** Yes ✅ (for issue #{state.selected_issue_index + 1})\n"
    else:
        response += "**Fix Proposed:** Not yet ❌\n"

    response += f"\n**Focus Areas:** {', '.join(state.focus_areas) if state.focus_areas else 'Not set'}"

    # Add next steps based on current state
    response += "\n\n**Next steps:**\n"
    if not state.queries:
        response += "- Generate queries with `generate_business_queries()`\n"
    elif not state.query_results:
        response += "- Execute queries with `execute_business_queries()`\n"
    elif not state.issues:
        response += "- Analyze results with `analyze_issues_from_results()`\n"
    elif not state.proposed_fixes:
        response += "- Get a fix proposal with `propose_fix_for_issue(N)`\n"
    else:
        response += "- Send notifications with `send_fix_emails()`\n"
        response += "- Or start fresh with `reset_analysis()`\n"

    return response


@tool
def reset_analysis() -> str:
    """
    Reset all analysis state to start fresh.
    Use when the user wants to begin a completely new analysis.

    Returns:
        Confirmation that the state has been reset.
    """
    state = IssuesAgentState.get_instance()
    state.reset()

    return "🔄 **Analysis state reset!**\n\nReady to start a new analysis. You can:\n- Call `generate_business_queries()` to investigate all areas\n- Call `generate_business_queries('inventory')` to focus on specific areas"
