-- Migration: Create saved_queries table for storing AI-generated SQL queries
-- This table stores the queries generated during Stage 0 of the Issues & Problems analysis
-- so they can be reused without regenerating

-- Create the saved_queries table
CREATE TABLE IF NOT EXISTS saved_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    queries JSONB NOT NULL,  -- Array of query objects
    model VARCHAR(100),      -- Model used to generate queries
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add index for faster lookups by name
CREATE INDEX IF NOT EXISTS idx_saved_queries_name ON saved_queries(name);

-- Add index for ordering by creation date
CREATE INDEX IF NOT EXISTS idx_saved_queries_created_at ON saved_queries(created_at DESC);

-- Create trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_saved_queries_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_saved_queries_updated_at ON saved_queries;
CREATE TRIGGER trigger_saved_queries_updated_at
    BEFORE UPDATE ON saved_queries
    FOR EACH ROW
    EXECUTE FUNCTION update_saved_queries_updated_at();

-- Insert a default row for "last generated" queries (will be updated each time)
INSERT INTO saved_queries (name, description, queries, model)
VALUES (
    'last_generated',
    'Auto-saved queries from the most recent Stage 0 generation',
    '[]'::jsonb,
    'none'
)
ON CONFLICT DO NOTHING;

-- Grant permissions (adjust based on your Supabase setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON saved_queries TO authenticated;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON saved_queries TO service_role;

COMMENT ON TABLE saved_queries IS 'Stores AI-generated SQL queries for reuse in business issues analysis';
COMMENT ON COLUMN saved_queries.name IS 'Identifier for the query set (e.g., last_generated, custom_name)';
COMMENT ON COLUMN saved_queries.queries IS 'JSONB array of query objects with query_id, purpose, explanation, sql_query, priority';
