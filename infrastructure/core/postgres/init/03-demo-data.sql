-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform v16.0.0 - Demo Data
-- بيانات تجريبية - للتطوير والاختبار فقط
-- ═══════════════════════════════════════════════════════════════════════════════
-- This file contains DEMO DATA for development and testing environments.
--
-- SECURITY WARNING:
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║  DO NOT RUN THIS FILE IN PRODUCTION ENVIRONMENTS                             ║
-- ║                                                                               ║
-- ║  For production deployments:                                                 ║
-- ║  1. Remove or rename this file                                               ║
-- ║  2. Or set SKIP_DEMO_DATA=true environment variable                          ║
-- ║  3. Create production users via secure admin API                             ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
--
-- NOTE: Demo data for Prisma-managed tables (users, fields, tasks, IoT devices,
-- experiments, chat, marketplace, etc.) should be inserted via each NestJS
-- service's own seed mechanism (prisma db seed) after the services start.
--
-- This file only seeds tables managed by the init script (00-init-sahool.sql):
--   tenants, crops, alerts, anwa_events, weather_records, weather_forecasts,
--   audit_logs, ai_consultations, equipment, equipment_maintenance
--
-- Usage:
--   Development: Keep this file as-is (03-demo-data.sql)
--   Production:  Rename to 03-demo-data.sql.bak or delete
--                Or use: docker-compose.prod.yml which excludes this file
-- ═══════════════════════════════════════════════════════════════════════════════

-- Check if we should skip demo data
DO $$
BEGIN
    -- Skip if SKIP_DEMO_DATA environment variable is set
    -- Note: This requires the variable to be passed to psql
    IF current_setting('app.skip_demo_data', true) = 'true' THEN
        RAISE NOTICE 'SKIP_DEMO_DATA is set - skipping demo data insertion';
        RETURN;
    END IF;

    RAISE NOTICE 'Loading demo data for development/testing environment...';
