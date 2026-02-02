-- SAHOOL Community Chat Service - Initial Migration
-- خدمة محادثات المجتمع - الهجرة الأولية
-- Created: 2026-02-02

-- ═══════════════════════════════════════════════════════════════════════════
-- Enable required extensions
-- تمكين الإضافات المطلوبة
-- ═══════════════════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. Chat Rooms Table - جدول غرف المحادثات
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE "community_chat_rooms" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" VARCHAR(255) NOT NULL,
    "type" VARCHAR(50) NOT NULL DEFAULT 'public',
    "tenant_id" VARCHAR(100) NOT NULL,
    "status" VARCHAR(50) NOT NULL DEFAULT 'active',
    "farmer_id" VARCHAR(100),
    "farmer_name" VARCHAR(255),
    "expert_id" VARCHAR(100),
    "expert_name" VARCHAR(255),
    "governorate" VARCHAR(100),
    "topic" VARCHAR(255),
    "diagnosis_id" VARCHAR(100),
    "created_by" VARCHAR(100),
    "accepted_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for Chat Rooms
CREATE INDEX "idx_chat_room_tenant" ON "community_chat_rooms"("tenant_id");
CREATE INDEX "idx_chat_room_status" ON "community_chat_rooms"("status");
CREATE INDEX "idx_chat_room_tenant_status" ON "community_chat_rooms"("tenant_id", "status");
CREATE INDEX "idx_chat_room_farmer" ON "community_chat_rooms"("farmer_id");
CREATE INDEX "idx_chat_room_expert" ON "community_chat_rooms"("expert_id");
CREATE INDEX "idx_chat_room_created" ON "community_chat_rooms"("created_at");

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. Messages Table - جدول الرسائل
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE "community_chat_messages" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "content" TEXT NOT NULL,
    "sender_id" VARCHAR(100) NOT NULL,
    "sender_name" VARCHAR(255) NOT NULL,
    "sender_type" VARCHAR(50) NOT NULL DEFAULT 'farmer',
    "room_id" UUID NOT NULL REFERENCES "community_chat_rooms"("id") ON DELETE CASCADE,
    "attachments" JSONB DEFAULT '[]',
    "status" VARCHAR(50) NOT NULL DEFAULT 'delivered',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for Messages
CREATE INDEX "idx_chat_message_room" ON "community_chat_messages"("room_id");
CREATE INDEX "idx_chat_message_sender" ON "community_chat_messages"("sender_id");
CREATE INDEX "idx_chat_message_created" ON "community_chat_messages"("created_at");
CREATE INDEX "idx_chat_message_room_created" ON "community_chat_messages"("room_id", "created_at");

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. Chat Members Table - جدول أعضاء المحادثات
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE "community_chat_members" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "odol_user_id" VARCHAR(100),
    "user_id" VARCHAR(100) NOT NULL,
    "user_name" VARCHAR(255) NOT NULL,
    "user_type" VARCHAR(50) NOT NULL DEFAULT 'member',
    "room_id" UUID NOT NULL REFERENCES "community_chat_rooms"("id") ON DELETE CASCADE,
    "role" VARCHAR(50) NOT NULL DEFAULT 'member',
    "joined_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT "community_chat_members_user_room_unique" UNIQUE ("user_id", "room_id")
);

-- Indexes for Chat Members
CREATE INDEX "idx_chat_member_room" ON "community_chat_members"("room_id");
CREATE INDEX "idx_chat_member_user" ON "community_chat_members"("user_id");

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. Helper Functions - وظائف مساعدة
-- ═══════════════════════════════════════════════════════════════════════════

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_chat_room_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for chat rooms
CREATE TRIGGER update_chat_rooms_updated_at
    BEFORE UPDATE ON "community_chat_rooms"
    FOR EACH ROW
    EXECUTE FUNCTION update_chat_room_updated_at();

-- ═══════════════════════════════════════════════════════════════════════════
-- Comments - التعليقات
-- ═══════════════════════════════════════════════════════════════════════════

COMMENT ON TABLE "community_chat_rooms" IS 'غرف المحادثات للتواصل بين المزارعين والخبراء - Chat rooms for farmer-expert communication';
COMMENT ON TABLE "community_chat_messages" IS 'الرسائل المتبادلة في غرف المحادثات - Messages exchanged in chat rooms';
COMMENT ON TABLE "community_chat_members" IS 'أعضاء غرف المحادثات - Chat room members';
