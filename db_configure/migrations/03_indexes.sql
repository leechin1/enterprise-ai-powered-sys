-- Misty AI Enterprise System - Indexes Migration
-- Migration: 03_indexes.sql
-- Description: Creates performance indexes

-- CUSTOMERS INDEXES
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_customers_lifetime_value ON customers(lifetime_value DESC);
CREATE INDEX IF NOT EXISTS idx_customers_date_joined ON customers(date_joined DESC);
CREATE INDEX IF NOT EXISTS idx_customers_preferred_genre ON customers(preferred_genre);

-- ALBUMS INDEXES
CREATE INDEX IF NOT EXISTS idx_albums_sku ON albums(sku);
CREATE INDEX IF NOT EXISTS idx_albums_genre ON albums(genre_id);
CREATE INDEX IF NOT EXISTS idx_albums_label ON albums(label_id);
CREATE INDEX IF NOT EXISTS idx_albums_artist ON albums(artist);
CREATE INDEX IF NOT EXISTS idx_albums_price ON albums(price);
CREATE INDEX IF NOT EXISTS idx_albums_is_rare ON albums(is_rare) WHERE is_rare = TRUE;
CREATE INDEX IF NOT EXISTS idx_albums_title_search ON albums USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_albums_artist_search ON albums USING gin(to_tsvector('english', artist));

-- INVENTORY INDEXES
CREATE INDEX IF NOT EXISTS idx_inventory_album ON inventory(album_id);
CREATE INDEX IF NOT EXISTS idx_inventory_quantity ON inventory(quantity);
CREATE INDEX IF NOT EXISTS idx_inventory_turnover ON inventory(turnover_rate DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_inventory_low_stock ON inventory(quantity) WHERE quantity <= reorder_point;
CREATE INDEX IF NOT EXISTS idx_inventory_last_restock ON inventory(last_restock_date DESC NULLS LAST);

-- INVENTORY TRANSACTIONS INDEXES
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_inventory ON inventory_transactions(inventory_id);
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_order ON inventory_transactions(order_id);
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_type ON inventory_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_created ON inventory_transactions(created_at DESC);

-- ORDERS INDEXES
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date DESC);
CREATE INDEX IF NOT EXISTS idx_orders_channel ON orders(channel);
CREATE INDEX IF NOT EXISTS idx_orders_total ON orders(total DESC);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status_date ON orders(status, order_date DESC);

-- ORDER ITEMS INDEXES
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_album ON order_items(album_id);
CREATE INDEX IF NOT EXISTS idx_order_items_created ON order_items(created_at DESC);

-- PAYMENTS INDEXES
CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date DESC);
CREATE INDEX IF NOT EXISTS idx_payments_fraud ON payments(fraud_flagged) WHERE fraud_flagged = TRUE;
CREATE INDEX IF NOT EXISTS idx_payments_transaction ON payments(transaction_id);

-- SHIPMENTS INDEXES
CREATE INDEX IF NOT EXISTS idx_shipments_order ON shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_tracking ON shipments(tracking_number);
CREATE INDEX IF NOT EXISTS idx_shipments_shipped_date ON shipments(shipped_date DESC NULLS LAST);

-- REVIEWS INDEXES
CREATE INDEX IF NOT EXISTS idx_reviews_customer ON reviews(customer_id);
CREATE INDEX IF NOT EXISTS idx_reviews_album ON reviews(album_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment);
CREATE INDEX IF NOT EXISTS idx_reviews_created ON reviews(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reviews_verified ON reviews(verified_purchase) WHERE verified_purchase = TRUE;

-- Full-text search on review text
CREATE INDEX IF NOT EXISTS idx_reviews_text_search ON reviews USING gin(to_tsvector('english', review_text));

-- USERS INDEXES
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(active) WHERE active = TRUE;

-- GENRES INDEXES
CREATE INDEX IF NOT EXISTS idx_genres_name ON genres(name);
CREATE INDEX IF NOT EXISTS idx_genres_popularity ON genres(popularity_score DESC);

-- LABELS INDEXES
CREATE INDEX IF NOT EXISTS idx_labels_name ON labels(name);
CREATE INDEX IF NOT EXISTS idx_labels_country ON labels(country);

-- WORKFLOW TABLES INDEXES (already in 02_workflow_tables.sql, but included here for completeness)

-- For case management
CREATE INDEX IF NOT EXISTS idx_cases_open
    ON cases(priority DESC, created_at DESC)
    WHERE status IN ('pending', 'in_progress');

-- For dashboard queries (removed WHERE clause with CURRENT_DATE as it's not immutable)
CREATE INDEX IF NOT EXISTS idx_workflow_executions_recent
    ON workflow_executions(status, start_time DESC);

-- For system logs queries
CREATE INDEX IF NOT EXISTS idx_system_logs_recent_errors
    ON system_logs(created_at DESC)
    WHERE log_level IN ('error', 'critical');

-- For integrations monitoring
CREATE INDEX IF NOT EXISTS idx_integrations_connected ON integrations(connected);
CREATE INDEX IF NOT EXISTS idx_integrations_errors ON integrations(error_count DESC) WHERE error_count > 0;

-- ANALYZE TABLES FOR QUERY PLANNER
ANALYZE customers;
ANALYZE albums;
ANALYZE inventory;
ANALYZE inventory_transactions;
ANALYZE orders;
ANALYZE order_items;
ANALYZE payments;
ANALYZE shipments;
ANALYZE reviews;
ANALYZE users;
ANALYZE genres;
ANALYZE labels;
ANALYZE cases;
ANALYZE case_messages;
ANALYZE workflows;
ANALYZE workflow_executions;
ANALYZE system_logs;
ANALYZE integrations;

-- SUCCESS MESSAGE
DO $$
BEGIN
    RAISE NOTICE 'Indexes migration completed successfully!';
    RAISE NOTICE 'Created performance indexes for all tables';
    RAISE NOTICE 'Analyzed tables for query optimization';
END $$;
