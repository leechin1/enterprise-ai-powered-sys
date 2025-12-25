-- =====================================================
-- Misty AI Enterprise System - Common Queries
-- File: queries.sql
-- Description: Frequently used SQL queries for reference
-- =====================================================

-- =====================================================
-- INVENTORY QUERIES
-- =====================================================

-- Get all low stock items
SELECT
    a.sku,
    a.title,
    a.artist,
    a.price,
    i.quantity,
    i.reorder_point,
    g.name AS genre
FROM inventory i
JOIN albums a ON i.album_id = a.album_id
LEFT JOIN genres g ON a.genre_id = g.genre_id
WHERE i.quantity <= i.reorder_point
ORDER BY i.quantity ASC;

-- Get inventory value by genre
SELECT
    g.name AS genre,
    COUNT(a.album_id) AS album_count,
    SUM(i.quantity) AS total_units,
    SUM(i.quantity * a.price) AS inventory_value
FROM inventory i
JOIN albums a ON i.album_id = a.album_id
LEFT JOIN genres g ON a.genre_id = g.genre_id
GROUP BY g.name
ORDER BY inventory_value DESC;

-- Get slow-moving inventory (low turnover)
SELECT
    a.sku,
    a.title,
    a.artist,
    i.quantity,
    i.turnover_rate,
    i.days_in_stock
FROM inventory i
JOIN albums a ON i.album_id = a.album_id
WHERE i.turnover_rate < 3.0
ORDER BY i.days_in_stock DESC
LIMIT 20;

-- =====================================================
-- CUSTOMER QUERIES
-- =====================================================

-- Get top customers by lifetime value
SELECT
    customer_id,
    first_name,
    last_name,
    email,
    lifetime_value,
    total_purchases,
    preferred_genre,
    status
FROM customers
ORDER BY lifetime_value DESC
LIMIT 20;

-- Get customer purchase history
SELECT
    c.first_name,
    c.last_name,
    o.order_number,
    o.order_date,
    o.total,
    o.status,
    COUNT(oi.order_item_id) AS items_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE c.email = 'customer@email.com'
GROUP BY c.first_name, c.last_name, o.order_number, o.order_date, o.total, o.status
ORDER BY o.order_date DESC;

-- Get customer segmentation distribution
SELECT
    segment_type,
    COUNT(DISTINCT customer_id) AS customer_count,
    ROUND(AVG(segment_score), 2) AS avg_score
FROM customer_segments
WHERE assigned_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY segment_type
ORDER BY customer_count DESC;

-- =====================================================
-- SALES QUERIES
-- =====================================================

-- Daily sales summary
SELECT
    DATE(order_date) AS sale_date,
    COUNT(order_id) AS order_count,
    SUM(total) AS total_revenue,
    AVG(total) AS avg_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(order_date)
ORDER BY sale_date DESC;

-- Sales by channel
SELECT
    channel,
    COUNT(order_id) AS order_count,
    SUM(total) AS revenue,
    ROUND(AVG(total), 2) AS avg_order_value
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY channel
ORDER BY revenue DESC;

-- Top selling albums
SELECT
    a.sku,
    a.title,
    a.artist,
    g.name AS genre,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.total) AS revenue
FROM order_items oi
JOIN albums a ON oi.album_id = a.album_id
LEFT JOIN genres g ON a.genre_id = g.genre_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY a.sku, a.title, a.artist, g.name
ORDER BY units_sold DESC
LIMIT 20;

-- Sales by genre
SELECT
    g.name AS genre,
    COUNT(DISTINCT oi.order_item_id) AS items_sold,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.total) AS revenue,
    ROUND(AVG(oi.unit_price), 2) AS avg_price
FROM order_items oi
JOIN albums a ON oi.album_id = a.album_id
LEFT JOIN genres g ON a.genre_id = g.genre_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY g.name
ORDER BY revenue DESC;

-- =====================================================
-- AI & ANALYTICS QUERIES
-- =====================================================

-- Get pending AI recommendations
SELECT
    recommendation_type,
    recommendation,
    insight,
    confidence_score,
    impact,
    created_at
FROM ai_recommendations
WHERE status = 'pending'
  AND (expires_at IS NULL OR expires_at > NOW())
ORDER BY confidence_score DESC, created_at DESC;

-- Get demand forecasts for next 7 days
SELECT
    a.sku,
    a.title,
    df.forecast_date,
    df.predicted_demand,
    df.lower_bound,
    df.upper_bound,
    df.confidence_level
FROM demand_forecasts df
JOIN albums a ON df.album_id = a.album_id
WHERE df.forecast_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
ORDER BY df.forecast_date, df.predicted_demand DESC;

-- Get reorder queue with supplier info
SELECT
    a.sku,
    a.title,
    rq.current_stock,
    rq.recommended_quantity,
    rq.unit_cost,
    rq.total_cost,
    rq.priority,
    rq.ai_confidence,
    s.name AS supplier
