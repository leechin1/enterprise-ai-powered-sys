"""
Business Agent Tools
Tools for the AI Business Consultant Agent to interact with the database and perform actions
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from utils.db_analytics import AnalyticsConnector

load_dotenv()


class BusinessAnalysisTools:
    """Tools for analyzing business data and taking actions"""

    def __init__(self):
        self.analytics = AnalyticsConnector()
        # Initialize Supabase client for actions
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

    def generate_customer_email(self, customer_id: str, email_type: str, context: str) -> str:
        """
        Generate an email template for a customer.

        Args:
            customer_id: Customer UUID
            email_type: Type of email (e.g., 'low_stock_notification', 'thank_you', 'promotion')
            context: Additional context for the email

        Returns:
            Email template as a string
        """
        try:
            # Fetch customer details
            customer_result = self.supabase_client.table('customers').select(
                'first_name, last_name, email'
            ).eq('customer_id', customer_id).execute()

            if not customer_result.data:
                return f"Customer {customer_id} not found."

            customer = customer_result.data[0]

            email_template = f"""
EMAIL TEMPLATE GENERATED
========================

To: {customer['email']}
Subject: {email_type.replace('_', ' ').title()} - Misty Jazz Records

Dear {customer['first_name']} {customer['last_name']},

{context}

Best regards,
Misty Jazz Records Team

========================
Note: This is a generated template. Review before sending.
"""
            return email_template

        except Exception as e:
            return f"Error generating email: {str(e)}"

    def generate_inventory_alert_email(self, album_ids: List[str]) -> str:
        """
        Generate an email alert for low inventory items.

        Args:
            album_ids: List of album IDs with low stock

        Returns:
            Email template for inventory manager
        """
        try:
            if not album_ids:
                return "No album IDs provided for inventory alert."

            # Fetch album details
            albums_data = []
            for album_id in album_ids[:10]:  # Limit to 10 items
                album_result = self.supabase_client.table('albums').select(
                    'title, artist'
                ).eq('album_id', album_id).execute()

                inventory_result = self.supabase_client.table('inventory').select(
                    'quantity'
                ).eq('album_id', album_id).execute()

                if album_result.data and inventory_result.data:
                    albums_data.append({
                        **album_result.data[0],
                        **inventory_result.data[0]
                    })

            email_content = """
INVENTORY ALERT EMAIL
=====================

To: inventory@mistyjazzrecords.com
Subject: LOW STOCK ALERT - Immediate Action Required

Dear Inventory Manager,

The following items have critically low stock levels and require immediate reordering:

"""
            for i, album in enumerate(albums_data, 1):
                email_content += f"{i}. '{album['title']}' by {album['artist']} - {album['quantity']} units remaining\n"

            email_content += """
Please review and place restock orders as soon as possible to avoid stockouts.

Best regards,
Misty AI Business Intelligence System
=====================
"""
            return email_content

        except Exception as e:
            return f"Error generating inventory alert: {str(e)}"

    def cancel_transaction(self, payment_id: str, reason: str) -> str:
        """
        Cancel a pending or failed payment transaction.

        Args:
            payment_id: Payment UUID to cancel
            reason: Reason for cancellation

        Returns:
            Confirmation message
        """
        try:
            # Check if payment exists and is cancellable
            payment_result = self.supabase_client.table('payments').select(
                'status, order_id, amount'
            ).eq('payment_id', payment_id).execute()

            if not payment_result.data:
                return f"Payment {payment_id} not found."

            payment = payment_result.data[0]

            if payment['status'] == 'completed':
                return f"Cannot cancel completed payment {payment_id}. Refund process required instead."

            # Update payment status to cancelled
            self.supabase_client.table('payments').update({
                'status': 'cancelled'
            }).eq('payment_id', payment_id).execute()

            return f"""
