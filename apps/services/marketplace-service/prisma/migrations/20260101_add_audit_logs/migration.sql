-- Add enhanced audit_logs table for marketplace service
-- This table provides comprehensive audit trail with field-level change tracking

CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Multi-tenancy
  tenant_id VARCHAR(255) NOT NULL,

  -- Actor information
  actor_id VARCHAR(255),
  actor_type VARCHAR(50) NOT NULL DEFAULT 'user',

  -- Event classification
  action VARCHAR(255) NOT NULL,
  category VARCHAR(50) NOT NULL,
  severity VARCHAR(50) NOT NULL DEFAULT 'info',

  -- Resource information
  resource_type VARCHAR(255) NOT NULL,
  resource_id VARCHAR(255) NOT NULL,

  -- Request context
  correlation_id VARCHAR(255) NOT NULL,
  session_id VARCHAR(255),

  -- Network context
  ip_address VARCHAR(50),
  user_agent TEXT,

  -- Change tracking (JSON)
  changes JSONB DEFAULT '[]'::jsonb,
  diff JSONB DEFAULT '{}'::jsonb,
  metadata JSONB DEFAULT '{}'::jsonb,

  -- Result
  success BOOLEAN NOT NULL DEFAULT true,
  error_code VARCHAR(100),
  error_message TEXT,

  -- Hash chain for tamper detection
  prev_hash VARCHAR(64),
  entry_hash VARCHAR(64),

  -- Timestamp
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_audit_tenant_created ON audit_logs(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_actor_created ON audit_logs(actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_correlation ON audit_logs(correlation_id);
CREATE INDEX IF NOT EXISTS idx_audit_category_created ON audit_logs(category, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_severity ON audit_logs(severity, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action, created_at DESC);

-- Prevent modification of audit logs (append-only)
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Audit logs are immutable and cannot be modified or deleted';
END;
$$ LANGUAGE plpgsql;

-- Trigger to prevent updates and deletes
DROP TRIGGER IF EXISTS audit_logs_no_update ON audit_logs;
CREATE TRIGGER audit_logs_no_update
  BEFORE UPDATE OR DELETE ON audit_logs
  FOR EACH ROW
  EXECUTE FUNCTION prevent_audit_modification();

-- Comment on table
COMMENT ON TABLE audit_logs IS 'Enhanced audit trail with field-level change tracking and hash chain integrity';
COMMENT ON COLUMN audit_logs.changes IS 'Array of field-level changes with before/after values';
COMMENT ON COLUMN audit_logs.diff IS 'Automatic diff of changes using deep-diff';
COMMENT ON COLUMN audit_logs.prev_hash IS 'Hash of previous entry for chain integrity';
COMMENT ON COLUMN audit_logs.entry_hash IS 'SHA-256 hash of this entry';
