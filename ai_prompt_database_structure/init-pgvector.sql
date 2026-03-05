-- Initialize pgvector extension for ValidoAI
-- This script runs automatically when the PostgreSQL container starts

-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

SELECT extname,extrelocatable,extversion FROM pg_extension where extname='vector'

-- Enable other useful extensions
-- Enable pgvector, pgcrypto, and plpython3u extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS plpython3u;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;
CREATE EXTENSION IF NOT EXISTS citus;

-- Test pgvector
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));
INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;

-- Test pgcrypto
SELECT gen_random_uuid();
SELECT crypt('password', gen_salt('bf'));

-- Test plpython3u
CREATE FUNCTION python_test() RETURNS text AS $$
return "Hello from Python " + str(plpy.info.__version__)
$$ LANGUAGE plpython3u;
SELECT python_test();

-- List all available extensions
SELECT name, default_version, comment FROM pg_available_extensions ORDER BY name;

-- Create a test table to verify vector extension works
CREATE TABLE IF NOT EXISTS test_vectors (
    id SERIAL PRIMARY KEY,
    embedding VECTOR(3),
    description TEXT
);

-- Insert a test vector
INSERT INTO test_vectors (embedding, description) 
VALUES ('[1,2,3]'::vector, 'Test vector for pgvector verification')
ON CONFLICT DO NOTHING;

-- Create HNSW index for similarity search
CREATE INDEX IF NOT EXISTS test_vectors_hnsw_idx 
ON test_vectors USING hnsw (embedding vector_cosine_ops);

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'pgvector extension initialized successfully for ValidoAI';
    RAISE NOTICE 'Vector extension version: %', (SELECT extversion FROM pg_extension WHERE extname = 'vector');
END $$;
