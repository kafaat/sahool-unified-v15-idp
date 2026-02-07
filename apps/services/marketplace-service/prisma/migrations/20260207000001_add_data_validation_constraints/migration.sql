-- Migration: Add Data Validation Constraints
-- الهجرة: إضافة قيود التحقق من البيانات
-- Created: 2026-02-07
-- Description: Adds CHECK constraints for data integrity and validation

-- ═══════════════════════════════════════════════════════════════════════════════
-- Product Table Constraints
-- قيود جدول المنتجات
-- ═══════════════════════════════════════════════════════════════════════════════

-- Price must be positive
-- السعر يجب أن يكون موجباً
ALTER TABLE "products"
ADD CONSTRAINT "chk_product_price_positive"
CHECK ("price" > 0);

-- Stock must be non-negative
-- المخزون يجب أن يكون غير سالب
ALTER TABLE "products"
ADD CONSTRAINT "chk_product_stock_non_negative"
CHECK ("stock" >= 0);

-- Quality grade must be valid
-- درجة الجودة يجب أن تكون صالحة
ALTER TABLE "products"
ADD CONSTRAINT "chk_product_quality_grade"
CHECK ("quality_grade" IS NULL OR "quality_grade" IN ('A', 'B', 'C'));

-- ═══════════════════════════════════════════════════════════════════════════════
-- Order Table Constraints
-- قيود جدول الطلبات
-- ═══════════════════════════════════════════════════════════════════════════════

-- Subtotal must be positive
-- المجموع الفرعي يجب أن يكون موجباً
ALTER TABLE "orders"
ADD CONSTRAINT "chk_order_subtotal_positive"
CHECK ("subtotal" > 0);

-- Delivery fee must be non-negative
-- رسوم التوصيل يجب أن تكون غير سالبة
ALTER TABLE "orders"
ADD CONSTRAINT "chk_order_delivery_fee_non_negative"
CHECK ("delivery_fee" >= 0);

-- Service fee must be non-negative
-- رسوم الخدمة يجب أن تكون غير سالبة
ALTER TABLE "orders"
ADD CONSTRAINT "chk_order_service_fee_non_negative"
CHECK ("service_fee" >= 0);

-- Total amount must be positive and consistent
-- المبلغ الإجمالي يجب أن يكون موجباً ومتسقاً
ALTER TABLE "orders"
ADD CONSTRAINT "chk_order_total_amount_positive"
CHECK ("total_amount" > 0);

ALTER TABLE "orders"
ADD CONSTRAINT "chk_order_total_consistent"
CHECK ("total_amount" >= "subtotal" + "delivery_fee" + "service_fee" - 0.01);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Order Item Table Constraints
-- قيود جدول عناصر الطلب
-- ═══════════════════════════════════════════════════════════════════════════════

-- Quantity must be positive
-- الكمية يجب أن تكون موجبة
ALTER TABLE "order_items"
ADD CONSTRAINT "chk_order_item_quantity_positive"
CHECK ("quantity" > 0);

-- Unit price must be positive
-- سعر الوحدة يجب أن يكون موجباً
ALTER TABLE "order_items"
ADD CONSTRAINT "chk_order_item_unit_price_positive"
CHECK ("unit_price" > 0);

-- Total price must be positive
-- السعر الإجمالي يجب أن يكون موجباً
ALTER TABLE "order_items"
ADD CONSTRAINT "chk_order_item_total_price_positive"
CHECK ("total_price" > 0);

-- Total price should match quantity * unit_price (with small tolerance for rounding)
-- السعر الإجمالي يجب أن يتطابق مع الكمية × سعر الوحدة
ALTER TABLE "order_items"
ADD CONSTRAINT "chk_order_item_price_consistent"
CHECK ("total_price" >= ("quantity" * "unit_price") - 0.01
   AND "total_price" <= ("quantity" * "unit_price") + 0.01);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Wallet Table Constraints
-- قيود جدول المحافظ
-- ═══════════════════════════════════════════════════════════════════════════════

-- Balance must be non-negative
-- الرصيد يجب أن يكون غير سالب
ALTER TABLE "wallets"
ADD CONSTRAINT "chk_wallet_balance_non_negative"
CHECK ("balance" >= 0);

-- Escrow balance must be non-negative
-- رصيد الإسكرو يجب أن يكون غير سالب
ALTER TABLE "wallets"
ADD CONSTRAINT "chk_wallet_escrow_non_negative"
CHECK ("escrow_balance" >= 0);

