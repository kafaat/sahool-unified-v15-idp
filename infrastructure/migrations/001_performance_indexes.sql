-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: 001_performance_indexes.sql
-- فهارس الأداء - Performance Indexes
-- ═══════════════════════════════════════════════════════════════════════════════
--
-- Description (EN): Creates performance-critical database indexes for the SAHOOL
--   agricultural platform. These indexes optimize query performance for the most
--   frequently accessed tables including fields, tasks, NDVI readings, events,
--   irrigation schedules, sensor data, weather, crops, marketplace, and notifications.
--
-- الوصف (AR): ينشئ فهارس قاعدة البيانات المهمة للأداء لمنصة سهول الزراعية.
--   هذه الفهارس تحسّن أداء الاستعلامات للجداول الأكثر استخداماً بما في ذلك
--   الحقول، المهام، قراءات NDVI، الأحداث، جداول الري، بيانات الاستشعار،
--   الطقس، المحاصيل، السوق، والإشعارات.
--
-- Version: 16.0.0
-- Date: 2026-03-01
-- Author: SAHOOL Platform Team
--
-- IMPORTANT / مهم:
--   - All indexes use CONCURRENTLY to avoid locking tables during creation
--     جميع الفهارس تستخدم CONCURRENTLY لتجنب قفل الجداول أثناء الإنشاء
--   - All indexes use IF NOT EXISTS for idempotent execution
--     جميع الفهارس تستخدم IF NOT EXISTS للتنفيذ المتكرر بأمان
--   - CONCURRENTLY cannot be used inside a transaction block
--     لا يمكن استخدام CONCURRENTLY داخل كتلة معاملة
--   - Run this migration outside of a transaction (e.g., psql -f)
--     نفّذ هذا الترحيل خارج المعاملة
--
-- Estimated execution time: 5-15 minutes depending on table sizes
-- الوقت المقدر للتنفيذ: 5-15 دقيقة حسب حجم الجداول
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- Field Indexes - فهارس الحقول
-- Used by: field-management-service, vegetation-analysis-service
-- تُستخدم بواسطة: خدمة إدارة الحقول، خدمة تحليل الغطاء النباتي
-- ─────────────────────────────────────────────────────────────────────────────

-- Tenant isolation: every query filters by tenant_id (multi-tenancy)
-- عزل المستأجر: كل استعلام يُصفّى بمعرف المستأجر (تعدد المستأجرين)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_tenant_id ON fields(tenant_id);

-- Spatial queries: field boundary lookups, intersection checks (PostGIS GIST)
-- الاستعلامات المكانية: البحث في حدود الحقول، فحص التقاطعات
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_geom ON fields USING GIST(geometry);

-- Recent fields listing: dashboard displays newest fields first
-- قائمة الحقول الحديثة: لوحة التحكم تعرض أحدث الحقول أولاً
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_created_at ON fields(created_at DESC);

-- Field status filtering: active/inactive/archived field queries
-- تصفية حالة الحقل: استعلامات الحقول النشطة/غير النشطة/المؤرشفة
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_status ON fields(status);

-- ─────────────────────────────────────────────────────────────────────────────
-- Task Indexes - فهارس المهام
-- Used by: task-service
-- تُستخدم بواسطة: خدمة المهام
-- ─────────────────────────────────────────────────────────────────────────────

-- Task dashboard: filter by status and sort by due date
-- لوحة المهام: التصفية حسب الحالة والترتيب حسب تاريخ الاستحقاق
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_status_due ON tasks(status, due_date);

-- Tenant-scoped task queries
-- استعلامات المهام حسب المستأجر
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_tenant_id ON tasks(tenant_id);

-- User assignment lookup: "my tasks" query
-- بحث المهام المسندة: استعلام "مهامي"
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);

-- ─────────────────────────────────────────────────────────────────────────────
-- NDVI Indexes - فهارس مؤشر الغطاء النباتي
-- Used by: vegetation-analysis-service, ndvi-processor, field-intelligence
-- تُستخدم بواسطة: خدمة تحليل الغطاء النباتي، معالج NDVI، ذكاء الحقول
-- ─────────────────────────────────────────────────────────────────────────────

-- Time-series NDVI lookup: latest readings per field (critical for dashboards)
-- بحث السلاسل الزمنية لـ NDVI: أحدث القراءات لكل حقل (حرج للوحات التحكم)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ndvi_field_date ON ndvi_readings(field_id, reading_date DESC);

