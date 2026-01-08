"""
Business Query Tools
Read-only analytics and querying tools for the AI Business Consultant Agent
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from utils.db_analytics import AnalyticsConnector

load_dotenv()


class BusinessQueryTools:
    """Tools for querying and analyzing business data (read-only)"""

    def __init__(self):
        self.analytics = AnalyticsConnector()
        # Initialize Supabase client for queries
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SECRET_KEY')
        self.supabase_client: Client = create_client(supabase_url, supabase_key)

    def scan_business_metrics(self) -> str:
        """
        Scan and retrieve all key business metrics from the database.
        Returns a comprehensive summary of financial, customer, inventory, and product data.
        """
        try:
            metrics = {
                "financial": {
                    "total_revenue": self.analytics.get_total_revenue(),
                    "total_orders": self.analytics.get_total_orders(),
                    "avg_order_value": self.analytics.get_average_order_value(),
                },
                "customers": {
                    "total_customers": self.analytics.get_total_customers(),
                    "avg_rating": self.analytics.get_average_rating(),
                    "total_reviews": self.analytics.get_review_count(),
                },
                "inventory": {
                    "summary": self.analytics.get_inventory_summary(),
                    "total_value": self.analytics.get_total_inventory_value(),
                    "low_stock_count": len(self.analytics.get_low_stock_albums(threshold=10)),
                },
                "payments": {
                    "status_summary": self.analytics.get_payment_status_summary(),
                }
            }

            # Format as readable string for the LLM
            summary = f"""
BUSINESS METRICS SUMMARY:

FINANCIAL:
- Total Revenue: ${metrics['financial']['total_revenue']:,.2f}
- Total Orders: {metrics['financial']['total_orders']}
- Average Order Value: ${metrics['financial']['avg_order_value']:,.2f}

CUSTOMERS:
- Total Customers: {metrics['customers']['total_customers']}
- Average Rating: {metrics['customers']['avg_rating']:.2f}/5.0
- Total Reviews: {metrics['customers']['total_reviews']}

INVENTORY:
- Total Items: {metrics['inventory']['summary']['total_items']}
- Total Value: ${metrics['inventory']['total_value']:,.2f}
- Low Stock Items (≤10): {metrics['inventory']['low_stock_count']}
- Out of Stock: {metrics['inventory']['summary']['out_of_stock']}

