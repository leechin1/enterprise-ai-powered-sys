-- Setup script for RAG with Supabase pgvector
-- Run this in Supabase SQL Editor to enable vector search

-- 1. Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the document embeddings table
CREATE TABLE IF NOT EXISTS document_embeddings (
    id BIGSERIAL PRIMARY KEY,
    document_name TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),  -- Google text-embedding-004 uses 768 dimensions
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint to prevent duplicate chunks
    UNIQUE(document_name, chunk_index)
);

-- 3. Create an index for fast similarity search
CREATE INDEX IF NOT EXISTS document_embeddings_embedding_idx
ON document_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. Create index on document name for filtering
CREATE INDEX IF NOT EXISTS document_embeddings_document_name_idx
ON document_embeddings(document_name);

-- 5. Create a function to search for similar documents
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(768),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    document_name TEXT,
    chunk_index INTEGER,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        de.id,
        de.document_name,
        de.chunk_index,
        de.content,
        de.metadata,
        1 - (de.embedding <=> query_embedding) AS similarity
    FROM document_embeddings de
    WHERE 1 - (de.embedding <=> query_embedding) > match_threshold
    ORDER BY de.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 6. Create a function to upsert document chunks
CREATE OR REPLACE FUNCTION upsert_document_chunk(
    p_document_name TEXT,
    p_chunk_index INTEGER,
    p_content TEXT,
    p_embedding vector(768),
    p_metadata JSONB DEFAULT '{}'
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    result_id BIGINT;
BEGIN
    INSERT INTO document_embeddings (document_name, chunk_index, content, embedding, metadata)
    VALUES (p_document_name, p_chunk_index, p_content, p_embedding, p_metadata)
    ON CONFLICT (document_name, chunk_index)
    DO UPDATE SET
        content = EXCLUDED.content,
        embedding = EXCLUDED.embedding,
        metadata = EXCLUDED.metadata,
        updated_at = NOW()
    RETURNING id INTO result_id;

    RETURN result_id;
END;
$$;

-- 7. Create a view to see document statistics
CREATE OR REPLACE VIEW document_stats AS
SELECT
    document_name,
    COUNT(*) as chunk_count,
    MIN(created_at) as first_indexed,
    MAX(updated_at) as last_updated
FROM document_embeddings
GROUP BY document_name
ORDER BY document_name;

-- 8. Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE ON document_embeddings TO authenticated;
-- GRANT EXECUTE ON FUNCTION match_documents TO authenticated;
-- GRANT EXECUTE ON FUNCTION upsert_document_chunk TO authenticated;

-- Verification query (run after setup)
-- SELECT * FROM document_stats;
