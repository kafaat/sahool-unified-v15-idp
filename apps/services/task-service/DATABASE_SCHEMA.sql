-- ============================================================================
-- SAHOOL Task Service - PostgreSQL Database Schema
-- ============================================================================
-- This file documents the database schema created by SQLAlchemy models
-- Run by: SQLAlchemy ORM on service startup
-- Tables: tasks, task_evidence, task_history
-- ============================================================================

-- ============================================================================
-- Table: tasks
-- Description: Main table for agricultural task management
-- ============================================================================
CREATE TABLE IF NOT EXISTS tasks (
    -- Primary Key
    task_id VARCHAR(50) PRIMARY KEY,

    -- Multi-tenancy
    tenant_id VARCHAR(50) NOT NULL,

    -- Core task information
    title VARCHAR(200) NOT NULL,
    title_ar VARCHAR(200),
    description TEXT,
    description_ar TEXT,

    -- Task attributes
    task_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',

    -- Assignment and location
    field_id VARCHAR(100),
    zone_id VARCHAR(100),
    assigned_to VARCHAR(100),
    created_by VARCHAR(100) NOT NULL,

    -- Scheduling
    due_date TIMESTAMP WITH TIME ZONE,
    scheduled_time VARCHAR(10),  -- HH:MM format
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    completion_notes TEXT,

    -- Metadata
    metadata JSONB,

    -- Astronomical integration fields
    astronomical_score INTEGER CHECK (astronomical_score >= 1 AND astronomical_score <= 10),
    moon_phase_at_due_date VARCHAR(100),
    lunar_mansion_at_due_date VARCHAR(100),
    optimal_time_of_day VARCHAR(50),
    suggested_by_calendar BOOLEAN DEFAULT FALSE,
    astronomical_recommendation JSONB,
    astronomical_warnings TEXT[]
);

