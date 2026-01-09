"""
Database Schema Documentation for Misty Jazz Records Enterprise System
This file provides the complete database schema for AI agents to generate queries
"""

DATABASE_SCHEMA = """
# Misty Jazz Records - Database Schema

## Core Business Tables

### customers
- customer_id (UUID, PRIMARY KEY)
- email (VARCHAR, UNIQUE, NOT NULL)
- first_name (VARCHAR, NOT NULL)
- last_name (VARCHAR, NOT NULL)
- phone (VARCHAR)
- created_at (TIMESTAMPTZ)

### albums
- album_id (UUID, PRIMARY KEY)
- title (VARCHAR, NOT NULL)
- artist (VARCHAR, NOT NULL)
- genre_id (UUID, FOREIGN KEY → genres.genre_id)
- label_id (UUID, FOREIGN KEY → labels.label_id)
- price (NUMERIC, NOT NULL)
- created_at (TIMESTAMPTZ)
- updated_at (TIMESTAMPTZ)

### genres
- genre_id (UUID, PRIMARY KEY)
- name (VARCHAR, UNIQUE, NOT NULL)
- created_at (TIMESTAMPTZ)

### labels
- label_id (UUID, PRIMARY KEY)
- name (VARCHAR, UNIQUE, NOT NULL)
- created_at (TIMESTAMPTZ)

### inventory
- inventory_id (UUID, PRIMARY KEY)
- album_id (UUID, UNIQUE, FOREIGN KEY → albums.album_id)
- quantity (INT, NOT NULL, DEFAULT 0)
- updated_at (TIMESTAMPTZ)

### orders
- order_id (UUID, PRIMARY KEY)
- order_number (VARCHAR, UNIQUE, NOT NULL)
- customer_id (UUID, FOREIGN KEY → customers.customer_id)
- total (NUMERIC, NOT NULL)
- shipping_address (TEXT)
- order_date (TIMESTAMPTZ)
- created_at (TIMESTAMPTZ)
- updated_at (TIMESTAMPTZ)

### order_items
- order_item_id (UUID, PRIMARY KEY)
- order_id (UUID, FOREIGN KEY → orders.order_id)
- album_id (UUID, FOREIGN KEY → albums.album_id)
- quantity (INT, NOT NULL)
- created_at (TIMESTAMPTZ)
Note: Unit prices calculated from albums.price via album_id

### payments
- payment_id (UUID, PRIMARY KEY)
- order_id (UUID, FOREIGN KEY → orders.order_id)
- amount (NUMERIC, NOT NULL)
- payment_method (VARCHAR, CHECK: 'card', 'cash', 'bank_transfer', 'paypal')
- status (VARCHAR, CHECK: 'pending', 'completed', 'failed', 'refunded')
- transaction_id (VARCHAR)
- payment_date (TIMESTAMPTZ)
- created_at (TIMESTAMPTZ)

### sales
- transaction_id (UUID, PRIMARY KEY)
- inventory_id (UUID, FOREIGN KEY → inventory.inventory_id)
- order_id (UUID)
- transaction_type (VARCHAR, CHECK: 'restock', 'sale', 'adjustment', 'return')
- quantity_change (INT, NOT NULL)
- unit_price (NUMERIC)
- created_at (TIMESTAMPTZ)

### reviews
- review_id (UUID, PRIMARY KEY)
- customer_id (UUID, FOREIGN KEY → customers.customer_id)
- album_id (UUID, FOREIGN KEY → albums.album_id)
- rating (INT, CHECK: 1-5)
- review_text (TEXT)
- created_at (TIMESTAMPTZ)

## Key Relationships
- albums → genres (many-to-one)
- albums → labels (many-to-one)
- inventory → albums (one-to-one)
- orders → customers (many-to-one)
- order_items → orders (many-to-one)
- order_items → albums (many-to-one)
- payments → orders (many-to-one)
- sales → inventory (many-to-one)
- reviews → customers (many-to-one)
- reviews → albums (many-to-one)

"""


def get_schema() -> str:
    """Get the complete database schema documentation"""
    return DATABASE_SCHEMA


def get_table_names() -> list:
    """Get list of all table names"""
    return [
        'customers',
        'albums',
        'genres',
        'labels',
        'inventory',
        'orders',
        'order_items',
        'payments',
        'sales',
        'reviews'
    ]


def get_table_relationships() -> dict:
    """Get foreign key relationships between tables"""
    return {
        'albums': ['genres', 'labels'],
        'inventory': ['albums'],
        'orders': ['customers'],
        'order_items': ['orders', 'albums'],
        'payments': ['orders'],
        'sales': ['inventory'],
        'reviews': ['customers', 'albums']
    }
