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
-- ║  This file contains:                                                         ║
-- ║  - Hardcoded passwords (admin, manager123, etc.)                             ║
-- ║  - Test user accounts                                                        ║
-- ║  - Sample data that may not be suitable for production                       ║
-- ║                                                                               ║
-- ║  For production deployments:                                                 ║
-- ║  1. Remove or rename this file                                               ║
-- ║  2. Or set SKIP_DEMO_DATA=true environment variable                          ║
-- ║  3. Create production users via secure admin API                             ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
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
-- DEMO USERS
-- ═══════════════════════════════════════════════════════════════════════════════
-- WARNING: These passwords are for DEVELOPMENT ONLY
-- Password hashes are generated using bcrypt with cost factor 12

-- Admin user (password: admin)
INSERT INTO users (id, tenant_id, email, password_hash, first_name, last_name, role, status, email_verified)
VALUES (
    'b0000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'n@admin.com',
    crypt('admin', gen_salt('bf', 12)),
    'Admin',
    'User',
    'ADMIN',
    'ACTIVE',
    true
) ON CONFLICT (email) DO UPDATE SET
    password_hash = crypt('admin', gen_salt('bf', 12)),
    role = 'ADMIN',
    status = 'ACTIVE';

-- Additional demo users
INSERT INTO users (id, tenant_id, email, password_hash, first_name, last_name, role, status, email_verified)
VALUES
    ('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'manager@sahool.io', crypt('manager123', gen_salt('bf', 12)), 'Farm', 'Manager', 'MANAGER', 'ACTIVE', true),
    ('b0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', 'agronomist@sahool.io', crypt('agro123', gen_salt('bf', 12)), 'Ahmed', 'Al-Rashid', 'FARMER', 'ACTIVE', true),
    ('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000001', 'worker@sahool.io', crypt('worker123', gen_salt('bf', 12)), 'Mohammed', 'Ali', 'WORKER', 'ACTIVE', true),
    ('b0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000001', 'researcher@sahool.io', crypt('research123', gen_salt('bf', 12)), 'Fatima', 'Hassan', 'VIEWER', 'ACTIVE', true)
ON CONFLICT (email) DO NOTHING;

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
-- DEMO FIELDS
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO fields (id, tenant_id, owner_id, name, name_ar, governorate, district, soil_type, irrigation_type, current_crop_id, status, health_score, boundary, area_hectares)
VALUES
    (
        'd0000000-0000-0000-0000-000000000001',
        'a0000000-0000-0000-0000-000000000001',
        'b0000000-0000-0000-0000-000000000002',
        'North Field',
        'الحقل الشمالي',
        'Riyadh',
        'Al-Kharj',
        'loam',
        'drip',
        'c0000000-0000-0000-0000-000000000001',
        'active',
        85.5,
        ST_GeomFromText('POLYGON((46.7 24.1, 46.71 24.1, 46.71 24.11, 46.7 24.11, 46.7 24.1))', 4326),
        120.5
    ),
    (
        'd0000000-0000-0000-0000-000000000002',
        'a0000000-0000-0000-0000-000000000001',
        'b0000000-0000-0000-0000-000000000002',
        'South Field',
        'الحقل الجنوبي',
        'Riyadh',
        'Al-Kharj',
        'sandy',
        'center_pivot',
        'c0000000-0000-0000-0000-000000000003',
        'active',
        78.2,
        ST_GeomFromText('POLYGON((46.72 24.08, 46.73 24.08, 46.73 24.09, 46.72 24.09, 46.72 24.08))', 4326),
        85.0
    ),
    (
        'd0000000-0000-0000-0000-000000000003',
        'a0000000-0000-0000-0000-000000000001',
        'b0000000-0000-0000-0000-000000000003',
        'East Greenhouse',
        'البيت المحمي الشرقي',
        'Riyadh',
        'Al-Kharj',
        'mixed',
        'drip',
        'c0000000-0000-0000-0000-000000000004',
        'active',
        92.0,
        ST_GeomFromText('POLYGON((46.74 24.1, 46.745 24.1, 46.745 24.105, 46.74 24.105, 46.74 24.1))', 4326),
        2.5
    )
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO FIELD CROPS
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO field_crops (id, field_id, crop_id, tenant_id, planting_date, expected_harvest_date, status, growth_stage, planted_area_hectares)
VALUES
    ('e0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', '2025-01-15', '2025-05-15', 'growing', 'vegetative', 120.5),
    ('e0000000-0000-0000-0000-000000000002', 'd0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', '2020-03-01', '2025-09-01', 'growing', 'fruiting', 85.0),
    ('e0000000-0000-0000-0000-000000000003', 'd0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000001', '2025-02-01', '2025-05-01', 'growing', 'flowering', 2.5)
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO TASKS
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO tasks (task_id, tenant_id, field_id, title, title_ar, task_type, status, priority, assigned_to, created_by, due_date)
VALUES
    ('f0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'Apply fertilizer', 'تطبيق السماد', 'fertilization', 'pending', 'high', 'b0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000001', CURRENT_DATE + 2),
    ('f0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000002', 'Irrigation check', 'فحص الري', 'irrigation', 'scheduled', 'medium', 'b0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000001', CURRENT_DATE + 1),
    ('f0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000003', 'Pest inspection', 'فحص الآفات', 'inspection', 'pending', 'high', 'b0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000001', CURRENT_DATE + 3),
    ('f0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'Soil sampling', 'أخذ عينات التربة', 'soil_prep', 'completed', 'low', 'b0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000001', CURRENT_DATE - 2)
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO NDVI RECORDS
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO ndvi_records (id, field_id, tenant_id, capture_date, satellite, cloud_coverage_percent, ndvi_mean, ndvi_min, ndvi_max, classification, health_score, trend)
VALUES
    ('00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', CURRENT_DATE - 7, 'Sentinel-2', 5.2, 0.72, 0.45, 0.89, 'good', 85.5, 'improving'),
    ('00000000-0000-0000-0001-000000000002', 'd0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', CURRENT_DATE - 14, 'Sentinel-2', 8.1, 0.68, 0.42, 0.85, 'good', 82.0, 'stable'),
    ('00000000-0000-0000-0001-000000000003', 'd0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', CURRENT_DATE - 7, 'Landsat-8', 3.5, 0.65, 0.38, 0.82, 'moderate', 78.2, 'stable'),
    ('00000000-0000-0000-0001-000000000004', 'd0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', CURRENT_DATE - 5, 'Sentinel-2', 2.0, 0.85, 0.72, 0.95, 'excellent', 92.0, 'improving')
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO IOT DEVICES
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO iot_devices (id, tenant_id, field_id, device_id, device_type, name, name_ar, status, battery_level)
VALUES
    ('00000000-0000-0000-0002-000000000001', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'SOIL-001', 'soil_sensor', 'Soil Sensor North-1', 'مستشعر التربة شمال-1', 'online', 85.0),
    ('00000000-0000-0000-0002-000000000002', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'WEATHER-001', 'weather_station', 'Weather Station Main', 'محطة الطقس الرئيسية', 'online', 92.0),
    ('00000000-0000-0000-0002-000000000003', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000002', 'WATER-001', 'water_meter', 'Water Meter South', 'عداد المياه الجنوبي', 'online', 78.0),
    ('00000000-0000-0000-0002-000000000004', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000003', 'CAM-001', 'camera', 'Greenhouse Camera', 'كاميرا البيت المحمي', 'online', 100.0)
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO IOT READINGS
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO iot_readings (id, device_id, tenant_id, recorded_at, readings, soil_moisture, soil_temperature, air_temperature, humidity)
VALUES
    ('00000000-0000-0000-0003-000000000001', '00000000-0000-0000-0002-000000000001', 'a0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '1 hour', '{"moisture": 45.2, "temperature": 22.5, "ec": 1.2}', 45.2, 22.5, 28.0, 55.0),
    ('00000000-0000-0000-0003-000000000002', '00000000-0000-0000-0002-000000000001', 'a0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '2 hours', '{"moisture": 44.8, "temperature": 23.0, "ec": 1.1}', 44.8, 23.0, 29.0, 52.0),
    ('00000000-0000-0000-0003-000000000003', '00000000-0000-0000-0002-000000000002', 'a0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '1 hour', '{"temperature": 28.5, "humidity": 45, "pressure": 1013}', NULL, NULL, 28.5, 45.0)
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO ALERTS
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

-- DEMO WALLETS - REMOVED
-- Tables now managed by Prisma ORM (marketplace-service)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO EXPERIMENT
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO experiments (id, tenant_id, title, title_ar, description, hypothesis, start_date, status, principal_researcher_id)
VALUES
    ('00000000-0000-0000-0007-000000000001', 'a0000000-0000-0000-0000-000000000001', 'Drought-Resistant Wheat Varieties Trial', 'تجربة أصناف القمح المقاومة للجفاف', 'Testing 5 wheat varieties for drought resistance in Al-Kharj region', 'Variety X-15 will show 20% higher yield under water stress conditions', '2025-01-01', 'active', 'b0000000-0000-0000-0000-000000000005')
ON CONFLICT DO NOTHING;

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
    user_count INTEGER;
    field_count INTEGER;
    crop_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users WHERE tenant_id = 'a0000000-0000-0000-0000-000000000001';
    SELECT COUNT(*) INTO field_count FROM fields WHERE tenant_id = 'a0000000-0000-0000-0000-000000000001';
    SELECT COUNT(*) INTO crop_count FROM crops;

    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  DEMO DATA LOADED SUCCESSFULLY';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  Demo Users: %', user_count;
    RAISE NOTICE '  Demo Fields: %', field_count;
    RAISE NOTICE '  Crop Types: %', crop_count;
    RAISE NOTICE '';
    RAISE NOTICE '  Demo Admin Login:';
    RAISE NOTICE '    Email: n@admin.com';
    RAISE NOTICE '    Password: admin';
    RAISE NOTICE '';
    RAISE NOTICE '  WARNING: This is demo data for development only!';
    RAISE NOTICE '  Do NOT use these credentials in production.';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
END;
$$;
