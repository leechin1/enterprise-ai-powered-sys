"""
Marketing Service
Handles customer segmentation and email campaign data for marketing purposes
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
from google import genai
from google.genai import types

load_dotenv()


class MarketingService:
    """Handle marketing-specific queries and email generation"""

    def __init__(self):
        self.client: Optional[Client] = None
        self.gemini_client = None
        self._connect()

    def _connect(self):
        """Connect to Supabase and Gemini"""
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SECRET_KEY')

            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set in .env file")

            self.client = create_client(supabase_url, supabase_key)

            # Initialize Gemini
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            if gemini_api_key:
                self.gemini_client = genai.Client(api_key=gemini_api_key)

        except Exception as e:
            print(f"Failed to connect to services: {e}")
            raise

    # ============ CUSTOMER SEGMENTATION QUERIES ============

    def get_lowest_purchasing_customers(self, limit: int = 50) -> pd.DataFrame:
        """
        Get customers with lowest total spending
        Calculation: SUM(orders.total) per customer, sorted ascending
        Query: Join orders with customers, group by customer, order by sum(total) ASC
        """
        try:
            # Get all customers
            customers_result = self.client.table('customers').select(
                'customer_id, first_name, last_name, email, created_at'
            ).execute()

            if not customers_result.data:
                return pd.DataFrame()

            # Get ALL orders with totals
            orders_result = self.client.table('orders').select(
                'customer_id, total'
            ).execute()

            if not orders_result.data:
                return pd.DataFrame()

            # Build customer spending map - start fresh for each calculation
            customer_spending = {}

            # Sum up order totals per customer
            for order in orders_result.data:
                customer_id = order['customer_id']
                if customer_id:
                    if customer_id not in customer_spending:
                        customer_spending[customer_id] = {
                            'total_spent': 0.0,
                            'order_count': 0
                        }
                    # Sum the order total
                    customer_spending[customer_id]['total_spent'] += float(order['total'])
                    customer_spending[customer_id]['order_count'] += 1

            # Build final customer list with details
            customer_list = []
            for customer in customers_result.data:
                customer_id = customer['customer_id']
                # Only include customers who have made purchases
                if customer_id in customer_spending:
                    customer_list.append({
                        'customer_id': customer_id,
                        'first_name': customer['first_name'],
                        'last_name': customer['last_name'],
                        'name': f"{customer['first_name']} {customer['last_name']}",
                        'email': customer['email'],
                        'created_at': customer['created_at'],
                        'total_spent': customer_spending[customer_id]['total_spent'],
                        'order_count': customer_spending[customer_id]['order_count']
                    })

            # Convert to dataframe and sort by lowest total spending (ascending)
            df = pd.DataFrame(customer_list)
            if not df.empty:
                df = df.sort_values('total_spent', ascending=True).head(limit)

            return df

        except Exception as e:
            print(f"Error in get_lowest_purchasing_customers: {e}")
            return pd.DataFrame()

    def get_inactive_customers(self, days_inactive: int = 90, limit: int = 50) -> pd.DataFrame:
        """
        Get customers who haven't purchased in X days
        Query: Find customers where last order_date < (today - days_inactive)
        """
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_inactive)
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')

            # Get all customers
            customers_result = self.client.table('customers').select(
                'customer_id, first_name, last_name, email, created_at'
            ).execute()

            if not customers_result.data:
                return pd.DataFrame()

            # Get all orders
            orders_result = self.client.table('orders').select(
                'customer_id, order_date, total'
            ).execute()

            # Build customer activity map
            customer_data = {}
            customer_orders = {}

            # Initialize all customers
            for customer in customers_result.data:
                customer_id = customer['customer_id']
                customer_data[customer_id] = {
                    'customer_id': customer_id,
                    'first_name': customer['first_name'],
                    'last_name': customer['last_name'],
                    'name': f"{customer['first_name']} {customer['last_name']}",
                    'email': customer['email'],
                    'created_at': customer['created_at'],
                    'last_order_date': None,
                    'total_spent': 0.0,
                    'order_count': 0
                }
                customer_orders[customer_id] = []

            # Process orders
            if orders_result.data:
                for order in orders_result.data:
                    customer_id = order['customer_id']
                    if customer_id and customer_id in customer_data:
                        order_date = pd.to_datetime(order['order_date'])
                        customer_orders[customer_id].append(order_date)
                        customer_data[customer_id]['total_spent'] += float(order['total'])
                        customer_data[customer_id]['order_count'] += 1

            # Find inactive customers
            inactive_customers = []
            now = datetime.now()

            for customer_id, customer in customer_data.items():
                if customer_orders[customer_id]:
                    # Has orders - check last order date
                    last_order = max(customer_orders[customer_id])
                    customer['last_order_date'] = last_order

                    if last_order < pd.Timestamp(cutoff_date):
                        days_since = (now - last_order.to_pydatetime()).days
                        customer['days_inactive'] = days_since
                        customer['last_order_date_str'] = last_order.strftime('%Y-%m-%d')
                        inactive_customers.append(customer)
                else:
                    # Never ordered - check registration date
                    registration_date = pd.to_datetime(customer['created_at'])
                    if registration_date < pd.Timestamp(cutoff_date):
                        days_since = (now - registration_date.to_pydatetime()).days
                        customer['days_inactive'] = days_since
                        customer['last_order_date_str'] = 'Never'
                        inactive_customers.append(customer)

            # Convert to dataframe
            df = pd.DataFrame(inactive_customers)
            if not df.empty:
                df = df.sort_values('days_inactive', ascending=False).head(limit)

            return df

        except Exception as e:
            print(f"Error in get_inactive_customers: {e}")
            return pd.DataFrame()

    def get_best_customers(self, limit: int = 50) -> pd.DataFrame:
        """
        Get best customers by total spending
        Query: Join orders with customers, group by customer, order by total DESC
        """
        try:
            # Get all customers
            customers_result = self.client.table('customers').select(
                'customer_id, first_name, last_name, email, created_at'
            ).execute()

            if not customers_result.data:
                return pd.DataFrame()

            # Get order totals per customer
            orders_result = self.client.table('orders').select(
                'customer_id, total'
            ).execute()

            # Build customer spending map
            customer_data = {}
            for customer in customers_result.data:
                customer_id = customer['customer_id']
                customer_data[customer_id] = {
                    'customer_id': customer_id,
                    'first_name': customer['first_name'],
                    'last_name': customer['last_name'],
                    'name': f"{customer['first_name']} {customer['last_name']}",
                    'email': customer['email'],
                    'created_at': customer['created_at'],
                    'total_spent': 0.0,
                    'order_count': 0
                }

            # Add order data
            if orders_result.data:
                for order in orders_result.data:
                    customer_id = order['customer_id']
                    if customer_id and customer_id in customer_data:
                        customer_data[customer_id]['total_spent'] += float(order['total'])
                        customer_data[customer_id]['order_count'] += 1

            # Convert to dataframe and sort by highest spending
            df = pd.DataFrame(list(customer_data.values()))
            if not df.empty:
                # Only include customers who have made purchases
                df = df[df['order_count'] > 0]
                df = df.sort_values('total_spent', ascending=False).head(limit)

            return df

        except Exception as e:
            print(f"Error in get_best_customers: {e}")
            return pd.DataFrame()

    def get_genre_specific_customers(self, genre_name: Optional[str] = None, limit: int = 50) -> pd.DataFrame:
        """
        Get customers who have purchased albums from specific genres
        Query: Join order_items -> orders -> customers and albums -> genres
        """
        try:
            # Get all genres first if no genre specified
            if not genre_name:
                genres_result = self.client.table('genres').select('name').limit(1).execute()
                if genres_result.data:
                    genre_name = genres_result.data[0]['name']
                else:
                    return pd.DataFrame()

            # Get the genre_id
            genre_result = self.client.table('genres').select('genre_id, name').eq('name', genre_name).execute()
            if not genre_result.data:
                return pd.DataFrame()

            genre_id = genre_result.data[0]['genre_id']

            # Get all albums for this genre
            albums_result = self.client.table('albums').select(
                'album_id, price'
            ).eq('genre_id', genre_id).execute()

            if not albums_result.data:
                return pd.DataFrame()

            album_ids = [album['album_id'] for album in albums_result.data]
            album_prices = {album['album_id']: float(album['price']) for album in albums_result.data}

            # Get order items for these albums
            order_items_result = self.client.table('order_items').select(
                'order_id, album_id, quantity'
            ).in_('album_id', album_ids).execute()

            if not order_items_result.data:
                return pd.DataFrame()

            # Get orders for these order items
            order_ids = list(set([item['order_id'] for item in order_items_result.data]))
            orders_result = self.client.table('orders').select(
                'order_id, customer_id'
            ).in_('order_id', order_ids).execute()

            if not orders_result.data:
                return pd.DataFrame()

            # Map order_id to customer_id
            order_to_customer = {order['order_id']: order['customer_id'] for order in orders_result.data}

            # Get unique customer IDs
            customer_ids = list(set([order['customer_id'] for order in orders_result.data if order['customer_id']]))

            # Get customer details
            customers_result = self.client.table('customers').select(
                'customer_id, first_name, last_name, email'
            ).in_('customer_id', customer_ids).execute()

            if not customers_result.data:
                return pd.DataFrame()

            # Build customer genre spending map
            customer_data = {}
            for customer in customers_result.data:
                customer_id = customer['customer_id']
                customer_data[customer_id] = {
                    'customer_id': customer_id,
                    'first_name': customer['first_name'],
                    'last_name': customer['last_name'],
                    'name': f"{customer['first_name']} {customer['last_name']}",
                    'email': customer['email'],
                    'genre': genre_name,
                    'genre_spent': 0.0,
                    'genre_units': 0
                }

            # Calculate spending per customer for this genre
            for item in order_items_result.data:
                order_id = item['order_id']
                album_id = item['album_id']
                quantity = item['quantity']

                if order_id in order_to_customer:
                    customer_id = order_to_customer[order_id]
                    if customer_id in customer_data:
                        price = album_prices.get(album_id, 0.0)
                        customer_data[customer_id]['genre_spent'] += quantity * price
                        customer_data[customer_id]['genre_units'] += quantity

            # Convert to dataframe
            df = pd.DataFrame(list(customer_data.values()))
            if not df.empty:
                # Only include customers who actually bought from this genre
                df = df[df['genre_units'] > 0]
                df = df.sort_values('genre_spent', ascending=False).head(limit)

            return df

        except Exception as e:
            print(f"Error in get_genre_specific_customers: {e}")
            return pd.DataFrame()

    def get_available_genres(self) -> List[str]:
        """Get list of all available genres"""
        try:
            result = self.client.table('genres').select('name').execute()
            if result.data:
                return [genre['name'] for genre in result.data]
            return []
        except Exception as e:
            print(f"Error getting genres: {e}")
            return []

    # ============ EMAIL GENERATION ============

    def generate_marketing_email(
        self,
        segment_type: str,
        segment_data: pd.DataFrame,
        tone: str,
        campaign_goal: str,
        include_discount: bool = False,
        discount_percentage: int = 0,
        email_length: str = "Medium",
        custom_instructions: str = ""
    ) -> Optional[str]:
        """
        Generate a marketing email using Gemini AI

        Args:
            segment_type: Type of customer segment (low_spend, inactive, best, genre)
            segment_data: DataFrame with customer segment data
            tone: Email tone (Professional, Friendly, etc.)
            campaign_goal: Campaign objective
            include_discount: Whether to include discount
            discount_percentage: Discount percentage if applicable
            email_length: Short, Medium, or Long
            custom_instructions: Additional instructions

        Returns:
            Generated email text or None if failed
        """
        if not self.gemini_client:
            raise ValueError("Gemini API key not configured")

        if segment_data.empty:
            raise ValueError("No customer data provided")

        # Build segment description
        segment_descriptions = {
            'low_spend': f"low-spending customers (average spent: ${segment_data['total_spent'].mean():.2f}, {len(segment_data)} customers)",
            'inactive': f"inactive customers (haven't purchased in {segment_data['days_inactive'].mean():.0f} days on average, {len(segment_data)} customers)",
            'best': f"VIP customers (average spent: ${segment_data['total_spent'].mean():.2f}, {len(segment_data)} customers)",
            'genre': f"customers who love {segment_data.iloc[0]['genre'] if 'genre' in segment_data.columns else 'jazz'} music ({len(segment_data)} customers)"
        }

        segment_desc = segment_descriptions.get(segment_type, f"valued customers ({len(segment_data)} customers)")

        # Build the prompt
        email_prompt = f"""You are writing a marketing email for Misty Jazz Records, a premium vinyl record store.

