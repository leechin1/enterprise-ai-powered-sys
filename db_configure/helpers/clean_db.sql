-- Clean all records from database (respecting foreign key constraints)
-- Execute this in Supabase SQL Editor

BEGIN;

-- Dependent tables first (child records)
DELETE FROM case_messages;
DELETE FROM workflow_executions;
DELETE FROM inventory_transactions;
DELETE FROM order_items;
DELETE FROM payments;
DELETE FROM shipments;
DELETE FROM reviews;

-- Mid-level tables
DELETE FROM cases;
DELETE FROM orders;
DELETE FROM inventory;
DELETE FROM integrations;
DELETE FROM workflows;
DELETE FROM system_logs;

-- Parent tables (base entities)
DELETE FROM albums;
DELETE FROM customers;
DELETE FROM users;
DELETE FROM genres;
DELETE FROM labels;

COMMIT;

-- Verify all tables are empty
SELECT 
    'genres' as table_name, COUNT(*) as records FROM genres
UNION ALL SELECT 'labels', COUNT(*) FROM labels
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'albums', COUNT(*) FROM albums
UNION ALL SELECT 'inventory', COUNT(*) FROM inventory
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'payments', COUNT(*) FROM payments
UNION ALL SELECT 'shipments', COUNT(*) FROM shipments
UNION ALL SELECT 'reviews', COUNT(*) FROM reviews
UNION ALL SELECT 'cases', COUNT(*) FROM cases
UNION ALL SELECT 'case_messages', COUNT(*) FROM case_messages
UNION ALL SELECT 'workflows', COUNT(*) FROM workflows
UNION ALL SELECT 'workflow_executions', COUNT(*) FROM workflow_executions
UNION ALL SELECT 'integrations', COUNT(*) FROM integrations
UNION ALL SELECT 'system_logs', COUNT(*) FROM system_logs
ORDER BY table_name;
