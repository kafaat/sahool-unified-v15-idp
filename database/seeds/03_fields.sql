-- SAHOOL Fields Seed Data
-- Sample fields with GeoJSON boundaries

-- Clean existing data (optional - comment out for production)
-- TRUNCATE TABLE fields CASCADE;

-- Farm 1: Green Valley Farm (Sana'a) - 2 fields
INSERT INTO fields (
    id, tenant_id, farm_id, name, name_ar,
    boundary_geojson, center_latitude, center_longitude,
    area_hectares, soil_type, irrigation_type, status,
    current_crop_id, created_at, updated_at
)
VALUES
(
    'fd111111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    '11111111-1111-1111-1111-111111111111',
    'North Field',
    'الحقل الشمالي',
    '{"type":"Polygon","coordinates":[[[44.2066,15.3547],[44.2076,15.3547],[44.2076,15.3557],[44.2066,15.3557],[44.2066,15.3547]]]}',
    15.3552,
    44.2071,
    12.5,
    'loamy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '6 months',
    NOW()
),
(
    'fd111111-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    '11111111-1111-1111-1111-111111111111',
    'South Field',
    'الحقل الجنوبي',
    '{"type":"Polygon","coordinates":[[[44.2066,15.3537],[44.2076,15.3537],[44.2076,15.3547],[44.2066,15.3547],[44.2066,15.3537]]]}',
    15.3542,
    44.2071,
    13.0,
    'clay',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '6 months',
    NOW()
);

-- Farm 2: Al-Haymah Agricultural Project (Sana'a) - 3 fields
INSERT INTO fields (
    id, tenant_id, farm_id, name, name_ar,
    boundary_geojson, center_latitude, center_longitude,
    area_hectares, soil_type, irrigation_type, status,
    current_crop_id, created_at, updated_at
)
VALUES
(
    'fd112222-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    '11111111-2222-2222-2222-222222222222',
    'East Terrace',
    'المصطبة الشرقية',
    '{"type":"Polygon","coordinates":[[[44.3185,15.2894],[44.3195,15.2894],[44.3195,15.2904],[44.3185,15.2904],[44.3185,15.2894]]]}',
    15.2899,
    44.3190,
    5.1,
    'loamy',
    'sprinkler',
    'active',
    NULL,
    NOW() - INTERVAL '4 months',
    NOW()
),
(
    'fd112222-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    '11111111-2222-2222-2222-222222222222',
    'West Terrace',
    'المصطبة الغربية',
    '{"type":"Polygon","coordinates":[[[44.3175,15.2894],[44.3185,15.2894],[44.3185,15.2904],[44.3175,15.2904],[44.3175,15.2894]]]}',
    15.2899,
    44.3180,
    5.2,
    'silty',
    'sprinkler',
    'active',
    NULL,
    NOW() - INTERVAL '4 months',
    NOW()
),
(
    'fd112222-3333-3333-3333-333333333333',
    'tenant-sahool-main',
    '11111111-2222-2222-2222-222222222222',
    'Valley Bottom',
    'قاع الوادي',
    '{"type":"Polygon","coordinates":[[[44.3175,15.2884],[44.3195,15.2884],[44.3195,15.2894],[44.3175,15.2894],[44.3175,15.2884]]]}',
    15.2889,
    44.3185,
    5.0,
    'clay',
    'flood',
    'active',
    NULL,
    NOW() - INTERVAL '4 months',
    NOW()
);

-- Farm 3: Al-Mawasit Coffee Estate (Ta'izz) - 2 fields
INSERT INTO fields (
    id, tenant_id, farm_id, name, name_ar,
    boundary_geojson, center_latitude, center_longitude,
    area_hectares, soil_type, irrigation_type, status,
    current_crop_id, created_at, updated_at
)
VALUES
(
    'fd221111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    '22222222-1111-1111-1111-111111111111',
    'Upper Mountain Slope',
    'المنحدر الجبلي العلوي',
    '{"type":"Polygon","coordinates":[[[44.0216,13.5795],[44.0226,13.5795],[44.0226,13.5805],[44.0216,13.5805],[44.0216,13.5795]]]}',
    13.5800,
    44.0221,
    6.4,
    'loamy',
    'rainfed',
    'active',
    NULL,
    NOW() - INTERVAL '4 months',
    NOW()
),
(
    'fd221111-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    '22222222-1111-1111-1111-111111111111',
    'Lower Mountain Slope',
    'المنحدر الجبلي السفلي',
    '{"type":"Polygon","coordinates":[[[44.0216,13.5785],[44.0226,13.5785],[44.0226,13.5795],[44.0216,13.5795],[44.0216,13.5785]]]}',
    13.5790,
    44.0221,
    6.4,
    'sandy',
    'rainfed',
    'active',
    NULL,
    NOW() - INTERVAL '4 months',
    NOW()
);

-- Farm 4: Sabr Terraced Farms (Ta'izz) - 3 fields
INSERT INTO fields (
    id, tenant_id, farm_id, name, name_ar,
    boundary_geojson, center_latitude, center_longitude,
    area_hectares, soil_type, irrigation_type, status,
    current_crop_id, created_at, updated_at
)
VALUES
(
    'fd222222-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    '22222222-2222-2222-2222-222222222222',
    'Top Terrace',
    'المصطبة العليا',
    '{"type":"Polygon","coordinates":[[[44.0389,13.6547],[44.0399,13.6547],[44.0399,13.6557],[44.0389,13.6557],[44.0389,13.6547]]]}',
    13.6552,
    44.0394,
    2.7,
    'loamy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '3 months',
    NOW()
),
(
    'fd222222-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    '22222222-2222-2222-2222-222222222222',
    'Middle Terrace',
    'المصطبة الوسطى',
    '{"type":"Polygon","coordinates":[[[44.0389,13.6537],[44.0399,13.6537],[44.0399,13.6547],[44.0389,13.6547],[44.0389,13.6537]]]}',
    13.6542,
    44.0394,
    2.8,
    'loamy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '3 months',
    NOW()
),
(
    'fd222222-3333-3333-3333-333333333333',
    'tenant-sahool-main',
    '22222222-2222-2222-2222-222222222222',
    'Lower Terrace',
    'المصطبة السفلى',
    '{"type":"Polygon","coordinates":[[[44.0389,13.6527],[44.0399,13.6527],[44.0399,13.6537],[44.0389,13.6537],[44.0389,13.6527]]]}',
    13.6532,
    44.0394,
    2.7,
    'clay',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '3 months',
    NOW()
);

-- Farm 5: Wadi Hadramout Date Farm (Hadramout) - 4 fields
INSERT INTO fields (
    id, tenant_id, farm_id, name, name_ar,
    boundary_geojson, center_latitude, center_longitude,
    area_hectares, soil_type, irrigation_type, status,
    current_crop_id, created_at, updated_at
)
VALUES
(
    'fd331111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    '33333333-1111-1111-1111-111111111111',
    'North Palm Grove',
    'بستان النخيل الشمالي',
    '{"type":"Polygon","coordinates":[[[48.7825,15.9288],[48.7845,15.9288],[48.7845,15.9308],[48.7825,15.9308],[48.7825,15.9288]]]}',
    15.9298,
    48.7835,
    11.25,
    'sandy',
    'flood',
    'active',
    NULL,
    NOW() - INTERVAL '8 months',
    NOW()
),
(
    'fd331111-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    '33333333-1111-1111-1111-111111111111',
    'South Palm Grove',
    'بستان النخيل الجنوبي',
    '{"type":"Polygon","coordinates":[[[48.7825,15.9268],[48.7845,15.9268],[48.7845,15.9288],[48.7825,15.9288],[48.7825,15.9268]]]}',
    15.9278,
    48.7835,
    11.25,
    'sandy',
    'flood',
    'active',
    NULL,
    NOW() - INTERVAL '8 months',
    NOW()
),
(
    'fd331111-3333-3333-3333-333333333333',
    'tenant-sahool-main',
    '33333333-1111-1111-1111-111111111111',
    'East Palm Grove',
    'بستان النخيل الشرقي',
    '{"type":"Polygon","coordinates":[[[48.7845,15.9268],[48.7865,15.9268],[48.7865,15.9288],[48.7845,15.9288],[48.7845,15.9268]]]}',
    15.9278,
    48.7855,
    11.25,
    'loamy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '8 months',
    NOW()
),
(
    'fd331111-4444-4444-4444-444444444444',
    'tenant-sahool-main',
    '33333333-1111-1111-1111-111111111111',
    'West Palm Grove',
    'بستان النخيل الغربي',
    '{"type":"Polygon","coordinates":[[[48.7805,15.9268],[48.7825,15.9268],[48.7825,15.9288],[48.7805,15.9288],[48.7805,15.9268]]]}',
    15.9278,
    48.7815,
    11.25,
    'silty',
    'flood',
    'active',
    NULL,
    NOW() - INTERVAL '8 months',
    NOW()
);

-- Farm 6: Al-Mukalla Coastal Farm (Hadramout) - 3 fields
INSERT INTO fields (
    id, tenant_id, farm_id, name, name_ar,
    boundary_geojson, center_latitude, center_longitude,
    area_hectares, soil_type, irrigation_type, status,
    current_crop_id, created_at, updated_at
)
VALUES
(
    'fd332222-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    '33333333-2222-2222-2222-222222222222',
    'Coastal Strip A',
    'الشريط الساحلي أ',
    '{"type":"Polygon","coordinates":[[[49.1242,14.5425],[49.1262,14.5425],[49.1262,14.5445],[49.1242,14.5445],[49.1242,14.5425]]]}',
    14.5435,
    49.1252,
    10.0,
    'sandy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '6 months',
    NOW()
),
(
    'fd332222-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    '33333333-2222-2222-2222-222222222222',
    'Coastal Strip B',
    'الشريط الساحلي ب',
    '{"type":"Polygon","coordinates":[[[49.1242,14.5405],[49.1262,14.5405],[49.1262,14.5425],[49.1242,14.5425],[49.1242,14.5405]]]}',
    14.5415,
    49.1252,
    10.1,
    'sandy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '6 months',
    NOW()
),
(
    'fd332222-3333-3333-3333-333333333333',
    'tenant-sahool-main',
    '33333333-2222-2222-2222-222222222222',
    'Coastal Strip C',
    'الشريط الساحلي ج',
    '{"type":"Polygon","coordinates":[[[49.1242,14.5385],[49.1262,14.5385],[49.1262,14.5405],[49.1242,14.5405],[49.1242,14.5385]]]}',
    14.5395,
    49.1252,
    10.1,
    'loamy',
    'sprinkler',
    'active',
    NULL,
    NOW() - INTERVAL '6 months',
    NOW()
);

-- Farm 7: Ibb Green Mountain Farm - 3 fields
INSERT INTO fields (
    id, tenant_id, farm_id, name, name_ar,
    boundary_geojson, center_latitude, center_longitude,
    area_hectares, soil_type, irrigation_type, status,
    current_crop_id, created_at, updated_at
)
VALUES
(
    'fd441111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    '44444444-1111-1111-1111-111111111111',
    'Highland Field 1',
    'حقل المرتفعات ١',
    '{"type":"Polygon","coordinates":[[[44.1667,13.9667],[44.1677,13.9667],[44.1677,13.9677],[44.1667,13.9677],[44.1667,13.9667]]]}',
    13.9672,
    44.1672,
    6.2,
    'loamy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '3 months',
    NOW()
),
(
    'fd441111-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    '44444444-1111-1111-1111-111111111111',
    'Highland Field 2',
    'حقل المرتفعات ٢',
    '{"type":"Polygon","coordinates":[[[44.1667,13.9657],[44.1677,13.9657],[44.1677,13.9667],[44.1667,13.9667],[44.1667,13.9657]]]}',
    13.9662,
    44.1672,
    6.2,
    'clay',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '3 months',
    NOW()
),
(
    'fd441111-3333-3333-3333-333333333333',
    'tenant-sahool-main',
    '44444444-1111-1111-1111-111111111111',
    'Highland Field 3',
    'حقل المرتفعات ٣',
    '{"type":"Polygon","coordinates":[[[44.1677,13.9657],[44.1687,13.9657],[44.1687,13.9677],[44.1677,13.9677],[44.1677,13.9657]]]}',
    13.9667,
    44.1682,
    6.1,
    'loamy',
    'sprinkler',
    'active',
    NULL,
    NOW() - INTERVAL '3 months',
    NOW()
);

-- Farm 8: Jiblah Heritage Farm - 2 fields
INSERT INTO fields (
    id, tenant_id, farm_id, name, name_ar,
    boundary_geojson, center_latitude, center_longitude,
    area_hectares, soil_type, irrigation_type, status,
    current_crop_id, created_at, updated_at
)
VALUES
(
    'fd442222-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    '44444444-2222-2222-2222-222222222222',
    'Heritage Plot East',
    'القطعة التراثية الشرقية',
    '{"type":"Polygon","coordinates":[[[44.1444,13.9172],[44.1454,13.9172],[44.1454,13.9182],[44.1444,13.9182],[44.1444,13.9172]]]}',
    13.9177,
    44.1449,
    5.3,
    'loamy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '2 months',
    NOW()
),
(
    'fd442222-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    '44444444-2222-2222-2222-222222222222',
    'Heritage Plot West',
    'القطعة التراثية الغربية',
    '{"type":"Polygon","coordinates":[[[44.1434,13.9172],[44.1444,13.9172],[44.1444,13.9182],[44.1434,13.9182],[44.1434,13.9172]]]}',
    13.9177,
    44.1439,
    5.4,
    'silty',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '2 months',
    NOW()
);

-- Farm 9: Red Sea Agricultural Complex - 3 fields (large)
INSERT INTO fields (
    id, tenant_id, farm_id, name, name_ar,
    boundary_geojson, center_latitude, center_longitude,
    area_hectares, soil_type, irrigation_type, status,
    current_crop_id, created_at, updated_at
)
VALUES
(
    'fd551111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    '55555555-1111-1111-1111-111111111111',
    'North Complex Section',
    'القسم الشمالي للمجمع',
    '{"type":"Polygon","coordinates":[[[42.9545,14.7978],[42.9595,14.7978],[42.9595,14.8028],[42.9545,14.8028],[42.9545,14.7978]]]}',
    14.8003,
    42.9570,
    33.3,
    'sandy',
    'sprinkler',
    'active',
    NULL,
    NOW() - INTERVAL '5 months',
    NOW()
),
(
    'fd551111-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    '55555555-1111-1111-1111-111111111111',
    'Central Complex Section',
    'القسم الأوسط للمجمع',
    '{"type":"Polygon","coordinates":[[[42.9545,14.7928],[42.9595,14.7928],[42.9595,14.7978],[42.9545,14.7978],[42.9545,14.7928]]]}',
    14.7953,
    42.9570,
    33.3,
    'loamy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '5 months',
    NOW()
),
(
    'fd551111-3333-3333-3333-333333333333',
    'tenant-sahool-main',
    '55555555-1111-1111-1111-111111111111',
    'South Complex Section',
    'القسم الجنوبي للمجمع',
    '{"type":"Polygon","coordinates":[[[42.9545,14.7878],[42.9595,14.7878],[42.9595,14.7928],[42.9545,14.7928],[42.9545,14.7878]]]}',
    14.7903,
    42.9570,
    33.4,
    'clay',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '5 months',
    NOW()
);

-- Farm 10: Tihama Plains Farm - 4 fields
INSERT INTO fields (
    id, tenant_id, farm_id, name, name_ar,
    boundary_geojson, center_latitude, center_longitude,
    area_hectares, soil_type, irrigation_type, status,
    current_crop_id, created_at, updated_at
)
VALUES
(
    'fd552222-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    '55555555-2222-2222-2222-222222222222',
    'Plains Section A',
    'قسم السهول أ',
    '{"type":"Polygon","coordinates":[[[43.0125,14.6547],[43.0155,14.6547],[43.0155,14.6577],[43.0125,14.6577],[43.0125,14.6547]]]}',
    14.6562,
    43.0140,
    18.9,
    'loamy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '4 months',
    NOW()
),
(
    'fd552222-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    '55555555-2222-2222-2222-222222222222',
    'Plains Section B',
    'قسم السهول ب',
    '{"type":"Polygon","coordinates":[[[43.0125,14.6517],[43.0155,14.6517],[43.0155,14.6547],[43.0125,14.6547],[43.0125,14.6517]]]}',
    14.6532,
    43.0140,
    18.9,
    'sandy',
    'sprinkler',
    'active',
    NULL,
    NOW() - INTERVAL '4 months',
    NOW()
),
(
    'fd552222-3333-3333-3333-333333333333',
    'tenant-sahool-main',
    '55555555-2222-2222-2222-222222222222',
    'Plains Section C',
    'قسم السهول ج',
    '{"type":"Polygon","coordinates":[[[43.0155,14.6517],[43.0185,14.6517],[43.0185,14.6547],[43.0155,14.6547],[43.0155,14.6517]]]}',
    14.6532,
    43.0170,
    18.9,
    'loamy',
    'drip',
    'active',
    NULL,
    NOW() - INTERVAL '4 months',
    NOW()
),
(
    'fd552222-4444-4444-4444-444444444444',
    'tenant-sahool-main',
    '55555555-2222-2222-2222-222222222222',
    'Plains Section D',
    'قسم السهول د',
    '{"type":"Polygon","coordinates":[[[43.0155,14.6547],[43.0185,14.6547],[43.0185,14.6577],[43.0155,14.6577],[43.0155,14.6547]]]}',
    14.6562,
    43.0170,
    18.8,
    'silty',
    'sprinkler',
    'active',
    NULL,
    NOW() - INTERVAL '4 months',
    NOW()
);

-- Verification queries
SELECT
    f.name as field_name,
    f.name_ar as field_name_ar,
    fm.name as farm_name,
    fm.governorate,
    f.area_hectares,
    f.soil_type,
    f.irrigation_type,
    f.status
FROM fields f
JOIN farms fm ON f.farm_id = fm.id
ORDER BY fm.governorate, fm.name, f.name;

-- Summary by soil type and irrigation
SELECT
    soil_type,
    irrigation_type,
    COUNT(*) as field_count,
    ROUND(SUM(area_hectares)::numeric, 2) as total_hectares
FROM fields
GROUP BY soil_type, irrigation_type
ORDER BY soil_type, irrigation_type;

-- Summary by governorate
SELECT
    fm.governorate,
    COUNT(f.id) as field_count,
    ROUND(SUM(f.area_hectares)::numeric, 2) as total_hectares,
    ROUND(AVG(f.area_hectares)::numeric, 2) as avg_hectares
FROM fields f
JOIN farms fm ON f.farm_id = fm.id
GROUP BY fm.governorate
ORDER BY fm.governorate;
