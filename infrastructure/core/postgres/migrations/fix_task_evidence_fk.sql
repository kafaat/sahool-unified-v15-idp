-- Ensure tasks table exists first
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT current_timestamp,
    updated_at TIMESTAMP DEFAULT current_timestamp
);

-- Now create task_evidence with proper foreign key
CREATE TABLE IF NOT EXISTS task_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks (id) ON DELETE CASCADE,
    evidence_type VARCHAR(100),
    evidence_url TEXT,
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_task_evidence_task_id ON task_evidence (task_id);
