-- SAHOOL Satellite Data Seed
-- Sample NDVI observations and growth stages

-- Clean existing data (optional - comment out for production)
-- TRUNCATE TABLE ndvi_observations, ndvi_alerts CASCADE;

-- Generate NDVI observations for sample fields
-- Simulates satellite imagery data over the past 6 months

-- Helper function to generate realistic NDVI values based on growth stage
CREATE OR REPLACE FUNCTION generate_ndvi_for_stage(days_since_planting INTEGER)
RETURNS TABLE(
    ndvi_mean DECIMAL,
    ndvi_min DECIMAL,
    ndvi_max DECIMAL,
    ndvi_std DECIMAL,
    cloud_coverage DECIMAL,
    confidence DECIMAL
) AS $$
BEGIN
    -- NDVI progression: low after planting, peaks during vegetative growth, decreases at harvest
    RETURN QUERY SELECT
        CASE
            WHEN days_since_planting < 15 THEN 0.15 + random() * 0.10  -- Early germination
            WHEN days_since_planting < 30 THEN 0.30 + random() * 0.15  -- Seedling
            WHEN days_since_planting < 60 THEN 0.50 + random() * 0.20  -- Vegetative growth
            WHEN days_since_planting < 90 THEN 0.65 + random() * 0.15  -- Peak growth
            WHEN days_since_planting < 120 THEN 0.55 + random() * 0.15 -- Flowering/fruiting
            WHEN days_since_planting < 150 THEN 0.40 + random() * 0.15 -- Ripening
            ELSE 0.25 + random() * 0.10                                 -- Harvest/senescence
        END::DECIMAL,
        CASE
            WHEN days_since_planting < 15 THEN 0.05 + random() * 0.08
            WHEN days_since_planting < 30 THEN 0.15 + random() * 0.12
            WHEN days_since_planting < 60 THEN 0.30 + random() * 0.15
            WHEN days_since_planting < 90 THEN 0.45 + random() * 0.15
            WHEN days_since_planting < 120 THEN 0.35 + random() * 0.15
            WHEN days_since_planting < 150 THEN 0.25 + random() * 0.12
            ELSE 0.15 + random() * 0.08
        END::DECIMAL,
        CASE
            WHEN days_since_planting < 15 THEN 0.25 + random() * 0.12
            WHEN days_since_planting < 30 THEN 0.45 + random() * 0.15
            WHEN days_since_planting < 60 THEN 0.70 + random() * 0.15
            WHEN days_since_planting < 90 THEN 0.85 + random() * 0.12
            WHEN days_since_planting < 120 THEN 0.75 + random() * 0.15
            WHEN days_since_planting < 150 THEN 0.55 + random() * 0.12
            ELSE 0.35 + random() * 0.10
        END::DECIMAL,
        (0.08 + random() * 0.10)::DECIMAL,  -- Standard deviation
        (random() * 0.3)::DECIMAL,           -- Cloud coverage (0-30%)
        (0.7 + random() * 0.3)::DECIMAL      -- Confidence (70-100%)
    ;
END;
$$ LANGUAGE plpgsql;

-- Generate NDVI observations for Field 1 (Green Valley Farm, North Field)
-- Assume planting date was 6 months ago
WITH date_series AS (
    SELECT
        generate_series(
            CURRENT_DATE - INTERVAL '180 days',
            CURRENT_DATE - INTERVAL '1 day',
            '5 days'::interval  -- Every 5 days (typical satellite revisit)
        )::date AS obs_date
),
ndvi_data AS (
    SELECT
        obs_date,
        EXTRACT(DAY FROM (obs_date - (CURRENT_DATE - INTERVAL '180 days')))::INTEGER as days_since_planting
    FROM date_series
)
INSERT INTO ndvi_observations (
    tenant_id, field_id, obs_date,
    ndvi_mean, ndvi_min, ndvi_max, ndvi_std,
    cloud_coverage, confidence, pixel_count,
    source, scene_id
)
SELECT
    'tenant-sahool-main'::UUID,
    'fd111111-1111-1111-1111-111111111111'::UUID,
    n.obs_date,
    g.ndvi_mean,
    g.ndvi_min,
    g.ndvi_max,
    g.ndvi_std,
    g.cloud_coverage,
    g.confidence,
    1200 + (random() * 200)::INTEGER,  -- Pixel count
    'sentinel2',
    'S2_' || to_char(n.obs_date, 'YYYYMMDD') || '_T38PGS'
