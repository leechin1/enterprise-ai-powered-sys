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
    """
    state = IssuesAgentState.get_instance()

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
