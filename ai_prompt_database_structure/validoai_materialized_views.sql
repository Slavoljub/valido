-- ============================================================================
-- VALIDOAI MATERIALIZED VIEWS
-- ============================================================================
-- This script creates comprehensive materialized views for analytics and reporting
-- Includes business intelligence, AI/ML analytics, and financial reporting views
-- ============================================================================

-- ============================================================================
-- BUSINESS INTELLIGENCE VIEWS
-- ============================================================================

-- Monthly sales performance
CREATE MATERIALIZED VIEW mv_monthly_sales AS
SELECT
    DATE_TRUNC('month', i.invoice_date) as month,
    c.company_name,
    COUNT(*) as invoice_count,
    SUM(i.total_amount) as total_revenue,
    AVG(i.total_amount) as avg_invoice_value,
    COUNT(CASE WHEN i.status = 'paid' THEN 1 END) as paid_invoices,
    COUNT(CASE WHEN i.status = 'overdue' THEN 1 END) as overdue_invoices
FROM invoices i
JOIN companies c ON i.company_id = c.companies_id
GROUP BY DATE_TRUNC('month', i.invoice_date), c.company_name;

-- Customer analytics and segmentation
CREATE MATERIALIZED VIEW mv_customer_analytics AS
SELECT
    COALESCE(i.customer_name, 'Unknown') as customer_name,
    COALESCE(i.customer_email, '') as customer_email,
    COUNT(*) as total_invoices,
    SUM(i.total_amount) as total_spent,
    AVG(i.total_amount) as avg_order_value,
    MAX(i.invoice_date) as last_purchase_date,
    MIN(i.invoice_date) as first_purchase_date,
    COUNT(CASE WHEN i.status = 'paid' THEN 1 END) as paid_invoices,
    COUNT(CASE WHEN i.status = 'overdue' THEN 1 END) as overdue_invoices,
    CASE
        WHEN MAX(i.invoice_date) > CURRENT_DATE - INTERVAL '30 days' THEN 'active'
        WHEN MAX(i.invoice_date) > CURRENT_DATE - INTERVAL '90 days' THEN 'recent'
        WHEN MAX(i.invoice_date) > CURRENT_DATE - INTERVAL '180 days' THEN 'inactive'
        ELSE 'lost'
    END as customer_status,
    CASE
        WHEN SUM(i.total_amount) >= 100000 THEN 'platinum'
        WHEN SUM(i.total_amount) >= 50000 THEN 'gold'
        WHEN SUM(i.total_amount) >= 10000 THEN 'silver'
        ELSE 'bronze'
    END as customer_segment
FROM invoices i
GROUP BY COALESCE(i.customer_name, 'Unknown'), COALESCE(i.customer_email, '');

-- Product performance analytics
CREATE MATERIALIZED VIEW mv_product_performance AS
SELECT
    p.product_code,
    p.product_name,
    p.product_type,
    c.company_name,
    COUNT(*) as total_sold,
    SUM(p.unit_price * COALESCE(p.stock_quantity, 0)) as total_revenue,
    AVG(p.unit_price) as avg_price,
    MAX(p.created_at) as last_sale_date,
    COUNT(CASE WHEN p.is_active = true THEN 1 END) as active_listings,
    CASE
        WHEN COUNT(*) >= 100 THEN 'high_performer'
        WHEN COUNT(*) >= 50 THEN 'medium_performer'
        WHEN COUNT(*) >= 10 THEN 'low_performer'
        ELSE 'new_product'
    END as performance_category
FROM products p
JOIN companies c ON p.company_id = c.companies_id
GROUP BY p.product_code, p.product_name, p.product_type, c.company_name;

-- ============================================================================
-- AI/ML ANALYTICS VIEWS
-- ============================================================================

