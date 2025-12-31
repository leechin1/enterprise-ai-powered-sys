"""
Database analytics utilities for fetching real-time data from Supabase
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()


class AnalyticsConnector:
    """Handle analytics queries to Supabase"""

    def __init__(self):
        self.client: Optional[Client] = None
        self._connect()

    def _connect(self):
        """Connect to Supabase"""
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SECRET_KEY')

            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set in .env file")

            self.client = create_client(supabase_url, supabase_key)

        except Exception as e:
            print(f"Failed to connect to Supabase: {e}")
            raise

    # ============ SALES ANALYTICS ============

    def get_total_revenue(self) -> float:
        """Get total revenue from all completed orders"""
        result = self.client.table('orders').select('total').execute()
        if result.data:
            return sum(float(order['total']) for order in result.data)
        return 0.0

    def get_total_orders(self) -> int:
        """Get total number of orders"""
        result = self.client.table('orders').select('order_id', count='exact').execute()
        return result.count if result.count else 0

    def get_total_customers(self) -> int:
        """Get total number of customers"""
        result = self.client.table('customers').select('customer_id', count='exact').execute()
        return result.count if result.count else 0

    def get_average_order_value(self) -> float:
        """Calculate average order value"""
        total_revenue = self.get_total_revenue()
        total_orders = self.get_total_orders()
        return total_revenue / total_orders if total_orders > 0 else 0.0

    def get_orders_by_date(self) -> pd.DataFrame:
        """Get orders grouped by date"""
        result = self.client.table('orders').select('order_date, total, order_id').execute()

        if not result.data:
            return pd.DataFrame()

        df = pd.DataFrame(result.data)
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['date'] = df['order_date'].dt.date

        # Group by date
        daily_stats = df.groupby('date').agg({
            'total': 'sum',
            'order_id': 'count'
        }).reset_index()

        daily_stats.columns = ['date', 'revenue', 'order_count']

        return daily_stats

    def get_top_customers(self, limit: int = 10) -> pd.DataFrame:
        """Get top customers by total spending"""
        # Get all orders with customer info
        result = self.client.table('orders').select(
            'customer_id, total, customers(first_name, last_name, email)'
        ).execute()

        if not result.data:
            return pd.DataFrame()

        # Process the data
        customer_spending = {}
        for order in result.data:
            if order['customer_id'] and order['customers']:
                customer_id = order['customer_id']
                if customer_id not in customer_spending:
                    customer_spending[customer_id] = {
                        'customer_id': customer_id,
                        'name': f"{order['customers']['first_name']} {order['customers']['last_name']}",
                        'email': order['customers']['email'],
                        'total_spent': 0.0,
                        'order_count': 0
                    }
                customer_spending[customer_id]['total_spent'] += float(order['total'])
                customer_spending[customer_id]['order_count'] += 1

        df = pd.DataFrame(list(customer_spending.values()))
        if not df.empty:
            df = df.sort_values('total_spent', ascending=False).head(limit)

        return df

    # ============ INVENTORY ANALYTICS ============

    def get_inventory_summary(self) -> Dict[str, int]:
        """Get inventory stock level summary"""
        result = self.client.table('inventory').select('quantity').execute()

        if not result.data:
            return {'total_items': 0, 'low_stock': 0, 'out_of_stock': 0, 'optimal_stock': 0}

        quantities = [item['quantity'] for item in result.data]

        return {
            'total_items': len(quantities),
            'low_stock': len([q for q in quantities if 0 < q <= 20]),
            'out_of_stock': len([q for q in quantities if q == 0]),
            'optimal_stock': len([q for q in quantities if q > 20])
        }

    def get_low_stock_albums(self, threshold: int = 20) -> pd.DataFrame:
        """Get albums with low stock"""
        result = self.client.table('inventory').select(
            'quantity, album_id, albums(title, artist, price)'
        ).lte('quantity', threshold).execute()

        if not result.data:
            return pd.DataFrame()

        data = []
        for item in result.data:
            if item['albums']:
                data.append({
                    'title': item['albums']['title'],
                    'artist': item['albums']['artist'],
                    'quantity': item['quantity'],
                    'price': float(item['albums']['price'])
                })

        return pd.DataFrame(data)

    def get_total_inventory_value(self) -> float:
        """Calculate total inventory value"""
        result = self.client.table('inventory').select(
            'quantity, albums(price)'
        ).execute()

        if not result.data:
            return 0.0

        total_value = 0.0
        for item in result.data:
            if item['albums']:
                total_value += item['quantity'] * float(item['albums']['price'])

        return total_value

    # ============ GENRE ANALYTICS ============

    def get_genre_performance(self) -> pd.DataFrame:
        """Get sales performance by genre"""
        # Get all order items with album and genre info
        result = self.client.table('order_items').select(
            'quantity, album_id, albums(price, genre_id, genres(name))'
        ).execute()

        if not result.data:
            return pd.DataFrame()

        genre_stats = {}
        for item in result.data:
            if item['albums'] and item['albums']['genres']:
                genre_name = item['albums']['genres']['name']
                quantity = item['quantity']
                price = float(item['albums']['price'])
                revenue = quantity * price

                if genre_name not in genre_stats:
                    genre_stats[genre_name] = {
                        'genre': genre_name,
                        'units_sold': 0,
                        'revenue': 0.0
                    }

                genre_stats[genre_name]['units_sold'] += quantity
                genre_stats[genre_name]['revenue'] += revenue

        df = pd.DataFrame(list(genre_stats.values()))
        if not df.empty:
            df = df.sort_values('revenue', ascending=False)

        return df

    # ============ ALBUM ANALYTICS ============

    def get_top_selling_albums(self, limit: int = 10) -> pd.DataFrame:
        """Get top selling albums by units sold"""
        result = self.client.table('order_items').select(
            'quantity, album_id, albums(title, artist, price)'
        ).execute()

        if not result.data:
            return pd.DataFrame()

        album_sales = {}
        for item in result.data:
            if item['albums']:
                album_id = item['album_id']
                if album_id not in album_sales:
                    album_sales[album_id] = {
                        'title': item['albums']['title'],
                        'artist': item['albums']['artist'],
                        'price': float(item['albums']['price']),
                        'units_sold': 0,
                        'revenue': 0.0
                    }

                quantity = item['quantity']
                album_sales[album_id]['units_sold'] += quantity
                album_sales[album_id]['revenue'] += quantity * album_sales[album_id]['price']

        df = pd.DataFrame(list(album_sales.values()))
        if not df.empty:
            df = df.sort_values('units_sold', ascending=False).head(limit)

        return df

    # ============ REVIEW ANALYTICS ============

    def get_average_rating(self) -> float:
        """Get average rating across all reviews"""
        result = self.client.table('reviews').select('rating').execute()

        if not result.data:
            return 0.0

        ratings = [review['rating'] for review in result.data]
        return sum(ratings) / len(ratings) if ratings else 0.0

    def get_review_count(self) -> int:
        """Get total number of reviews"""
        result = self.client.table('reviews').select('review_id', count='exact').execute()
        return result.count if result.count else 0

    def get_top_rated_albums(self, limit: int = 10) -> pd.DataFrame:
        """Get top rated albums with minimum review count"""
        result = self.client.table('reviews').select(
            'rating, album_id, albums(title, artist)'
        ).execute()

        if not result.data:
            return pd.DataFrame()

        album_ratings = {}
        for review in result.data:
            if review['albums']:
                album_id = review['album_id']
                if album_id not in album_ratings:
                    album_ratings[album_id] = {
                        'title': review['albums']['title'],
                        'artist': review['albums']['artist'],
                        'total_rating': 0,
                        'review_count': 0
                    }

                album_ratings[album_id]['total_rating'] += review['rating']
                album_ratings[album_id]['review_count'] += 1

        # Calculate average ratings
        data = []
        for album_id, stats in album_ratings.items():
            if stats['review_count'] >= 2:  # Minimum 2 reviews
                data.append({
                    'title': stats['title'],
                    'artist': stats['artist'],
                    'avg_rating': stats['total_rating'] / stats['review_count'],
                    'review_count': stats['review_count']
                })

        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values('avg_rating', ascending=False).head(limit)

        return df

    # ============ PAYMENT ANALYTICS ============

    def get_payment_method_distribution(self) -> pd.DataFrame:
        """Get distribution of payment methods"""
        result = self.client.table('payments').select('payment_method, amount').execute()

        if not result.data:
            return pd.DataFrame()

        method_stats = {}
        for payment in result.data:
            method = payment['payment_method']
            if method not in method_stats:
                method_stats[method] = {
                    'payment_method': method,
                    'count': 0,
                    'total_amount': 0.0
                }

            method_stats[method]['count'] += 1
            method_stats[method]['total_amount'] += float(payment['amount'])

        return pd.DataFrame(list(method_stats.values()))

    def get_payment_status_summary(self) -> Dict[str, int]:
        """Get payment status summary"""
        result = self.client.table('payments').select('status').execute()

        if not result.data:
            return {}

        status_counts = {}
        for payment in result.data:
            status = payment['status']
            status_counts[status] = status_counts.get(status, 0) + 1

        return status_counts

    # ============ LABEL ANALYTICS ============

    def get_label_performance(self) -> pd.DataFrame:
        """Get sales performance by record label"""
        result = self.client.table('order_items').select(
            'quantity, albums(price, label_id, labels(name))'
        ).execute()

        if not result.data:
            return pd.DataFrame()

        label_stats = {}
        for item in result.data:
            if item['albums'] and item['albums']['labels']:
                label_name = item['albums']['labels']['name']
                quantity = item['quantity']
                price = float(item['albums']['price'])
                revenue = quantity * price

                if label_name not in label_stats:
                    label_stats[label_name] = {
                        'label': label_name,
                        'units_sold': 0,
                        'revenue': 0.0
                    }

                label_stats[label_name]['units_sold'] += quantity
                label_stats[label_name]['revenue'] += revenue

        df = pd.DataFrame(list(label_stats.values()))
        if not df.empty:
            df = df.sort_values('revenue', ascending=False)

        return df
