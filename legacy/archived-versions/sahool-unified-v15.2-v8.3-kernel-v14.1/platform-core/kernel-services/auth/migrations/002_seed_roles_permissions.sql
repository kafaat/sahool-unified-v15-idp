-- =============================================================================
-- SAHOOL Auth Service - Seed Data
-- =============================================================================
-- الأدوار والصلاحيات الأساسية للنظام
-- Default roles and permissions for the system
-- =============================================================================

-- =============================================================================
-- PERMISSIONS - صلاحيات النظام
-- =============================================================================

-- Fields (الحقول)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111001', 'fields', 'read', 'View fields'),
    ('11111111-1111-1111-1111-111111111002', 'fields', 'write', 'Create/update fields'),
    ('11111111-1111-1111-1111-111111111003', 'fields', 'delete', 'Delete fields'),
    ('11111111-1111-1111-1111-111111111004', 'fields', 'admin', 'Full field management')
ON CONFLICT (resource, action) DO NOTHING;

-- Tasks (المهام)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111011', 'tasks', 'read', 'View tasks'),
    ('11111111-1111-1111-1111-111111111012', 'tasks', 'write', 'Create/update tasks'),
    ('11111111-1111-1111-1111-111111111013', 'tasks', 'delete', 'Delete tasks'),
    ('11111111-1111-1111-1111-111111111014', 'tasks', 'assign', 'Assign tasks to users'),
    ('11111111-1111-1111-1111-111111111015', 'tasks', 'admin', 'Full task management')
ON CONFLICT (resource, action) DO NOTHING;

-- Crops (المحاصيل)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111021', 'crops', 'read', 'View crops'),
    ('11111111-1111-1111-1111-111111111022', 'crops', 'write', 'Create/update crops'),
    ('11111111-1111-1111-1111-111111111023', 'crops', 'delete', 'Delete crops'),
    ('11111111-1111-1111-1111-111111111024', 'crops', 'admin', 'Full crop management')
ON CONFLICT (resource, action) DO NOTHING;

-- Weather (الطقس)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111031', 'weather', 'read', 'View weather data'),
    ('11111111-1111-1111-1111-111111111032', 'weather', 'admin', 'Weather admin')
ON CONFLICT (resource, action) DO NOTHING;

-- NDVI/Satellite (صور الأقمار الصناعية)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111041', 'ndvi', 'read', 'View NDVI data'),
    ('11111111-1111-1111-1111-111111111042', 'ndvi', 'analyze', 'Request NDVI analysis'),
    ('11111111-1111-1111-1111-111111111043', 'ndvi', 'admin', 'NDVI admin')
ON CONFLICT (resource, action) DO NOTHING;

-- Alerts (التنبيهات)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111051', 'alerts', 'read', 'View alerts'),
    ('11111111-1111-1111-1111-111111111052', 'alerts', 'write', 'Create alerts'),
    ('11111111-1111-1111-1111-111111111053', 'alerts', 'acknowledge', 'Acknowledge alerts'),
    ('11111111-1111-1111-1111-111111111054', 'alerts', 'admin', 'Alert admin')
ON CONFLICT (resource, action) DO NOTHING;

-- Reports (التقارير)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111061', 'reports', 'read', 'View reports'),
    ('11111111-1111-1111-1111-111111111062', 'reports', 'generate', 'Generate reports'),
    ('11111111-1111-1111-1111-111111111063', 'reports', 'export', 'Export reports'),
    ('11111111-1111-1111-1111-111111111064', 'reports', 'admin', 'Reports admin')
ON CONFLICT (resource, action) DO NOTHING;

-- Users (المستخدمين)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111071', 'users', 'read', 'View users'),
    ('11111111-1111-1111-1111-111111111072', 'users', 'write', 'Create/update users'),
    ('11111111-1111-1111-1111-111111111073', 'users', 'delete', 'Delete users'),
    ('11111111-1111-1111-1111-111111111074', 'users', 'admin', 'User admin')
ON CONFLICT (resource, action) DO NOTHING;

-- Equipment (المعدات)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111081', 'equipment', 'read', 'View equipment'),
    ('11111111-1111-1111-1111-111111111082', 'equipment', 'write', 'Create/update equipment'),
    ('11111111-1111-1111-1111-111111111083', 'equipment', 'delete', 'Delete equipment'),
    ('11111111-1111-1111-1111-111111111084', 'equipment', 'admin', 'Equipment admin')
ON CONFLICT (resource, action) DO NOTHING;

-- Irrigation (الري)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111091', 'irrigation', 'read', 'View irrigation data'),
    ('11111111-1111-1111-1111-111111111092', 'irrigation', 'write', 'Control irrigation'),
    ('11111111-1111-1111-1111-111111111093', 'irrigation', 'schedule', 'Schedule irrigation'),
    ('11111111-1111-1111-1111-111111111094', 'irrigation', 'admin', 'Irrigation admin')
ON CONFLICT (resource, action) DO NOTHING;

-- Calendar (التقويم الفلكي)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111101', 'calendar', 'read', 'View astronomical calendar'),
    ('11111111-1111-1111-1111-111111111102', 'calendar', 'admin', 'Calendar admin')
ON CONFLICT (resource, action) DO NOTHING;

-- Market (الأسواق)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111111', 'market', 'read', 'View market prices'),
    ('11111111-1111-1111-1111-111111111112', 'market', 'write', 'Update market prices'),
    ('11111111-1111-1111-1111-111111111113', 'market', 'admin', 'Market admin')
ON CONFLICT (resource, action) DO NOTHING;

