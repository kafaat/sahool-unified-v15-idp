-- SAHOOL Users Seed Data
-- Sample users for different roles and regions in Yemen

-- Clean existing data (optional - comment out for production)
-- TRUNCATE TABLE users CASCADE;

-- Insert Admin User
INSERT INTO users (id, tenant_id, email, name, name_ar, phone, language, roles, is_active, is_verified, password_hash, created_at, updated_at)
VALUES
(
    'a1111111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    'admin@sahool.ye',
    'System Administrator',
    'مدير النظام',
    '+967-777-000000',
    'ar',
    ARRAY['admin', 'user'],
    true,
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3qGKqJqK2', -- password: admin123
    NOW(),
    NOW()
);

-- Insert Farmer Users from Different Yemen Regions

-- Farmer 1: Sana'a (صنعاء)
INSERT INTO users (id, tenant_id, email, name, name_ar, phone, language, roles, is_active, is_verified, password_hash, created_at, updated_at)
VALUES
(
    'f1111111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    'ahmed.alsanani@sahool.ye',
    'Ahmed Al-Sanani',
    'أحمد الصنعاني',
    '+967-777-111111',
    'ar',
    ARRAY['farmer', 'user'],
    true,
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3qGKqJqK2', -- password: farmer123
    NOW() - INTERVAL '6 months',
    NOW()
);

-- Farmer 2: Ta'izz (تعز)
INSERT INTO users (id, tenant_id, email, name, name_ar, phone, language, roles, is_active, is_verified, password_hash, created_at, updated_at)
VALUES
(
    'f2222222-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    'mohammed.altaizi@sahool.ye',
    'Mohammed Al-Taizi',
    'محمد التعزي',
    '+967-777-222222',
    'ar',
    ARRAY['farmer', 'user'],
    true,
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3qGKqJqK2',
    NOW() - INTERVAL '4 months',
    NOW()
);

-- Farmer 3: Hadramout (حضرموت)
INSERT INTO users (id, tenant_id, email, name, name_ar, phone, language, roles, is_active, is_verified, password_hash, created_at, updated_at)
VALUES
(
    'f3333333-3333-3333-3333-333333333333',
    'tenant-sahool-main',
    'ali.alhadrami@sahool.ye',
    'Ali Al-Hadrami',
    'علي الحضرمي',
    '+967-777-333333',
    'ar',
    ARRAY['farmer', 'user'],
    true,
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3qGKqJqK2',
    NOW() - INTERVAL '8 months',
    NOW()
);

-- Farmer 4: Ibb (إب)
INSERT INTO users (id, tenant_id, email, name, name_ar, phone, language, roles, is_active, is_verified, password_hash, created_at, updated_at)
VALUES
(
    'f4444444-4444-4444-4444-444444444444',
    'tenant-sahool-main',
    'hassan.alibbi@sahool.ye',
    'Hassan Al-Ibbi',
    'حسن الإبي',
    '+967-777-444444',
    'ar',
    ARRAY['farmer', 'user'],
    true,
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3qGKqJqK2',
    NOW() - INTERVAL '3 months',
    NOW()
);

-- Farmer 5: Al-Hudaydah (الحديدة)
INSERT INTO users (id, tenant_id, email, name, name_ar, phone, language, roles, is_active, is_verified, password_hash, created_at, updated_at)
VALUES
(
    'f5555555-5555-5555-5555-555555555555',
    'tenant-sahool-main',
    'fatima.alhudaydi@sahool.ye',
    'Fatima Al-Hudaydi',
    'فاطمة الحديدية',
    '+967-777-555555',
    'ar',
    ARRAY['farmer', 'user'],
    true,
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3qGKqJqK2',
    NOW() - INTERVAL '5 months',
    NOW()
);

-- Insert Agronomist Users

-- Agronomist 1
INSERT INTO users (id, tenant_id, email, name, name_ar, phone, language, roles, is_active, is_verified, password_hash, created_at, updated_at)
VALUES
(
    'g1111111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    'dr.khalid@sahool.ye',
    'Dr. Khalid Al-Sharif',
    'د. خالد الشريف',
    '+967-777-666666',
    'ar',
    ARRAY['agronomist', 'advisor', 'user'],
    true,
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3qGKqJqK2',
    NOW() - INTERVAL '1 year',
    NOW()
);

-- Agronomist 2
INSERT INTO users (id, tenant_id, email, name, name_ar, phone, language, roles, is_active, is_verified, password_hash, created_at, updated_at)
VALUES
(
    'g2222222-2222-2222-2222-222222222222',
    'tenant-sahool-main',
    'eng.sara@sahool.ye',
    'Eng. Sara Abdullah',
    'م. سارة عبدالله',
    '+967-777-777777',
    'ar',
    ARRAY['agronomist', 'advisor', 'user'],
    true,
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3qGKqJqK2',
    NOW() - INTERVAL '2 years',
    NOW()
);

-- Insert Research User
INSERT INTO users (id, tenant_id, email, name, name_ar, phone, language, roles, is_active, is_verified, password_hash, created_at, updated_at)
VALUES
(
    'r1111111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    'research@sahool.ye',
    'Research Department',
    'قسم الأبحاث',
    '+967-777-888888',
    'ar',
    ARRAY['researcher', 'analyst', 'user'],
    true,
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3qGKqJqK2',
    NOW() - INTERVAL '1 year',
    NOW()
);

-- Add some demo/test users
INSERT INTO users (id, tenant_id, email, name, name_ar, phone, language, roles, is_active, is_verified, password_hash, created_at, updated_at)
VALUES
(
    'd1111111-1111-1111-1111-111111111111',
    'tenant-sahool-main',
    'demo@sahool.ye',
    'Demo User',
    'مستخدم تجريبي',
    '+967-777-999999',
    'ar',
    ARRAY['viewer', 'user'],
    true,
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtJ3qGKqJqK2',
    NOW(),
    NOW()
);

-- Verify inserts
SELECT
    email,
    name,
    name_ar,
    array_to_string(roles, ', ') as roles,
    is_active,
    created_at
FROM users
ORDER BY created_at;
