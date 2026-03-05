#!/bin/bash
# MySQL Optimization Script

echo "Optimizing MySQL performance..."

mysql -u root -proot << 'SQL'
-- Create database if not exists
CREATE DATABASE IF NOT EXISTS ai_valido_online;
USE ai_valido_online;

-- Optimize settings
SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
SET GLOBAL innodb_log_file_size = 268435456; -- 256MB
SET GLOBAL innodb_flush_log_at_trx_commit = 2;
SET GLOBAL sync_binlog = 0;
SET GLOBAL innodb_flush_method = 'O_DIRECT';

-- Create sample tables
CREATE TABLE IF NOT EXISTS test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO test_table (name) VALUES ('test_data');
SQL

echo "MySQL optimization completed"
