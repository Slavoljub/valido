-- MSSQL Initialization Script
-- Creates database and enables SQL Agent

USE master;
GO

-- Create database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ai_valido_online')
BEGIN
    CREATE DATABASE ai_valido_online;
END
GO

-- Use the database
USE ai_valido_online;
GO

-- Create a test table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[test_table]') AND type in (N'U'))
BEGIN
    CREATE TABLE test_table (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255),
        created_at DATETIME2 DEFAULT GETDATE()
    );
    
    INSERT INTO test_table (name) VALUES ('test_data');
END
GO

PRINT 'MSSQL initialization completed successfully';
GO