-- Tenant (المستأجرين)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111121', 'tenant', 'read', 'View tenant info'),
    ('11111111-1111-1111-1111-111111111122', 'tenant', 'write', 'Update tenant settings'),
    ('11111111-1111-1111-1111-111111111123', 'tenant', 'admin', 'Tenant admin')
ON CONFLICT (resource, action) DO NOTHING;

-- System Admin (إدارة النظام)
INSERT INTO permissions (id, resource, action, description) VALUES
    ('11111111-1111-1111-1111-111111111131', 'admin', '*', 'Super admin - all permissions')
ON CONFLICT (resource, action) DO NOTHING;

-- =============================================================================
-- ROLES - أدوار النظام
-- =============================================================================

-- مدير عام النظام
INSERT INTO roles (id, name, name_ar, description, description_ar, is_system) VALUES
    ('22222222-2222-2222-2222-222222222001', 'super_admin', 'مدير النظام', 
     'System super administrator with full access', 
     'مدير النظام العام مع صلاحيات كاملة', true)
ON CONFLICT (name) DO NOTHING;

-- مدير المستأجر (المزرعة)
INSERT INTO roles (id, name, name_ar, description, description_ar, is_system) VALUES
    ('22222222-2222-2222-2222-222222222002', 'tenant_admin', 'مدير المزرعة', 
     'Tenant administrator with full tenant access', 
     'مدير المزرعة مع صلاحيات كاملة على المستأجر', true)
ON CONFLICT (name) DO NOTHING;

-- مدير المزرعة
INSERT INTO roles (id, name, name_ar, description, description_ar, is_system) VALUES
    ('22222222-2222-2222-2222-222222222003', 'farm_manager', 'مدير الحقول', 
     'Farm manager with field and task management', 
     'مدير الحقول والمهام الزراعية', true)
ON CONFLICT (name) DO NOTHING;

-- المهندس الزراعي
INSERT INTO roles (id, name, name_ar, description, description_ar, is_system) VALUES
    ('22222222-2222-2222-2222-222222222004', 'agronomist', 'مهندس زراعي', 
     'Agricultural engineer with advisory access', 
     'مهندس زراعي مع صلاحيات استشارية', true)
ON CONFLICT (name) DO NOTHING;

-- عامل الحقل
INSERT INTO roles (id, name, name_ar, description, description_ar, is_system) VALUES
    ('22222222-2222-2222-2222-222222222005', 'field_worker', 'عامل حقل', 
     'Field worker with task execution access', 
     'عامل حقل مع صلاحيات تنفيذ المهام', true)
ON CONFLICT (name) DO NOTHING;

-- مشاهد فقط
INSERT INTO roles (id, name, name_ar, description, description_ar, is_system) VALUES
    ('22222222-2222-2222-2222-222222222006', 'viewer', 'مشاهد', 
     'View-only access to data', 
     'صلاحيات مشاهدة فقط', true)
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- ROLE-PERMISSION MAPPINGS - ربط الأدوار بالصلاحيات
-- =============================================================================

-- Super Admin - كل الصلاحيات
INSERT INTO role_permissions (role_id, permission_id) VALUES
    ('22222222-2222-2222-2222-222222222001', '11111111-1111-1111-1111-111111111131')
ON CONFLICT DO NOTHING;

-- Tenant Admin - كل صلاحيات المستأجر
INSERT INTO role_permissions (role_id, permission_id) 
SELECT '22222222-2222-2222-2222-222222222002', id 
FROM permissions 
WHERE action = 'admin' AND resource != 'admin'
ON CONFLICT DO NOTHING;

-- Farm Manager - إدارة الحقول والمهام
INSERT INTO role_permissions (role_id, permission_id) VALUES
    -- Fields
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111001'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111002'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111003'),
    -- Tasks
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111011'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111012'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111013'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111014'),
    -- Crops
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111021'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111022'),
    -- Weather
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111031'),
    -- NDVI
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111041'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111042'),
    -- Alerts
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111051'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111052'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111053'),
    -- Reports
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111061'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111062'),
    -- Equipment
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111081'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111082'),
    -- Irrigation
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111091'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111092'),
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111093'),
    -- Calendar
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111101'),
    -- Market
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111111'),
    -- Users (read only)
    ('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111071')
ON CONFLICT DO NOTHING;

-- Agronomist - صلاحيات استشارية
INSERT INTO role_permissions (role_id, permission_id) VALUES
    -- Fields (read)
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111001'),
    -- Tasks (read, write)
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111011'),
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111012'),
    -- Crops (read, write)
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111021'),
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111022'),
    -- Weather
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111031'),
    -- NDVI
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111041'),
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111042'),
    -- Alerts
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111051'),
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111052'),
    -- Reports
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111061'),
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111062'),
    -- Irrigation (read)
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111091'),
    -- Calendar
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111101'),
    -- Market
    ('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111111')
ON CONFLICT DO NOTHING;

-- Field Worker - تنفيذ المهام
INSERT INTO role_permissions (role_id, permission_id) VALUES
    -- Fields (read)
    ('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111001'),
    -- Tasks (read, write - assigned only enforced in app)
    ('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111011'),
    ('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111012'),
    -- Weather
    ('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111031'),
    -- Alerts (read, acknowledge)
    ('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111051'),
    ('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111053'),
    -- Equipment (read)
    ('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111081'),
    -- Calendar
    ('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111101')
ON CONFLICT DO NOTHING;

-- Viewer - مشاهدة فقط
INSERT INTO role_permissions (role_id, permission_id) VALUES
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111001'),
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111011'),
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111021'),
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111031'),
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111041'),
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111051'),
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111061'),
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111081'),
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111091'),
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111101'),
    ('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111111')
ON CONFLICT DO NOTHING;
