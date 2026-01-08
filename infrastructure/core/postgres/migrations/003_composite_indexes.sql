-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform - Composite Indexes Migration
-- الفهارس المركبة لتحسين الأداء
-- ═══════════════════════════════════════════════════════════════════════════════

-- Skip if already applied
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM public._migrations WHERE name = '003_composite_indexes') THEN
        RAISE NOTICE 'Migration 003_composite_indexes already applied, skipping...';
        RETURN;
    END IF;

    RAISE NOTICE 'Applying migration 003_composite_indexes...';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Fields Table Indexes (جداول الحقول)
    -- ═══════════════════════════════════════════════════════════════════════════

    -- Tenant + Status: للاستعلامات المتكررة عن حقول المستأجر النشطة
    CREATE INDEX IF NOT EXISTS idx_fields_tenant_status
        ON geo.fields(tenant_id, status);

    -- Tenant + Crop Type: للفلترة حسب نوع المحصول
    CREATE INDEX IF NOT EXISTS idx_fields_tenant_crop
        ON geo.fields(tenant_id, crop_type);

    -- Tenant + Health Score: للترتيب حسب صحة الحقل
    CREATE INDEX IF NOT EXISTS idx_fields_tenant_health
        ON geo.fields(tenant_id, health_score DESC NULLS LAST);

    -- Tenant + Updated: للمزامنة
    CREATE INDEX IF NOT EXISTS idx_fields_tenant_updated
        ON geo.fields(tenant_id, updated_at DESC);

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Farms Table Indexes (جداول المزارع)
    -- ═══════════════════════════════════════════════════════════════════════════

    -- Tenant + Status: للاستعلامات عن مزارع المستأجر
    CREATE INDEX IF NOT EXISTS idx_farms_tenant_status
        ON geo.farms(tenant_id, status);

    -- Owner + Status: للاستعلامات عن مزارع المالك
    CREATE INDEX IF NOT EXISTS idx_farms_owner_status
        ON geo.farms(owner_id, status);

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Tasks Table Indexes (جداول المهام)
    -- ═══════════════════════════════════════════════════════════════════════════

    -- تحقق من وجود جدول المهام
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tasks') THEN
        -- Field + Status: للمهام حسب الحقل
        CREATE INDEX IF NOT EXISTS idx_tasks_field_status
            ON tasks(field_id, status);

        -- Assignee + Due Date: للمهام المعينة
        CREATE INDEX IF NOT EXISTS idx_tasks_assignee_due
            ON tasks(assigned_to, due_date);

        -- Status + Due Date: للمهام المتأخرة
        CREATE INDEX IF NOT EXISTS idx_tasks_status_due
            ON tasks(status, due_date)
            WHERE status IN ('pending', 'in_progress');

        -- Created By + Status: لمتابعة المنشئ
        CREATE INDEX IF NOT EXISTS idx_tasks_creator_status
            ON tasks(created_by, status);

        RAISE NOTICE 'Tasks indexes created';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Users Table Indexes (جداول المستخدمين)
    -- ═══════════════════════════════════════════════════════════════════════════

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'users' AND table_name = 'users') THEN
        -- Tenant + Role: للاستعلامات عن مستخدمي المستأجر حسب الدور
        CREATE INDEX IF NOT EXISTS idx_users_tenant_role
            ON users.users(tenant_id, role);

        -- Tenant + Active: للمستخدمين النشطين
        CREATE INDEX IF NOT EXISTS idx_users_tenant_active
            ON users.users(tenant_id, is_active)
            WHERE is_active = true;

        -- Last Login: للمستخدمين الأكثر نشاطاً
        CREATE INDEX IF NOT EXISTS idx_users_last_login
            ON users.users(last_login DESC NULLS LAST);

        RAISE NOTICE 'Users indexes created';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Sensors & IoT Indexes (جداول المستشعرات وإنترنت الأشياء)
    -- ═══════════════════════════════════════════════════════════════════════════

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'devices') THEN
        -- Tenant + Status: للأجهزة حسب المستأجر
        CREATE INDEX IF NOT EXISTS idx_devices_tenant_status
            ON devices(tenant_id, status);

        -- Field + Status: للأجهزة حسب الحقل
        CREATE INDEX IF NOT EXISTS idx_devices_field_status
            ON devices(field_id, status);

        -- Last Seen: للأجهزة غير المتصلة
        CREATE INDEX IF NOT EXISTS idx_devices_last_seen
            ON devices(last_seen DESC NULLS LAST);

        RAISE NOTICE 'Devices indexes created';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sensor_readings') THEN
        -- Sensor + Timestamp: للقراءات التاريخية
        CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_time
            ON sensor_readings(sensor_id, timestamp DESC);

        -- Device + Timestamp: للقراءات حسب الجهاز
        CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_time
            ON sensor_readings(device_id, timestamp DESC);

        -- Partial index for recent readings (last 7 days)
        CREATE INDEX IF NOT EXISTS idx_sensor_readings_recent
            ON sensor_readings(sensor_id, timestamp DESC)
            WHERE timestamp > NOW() - INTERVAL '7 days';

        RAISE NOTICE 'Sensor readings indexes created';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Alerts Indexes (جداول التنبيهات)
    -- ═══════════════════════════════════════════════════════════════════════════

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'device_alerts') THEN
        -- Tenant + Acknowledged: للتنبيهات غير المقروءة
        CREATE INDEX IF NOT EXISTS idx_alerts_tenant_unack
            ON device_alerts(tenant_id, acknowledged)
            WHERE acknowledged = false;

        -- Severity + Created: للتنبيهات الحرجة الأخيرة
        CREATE INDEX IF NOT EXISTS idx_alerts_severity_created
            ON device_alerts(severity, created_at DESC);

        -- Device + Acknowledged: لتنبيهات الجهاز
        CREATE INDEX IF NOT EXISTS idx_alerts_device_unack
            ON device_alerts(device_id, acknowledged);

        RAISE NOTICE 'Device alerts indexes created';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════════
    -- NDVI Readings Indexes (قراءات NDVI)
    -- ═══════════════════════════════════════════════════════════════════════════

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ndvi_readings') THEN
        -- Field + Captured At: للسجل التاريخي
        CREATE INDEX IF NOT EXISTS idx_ndvi_field_captured
            ON ndvi_readings(field_id, captured_at DESC);

        -- Source + Quality: للفلترة حسب المصدر
        CREATE INDEX IF NOT EXISTS idx_ndvi_source_quality
            ON ndvi_readings(source, quality);

        RAISE NOTICE 'NDVI readings indexes created';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Marketplace Indexes (جداول السوق)
    -- ═══════════════════════════════════════════════════════════════════════════

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'products') THEN
        -- Category + Status: للمنتجات المتاحة
        CREATE INDEX IF NOT EXISTS idx_products_category_status
            ON products(category, status);

        -- Seller + Status: لمنتجات البائع
        CREATE INDEX IF NOT EXISTS idx_products_seller_status
            ON products(seller_id, status);

        -- Featured + Status: للمنتجات المميزة
        CREATE INDEX IF NOT EXISTS idx_products_featured
            ON products(featured, status)
            WHERE featured = true AND status = 'AVAILABLE';

        RAISE NOTICE 'Products indexes created';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'orders') THEN
        -- Buyer + Status: لطلبات المشتري
        CREATE INDEX IF NOT EXISTS idx_orders_buyer_status
            ON orders(buyer_id, status);

        -- Status + Created: للطلبات حسب الحالة
        CREATE INDEX IF NOT EXISTS idx_orders_status_created
            ON orders(status, created_at DESC);

        -- Payment Status: للطلبات غير المدفوعة
        CREATE INDEX IF NOT EXISTS idx_orders_payment_pending
            ON orders(payment_status, created_at DESC)
            WHERE payment_status IN ('UNPAID', 'PARTIAL');

        RAISE NOTICE 'Orders indexes created';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'wallets') THEN
        -- User + KYC: للمحافظ المعتمدة
        CREATE INDEX IF NOT EXISTS idx_wallets_verified
            ON wallets(is_verified, kyc_status);

        RAISE NOTICE 'Wallets indexes created';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'transactions') THEN
        -- Wallet + Type + Created: لتاريخ المعاملات
        CREATE INDEX IF NOT EXISTS idx_transactions_wallet_type
            ON transactions(wallet_id, type, created_at DESC);

        -- Status + Created: للمعاملات المعلقة
        CREATE INDEX IF NOT EXISTS idx_transactions_pending
            ON transactions(status, created_at)
            WHERE status = 'PENDING';

        RAISE NOTICE 'Transactions indexes created';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Billing Indexes (جداول الفواتير)
    -- ═══════════════════════════════════════════════════════════════════════════

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscriptions') THEN
        -- Tenant + Status: للاشتراكات النشطة
        CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant_status
            ON subscriptions(tenant_id, status);

        -- Next Billing: للفوترة التالية
        CREATE INDEX IF NOT EXISTS idx_subscriptions_next_billing
            ON subscriptions(next_billing_date, status)
            WHERE status IN ('ACTIVE', 'TRIAL');

        RAISE NOTICE 'Subscriptions indexes created';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'invoices') THEN
        -- Tenant + Status: لفواتير المستأجر
        CREATE INDEX IF NOT EXISTS idx_invoices_tenant_status
            ON invoices(tenant_id, status);

        -- Due Date + Status: للفواتير المتأخرة
        CREATE INDEX IF NOT EXISTS idx_invoices_overdue
            ON invoices(due_date, status)
            WHERE status IN ('PENDING', 'OVERDUE');

        RAISE NOTICE 'Invoices indexes created';
    END IF;

    -- Record this migration
    INSERT INTO public._migrations (name, applied_at)
    VALUES ('003_composite_indexes', NOW());

    RAISE NOTICE 'Migration 003_composite_indexes completed successfully';
    RAISE NOTICE 'Total indexes created for improved query performance';

END $$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Analyze tables to update statistics
-- ═══════════════════════════════════════════════════════════════════════════════

-- This should be run after creating indexes for optimal query planning
-- ANALYZE geo.farms;
-- ANALYZE geo.fields;
-- ANALYZE users.users;
