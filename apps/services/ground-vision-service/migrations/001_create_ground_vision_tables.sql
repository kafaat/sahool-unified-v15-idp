-- Migration: 001_create_ground_vision_tables
-- Description: Create tables consumed by ground-vision-service
-- Service: ground-vision-service
-- Date: 2026-04-18
--
-- Schemas derived from the SQL statements in src/main.py:
--   cameras          → INSERT at main.py:352
--   frame_results    → INSERT at main.py:531
--   timeline_analyses → INSERT at main.py:738
--   anomalies        → UPDATE at main.py:936, 983 (schema inferred from
--                       SELECT + UPDATE columns — service does NOT INSERT
--                       directly, rows expected from a NATS subscriber)
--   detections       → SELECT only at main.py:647, 648 (same as anomalies)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- cameras
-- INSERT columns: camera_id, tower_id, name, name_ar, latitude, longitude,
--                 altitude_m, focal_length_mm, sensor_width_mm, sensor_height_mm,
--                 image_width_px, image_height_px, zoom_min, zoom_max,
--                 tenant_id, status, created_at
-- ON CONFLICT (camera_id) DO UPDATE — so camera_id must be unique.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cameras (
    camera_id          VARCHAR(100) PRIMARY KEY,
    tower_id           VARCHAR(100) NOT NULL,
    name               VARCHAR(200) NOT NULL,
    name_ar            VARCHAR(200),
    latitude           DOUBLE PRECISION NOT NULL,
    longitude          DOUBLE PRECISION NOT NULL,
    altitude_m         DOUBLE PRECISION,
    focal_length_mm    DOUBLE PRECISION,
    sensor_width_mm    DOUBLE PRECISION,
    sensor_height_mm   DOUBLE PRECISION,
    image_width_px     INTEGER,
    image_height_px    INTEGER,
    zoom_min           DOUBLE PRECISION,
    zoom_max           DOUBLE PRECISION,
    tenant_id          VARCHAR(100) NOT NULL,
    status             VARCHAR(30)  NOT NULL DEFAULT 'active',
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
-- Hot query: WHERE tenant_id=$1 AND tower_id=$2 ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_cameras_tenant_tower
    ON cameras (tenant_id, tower_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cameras_tenant
    ON cameras (tenant_id, created_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- frame_results
-- INSERT columns: frame_id, camera_id, field_id, tenant_id,
--                 detections_count, anomalies_count, processed_at
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS frame_results (
    frame_id           VARCHAR(100) PRIMARY KEY,
    camera_id          VARCHAR(100) NOT NULL,
    field_id           VARCHAR(100),
    tenant_id          VARCHAR(100) NOT NULL,
    detections_count   INTEGER      NOT NULL DEFAULT 0,
    anomalies_count    INTEGER      NOT NULL DEFAULT 0,
    processed_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_frame_results_camera
        FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_frame_results_tenant_camera
    ON frame_results (tenant_id, camera_id, processed_at DESC);
CREATE INDEX IF NOT EXISTS idx_frame_results_tenant_field
    ON frame_results (tenant_id, field_id, processed_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- timeline_analyses
-- INSERT columns: analysis_id, field_id, tenant_id, crop_type, growth_stage,
--                 confidence, processing_time_ms, analyzed_at
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS timeline_analyses (
    analysis_id           VARCHAR(100) PRIMARY KEY,
    field_id              VARCHAR(100) NOT NULL,
    tenant_id             VARCHAR(100) NOT NULL,
    crop_type             VARCHAR(80),
    growth_stage          VARCHAR(50),
    confidence            DOUBLE PRECISION,
    processing_time_ms    INTEGER,
    analyzed_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
-- Hot query: WHERE field_id=$1 AND tenant_id=$2
CREATE INDEX IF NOT EXISTS idx_timeline_analyses_tenant_field
    ON timeline_analyses (tenant_id, field_id, analyzed_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- detections
-- The service has only SELECT against this table; rows are expected to be
-- populated by a NATS subscriber that processes sahool.vision.*_detected
-- events. Schema covers the identity keys the reader uses plus a JSONB
-- `data` column so new fields can land without migrations.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS detections (
    detection_id   UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id      VARCHAR(100) NOT NULL,
    camera_id      VARCHAR(100),
    frame_id       VARCHAR(100),
    field_id       VARCHAR(100),
    detected_class VARCHAR(80),
    confidence     DOUBLE PRECISION,
    bbox           JSONB,
    data           JSONB        NOT NULL DEFAULT '{}'::jsonb,
    detected_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_detections_tenant
    ON detections (tenant_id, detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_detections_tenant_camera
    ON detections (tenant_id, camera_id, detected_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- anomalies
-- UPDATE columns (main.py:936,983): status, acknowledged_by, acknowledged_notes,
-- acknowledged_at, resolved_by, resolution_notes, resolution_notes_ar,
-- resolved_at. Primary lookup: (anomaly_id, tenant_id).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS anomalies (
    anomaly_id               UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id                VARCHAR(100) NOT NULL,
    camera_id                VARCHAR(100),
    field_id                 VARCHAR(100),
    anomaly_type             VARCHAR(80),
    severity                 VARCHAR(30),
    confidence               DOUBLE PRECISION,
    data                     JSONB        NOT NULL DEFAULT '{}'::jsonb,
    status                   VARCHAR(30)  NOT NULL DEFAULT 'detected',
    acknowledged_by          VARCHAR(100),
    acknowledged_notes       TEXT,
    acknowledged_at          TIMESTAMPTZ,
    resolved_by              VARCHAR(100),
    resolution_notes         TEXT,
    resolution_notes_ar      TEXT,
    resolved_at              TIMESTAMPTZ,
    detected_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_anomaly_status CHECK (
        status IN ('detected', 'acknowledged', 'resolved', 'false_positive')
    )
);
CREATE INDEX IF NOT EXISTS idx_anomalies_tenant_status
    ON anomalies (tenant_id, status, detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_tenant_field
    ON anomalies (tenant_id, field_id, detected_at DESC);

-- Migration bookkeeping
CREATE TABLE IF NOT EXISTS public._migrations (
    name        VARCHAR(255) PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO public._migrations (name)
VALUES ('001_create_ground_vision_tables')
ON CONFLICT (name) DO NOTHING;