-- Tenant-scoped NDVI queries
-- استعلامات NDVI حسب المستأجر
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ndvi_tenant ON ndvi_readings(tenant_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Event Indexes - فهارس الأحداث
-- Used by: audit-service, notification-service
-- تُستخدم بواسطة: خدمة التدقيق، خدمة الإشعارات
-- ─────────────────────────────────────────────────────────────────────────────

-- Event timeline: tenant-scoped chronological event listing
-- الجدول الزمني للأحداث: قائمة الأحداث الزمنية حسب المستأجر
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_tenant_created ON events(tenant_id, created_at DESC);

-- Event type filtering: filter by event_type (e.g., field.created, pest.detected)
-- تصفية نوع الحدث: التصفية حسب نوع الحدث
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_type ON events(event_type);

-- ─────────────────────────────────────────────────────────────────────────────
-- Irrigation Indexes - فهارس الري
-- Used by: irrigation-smart, irrigation-cycle-engine
-- تُستخدم بواسطة: الري الذكي، محرك دورة الري
-- ─────────────────────────────────────────────────────────────────────────────

-- Field irrigation schedules: lookup schedules for a specific field
-- جداول ري الحقل: البحث عن جداول الري لحقل معين
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_irrigation_field ON irrigation_schedules(field_id);

-- Next irrigation date: upcoming irrigation scheduling queries
-- تاريخ الري التالي: استعلامات جدولة الري القادمة
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_irrigation_next ON irrigation_schedules(next_irrigation_date);

-- ─────────────────────────────────────────────────────────────────────────────
-- Sensor Data Indexes - فهارس بيانات الاستشعار
-- Used by: iot-service, iot-gateway, virtual-sensors, iot-sensor-hub
-- تُستخدم بواسطة: خدمة إنترنت الأشياء، بوابة IoT، الحساسات الافتراضية
-- ─────────────────────────────────────────────────────────────────────────────

-- Device time-series: sensor readings ordered by time per device
-- السلاسل الزمنية للجهاز: قراءات الحساسات مرتبة زمنياً لكل جهاز
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sensor_data_device_time ON sensor_data(device_id, recorded_at DESC);

-- Field sensor data: all sensor data for a specific field
-- بيانات حساسات الحقل: جميع بيانات الحساسات لحقل معين
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sensor_data_field ON sensor_data(field_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Weather Indexes - فهارس الطقس
-- Used by: weather-service
-- تُستخدم بواسطة: خدمة الطقس
-- ─────────────────────────────────────────────────────────────────────────────

-- Weather location time-series: recent weather data per location
-- السلاسل الزمنية لموقع الطقس: بيانات الطقس الحديثة لكل موقع
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_weather_location ON weather_data(location_id, recorded_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- Crop Indexes - فهارس المحاصيل
-- Used by: crop-intelligence-service, crop-growth-model, advisory-service
-- تُستخدم بواسطة: خدمة ذكاء المحاصيل، نموذج نمو المحاصيل، خدمة الاستشارات
-- ─────────────────────────────────────────────────────────────────────────────

-- Field season lookup: crops planted in a field for a given season
-- بحث موسم الحقل: المحاصيل المزروعة في حقل لموسم معين
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crops_field_season ON crops(field_id, season);

-- Crop type filtering: aggregate queries by crop type
-- تصفية نوع المحصول: الاستعلامات التجميعية حسب نوع المحصول
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crops_type ON crops(crop_type);

-- ─────────────────────────────────────────────────────────────────────────────
-- Marketplace Indexes - فهارس السوق
-- Used by: marketplace-service
-- تُستخدم بواسطة: خدمة السوق
-- ─────────────────────────────────────────────────────────────────────────────

-- Active listings: browse marketplace filtered by status, sorted by newest
-- القوائم النشطة: تصفح السوق مع التصفية حسب الحالة، مرتبة بالأحدث
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_listings_status ON marketplace_listings(status, created_at DESC);

-- Crop type listings: filter marketplace by crop type
-- قوائم نوع المحصول: تصفية السوق حسب نوع المحصول
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_listings_crop ON marketplace_listings(crop_type);

-- ─────────────────────────────────────────────────────────────────────────────
-- Notification Indexes - فهارس الإشعارات
-- Used by: notification-service
-- تُستخدم بواسطة: خدمة الإشعارات
-- ─────────────────────────────────────────────────────────────────────────────

-- User notifications: unread notifications per user (read_at IS NULL = unread)
-- إشعارات المستخدم: الإشعارات غير المقروءة لكل مستخدم
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user ON notifications(user_id, read_at);

-- Tenant notification timeline: recent notifications per tenant
-- الجدول الزمني لإشعارات المستأجر: أحدث الإشعارات لكل مستأجر
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_tenant ON notifications(tenant_id, created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- End of Migration 001 - نهاية الترحيل 001
-- Total indexes created: 22
-- إجمالي الفهارس المُنشأة: 22
-- ═══════════════════════════════════════════════════════════════════════════════
