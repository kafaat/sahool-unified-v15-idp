-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "ProductCategory" AS ENUM ('HARVEST', 'SEEDS', 'FERTILIZER', 'PESTICIDE', 'EQUIPMENT', 'IRRIGATION', 'OTHER');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "SellerType" AS ENUM ('FARMER', 'COMPANY', 'COOPERATIVE');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "ProductStatus" AS ENUM ('AVAILABLE', 'SOLD_OUT', 'RESERVED', 'PENDING');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "OrderStatus" AS ENUM ('PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "PaymentStatus" AS ENUM ('UNPAID', 'PARTIAL', 'PAID', 'REFUNDED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "CreditTier" AS ENUM ('BRONZE', 'SILVER', 'GOLD', 'PLATINUM');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "TransactionType" AS ENUM ('DEPOSIT', 'WITHDRAWAL', 'PURCHASE', 'SALE', 'LOAN', 'REPAYMENT', 'FEE', 'REFUND', 'MARKETPLACE_SALE', 'MARKETPLACE_PURCHASE', 'LOAN_DISBURSEMENT', 'LOAN_REPAYMENT', 'ESCROW_HOLD', 'ESCROW_RELEASE', 'ESCROW_REFUND', 'SCHEDULED_PAYMENT', 'TRANSFER_IN', 'TRANSFER_OUT');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "TransactionStatus" AS ENUM ('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "LoanPurpose" AS ENUM ('SEEDS', 'FERTILIZER', 'EQUIPMENT', 'IRRIGATION', 'EXPANSION', 'EMERGENCY', 'OTHER');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "LoanStatus" AS ENUM ('PENDING', 'APPROVED', 'ACTIVE', 'PAID', 'DEFAULTED', 'REJECTED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "CreditEventType" AS ENUM ('LOAN_REPAID_ONTIME', 'LOAN_REPAID_LATE', 'LOAN_DEFAULTED', 'ORDER_COMPLETED', 'ORDER_CANCELLED', 'VERIFICATION_UPGRADE', 'FARM_VERIFIED', 'COOPERATIVE_JOINED', 'LAND_VERIFIED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "EscrowStatus" AS ENUM ('HELD', 'RELEASED', 'REFUNDED', 'DISPUTED', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "PaymentFrequency" AS ENUM ('DAILY', 'WEEKLY', 'BIWEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$ BEGIN
    CREATE TYPE "BusinessType" AS ENUM ('INDIVIDUAL', 'FARM', 'COOPERATIVE', 'DISTRIBUTOR', 'RETAILER');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateTable
CREATE TABLE IF NOT EXISTS "products" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "name" TEXT NOT NULL,
    "name_ar" TEXT NOT NULL,
    "category" "ProductCategory" NOT NULL,
    "price" DECIMAL(15,2) NOT NULL,
    "stock" DOUBLE PRECISION NOT NULL,
    "unit" TEXT NOT NULL,
    "description" TEXT,
    "description_ar" TEXT,
    "image_url" TEXT,
    "seller_id" TEXT NOT NULL,
    "seller_type" "SellerType" NOT NULL,
    "seller_name" TEXT,
    "governorate" TEXT,
    "district" TEXT,
    "crop_type" TEXT,
    "harvest_date" TIMESTAMP(3),
    "quality_grade" TEXT,
    "status" "ProductStatus" NOT NULL DEFAULT 'AVAILABLE',
    "featured" BOOLEAN NOT NULL DEFAULT false,
    "deleted_at" TIMESTAMP(3),
    "deleted_by" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "products_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "orders" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "order_number" TEXT NOT NULL,
    "buyer_id" TEXT NOT NULL,
    "buyer_name" TEXT,
    "buyer_phone" TEXT,
    "subtotal" DECIMAL(15,2) NOT NULL,
    "delivery_fee" DECIMAL(15,2) NOT NULL DEFAULT 0,
    "service_fee" DECIMAL(15,2) NOT NULL DEFAULT 0,
    "total_amount" DECIMAL(15,2) NOT NULL,
    "status" "OrderStatus" NOT NULL DEFAULT 'PENDING',
    "payment_status" "PaymentStatus" NOT NULL DEFAULT 'UNPAID',
    "payment_method" TEXT,
    "delivery_address" TEXT,
    "delivery_date" TIMESTAMP(3),
    "delivery_notes" TEXT,
    "deleted_at" TIMESTAMP(3),
    "deleted_by" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "orders_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "order_items" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "order_id" UUID NOT NULL,
    "product_id" UUID NOT NULL,
    "quantity" DOUBLE PRECISION NOT NULL,
    "unit_price" DECIMAL(15,2) NOT NULL,
    "total_price" DECIMAL(15,2) NOT NULL,

    CONSTRAINT "order_items_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "wallets" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "user_id" TEXT NOT NULL,
    "user_type" TEXT NOT NULL,
    "balance" DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    "escrow_balance" DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    "currency" TEXT NOT NULL DEFAULT 'YER',
    "credit_score" INTEGER NOT NULL DEFAULT 300,
    "credit_tier" "CreditTier" NOT NULL DEFAULT 'BRONZE',
    "loan_limit" DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    "current_loan" DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    "daily_withdraw_limit" DECIMAL(15,2) NOT NULL DEFAULT 10000.0,
    "single_transaction_limit" DECIMAL(15,2) NOT NULL DEFAULT 50000.0,
    "requires_pin_for_amount" DECIMAL(15,2) NOT NULL DEFAULT 5000.0,
    "daily_withdrawn_today" DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    "last_withdraw_reset" TIMESTAMP(3),
    "version" INTEGER NOT NULL DEFAULT 0,
    "is_verified" BOOLEAN NOT NULL DEFAULT false,
    "kyc_status" TEXT,
    "pin" TEXT,
    "deleted_at" TIMESTAMP(3),
    "deleted_by" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "wallets_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "transactions" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "wallet_id" UUID NOT NULL,
    "type" "TransactionType" NOT NULL,
    "amount" DECIMAL(15,2) NOT NULL,
    "balance_after" DECIMAL(15,2) NOT NULL,
    "balance_before" DECIMAL(15,2),
    "reference_id" TEXT,
    "reference_type" TEXT,
    "description" TEXT,
    "description_ar" TEXT,
    "status" "TransactionStatus" NOT NULL DEFAULT 'COMPLETED',
    "idempotency_key" TEXT,
    "user_id" TEXT,
    "ip_address" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "transactions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "loans" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "wallet_id" UUID NOT NULL,
    "amount" DECIMAL(15,2) NOT NULL,
    "interest_rate" DECIMAL(5,4) NOT NULL DEFAULT 0,
    "total_due" DECIMAL(15,2) NOT NULL,
    "paid_amount" DECIMAL(15,2) NOT NULL DEFAULT 0,
    "term_months" INTEGER NOT NULL,
    "start_date" TIMESTAMP(3) NOT NULL,
    "due_date" TIMESTAMP(3) NOT NULL,
    "purpose" "LoanPurpose" NOT NULL,
    "purpose_details" TEXT,
    "collateral_type" TEXT,
    "collateral_value" DECIMAL(15,2),
    "status" "LoanStatus" NOT NULL DEFAULT 'PENDING',
    "deleted_at" TIMESTAMP(3),
    "deleted_by" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "loans_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "credit_events" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "wallet_id" UUID NOT NULL,
    "event_type" "CreditEventType" NOT NULL,
    "amount" DECIMAL(15,2),
    "impact" INTEGER NOT NULL,
    "description" TEXT NOT NULL,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "credit_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "escrows" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "order_id" TEXT NOT NULL,
    "buyer_wallet_id" UUID NOT NULL,
    "seller_wallet_id" UUID NOT NULL,
    "amount" DECIMAL(15,2) NOT NULL,
    "status" "EscrowStatus" NOT NULL DEFAULT 'HELD',
    "notes" TEXT,
    "dispute_reason" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "released_at" TIMESTAMP(3),
    "refunded_at" TIMESTAMP(3),

    CONSTRAINT "escrows_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "scheduled_payments" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "wallet_id" UUID NOT NULL,
    "amount" DECIMAL(15,2) NOT NULL,
    "frequency" "PaymentFrequency" NOT NULL,
    "next_payment_date" TIMESTAMP(3) NOT NULL,
    "loan_id" TEXT,
    "description" TEXT,
    "description_ar" TEXT,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "failed_attempts" INTEGER NOT NULL DEFAULT 0,
    "last_payment_date" TIMESTAMP(3),
    "last_failure_reason" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "scheduled_payments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "wallet_audit_logs" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "wallet_id" UUID NOT NULL,
    "transaction_id" UUID,
    "user_id" TEXT,
    "operation" TEXT NOT NULL,
    "balance_before" DECIMAL(15,2) NOT NULL,
    "balance_after" DECIMAL(15,2) NOT NULL,
    "amount" DECIMAL(15,2) NOT NULL,
    "escrow_balance_before" DECIMAL(15,2),
    "escrow_balance_after" DECIMAL(15,2),
    "version_before" INTEGER,
    "version_after" INTEGER,
    "idempotency_key" TEXT,
    "ip_address" TEXT,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "wallet_audit_logs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "seller_profiles" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "business_name" TEXT NOT NULL,
    "business_type" "BusinessType" NOT NULL,
    "tax_id" TEXT,
    "rating" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "total_sales" INTEGER NOT NULL DEFAULT 0,
    "total_revenue" DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "verified_at" TIMESTAMP(3),
    "bank_account" JSONB,
    "payout_preferences" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "seller_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "buyer_profiles" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "shipping_addresses" JSONB,
    "preferred_payment" TEXT,
    "total_purchases" INTEGER NOT NULL DEFAULT 0,
    "total_spent" DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    "loyalty_points" INTEGER NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "buyer_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "product_reviews" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "product_id" UUID NOT NULL,
    "buyer_id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "rating" INTEGER NOT NULL,
    "title" TEXT NOT NULL,
    "comment" TEXT,
    "photos" JSONB,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "helpful" INTEGER NOT NULL DEFAULT 0,
    "reported" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "product_reviews_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "review_responses" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id" TEXT NOT NULL DEFAULT 'unassigned',
    "review_id" UUID NOT NULL,
    "seller_id" UUID NOT NULL,
    "response" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "review_responses_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_product_tenant" ON "products"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_product_tenant_status" ON "products"("tenant_id", "status");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "products_seller_id_status_idx" ON "products"("seller_id", "status");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "products_category_status_idx" ON "products"("category", "status");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "products_status_featured_idx" ON "products"("status", "featured");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "products_id_stock_idx" ON "products"("id", "stock");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "products_deleted_at_idx" ON "products"("deleted_at");

-- CreateIndex
CREATE UNIQUE INDEX IF NOT EXISTS "orders_order_number_key" ON "orders"("order_number");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_order_tenant" ON "orders"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_order_tenant_status" ON "orders"("tenant_id", "status");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "orders_buyer_id_status_idx" ON "orders"("buyer_id", "status");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_order_buyer_date" ON "orders"("buyer_id", "created_at");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "orders_status_created_at_idx" ON "orders"("status", "created_at");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "orders_payment_status_idx" ON "orders"("payment_status");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "orders_created_at_idx" ON "orders"("created_at");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "orders_deleted_at_idx" ON "orders"("deleted_at");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_order_item_tenant" ON "order_items"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "order_items_order_id_idx" ON "order_items"("order_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "order_items_product_id_idx" ON "order_items"("product_id");

-- CreateIndex
CREATE UNIQUE INDEX IF NOT EXISTS "wallets_user_id_key" ON "wallets"("user_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_wallet_tenant" ON "wallets"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "wallets_deleted_at_idx" ON "wallets"("deleted_at");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_wallet_credit_tier" ON "wallets"("credit_tier");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_wallet_verified" ON "wallets"("is_verified");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_wallet_kyc_status" ON "wallets"("kyc_status");

-- CreateIndex
CREATE UNIQUE INDEX IF NOT EXISTS "transactions_idempotency_key_key" ON "transactions"("idempotency_key");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_transaction_tenant" ON "transactions"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_transaction_wallet" ON "transactions"("wallet_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_transaction_reference" ON "transactions"("reference_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_transaction_type" ON "transactions"("type");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_transaction_status" ON "transactions"("status");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_transaction_wallet_date" ON "transactions"("wallet_id", "created_at");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "transactions_idempotency_key_idx" ON "transactions"("idempotency_key");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_loan_tenant" ON "loans"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_loan_wallet" ON "loans"("wallet_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_loan_status" ON "loans"("status");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_loan_wallet_status" ON "loans"("wallet_id", "status");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "loans_deleted_at_idx" ON "loans"("deleted_at");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_credit_event_tenant" ON "credit_events"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "credit_events_wallet_id_idx" ON "credit_events"("wallet_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "credit_events_event_type_idx" ON "credit_events"("event_type");

-- CreateIndex
CREATE UNIQUE INDEX IF NOT EXISTS "escrows_order_id_key" ON "escrows"("order_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_escrow_tenant" ON "escrows"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "escrows_buyer_wallet_id_idx" ON "escrows"("buyer_wallet_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "escrows_seller_wallet_id_idx" ON "escrows"("seller_wallet_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "escrows_status_idx" ON "escrows"("status");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_scheduled_payment_tenant" ON "scheduled_payments"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "scheduled_payments_wallet_id_idx" ON "scheduled_payments"("wallet_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "scheduled_payments_next_payment_date_idx" ON "scheduled_payments"("next_payment_date");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "scheduled_payments_is_active_idx" ON "scheduled_payments"("is_active");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "scheduled_payments_loan_id_idx" ON "scheduled_payments"("loan_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_wallet_audit_tenant" ON "wallet_audit_logs"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "wallet_audit_logs_wallet_id_idx" ON "wallet_audit_logs"("wallet_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "wallet_audit_logs_transaction_id_idx" ON "wallet_audit_logs"("transaction_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "wallet_audit_logs_created_at_idx" ON "wallet_audit_logs"("created_at");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "wallet_audit_logs_idempotency_key_idx" ON "wallet_audit_logs"("idempotency_key");

-- CreateIndex
CREATE UNIQUE INDEX IF NOT EXISTS "seller_profiles_user_id_key" ON "seller_profiles"("user_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "seller_profiles_user_id_idx" ON "seller_profiles"("user_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "seller_profiles_tenant_id_idx" ON "seller_profiles"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "seller_profiles_business_type_idx" ON "seller_profiles"("business_type");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "seller_profiles_verified_idx" ON "seller_profiles"("verified");

-- CreateIndex
CREATE UNIQUE INDEX IF NOT EXISTS "buyer_profiles_user_id_key" ON "buyer_profiles"("user_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "buyer_profiles_user_id_idx" ON "buyer_profiles"("user_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "buyer_profiles_tenant_id_idx" ON "buyer_profiles"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_review_tenant" ON "product_reviews"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "product_reviews_product_id_idx" ON "product_reviews"("product_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "product_reviews_buyer_id_idx" ON "product_reviews"("buyer_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "product_reviews_order_id_idx" ON "product_reviews"("order_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "product_reviews_rating_idx" ON "product_reviews"("rating");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "product_reviews_verified_idx" ON "product_reviews"("verified");

-- CreateIndex
CREATE UNIQUE INDEX IF NOT EXISTS "review_responses_review_id_key" ON "review_responses"("review_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_review_response_tenant" ON "review_responses"("tenant_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "review_responses_review_id_idx" ON "review_responses"("review_id");

-- CreateIndex
CREATE INDEX IF NOT EXISTS "review_responses_seller_id_idx" ON "review_responses"("seller_id");

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "order_items" ADD CONSTRAINT "order_items_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "orders"("id") ON DELETE CASCADE ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "order_items" ADD CONSTRAINT "order_items_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "transactions" ADD CONSTRAINT "transactions_wallet_id_fkey" FOREIGN KEY ("wallet_id") REFERENCES "wallets"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- NOTE: transactions.reference_id is a polymorphic reference (can point to orders, loans,
-- scheduled_payments, etc. based on reference_type). No FK constraint is added intentionally.

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "loans" ADD CONSTRAINT "loans_wallet_id_fkey" FOREIGN KEY ("wallet_id") REFERENCES "wallets"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "credit_events" ADD CONSTRAINT "credit_events_wallet_id_fkey" FOREIGN KEY ("wallet_id") REFERENCES "wallets"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "escrows" ADD CONSTRAINT "escrows_buyer_wallet_id_fkey" FOREIGN KEY ("buyer_wallet_id") REFERENCES "wallets"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "escrows" ADD CONSTRAINT "escrows_seller_wallet_id_fkey" FOREIGN KEY ("seller_wallet_id") REFERENCES "wallets"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "scheduled_payments" ADD CONSTRAINT "scheduled_payments_wallet_id_fkey" FOREIGN KEY ("wallet_id") REFERENCES "wallets"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "wallet_audit_logs" ADD CONSTRAINT "wallet_audit_logs_wallet_id_fkey" FOREIGN KEY ("wallet_id") REFERENCES "wallets"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "wallet_audit_logs" ADD CONSTRAINT "wallet_audit_logs_transaction_id_fkey" FOREIGN KEY ("transaction_id") REFERENCES "transactions"("id") ON DELETE SET NULL ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "product_reviews" ADD CONSTRAINT "product_reviews_buyer_id_fkey" FOREIGN KEY ("buyer_id") REFERENCES "buyer_profiles"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "review_responses" ADD CONSTRAINT "review_responses_review_id_fkey" FOREIGN KEY ("review_id") REFERENCES "product_reviews"("id") ON DELETE CASCADE ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- AddForeignKey
DO $$ BEGIN
    ALTER TABLE "review_responses" ADD CONSTRAINT "review_responses_seller_id_fkey" FOREIGN KEY ("seller_id") REFERENCES "seller_profiles"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
