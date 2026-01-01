-- Migration: Add Soft Delete Fields
-- تحديث: إضافة حقول الحذف الناعم
-- Created: 2026-01-01
-- Description: Adds deletedAt and deletedBy fields to main entities for soft delete pattern

-- ═══════════════════════════════════════════════════════════════════════════
-- Add soft delete fields to products table
-- إضافة حقول الحذف الناعم لجدول المنتجات
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE "products"
ADD COLUMN "deleted_at" TIMESTAMPTZ,
ADD COLUMN "deleted_by" VARCHAR(255);

-- Create index for soft delete queries
CREATE INDEX "idx_products_deleted_at" ON "products"("deleted_at");

-- Add comment to columns
COMMENT ON COLUMN "products"."deleted_at" IS 'تاريخ الحذف الناعم - Soft delete timestamp';
COMMENT ON COLUMN "products"."deleted_by" IS 'من قام بالحذف - User who deleted the record';


-- ═══════════════════════════════════════════════════════════════════════════
-- Add soft delete fields to orders table
-- إضافة حقول الحذف الناعم لجدول الطلبات
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE "orders"
ADD COLUMN "deleted_at" TIMESTAMPTZ,
ADD COLUMN "deleted_by" VARCHAR(255);

-- Create index for soft delete queries
CREATE INDEX "idx_orders_deleted_at" ON "orders"("deleted_at");

-- Add comment to columns
COMMENT ON COLUMN "orders"."deleted_at" IS 'تاريخ الحذف الناعم - Soft delete timestamp';
COMMENT ON COLUMN "orders"."deleted_by" IS 'من قام بالحذف - User who deleted the record';


-- ═══════════════════════════════════════════════════════════════════════════
-- Add soft delete fields to wallets table
-- إضافة حقول الحذف الناعم لجدول المحافظ
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE "wallets"
ADD COLUMN "deleted_at" TIMESTAMPTZ,
ADD COLUMN "deleted_by" VARCHAR(255);

-- Create index for soft delete queries
CREATE INDEX "idx_wallets_deleted_at" ON "wallets"("deleted_at");

-- Add comment to columns
COMMENT ON COLUMN "wallets"."deleted_at" IS 'تاريخ الحذف الناعم - Soft delete timestamp';
COMMENT ON COLUMN "wallets"."deleted_by" IS 'من قام بالحذف - User who deleted the record';


-- ═══════════════════════════════════════════════════════════════════════════
-- Add soft delete fields to loans table
-- إضافة حقول الحذف الناعم لجدول القروض
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE "loans"
ADD COLUMN "deleted_at" TIMESTAMPTZ,
ADD COLUMN "deleted_by" VARCHAR(255);

-- Create index for soft delete queries
CREATE INDEX "idx_loans_deleted_at" ON "loans"("deleted_at");

-- Add comment to columns
COMMENT ON COLUMN "loans"."deleted_at" IS 'تاريخ الحذف الناعم - Soft delete timestamp';
COMMENT ON COLUMN "loans"."deleted_by" IS 'من قام بالحذف - User who deleted the record';


-- ═══════════════════════════════════════════════════════════════════════════
-- Notes on Soft Delete Implementation
-- ملاحظات حول تطبيق الحذف الناعم
-- ═══════════════════════════════════════════════════════════════════════════

-- 1. Records are not physically deleted, just marked as deleted with a timestamp
--    السجلات لا يتم حذفها فعليًا، بل يتم وضع علامة عليها كمحذوفة مع طابع زمني
--
-- 2. The deleted_by field stores the user ID who performed the deletion
--    حقل deleted_by يخزن معرف المستخدم الذي قام بالحذف
--
-- 3. Application middleware automatically filters out deleted records in queries
--    البرنامج الوسيط يقوم تلقائيًا بتصفية السجلات المحذوفة في الاستعلامات
--
-- 4. Deleted records can be restored by setting deleted_at back to NULL
--    يمكن استعادة السجلات المحذوفة بتعيين deleted_at إلى NULL
--
-- 5. For permanent deletion (GDPR compliance), use hard delete operations
--    للحذف الدائم (امتثال GDPR)، استخدم عمليات الحذف الصلب
--
-- 6. Audit tables (transactions, credit_events, wallet_audit_log) are excluded
--    from soft delete to maintain complete audit trail
--    جداول التدقيق مستبعدة من الحذف الناعم للحفاظ على سجل تدقيق كامل


-- ═══════════════════════════════════════════════════════════════════════════
-- Example queries using soft delete
-- أمثلة على الاستعلامات باستخدام الحذف الناعم
-- ═══════════════════════════════════════════════════════════════════════════

-- Find all active (non-deleted) products
-- البحث عن جميع المنتجات النشطة (غير المحذوفة)
-- SELECT * FROM products WHERE deleted_at IS NULL;

-- Find all deleted products
-- البحث عن جميع المنتجات المحذوفة
-- SELECT * FROM products WHERE deleted_at IS NOT NULL;

-- Find all products including deleted ones
-- البحث عن جميع المنتجات بما في ذلك المحذوفة
-- SELECT * FROM products;

-- Soft delete a product
-- حذف ناعم لمنتج
-- UPDATE products SET deleted_at = NOW(), deleted_by = 'user-123' WHERE id = 'product-456';

-- Restore a soft-deleted product
-- استعادة منتج محذوف
-- UPDATE products SET deleted_at = NULL, deleted_by = NULL WHERE id = 'product-456';

-- Count active vs deleted products
-- عد المنتجات النشطة مقابل المحذوفة
-- SELECT
--   COUNT(*) FILTER (WHERE deleted_at IS NULL) as active_count,
--   COUNT(*) FILTER (WHERE deleted_at IS NOT NULL) as deleted_count,
--   COUNT(*) as total_count
-- FROM products;

-- Get deletion audit trail
-- الحصول على سجل تدقيق الحذف
-- SELECT
--   id, name, deleted_at, deleted_by
-- FROM products
-- WHERE deleted_at IS NOT NULL
-- ORDER BY deleted_at DESC;
