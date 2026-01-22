-- Migration: 001_create_agent_executions
-- Description: Create agent_executions table for AI Agents Service
-- Author: Claude
-- Date: 2026-01-22

-- ═══════════════════════════════════════════════════════════════════════════════
-- Create agent_executions table
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS agent_executions (
    -- Primary Key
    id UUID PRIMARY KEY,

    -- Agent Configuration
    agent_type VARCHAR(50) NOT NULL,
    mode VARCHAR(20) NOT NULL DEFAULT 'hybrid',

    -- Task Information
    goal TEXT NOT NULL,

    -- Execution Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    state VARCHAR(20) NOT NULL DEFAULT 'idle',

    -- Results
    result JSONB,
    steps JSONB DEFAULT '[]'::jsonb,
    error TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    total_duration_ms INTEGER,

    -- Multi-tenancy & Context
    tenant_id VARCHAR(100) NOT NULL,
    field_id VARCHAR(100),
    farm_id VARCHAR(100),

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_state CHECK (state IN ('idle', 'planning', 'executing', 'validating', 'completed', 'error', 'cancelled')),
    CONSTRAINT valid_mode CHECK (mode IN ('plan', 'execute', 'hybrid'))
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Indexes
-- ═══════════════════════════════════════════════════════════════════════════════

-- Index for filtering by tenant (required for multi-tenancy)
CREATE INDEX IF NOT EXISTS idx_agent_executions_tenant_id
    ON agent_executions(tenant_id);

-- Index for filtering by status
CREATE INDEX IF NOT EXISTS idx_agent_executions_status
    ON agent_executions(status);

-- Index for sorting by creation date (descending for recent-first queries)
CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at
    ON agent_executions(created_at DESC);

-- Index for filtering by agent type
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_type
    ON agent_executions(agent_type);

-- Composite index for common query pattern (tenant + status + created_at)
CREATE INDEX IF NOT EXISTS idx_agent_executions_tenant_status_created
    ON agent_executions(tenant_id, status, created_at DESC);

-- Index for field-specific queries
CREATE INDEX IF NOT EXISTS idx_agent_executions_field_id
    ON agent_executions(field_id)
    WHERE field_id IS NOT NULL;

-- Index for farm-specific queries
CREATE INDEX IF NOT EXISTS idx_agent_executions_farm_id
    ON agent_executions(farm_id)
    WHERE farm_id IS NOT NULL;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Trigger for updated_at
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_agent_executions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_agent_executions_updated_at ON agent_executions;

CREATE TRIGGER trigger_agent_executions_updated_at
    BEFORE UPDATE ON agent_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_executions_updated_at();

-- ═══════════════════════════════════════════════════════════════════════════════
-- Comments
-- ═══════════════════════════════════════════════════════════════════════════════

COMMENT ON TABLE agent_executions IS 'Stores AI agent execution records for the AI Agents Service';
COMMENT ON COLUMN agent_executions.id IS 'Unique identifier for the execution (UUID)';
COMMENT ON COLUMN agent_executions.agent_type IS 'Type of agent: farm_advisor, research, planner';
COMMENT ON COLUMN agent_executions.mode IS 'Execution mode: plan, execute, hybrid';
COMMENT ON COLUMN agent_executions.goal IS 'Task description / goal in natural language';
COMMENT ON COLUMN agent_executions.status IS 'Execution status: pending, running, completed, failed, cancelled';
COMMENT ON COLUMN agent_executions.state IS 'Current state: idle, planning, executing, validating, completed, error, cancelled';
COMMENT ON COLUMN agent_executions.result IS 'Final execution result as JSONB';
COMMENT ON COLUMN agent_executions.steps IS 'Array of execution steps as JSONB';
COMMENT ON COLUMN agent_executions.error IS 'Error message if execution failed';
COMMENT ON COLUMN agent_executions.tenant_id IS 'Tenant ID for multi-tenancy';
COMMENT ON COLUMN agent_executions.field_id IS 'Optional field ID for field-specific tasks';
COMMENT ON COLUMN agent_executions.farm_id IS 'Optional farm ID';
