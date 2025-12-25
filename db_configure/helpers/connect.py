"""
Supabase Database Connection Helper
Provides easy database connectivity for Misty AI Enterprise System
"""

import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseDB:
    """Supabase database connection and query helper"""

    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file"
            )

        self.client: Client = create_client(self.url, self.key)

    # ==================== CUSTOMERS ====================

    def get_customers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all customers"""
        response = self.client.table('customers').select("*").limit(limit).execute()
        return response.data

    def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get customer by email"""
        response = self.client.table('customers').select("*").eq('email', email).execute()
        return response.data[0] if response.data else None

    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer"""
        response = self.client.table('customers').insert(customer_data).execute()
        return response.data[0]

    # ==================== ALBUMS ====================

    def get_albums(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all albums with genre information"""
        response = (
            self.client.table('albums')
            .select("*, genres(name), labels(name)")
            .limit(limit)
            .execute()
        )
        return response.data

    def get_album_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get album by SKU"""
        response = (
            self.client.table('albums')
            .select("*, genres(name), labels(name)")
            .eq('sku', sku)
            .execute()
        )
        return response.data[0] if response.data else None

    def search_albums(self, query: str) -> List[Dict[str, Any]]:
        """Search albums by title or artist"""
        response = (
            self.client.table('albums')
            .select("*, genres(name)")
            .or_(f"title.ilike.%{query}%,artist.ilike.%{query}%")
            .execute()
        )
        return response.data

    # ==================== INVENTORY ====================

    def get_inventory(self) -> List[Dict[str, Any]]:
        """Get inventory with album details"""
        response = (
            self.client.table('inventory')
            .select("*, albums(sku, title, artist, price)")
            .execute()
        )
        return response.data

    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """Get items with stock below reorder point"""
        response = (
            self.client.table('inventory')
            .select("*, albums(sku, title, artist, price)")
            .filter('quantity', 'lte', 'reorder_point')
            .execute()
        )
        return response.data

    def update_inventory(self, album_id: str, quantity: int) -> Dict[str, Any]:
        """Update inventory quantity"""
        response = (
            self.client.table('inventory')
            .update({'quantity': quantity})
            .eq('album_id', album_id)
            .execute()
        )
        return response.data[0]

    # ==================== ORDERS ====================

    def get_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent orders"""
        response = (
            self.client.table('orders')
            .select("*, customers(first_name, last_name, email)")
            .order('order_date', desc=True)
            .limit(limit)
            .execute()
        )
        return response.data

    def get_customer_orders(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get orders for a specific customer"""
        response = (
            self.client.table('orders')
            .select("*, order_items(*, albums(title, artist))")
            .eq('customer_id', customer_id)
            .order('order_date', desc=True)
            .execute()
        )
        return response.data

    def create_order(self, order_data: Dict[str, Any], order_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new order with items"""
        # Insert order
        order_response = self.client.table('orders').insert(order_data).execute()
        order_id = order_response.data[0]['order_id']

        # Insert order items
        items_data = [{'order_id': order_id, **item} for item in order_items]
        self.client.table('order_items').insert(items_data).execute()

        return order_response.data[0]

    # ==================== AI RECOMMENDATIONS ====================

    def get_ai_recommendations(self, status: str = 'pending') -> List[Dict[str, Any]]:
        """Get AI recommendations by status"""
        response = (
            self.client.table('ai_recommendations')
            .select("*")
            .eq('status', status)
            .order('confidence_score', desc=True)
            .execute()
        )
        return response.data

    def get_customer_recommendations(self, customer_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a customer"""
        response = (
            self.client.table('customer_recommendations')
            .select("*, albums(sku, title, artist, price)")
            .eq('customer_id', customer_id)
            .order('recommendation_score', desc=True)
            .limit(limit)
            .execute()
        )
        return response.data

    # ==================== ANALYTICS ====================

    def get_sales_metrics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get sales metrics for the last N days"""
        response = (
            self.client.table('sales_metrics')
            .select("*")
            .gte('metric_date', f'now() - interval \'{days} days\'')
            .order('metric_date', desc=True)
            .execute()
        )
        return response.data

    def get_inventory_metrics(self) -> List[Dict[str, Any]]:
        """Get latest inventory metrics"""
        response = (
            self.client.table('inventory_metrics')
            .select("*")
            .order('metric_date', desc=True)
            .limit(1)
            .execute()
        )
        return response.data

    # ==================== CASES ====================

    def get_cases(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get customer service cases"""
        query = self.client.table('cases').select("*, customers(first_name, last_name, email)")

        if status:
            query = query.eq('status', status)

        response = query.order('created_at', desc=True).execute()
        return response.data

    def create_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer service case"""
        response = self.client.table('cases').insert(case_data).execute()
        return response.data[0]

    # ==================== RAW SQL ====================

    def execute_sql(self, query: str) -> List[Dict[str, Any]]:
        """Execute raw SQL query using RPC"""
        # Note: For raw SQL, you need to create a Postgres function in Supabase
        # This is a placeholder for custom queries
        raise NotImplementedError("Use Supabase RPC functions for custom SQL queries")


# Example usage
if __name__ == "__main__":
    try:
        db = SupabaseDB()

        print("=== Testing Supabase Connection ===\n")

        # Test customers
        customers = db.get_customers(limit=5)
        print(f"Found {len(customers)} customers")
        if customers:
            print(f"First customer: {customers[0]['first_name']} {customers[0]['last_name']}")

        # Test albums
        albums = db.get_albums(limit=5)
        print(f"\nFound {len(albums)} albums")
        if albums:
            print(f"First album: {albums[0]['title']} by {albums[0]['artist']}")

        # Test low stock
        low_stock = db.get_low_stock_items()
        print(f"\nFound {len(low_stock)} low stock items")

        # Test AI recommendations
        recommendations = db.get_ai_recommendations()
        print(f"\nFound {len(recommendations)} AI recommendations")

        print("\n=== Connection Test Successful! ===")

    except Exception as e:
        print(f"Error: {e}")
