-- Misty AI Enterprise System - Workflow Tables Migration
-- Migration: 03_workflow_tables.sql
-- Description: Creates workflow automation tables

-- CASES TABLE (Customer Service)
CREATE TABLE cases (
    case_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id UUID REFERENCES customers(customer_id) ON DELETE SET NULL,
    subject VARCHAR(300) NOT NULL,
    description TEXT,
    category VARCHAR(50) CHECK (category IN ('order_issue', 'product_question', 'return', 'technical', 'general', 'complaint', 'feedback')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'resolved', 'closed', 'escalated')),
    assigned_to UUID REFERENCES users(user_id) ON DELETE SET NULL,
    ai_sentiment VARCHAR(20) CHECK (ai_sentiment IN ('happy', 'neutral', 'frustrated', 'angry', 'confused')),
    ai_score INTEGER CHECK (ai_score >= 0 AND ai_score <= 100),
    ai_suggestion TEXT,
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE cases IS 'Customer service tickets and support cases';
COMMENT ON COLUMN cases.ai_sentiment IS 'AI-detected customer sentiment';
COMMENT ON COLUMN cases.ai_score IS 'AI priority/urgency score';

-- Generate case numbers automatically
CREATE SEQUENCE IF NOT EXISTS case_number_seq START 1000;

CREATE OR REPLACE FUNCTION generate_case_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.case_number := 'CS-' || LPAD(nextval('case_number_seq')::TEXT, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_case_number BEFORE INSERT ON cases
    FOR EACH ROW EXECUTE FUNCTION generate_case_number();

CREATE INDEX idx_cases_customer ON cases(customer_id);
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_priority ON cases(priority);
CREATE INDEX idx_cases_assigned ON cases(assigned_to);
CREATE INDEX idx_cases_created ON cases(created_at DESC);

-- CASE MESSAGES TABLE
CREATE TABLE case_messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES cases(case_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE,
    from_customer BOOLEAN DEFAULT FALSE,
    attachments JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE case_messages IS 'Messages and conversation history for cases';
COMMENT ON COLUMN case_messages.is_internal IS 'Internal staff note (not visible to customer)';

CREATE INDEX idx_case_messages_case ON case_messages(case_id);
CREATE INDEX idx_case_messages_created ON case_messages(created_at DESC);

-- WORKFLOWS TABLE
CREATE TABLE workflows (
    workflow_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    trigger_type VARCHAR(30) CHECK (trigger_type IN ('schedule', 'event', 'manual', 'api', 'webhook')),
    trigger_config JSONB,
    workflow_definition JSONB NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5, 2) GENERATED ALWAYS AS (
        CASE
            WHEN execution_count > 0 THEN (success_count::DECIMAL / execution_count * 100)
            ELSE 0
        END
    ) STORED,
    avg_duration_ms INTEGER,
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
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN end_time IS NOT NULL THEN EXTRACT(EPOCH FROM (end_time - start_time)) * 1000
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

-- SYSTEM LOGS TABLE
CREATE TABLE system_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    log_level VARCHAR(20) CHECK (log_level IN ('debug', 'info', 'warning', 'error', 'critical')),
    source VARCHAR(100),
    message TEXT NOT NULL,
    metadata JSONB,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE system_logs IS 'System-wide logging and audit trail';

CREATE INDEX idx_system_logs_level ON system_logs(log_level);
CREATE INDEX idx_system_logs_source ON system_logs(source);
CREATE INDEX idx_system_logs_created ON system_logs(created_at DESC);

-- Partition system_logs by month for better performance
-- This can be enabled if needed:
-- CREATE TABLE system_logs_y2024m12 PARTITION OF system_logs
--     FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

-- INTEGRATIONS TABLE
CREATE TABLE integrations (
    integration_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) CHECK (category IN ('payment', 'ecommerce', 'email', 'analytics', 'shipping', 'accounting', 'communication')),
    connected BOOLEAN DEFAULT FALSE,
    credentials JSONB,
    settings JSONB,
    last_sync TIMESTAMP WITH TIME ZONE,
    sync_frequency VARCHAR(50),
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE integrations IS 'Third-party service integrations';
COMMENT ON COLUMN integrations.credentials IS 'Encrypted API keys and credentials (should be encrypted at rest)';

CREATE INDEX idx_integrations_service ON integrations(service_name);
CREATE INDEX idx_integrations_category ON integrations(category);

-- Triggers
CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- SUCCESS MESSAGE
DO $$
BEGIN
    RAISE NOTICE 'Workflow tables migration completed successfully!';
    RAISE NOTICE 'Created: cases, case_messages, workflows, workflow_executions, system_logs, integrations';
END $$;