-- AI insights performance summary
CREATE MATERIALIZED VIEW mv_ai_insights_performance AS
SELECT
    DATE_TRUNC('day', ai.created_at) as analysis_date,
    ai.insight_type,
    ai.impact_level,
    COUNT(*) as insight_count,
    AVG(ai.quality_score) as avg_quality_score,
    AVG(ai.usefulness_score) as avg_usefulness_score,
    AVG(ai.accuracy_verified::integer) as verification_rate,
    COUNT(CASE WHEN ai.impact_level = 'critical' THEN 1 END) as critical_insights,
    COUNT(CASE WHEN ai.impact_level = 'high' THEN 1 END) as high_impact_insights,
    COUNT(CASE WHEN ai.impact_level = 'medium' THEN 1 END) as medium_impact_insights,
    COUNT(CASE WHEN ai.impact_level = 'low' THEN 1 END) as low_impact_insights
FROM ai_insights ai
WHERE ai.status = 'active'
GROUP BY DATE_TRUNC('day', ai.created_at), ai.insight_type, ai.impact_level;

-- Chat conversation analytics
CREATE MATERIALIZED VIEW mv_chat_conversation_analytics AS
SELECT
    DATE_TRUNC('day', cs.created_at) as conversation_date,
    cs.session_type,
    COUNT(DISTINCT cs.chat_sessions_id) as total_sessions,
    COUNT(cm.chat_messages_id) as total_messages,
    AVG(cm.tokens_used) as avg_tokens_per_message,
    SUM(cm.tokens_used) as total_tokens_used,
    COUNT(CASE WHEN cm.message_type = 'user' THEN 1 END) as user_messages,
    COUNT(CASE WHEN cm.message_type = 'assistant' THEN 1 END) as assistant_messages,
    AVG(EXTRACT(EPOCH FROM (cm.created_at - LAG(cm.created_at) OVER (PARTITION BY cs.chat_sessions_id ORDER BY cm.created_at)))) as avg_response_time,
    COUNT(DISTINCT cs.user_id) as unique_users
FROM chat_sessions cs
LEFT JOIN chat_messages cm ON cs.chat_sessions_id = cm.chat_session_id
GROUP BY DATE_TRUNC('day', cs.created_at), cs.session_type;

-- AI model usage statistics
CREATE MATERIALIZED VIEW mv_ai_model_usage AS
SELECT
    DATE_TRUNC('hour', cm.created_at) as usage_hour,
    cm.model_used,
    COUNT(*) as total_requests,
    SUM(cm.tokens_used) as total_tokens,
    AVG(cm.tokens_used) as avg_tokens_per_request,
    COUNT(CASE WHEN cm.message_type = 'user' THEN 1 END) as user_queries,
    COUNT(CASE WHEN cm.message_type = 'assistant' THEN 1 END) as ai_responses,
    MAX(cm.tokens_used) as max_tokens_used,
    MIN(cm.tokens_used) as min_tokens_used
FROM chat_messages cm
WHERE cm.model_used IS NOT NULL
GROUP BY DATE_TRUNC('hour', cm.created_at), cm.model_used;

-- ============================================================================
-- FINANCIAL ANALYTICS VIEWS
-- ============================================================================

-- General ledger monthly summary
CREATE MATERIALIZED VIEW mv_general_ledger_monthly AS
SELECT
    DATE_TRUNC('month', gl.transaction_date) as transaction_month,
    c.company_name,
    coa.account_name,
    coa.account_type_id,
    COUNT(*) as transaction_count,
    SUM(gl.debit_amount) as total_debits,
    SUM(gl.credit_amount) as total_credits,
    SUM(gl.debit_amount - gl.credit_amount) as net_movement,
    AVG(gl.debit_amount + gl.credit_amount) as avg_transaction_value
FROM general_ledger gl
JOIN companies c ON gl.company_id = c.companies_id
JOIN chart_of_accounts coa ON gl.account_id = coa.chart_of_accounts_id
WHERE gl.status = 'posted'
GROUP BY DATE_TRUNC('month', gl.transaction_date), c.company_name, coa.account_name, coa.account_type_id;