TRANSACTION CANCELLED
====================
Payment ID: {payment_id}
Order ID: {payment['order_id']}
Amount: ${payment['amount']:,.2f}
Previous Status: {payment['status']}
New Status: cancelled
Reason: {reason}
====================
"""

        except Exception as e:
            return f"Error cancelling transaction: {str(e)}"

    def recommend_restock_quantity(self, album_id: str) -> str:
        """
        Recommend optimal restock quantity for an album based on sales history.

        Args:
            album_id: Album UUID

        Returns:
            Recommendation with quantity and rationale
        """
        try:
            # Get album details
            album_result = self.supabase_client.table('albums').select(
                'title, artist'
            ).eq('album_id', album_id).execute()

            if not album_result.data:
                return f"Album {album_id} not found."

            album = album_result.data[0]

            # Get current inventory
            inventory_result = self.supabase_client.table('inventory').select(
                'quantity'
            ).eq('album_id', album_id).execute()

            current_stock = inventory_result.data[0]['quantity'] if inventory_result.data else 0

            # Get sales history
            sales_result = self.supabase_client.table('sales').select(
                'quantity_change'
            ).eq('inventory_id', album_id).execute()

            total_sold = abs(sum([s['quantity_change'] for s in sales_result.data])) if sales_result.data else 0

            # Simple recommendation logic
            if total_sold > 50:
                recommended_qty = 100
                rationale = "High demand item"
            elif total_sold > 20:
                recommended_qty = 50
                rationale = "Moderate demand"
            else:
                recommended_qty = 25
                rationale = "Standard restock"

            return f"""
RESTOCK RECOMMENDATION
======================
Album: '{album['title']}' by {album['artist']}
Current Stock: {current_stock} units
Total Sold: {total_sold} units
Recommended Restock: {recommended_qty} units
Rationale: {rationale}
======================
"""

        except Exception as e:
            return f"Error generating restock recommendation: {str(e)}"


# Tool function wrappers for LangChain
def scan_business_metrics() -> str:
    """Scan and retrieve all key business metrics from the database."""
    tools = BusinessAnalysisTools()
    return tools.scan_business_metrics()


def get_top_performing_products(limit: int = 5) -> str:
    """Get top-selling albums with revenue and units sold data."""
    tools = BusinessAnalysisTools()
    return tools.get_top_performing_products(limit)


def get_top_customers(limit: int = 5) -> str:
    """Get top customers by total spending."""
    tools = BusinessAnalysisTools()
    return tools.get_top_customers(limit)


def get_low_stock_items(threshold: int = 10) -> str:
    """Get albums with low inventory levels."""
    tools = BusinessAnalysisTools()
    return tools.get_low_stock_items(threshold)


def get_failed_payments() -> str:
    """Get all failed payment transactions that need attention."""
    tools = BusinessAnalysisTools()
    return tools.get_failed_payments()


def get_pending_payments() -> str:
    """Get all pending payment transactions."""
    tools = BusinessAnalysisTools()
    return tools.get_pending_payments()


def get_genre_performance() -> str:
    """Get sales performance by genre."""
    tools = BusinessAnalysisTools()
    return tools.get_genre_performance()


def generate_customer_email(customer_id: str, email_type: str, context: str) -> str:
    """
    Generate an email template for a customer.

    Args:
        customer_id: Customer UUID
        email_type: Type of email (e.g., 'low_stock_notification', 'thank_you', 'promotion')
        context: Additional context for the email
    """
    tools = BusinessAnalysisTools()
    return tools.generate_customer_email(customer_id, email_type, context)


def generate_inventory_alert_email(album_ids: str) -> str:
    """
    Generate an email alert for low inventory items.

    Args:
        album_ids: Comma-separated list of album IDs with low stock
    """
    tools = BusinessAnalysisTools()
    # Convert string to list
    ids_list = [id.strip() for id in album_ids.split(',')]
    return tools.generate_inventory_alert_email(ids_list)


def cancel_transaction(payment_id: str, reason: str) -> str:
    """
    Cancel a pending or failed payment transaction.

    Args:
        payment_id: Payment UUID to cancel
        reason: Reason for cancellation
    """
    tools = BusinessAnalysisTools()
    return tools.cancel_transaction(payment_id, reason)


def recommend_restock_quantity(album_id: str) -> str:
    """
    Recommend optimal restock quantity for an album based on sales history.

    Args:
        album_id: Album UUID
    """
    tools = BusinessAnalysisTools()
    return tools.recommend_restock_quantity(album_id)
