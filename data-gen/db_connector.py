"""
Database connection and data insertion utilities
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()


class DatabaseConnector:
    """Handle database connections and data insertion"""

    def __init__(self):
        self.client: Client = None

    def connect(self):
        """Connect to Supabase using the client library"""
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SECRET_KEY')

            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set in .env file")

            # Create Supabase client with service role key for server-side operations
            self.client = create_client(supabase_url, supabase_key)
            print("Connected to Supabase successfully")

        except Exception as e:
            print(f"Failed to connect to Supabase: {e}")
            raise

    def close(self):
        """Close database connection"""
        # Supabase client doesn't need explicit closing
        print("Database connection closed")

    def insert_genres(self, data: List[Dict]) -> List[str]:
        """Insert genres and return UUIDs"""
        result = self.client.table('genres').insert(data).execute()
        return [row['genre_id'] for row in result.data]

    def insert_labels(self, data: List[Dict]) -> List[str]:
        """Insert labels and return UUIDs"""
        result = self.client.table('labels').insert(data).execute()
        return [row['label_id'] for row in result.data]

    def insert_customers(self, data: List[Dict]) -> List[str]:
        """Insert customers and return UUIDs"""
        result = self.client.table('customers').insert(data).execute()
        return [row['customer_id'] for row in result.data]

    def insert_albums(self, data: List[Dict]) -> List[str]:
        """Insert albums and return UUIDs"""
        result = self.client.table('albums').insert(data).execute()
        return [row['album_id'] for row in result.data]

    def insert_inventory(self, data: List[Dict]) -> List[str]:
        """Insert inventory records and return UUIDs"""
        result = self.client.table('inventory').insert(data).execute()
        return [row['inventory_id'] for row in result.data]

    def insert_orders(self, data: List[Dict]) -> List[str]:
        """Insert orders and return UUIDs"""
        result = self.client.table('orders').insert(data).execute()
        return [row['order_id'] for row in result.data]

    def insert_order_items(self, data: List[Dict]):
        """Insert order items"""
        self.client.table('order_items').insert(data).execute()

    def insert_payments(self, data: List[Dict]):
        """Insert payments"""
        self.client.table('payments').insert(data).execute()

    def insert_reviews(self, data: List[Dict]):
        """Insert reviews"""
        self.client.table('reviews').insert(data).execute()

    def insert_sales(self, data: List[Dict]):
        """Insert sales transactions (renamed from inventory_transactions)"""
        self.client.table('sales').insert(data).execute()

    def insert_workflows(self, data: List[Dict]) -> List[str]:
        """Insert workflows and return UUIDs"""
        result = self.client.table('workflows').insert(data).execute()
        return [row['workflow_id'] for row in result.data]

    def insert_workflow_executions(self, data: List[Dict]):
        """Insert workflow executions"""
        self.client.table('workflow_executions').insert(data).execute()
