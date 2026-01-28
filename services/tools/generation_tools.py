"""
Business Generation Tools
Content generation and action tools for the AI Business Consultant Agent.
Includes email generation, recommendations, and transaction actions.
"""

import os
from typing import List
from pathlib import Path

from .base import BaseBusinessTools


class BusinessGenerationTools(BaseBusinessTools):
    """Tools for generating content and performing actions (write operations)."""

    def __init__(self):
        super().__init__()
        # Path to templates directory (one level up from tools/)
        self.templates_dir = Path(__file__).parent.parent / "tools_templates"

    def _load_template(self, filename: str) -> str:
        """Load a template file from the templates directory."""
        try:
            filepath = self.templates_dir / filename
            if filepath.exists():
                return filepath.read_text()
            # Fallback: return None to use inline templates
            return None
        except Exception as e:
            return None

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
            customer_result = self.supabase.table('customers').select(
                'first_name, last_name, email'
            ).eq('customer_id', customer_id).execute()

            if not customer_result.data:
                return f"Customer {customer_id} not found."

            customer = customer_result.data[0]

            # Try to load template
            template = self._load_template('customer_email_template.txt')

            if template:
                email = template.format(
                    email=customer['email'],
                    subject=email_type.replace('_', ' ').title(),
                    first_name=customer['first_name'],
                    last_name=customer['last_name'],
                    context=context
                )
            else:
                # Fallback inline template
                email = f"""
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
            return email

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
                album_result = self.supabase.table('albums').select(
                    'title, artist'
                ).eq('album_id', album_id).execute()

                inventory_result = self.supabase.table('inventory').select(
                    'quantity'
                ).eq('album_id', album_id).execute()

                if album_result.data and inventory_result.data:
                    albums_data.append({
                        **album_result.data[0],
                        **inventory_result.data[0]
                    })

            # Build items list
            items_list = ""
            for i, album in enumerate(albums_data, 1):
                items_list += f"{i}. '{album['title']}' by {album['artist']} - {album['quantity']} units remaining\n"

            # Try to load template
            template = self._load_template('inventory_alert_email_template.txt')

            if template:
                email = template.format(items_list=items_list)
            else:
                # Fallback inline template
                email = f"""
INVENTORY ALERT EMAIL
=====================

To: inventory@mistyjazzrecords.com
Subject: LOW STOCK ALERT - Immediate Action Required

Dear Inventory Manager,

The following items have critically low stock levels and require immediate reordering:

{items_list}
Please review and place restock orders as soon as possible to avoid stockouts.

Best regards,
Misty AI Business Intelligence System
=====================
"""
            return email

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
            payment_result = self.supabase.table('payments').select(
                'status, order_id, amount'
            ).eq('payment_id', payment_id).execute()

            if not payment_result.data:
                return f"Payment {payment_id} not found."

            payment = payment_result.data[0]

            if payment['status'] == 'completed':
                return f"Cannot cancel completed payment {payment_id}. Refund process required instead."

            # Update payment status to cancelled
            self.supabase.table('payments').update({
                'status': 'cancelled'
            }).eq('payment_id', payment_id).execute()

            # Try to load template
            template = self._load_template('transaction_cancelled_template.txt')

            if template:
                confirmation = template.format(
                    payment_id=payment_id,
                    order_id=payment['order_id'],
                    amount=f"{payment['amount']:,.2f}",
                    previous_status=payment['status'],
                    reason=reason
                )
            else:
                # Fallback inline template
                confirmation = f"""
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
            return confirmation

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
            album_result = self.supabase.table('albums').select(
                'title, artist'
            ).eq('album_id', album_id).execute()

            if not album_result.data:
                return f"Album {album_id} not found."

            album = album_result.data[0]

            # Get current inventory
            inventory_result = self.supabase.table('inventory').select(
                'quantity'
            ).eq('album_id', album_id).execute()

            current_stock = inventory_result.data[0]['quantity'] if inventory_result.data else 0

            # Get sales history
            sales_result = self.supabase.table('sales').select(
                'quantity_change'
            ).eq('inventory_id', album_id).execute()

            total_sold = abs(sum([s['quantity_change'] for s in sales_result.data])) if sales_result.data else 0

            # Recommendation logic based on demand
            if total_sold > 50:
                recommended_qty = 100
                rationale = "High demand item"
            elif total_sold > 20:
                recommended_qty = 50
                rationale = "Moderate demand"
            else:
                recommended_qty = 25
                rationale = "Standard restock"

            # Try to load template
            template = self._load_template('restock_recommendation_template.txt')

            if template:
                recommendation = template.format(
                    title=album['title'],
                    artist=album['artist'],
                    current_stock=current_stock,
                    total_sold=total_sold,
                    recommended_qty=recommended_qty,
                    rationale=rationale
                )
            else:
                # Fallback inline template
                recommendation = f"""
RESTOCK RECOMMENDATION
======================
Album: '{album['title']}' by {album['artist']}
Current Stock: {current_stock} units
Total Sold: {total_sold} units
Recommended Restock: {recommended_qty} units
Rationale: {rationale}
======================
"""
            return recommendation

        except Exception as e:
            return f"Error generating restock recommendation: {str(e)}"


# Tool function wrappers for LangChain
def generate_customer_email(customer_id: str, email_type: str, context: str) -> str:
    """
    Generate an email template for a customer.

    Args:
        customer_id: Customer UUID
        email_type: Type of email (e.g., 'low_stock_notification', 'thank_you', 'promotion')
        context: Additional context for the email
    """
    return BusinessGenerationTools().generate_customer_email(customer_id, email_type, context)


def generate_inventory_alert_email(album_ids: str) -> str:
    """
    Generate an email alert for low inventory items.

    Args:
        album_ids: Comma-separated list of album IDs with low stock
    """
    # Convert string to list
    ids_list = [id.strip() for id in album_ids.split(',')]
    return BusinessGenerationTools().generate_inventory_alert_email(ids_list)


def cancel_transaction(payment_id: str, reason: str) -> str:
    """
    Cancel a pending or failed payment transaction.

    Args:
        payment_id: Payment UUID to cancel
        reason: Reason for cancellation
    """
    return BusinessGenerationTools().cancel_transaction(payment_id, reason)


def recommend_restock_quantity(album_id: str) -> str:
    """
    Recommend optimal restock quantity for an album based on sales history.

    Args:
        album_id: Album UUID
    """
    return BusinessGenerationTools().recommend_restock_quantity(album_id)
