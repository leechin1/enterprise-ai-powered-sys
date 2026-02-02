"""
Issues Agent Query Tools
Tools for generating and executing SQL queries.
"""

from langchain.tools import tool
from services.ai_issues_agent import AIIssuesAgent
from .issues_state import IssuesAgentState


@tool
def generate_business_queries(focus_areas: str = "all") -> str:
    """
    Generate SQL queries to investigate potential business issues.
    This is typically the FIRST step in analyzing business problems.

    Args:
        focus_areas: Areas to focus on. Options:
                    - "inventory" for stock issues
                    - "payments" for payment/transaction issues
                    - "customers" for customer satisfaction issues
                    - "revenue" for sales/revenue concerns
                    - "operations" for operational issues
                    - "all" for comprehensive analysis (default)
                    Can combine multiple: "inventory, payments"

    Returns:
        Summary of generated queries with their purposes and priorities.

    Example:
        generate_business_queries("inventory, payments")
    """
    state = IssuesAgentState.get_instance()

    # Parse focus areas
    areas = [a.strip().lower() for a in focus_areas.split(',')]
    state.focus_areas = areas

    # Use base agent to generate queries with focus areas
    base_agent = AIIssuesAgent()
    result = base_agent.generate_sql_queries(focus_areas=areas)

    if not result.get('success'):
        return f"❌ Failed to generate queries: {result.get('error', 'Unknown error')}"

    queries = result.get('data', {}).get('queries', [])
    state.queries = queries

    # Format response
    response = f"✅ **Generated {len(queries)} SQL Queries**\n"
    response += f"Focus areas: {', '.join(areas)}\n\n"

    priority_icons = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}

    for i, q in enumerate(queries, 1):
        priority = q.get('priority', 'medium')
        icon = priority_icons.get(priority, '⚪')
        response += f"{i}. {icon} **{q.get('purpose', 'Query')}** ({priority})\n"
        response += f"   _{q.get('explanation', '')}_\n\n"

    response += f"\n**Status:** Queries ready for execution."

    return response


@tool
def execute_business_queries() -> str:
    """
    Execute the previously generated SQL queries against the database.
    MUST call generate_business_queries() first.

    Returns:
        Summary of query execution results including row counts, sample data, and any errors.
    """
    state = IssuesAgentState.get_instance()

    if not state.queries:
        return "❌ No queries to execute. Please generate queries first."

    base_agent = AIIssuesAgent()
    result = base_agent.execute_sql_queries(state.queries)

    if not result.get('success'):
        return f"❌ Query execution failed: {result.get('error', 'Unknown error')}"

    results = result.get('results', [])
    state.query_results = results

    successful = result.get('successful_queries', 0)
    total = result.get('total_queries', 0)
    total_rows = sum(len(r.get('data', [])) for r in results)

    response = f"✅ **Executed {successful}/{total} Queries Successfully**\n\n"
    response += f"📊 **Total Records Found:** {total_rows}\n\n"

    response += "| Query | Purpose | Records |\n"
    response += "|-------|---------|--------|\n"

    for r in results:
        status = "✅" if r.get('success') else "❌"
        row_count = len(r.get('data', []))
        purpose = r.get('purpose', 'Query')[:40]
        response += f"| {status} {r.get('query_id', '?')} | {purpose} | {row_count} |\n"

    response += f"\n**Status:** Query data ready for analysis."

    return response
