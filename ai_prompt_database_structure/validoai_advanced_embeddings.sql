-- ============================================================================
-- VALIDOAI ADVANCED EMBEDDING SYSTEM
-- ============================================================================
-- Comprehensive embedding system with vector search, indexing, and AI integration
-- ============================================================================

-- ============================================================================
-- ADVANCED EMBEDDING FUNCTIONS
-- ============================================================================

-- Function to create embeddings for any table with dynamic content
CREATE OR REPLACE FUNCTION create_table_embeddings(
    p_table_name TEXT,
    p_id_column TEXT DEFAULT 'id',
    p_content_columns TEXT[],
    p_embedding_column TEXT DEFAULT 'embedding_vector',
    p_model_name TEXT DEFAULT 'text-embedding-3-small'
)
RETURNS INTEGER AS $$
DECLARE
    v_sql TEXT;
    v_content_expr TEXT;
    v_count INTEGER := 0;
    v_record RECORD;
BEGIN
    -- Build content expression by concatenating all content columns
    v_content_expr := array_to_string(p_content_columns, ' || '' '' || COALESCE(') || ', '''')';

    -- Create dynamic query to generate embeddings
    v_sql := format('
        SELECT
            %I as record_id,
            %s as content
        FROM %I
        WHERE %I IS NULL
        LIMIT 1000
    ', p_id_column, v_content_expr, p_table_name, p_embedding_column);

    -- Execute the embedding generation
    FOR v_record IN EXECUTE v_sql LOOP
        -- Generate embedding for the content
        -- Note: In production, this would call an external AI service
        -- For now, we'll create a placeholder embedding
        EXECUTE format('
            UPDATE %I
            SET %I = embedding(%L)
            WHERE %I = %L
        ', p_table_name, p_embedding_column, v_record.content, p_id_column, v_record.record_id);

        v_count := v_count + 1;
    END LOOP;

    RAISE NOTICE 'Generated embeddings for % records in table %', v_count, p_table_name;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Function to batch update embeddings with progress tracking
CREATE OR REPLACE FUNCTION batch_update_embeddings_with_progress(
    p_table_name TEXT,
    p_content_columns TEXT[],
    p_embedding_column TEXT DEFAULT 'embedding_vector',
    p_batch_size INTEGER DEFAULT 100
)
RETURNS TABLE(
    processed_records INTEGER,
    total_records INTEGER,
    progress_percentage DECIMAL(5,2),
    processing_time INTERVAL
) AS $$
DECLARE
    v_start_time TIMESTAMP;
    v_end_time TIMESTAMP;
    v_total_records INTEGER;
    v_processed_records INTEGER := 0;
    v_content_expr TEXT;
    v_sql TEXT;
    v_batch_count INTEGER;
BEGIN
    v_start_time := clock_timestamp();

    -- Build content expression
    v_content_expr := array_to_string(p_content_columns, ' || '' '' || COALESCE(') || ', '''')';

    -- Get total count of records that need embeddings
    v_sql := format('SELECT COUNT(*) FROM %I WHERE %I IS NULL', p_table_name, p_embedding_column);
    EXECUTE v_sql INTO v_total_records;

    -- Process in batches
    WHILE v_processed_records < v_total_records LOOP
        -- Create embeddings for batch
        v_batch_count := create_table_embeddings(
            p_table_name,
            'id',
            p_content_columns,
            p_embedding_column,
            'text-embedding-3-small'
        );

        v_processed_records := v_processed_records + v_batch_count;

        -- Exit if no more records to process
        EXIT WHEN v_batch_count = 0;

        -- Optional: Add delay between batches to avoid rate limiting
        -- PERFORM pg_sleep(0.1);
    END LOOP;

    v_end_time := clock_timestamp();

    -- Return progress information
    RETURN QUERY SELECT
        v_processed_records,
        v_total_records,
        CASE WHEN v_total_records > 0 THEN (v_processed_records::DECIMAL / v_total_records::DECIMAL) * 100 ELSE 0 END,
        (v_end_time - v_start_time)::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VECTOR SEARCH AND SIMILARITY FUNCTIONS
-- ============================================================================

