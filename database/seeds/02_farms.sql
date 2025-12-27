-- SAHOOL Farms Seed Data
-- Sample farms in different Yemen governorates

-- Clean existing data (optional - comment out for production)
-- TRUNCATE TABLE farms CASCADE;

-- Insert Farms in Sana'a Governorate (صنعاء)

INSERT INTO farms (id, tenant_id, name, name_ar, owner_id, latitude, longitude, address, address_ar, region, governorate, total_area_hectares, status, created_at, updated_at)
VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    'Green Valley Farm',
    'مزرعة الوادي الأخضر',
    'f1111111-1111-1111-1111-111111111111', -- Ahmed Al-Sanani
    15.3547,
    44.2066,
    'Bani Matar District, Sana''a',
    'مديرية بني مطر، صنعاء',
    'Highland',
    'صنعاء',
    25.5,
    'active',
    NOW() - INTERVAL '6 months',
    NOW()
),
(
    '11111111-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    'Al-Haymah Agricultural Project',
    'مشروع الحيمة الزراعي',
    'f1111111-1111-1111-1111-111111111111', -- Ahmed Al-Sanani
    15.2894,
    44.3185,
    'Al-Haymah District, Sana''a',
    'مديرية الحيمة، صنعاء',
    'Highland',
    'صنعاء',
    15.3,
    'active',
    NOW() - INTERVAL '4 months',
    NOW()
);

-- Insert Farms in Ta'izz Governorate (تعز)

INSERT INTO farms (id, tenant_id, name, name_ar, owner_id, latitude, longitude, address, address_ar, region, governorate, total_area_hectares, status, created_at, updated_at)
VALUES
(
    '22222222-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    'Al-Mawasit Coffee Estate',
    'مزرعة المواسط للبن',
    'f2222222-2222-2222-2222-222222222222', -- Mohammed Al-Taizi
    13.5795,
    44.0216,
    'Al-Mawasit District, Ta''izz',
    'مديرية المواسط، تعز',
    'Mountain',
    'تعز',
    12.8,
    'active',
    NOW() - INTERVAL '4 months',
    NOW()
),
(
    '22222222-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    'Sabr Terraced Farms',
    'مزارع صبر المدرجة',
    'f2222222-2222-2222-2222-222222222222', -- Mohammed Al-Taizi
    13.6547,
    44.0389,
    'Sabr Al-Mawadim, Ta''izz',
    'صبر الموادم، تعز',
    'Mountain',
    'تعز',
    8.2,
    'active',
    NOW() - INTERVAL '3 months',
    NOW()
);

-- Insert Farms in Hadramout Governorate (حضرموت)

INSERT INTO farms (id, tenant_id, name, name_ar, owner_id, latitude, longitude, address, address_ar, region, governorate, total_area_hectares, status, created_at, updated_at)
VALUES
(
    '33333333-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    'Wadi Hadramout Date Farm',
    'مزرعة وادي حضرموت للنخيل',
    'f3333333-3333-3333-3333-333333333333', -- Ali Al-Hadrami
    15.9288,
    48.7825,
    'Wadi Hadramout, Shibam',
    'وادي حضرموت، شبام',
    'Wadi',
    'حضرموت',
    45.0,
    'active',
    NOW() - INTERVAL '8 months',
    NOW()
),
(
    '33333333-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    'Al-Mukalla Coastal Farm',
    'مزرعة المكلا الساحلية',
    'f3333333-3333-3333-3333-333333333333', -- Ali Al-Hadrami
    14.5425,
    49.1242,
    'Al-Mukalla City, Hadramout',
    'مدينة المكلا، حضرموت',
    'Coastal',
    'حضرموت',
    30.2,
    'active',
    NOW() - INTERVAL '6 months',
    NOW()
);

-- Insert Farms in Ibb Governorate (إب)

INSERT INTO farms (id, tenant_id, name, name_ar, owner_id, latitude, longitude, address, address_ar, region, governorate, total_area_hectares, status, created_at, updated_at)
VALUES
(
    '44444444-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    'Ibb Green Mountain Farm',
    'مزرعة الجبل الأخضر إب',
    'f4444444-4444-4444-4444-444444444444', -- Hassan Al-Ibbi
    13.9667,
    44.1667,
    'Ibb City, Al-Udayn District',
    'مدينة إب، مديرية العدين',
    'Highland',
    'إب',
    18.5,
    'active',
    NOW() - INTERVAL '3 months',
    NOW()
),
(
    '44444444-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    'Jiblah Heritage Farm',
    'مزرعة جبلة التراثية',
    'f4444444-4444-4444-4444-444444444444', -- Hassan Al-Ibbi
    13.9172,
    44.1444,
    'Jiblah District, Ibb',
    'مديرية جبلة، إب',
    'Highland',
    'إب',
    10.7,
    'active',
    NOW() - INTERVAL '2 months',
    NOW()
);

-- Insert Farms in Al-Hudaydah Governorate (الحديدة)

INSERT INTO farms (id, tenant_id, name, name_ar, owner_id, latitude, longitude, address, address_ar, region, governorate, total_area_hectares, status, created_at, updated_at)
VALUES
(
    '55555555-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    'Red Sea Agricultural Complex',
    'مجمع البحر الأحمر الزراعي',
    'f5555555-5555-5555-5555-555555555555', -- Fatima Al-Hudaydi
    14.7978,
    42.9545,
    'Al-Hudaydah City, Zabid',
    'مدينة الحديدة، زبيد',
    'Coastal',
    'الحديدة',
    100.0,
    'active',
    NOW() - INTERVAL '5 months',
    NOW()
),
(
    '55555555-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    'Tihama Plains Farm',
    'مزرعة سهول تهامة',
    'f5555555-5555-5555-5555-555555555555', -- Fatima Al-Hudaydi
    14.6547,
    43.0125,
    'Bayt Al-Faqih, Al-Hudaydah',
    'بيت الفقيه، الحديدة',
    'Coastal',
    'الحديدة',
    75.5,
    'active',
    NOW() - INTERVAL '4 months',
    NOW()
);

-- Add verification query
SELECT
    name,
    name_ar,
    governorate,
    total_area_hectares,
    status,
    (SELECT name FROM users WHERE id = farms.owner_id) as owner_name
FROM farms
ORDER BY governorate, name;

-- Show summary by governorate
SELECT
    governorate,
    COUNT(*) as farm_count,
    ROUND(SUM(total_area_hectares)::numeric, 2) as total_hectares,
    ROUND(AVG(total_area_hectares)::numeric, 2) as avg_hectares
FROM farms
GROUP BY governorate
ORDER BY governorate;