-- Credit score must be in valid range (300-850)
-- درجة الائتمان يجب أن تكون في النطاق الصالح
ALTER TABLE "wallets"
ADD CONSTRAINT "chk_wallet_credit_score_range"
CHECK ("credit_score" >= 300 AND "credit_score" <= 850);

-- Loan limit must be non-negative
-- حد القرض يجب أن يكون غير سالب
ALTER TABLE "wallets"
ADD CONSTRAINT "chk_wallet_loan_limit_non_negative"
CHECK ("loan_limit" >= 0);

-- Current loan must be non-negative
-- القرض الحالي يجب أن يكون غير سالب
ALTER TABLE "wallets"
ADD CONSTRAINT "chk_wallet_current_loan_non_negative"
CHECK ("current_loan" >= 0);

-- Current loan should not exceed loan limit
-- القرض الحالي يجب ألا يتجاوز حد القرض
ALTER TABLE "wallets"
ADD CONSTRAINT "chk_wallet_loan_within_limit"
CHECK ("current_loan" <= "loan_limit" OR "loan_limit" = 0);

-- Daily withdraw limit must be positive
-- حد السحب اليومي يجب أن يكون موجباً
ALTER TABLE "wallets"
ADD CONSTRAINT "chk_wallet_daily_limit_positive"
CHECK ("daily_withdraw_limit" > 0);

-- Daily withdrawn must be non-negative
-- المسحوب اليومي يجب أن يكون غير سالب
ALTER TABLE "wallets"
ADD CONSTRAINT "chk_wallet_daily_withdrawn_non_negative"
CHECK ("daily_withdrawn_today" >= 0);

-- Version must be non-negative (for optimistic locking)
-- الإصدار يجب أن يكون غير سالب
ALTER TABLE "wallets"
ADD CONSTRAINT "chk_wallet_version_non_negative"
CHECK ("version" >= 0);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Transaction Table Constraints
-- قيود جدول المعاملات
-- ═══════════════════════════════════════════════════════════════════════════════

-- Amount must be positive
-- المبلغ يجب أن يكون موجباً
ALTER TABLE "transactions"
ADD CONSTRAINT "chk_transaction_amount_positive"
CHECK ("amount" > 0);

-- Balance after must be non-negative
-- الرصيد بعد يجب أن يكون غير سالب
ALTER TABLE "transactions"
ADD CONSTRAINT "chk_transaction_balance_after_non_negative"
CHECK ("balance_after" >= 0);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Loan Table Constraints
-- قيود جدول القروض
-- ═══════════════════════════════════════════════════════════════════════════════

-- Loan amount must be positive
-- مبلغ القرض يجب أن يكون موجباً
ALTER TABLE "loans"
ADD CONSTRAINT "chk_loan_amount_positive"
CHECK ("amount" > 0);

-- Interest rate must be non-negative
-- معدل الفائدة يجب أن يكون غير سالب
ALTER TABLE "loans"
ADD CONSTRAINT "chk_loan_interest_rate_non_negative"
CHECK ("interest_rate" >= 0);

-- Total due must be positive
-- إجمالي المستحق يجب أن يكون موجباً
ALTER TABLE "loans"
ADD CONSTRAINT "chk_loan_total_due_positive"
CHECK ("total_due" > 0);

-- Paid amount must be non-negative
-- المبلغ المدفوع يجب أن يكون غير سالب
ALTER TABLE "loans"
ADD CONSTRAINT "chk_loan_paid_amount_non_negative"
CHECK ("paid_amount" >= 0);

-- Paid amount should not exceed total due
-- المبلغ المدفوع يجب ألا يتجاوز إجمالي المستحق
ALTER TABLE "loans"
ADD CONSTRAINT "chk_loan_paid_not_exceeds_due"
CHECK ("paid_amount" <= "total_due");

-- Term months must be positive
-- مدة الأشهر يجب أن تكون موجبة
ALTER TABLE "loans"
ADD CONSTRAINT "chk_loan_term_months_positive"
CHECK ("term_months" > 0);

-- Due date must be after start date
-- تاريخ الاستحقاق يجب أن يكون بعد تاريخ البدء
ALTER TABLE "loans"
ADD CONSTRAINT "chk_loan_due_after_start"
CHECK ("due_date" > "start_date");

-- ═══════════════════════════════════════════════════════════════════════════════
-- Escrow Table Constraints
-- قيود جدول الإسكرو
-- ═══════════════════════════════════════════════════════════════════════════════