END;
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO TENANT
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO tenants (id, name, name_ar, slug, subscription_tier, subscription_status, max_users, max_fields, contact_email)
VALUES (
    'a0000000-0000-0000-0000-000000000001',
    'Sahool Demo Farm',
    'مزرعة سهول التجريبية',
    'sahool-demo',
    'enterprise',
    'active',
    100,
    1000,
    'admin@sahool.io'
) ON CONFLICT (slug) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO USERS - REMOVED
-- Users table is now managed by Prisma ORM (user-service)
-- Seed demo users via: cd apps/services/user-service && npx prisma db seed
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO CROPS (Master Data)
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO crops (id, name_en, name_ar, scientific_name, category, min_temp_celsius, max_temp_celsius, water_needs, growth_duration_days, is_active)
VALUES
    ('c0000000-0000-0000-0000-000000000001', 'Wheat', 'القمح', 'Triticum aestivum', 'grains', 5, 35, 'medium', 120, true),
    ('c0000000-0000-0000-0000-000000000002', 'Barley', 'الشعير', 'Hordeum vulgare', 'grains', 5, 30, 'low', 90, true),
    ('c0000000-0000-0000-0000-000000000003', 'Date Palm', 'النخيل', 'Phoenix dactylifera', 'fruits', 10, 50, 'low', 365, true),
    ('c0000000-0000-0000-0000-000000000004', 'Tomato', 'الطماطم', 'Solanum lycopersicum', 'vegetables', 15, 35, 'high', 90, true),
    ('c0000000-0000-0000-0000-000000000005', 'Alfalfa', 'البرسيم', 'Medicago sativa', 'fodder', 10, 40, 'high', 60, true),
    ('c0000000-0000-0000-0000-000000000006', 'Cucumber', 'الخيار', 'Cucumis sativus', 'vegetables', 18, 35, 'high', 60, true),
    ('c0000000-0000-0000-0000-000000000007', 'Olive', 'الزيتون', 'Olea europaea', 'fruits', 5, 40, 'low', 365, true),
    ('c0000000-0000-0000-0000-000000000008', 'Grape', 'العنب', 'Vitis vinifera', 'fruits', 10, 40, 'medium', 180, true),
    ('c0000000-0000-0000-0000-000000000009', 'Citrus', 'الحمضيات', 'Citrus spp.', 'fruits', 10, 38, 'medium', 365, true),
    ('c0000000-0000-0000-0000-000000000010', 'Onion', 'البصل', 'Allium cepa', 'vegetables', 10, 30, 'medium', 120, true)
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO FIELDS - REMOVED
-- Fields table is now managed by Prisma ORM (field-management-service)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO FIELD CROPS - REMOVED
-- Table is now managed by Prisma ORM (field-management-service)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO TASKS - REMOVED
-- Tasks table is now managed by Prisma ORM (field-management-service)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO NDVI RECORDS - REMOVED
-- Table is now managed by Prisma ORM (field-management-service)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO IOT DEVICES - REMOVED
-- Table is now managed by Prisma ORM (iot-service)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO IOT READINGS - REMOVED
-- Table is now managed by Prisma ORM (iot-service)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO ALERTS
-- NOTE: field_id values reference fields that will be created by
-- field-management-service's Prisma migrations. No FK constraint enforced.
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO alerts (id, tenant_id, field_id, title, title_ar, message, message_ar, category, severity, status)
VALUES
    ('00000000-0000-0000-0004-000000000001', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'Low Soil Moisture', 'انخفاض رطوبة التربة', 'Soil moisture in North Field has dropped below 40%', 'انخفضت رطوبة التربة في الحقل الشمالي إلى أقل من 40%', 'irrigation', 'warning', 'active'),
    ('00000000-0000-0000-0004-000000000002', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000003', 'High Temperature Alert', 'تنبيه درجة حرارة مرتفعة', 'Greenhouse temperature exceeds 38°C', 'درجة حرارة البيت المحمي تتجاوز 38 درجة مئوية', 'weather', 'critical', 'active'),
    ('00000000-0000-0000-0004-000000000003', 'a0000000-0000-0000-0000-000000000001', NULL, 'Harvest Season Reminder', 'تذكير موسم الحصاد', 'Wheat harvest season approaching in 30 days', 'يقترب موسم حصاد القمح خلال 30 يوماً', 'harvest', 'info', 'active')
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO MARKETPLACE PRODUCTS - REMOVED
-- Tables now managed by Prisma ORM (marketplace-service)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO EXPERIMENT - REMOVED
-- Tables now managed by Prisma ORM (research-core)
-- ═══════════════════════════════════════════════════════════════════════════════


-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO ANWA EVENTS (Agricultural Calendar)
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO anwa_events (id, naw_id, naw_name_ar, naw_name_en, year, start_date, end_date, season, season_ar, suitable_crops, recommendations)
VALUES
    ('00000000-0000-0000-0008-000000000001', 1, 'الثريا', 'Al-Thurayya', 2025, '2025-06-07', '2025-06-19', 'summer', 'الصيف', '["dates", "grapes"]', '{"irrigation": "increase", "activities": ["harvest_dates"]}'),
    ('00000000-0000-0000-0008-000000000002', 2, 'الدبران', 'Al-Dabaran', 2025, '2025-06-20', '2025-07-02', 'summer', 'الصيف', '["dates", "melons"]', '{"irrigation": "maintain", "activities": ["protect_from_heat"]}'),
    ('00000000-0000-0000-0008-000000000003', 15, 'سعد الذابح', 'Saad Al-Thabeh', 2025, '2025-01-29', '2025-02-10', 'winter', 'الشتاء', '["wheat", "barley", "vegetables"]', '{"irrigation": "reduce", "activities": ["planting_grains"]}')
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO WEATHER RECORDS
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO weather_records (id, tenant_id, location_id, location_name, recorded_at, temperature_celsius, humidity_percent, wind_speed_ms, conditions, conditions_ar, source)
VALUES
    ('00000000-0000-0000-0009-000000000001', 'a0000000-0000-0000-0000-000000000001', 'al-kharj', 'Al-Kharj', NOW(), 32.5, 35.0, 4.2, 'Clear', 'صافي', 'openweather'),
    ('00000000-0000-0000-0009-000000000002', 'a0000000-0000-0000-0000-000000000001', 'al-kharj', 'Al-Kharj', NOW() - INTERVAL '1 day', 30.2, 40.0, 3.8, 'Partly Cloudy', 'غائم جزئياً', 'openweather')
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO DATA SUMMARY
-- ═══════════════════════════════════════════════════════════════════════════════

DO $$
DECLARE
    tenant_count INTEGER;
    crop_count INTEGER;
    alert_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO tenant_count FROM tenants;
    SELECT COUNT(*) INTO crop_count FROM crops;
    SELECT COUNT(*) INTO alert_count FROM alerts;

    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  DEMO DATA LOADED SUCCESSFULLY';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  Tenants: %', tenant_count;
    RAISE NOTICE '  Crop Types: %', crop_count;
    RAISE NOTICE '  Alerts: %', alert_count;
    RAISE NOTICE '';
    RAISE NOTICE '  NOTE: Demo data for users, fields, tasks, IoT, experiments,';
    RAISE NOTICE '  and chat should be seeded via NestJS services after startup:';
    RAISE NOTICE '    cd apps/services/<service> && npx prisma db seed';
    RAISE NOTICE '';
    RAISE NOTICE '  WARNING: This is demo data for development only!';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
END;
$$;
