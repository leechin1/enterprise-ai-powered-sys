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

# Base class for custom tools
from .base import BaseBusinessTools

__all__ = [
    # Classes
    "BaseBusinessTools",
    "BusinessQueryTools",
    "BusinessGenerationTools",
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
]