-- Indexes for tasks table
CREATE INDEX IF NOT EXISTS idx_tasks_tenant_status ON tasks(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_status ON tasks(assigned_to, status);
CREATE INDEX IF NOT EXISTS idx_tasks_field_status ON tasks(field_id, status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date_status ON tasks(due_date, status);
CREATE INDEX IF NOT EXISTS idx_tasks_task_type ON tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);

-- Comments
COMMENT ON TABLE tasks IS 'Agricultural task management - المهام الزراعية';
COMMENT ON COLUMN tasks.task_type IS 'irrigation, fertilization, spraying, scouting, maintenance, sampling, harvest, planting, other';
COMMENT ON COLUMN tasks.priority IS 'urgent, high, medium, low';
COMMENT ON COLUMN tasks.status IS 'pending, in_progress, completed, cancelled, overdue';
COMMENT ON COLUMN tasks.astronomical_score IS 'Astronomical suitability score (1-10) - التصنيف الفلكي';

-- ============================================================================
-- Table: task_evidence
-- Description: Evidence attached to tasks (photos, notes, voice, measurements)
-- ============================================================================
CREATE TABLE IF NOT EXISTS task_evidence (
    -- Primary Key
    evidence_id VARCHAR(50) PRIMARY KEY,

    -- Foreign Key to tasks
    task_id VARCHAR(50) NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,

    -- Evidence details
    type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    captured_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Location (GPS coordinates)
    location JSONB,  -- Format: {"lat": float, "lon": float}

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for task_evidence table
CREATE INDEX IF NOT EXISTS idx_evidence_task_id ON task_evidence(task_id);
CREATE INDEX IF NOT EXISTS idx_evidence_type ON task_evidence(type);

-- Comments
COMMENT ON TABLE task_evidence IS 'Evidence attached to tasks - أدلة المهام';
COMMENT ON COLUMN task_evidence.type IS 'photo, note, voice, measurement';
COMMENT ON COLUMN task_evidence.content IS 'URL for media files or text content for notes';
COMMENT ON COLUMN task_evidence.location IS 'GPS coordinates in JSONB format';

-- ============================================================================
-- Table: task_history
-- Description: Audit trail for task changes
-- ============================================================================
CREATE TABLE IF NOT EXISTS task_history (
    -- Primary Key
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Key to tasks
    task_id VARCHAR(50) NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,

    -- Change tracking
    action VARCHAR(50) NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20),

    -- User and context
    performed_by VARCHAR(100) NOT NULL,
    changes JSONB,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for task_history table
CREATE INDEX IF NOT EXISTS idx_history_task_id ON task_history(task_id);
CREATE INDEX IF NOT EXISTS idx_history_action ON task_history(action);
CREATE INDEX IF NOT EXISTS idx_history_created_at ON task_history(created_at);

-- Comments
COMMENT ON TABLE task_history IS 'Audit trail for task changes - سجل تغييرات المهام';
COMMENT ON COLUMN task_history.action IS 'created, updated, started, completed, cancelled, assigned';
COMMENT ON COLUMN task_history.changes IS 'Detailed field changes in JSON format';

-- ============================================================================
-- Sample Queries
-- ============================================================================

-- Get all pending tasks for a tenant
-- SELECT * FROM tasks WHERE tenant_id = 'tenant_demo' AND status = 'pending';

-- Get tasks due today
-- SELECT * FROM tasks
-- WHERE due_date >= CURRENT_DATE
--   AND due_date < CURRENT_DATE + INTERVAL '1 day'
--   AND status != 'completed';

-- Get tasks with evidence count
-- SELECT t.*, COUNT(e.evidence_id) as evidence_count
-- FROM tasks t
-- LEFT JOIN task_evidence e ON t.task_id = e.task_id
-- GROUP BY t.task_id;

-- Get task history
-- SELECT h.*, t.title
-- FROM task_history h
-- JOIN tasks t ON h.task_id = t.task_id
-- WHERE h.task_id = 'task_001'
-- ORDER BY h.created_at DESC;

-- Get overdue tasks
-- SELECT * FROM tasks
-- WHERE due_date < CURRENT_TIMESTAMP
--   AND status NOT IN ('completed', 'cancelled');

-- Get tasks by field with astronomical score
-- SELECT task_id, title, field_id, astronomical_score, moon_phase_at_due_date
-- FROM tasks
-- WHERE field_id = 'field_north'
--   AND astronomical_score >= 7
-- ORDER BY astronomical_score DESC;

-- Get task statistics by status
-- SELECT
--   status,
--   COUNT(*) as count,
--   AVG(actual_duration_minutes) as avg_duration
-- FROM tasks
-- WHERE tenant_id = 'tenant_demo'
-- GROUP BY status;

-- ============================================================================
-- Data Integrity Rules
-- ============================================================================

-- 1. Cascade delete: When a task is deleted, all evidence and history are automatically deleted
-- 2. Timestamps: created_at and updated_at are automatically managed
-- 3. Enums are stored as strings for flexibility
-- 4. JSONB fields allow flexible schema evolution
-- 5. Indexes are optimized for common query patterns

-- ============================================================================
-- Maintenance Queries
-- ============================================================================

-- Get table sizes
-- SELECT
--   schemaname as schema,
--   tablename as table,
--   pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
-- FROM pg_tables
-- WHERE tablename IN ('tasks', 'task_evidence', 'task_history')
-- ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Get index usage
-- SELECT
--   indexrelname as index_name,
--   idx_scan as index_scans,
--   idx_tup_read as tuples_read,
--   idx_tup_fetch as tuples_fetched
-- FROM pg_stat_user_indexes
-- WHERE schemaname = 'public'
--   AND indexrelname LIKE 'idx_%'
-- ORDER BY idx_scan DESC;

-- Vacuum and analyze (run periodically)
-- VACUUM ANALYZE tasks;
-- VACUUM ANALYZE task_evidence;
-- VACUUM ANALYZE task_history;

-- ============================================================================
-- End of Schema Definition
-- ============================================================================