-- Revenue recognition and analysis
CREATE MATERIALIZED VIEW mv_revenue_analysis AS
SELECT
    DATE_TRUNC('month', gl.transaction_date) as revenue_month,
    c.company_name,
    coa.account_name as revenue_account,
    SUM(gl.debit_amount - gl.credit_amount) as revenue_amount,
    COUNT(*) as revenue_transactions,
    AVG(gl.debit_amount - gl.credit_amount) as avg_revenue_per_transaction,
    SUM(CASE WHEN gl.debit_amount > 0 THEN gl.debit_amount END) as total_revenue_credits
FROM general_ledger gl
JOIN companies c ON gl.company_id = c.companies_id
JOIN chart_of_accounts coa ON gl.account_id = coa.chart_of_accounts_id
WHERE coa.account_name ILIKE '%revenue%' AND gl.status = 'posted'
GROUP BY DATE_TRUNC('month', gl.transaction_date), c.company_name, coa.account_name;

-- Expense analysis by category
CREATE MATERIALIZED VIEW mv_expense_analysis AS
SELECT
    DATE_TRUNC('month', gl.transaction_date) as expense_month,
    c.company_name,
    coa.account_name as expense_account,
    at.type_name as account_type,
    SUM(gl.credit_amount) as total_expenses,
    COUNT(*) as expense_transactions,
    AVG(gl.credit_amount) as avg_expense_per_transaction,
    SUM(gl.credit_amount) / NULLIF(COUNT(*), 0) as expense_efficiency
FROM general_ledger gl
JOIN companies c ON gl.company_id = c.companies_id
JOIN chart_of_accounts coa ON gl.account_id = coa.chart_of_accounts_id
JOIN account_types at ON coa.account_type_id = at.account_types_id
WHERE at.type_name IN ('expense', 'cost of goods sold') AND gl.status = 'posted'
GROUP BY DATE_TRUNC('month', gl.transaction_date), c.company_name, coa.account_name, at.type_name;

-- Cash flow analysis
CREATE MATERIALIZED VIEW mv_cash_flow_analysis AS
SELECT
    DATE_TRUNC('week', gl.transaction_date) as cash_flow_week,
    c.company_name,
    coa.account_name,
    SUM(CASE WHEN gl.debit_amount > gl.credit_amount THEN gl.debit_amount - gl.credit_amount END) as cash_inflow,
    SUM(CASE WHEN gl.credit_amount > gl.debit_amount THEN gl.credit_amount - gl.debit_amount END) as cash_outflow,
    SUM(gl.debit_amount - gl.credit_amount) as net_cash_flow,
    COUNT(*) as cash_transactions
FROM general_ledger gl
JOIN companies c ON gl.company_id = c.companies_id
JOIN chart_of_accounts coa ON gl.account_id = coa.chart_of_accounts_id
WHERE coa.account_name ILIKE '%cash%' AND gl.status = 'posted'
GROUP BY DATE_TRUNC('week', gl.transaction_date), c.company_name, coa.account_name;

-- ============================================================================
-- OPERATIONAL ANALYTICS VIEWS
-- ============================================================================