FROM ndvi_data n
CROSS JOIN LATERAL generate_ndvi_for_stage(n.days_since_planting) g
WHERE g.cloud_coverage < 0.5;  -- Filter out very cloudy observations

-- Generate NDVI for Field 2 (Green Valley Farm, South Field)
WITH date_series AS (
    SELECT
        generate_series(
            CURRENT_DATE - INTERVAL '180 days',
            CURRENT_DATE - INTERVAL '1 day',
            '5 days'::interval
        )::date AS obs_date
),
ndvi_data AS (
    SELECT
        obs_date,
        EXTRACT(DAY FROM (obs_date - (CURRENT_DATE - INTERVAL '180 days')))::INTEGER as days_since_planting
    FROM date_series
)
INSERT INTO ndvi_observations (
    tenant_id, field_id, obs_date,
    ndvi_mean, ndvi_min, ndvi_max, ndvi_std,
    cloud_coverage, confidence, pixel_count,
    source, scene_id
)
SELECT
    'tenant-sahool-main'::UUID,
    'fd111111-2222-2222-2222-222222222222'::UUID,
    n.obs_date,
    g.ndvi_mean,
    g.ndvi_min,
    g.ndvi_max,
    g.ndvi_std,
    g.cloud_coverage,
    g.confidence,
    1300 + (random() * 200)::INTEGER,
    'sentinel2',
    'S2_' || to_char(n.obs_date, 'YYYYMMDD') || '_T38PGS'
FROM ndvi_data n
CROSS JOIN LATERAL generate_ndvi_for_stage(n.days_since_planting) g
WHERE g.cloud_coverage < 0.5;

-- Generate NDVI for Field 3-5 (Al-Haymah Agricultural Project)
WITH date_series AS (
    SELECT
        generate_series(
            CURRENT_DATE - INTERVAL '120 days',
            CURRENT_DATE - INTERVAL '1 day',
            '5 days'::interval
        )::date AS obs_date
),
ndvi_data AS (
    SELECT
        obs_date,
        EXTRACT(DAY FROM (obs_date - (CURRENT_DATE - INTERVAL '120 days')))::INTEGER as days_since_planting
    FROM date_series
),
fields AS (
    SELECT unnest(ARRAY[
        'fd112222-1111-1111-1111-111111111111',
        'fd112222-2222-2222-2222-222222222222',
        'fd112222-3333-3333-3333-333333333333'
    ]::UUID[]) as field_id
)
INSERT INTO ndvi_observations (
    tenant_id, field_id, obs_date,
    ndvi_mean, ndvi_min, ndvi_max, ndvi_std,
    cloud_coverage, confidence, pixel_count,
    source
)
SELECT
    'tenant-sahool-main'::UUID,
    f.field_id,
    n.obs_date,
    g.ndvi_mean,
    g.ndvi_min,
    g.ndvi_max,
    g.ndvi_std,
    g.cloud_coverage,
    g.confidence,
    800 + (random() * 150)::INTEGER,
    'sentinel2'
FROM ndvi_data n
CROSS JOIN fields f
CROSS JOIN LATERAL generate_ndvi_for_stage(n.days_since_planting) g
WHERE g.cloud_coverage < 0.5;