PAYMENTS:
- Completed: {metrics['payments']['status_summary'].get('completed', 0)}
- Pending: {metrics['payments']['status_summary'].get('pending', 0)}
- Failed: {metrics['payments']['status_summary'].get('failed', 0)}
"""
            return summary

        except Exception as e:
            return f"Error scanning business metrics: {str(e)}"

    def get_top_performing_products(self, limit: int = 5) -> str:
        """
        Get top-selling albums with revenue and units sold data.

        Args:
            limit: Number of top products to retrieve (default 5)
        """
        try:
            top_albums = self.analytics.get_top_selling_albums(limit=limit)

            if top_albums.empty:
                return "No product sales data available."

            result = f"TOP {limit} PERFORMING PRODUCTS:\n\n"
            for i, album in enumerate(top_albums.to_dict('records'), 1):
                result += f"{i}. '{album.get('title', 'N/A')}' by {album.get('artist', 'N/A')}\n"
                result += f"   - Units Sold: {album.get('units_sold', 0)}\n"
                result += f"   - Revenue: ${album.get('revenue', 0):,.2f}\n\n"

            return result

        except Exception as e:
            return f"Error retrieving top products: {str(e)}"

    def get_top_customers(self, limit: int = 5) -> str:
        """
        Get top customers by total spending.

        Args:
            limit: Number of top customers to retrieve (default 5)
        """
        try:
            top_customers = self.analytics.get_top_customers(limit=limit)

            if top_customers.empty:
                return "No customer spending data available."

            result = f"TOP {limit} CUSTOMERS BY SPENDING:\n\n"
            for i, customer in enumerate(top_customers.to_dict('records'), 1):
                result += f"{i}. {customer.get('name', 'N/A')}\n"
                result += f"   - Total Spent: ${customer.get('total_spent', 0):,.2f}\n"
                result += f"   - Orders: {customer.get('order_count', 0)}\n\n"

            return result

        except Exception as e:
            return f"Error retrieving top customers: {str(e)}"

    def get_low_stock_items(self, threshold: int = 10) -> str:
        """
        Get albums with low inventory levels.

        Args:
            threshold: Stock level threshold (default 10)
        """
        try:
            low_stock = self.analytics.get_low_stock_albums(threshold=threshold)

            if low_stock.empty:
                return f"No items with stock below {threshold} units."

            result = f"LOW STOCK ITEMS (≤{threshold} units):\n\n"
            for i, item in enumerate(low_stock.to_dict('records'), 1):
                result += f"{i}. '{item.get('title', 'N/A')}' by {item.get('artist', 'N/A')}\n"
                result += f"   - Current Stock: {item.get('quantity', 0)} units\n"
                result += f"   - Album ID: {item.get('album_id', 'N/A')}\n\n"

            return result

        except Exception as e:
            return f"Error retrieving low stock items: {str(e)}"

    def get_failed_payments(self) -> str:
        """Get all failed payment transactions that need attention."""
        try:
            result = self.supabase_client.table('payments').select(
                'payment_id, order_id, amount, payment_method, transaction_id, created_at'
            ).eq('status', 'failed').execute()

            if not result.data:
                return "No failed payments found."

            output = "FAILED PAYMENTS:\n\n"
            for i, payment in enumerate(result.data, 1):
                output += f"{i}. Payment ID: {payment['payment_id']}\n"
                output += f"   - Order ID: {payment['order_id']}\n"
                output += f"   - Amount: ${payment['amount']:,.2f}\n"
                output += f"   - Method: {payment['payment_method']}\n"
                output += f"   - Transaction ID: {payment['transaction_id']}\n\n"

            return output

        except Exception as e:
            return f"Error retrieving failed payments: {str(e)}"

    def get_pending_payments(self) -> str:
        """Get all pending payment transactions."""
        try:
            result = self.supabase_client.table('payments').select(
                'payment_id, order_id, amount, payment_method, transaction_id, created_at'
            ).eq('status', 'pending').execute()

            if not result.data:
                return "No pending payments found."

            output = "PENDING PAYMENTS:\n\n"
            for i, payment in enumerate(result.data, 1):
                output += f"{i}. Payment ID: {payment['payment_id']}\n"
                output += f"   - Order ID: {payment['order_id']}\n"
                output += f"   - Amount: ${payment['amount']:,.2f}\n"
                output += f"   - Method: {payment['payment_method']}\n\n"

            return output

        except Exception as e:
            return f"Error retrieving pending payments: {str(e)}"

    def get_genre_performance(self) -> str:
        """Get sales performance by genre."""
        try:
            genre_perf = self.analytics.get_genre_performance()

            if genre_perf.empty:
                return "No genre performance data available."

            result = "GENRE PERFORMANCE:\n\n"
            for i, genre in enumerate(genre_perf.to_dict('records'), 1):
                result += f"{i}. {genre.get('genre', 'N/A')}\n"
                result += f"   - Units Sold: {genre.get('units_sold', 0)}\n"
                result += f"   - Revenue: ${genre.get('revenue', 0):,.2f}\n\n"

            return result

        except Exception as e:
            return f"Error retrieving genre performance: {str(e)}"

    def get_label_performance(self) -> str:
        """Get sales performance by record label."""
        try:
            label_perf = self.analytics.get_label_performance()

            if label_perf.empty:
                return "No label performance data available."

            result = "LABEL PERFORMANCE:\n\n"
            for i, label in enumerate(label_perf.to_dict('records'), 1):
                result += f"{i}. {label.get('label', 'N/A')}\n"
                result += f"   - Units Sold: {label.get('units_sold', 0)}\n"
                result += f"   - Revenue: ${label.get('revenue', 0):,.2f}\n\n"

            return result

        except Exception as e:
            return f"Error retrieving label performance: {str(e)}"

    def get_top_rated_albums(self, limit: int = 5) -> str:
        """
        Get top-rated albums with minimum review count.

        Args:
            limit: Number of top albums to retrieve (default 5)
        """
        try:
            top_rated = self.analytics.get_top_rated_albums(limit=limit)

            if top_rated.empty:
                return "No album ratings available."

            result = f"TOP {limit} RATED ALBUMS:\n\n"
            for i, album in enumerate(top_rated.to_dict('records'), 1):
                result += f"{i}. '{album.get('title', 'N/A')}' by {album.get('artist', 'N/A')}\n"
                result += f"   - Average Rating: {album.get('avg_rating', 0):.2f}/5.0\n"
                result += f"   - Review Count: {album.get('review_count', 0)}\n\n"

            return result

        except Exception as e:
            return f"Error retrieving top rated albums: {str(e)}"

    def get_payment_method_distribution(self) -> str:
        """Get distribution of payment methods used."""
        try:
            payment_dist = self.analytics.get_payment_method_distribution()

            if payment_dist.empty:
                return "No payment method data available."

            result = "PAYMENT METHOD DISTRIBUTION:\n\n"
            for i, method in enumerate(payment_dist.to_dict('records'), 1):
                result += f"{i}. {method.get('payment_method', 'N/A').title()}\n"
                result += f"   - Transaction Count: {method.get('count', 0)}\n"
                result += f"   - Total Amount: ${method.get('total_amount', 0):,.2f}\n\n"

            return result

        except Exception as e:
            return f"Error retrieving payment method distribution: {str(e)}"

    def get_revenue_by_date(self) -> str:
        """Get daily revenue breakdown."""
        try:
            orders_by_date = self.analytics.get_orders_by_date()

            if orders_by_date.empty:
                return "No order date data available."

            result = "DAILY REVENUE BREAKDOWN:\n\n"
            for i, day in enumerate(orders_by_date.to_dict('records'), 1):
                result += f"{day.get('date', 'N/A')}: ${day.get('revenue', 0):,.2f} ({day.get('order_count', 0)} orders)\n"

            return result

        except Exception as e:
            return f"Error retrieving revenue by date: {str(e)}"


# Tool function wrappers for LangChain
def scan_business_metrics() -> str:
    """Scan and retrieve all key business metrics from the database."""
    tools = BusinessQueryTools()
    return tools.scan_business_metrics()


def get_top_performing_products(limit: int = 5) -> str:
    """Get top-selling albums with revenue and units sold data."""
    tools = BusinessQueryTools()
    return tools.get_top_performing_products(limit)


def get_top_customers(limit: int = 5) -> str:
    """Get top customers by total spending."""
    tools = BusinessQueryTools()
    return tools.get_top_customers(limit)


def get_low_stock_items(threshold: int = 10) -> str:
    """Get albums with low inventory levels."""
    tools = BusinessQueryTools()
    return tools.get_low_stock_items(threshold)


def get_failed_payments() -> str:
    """Get all failed payment transactions that need attention."""
    tools = BusinessQueryTools()
    return tools.get_failed_payments()


def get_pending_payments() -> str:
    """Get all pending payment transactions."""
    tools = BusinessQueryTools()
    return tools.get_pending_payments()


def get_genre_performance() -> str:
    """Get sales performance by genre."""
    tools = BusinessQueryTools()
    return tools.get_genre_performance()


def get_label_performance() -> str:
    """Get sales performance by record label."""
    tools = BusinessQueryTools()
    return tools.get_label_performance()


def get_top_rated_albums(limit: int = 5) -> str:
    """Get top-rated albums with minimum review count."""
    tools = BusinessQueryTools()
    return tools.get_top_rated_albums(limit)


def get_payment_method_distribution() -> str:
    """Get distribution of payment methods used."""
    tools = BusinessQueryTools()
    return tools.get_payment_method_distribution()


def get_revenue_by_date() -> str:
    """Get daily revenue breakdown."""
    tools = BusinessQueryTools()
    return tools.get_revenue_by_date()