-- Escrow amount must be positive
-- مبلغ الإسكرو يجب أن يكون موجباً
ALTER TABLE "escrows"
ADD CONSTRAINT "chk_escrow_amount_positive"
CHECK ("amount" > 0);

-- Buyer and seller wallets must be different
-- محفظة المشتري والبائع يجب أن تكون مختلفة
ALTER TABLE "escrows"
ADD CONSTRAINT "chk_escrow_different_wallets"
CHECK ("buyer_wallet_id" != "seller_wallet_id");

-- ═══════════════════════════════════════════════════════════════════════════════
-- Seller Profile Constraints
-- قيود ملف البائع
-- ═══════════════════════════════════════════════════════════════════════════════

-- Rating must be between 0 and 5
-- التقييم يجب أن يكون بين 0 و 5
ALTER TABLE "seller_profiles"
ADD CONSTRAINT "chk_seller_rating_range"
CHECK ("rating" >= 0 AND "rating" <= 5);

-- Total sales must be non-negative
-- إجمالي المبيعات يجب أن يكون غير سالب
ALTER TABLE "seller_profiles"
ADD CONSTRAINT "chk_seller_total_sales_non_negative"
CHECK ("total_sales" >= 0);

-- Total revenue must be non-negative
-- إجمالي الإيرادات يجب أن يكون غير سالب
ALTER TABLE "seller_profiles"
ADD CONSTRAINT "chk_seller_total_revenue_non_negative"
CHECK ("total_revenue" >= 0);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Buyer Profile Constraints
-- قيود ملف المشتري
-- ═══════════════════════════════════════════════════════════════════════════════

-- Total purchases must be non-negative
-- إجمالي المشتريات يجب أن يكون غير سالب
ALTER TABLE "buyer_profiles"
ADD CONSTRAINT "chk_buyer_total_purchases_non_negative"
CHECK ("total_purchases" >= 0);

-- Total spent must be non-negative
-- إجمالي الإنفاق يجب أن يكون غير سالب
ALTER TABLE "buyer_profiles"
ADD CONSTRAINT "chk_buyer_total_spent_non_negative"
CHECK ("total_spent" >= 0);

-- Loyalty points must be non-negative
-- نقاط الولاء يجب أن تكون غير سالبة
ALTER TABLE "buyer_profiles"
ADD CONSTRAINT "chk_buyer_loyalty_points_non_negative"
CHECK ("loyalty_points" >= 0);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Product Review Constraints
-- قيود مراجعة المنتج
-- ═══════════════════════════════════════════════════════════════════════════════

-- Rating must be between 1 and 5
-- التقييم يجب أن يكون بين 1 و 5
ALTER TABLE "product_reviews"
ADD CONSTRAINT "chk_review_rating_range"
CHECK ("rating" >= 1 AND "rating" <= 5);

-- Helpful count must be non-negative
-- عدد التقييمات المفيدة يجب أن يكون غير سالب
ALTER TABLE "product_reviews"
ADD CONSTRAINT "chk_review_helpful_non_negative"
CHECK ("helpful" >= 0);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Scheduled Payment Constraints
-- قيود الدفعات المجدولة
-- ═══════════════════════════════════════════════════════════════════════════════

-- Scheduled payment amount must be positive
-- مبلغ الدفعة المجدولة يجب أن يكون موجباً
ALTER TABLE "scheduled_payments"
ADD CONSTRAINT "chk_scheduled_payment_amount_positive"
CHECK ("amount" > 0);

-- Failed attempts must be non-negative
-- محاولات الفشل يجب أن تكون غير سالبة
ALTER TABLE "scheduled_payments"
ADD CONSTRAINT "chk_scheduled_payment_failed_attempts_non_negative"
CHECK ("failed_attempts" >= 0);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Comments on constraints
-- التعليقات على القيود
-- ═══════════════════════════════════════════════════════════════════════════════

COMMENT ON CONSTRAINT "chk_wallet_balance_non_negative" ON "wallets"
IS 'Prevents negative wallet balance - critical for financial integrity';

COMMENT ON CONSTRAINT "chk_wallet_credit_score_range" ON "wallets"
IS 'Credit score follows standard FICO range (300-850)';

COMMENT ON CONSTRAINT "chk_escrow_different_wallets" ON "escrows"
IS 'Prevents self-dealing in escrow transactions';

COMMENT ON CONSTRAINT "chk_loan_paid_not_exceeds_due" ON "loans"
IS 'Ensures paid amount never exceeds what is owed';
