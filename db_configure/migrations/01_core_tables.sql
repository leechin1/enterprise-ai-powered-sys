-- Misty AI Enterprise System - Core Tables Migration
-- Migration: 01_core_tables.sql
-- Description: Creates core business entities

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for additional cryptographic functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- CUSTOMERS TABLE
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE customers IS 'Customer profiles';

-- GENRES TABLE
CREATE TABLE genres (
    genre_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE genres IS 'Music genres and categories';

-- LABELS TABLE
CREATE TABLE labels (
    label_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE labels IS 'Record labels and publishers';

-- ALBUMS TABLE
CREATE TABLE albums (
    album_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(300) NOT NULL,
    artist VARCHAR(300) NOT NULL,
    genre_id UUID REFERENCES genres(genre_id) ON DELETE SET NULL,
    label_id UUID REFERENCES labels(label_id) ON DELETE SET NULL,
    price NUMERIC NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE albums IS 'Vinyl album catalog';

-- INVENTORY TABLE
CREATE TABLE inventory (
    inventory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    album_id UUID UNIQUE REFERENCES albums(album_id) ON DELETE CASCADE,
    quantity INT4 NOT NULL DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE inventory IS 'Real-time inventory tracking';

-- SALES TABLE 
CREATE TABLE sales (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventory_id UUID REFERENCES inventory(inventory_id) ON DELETE CASCADE,
    order_id UUID,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('restock', 'sale', 'adjustment', 'return')),
    quantity_change INT4 NOT NULL,
    unit_price NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE sales IS 'Complete audit trail of inventory changes';

-- ORDERS TABLE
CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id UUID REFERENCES customers(customer_id) ON DELETE SET NULL,
    total NUMERIC NOT NULL,
    shipping_address TEXT,
    order_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE orders IS 'Customer orders';

-- ORDER ITEMS TABLE
CREATE TABLE order_items (
    order_item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(order_id) ON DELETE CASCADE,
    album_id UUID REFERENCES albums(album_id) ON DELETE SET NULL,
    quantity INT4 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE order_items IS 'Line items in orders - unit price calculated from albums.price via album_id';

-- PAYMENTS TABLE
CREATE TABLE payments (
    payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(order_id) ON DELETE CASCADE,
    amount NUMERIC NOT NULL,
    payment_method VARCHAR(30) CHECK (payment_method IN ('card', 'cash', 'bank_transfer', 'paypal')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    transaction_id VARCHAR(200),
    payment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE payments IS 'Payment transactions';

-- REVIEWS TABLE
CREATE TABLE reviews (
    review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(customer_id) ON DELETE CASCADE,
    album_id UUID REFERENCES albums(album_id) ON DELETE CASCADE,
    rating INT4 NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE reviews IS 'Customer product reviews';

-- TRIGGERS FOR UPDATED_AT

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to inventory table
CREATE TRIGGER update_inventory_updated_at BEFORE UPDATE ON inventory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- SUCCESS MESSAGE
DO $$
BEGIN
    RAISE NOTICE 'Core tables migration completed successfully!';
    RAISE NOTICE 'Created: customers, genres, labels, albums, inventory, sales, orders, order_items, payments, reviews';
END $$;
