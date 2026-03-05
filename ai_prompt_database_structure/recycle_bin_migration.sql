-- Recycle Bin Migration for ValidoAI Database
-- Adds comprehensive soft delete functionality to all tables

-- Create recycle_bin table
CREATE TABLE IF NOT EXISTS recycle_bin (
    recycle_bin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    record_data JSONB NOT NULL,
    deleted_by VARCHAR(255),
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_reason TEXT,
    restored_by VARCHAR(255),
    restored_at TIMESTAMP,
    restore_reason TEXT,
    is_permanently_deleted BOOLEAN DEFAULT FALSE,
    permanent_delete_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_recycle_bin_table_record ON recycle_bin(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_recycle_bin_deleted_at ON recycle_bin(deleted_at);
CREATE INDEX IF NOT EXISTS idx_recycle_bin_status ON recycle_bin(is_permanently_deleted);

-- Add comments for documentation
COMMENT ON TABLE recycle_bin IS 'Central table for soft delete functionality across all database tables';
COMMENT ON COLUMN recycle_bin.recycle_bin_id IS 'Unique identifier for recycle bin entries';
COMMENT ON COLUMN recycle_bin.table_name IS 'Name of the original table where the record was deleted from';
COMMENT ON COLUMN recycle_bin.record_id IS 'Original record ID from the source table';
COMMENT ON COLUMN recycle_bin.record_data IS 'Complete record data stored as JSON for restoration';
COMMENT ON COLUMN recycle_bin.deleted_by IS 'User who performed the deletion';
COMMENT ON COLUMN recycle_bin.deleted_at IS 'Timestamp when the record was moved to recycle bin';
COMMENT ON COLUMN recycle_bin.deleted_reason IS 'Reason for deletion provided by user';
COMMENT ON COLUMN recycle_bin.restored_by IS 'User who performed the restoration';
COMMENT ON COLUMN recycle_bin.restored_at IS 'Timestamp when the record was restored';
COMMENT ON COLUMN recycle_bin.restore_reason IS 'Reason for restoration provided by user';
COMMENT ON COLUMN recycle_bin.is_permanently_deleted IS 'Flag indicating if record has been permanently deleted';
COMMENT ON COLUMN recycle_bin.permanent_delete_date IS 'Timestamp when record was permanently deleted';

-- Create function to automatically move records to recycle bin
CREATE OR REPLACE FUNCTION move_to_recycle_bin()
RETURNS TRIGGER AS $$
DECLARE
    record_json JSONB;
    deleted_by_val TEXT;
    deleted_reason_val TEXT;
BEGIN
    -- Convert the old record to JSONB
    record_json := to_jsonb(OLD);

    -- Get deletion metadata from TG_ARGV if provided
    deleted_by_val := COALESCE(TG_ARGV[0], 'system');
    deleted_reason_val := COALESCE(TG_ARGV[1], 'Deleted via trigger');

    -- Remove system columns from JSON
    record_json := record_json - 'created_at' - 'updated_at';

    -- Insert into recycle bin
    INSERT INTO recycle_bin (table_name, record_id, record_data, deleted_by, deleted_reason)
    VALUES (TG_TABLE_NAME, OLD.id::TEXT, record_json, deleted_by_val, deleted_reason_val);

    -- Return OLD to complete the deletion
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Create function to cleanup old records from recycle bin
CREATE OR REPLACE FUNCTION cleanup_recycle_bin(days_old INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Update records older than specified days to permanently deleted
    UPDATE recycle_bin
    SET is_permanently_deleted = TRUE,
        permanent_delete_date = CURRENT_TIMESTAMP,
        deleted_reason = 'Auto-deleted: older than ' || days_old || ' days',
        updated_at = CURRENT_TIMESTAMP
    WHERE is_permanently_deleted = FALSE
    AND deleted_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_old;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create view for recycle bin statistics
CREATE OR REPLACE VIEW recycle_bin_stats AS
SELECT
    'total_records' as metric,
    COUNT(*) as value
FROM recycle_bin
WHERE is_permanently_deleted = FALSE
UNION ALL
SELECT
    'permanently_deleted' as metric,
    COUNT(*) as value
FROM recycle_bin
WHERE is_permanently_deleted = TRUE
UNION ALL
SELECT
    'records_by_table' as metric,
    COUNT(*) as value
FROM recycle_bin
WHERE is_permanently_deleted = FALSE
GROUP BY table_name;

-- Create function to restore record from recycle bin
CREATE OR REPLACE FUNCTION restore_from_recycle_bin(recycle_id UUID, restored_by_val TEXT DEFAULT 'system')
RETURNS BOOLEAN AS $$
DECLARE
    recycle_record RECORD;
    insert_columns TEXT[];
    insert_values TEXT[];
    col_name TEXT;
    col_value TEXT;
    query_text TEXT;
BEGIN
    -- Get record from recycle bin
    SELECT * INTO recycle_record
    FROM recycle_bin
    WHERE recycle_bin_id = recycle_id
    AND is_permanently_deleted = FALSE;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Build dynamic insert query
    FOR col_name IN SELECT jsonb_object_keys(recycle_record.record_data)
    LOOP
        insert_columns := array_append(insert_columns, col_name);
        insert_values := array_append(insert_values,
            format('%L', recycle_record.record_data->>col_name));
    END LOOP;

    -- Create insert query
    query_text := format(
        'INSERT INTO %I (%s) VALUES (%s)',
        recycle_record.table_name,
        array_to_string(insert_columns, ', '),
        array_to_string(insert_values, ', ')
    );

    -- Execute insert
    EXECUTE query_text;

    -- Mark as restored in recycle bin
    UPDATE recycle_bin
    SET restored_by = restored_by_val,
        restored_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE recycle_bin_id = recycle_id;

    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error restoring record: %', SQLERRM;
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE recycle_bin TO validoai;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO validoai;

-- Create trigger example (uncomment and modify for specific tables)
/*
-- Example: Add soft delete trigger to companies table
CREATE TRIGGER companies_soft_delete_trigger
    BEFORE DELETE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION move_to_recycle_bin('system_user', 'Deleted from application');

-- Example: Add soft delete trigger to users table
CREATE TRIGGER users_soft_delete_trigger
    BEFORE DELETE ON users
    FOR EACH ROW
    EXECUTE FUNCTION move_to_recycle_bin('system_user', 'Deleted from application');
*/

-- Insert sample data for testing (optional)
-- INSERT INTO recycle_bin (table_name, record_id, record_data, deleted_by, deleted_reason)
-- VALUES ('companies', '123', '{"name": "Test Company", "email": "test@example.com"}', 'admin', 'Test deletion');

COMMIT;