-- Generate NDVI for Coffee fields (Ta'izz) - slower growth cycle
WITH date_series AS (
    SELECT
        generate_series(
            CURRENT_DATE - INTERVAL '120 days',
            CURRENT_DATE - INTERVAL '1 day',
            '5 days'::interval
        )::date AS obs_date
),
ndvi_data AS (
    SELECT
        obs_date,
        EXTRACT(DAY FROM (obs_date - (CURRENT_DATE - INTERVAL '120 days')))::INTEGER as days_since_planting
    FROM date_series
),
fields AS (
    SELECT unnest(ARRAY[
        'fd221111-1111-1111-1111-111111111111',
        'fd221111-2222-2222-2222-222222222222'
    ]::UUID[]) as field_id
)
INSERT INTO ndvi_observations (
    tenant_id, field_id, obs_date,
    ndvi_mean, ndvi_min, ndvi_max, ndvi_std,
    cloud_coverage, confidence, pixel_count,
    source
)
SELECT
    'tenant-sahool-main'::UUID,
    f.field_id,
    n.obs_date,
    -- Coffee has relatively stable high NDVI (perennial)
    0.70 + random() * 0.15,
    0.55 + random() * 0.10,
    0.85 + random() * 0.10,
    0.08 + random() * 0.05,
    random() * 0.4,
    0.75 + random() * 0.25,
    600 + (random() * 100)::INTEGER,
    'sentinel2'
FROM ndvi_data n
CROSS JOIN fields f
WHERE random() < 0.7;  -- Some missing observations

-- Generate NDVI for Date Palm fields (Hadramout) - perennial, stable NDVI
WITH date_series AS (
    SELECT
        generate_series(
            CURRENT_DATE - INTERVAL '240 days',
            CURRENT_DATE - INTERVAL '1 day',
            '8 days'::interval  -- Less frequent monitoring for stable crops
        )::date AS obs_date
),
fields AS (
    SELECT unnest(ARRAY[
        'fd331111-1111-1111-1111-111111111111',
        'fd331111-2222-2222-2222-222222222222',
        'fd331111-3333-3333-3333-333333333333',
        'fd331111-4444-4444-4444-444444444444'
    ]::UUID[]) as field_id
)
INSERT INTO ndvi_observations (
    tenant_id, field_id, obs_date,
    ndvi_mean, ndvi_min, ndvi_max, ndvi_std,
    cloud_coverage, confidence, pixel_count,
    source
)
SELECT
    'tenant-sahool-main'::UUID,
    f.field_id,
    d.obs_date,
    0.65 + random() * 0.15,  -- Stable high NDVI for palm trees
    0.50 + random() * 0.10,
    0.80 + random() * 0.10,
    0.06 + random() * 0.04,
    random() * 0.25,  -- Low cloud coverage (desert)
    0.80 + random() * 0.20,
    1500 + (random() * 300)::INTEGER,
    'sentinel2'
FROM date_series d
CROSS JOIN fields f;

-- Generate NDVI for large coastal fields (Al-Hudaydah)
WITH date_series AS (
    SELECT
        generate_series(
            CURRENT_DATE - INTERVAL '150 days',
            CURRENT_DATE - INTERVAL '1 day',
            '5 days'::interval
        )::date AS obs_date
),
ndvi_data AS (
    SELECT
        obs_date,
        EXTRACT(DAY FROM (obs_date - (CURRENT_DATE - INTERVAL '150 days')))::INTEGER as days_since_planting
    FROM date_series
),
fields AS (
    SELECT unnest(ARRAY[
        'fd551111-1111-1111-1111-111111111111',
        'fd551111-2222-2222-2222-222222222222',
        'fd551111-3333-3333-3333-333333333333'
    ]::UUID[]) as field_id
)
INSERT INTO ndvi_observations (
    tenant_id, field_id, obs_date,
    ndvi_mean, ndvi_min, ndvi_max, ndvi_std,
    cloud_coverage, confidence, pixel_count,
    source
)
SELECT
    'tenant-sahool-main'::UUID,
    f.field_id,
    n.obs_date,
    g.ndvi_mean,
    g.ndvi_min,
    g.ndvi_max,
    g.ndvi_std,
    g.cloud_coverage,
    g.confidence,
    3500 + (random() * 500)::INTEGER,  -- Large fields = more pixels
    'sentinel2'
FROM ndvi_data n
CROSS JOIN fields f
CROSS JOIN LATERAL generate_ndvi_for_stage(n.days_since_planting) g
WHERE g.cloud_coverage < 0.5;

-- ========================================
-- INSERT SAMPLE NDVI ALERTS
-- ========================================

-- Insert alerts for anomalies (low NDVI in expected high growth period)
INSERT INTO ndvi_alerts (
    tenant_id, field_id, observation_id,
    alert_type, severity,
    current_value, threshold_value, deviation_pct, z_score,
    message, message_ar,
    acknowledged
)
SELECT
    tenant_id,
    field_id,
    id as observation_id,
    'anomaly_negative',
    CASE
        WHEN ndvi_mean < 0.30 THEN 'high'
        WHEN ndvi_mean < 0.40 THEN 'medium'
        ELSE 'low'
    END,
    ndvi_mean,
    0.50,  -- Expected threshold
    ((0.50 - ndvi_mean) / 0.50 * 100),
    ((0.50 - ndvi_mean) / 0.15),  -- Assuming std dev of 0.15
    'NDVI below expected range for this growth stage',
    'قيمة NDVI أقل من المتوقع لهذه المرحلة من النمو',
    false
FROM ndvi_observations
WHERE ndvi_mean < 0.40
    AND obs_date > CURRENT_DATE - INTERVAL '60 days'
    AND obs_date BETWEEN (CURRENT_DATE - INTERVAL '90 days') AND (CURRENT_DATE - INTERVAL '30 days')
LIMIT 15;

-- Insert alerts for sudden drops
WITH ndvi_changes AS (
    SELECT
        n1.id,
        n1.tenant_id,
        n1.field_id,
        n1.obs_date,
        n1.ndvi_mean as current_ndvi,
        LAG(n1.ndvi_mean) OVER (PARTITION BY n1.field_id ORDER BY n1.obs_date) as previous_ndvi
    FROM ndvi_observations n1
    WHERE n1.obs_date > CURRENT_DATE - INTERVAL '90 days'
)
INSERT INTO ndvi_alerts (
    tenant_id, field_id, observation_id,
    alert_type, severity,
    current_value, threshold_value, deviation_pct,
    message, message_ar,
    acknowledged
)
SELECT
    tenant_id,
    field_id,
    id,
    'threshold_breach',
    'medium',
    current_ndvi,
    previous_ndvi,
    ((previous_ndvi - current_ndvi) / previous_ndvi * 100),
    'Significant NDVI drop detected - possible stress or damage',
    'انخفاض كبير في NDVI - احتمال إجهاد أو ضرر',
    false
FROM ndvi_changes
WHERE previous_ndvi IS NOT NULL
    AND current_ndvi < previous_ndvi * 0.85  -- More than 15% drop
    AND current_ndvi > 0.20  -- Not just bare soil
LIMIT 10;

-- Verification queries
SELECT
    COUNT(*) as total_observations,
    COUNT(DISTINCT field_id) as fields_monitored,
    MIN(obs_date) as earliest_observation,
    MAX(obs_date) as latest_observation,
    ROUND(AVG(ndvi_mean)::numeric, 3) as avg_ndvi,
    ROUND(AVG(cloud_coverage)::numeric, 3) as avg_cloud_cover
FROM ndvi_observations;

SELECT
    f.name as field_name,
    COUNT(n.id) as observation_count,
    ROUND(AVG(n.ndvi_mean)::numeric, 3) as avg_ndvi,
    ROUND(MAX(n.ndvi_mean)::numeric, 3) as max_ndvi,
    ROUND(MIN(n.ndvi_mean)::numeric, 3) as min_ndvi,
    MAX(n.obs_date) as latest_observation
FROM ndvi_observations n
JOIN fields f ON n.field_id = f.id
GROUP BY f.id, f.name
ORDER BY observation_count DESC
LIMIT 10;

SELECT
    alert_type,
    severity,
    COUNT(*) as alert_count,
    COUNT(*) FILTER (WHERE acknowledged) as acknowledged_count,
    COUNT(*) FILTER (WHERE NOT acknowledged) as pending_count
FROM ndvi_alerts
GROUP BY alert_type, severity
ORDER BY alert_type, severity;

-- Show recent alerts
SELECT
    a.alert_type,
    a.severity,
    f.name as field_name,
    fm.name as farm_name,
    a.current_value,
    a.message,
    a.message_ar,
    a.created_at
FROM ndvi_alerts a
JOIN fields f ON a.field_id = f.id
JOIN farms fm ON f.farm_id = fm.id
WHERE NOT a.acknowledged
ORDER BY a.created_at DESC
LIMIT 20;
