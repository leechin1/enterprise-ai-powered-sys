"""
Business Tools Package
Provides LangChain-compatible tools for the AI Business Consultant Agent.
"""

# Query tools (read-only operations)
from .query_tools import (
    BusinessQueryTools,
    scan_business_metrics,
    get_top_performing_products,
    get_top_customers,
    get_low_stock_items,
    get_failed_payments,
    get_pending_payments,
    get_genre_performance,
    get_label_performance,
    get_top_rated_albums,
    get_payment_method_distribution,
    get_revenue_by_date,
)

# Generation tools (write operations)
from .generation_tools import (
    BusinessGenerationTools,
    generate_customer_email,
    generate_inventory_alert_email,
    cancel_transaction,
    recommend_restock_quantity,
)

# Issues Agent tools (agentic workflow) - modular imports
from .issues_state import IssuesAgentState
from .issues_query_tools import generate_business_queries, execute_business_queries
from .issues_analysis_tools import (
    analyze_issues_from_results,
    get_issue_details,
    get_issue_detail,
    find_issue_by_keyword,
)
from .issues_fix_tools import propose_fix_for_issue, edit_email, send_fix_emails
from .issues_utility_tools import get_current_analysis_state, reset_analysis

# Base class for custom tools
from .base import BaseBusinessTools

__all__ = [
    # Classes
    "BaseBusinessTools",
    "BusinessQueryTools",
    "BusinessGenerationTools",
    "IssuesAgentState",
    # Query functions
    "scan_business_metrics",
    "get_top_performing_products",
    "get_top_customers",
    "get_low_stock_items",
    "get_failed_payments",
    "get_pending_payments",
    "get_genre_performance",
    "get_label_performance",
    "get_top_rated_albums",
    "get_payment_method_distribution",
    "get_revenue_by_date",
    # Generation functions
    "generate_customer_email",
    "generate_inventory_alert_email",
    "cancel_transaction",
    "recommend_restock_quantity",
    # Issues Agent tools
    "generate_business_queries",
    "execute_business_queries",
    "analyze_issues_from_results",
    "propose_fix_for_issue",
    "edit_email",
    "send_fix_emails",
    "get_current_analysis_state",
    "reset_analysis",
    "get_issue_details",
    "get_issue_detail",
    "find_issue_by_keyword",
]
