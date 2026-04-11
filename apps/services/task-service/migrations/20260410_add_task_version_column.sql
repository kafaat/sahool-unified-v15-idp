-- ============================================================================
-- Migration: Add `version` column to `tasks` for optimistic locking
-- Service  : task-service (Wave 2)
-- Date     : 2026-04-10
-- Ticket   : SAHOOL Wave 2 — task-service hardening
-- ============================================================================
--
-- Purpose
-- -------
-- Adds an integer `version` column used for optimistic concurrency control on
-- PUT /api/v1/tasks/{task_id}. Clients may pass `if_match_version` in the
-- update payload; if the stored row's `version` does not match, the server
-- returns HTTP 409 Conflict instead of silently overwriting concurrent
-- edits (e.g. kanban drag-drop races between mobile/web tabs).
--
-- Rollout
-- -------
-- Safe additive change:
--   * Column has NOT NULL + DEFAULT 1, so all existing rows are backfilled
--     atomically by PostgreSQL as part of the ALTER.
--   * No application code writes to this column until the corresponding
--     service release — old writers remain compatible because they don't
--     touch the column (it keeps its default on insert).
--
-- Rollback
-- --------
--   ALTER TABLE tasks DROP COLUMN IF EXISTS version;
--
-- NOTE: This migration is NOT applied automatically. Run it via your
-- standard database migration pipeline (psql / flyway / alembic wrapper).
-- ============================================================================

BEGIN;

ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;

COMMENT ON COLUMN tasks.version IS
    'Optimistic concurrency token. Incremented on every successful update. '
    'Clients may send if_match_version in PUT /tasks/{id} to detect races.';

COMMIT;
