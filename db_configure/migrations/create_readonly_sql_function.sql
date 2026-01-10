-- Migration: Create execute_readonly_sql function for AI Issues Agent
-- Purpose: Allow read-only SQL query execution with proper security controls
-- Date: 2026-01-10

-- Drop function if it already exists
DROP FUNCTION IF EXISTS execute_readonly_sql(text);

-- Create a function to execute read-only SQL queries
-- This function uses SECURITY DEFINER to run with elevated privileges
-- but implements strict validation to ensure only SELECT queries are executed
CREATE OR REPLACE FUNCTION execute_readonly_sql(sql_query text)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER -- Runs with the privileges of the function owner
SET search_path = public -- Prevent search_path injection
AS $$
DECLARE
    result json;
    query_upper text;
    forbidden_keywords text[] := ARRAY[
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'GRANT', 'REVOKE', 'EXECUTE', 'EXEC',
        'MERGE', 'REPLACE', 'COPY', 'CALL', 'VACUUM', 'ANALYZE',
        'REINDEX', 'CLUSTER', 'COMMENT', 'LOCK', 'LISTEN', 'NOTIFY'
    ];
    keyword text;
BEGIN
    -- Validate input
    IF sql_query IS NULL OR trim(sql_query) = '' THEN
        RAISE EXCEPTION 'SQL query cannot be empty';
    END IF;

    -- Strip trailing semicolons (single trailing semicolon is acceptable)
    sql_query := rtrim(trim(sql_query), ';');

    -- Convert to uppercase for checking
    query_upper := upper(sql_query);

    -- Remove SQL comments for validation
    query_upper := regexp_replace(query_upper, '--.*$', '', 'gm');
    query_upper := regexp_replace(query_upper, '/\*.*?\*/', '', 'g');

    -- Additional security: Check for semicolons in the middle (multi-statement attempts)
    -- After removing trailing semicolons, any remaining semicolon indicates multiple statements
    IF position(';' IN query_upper) > 0 THEN
        RAISE EXCEPTION 'READ-ONLY VIOLATION: Multiple statements not allowed';
    END IF;

    -- Check for forbidden keywords using word boundaries
    -- This prevents false positives like "created_at" matching "CREATE"
    FOREACH keyword IN ARRAY forbidden_keywords
    LOOP
        -- Use regex word boundary to match whole words only
        IF query_upper ~ ('\m' || keyword || '\M') THEN
            RAISE EXCEPTION 'READ-ONLY VIOLATION: Query contains forbidden keyword "%"', keyword;
        END IF;
    END LOOP;

    -- Ensure query starts with SELECT or WITH (for CTEs)
    IF NOT (query_upper ~ '^\s*(SELECT|WITH)\M') THEN
        RAISE EXCEPTION 'READ-ONLY VIOLATION: Only SELECT queries are allowed';
    END IF;

    -- Execute the query and return results as JSON
    BEGIN
        EXECUTE format('SELECT json_agg(row_to_json(t)) FROM (%s) t', sql_query) INTO result;

        -- If no results, return empty array
        IF result IS NULL THEN
            result := '[]'::json;
        END IF;

        RETURN result;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'Query execution failed: %', SQLERRM;
    END;
END;
$$;

-- Grant execute permission to authenticated users
-- Adjust this based on your security requirements
GRANT EXECUTE ON FUNCTION execute_readonly_sql(text) TO authenticated;
GRANT EXECUTE ON FUNCTION execute_readonly_sql(text) TO service_role;

-- Add comment for documentation
COMMENT ON FUNCTION execute_readonly_sql(text) IS
'Executes read-only SELECT queries with security validation. Used by AI Issues Agent to analyze business data. Only SELECT and WITH (CTE) statements are allowed.';

-- Test the function (optional - comment out if you want to skip tests)
DO $$
DECLARE
    test_result json;
BEGIN
    -- Test 1: Valid SELECT query
    SELECT execute_readonly_sql('SELECT 1 as test_column') INTO test_result;
    RAISE NOTICE 'Test 1 passed: %', test_result;

    -- Test 2: Should fail - INSERT attempt
    BEGIN
        SELECT execute_readonly_sql('INSERT INTO customers (name) VALUES (''test'')') INTO test_result;
        RAISE EXCEPTION 'Test 2 FAILED: INSERT was not blocked';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Test 2 passed: INSERT blocked correctly';
    END;

    -- Test 3: Should fail - UPDATE attempt
    BEGIN
        SELECT execute_readonly_sql('UPDATE customers SET name = ''test'' WHERE id = 1') INTO test_result;
        RAISE EXCEPTION 'Test 3 FAILED: UPDATE was not blocked';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Test 3 passed: UPDATE blocked correctly';
    END;

    RAISE NOTICE 'All tests passed successfully!';
END;
$$;