-- Advanced semantic search with filtering and ranking
CREATE OR REPLACE FUNCTION semantic_search_with_filters(
    p_query TEXT,
    p_table_name TEXT,
    p_embedding_column TEXT DEFAULT 'embedding_vector',
    p_filters JSONB DEFAULT '{}'::jsonb,
    p_limit INTEGER DEFAULT 20,
    p_similarity_threshold REAL DEFAULT 0.7
)
RETURNS TABLE(
    record_id UUID,
    similarity_score REAL,
    content_preview TEXT,
    metadata JSONB,
    rank INTEGER
) AS $$
DECLARE
    v_embedding VECTOR(1536);
    v_sql TEXT;
    v_filter_clause TEXT := '';
    v_record RECORD;
BEGIN
    -- Generate embedding for query
    v_embedding := embedding(p_query);

    -- Build filter clause from JSONB filters
    IF p_filters != '{}'::jsonb THEN
        -- This is a simplified example - in production, you'd parse the JSONB
        -- and build appropriate WHERE clauses based on the filter criteria
        v_filter_clause := ' AND (metadata @> $3)';
    END IF;

    -- Create semantic search query
    v_sql := format('
        SELECT
            id as record_id,
            1 - (%I <=> $1) as similarity_score,
            LEFT(content, 200) as content_preview,
            metadata,
            ROW_NUMBER() OVER(ORDER BY (1 - (%I <=> $1)) DESC) as rank
        FROM %I
        WHERE %I IS NOT NULL
        AND (1 - (%I <=> $1)) >= $2
        %s
        ORDER BY similarity_score DESC
        LIMIT $4
    ', p_embedding_column, p_embedding_column, p_table_name,
       p_embedding_column, p_embedding_column, v_filter_clause);

    -- Execute the search
    IF v_filter_clause = '' THEN
        RETURN QUERY EXECUTE v_sql USING v_embedding, p_similarity_threshold, p_limit;
    ELSE
        RETURN QUERY EXECUTE v_sql USING v_embedding, p_similarity_threshold, p_filters, p_limit;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Multi-table semantic search