**Target Audience:** {segment_desc}
**Total Recipients:** {len(segment_data)}
**Email Tone:** {tone}
**Campaign Goal:** {campaign_goal}
**Discount Offer:** {"Yes - " + str(discount_percentage) + "% off" if include_discount else "No discount"}
**Email Length:** {email_length}

**Additional Instructions:** {custom_instructions if custom_instructions else "None"}

Please generate a compelling marketing email that:
1. Has an engaging subject line
2. Addresses the customer segment appropriately
3. Matches the specified tone
4. Achieves the campaign goal
5. {"Includes the " + str(discount_percentage) + "% discount offer prominently" if include_discount else "Focuses on value and engagement without discounts"}
6. Includes a clear call-to-action
7. Maintains the brand voice of a premium jazz vinyl retailer
8. Is appropriate for the specified length ({email_length})

Format your response as:
SUBJECT: [subject line]

BODY:
[email body]

CALL-TO-ACTION: [main CTA]
"""

        try:
            generation_config = types.GenerateContentConfig(
                system_instruction=[
                    "You are an expert email marketing copywriter for a premium jazz vinyl record store.",
                    "Your emails are engaging, on-brand, and drive customer action.",
                    "You understand different customer segments and tailor messaging accordingly.",
                    "You create compelling subject lines that increase open rates."
                ],
                temperature=0.8,
                top_p=0.95,
                top_k=40,
            )

            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=email_prompt,
                config=generation_config
            )

            return response.text

        except Exception as e:
            print(f"Error generating email: {e}")
            return None
