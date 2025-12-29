-- Misty AI Enterprise System - Workflow Tables Migration
-- Migration: 02_workflow_tables.sql
-- Description: Creates workflow automation tables

-- WORKFLOWS TABLE
CREATE TABLE workflows (
    workflow_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    trigger_type VARCHAR(30) CHECK (trigger_type IN ('schedule', 'event', 'manual', 'api', 'webhook')),
    trigger_config JSONB,
    workflow_definition JSONB NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    execution_count INT4 DEFAULT 0,
    success_count INT4 DEFAULT 0,
    failure_count INT4 DEFAULT 0,
    success_rate NUMERIC GENERATED ALWAYS AS (
        CASE
            WHEN execution_count > 0 THEN (success_count::NUMERIC / execution_count * 100)
            ELSE 0
        END
    ) STORED,
    avg_duration_ms INT4,
    last_execution_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE workflows IS 'Automated workflow definitions';
COMMENT ON COLUMN workflows.trigger_config IS 'JSON config for trigger (schedule, event filters, etc)';
COMMENT ON COLUMN workflows.workflow_definition IS 'JSON workflow steps and logic';

CREATE INDEX idx_workflows_enabled ON workflows(enabled);
CREATE INDEX idx_workflows_trigger ON workflows(trigger_type);

-- WORKFLOW EXECUTIONS TABLE
CREATE TABLE workflow_executions (
    execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    execution_number VARCHAR(50),
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('queued', 'running', 'complete', 'error', 'blocked', 'cancelled')),
    description TEXT,
    progress_percentage INT4 DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INT4 GENERATED ALWAYS AS (
        CASE
            WHEN end_time IS NOT NULL THEN EXTRACT(EPOCH FROM (end_time - start_time))::INT4 * 1000
            ELSE NULL
        END
    ) STORED,
    execution_log JSONB,
    error_message TEXT,
    triggered_by VARCHAR(100),
    metadata JSONB
);

COMMENT ON TABLE workflow_executions IS 'Workflow execution history and logs';
COMMENT ON COLUMN workflow_executions.execution_log IS 'JSON array of execution step logs';

-- Generate execution numbers
CREATE SEQUENCE IF NOT EXISTS execution_number_seq START 1000;

CREATE OR REPLACE FUNCTION generate_execution_number()
RETURNS TRIGGER AS $$
DECLARE
    workflow_name VARCHAR(50);
BEGIN
    SELECT SUBSTRING(name, 1, 3) INTO workflow_name FROM workflows WHERE workflow_id = NEW.workflow_id;
    NEW.execution_number := '#' || LPAD(nextval('execution_number_seq')::TEXT, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_execution_number BEFORE INSERT ON workflow_executions
    FOR EACH ROW EXECUTE FUNCTION generate_execution_number();

CREATE INDEX idx_workflow_executions_workflow ON workflow_executions(workflow_id);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX idx_workflow_executions_start ON workflow_executions(start_time DESC);

-- Trigger to update workflow stats
CREATE OR REPLACE FUNCTION update_workflow_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'complete' THEN
        UPDATE workflows SET
            execution_count = execution_count + 1,
            success_count = success_count + 1,
            last_execution_at = NEW.end_time,
            avg_duration_ms = (
                COALESCE(avg_duration_ms * (execution_count - 1), 0) + NEW.duration_ms
            ) / execution_count
        WHERE workflow_id = NEW.workflow_id;
    ELSIF NEW.status = 'error' THEN
        UPDATE workflows SET
            execution_count = execution_count + 1,
            failure_count = failure_count + 1,
            last_execution_at = NEW.end_time
        WHERE workflow_id = NEW.workflow_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_workflow_stats_on_completion
    AFTER UPDATE OF status ON workflow_executions
    FOR EACH ROW
    WHEN (NEW.status IN ('complete', 'error') AND OLD.status != NEW.status)
    EXECUTE FUNCTION update_workflow_stats();

-- Trigger for updated_at
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- SUCCESS MESSAGE
DO $$
BEGIN
    RAISE NOTICE 'Workflow tables migration completed successfully!';
    RAISE NOTICE 'Created: workflows, workflow_executions';
END $$;