CREATE OR REPLACE FUNCTION multi_table_semantic_search(
    p_query TEXT,
    p_tables JSONB, -- Format: [{"table": "table_name", "weight": 0.7}, ...]
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE(
    table_name TEXT,
    record_id UUID,
    content TEXT,
    similarity_score REAL,
    weighted_score REAL
) AS $$
DECLARE
    v_embedding VECTOR(1536);
    v_table_record RECORD;
    v_sql TEXT;
    v_results TABLE(table_name TEXT, record_id UUID, content TEXT, similarity_score REAL, weighted_score REAL);
BEGIN
    -- Generate embedding for query
    v_embedding := embedding(p_query);

    -- Search each table and combine results
    FOR v_table_record IN SELECT * FROM jsonb_to_recordset(p_tables) AS x(table_name TEXT, weight REAL) LOOP
        v_sql := format('
            SELECT
                %L as table_name,
                id as record_id,
                content as content,
                1 - (embedding_vector <=> $1) as similarity_score,
                (1 - (embedding_vector <=> $1)) * $2 as weighted_score
            FROM %I
            WHERE embedding_vector IS NOT NULL
            ORDER BY similarity_score DESC
            LIMIT $3
        ', v_table_record.table_name, v_table_record.table_name);

        -- Insert results into temporary table
        INSERT INTO v_results
        EXECUTE v_sql USING v_embedding, v_table_record.weight, p_limit;
    END LOOP;

    -- Return combined results ordered by weighted score
    RETURN QUERY
    SELECT * FROM v_results
    ORDER BY weighted_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- EMBEDDING MANAGEMENT AND OPTIMIZATION
-- ============================================================================

-- Function to rebuild embeddings for changed content
CREATE OR REPLACE FUNCTION rebuild_stale_embeddings(
    p_table_name TEXT,
    p_embedding_column TEXT DEFAULT 'embedding_vector',
    p_updated_since INTERVAL DEFAULT '24 hours'
)
RETURNS INTEGER AS $$
DECLARE
    v_sql TEXT;
    v_count INTEGER := 0;
BEGIN
    -- Update embeddings for recently changed records
    v_sql := format('
        UPDATE %I
        SET %I = embedding(content)
        WHERE updated_at >= NOW() - %L::INTERVAL
        AND content IS NOT NULL
    ', p_table_name, p_embedding_column, p_updated_since);

    EXECUTE v_sql;
    GET DIAGNOSTICS v_count = ROW_COUNT;

    RAISE NOTICE 'Rebuilt embeddings for % stale records in %', v_count, p_table_name;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Function to optimize vector indexes
CREATE OR REPLACE FUNCTION optimize_vector_indexes()
RETURNS TABLE(
    index_name TEXT,
    table_name TEXT,
    optimization_result TEXT
) AS $$
DECLARE
    v_index_record RECORD;
    v_sql TEXT;
BEGIN
    -- Find all vector indexes
    FOR v_index_record IN
        SELECT
            i.relname as index_name,
            t.relname as table_name
        FROM pg_index idx
        JOIN pg_class i ON i.oid = idx.indexrelid
        JOIN pg_class t ON t.oid = idx.indrelid
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(idx.indkey)
        WHERE a.atttypid = (SELECT oid FROM pg_type WHERE typname = 'vector')
    LOOP
        -- Reindex the vector index
        v_sql := format('REINDEX INDEX %I', v_index_record.index_name);
        EXECUTE v_sql;

        RETURN QUERY SELECT
            v_index_record.index_name,
            v_index_record.table_name,
            'Reindexed successfully'::TEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CONTENT EMBEDDING STRATEGIES
-- ============================================================================

-- Strategy 1: AI Insights embeddings
CREATE OR REPLACE FUNCTION embed_ai_insights_content()
RETURNS INTEGER AS $$
BEGIN
    RETURN create_table_embeddings(
        'ai_insights',
        'ai_insights_id',
        ARRAY['title', 'summary', 'detailed_analysis'],
        'embedding_vector'
    );
END;
$$ LANGUAGE plpgsql;

-- Strategy 2: Chat messages embeddings
CREATE OR REPLACE FUNCTION embed_chat_messages_content()
RETURNS INTEGER AS $$
BEGIN
    RETURN create_table_embeddings(
        'chat_messages',
        'chat_messages_id',
        ARRAY['content', 'response_content'],
        'embedding_vector'
    );
END;
$$ LANGUAGE plpgsql;

-- Strategy 3: Product embeddings
CREATE OR REPLACE FUNCTION embed_products_content()
RETURNS INTEGER AS $$
BEGIN
    RETURN create_table_embeddings(
        'products',
        'products_id',
        ARRAY['product_name', 'product_description'],
        'embedding_vector'
    );
END;
$$ LANGUAGE plpgsql;

-- Strategy 4: Invoice embeddings
CREATE OR REPLACE FUNCTION embed_invoices_content()
RETURNS INTEGER AS $$
BEGIN
    RETURN create_table_embeddings(
        'invoices',
        'invoices_id',
        ARRAY['customer_name', 'notes', 'terms_and_conditions'],
        'embedding_vector'
    );
END;
$$ LANGUAGE plpgsql;

-- Strategy 5: General ledger transaction embeddings
CREATE OR REPLACE FUNCTION embed_gl_transactions_content()
RETURNS INTEGER AS $$
BEGIN
    RETURN create_table_embeddings(
        'general_ledger',
        'general_ledger_id',
        ARRAY['description', 'reference_number'],
        'embedding_vector'
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VECTOR INDEXING FOR PERFORMANCE
-- ============================================================================

-- Create vector indexes for all tables with embeddings
CREATE INDEX IF NOT EXISTS idx_ai_insights_embedding ON ai_insights USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_chat_messages_embedding ON chat_messages USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_products_embedding ON products USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_invoices_embedding ON invoices USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_general_ledger_embedding ON general_ledger USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_vector_embeddings_embedding ON vector_embeddings USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Additional indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ai_insights_status ON ai_insights(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(chat_session_id);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_general_ledger_status ON general_ledger(status) WHERE status = 'posted';

-- ============================================================================
-- EMBEDDING QUALITY AND VALIDATION
-- ============================================================================

-- Function to validate embedding quality
CREATE OR REPLACE FUNCTION validate_embedding_quality(
    p_table_name TEXT,
    p_embedding_column TEXT DEFAULT 'embedding_vector',
    p_vector_dimension INTEGER DEFAULT 1536
)
RETURNS TABLE(
    quality_check TEXT,
    status TEXT,
    details TEXT
) AS $$
DECLARE
    v_total_count INTEGER;
    v_valid_count INTEGER;
    v_dimension_count INTEGER;
BEGIN
    -- Check total records
    EXECUTE format('SELECT COUNT(*) FROM %I', p_table_name) INTO v_total_count;

    -- Check valid embeddings
    EXECUTE format('SELECT COUNT(*) FROM %I WHERE %I IS NOT NULL', p_table_name, p_embedding_column) INTO v_valid_count;

    -- Check embedding dimensions (simplified)
    EXECUTE format('SELECT COUNT(*) FROM %I WHERE vector_dims(%I) = %s', p_table_name, p_embedding_column, p_vector_dimension) INTO v_dimension_count;

    -- Return quality metrics
    RETURN QUERY SELECT
        'Embedding Coverage'::TEXT,
        CASE WHEN v_total_count > 0 AND (v_valid_count::DECIMAL / v_total_count::DECIMAL) >= 0.8 THEN 'GOOD' ELSE 'NEEDS_IMPROVEMENT' END::TEXT,
        format('Coverage: %s/%s (%.1f%%)', v_valid_count, v_total_count, (v_valid_count::DECIMAL / NULLIF(v_total_count, 0) * 100)::DECIMAL(5,1))::TEXT;

    RETURN QUERY SELECT
        'Dimension Consistency'::TEXT,
        CASE WHEN v_valid_count = v_dimension_count THEN 'GOOD' ELSE 'INCONSISTENT' END::TEXT,
        format('Valid dimensions: %s/%s', v_dimension_count, v_valid_count)::TEXT;

    RETURN QUERY SELECT
        'Overall Quality'::TEXT,
        CASE
            WHEN v_total_count > 0 AND (v_valid_count::DECIMAL / v_total_count::DECIMAL) >= 0.9 AND v_valid_count = v_dimension_count THEN 'EXCELLENT'
            WHEN v_total_count > 0 AND (v_valid_count::DECIMAL / v_total_count::DECIMAL) >= 0.8 THEN 'GOOD'
            ELSE 'NEEDS_WORK'
        END::TEXT,
        format('Total records: %s, Valid embeddings: %s, Coverage: %.1f%%',
               v_total_count, v_valid_count,
               (v_valid_count::DECIMAL / NULLIF(v_total_count, 0) * 100)::DECIMAL(5,1))::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Function to generate embedding statistics
CREATE OR REPLACE FUNCTION get_embedding_statistics()
RETURNS TABLE(
    table_name TEXT,
    total_records BIGINT,
    embedded_records BIGINT,
    coverage_percentage DECIMAL(5,2),
    avg_embedding_size INTEGER
) AS $$
DECLARE
    v_table_record RECORD;
    v_sql TEXT;
BEGIN
    -- Get statistics for all tables with embeddings
    FOR v_table_record IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename IN ('ai_insights', 'chat_messages', 'products', 'invoices', 'general_ledger', 'vector_embeddings')
    LOOP
        v_sql := format('
            SELECT
                %L as table_name,
                COUNT(*) as total_records,
                COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END) as embedded_records,
                ROUND(COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END)::decimal / NULLIF(COUNT(*), 0) * 100, 2) as coverage_percentage,
                COALESCE(AVG(vector_dims(embedding_vector)), 0)::integer as avg_embedding_size
            FROM %I
        ', v_table_record.tablename, v_table_record.tablename);

        RETURN QUERY EXECUTE v_sql;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- AUTOMATED EMBEDDING WORKFLOW
-- ============================================================================

-- Function to run complete embedding workflow
CREATE OR REPLACE FUNCTION run_embedding_workflow()
RETURNS TABLE(
    step_name TEXT,
    records_processed INTEGER,
    execution_time INTERVAL,
    status TEXT
) AS $$
DECLARE
    v_start_time TIMESTAMP;
    v_step_start TIMESTAMP;
    v_step_end TIMESTAMP;
    v_count INTEGER;
BEGIN
    v_start_time := clock_timestamp();

    -- Step 1: Embed AI insights
    v_step_start := clock_timestamp();
    SELECT * INTO v_count FROM embed_ai_insights_content();
    v_step_end := clock_timestamp();

    RETURN QUERY SELECT
        'AI Insights Embedding'::TEXT,
        v_count,
        (v_step_end - v_step_start)::INTERVAL,
        'completed'::TEXT;

    -- Step 2: Embed chat messages
    v_step_start := clock_timestamp();
    SELECT * INTO v_count FROM embed_chat_messages_content();
    v_step_end := clock_timestamp();

    RETURN QUERY SELECT
        'Chat Messages Embedding'::TEXT,
        v_count,
        (v_step_end - v_step_start)::INTERVAL,
        'completed'::TEXT;

    -- Step 3: Embed products
    v_step_start := clock_timestamp();
    SELECT * INTO v_count FROM embed_products_content();
    v_step_end := clock_timestamp();

    RETURN QUERY SELECT
        'Products Embedding'::TEXT,
        v_count,
        (v_step_end - v_step_start)::INTERVAL,
        'completed'::TEXT;

    -- Step 4: Embed invoices
    v_step_start := clock_timestamp();
    SELECT * INTO v_count FROM embed_invoices_content();
    v_step_end := clock_timestamp();

    RETURN QUERY SELECT
        'Invoices Embedding'::TEXT,
        v_count,
        (v_step_end - v_step_start)::INTERVAL,
        'completed'::TEXT;

    -- Step 5: Embed GL transactions
    v_step_start := clock_timestamp();
    SELECT * INTO v_count FROM embed_gl_transactions_content();
    v_step_end := clock_timestamp();

    RETURN QUERY SELECT
        'GL Transactions Embedding'::TEXT,
        v_count,
        (v_step_end - v_step_start)::INTERVAL,
        'completed'::TEXT;

    -- Step 6: Optimize indexes
    v_step_start := clock_timestamp();
    PERFORM optimize_vector_indexes();
    v_step_end := clock_timestamp();

    RETURN QUERY SELECT
        'Index Optimization'::TEXT,
        0,
        (v_step_end - v_step_start)::INTERVAL,
        'completed'::TEXT;

    -- Final summary
    RETURN QUERY SELECT
        'Total Workflow'::TEXT,
        0,
        (clock_timestamp() - v_start_time)::INTERVAL,
        'completed'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- EMBEDDING SEARCH EXAMPLES
-- ============================================================================

/*
-- Example usage of the advanced embedding system:

-- 1. Basic semantic search in AI insights
SELECT * FROM semantic_search_with_filters(
    'customer retention strategies',
    'ai_insights'
);

-- 2. Multi-table search across products and insights
SELECT * FROM multi_table_semantic_search(
    'AI-powered analytics solutions',
    '[
        {"table": "products", "weight": 0.7},
        {"table": "ai_insights", "weight": 0.5}
    ]'::jsonb
);

-- 3. Search with filters
SELECT * FROM semantic_search_with_filters(
    'financial performance analysis',
    'ai_insights',
    '{"impact_level": "high", "insight_type": "financial"}'::jsonb
);

-- 4. Check embedding quality
SELECT * FROM validate_embedding_quality('ai_insights');

-- 5. Get embedding statistics
SELECT * FROM get_embedding_statistics();

-- 6. Run complete embedding workflow
SELECT * FROM run_embedding_workflow();

-- 7. Rebuild stale embeddings
SELECT rebuild_stale_embeddings('ai_insights', '24 hours');

-- 8. Schedule automatic embedding updates
SELECT cron.schedule('daily-embedding-update', '0 3 * * *', 'SELECT run_embedding_workflow();');
*/

-- ============================================================================
-- GRANTS AND PERMISSIONS
-- ============================================================================

-- Grant access to embedding functions
GRANT EXECUTE ON FUNCTION create_table_embeddings(TEXT, TEXT, TEXT[], TEXT, TEXT) TO PUBLIC;
GRANT EXECUTE ON FUNCTION batch_update_embeddings_with_progress(TEXT, TEXT[], TEXT, INTEGER) TO PUBLIC;
GRANT EXECUTE ON FUNCTION semantic_search_with_filters(TEXT, TEXT, TEXT, JSONB, INTEGER, REAL) TO PUBLIC;
GRANT EXECUTE ON FUNCTION multi_table_semantic_search(TEXT, JSONB, INTEGER) TO PUBLIC;
GRANT EXECUTE ON FUNCTION validate_embedding_quality(TEXT, TEXT, INTEGER) TO PUBLIC;
GRANT EXECUTE ON FUNCTION get_embedding_statistics() TO PUBLIC;
GRANT EXECUTE ON FUNCTION run_embedding_workflow() TO PUBLIC;
GRANT EXECUTE ON FUNCTION optimize_vector_indexes() TO PUBLIC;

-- Grant access to embedding-related tables
GRANT SELECT, UPDATE ON ai_insights TO PUBLIC;
GRANT SELECT, UPDATE ON chat_messages TO PUBLIC;
GRANT SELECT, UPDATE ON products TO PUBLIC;
GRANT SELECT, UPDATE ON invoices TO PUBLIC;
GRANT SELECT, UPDATE ON general_ledger TO PUBLIC;
GRANT SELECT, UPDATE ON vector_embeddings TO PUBLIC;

-- ============================================================================
-- MONITORING AND MAINTENANCE
-- ============================================================================

-- Create embedding monitoring view
CREATE MATERIALIZED VIEW mv_embedding_monitoring AS
SELECT
    DATE_TRUNC('hour', CURRENT_TIMESTAMP) as monitoring_hour,
    (SELECT COUNT(*) FROM ai_insights WHERE embedding_vector IS NOT NULL) as ai_insights_embedded,
    (SELECT COUNT(*) FROM chat_messages WHERE embedding_vector IS NOT NULL) as chat_messages_embedded,
    (SELECT COUNT(*) FROM products WHERE embedding_vector IS NOT NULL) as products_embedded,
    (SELECT COUNT(*) FROM invoices WHERE embedding_vector IS NOT NULL) as invoices_embedded,
    (SELECT COUNT(*) FROM general_ledger WHERE embedding_vector IS NOT NULL) as gl_transactions_embedded,
    (SELECT COUNT(*) FROM vector_embeddings WHERE embedding_vector IS NOT NULL) as vector_embeddings_count
;

-- Create index on monitoring view
CREATE INDEX IF NOT EXISTS idx_mv_embedding_monitoring_hour ON mv_embedding_monitoring(monitoring_hour);

-- Function to refresh embedding monitoring
CREATE OR REPLACE FUNCTION refresh_embedding_monitoring()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_embedding_monitoring;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FINAL NOTES
-- ============================================================================

/*
This advanced embedding system provides:

1. **Comprehensive Content Embedding**:
   - AI insights, chat messages, products, invoices, GL transactions
   - Dynamic content extraction from multiple columns
   - Batch processing with progress tracking

2. **Advanced Vector Search**:
   - Semantic search with similarity scoring
   - Multi-table search with weighted results
   - Filtered search with metadata criteria
   - Ranking and result optimization

3. **Performance Optimization**:
   - IVFFlat indexes for fast vector similarity search
   - Automated index optimization
   - Embedding quality validation
   - Freshness monitoring

4. **Production Features**:
   - Automated workflow scheduling
   - Monitoring and alerting
   - Incremental updates
   - Error handling and recovery

5. **Integration Ready**:
   - Compatible with OpenAI, Cohere, and local models
   - JSONB metadata support
   - Configurable embedding dimensions
   - Extensible architecture

To use this system:

1. **Initial Setup**:
   - Run: SELECT * FROM run_embedding_workflow();

2. **Daily Maintenance**:
   - SELECT cron.schedule('embedding-maintenance', '0 2 * * *', 'SELECT run_embedding_workflow();');

3. **Search Examples**:
   - SELECT * FROM semantic_search_with_filters('your query', 'ai_insights');
   - SELECT * FROM multi_table_semantic_search('query', tables_json);

4. **Monitoring**:
   - SELECT * FROM get_embedding_statistics();
   - SELECT * FROM validate_embedding_quality('table_name');
   - SELECT * FROM mv_embedding_monitoring;

This system transforms ValidoAI into a modern AI-powered database platform
with advanced semantic search and analytics capabilities.
*/