FROM reorder_queue rq
JOIN albums a ON rq.album_id = a.album_id
LEFT JOIN suppliers s ON rq.supplier_id = s.supplier_id
WHERE rq.status = 'pending'
ORDER BY
    CASE rq.priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        ELSE 4
    END,
    rq.ai_confidence DESC;

-- =====================================================
-- CUSTOMER SERVICE QUERIES
-- =====================================================

-- Get open cases with customer info
SELECT
    cs.case_number,
    c.first_name,
    c.last_name,
    c.email,
    cs.subject,
    cs.category,
    cs.priority,
    cs.status,
    cs.ai_sentiment,
    cs.created_at,
    u.first_name AS assigned_to_first_name,
    u.last_name AS assigned_to_last_name
FROM cases cs
JOIN customers c ON cs.customer_id = c.customer_id
LEFT JOIN users u ON cs.assigned_to = u.user_id
WHERE cs.status IN ('pending', 'in_progress')
ORDER BY
    CASE cs.priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        ELSE 4
    END,
    cs.created_at ASC;

-- Get average case resolution time
SELECT
    category,
    COUNT(*) AS total_cases,
    ROUND(AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600), 2) AS avg_hours_to_resolve
FROM cases
WHERE resolved_at IS NOT NULL
  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY category
ORDER BY avg_hours_to_resolve ASC;

-- =====================================================
-- WORKFLOW QUERIES
-- =====================================================

-- Get workflow performance summary
SELECT
    name,
    enabled,
    execution_count,
    success_count,
    failure_count,
    success_rate,
    avg_duration_ms,
    last_execution_at
FROM workflows
ORDER BY execution_count DESC;

-- Get recent workflow executions
SELECT
    w.name AS workflow_name,
    we.execution_number,
    we.status,
    we.progress_percentage,
    we.start_time,
    we.end_time,
    we.duration_ms,
    we.error_message
FROM workflow_executions we
JOIN workflows w ON we.workflow_id = w.workflow_id
WHERE we.start_time >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY we.start_time DESC
LIMIT 50;

-- Get workflow failure analysis
SELECT
    w.name AS workflow_name,
    COUNT(*) AS failure_count,
    ARRAY_AGG(DISTINCT we.error_message) AS error_messages
FROM workflow_executions we
JOIN workflows w ON we.workflow_id = w.workflow_id
WHERE we.status = 'error'
  AND we.start_time >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY w.name
ORDER BY failure_count DESC;

-- =====================================================
-- REPORTING QUERIES
-- =====================================================

-- Monthly revenue report
SELECT
    DATE_TRUNC('month', order_date) AS month,
    COUNT(order_id) AS total_orders,
    SUM(total) AS total_revenue,
    ROUND(AVG(total), 2) AS avg_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month DESC;

-- Customer retention cohort
SELECT
    DATE_TRUNC('month', c.date_joined) AS cohort_month,
    COUNT(DISTINCT c.customer_id) AS cohort_size,
    COUNT(DISTINCT CASE
        WHEN o.order_date >= DATE_TRUNC('month', c.date_joined) + INTERVAL '1 month'
        THEN c.customer_id
    END) AS retained_month_1,
    COUNT(DISTINCT CASE
        WHEN o.order_date >= DATE_TRUNC('month', c.date_joined) + INTERVAL '2 months'
        THEN c.customer_id
    END) AS retained_month_2,
    COUNT(DISTINCT CASE
        WHEN o.order_date >= DATE_TRUNC('month', c.date_joined) + INTERVAL '3 months'
        THEN c.customer_id
    END) AS retained_month_3
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.date_joined >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY DATE_TRUNC('month', c.date_joined)
ORDER BY cohort_month DESC;

-- Product performance report
SELECT
    a.sku,
    a.title,
    a.artist,
    g.name AS genre,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.total) AS revenue,
    SUM(oi.total - (a.cost * oi.quantity)) AS profit,
    ROUND((SUM(oi.total - (a.cost * oi.quantity)) / SUM(oi.total) * 100), 2) AS margin_percentage,
    COUNT(DISTINCT o.customer_id) AS unique_customers
FROM albums a
JOIN order_items oi ON a.album_id = oi.album_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN genres g ON a.genre_id = g.genre_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY a.sku, a.title, a.artist, g.name, a.cost
ORDER BY revenue DESC
LIMIT 20;

-- =====================================================
-- UTILITY QUERIES
-- =====================================================

-- Check database size
SELECT
    pg_size_pretty(pg_database_size(current_database())) AS database_size;

-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check slow queries (requires pg_stat_statements extension)
-- SELECT
--     query,
--     calls,
--     total_time,
--     mean_time,
--     max_time
-- FROM pg_stat_statements
-- ORDER BY mean_time DESC
-- LIMIT 10;
