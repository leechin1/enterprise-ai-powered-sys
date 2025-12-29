-- Misty AI Enterprise System - Indexes Migration
-- Migration: 03_indexes.sql
-- Description: Creates performance indexes

-- CUSTOMERS INDEXES
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);

-- ALBUMS INDEXES
CREATE INDEX IF NOT EXISTS idx_albums_genre ON albums(genre_id);
CREATE INDEX IF NOT EXISTS idx_albums_label ON albums(label_id);
CREATE INDEX IF NOT EXISTS idx_albums_artist ON albums(artist);
CREATE INDEX IF NOT EXISTS idx_albums_price ON albums(price);
CREATE INDEX IF NOT EXISTS idx_albums_title_search ON albums USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_albums_artist_search ON albums USING gin(to_tsvector('english', artist));

-- INVENTORY INDEXES
CREATE INDEX IF NOT EXISTS idx_inventory_album ON inventory(album_id);
CREATE INDEX IF NOT EXISTS idx_inventory_quantity ON inventory(quantity);

-- SALES INDEXES (renamed from inventory_transactions)
CREATE INDEX IF NOT EXISTS idx_sales_inventory ON sales(inventory_id);
CREATE INDEX IF NOT EXISTS idx_sales_order ON sales(order_id);
CREATE INDEX IF NOT EXISTS idx_sales_type ON sales(transaction_type);
CREATE INDEX IF NOT EXISTS idx_sales_created ON sales(created_at DESC);

-- ORDERS INDEXES
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date DESC);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date DESC);

-- ORDER ITEMS INDEXES
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_album ON order_items(album_id);
CREATE INDEX IF NOT EXISTS idx_order_items_created ON order_items(created_at DESC);

-- PAYMENTS INDEXES
CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date DESC);
CREATE INDEX IF NOT EXISTS idx_payments_transaction ON payments(transaction_id);

-- REVIEWS INDEXES
CREATE INDEX IF NOT EXISTS idx_reviews_customer ON reviews(customer_id);
CREATE INDEX IF NOT EXISTS idx_reviews_album ON reviews(album_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_created ON reviews(created_at DESC);

-- Full-text search on review text
CREATE INDEX IF NOT EXISTS idx_reviews_text_search ON reviews USING gin(to_tsvector('english', review_text));

-- GENRES INDEXES
CREATE INDEX IF NOT EXISTS idx_genres_name ON genres(name);

-- LABELS INDEXES
CREATE INDEX IF NOT EXISTS idx_labels_name ON labels(name);

-- WORKFLOW TABLES INDEXES (already in 02_workflow_tables.sql, but included here for completeness)

-- For dashboard queries
CREATE INDEX IF NOT EXISTS idx_workflow_executions_recent
    ON workflow_executions(status, start_time DESC);

-- ANALYZE TABLES FOR QUERY PLANNER
ANALYZE customers;
ANALYZE albums;
ANALYZE inventory;
ANALYZE sales;
ANALYZE orders;
ANALYZE order_items;
ANALYZE payments;
ANALYZE reviews;
ANALYZE genres;
ANALYZE labels;
ANALYZE workflows;
ANALYZE workflow_executions;

-- SUCCESS MESSAGE
DO $$
BEGIN
    RAISE NOTICE 'Indexes migration completed successfully!';
    RAISE NOTICE 'Created performance indexes for all tables';
    RAISE NOTICE 'Analyzed tables for query optimization';
END $$;
