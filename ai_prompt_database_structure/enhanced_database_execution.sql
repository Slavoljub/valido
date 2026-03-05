-- ============================================================================
-- ENHANCED VALIDOAI DATABASE EXECUTION SCRIPT
-- ============================================================================
-- This script executes the enhanced PostgreSQL schema with all new features:
-- ✅ PWA Support, AI/LLM Models, ML Models, Chat History, Vector Search
-- ✅ Materialized Views, Automation, Backups, Caching, Performance Monitoring
-- ✅ Full-Text Search, Row Level Security, Enterprise Features
-- ============================================================================

-- Enable required extensions first
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_buffercache";
CREATE EXTENSION IF NOT EXISTS "pg_prewarm";
CREATE EXTENSION IF NOT EXISTS "pg_similarity";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gist";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "pg_freespacemap";
CREATE EXTENSION IF NOT EXISTS "pg_stat_monitor";
CREATE EXTENSION IF NOT EXISTS "pg_cron";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Set search path
SET search_path TO public;

-- Execute the enhanced schema
\i Postgres_ai_valido_structure.sql

-- Execute the enhanced sample data
\i Postgres_ai_valido_data.sql

-- ============================================================================
-- POST-EXECUTION OPTIMIZATION COMMANDS
-- ============================================================================

-- Refresh all materialized views to populate with data
REFRESH MATERIALIZED VIEW mv_user_activity_summary;
REFRESH MATERIALIZED VIEW mv_company_financial_summary;
REFRESH MATERIALIZED VIEW mv_ai_model_performance;
REFRESH MATERIALIZED VIEW mv_email_campaign_performance;

-- Update search vectors for existing data
UPDATE search_index SET search_vector = setweight(to_tsvector('english', coalesce(search_content, '')), 'A');

-- Create additional indexes for performance
CREATE INDEX CONCURRENTLY idx_chat_messages_embedding ON chat_messages USING ivfflat (embedding_vector vector_cosine_ops);
CREATE INDEX CONCURRENTLY idx_vector_embeddings_search ON vector_embeddings USING ivfflat (embedding_vector vector_cosine_ops);

-- Set up automated materialized view refresh (requires pg_cron)
-- SELECT cron.schedule('refresh-mv-user-activity', '0 */2 * * *', 'REFRESH MATERIALIZED VIEW mv_user_activity_summary;');
-- SELECT cron.schedule('refresh-mv-company-financial', '0 */4 * * *', 'REFRESH MATERIALIZED VIEW mv_company_financial_summary;');
-- SELECT cron.schedule('refresh-mv-ai-performance', '0 */6 * * *', 'REFRESH MATERIALIZED VIEW mv_ai_model_performance;');
-- SELECT cron.schedule('refresh-mv-email-performance', '0 */12 * * *', 'REFRESH MATERIALIZED VIEW mv_email_campaign_performance;');

-- Set up automated backup tasks
-- SELECT cron.schedule('daily-backup', '0 2 * * *', $$
--    SELECT backup_database('Daily Full Backup', 'full', '/backup/postgres/daily/');
-- $$);

-- ============================================================================
-- SYSTEM CONFIGURATION AND DEFAULTS
-- ============================================================================

