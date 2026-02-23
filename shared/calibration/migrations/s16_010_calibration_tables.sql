-- ============================================================================
-- s16_010_calibration_tables.sql
-- Calibration Engine persistence layer
-- محرك المعايرة - طبقة الثبات
--
-- Tables:
--   calibration_run          – Tracks each calibration execution
--   parameter_set            – Versioned parameter sets (candidate → active → deprecated)
--   parameter_change_log     – Audit trail for parameter activations
-- ============================================================================

-- 1. Calibration Run
CREATE TABLE IF NOT EXISTS calibration_run (
    id                  uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           text            NOT NULL,
    field_id            text            NOT NULL,
    season_id           text            NOT NULL,
    crop_type           text            NOT NULL,
    model_name          text            NOT NULL,
    model_version       text            NOT NULL,
    method              text            NOT NULL,   -- 'bayes_opt' | 'hill_climb' | ...
    status              text            NOT NULL,   -- queued | running | succeeded | failed | cancelled
    dataset_fingerprint text            NOT NULL,   -- SHA-256 of observation dataset
    objective_value     double precision NULL,       -- Best objective (NLL or RMSE)
    metrics             jsonb           NOT NULL DEFAULT '{}'::jsonb,
    notes               text            NULL,
    started_at          timestamptz     NOT NULL DEFAULT now(),
    ended_at            timestamptz     NULL
);

COMMENT ON TABLE calibration_run IS 'تشغيلات المعايرة - Calibration execution records';

-- Fast lookup by (tenant, field, season, model) sorted by recency
CREATE INDEX IF NOT EXISTS idx_cal_run_tenant_field_season
    ON calibration_run (tenant_id, field_id, season_id, model_name, started_at DESC);

-- Find duplicate datasets
CREATE INDEX IF NOT EXISTS idx_cal_run_fingerprint
    ON calibration_run (dataset_fingerprint);


-- 2. Parameter Set
CREATE TABLE IF NOT EXISTS parameter_set (
    id                  uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           text            NOT NULL,
    field_id            text            NOT NULL,
    season_id           text            NOT NULL,
    model_name          text            NOT NULL,
    model_version       text            NOT NULL,
    parameters          jsonb           NOT NULL DEFAULT '{}'::jsonb,   -- { "rue_g_mj": 1.3, ... }
    param_uncertainty   jsonb           NOT NULL DEFAULT '{}'::jsonb,   -- { "rue_g_mj": 0.05, ... }
    prior               jsonb           NOT NULL DEFAULT '{}'::jsonb,   -- Initial / prior values
    posterior_summary   jsonb           NOT NULL DEFAULT '{}'::jsonb,   -- Bayesian posterior stats
    created_from_run_id uuid            NULL REFERENCES calibration_run(id) ON DELETE SET NULL,
    status              text            NOT NULL DEFAULT 'candidate',   -- candidate | active | deprecated
    created_at          timestamptz     NOT NULL DEFAULT now(),
    activated_at        timestamptz     NULL,
    deactivated_at      timestamptz     NULL
);

COMMENT ON TABLE parameter_set IS 'مجموعات المعاملات - Versioned calibrated parameter sets';

-- Lookup by (tenant, field, season, model) sorted by recency
CREATE INDEX IF NOT EXISTS idx_param_set_lookup
    ON parameter_set (tenant_id, field_id, season_id, model_name, created_at DESC);

-- Enforce at most ONE active parameter set per (tenant, field, season, model)
CREATE UNIQUE INDEX IF NOT EXISTS ux_param_set_one_active
    ON parameter_set (tenant_id, field_id, season_id, model_name)
    WHERE status = 'active';


-- 3. Parameter Change Log (audit trail)
CREATE TABLE IF NOT EXISTS parameter_change_log (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               text        NOT NULL,
    field_id                text        NOT NULL,
    season_id               text        NOT NULL,
    model_name              text        NOT NULL,
    from_parameter_set_id   uuid        NULL,
    to_parameter_set_id     uuid        NOT NULL REFERENCES parameter_set(id) ON DELETE RESTRICT,
    actor                   text        NOT NULL,   -- user_id or 'system'
    reason                  text        NOT NULL,
    created_at              timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE parameter_change_log IS 'سجل تغيير المعاملات - Activation audit trail';

CREATE INDEX IF NOT EXISTS idx_param_change_tenant_field
    ON parameter_change_log (tenant_id, field_id, season_id, model_name, created_at DESC);