-- User activity and engagement
CREATE MATERIALIZED VIEW mv_user_activity_summary AS
SELECT
    DATE_TRUNC('day', u.last_login_at) as activity_date,
    COUNT(DISTINCT u.users_id) as active_users,
    COUNT(DISTINCT CASE WHEN u.email_verified_at IS NOT NULL THEN u.users_id END) as verified_users,
    COUNT(DISTINCT CASE WHEN u.is_active = true THEN u.users_id END) as enabled_users,
    AVG(EXTRACT(EPOCH FROM (u.last_login_at - u.created_at))/86400) as avg_days_since_registration,
    COUNT(CASE WHEN u.last_login_at > CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as weekly_active_users,
    COUNT(CASE WHEN u.last_login_at > CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as monthly_active_users
FROM users u
WHERE u.last_login_at IS NOT NULL
GROUP BY DATE_TRUNC('day', u.last_login_at);

-- System performance metrics
CREATE MATERIALIZED VIEW mv_system_performance AS
SELECT
    DATE_TRUNC('hour', pm.created_at) as metric_hour,
    pm.metric_name,
    AVG(pm.metric_value) as avg_value,
    MAX(pm.metric_value) as max_value,
    MIN(pm.metric_value) as min_value,
    COUNT(*) as measurement_count,
    STDDEV(pm.metric_value) as value_stddev
FROM performance_metrics pm
GROUP BY DATE_TRUNC('hour', pm.created_at), pm.metric_name;

-- Email campaign performance
CREATE MATERIALIZED VIEW mv_email_campaign_performance AS
SELECT
    ec.campaign_name,
    DATE_TRUNC('day', ec.created_at) as campaign_date,
    COUNT(ed.email_deliveries_id) as total_sent,
    COUNT(CASE WHEN ed.status = 'delivered' THEN 1 END) as delivered_count,
    COUNT(CASE WHEN ed.status = 'opened' THEN 1 END) as opened_count,
    COUNT(CASE WHEN ed.status = 'clicked' THEN 1 END) as clicked_count,
    COUNT(et.email_tracking_id) as total_interactions,
    ROUND(COUNT(CASE WHEN ed.status = 'delivered' THEN 1 END)::decimal / NULLIF(COUNT(ed.email_deliveries_id), 0) * 100, 2) as delivery_rate,
    ROUND(COUNT(CASE WHEN ed.status = 'opened' THEN 1 END)::decimal / NULLIF(COUNT(ed.email_deliveries_id), 0) * 100, 2) as open_rate,
    ROUND(COUNT(CASE WHEN ed.status = 'clicked' THEN 1 END)::decimal / NULLIF(COUNT(ed.email_deliveries_id), 0) * 100, 2) as click_rate
FROM email_campaigns ec
LEFT JOIN email_deliveries ed ON ec.campaign_name = ed.campaign_name
LEFT JOIN email_tracking et ON ed.email_deliveries_id = et.email_delivery_id
GROUP BY ec.campaign_name, DATE_TRUNC('day', ec.created_at);

-- ============================================================================
-- SEARCH AND CONTENT ANALYTICS VIEWS
-- ============================================================================

-- Content search analytics
CREATE MATERIALIZED VIEW mv_search_analytics AS
SELECT
    DATE_TRUNC('day', sq.created_at) as search_date,
    sq.search_query,
    COUNT(*) as search_count,
    COUNT(CASE WHEN sq.results_count > 0 THEN 1 END) as successful_searches,
    AVG(sq.results_count) as avg_results_count,
    AVG(sq.search_time_ms) as avg_search_time,
    COUNT(DISTINCT sq.user_id) as unique_searchers
FROM search_queries sq
GROUP BY DATE_TRUNC('day', sq.created_at), sq.search_query
ORDER BY search_count DESC;

-- Vector embedding coverage
CREATE MATERIALIZED VIEW mv_embedding_coverage AS
SELECT
    'ai_insights' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END) as embedded_records,
    ROUND(COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END)::decimal / NULLIF(COUNT(*), 0) * 100, 2) as embedding_coverage
FROM ai_insights
WHERE status = 'active'
UNION ALL
SELECT
    'products' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END) as embedded_records,
    ROUND(COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END)::decimal / NULLIF(COUNT(*), 0) * 100, 2) as embedding_coverage
FROM products
WHERE is_active = true
UNION ALL
SELECT
    'chat_messages' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END) as embedded_records,
    ROUND(COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END)::decimal / NULLIF(COUNT(*), 0) * 100, 2) as embedding_coverage
FROM chat_messages
WHERE content IS NOT NULL;

-- ============================================================================
-- REFRESH AND MAINTENANCE FUNCTIONS
-- ============================================================================

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_analytics_views()
RETURNS TABLE(view_name TEXT, refresh_status TEXT, refresh_duration INTERVAL) AS $$
DECLARE
    v_start_time TIMESTAMP;
    v_end_time TIMESTAMP;
    v_view_name TEXT;
    v_sql TEXT;