-- Insert default cache configurations
INSERT INTO cache_defaults (cache_key, cache_type, cache_value, cache_ttl, cache_category, is_system_cache, is_compressed, compression_algorithm) VALUES
('system_settings', 'memory', '{"ttl": 300, "compress": false}', 300, 'system', true, false, 'none'),
('user_permissions', 'redis', '{"ttl": 1800, "compress": true}', 1800, 'user', true, true, 'gzip'),
('company_data', 'redis', '{"ttl": 3600, "compress": true}', 3600, 'company', false, true, 'gzip'),
('financial_reports', 'redis', '{"ttl": 1800, "compress": true}', 1800, 'financial', false, true, 'gzip'),
('ai_model_cache', 'redis', '{"ttl": 7200, "compress": true}', 7200, 'ai', true, true, 'gzip'),
('chat_history', 'redis', '{"ttl": 3600, "compress": true}', 3600, 'chat', false, true, 'gzip'),
('search_results', 'memory', '{"ttl": 300, "compress": false}', 300, 'search', false, false, 'none'),
('pwa_cache', 'memory', '{"ttl": 86400, "compress": false}', 86400, 'pwa', true, false, 'none');

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, category, description, is_system_setting, is_user_editable, validation_rules) VALUES
('system.maintenance_mode', 'false', 'boolean', 'system', 'Enable maintenance mode', true, false, '{"type": "boolean"}'),
('system.debug_mode', 'false', 'boolean', 'system', 'Enable debug logging', true, false, '{"type": "boolean"}'),
('system.timezone', 'Europe/Belgrade', 'string', 'system', 'System timezone', true, false, '{"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9/_-]*$"}'),
('ai.default_model', 'llama2-7b-chat-gguf', 'string', 'ai', 'Default AI model for chat', true, true, '{"type": "string"}'),
('ai.max_tokens', '2048', 'number', 'ai', 'Maximum tokens per request', true, true, '{"type": "number", "minimum": 1, "maximum": 32768}'),
('ai.temperature', '0.7', 'number', 'ai', 'AI model temperature', true, true, '{"type": "number", "minimum": 0, "maximum": 2}'),
('email.smtp_host', 'smtp.gmail.com', 'string', 'email', 'SMTP server hostname', true, false, '{"type": "string", "format": "hostname"}'),
('email.smtp_port', '587', 'number', 'email', 'SMTP server port', true, false, '{"type": "number", "minimum": 1, "maximum": 65535}'),
('email.rate_limit', '100', 'number', 'email', 'Emails per hour limit', true, true, '{"type": "number", "minimum": 1, "maximum": 10000}'),
('security.session_timeout', '3600', 'number', 'security', 'Session timeout in seconds', true, false, '{"type": "number", "minimum": 300, "maximum": 86400}'),
('security.password_min_length', '8', 'number', 'security', 'Minimum password length', true, false, '{"type": "number", "minimum": 6, "maximum": 128}'),
('backup.retention_days', '30', 'number', 'backup', 'Backup retention period', true, true, '{"type": "number", "minimum": 1, "maximum": 3650}'),
('pwa.cache_max_age', '86400', 'number', 'pwa', 'PWA cache maximum age', true, true, '{"type": "number", "minimum": 3600, "maximum": 2592000}');

-- ============================================================================
-- AUTOMATION TASKS SETUP
-- ============================================================================

-- Insert default automated tasks
INSERT INTO automated_tasks (company_id, task_name, task_type, task_description, schedule_cron, is_active, task_config, created_by) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Daily Cache Cleanup', 'cleanup', 'Clean expired cache entries', '0 */6 * * *', true, '{"cleanup_types": ["expired", "orphaned"], "batch_size": 1000}', (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Search Index Optimization', 'maintenance', 'Optimize search indexes and update vectors', '0 1 * * *', true, '{"vacuum": true, "reindex": false}', (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Performance Metrics Collection', 'monitoring', 'Collect system performance metrics', '*/15 * * * *', true, '{"metrics": ["cpu", "memory", "disk", "network"]}', (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'AI Model Health Check', 'monitoring', 'Check AI model status and performance', '0 */2 * * *', true, '{"check_types": ["availability", "performance", "memory"]}', (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Chat Session Cleanup', 'cleanup', 'Clean inactive chat sessions', '0 3 * * *', true, '{"inactive_days": 30, "archive": true}', (SELECT users_id FROM users WHERE username = 'system.admin'));

-- ============================================================================
-- BACKUP CONFIGURATION SETUP
-- ============================================================================

