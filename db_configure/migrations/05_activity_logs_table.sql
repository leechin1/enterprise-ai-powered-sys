-- Activity Logs Table for Enterprise System
-- Tracks all actions and events in the system

-- Create the activity_logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'system',
    metadata JSONB DEFAULT '{}',
    user_id VARCHAR(100),
    related_entity_type VARCHAR(50),
    related_entity_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'success',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_category ON activity_logs(category);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action_type ON activity_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_activity_logs_status ON activity_logs(status);
CREATE INDEX IF NOT EXISTS idx_activity_logs_related_entity ON activity_logs(related_entity_type, related_entity_id);

-- Add comments
COMMENT ON TABLE activity_logs IS 'Stores activity logs for all actions in the enterprise system';
COMMENT ON COLUMN activity_logs.action_type IS 'Type of action: fix_proposed, fix_approved, email_sent, etc.';
COMMENT ON COLUMN activity_logs.description IS 'Human-readable description of the activity';
COMMENT ON COLUMN activity_logs.category IS 'Category: ai_reporting, email, issues, fixes, knowledge, analytics, system';
COMMENT ON COLUMN activity_logs.metadata IS 'Additional JSON data about the activity';
COMMENT ON COLUMN activity_logs.status IS 'Status: success, failed, pending, declined';

-- Enable RLS (Row Level Security) - optional, adjust as needed
-- ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow all operations for authenticated users (adjust as needed)
-- CREATE POLICY "Allow all for authenticated users" ON activity_logs
--     FOR ALL
--     USING (true)
--     WITH CHECK (true);