BEGIN
    -- List of all materialized views to refresh
    FOR v_view_name IN
        SELECT matviewname
        FROM pg_matviews
        WHERE schemaname = 'public'
        AND matviewname LIKE 'mv_%'
    LOOP
        v_start_time := clock_timestamp();

        -- Refresh the view
        v_sql := format('REFRESH MATERIALIZED VIEW CONCURRENTLY %I', v_view_name);
        EXECUTE v_sql;

        v_end_time := clock_timestamp();

        RETURN QUERY SELECT
            v_view_name,
            'completed'::TEXT,
            (v_end_time - v_start_time)::INTERVAL;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function to check materialized view freshness
CREATE OR REPLACE FUNCTION check_materialized_view_freshness()
RETURNS TABLE(
    view_name TEXT,
    last_refresh TIMESTAMP,
    age_hours INTEGER,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.matviewname::TEXT as view_name,
        GREATEST(
            COALESCE(s.last_vacuum, '1970-01-01'::timestamp),
            COALESCE(s.last_autovacuum, '1970-01-01'::timestamp)
        ) as last_refresh,
        EXTRACT(EPOCH FROM (NOW() - GREATEST(
            COALESCE(s.last_vacuum, NOW()),
            COALESCE(s.last_autovacuum, NOW())
        )))/3600::INTEGER as age_hours,
        CASE
            WHEN EXTRACT(EPOCH FROM (NOW() - GREATEST(
                COALESCE(s.last_vacuum, NOW()),
                COALESCE(s.last_autovacuum, NOW())
            )))/3600 > 24 THEN 'stale'
            WHEN EXTRACT(EPOCH FROM (NOW() - GREATEST(
                COALESCE(s.last_vacuum, NOW()),
                COALESCE(s.last_autovacuum, NOW())
            )))/3600 > 12 THEN 'aging'
            ELSE 'fresh'
        END as status
    FROM pg_matviews m
    LEFT JOIN pg_stat_user_tables s ON m.matviewname = s.relname
    WHERE m.schemaname = 'public'
    AND m.matviewname LIKE 'mv_%';
END;
$$ LANGUAGE plpgsql;

-- Function to get materialized view statistics
CREATE OR REPLACE FUNCTION get_materialized_view_stats()
RETURNS TABLE(
    view_name TEXT,
    row_count BIGINT,
    size_mb NUMERIC,
    last_refresh TIMESTAMP,
    refresh_age_hours INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.matviewname::TEXT as view_name,
        GREATEST(COALESCE(s.n_tup_ins, 0) - COALESCE(s.n_tup_del, 0), 0)::BIGINT as row_count,
        ROUND(pg_total_relation_size(m.matviewname::regclass) / 1024.0 / 1024.0, 2) as size_mb,
        GREATEST(
            COALESCE(s.last_vacuum, '1970-01-01'::timestamp),
            COALESCE(s.last_autovacuum, '1970-01-01'::timestamp)
        ) as last_refresh,
        EXTRACT(EPOCH FROM (NOW() - GREATEST(
            COALESCE(s.last_vacuum, NOW()),
            COALESCE(s.last_autovacuum, NOW())
        )))/3600::INTEGER as refresh_age_hours
    FROM pg_matviews m
    LEFT JOIN pg_stat_user_tables s ON m.matviewname = s.relname
    WHERE m.schemaname = 'public'
    AND m.matviewname LIKE 'mv_%';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INDEXES FOR MATERIALIZED VIEWS
-- ============================================================================

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_mv_monthly_sales_month ON mv_monthly_sales(month);
CREATE INDEX IF NOT EXISTS idx_mv_monthly_sales_company ON mv_monthly_sales(company_name);

CREATE INDEX IF NOT EXISTS idx_mv_customer_analytics_status ON mv_customer_analytics(customer_status);
CREATE INDEX IF NOT EXISTS idx_mv_customer_analytics_segment ON mv_customer_analytics(customer_segment);

CREATE INDEX IF NOT EXISTS idx_mv_ai_insights_date ON mv_ai_insights_performance(analysis_date);
CREATE INDEX IF NOT EXISTS idx_mv_ai_insights_type ON mv_ai_insights_performance(insight_type);

CREATE INDEX IF NOT EXISTS idx_mv_chat_analytics_date ON mv_chat_conversation_analytics(conversation_date);
CREATE INDEX IF NOT EXISTS idx_mv_chat_analytics_session_type ON mv_chat_conversation_analytics(session_type);

CREATE INDEX IF NOT EXISTS idx_mv_gl_monthly_date ON mv_general_ledger_monthly(transaction_month);
CREATE INDEX IF NOT EXISTS idx_mv_revenue_analysis_date ON mv_revenue_analysis(revenue_month);

-- ============================================================================
-- SAMPLE QUERIES FOR MATERIALIZED VIEWS
-- ============================================================================

/*
-- Example queries for the materialized views:

-- Monthly sales trend
SELECT
    month,
    company_name,
    total_revenue,
    invoice_count,
    avg_invoice_value
FROM mv_monthly_sales
WHERE month >= CURRENT_DATE - INTERVAL '6 months'
ORDER BY month, total_revenue DESC;

-- Customer segmentation analysis
SELECT
    customer_segment,
    COUNT(*) as customer_count,
    SUM(total_spent) as segment_revenue,
    AVG(avg_order_value) as avg_order_value
FROM mv_customer_analytics
WHERE customer_status = 'active'
GROUP BY customer_segment
ORDER BY segment_revenue DESC;

-- AI insights performance
SELECT
    analysis_date,
    insight_type,
    insight_count,
    avg_quality_score,
    critical_insights + high_impact_insights as high_priority_insights
FROM mv_ai_insights_performance
WHERE analysis_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY analysis_date, insight_count DESC;

-- Revenue analysis by month
SELECT
    revenue_month,
    company_name,
    SUM(revenue_amount) as total_revenue,
    SUM(revenue_transactions) as transaction_count
FROM mv_revenue_analysis
GROUP BY revenue_month, company_name
ORDER BY revenue_month, total_revenue DESC;

-- System performance monitoring
SELECT
    metric_hour,
    metric_name,
    avg_value,
    max_value,
    min_value
FROM mv_system_performance
WHERE metric_hour >= CURRENT_DATE - INTERVAL '24 hours'
ORDER BY metric_hour, metric_name;
*/

-- ============================================================================
-- GRANTS AND PERMISSIONS
-- ============================================================================

-- Grant access to the materialized views
GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT USAGE ON SCHEMA public TO PUBLIC;

-- Grant execute permissions on utility functions
GRANT EXECUTE ON FUNCTION refresh_all_analytics_views() TO PUBLIC;
GRANT EXECUTE ON FUNCTION check_materialized_view_freshness() TO PUBLIC;
GRANT EXECUTE ON FUNCTION get_materialized_view_stats() TO PUBLIC;

-- ============================================================================
-- FINAL NOTES
-- ============================================================================

/*
This script creates comprehensive materialized views for:

1. Business Intelligence:
   - Monthly sales performance
   - Customer analytics and segmentation
   - Product performance analytics

2. AI/ML Analytics:
   - AI insights performance tracking
   - Chat conversation analytics
   - AI model usage statistics

3. Financial Analytics:
   - General ledger monthly summaries
   - Revenue recognition and analysis
   - Expense analysis by category
   - Cash flow analysis

4. Operational Analytics:
   - User activity and engagement
   - System performance metrics
   - Email campaign performance

5. Search and Content Analytics:
   - Search analytics
   - Vector embedding coverage

To refresh all views automatically:
SELECT cron.schedule('refresh-analytics-views', '0 2 * * *', 'SELECT refresh_all_analytics_views();');

To monitor view freshness:
SELECT * FROM check_materialized_view_freshness();

To get view statistics:
SELECT * FROM get_materialized_view_stats();
*/
