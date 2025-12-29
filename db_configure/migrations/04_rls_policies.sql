-- Misty AI Enterprise System - Row Level Security Policies
-- Migration: 04_rls_policies.sql
-- Description: Configures Row Level Security (RLS)

-- ENABLE RLS ON TABLES

ALTER TABLE genres ENABLE ROW LEVEL SECURITY;
ALTER TABLE labels ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE albums ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_executions ENABLE ROW LEVEL SECURITY;

-- HELPER FUNCTIONS

-- Function to get current user role
CREATE OR REPLACE FUNCTION auth_role()
RETURNS TEXT AS $$
BEGIN
    RETURN COALESCE(
        current_setting('request.jwt.claims', true)::json->>'role',
        current_setting('request.jwt.claim.role', true),
        'anon'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get current user ID
CREATE OR REPLACE FUNCTION auth_uid()
RETURNS UUID AS $$
BEGIN
    RETURN COALESCE(
        (current_setting('request.jwt.claims', true)::json->>'sub')::UUID,
        (current_setting('request.jwt.claim.sub', true))::UUID
    );
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- GENRES POLICIES

-- Public can view genres (for browsing)
CREATE POLICY "Public can view genres"
    ON genres
    FOR SELECT
    USING (true);

-- Only staff can manage genres
CREATE POLICY "Staff can manage genres"
    ON genres
    FOR ALL
    USING (auth_role() IN ('admin', 'manager', 'staff', 'service_role'));

-- LABELS POLICIES

-- Public can view labels (for browsing)
CREATE POLICY "Public can view labels"
    ON labels
    FOR SELECT
    USING (true);

-- Only staff can manage labels
CREATE POLICY "Staff can manage labels"
    ON labels
    FOR ALL
    USING (auth_role() IN ('admin', 'manager', 'staff', 'service_role'));

-- CUSTOMERS POLICIES

-- Customers can view their own data
CREATE POLICY "Customers can view own data"
    ON customers
    FOR SELECT
    USING (customer_id = auth_uid() OR auth_role() IN ('admin', 'manager', 'staff'));

-- Customers can update their own data
CREATE POLICY "Customers can update own data"
    ON customers
    FOR UPDATE
    USING (customer_id = auth_uid())
    WITH CHECK (customer_id = auth_uid());

-- Staff can view all customers
CREATE POLICY "Staff can view all customers"
    ON customers
    FOR SELECT
    USING (auth_role() IN ('admin', 'manager', 'staff'));

-- Admin can insert/update/delete customers
CREATE POLICY "Admin can manage customers"
    ON customers
    FOR ALL
    USING (auth_role() = 'admin');

-- ALBUMS POLICIES

-- Public can view albums (for browsing)
CREATE POLICY "Public can view albums"
    ON albums
    FOR SELECT
    USING (true);

-- Staff can manage albums
CREATE POLICY "Staff can manage albums"
    ON albums
    FOR ALL
    USING (auth_role() IN ('admin', 'manager', 'staff'));

-- INVENTORY POLICIES

-- Staff can view inventory
CREATE POLICY "Staff can view inventory"
    ON inventory
    FOR SELECT
    USING (auth_role() IN ('admin', 'manager', 'staff'));

-- Manager and admin can manage inventory
CREATE POLICY "Managers can manage inventory"
    ON inventory
    FOR ALL
    USING (auth_role() IN ('admin', 'manager'));

-- ORDERS POLICIES

-- Customers can view their own orders
CREATE POLICY "Customers can view own orders"
    ON orders
    FOR SELECT
    USING (customer_id = auth_uid() OR auth_role() IN ('admin', 'manager', 'staff'));

-- Customers can insert their own orders
CREATE POLICY "Customers can create orders"
    ON orders
    FOR INSERT
    WITH CHECK (customer_id = auth_uid() OR auth_role() IN ('admin', 'manager', 'staff'));

-- Staff can manage all orders
CREATE POLICY "Staff can manage orders"
    ON orders
    FOR ALL
    USING (auth_role() IN ('admin', 'manager', 'staff'));

-- ORDER ITEMS POLICIES

-- Customers can view items in their orders
CREATE POLICY "Customers can view own order items"
    ON order_items
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM orders
            WHERE orders.order_id = order_items.order_id
            AND (orders.customer_id = auth_uid() OR auth_role() IN ('admin', 'manager', 'staff'))
        )
    );

