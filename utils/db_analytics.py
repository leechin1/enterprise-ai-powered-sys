"""
Database analytics utilities for fetching real-time data from Supabase
"""

import os
from typing import List, Dict, Any, Optional
from collections import Counter
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

    # ============ TABLE VIEWER ============

    def get_available_tables(self) -> List[str]:
        """Get list of available tables to query"""
        return [
            'customers',
            'orders',
            'order_items',
            'albums',
            'genres',
            'labels',
            'inventory',
            'sales',
            'payments',
            'reviews'
        ]

    def get_table_data(self, table_name: str, limit: int = 100) -> pd.DataFrame:
        """
        Get all data from a specific table

        Args:
            table_name: Name of the table to query
            limit: Maximum number of rows to return (default 100)

        Returns:
            DataFrame with table data
        """
        try:
            # Validate table name to prevent SQL injection
            valid_tables = self.get_available_tables()
            if table_name not in valid_tables:
                raise ValueError(f"Invalid table name: {table_name}")

            # Query the table
            result = self.client.table(table_name).select('*').limit(limit).execute()

            if not result.data:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(result.data)

            return df

        except Exception as e:
            print(f"Error getting table data for {table_name}: {e}")
            return pd.DataFrame()

    def get_table_count(self, table_name: str) -> int:
        """Get total row count for a table"""
        try:
            valid_tables = self.get_available_tables()
            if table_name not in valid_tables:
                return 0

            result = self.client.table(table_name).select('*', count='exact').limit(1).execute()
            return result.count if result.count else 0

        except Exception as e:
            print(f"Error getting table count for {table_name}: {e}")
            return 0

    # ============ ARTIST ANALYTICS ============

    def get_artist_performance(self, limit: int = 15) -> pd.DataFrame:
        """Get sales performance by artist"""
        result = self.client.table('order_items').select(
            'quantity, albums(artist, price)'
        ).execute()

        if not result.data:
            return pd.DataFrame()

        artist_stats = {}
        for item in result.data:
            if item['albums']:
                artist = item['albums']['artist']
                quantity = item['quantity']
                price = float(item['albums']['price'])
                revenue = quantity * price

                if artist not in artist_stats:
                    artist_stats[artist] = {
                        'artist': artist,
                        'units_sold': 0,
                        'revenue': 0.0,
                        'order_count': 0
                    }

                artist_stats[artist]['units_sold'] += quantity
                artist_stats[artist]['revenue'] += revenue
                artist_stats[artist]['order_count'] += 1

        df = pd.DataFrame(list(artist_stats.values()))
        if not df.empty:
            df = df.sort_values('revenue', ascending=False).head(limit)

        return df

    def get_artist_album_count(self) -> pd.DataFrame:
        """Get number of albums per artist"""
        result = self.client.table('albums').select('artist').execute()

        if not result.data:
            return pd.DataFrame()

        artist_counts = {}
        for album in result.data:
            artist = album['artist']
            artist_counts[artist] = artist_counts.get(artist, 0) + 1

        df = pd.DataFrame([
            {'artist': k, 'album_count': v}
            for k, v in artist_counts.items()
        ])
        if not df.empty:
            df = df.sort_values('album_count', ascending=False)

        return df

    # ============ REVIEW ANALYTICS (EXTENDED) ============

    def get_rating_distribution(self) -> pd.DataFrame:
        """Get distribution of ratings (1-5 stars)"""
        result = self.client.table('reviews').select('rating').execute()

        if not result.data:
            return pd.DataFrame()

        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in result.data:
            rating = review['rating']
            if rating in rating_counts:
                rating_counts[rating] += 1

        df = pd.DataFrame([
            {'rating': k, 'count': v}
            for k, v in sorted(rating_counts.items())
        ])
        return df

    def get_recent_reviews(self, limit: int = 10) -> pd.DataFrame:
        """Get most recent reviews with album and customer info"""
        result = self.client.table('reviews').select(
            'rating, review_text, created_at, albums(title, artist), customers(first_name, last_name)'
        ).order('created_at', desc=True).limit(limit).execute()

        if not result.data:
            return pd.DataFrame()

        data = []
        for review in result.data:
            data.append({
                'album': review['albums']['title'] if review['albums'] else 'N/A',
                'artist': review['albums']['artist'] if review['albums'] else 'N/A',
                'customer': f"{review['customers']['first_name']} {review['customers']['last_name']}" if review['customers'] else 'Anonymous',
                'rating': review['rating'],
                'review': review['review_text'][:100] + '...' if review['review_text'] and len(review['review_text']) > 100 else review['review_text'],
                'date': review['created_at']
            })

        return pd.DataFrame(data)

    # ============ ORDER ANALYTICS (EXTENDED) ============

    def get_orders_by_month(self) -> pd.DataFrame:
        """Get orders grouped by month"""
        result = self.client.table('orders').select('order_date, total, order_id').execute()

        if not result.data:
            return pd.DataFrame()

        df = pd.DataFrame(result.data)
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['month'] = df['order_date'].dt.to_period('M').astype(str)

        monthly_stats = df.groupby('month').agg({
            'total': 'sum',
            'order_id': 'count'
        }).reset_index()

        monthly_stats.columns = ['month', 'revenue', 'order_count']
        return monthly_stats

    def get_orders_by_day_of_week(self) -> pd.DataFrame:
        """Get order distribution by day of week"""
        result = self.client.table('orders').select('order_date, total').execute()

        if not result.data:
            return pd.DataFrame()

        df = pd.DataFrame(result.data)
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['day_of_week'] = df['order_date'].dt.day_name()

        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_stats = df.groupby('day_of_week').agg({
            'total': ['sum', 'count']
        }).reset_index()

        day_stats.columns = ['day', 'revenue', 'order_count']
        day_stats['day'] = pd.Categorical(day_stats['day'], categories=day_order, ordered=True)
        day_stats = day_stats.sort_values('day')

        return day_stats

    def get_customer_order_frequency(self) -> pd.DataFrame:
        """Get distribution of order frequency per customer"""
        result = self.client.table('orders').select('customer_id').execute()

        if not result.data:
            return pd.DataFrame()

        customer_orders = {}
        for order in result.data:
            cid = order['customer_id']
            if cid:
                customer_orders[cid] = customer_orders.get(cid, 0) + 1

        # Categorize into frequency buckets
        freq_buckets = {'1 order': 0, '2-3 orders': 0, '4-5 orders': 0, '6+ orders': 0}
        for count in customer_orders.values():
            if count == 1:
                freq_buckets['1 order'] += 1
            elif count <= 3:
                freq_buckets['2-3 orders'] += 1
            elif count <= 5:
                freq_buckets['4-5 orders'] += 1
            else:
                freq_buckets['6+ orders'] += 1

        return pd.DataFrame([
            {'frequency': k, 'customers': v}
            for k, v in freq_buckets.items()
        ])

    # ============ PAYMENT ANALYTICS (EXTENDED) ============

    def get_payment_status_distribution(self) -> pd.DataFrame:
        """Get payment status distribution with amounts"""
        result = self.client.table('payments').select('status, amount').execute()

        if not result.data:
            return pd.DataFrame()

        status_stats = {}
        for payment in result.data:
            status = payment['status']
            if status not in status_stats:
                status_stats[status] = {
                    'status': status,
                    'count': 0,
                    'total_amount': 0.0
                }
            status_stats[status]['count'] += 1
            status_stats[status]['total_amount'] += float(payment['amount'])

        return pd.DataFrame(list(status_stats.values()))

    def get_payments_over_time(self) -> pd.DataFrame:
        """Get payment trends over time"""
        result = self.client.table('payments').select('payment_date, amount, status').execute()

        if not result.data:
            return pd.DataFrame()

        df = pd.DataFrame(result.data)
        df['payment_date'] = pd.to_datetime(df['payment_date'])
        df['date'] = df['payment_date'].dt.date

        daily_stats = df.groupby('date').agg({
            'amount': 'sum'
        }).reset_index()

        daily_stats.columns = ['date', 'amount']
        return daily_stats

    # ============ SALES TRANSACTION ANALYTICS ============

    def get_sales_transactions_by_type(self) -> pd.DataFrame:
        """Get sales transactions grouped by type"""
        result = self.client.table('sales').select('transaction_type, quantity_change, unit_price').execute()

        if not result.data:
            return pd.DataFrame()

        type_stats = {}
        for txn in result.data:
            txn_type = txn['transaction_type']
            if txn_type not in type_stats:
                type_stats[txn_type] = {
                    'type': txn_type,
                    'count': 0,
                    'total_quantity': 0,
                    'total_value': 0.0
                }
            type_stats[txn_type]['count'] += 1
            type_stats[txn_type]['total_quantity'] += abs(txn['quantity_change'])
            if txn['unit_price']:
                type_stats[txn_type]['total_value'] += abs(txn['quantity_change']) * float(txn['unit_price'])

        return pd.DataFrame(list(type_stats.values()))

    # ============ CUSTOMER ANALYTICS (EXTENDED) ============

    def get_customers_by_registration_month(self) -> pd.DataFrame:
        """Get new customer registrations by month"""
        result = self.client.table('customers').select('created_at').execute()

        if not result.data:
            return pd.DataFrame()

        df = pd.DataFrame(result.data)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['month'] = df['created_at'].dt.to_period('M').astype(str)

        monthly_stats = df.groupby('month').size().reset_index(name='new_customers')
        return monthly_stats

    # ============ PRICE ANALYTICS ============

    def get_price_distribution(self) -> pd.DataFrame:
        """Get album price distribution"""
        result = self.client.table('albums').select('price').execute()

        if not result.data:
            return pd.DataFrame()

        prices = [float(album['price']) for album in result.data]

        # Create price buckets
        buckets = {'$0-$15': 0, '$15-$25': 0, '$25-$35': 0, '$35-$50': 0, '$50+': 0}
        for price in prices:
            if price < 15:
                buckets['$0-$15'] += 1
            elif price < 25:
                buckets['$15-$25'] += 1
            elif price < 35:
                buckets['$25-$35'] += 1
            elif price < 50:
                buckets['$35-$50'] += 1
            else:
                buckets['$50+'] += 1

        return pd.DataFrame([
            {'price_range': k, 'count': v}
            for k, v in buckets.items()
        ])

    # ============ SAVED QUERIES ANALYTICS ============

    def save_generated_queries(self, queries: List[Dict], model: str, name: str = 'last_generated') -> bool:
        """
        Save generated SQL queries to Supabase for later reuse

        Args:
            queries: List of query objects from generate_sql_queries()
            model: Model used to generate queries
            name: Identifier for this query set (default: 'last_generated')

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            import json
            from datetime import datetime

            # Check if entry exists
            existing = self.client.table('saved_queries').select('id').eq('name', name).execute()

            if existing.data:
                # Update existing
                result = self.client.table('saved_queries').update({
                    'queries': queries,
                    'model': model,
                    'updated_at': datetime.now().isoformat()
                }).eq('name', name).execute()
            else:
                # Insert new
                result = self.client.table('saved_queries').insert({
                    'name': name,
                    'description': f'Queries generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                    'queries': queries,
                    'model': model
                }).execute()

            return True

        except Exception as e:
            print(f"Error saving queries: {e}")
            return False

    def load_saved_queries(self, name: str = 'last_generated') -> Optional[Dict]:
        """
        Load previously saved SQL queries from Supabase

        Args:
            name: Identifier for the query set to load

        Returns:
            Dictionary with queries data or None if not found
        """
        try:
            result = self.client.table('saved_queries').select('*').eq('name', name).execute()

            if result.data and len(result.data) > 0:
                row = result.data[0]
                queries = row.get('queries', [])

                # Check if queries is empty
                if not queries or queries == []:
                    return None

                return {
                    'id': row.get('id'),
                    'name': row.get('name'),
                    'description': row.get('description'),
                    'queries': queries,
                    'model': row.get('model'),
                    'created_at': row.get('created_at'),
                    'updated_at': row.get('updated_at')
                }

            return None

        except Exception as e:
            print(f"Error loading queries: {e}")
            return None

    def get_saved_queries_info(self, name: str = 'last_generated') -> Optional[Dict]:
        """
        Get metadata about saved queries without loading full content

        Args:
            name: Identifier for the query set

        Returns:
            Dictionary with metadata or None if not found
        """
        try:
            result = self.client.table('saved_queries').select(
                'name, model, created_at, updated_at, queries'
            ).eq('name', name).execute()

            if result.data and len(result.data) > 0:
                row = result.data[0]
                queries = row.get('queries', [])

                # Check if queries is empty
                if not queries or queries == []:
                    return None

                return {
                    'name': row.get('name'),
                    'model': row.get('model'),
                    'query_count': len(queries),
                    'created_at': row.get('created_at'),
                    'updated_at': row.get('updated_at')
                }

            return None

        except Exception as e:
            print(f"Error getting queries info: {e}")
            return None

    def list_saved_queries(self) -> pd.DataFrame:
        """
        List all saved query sets

        Returns:
            DataFrame with saved query metadata
        """
        try:
            result = self.client.table('saved_queries').select(
                'name, description, model, created_at, updated_at, queries'
            ).order('updated_at', desc=True).execute()

            if not result.data:
                return pd.DataFrame()

            data = []
            for row in result.data:
                queries = row.get('queries', [])
                if queries and queries != []:  # Only include non-empty
                    data.append({
                        'name': row.get('name'),
                        'description': row.get('description'),
                        'model': row.get('model'),
                        'query_count': len(queries),
                        'updated_at': row.get('updated_at')
                    })

            return pd.DataFrame(data)

        except Exception as e:
            print(f"Error listing queries: {e}")
            return pd.DataFrame()
        


    # ============ RECOMMENDER DATA EXTRACTION (ENHANCED) ============

    def get_order_baskets(
        self,
        min_items_per_basket: int = 2,
        min_item_frequency: int = 2,
        use_album_title: bool = True,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[List[str]]:
        
        """
        Build transaction baskets grouped by order.
        Each basket represents a single order and contains
        the unique albums purchased together in that order.

        Processing steps:
        - Deduplicates albums within each order
        - Sorts items deterministically for reproducibility
        - Filters orders by order_date (start_date / end_date)
        - Removes infrequent albums based on global occurrence
        - Discards baskets that become too small after filtering

        Args:
            min_items_per_basket: Minimum number of unique albums required
                for an order to be kept as a basket.
            min_item_frequency: Minimum number of baskets an album must
                appear in globally to be retained.
            use_album_title: If True, uses album titles as basket items;
                otherwise uses album IDs.
            start_date: Optional lower bound (inclusive) for order_date
                filtering (e.g. '2024-01-01').
            end_date: Optional upper bound (inclusive) for order_date
                filtering (e.g. '2024-12-31').

        Returns:
            A list of baskets, where each basket is a sorted list of albums
            purchased together in the same order.
        """

        query = self.client.table('orders').select(
            'order_id, order_date, order_items(album_id, albums(title))'
        )

        if start_date:
            query = query.gte('order_date', start_date)

        if end_date:
            query = query.lte('order_date', end_date)

        result = query.execute()

        if not result.data:
            return []

        baskets: Dict[str, set] = {}

        for order in result.data:
            order_id = order['order_id']
            items = order.get('order_items', [])

            if not items:
                continue

            baskets[order_id] = set()

            for item in items:
                album = item.get('albums')
                if not album:
                    continue

                value = album['title'] if use_album_title else item['album_id']
                baskets[order_id].add(value)

        # Convert to list + filter by basket size
        basket_lists = [
            sorted(list(items))
            for items in baskets.values()
            if len(items) >= min_items_per_basket
        ]

        # Global item frequency filtering
        item_counts = Counter(item for basket in basket_lists for item in basket)
        frequent_items = {
            item for item, count in item_counts.items()
            if count >= min_item_frequency
        }

        filtered_baskets = [
            sorted([item for item in basket if item in frequent_items])
            for basket in basket_lists
        ]

        # Final cleanup: remove baskets that became too small
        return [
            basket for basket in filtered_baskets
            if len(basket) >= min_items_per_basket
        ]


    def get_customer_baskets(
        self,
        min_items_per_customer: int = 2,
        min_item_frequency: int = 2,
        use_album_title: bool = True,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, List[str]]:
        
        """
        Build purchase baskets grouped by customer, suitable for
        customer-level preference modeling and recommendation systems.

        Each basket represents a single customer and contains the unique
        albums purchased by that customer across all their orders.

        Processing steps:
        - Deduplicates albums within each customer basket
        - Sorts items deterministically for reproducibility
        - Filters contributing orders by order_date (start_date / end_date)
        - Removes infrequent albums based on global occurrence
        - Discards customers with too few remaining items

        Args:
            min_items_per_customer: Minimum number of unique albums required
                for a customer to be kept as a basket.
            min_item_frequency: Minimum number of customer baskets an album
                must appear in globally to be retained.
            use_album_title: If True, uses album titles as basket items;
                otherwise uses album IDs.
            start_date: Optional lower bound (inclusive) for order_date
                filtering (e.g. '2024-01-01').
            end_date: Optional upper bound (inclusive) for order_date
                filtering (e.g. '2024-12-31').

        Returns:
            A dictionary mapping customer_id to a sorted list of albums
            purchased by that customer.
        """

        query = self.client.table('orders').select(
            'customer_id, order_date, order_items(album_id, albums(title))'
        )

        if start_date:
            query = query.gte('order_date', start_date)

        if end_date:
            query = query.lte('order_date', end_date)

        result = query.execute()

        if not result.data:
            return {}

        customer_baskets: Dict[str, set] = {}

        for order in result.data:
            customer_id = order.get('customer_id')
            items = order.get('order_items', [])

            if not customer_id or not items:
                continue

            if customer_id not in customer_baskets:
                customer_baskets[customer_id] = set()

            for item in items:
                album = item.get('albums')
                if not album:
                    continue

                value = album['title'] if use_album_title else item['album_id']
                customer_baskets[customer_id].add(value)

        # Convert to sorted lists
        customer_lists = {
            cid: sorted(list(items))
            for cid, items in customer_baskets.items()
            if len(items) >= min_items_per_customer
        }

        # Global item frequency filtering
        item_counts = Counter(
            item for items in customer_lists.values() for item in items
        )

        frequent_items = {
            item for item, count in item_counts.items()
            if count >= min_item_frequency
        }

        filtered_customers = {
            cid: sorted([item for item in items if item in frequent_items])
            for cid, items in customer_lists.items()
        }

        return {
            cid: items
            for cid, items in filtered_customers.items()
            if len(items) >= min_items_per_customer
        }

