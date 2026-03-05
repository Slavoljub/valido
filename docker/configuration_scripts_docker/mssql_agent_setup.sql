-- MSSQL Agent Setup Script
-- Enables and configures SQL Server Agent

USE master;
GO

-- Enable SQL Server Agent
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'Agent XPs', 1;
RECONFIGURE;
GO

-- Start SQL Server Agent service
EXEC xp_servicecontrol 'Start', 'SQLServerAgent';
GO

-- Create a test job to verify Agent is working
USE msdb;
GO

IF NOT EXISTS (SELECT job_id FROM msdb.dbo.sysjobs WHERE name = 'TestJob')
BEGIN
    EXEC dbo.sp_add_job
        @job_name = N'TestJob',
        @enabled = 1,
        @description = N'Test job to verify SQL Agent is working';
    
    EXEC dbo.sp_add_jobstep
        @job_name = N'TestJob',
        @step_name = N'Test Step',
        @subsystem = N'TSQL',
        @command = N'SELECT GETDATE() AS CurrentTime, ''SQL Agent is working!'' AS Status';
    
    EXEC dbo.sp_add_schedule
        @schedule_name = N'TestSchedule',
        @freq_type = 1, -- Once
        @active_start_time = 235959; -- 23:59:59
    
    EXEC dbo.sp_attach_schedule
        @job_name = N'TestJob',
        @schedule_name = N'TestSchedule';
END
GO

PRINT 'MSSQL Agent setup completed successfully';
GO