-- Staff can manage order items
CREATE POLICY "Staff can manage order items"
    ON order_items
    FOR ALL
    USING (auth_role() IN ('admin', 'manager', 'staff'));

-- PAYMENTS POLICIES

-- Customers can view their own payments
CREATE POLICY "Customers can view own payments"
    ON payments
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM orders
            WHERE orders.order_id = payments.order_id
            AND (orders.customer_id = auth_uid() OR auth_role() IN ('admin', 'manager', 'staff'))
        )
    );

-- Only admin can view all payments
CREATE POLICY "Admin can manage payments"
    ON payments
    FOR ALL
    USING (auth_role() = 'admin');

-- REVIEWS POLICIES

-- Public can read reviews
CREATE POLICY "Public can view reviews"
    ON reviews
    FOR SELECT
    USING (true);

-- Customers can insert their own reviews
CREATE POLICY "Customers can create reviews"
    ON reviews
    FOR INSERT
    WITH CHECK (customer_id = auth_uid());

-- Customers can update/delete their own reviews
CREATE POLICY "Customers can manage own reviews"
    ON reviews
    FOR UPDATE
    USING (customer_id = auth_uid())
    WITH CHECK (customer_id = auth_uid());

CREATE POLICY "Customers can delete own reviews"
    ON reviews
    FOR DELETE
    USING (customer_id = auth_uid());

-- Admin can manage all reviews
CREATE POLICY "Admin can manage all reviews"
    ON reviews
    FOR ALL
    USING (auth_role() = 'admin');

-- WORKFLOWS POLICIES

-- Staff can view workflows
CREATE POLICY "Staff can view workflows"
    ON workflows
    FOR SELECT
    USING (auth_role() IN ('admin', 'manager', 'staff', 'system'));

-- Admin can manage workflows
CREATE POLICY "Admin can manage workflows"
    ON workflows
    FOR ALL
    USING (auth_role() IN ('admin', 'system'));

-- WORKFLOW EXECUTIONS POLICIES

-- Staff can view workflow executions
CREATE POLICY "Staff can view workflow executions"
    ON workflow_executions
    FOR SELECT
    USING (auth_role() IN ('admin', 'manager', 'staff', 'system'));

-- System can manage workflow executions
CREATE POLICY "System can manage workflow executions"
    ON workflow_executions
    FOR ALL
    USING (auth_role() IN ('admin', 'system'));

-- SALES POLICIES

-- Staff can view sales transactions
CREATE POLICY "Staff can view sales"
    ON sales
    FOR SELECT
    USING (auth_role() IN ('admin', 'manager', 'staff', 'system'));

-- Manager/admin can manage sales transactions
CREATE POLICY "Managers can manage sales"
    ON sales
    FOR ALL
    USING (auth_role() IN ('admin', 'manager', 'system'));

-- GRANT PERMISSIONS

-- Anonymous users (public browsing)
GRANT SELECT ON albums TO anon;
GRANT SELECT ON reviews TO anon;
GRANT SELECT ON genres TO anon;
GRANT SELECT ON labels TO anon;

-- Authenticated users
GRANT SELECT, INSERT, UPDATE ON customers TO authenticated;
GRANT SELECT ON albums, genres, labels TO authenticated;
GRANT SELECT, INSERT, UPDATE ON orders TO authenticated;
GRANT SELECT, INSERT ON order_items TO authenticated;
GRANT SELECT ON payments TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON reviews TO authenticated;

-- Service role (backend/system)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- SUCCESS MESSAGE
DO $$
BEGIN
    RAISE NOTICE 'RLS policies migration completed successfully!';
    RAISE NOTICE 'Enabled Row Level Security on all sensitive tables';
    RAISE NOTICE 'Created policies for role-based access control';
    RAISE NOTICE 'Configured permissions for anon, authenticated, and service_role';
END $$;
