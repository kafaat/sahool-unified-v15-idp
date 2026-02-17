-- Migration: Add Message Indexes
-- الهجرة: إضافة فهارس الرسائل
-- Created: 2026-02-07
-- Description: Adds indexes to optimize message queries for chat service

-- ═══════════════════════════════════════════════════════════════════════════════
-- Message Table Indexes
-- فهارس جدول الرسائل
-- ═══════════════════════════════════════════════════════════════════════════════

-- Index for time-based message queries
-- فهرس للاستعلامات الزمنية للرسائل
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_message_created"
    ON "community_chat_messages" ("created_at");

-- Composite index for room messages by date (pagination pattern)
-- فهرس مركب لرسائل الغرفة حسب التاريخ (نمط التصفح)
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_message_room_date"
    ON "community_chat_messages" ("room_id", "created_at" DESC);

-- Index for message status filtering
-- فهرس لتصفية حالة الرسالة
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_message_status"
    ON "community_chat_messages" ("status");

-- ═══════════════════════════════════════════════════════════════════════════════
-- Chat Room Additional Indexes
-- فهارس إضافية لغرف المحادثة
-- ═══════════════════════════════════════════════════════════════════════════════

-- Composite index for diagnosis-based chat rooms
-- فهرس مركب لغرف المحادثة القائمة على التشخيص
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_chat_room_diagnosis"
    ON "community_chat_rooms" ("diagnosis_id")
    WHERE "diagnosis_id" IS NOT NULL;

-- Index for room type filtering
-- فهرس لتصفية نوع الغرفة
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_chat_room_type"
    ON "community_chat_rooms" ("type");

-- Composite index for governorate-based rooms
-- فهرس مركب للغرف القائمة على المحافظة
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_chat_room_governorate"
    ON "community_chat_rooms" ("governorate")
    WHERE "governorate" IS NOT NULL;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Chat Member Indexes
-- فهارس أعضاء المحادثة
-- ═══════════════════════════════════════════════════════════════════════════════

-- Index for user type filtering
-- فهرس لتصفية نوع المستخدم
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_chat_member_user_type"
    ON "community_chat_members" ("user_type");

-- Index for user's rooms
-- فهرس لغرف المستخدم
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_chat_member_user"
    ON "community_chat_members" ("user_id");

-- ═══════════════════════════════════════════════════════════════════════════════
-- Comments
-- التعليقات
-- ═══════════════════════════════════════════════════════════════════════════════

COMMENT ON INDEX "idx_message_room_date" IS 'Optimizes fetching recent messages in a chat room with DESC ordering for pagination';
COMMENT ON INDEX "idx_chat_room_diagnosis" IS 'Partial index for diagnosis-linked chat rooms';