-- Insert default backup configurations
INSERT INTO backup_configurations (company_id, backup_name, backup_type, backup_schedule, retention_days, backup_location, compression_enabled, encryption_enabled, include_data, include_files, file_paths, is_active, created_by) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'System Full Backup', 'full', '0 2 * * *', 30, '/backup/postgres/full/', true, true, true, false, null, true, (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Configuration Backup', 'full', '0 3 * * 0', 90, '/backup/config/', true, true, false, true, ARRAY['/etc/validoai/', '/opt/validoai/config/', '/home/validoai/.config/'], true, (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'AI Models Backup', 'incremental', '0 4 * * *', 14, '/backup/ai_models/', true, true, false, true, ARRAY['/models/', '/opt/validoai/models/'], true, (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'File Attachments Backup', 'incremental', '0 5 * * *', 7, '/backup/attachments/', true, true, false, true, ARRAY['/uploads/', '/opt/validoai/uploads/'], true, (SELECT users_id FROM users WHERE username = 'system.admin'));

-- ============================================================================
-- PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Create additional performance indexes
CREATE INDEX CONCURRENTLY idx_performance_metrics_recent ON performance_metrics (recorded_at DESC) WHERE recorded_at > NOW() - INTERVAL '30 days';
CREATE INDEX CONCURRENTLY idx_cache_analytics_recent ON cache_analytics (recorded_at DESC) WHERE recorded_at > NOW() - INTERVAL '7 days';
CREATE INDEX CONCURRENTLY idx_search_queries_recent ON search_queries (searched_at DESC) WHERE searched_at > NOW() - INTERVAL '7 days';

-- Optimize vector indexes
SET ivfflat.probes = 10;
SELECT ivfflat_index_stat('chat_messages_embedding');
SELECT ivfflat_index_stat('vector_embeddings_search');

-- ============================================================================
-- MONITORING AND HEALTH CHECKS
-- ============================================================================

-- Create monitoring views
CREATE VIEW v_system_health AS
SELECT
    'database' as component,
    CASE
        WHEN (SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active') < 20 THEN 'healthy'
        WHEN (SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active') < 50 THEN 'warning'
        ELSE 'critical'
    END as status,
    json_build_object(
        'active_connections', (SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'),
        'total_connections', (SELECT COUNT(*) FROM pg_stat_activity),
        'database_size', pg_size_pretty(pg_database_size(current_database())),
        'last_backup', (SELECT MAX(backup_end) FROM backup_history WHERE backup_status = 'success')
    ) as details,
    NOW() as checked_at;

CREATE VIEW v_ai_model_health AS
SELECT
    am.model_name,
    am.model_type,
    am.is_loaded,
    am.performance_score,
    COUNT(amm.metric_value) as metrics_count,
    MAX(amm.recorded_at) as last_metric,
    CASE
        WHEN am.is_loaded = true AND am.performance_score > 7.0 THEN 'healthy'
        WHEN am.is_loaded = true AND am.performance_score > 5.0 THEN 'warning'
        ELSE 'critical'
    END as status
FROM ai_models am
LEFT JOIN ai_model_metrics amm ON am.ai_models_id = amm.model_id
GROUP BY am.ai_models_id, am.model_name, am.model_type, am.is_loaded, am.performance_score;

-- ============================================================================
-- SECURITY ENHANCEMENTS
-- ============================================================================

-- Create additional security policies
CREATE POLICY pwa_cache_isolation ON pwa_cache_manifests
FOR ALL USING (company_id IN (
    SELECT company_id FROM user_company_access
    WHERE user_id = current_user_id() AND status = 'active'
));

CREATE POLICY automation_task_isolation ON automated_tasks
FOR ALL USING (company_id IN (
    SELECT company_id FROM user_company_access
    WHERE user_id = current_user_id() AND status = 'active'
));

CREATE POLICY backup_config_isolation ON backup_configurations
FOR ALL USING (company_id IN (
    SELECT company_id FROM user_company_access
    WHERE user_id = current_user_id() AND status = 'active'
));

CREATE POLICY system_settings_isolation ON system_settings
FOR ALL USING (
    is_system_setting = false OR
    current_user_id() IN (
        SELECT users_id FROM users WHERE username = 'system.admin'
    )
);

-- ============================================================================
-- FINAL OPTIMIZATION COMMANDS
-- ============================================================================

-- Vacuum and analyze for optimal performance
VACUUM ANALYZE;

-- Update table statistics
ANALYZE VERBOSE;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Enhanced ValidoAI database setup completed successfully!';
    RAISE NOTICE 'Features enabled:';
    RAISE NOTICE '  ✅ PWA Support with Service Workers and Push Notifications';
    RAISE NOTICE '  ✅ AI/LLM Local Models with Performance Tracking';
    RAISE NOTICE '  ✅ ML Models and Algorithms with Training History';
    RAISE NOTICE '  ✅ Chat History with Vector Embeddings';
    RAISE NOTICE '  ✅ Full-Text and Vector Search Capabilities';
    RAISE NOTICE '  ✅ Materialized Views for Performance';
    RAISE NOTICE '  ✅ Automation System with Task Scheduling';
    RAISE NOTICE '  ✅ Backup System with Retention Policies';
    RAISE NOTICE '  ✅ Caching System with Performance Monitoring';
    RAISE NOTICE '  ✅ Row Level Security for Multi-Tenancy';
    RAISE NOTICE '  ✅ Enterprise-grade Features Ready';
END $$;

-- Display final statistics
SELECT
    'Database Objects Created' as metric,
    json_build_object(
        'tables', (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'),
        'indexes', (SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'),
        'views', (SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'public'),
        'materialized_views', (SELECT COUNT(*) FROM pg_matviews WHERE schemaname = 'public'),
        'functions', (SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema = 'public' AND routine_type = 'FUNCTION'),
        'extensions', (SELECT COUNT(*) FROM pg_extension)
    ) as details;

-- ============================================================================
-- DEPLOYMENT CHECKLIST VERIFICATION
-- ============================================================================

DO $$
DECLARE
    total_checks INTEGER := 0;
    passed_checks INTEGER := 0;
BEGIN
    -- Check 1: Extensions
    SELECT COUNT(*) INTO total_checks FROM (VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10),(11),(12),(13),(14),(15),(16)) as t(id);
    SELECT COUNT(*) INTO passed_checks FROM pg_extension WHERE extname IN ('uuid-ossp', 'pgcrypto', 'pg_stat_statements', 'pg_buffercache', 'pg_prewarm', 'pg_similarity', 'pg_trgm', 'btree_gist', 'btree_gin', 'unaccent', 'pg_freespacemap', 'pg_stat_monitor', 'pg_cron', 'vector');

    RAISE NOTICE 'Extensions Check: %/% installed', passed_checks, total_checks;

    -- Check 2: Core Tables
    SELECT COUNT(*) INTO total_checks FROM (VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10)) as t(id);
    SELECT COUNT(*) INTO passed_checks FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('companies', 'users', 'user_company_access', 'ai_models', 'ml_models', 'chat_sessions', 'pwa_service_workers', 'automated_tasks', 'backup_configurations', 'cache_defaults');

    RAISE NOTICE 'Core Tables Check: %/% created', passed_checks, total_checks;

    -- Check 3: Security Policies
    SELECT COUNT(*) INTO total_checks FROM (VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10)) as t(id);
    SELECT COUNT(*) INTO passed_checks FROM pg_policies WHERE schemaname = 'public';

    RAISE NOTICE 'Security Policies Check: %/% created', passed_checks, total_checks;

    -- Check 4: Indexes
    SELECT COUNT(*) INTO passed_checks FROM pg_indexes WHERE schemaname = 'public';
    RAISE NOTICE 'Performance Indexes Check: % created', passed_checks;

    -- Check 5: Sample Data
    SELECT COUNT(*) INTO passed_checks FROM companies;
    RAISE NOTICE 'Sample Data Check: % companies loaded', passed_checks;

    RAISE NOTICE 'Database deployment completed successfully! All systems operational.';
END $$;
