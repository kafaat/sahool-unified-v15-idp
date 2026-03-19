-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Initial schema for chat-service
-- الترحيل: المخطط الأساسي لخدمة المحادثات
-- Creates all tables, enums, indexes, and constraints from scratch
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Create enums
CREATE TYPE "MessageType" AS ENUM ('TEXT', 'IMAGE', 'OFFER', 'SYSTEM');
CREATE TYPE "ParticipantRole" AS ENUM ('BUYER', 'SELLER');

-- Step 2: Create conversations table
CREATE TABLE "conversations" (
    "id" UUID NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "participant_ids" TEXT[],
    "product_id" TEXT,
    "order_id" TEXT,
    "last_message" TEXT,
    "last_message_at" TIMESTAMP(3),
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "conversations_pkey" PRIMARY KEY ("id")
);

-- Step 3: Create messages table
CREATE TABLE "messages" (
    "id" UUID NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "conversation_id" TEXT NOT NULL,
    "sender_id" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "message_type" "MessageType" NOT NULL DEFAULT 'TEXT',
    "attachment_url" TEXT,
    "offer_amount" DOUBLE PRECISION,
    "offer_currency" TEXT DEFAULT 'YER',
    "is_read" BOOLEAN NOT NULL DEFAULT false,
    "read_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "messages_pkey" PRIMARY KEY ("id")
);

-- Step 4: Create participants table
CREATE TABLE "participants" (
    "id" UUID NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "conversation_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "role" "ParticipantRole" NOT NULL DEFAULT 'BUYER',
    "last_read_at" TIMESTAMP(3),
    "unread_count" INTEGER NOT NULL DEFAULT 0,
    "is_online" BOOLEAN NOT NULL DEFAULT false,
    "last_seen_at" TIMESTAMP(3),
    "is_typing" BOOLEAN NOT NULL DEFAULT false,
    "joined_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "participants_pkey" PRIMARY KEY ("id")
);

-- Step 5: Create unique constraints
CREATE UNIQUE INDEX "participants_conversation_id_user_id_key" ON "participants"("conversation_id", "user_id");

-- Step 6: Create indexes for conversations
CREATE INDEX "idx_conversation_tenant" ON "conversations"("tenant_id");
CREATE INDEX "idx_conversation_tenant_active" ON "conversations"("tenant_id", "is_active");
CREATE INDEX "conversations_product_id_idx" ON "conversations"("product_id");
CREATE INDEX "conversations_order_id_idx" ON "conversations"("order_id");
CREATE INDEX "idx_conversation_active_updated" ON "conversations"("is_active", "last_message_at");
CREATE INDEX "idx_conversation_active" ON "conversations"("is_active");

-- Step 7: Create indexes for messages
CREATE INDEX "idx_message_tenant" ON "messages"("tenant_id");
CREATE INDEX "messages_conversation_id_idx" ON "messages"("conversation_id");
CREATE INDEX "messages_sender_id_idx" ON "messages"("sender_id");
CREATE INDEX "messages_created_at_idx" ON "messages"("created_at");
CREATE INDEX "messages_conversation_id_sender_id_is_read_idx" ON "messages"("conversation_id", "sender_id", "is_read");
CREATE INDEX "messages_conversation_id_created_at_idx" ON "messages"("conversation_id", "created_at");

-- Step 8: Create indexes for participants
CREATE INDEX "idx_participant_tenant" ON "participants"("tenant_id");
CREATE INDEX "participants_user_id_idx" ON "participants"("user_id");
CREATE INDEX "participants_conversation_id_idx" ON "participants"("conversation_id");
CREATE INDEX "idx_participant_user_online" ON "participants"("user_id", "is_online");

-- Step 9: Add foreign key constraints
ALTER TABLE "messages" ADD CONSTRAINT "messages_conversation_id_fkey" FOREIGN KEY ("conversation_id") REFERENCES "conversations"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "participants" ADD CONSTRAINT "participants_conversation_id_fkey" FOREIGN KEY ("conversation_id") REFERENCES "conversations"("id") ON DELETE CASCADE ON UPDATE CASCADE;
