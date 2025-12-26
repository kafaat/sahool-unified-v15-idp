-- SAHOOL Financial Data Seed
-- Sample transactions, invoices, and subscriptions

-- Create tables if not exist
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id UUID,
    farm_id UUID,
    field_id UUID,

    transaction_type VARCHAR(50) NOT NULL, -- INCOME, EXPENSE, INVESTMENT
    category VARCHAR(100) NOT NULL, -- SEED_PURCHASE, FERTILIZER, HARVEST_SALE, etc.
    subcategory VARCHAR(100),

    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'YER',

    description TEXT,
    description_ar TEXT,

    transaction_date DATE NOT NULL,
    payment_method VARCHAR(50), -- CASH, BANK_TRANSFER, MOBILE_MONEY, CREDIT

    reference_type VARCHAR(50), -- invoice, purchase_order, etc.
    reference_id UUID,

    invoice_number VARCHAR(100),
    receipt_number VARCHAR(100),

    vendor_supplier VARCHAR(200),
    vendor_supplier_ar VARCHAR(200),

    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    invoice_type VARCHAR(50) NOT NULL, -- SALE, PURCHASE
    status VARCHAR(50) DEFAULT 'pending', -- pending, paid, overdue, cancelled

    customer_vendor_id UUID,
    customer_vendor_name VARCHAR(200),
    customer_vendor_name_ar VARCHAR(200),

    issue_date DATE NOT NULL,
    due_date DATE,
    paid_date DATE,

    subtotal DECIMAL(15, 2) NOT NULL,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) NOT NULL,
    amount_paid DECIMAL(15, 2) DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'YER',

    notes TEXT,
    terms_conditions TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS invoice_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES invoices(id) NOT NULL,
    line_number INTEGER NOT NULL,

    item_type VARCHAR(50), -- product, service
    item_id UUID, -- Reference to inventory item or service
    description VARCHAR(500) NOT NULL,
    description_ar VARCHAR(500),

    quantity DECIMAL(12, 3) NOT NULL,
    unit VARCHAR(20),
    unit_price DECIMAL(12, 2) NOT NULL,
    line_total DECIMAL(15, 2) NOT NULL,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id UUID,

    plan_name VARCHAR(100) NOT NULL,
    plan_name_ar VARCHAR(100),
    plan_type VARCHAR(50), -- BASIC, PREMIUM, ENTERPRISE

    status VARCHAR(50) DEFAULT 'active', -- active, suspended, cancelled, expired

    start_date DATE NOT NULL,
    end_date DATE,
    renewal_date DATE,

    billing_cycle VARCHAR(50), -- monthly, quarterly, annual
    price_per_cycle DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'YER',

    features_json JSONB,

    auto_renew BOOLEAN DEFAULT true,
    trial_end_date DATE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_farm_date ON transactions(farm_id, transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_type_date ON transactions(transaction_type, transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status, due_date);
CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant ON subscriptions(tenant_id, status);

-- ========================================
-- INSERT SAMPLE SUBSCRIPTIONS
-- ========================================

INSERT INTO subscriptions (
    tenant_id, user_id, plan_name, plan_name_ar, plan_type, status,
    start_date, end_date, renewal_date, billing_cycle, price_per_cycle,
    features_json, auto_renew
)
VALUES
('tenant-sahool-main'::UUID, 'f1111111-1111-1111-1111-111111111111'::UUID,
    'SAHOOL Premium', 'سهول بريميوم', 'PREMIUM', 'active',
    CURRENT_DATE - INTERVAL '6 months', CURRENT_DATE + INTERVAL '6 months', CURRENT_DATE + INTERVAL '1 month',
    'monthly', 15000.00,
    '{"max_farms": 10, "max_fields": 100, "satellite_monitoring": true, "ai_advisor": true, "weather_alerts": true}'::jsonb,
    true),

('tenant-sahool-main'::UUID, 'f2222222-2222-2222-2222-222222222222'::UUID,
    'SAHOOL Basic', 'سهول أساسي', 'BASIC', 'active',
    CURRENT_DATE - INTERVAL '4 months', CURRENT_DATE + INTERVAL '8 months', CURRENT_DATE + INTERVAL '1 month',
    'monthly', 5000.00,
    '{"max_farms": 3, "max_fields": 20, "satellite_monitoring": false, "ai_advisor": false, "weather_alerts": true}'::jsonb,
    true),

('tenant-sahool-main'::UUID, 'f3333333-3333-3333-3333-333333333333'::UUID,
    'SAHOOL Premium', 'سهول بريميوم', 'PREMIUM', 'active',
    CURRENT_DATE - INTERVAL '8 months', CURRENT_DATE + INTERVAL '4 months', CURRENT_DATE + INTERVAL '1 month',
    'monthly', 15000.00,
    '{"max_farms": 10, "max_fields": 100, "satellite_monitoring": true, "ai_advisor": true, "weather_alerts": true}'::jsonb,
    true),

('tenant-sahool-main'::UUID, 'f4444444-4444-4444-4444-444444444444'::UUID,
    'SAHOOL Basic', 'سهول أساسي', 'BASIC', 'active',
    CURRENT_DATE - INTERVAL '3 months', CURRENT_DATE + INTERVAL '9 months', CURRENT_DATE + INTERVAL '1 month',
    'monthly', 5000.00,
    '{"max_farms": 3, "max_fields": 20, "satellite_monitoring": false, "ai_advisor": false, "weather_alerts": true}'::jsonb,
    true),

('tenant-sahool-main'::UUID, 'f5555555-5555-5555-5555-555555555555'::UUID,
    'SAHOOL Enterprise', 'سهول للمؤسسات', 'ENTERPRISE', 'active',
    CURRENT_DATE - INTERVAL '5 months', CURRENT_DATE + INTERVAL '7 months', CURRENT_DATE + INTERVAL '1 month',
    'annual', 150000.00,
    '{"max_farms": 999, "max_fields": 9999, "satellite_monitoring": true, "ai_advisor": true, "weather_alerts": true, "api_access": true, "priority_support": true}'::jsonb,
    true);

-- ========================================
-- INSERT SAMPLE TRANSACTIONS - EXPENSES
-- ========================================

-- Seed purchases
INSERT INTO transactions (
    tenant_id, user_id, farm_id, transaction_type, category, subcategory,
    amount, description, description_ar, transaction_date, payment_method,
    vendor_supplier, vendor_supplier_ar
)
VALUES
-- Ahmed Al-Sanani (Farm 1) transactions
('tenant-sahool-main'::UUID, 'f1111111-1111-1111-1111-111111111111'::UUID, '11111111-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'SEED_PURCHASE', 'Wheat', 50000.00,
    'Wheat seeds for North Field', 'بذور قمح للحقل الشمالي',
    CURRENT_DATE - INTERVAL '5 months', 'CASH',
    'Yemen Agricultural Supplies Co.', 'شركة اليمن للمستلزمات الزراعية'),

('tenant-sahool-main'::UUID, 'f1111111-1111-1111-1111-111111111111'::UUID, '11111111-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'FERTILIZER_PURCHASE', 'NPK', 120000.00,
    'NPK fertilizer 10 bags', 'سماد NPK 10 أكياس',
    CURRENT_DATE - INTERVAL '4 months', 'BANK_TRANSFER',
    'Al-Thawra Seeds & Fertilizers', 'الثورة للبذور والأسمدة'),

('tenant-sahool-main'::UUID, 'f1111111-1111-1111-1111-111111111111'::UUID, '11111111-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'LABOR', 'Planting', 75000.00,
    'Labor for planting wheat', 'عمالة لزراعة القمح',
    CURRENT_DATE - INTERVAL '5 months', 'CASH', NULL, NULL),

('tenant-sahool-main'::UUID, 'f1111111-1111-1111-1111-111111111111'::UUID, '11111111-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'IRRIGATION', 'Water', 35000.00,
    'Irrigation system maintenance', 'صيانة نظام الري',
    CURRENT_DATE - INTERVAL '3 months', 'CASH', NULL, NULL),

('tenant-sahool-main'::UUID, 'f1111111-1111-1111-1111-111111111111'::UUID, '11111111-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'PESTICIDE_PURCHASE', 'Herbicide', 28000.00,
    'Herbicide for weed control', 'مبيد أعشاب لمكافحة الحشائش',
    CURRENT_DATE - INTERVAL '3 months', 'MOBILE_MONEY',
    'International Agro Tech Yemen', 'اليمن للتكنولوجيا الزراعية الدولية'),

-- Mohammed Al-Taizi (Farm 3) transactions - Coffee
('tenant-sahool-main'::UUID, 'f2222222-2222-2222-2222-222222222222'::UUID, '22222222-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'FERTILIZER_PURCHASE', 'Organic', 85000.00,
    'Organic fertilizer for coffee', 'سماد عضوي للبن',
    CURRENT_DATE - INTERVAL '4 months', 'BANK_TRANSFER',
    'Green Yemen Trading', 'اليمن الأخضر للتجارة'),

('tenant-sahool-main'::UUID, 'f2222222-2222-2222-2222-222222222222'::UUID, '22222222-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'LABOR', 'Pruning', 60000.00,
    'Coffee tree pruning labor', 'عمالة تقليم أشجار البن',
    CURRENT_DATE - INTERVAL '3 months', 'CASH', NULL, NULL),

('tenant-sahool-main'::UUID, 'f2222222-2222-2222-2222-222222222222'::UUID, '22222222-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'EQUIPMENT', 'Processing', 450000.00,
    'Coffee processing equipment', 'معدات معالجة البن',
    CURRENT_DATE - INTERVAL '2 months', 'BANK_TRANSFER', NULL, NULL),

-- Ali Al-Hadrami (Farm 5) transactions - Date Palm
('tenant-sahool-main'::UUID, 'f3333333-3333-3333-3333-333333333333'::UUID, '33333333-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'FERTILIZER_PURCHASE', 'Compound', 180000.00,
    'Fertilizer for date palms', 'سماد لنخيل التمر',
    CURRENT_DATE - INTERVAL '6 months', 'BANK_TRANSFER',
    'Hadramout Farming Solutions', 'حلول حضرموت الزراعية'),

('tenant-sahool-main'::UUID, 'f3333333-3333-3333-3333-333333333333'::UUID, '33333333-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'IRRIGATION', 'System Upgrade', 850000.00,
    'Drip irrigation system installation', 'تركيب نظام الري بالتنقيط',
    CURRENT_DATE - INTERVAL '5 months', 'BANK_TRANSFER', NULL, NULL),

('tenant-sahool-main'::UUID, 'f3333333-3333-3333-3333-333333333333'::UUID, '33333333-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'LABOR', 'Pollination', 95000.00,
    'Manual pollination labor', 'عمالة التلقيح اليدوي',
    CURRENT_DATE - INTERVAL '2 months', 'CASH', NULL, NULL),

-- Fatima Al-Hudaydi (Farm 9) transactions - Large complex
('tenant-sahool-main'::UUID, 'f5555555-5555-5555-5555-555555555555'::UUID, '55555555-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'SEED_PURCHASE', 'Vegetables', 280000.00,
    'Various vegetable seeds', 'بذور خضروات متنوعة',
    CURRENT_DATE - INTERVAL '5 months', 'BANK_TRANSFER',
    'Red Sea Agricultural Import/Export', 'شركة البحر الأحمر للاستيراد والتصدير الزراعي'),

('tenant-sahool-main'::UUID, 'f5555555-5555-5555-5555-555555555555'::UUID, '55555555-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'EQUIPMENT', 'Tractor', 3500000.00,
    'New tractor purchase', 'شراء جرار جديد',
    CURRENT_DATE - INTERVAL '4 months', 'BANK_TRANSFER', NULL, NULL),

('tenant-sahool-main'::UUID, 'f5555555-5555-5555-5555-555555555555'::UUID, '55555555-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'FERTILIZER_PURCHASE', 'Bulk Order', 650000.00,
    'Bulk fertilizer order for 100 hectares', 'طلب سماد كبير لـ 100 هكتار',
    CURRENT_DATE - INTERVAL '3 months', 'BANK_TRANSFER',
    'Red Sea Agricultural Import/Export', 'شركة البحر الأحمر للاستيراد والتصدير الزراعي'),

('tenant-sahool-main'::UUID, 'f5555555-5555-5555-5555-555555555555'::UUID, '55555555-1111-1111-1111-111111111111'::UUID,
    'EXPENSE', 'LABOR', 'Harvesting', 320000.00,
    'Harvest labor - tomatoes and vegetables', 'عمالة الحصاد - طماطم وخضروات',
    CURRENT_DATE - INTERVAL '1 month', 'CASH', NULL, NULL);

-- ========================================
-- INSERT SAMPLE TRANSACTIONS - INCOME
-- ========================================

INSERT INTO transactions (
    tenant_id, user_id, farm_id, transaction_type, category, subcategory,
    amount, description, description_ar, transaction_date, payment_method,
    vendor_supplier, vendor_supplier_ar
)
VALUES
-- Harvest sales
('tenant-sahool-main'::UUID, 'f1111111-1111-1111-1111-111111111111'::UUID, '11111111-1111-1111-1111-111111111111'::UUID,
    'INCOME', 'HARVEST_SALE', 'Wheat', 450000.00,
    'Wheat harvest sale - 1200 kg', 'بيع محصول القمح - 1200 كجم',
    CURRENT_DATE - INTERVAL '1 month', 'BANK_TRANSFER',
    'Al-Salam Grain Trading', 'تجارة الحبوب السلام'),

('tenant-sahool-main'::UUID, 'f2222222-2222-2222-2222-222222222222'::UUID, '22222222-1111-1111-1111-111111111111'::UUID,
    'INCOME', 'HARVEST_SALE', 'Coffee', 1800000.00,
    'Coffee harvest sale - 150 kg premium beans', 'بيع محصول البن - 150 كجم حبوب ممتازة',
    CURRENT_DATE - INTERVAL '2 weeks', 'BANK_TRANSFER',
    'Yemen Coffee Exporters', 'مصدرو البن اليمني'),

('tenant-sahool-main'::UUID, 'f3333333-3333-3333-3333-333333333333'::UUID, '33333333-1111-1111-1111-111111111111'::UUID,
    'INCOME', 'HARVEST_SALE', 'Dates', 2400000.00,
    'Premium dates harvest - 1500 kg', 'محصول تمور ممتازة - 1500 كجم',
    CURRENT_DATE - INTERVAL '1 month', 'BANK_TRANSFER',
    'Gulf Dates Trading Co.', 'شركة تجارة التمور الخليجية'),

('tenant-sahool-main'::UUID, 'f5555555-5555-5555-5555-555555555555'::UUID, '55555555-1111-1111-1111-111111111111'::UUID,
    'INCOME', 'HARVEST_SALE', 'Tomatoes', 1850000.00,
    'Tomato harvest sale - 3700 kg', 'بيع محصول الطماطم - 3700 كجم',
    CURRENT_DATE - INTERVAL '3 weeks', 'BANK_TRANSFER',
    'Sana\'a Vegetable Market', 'سوق صنعاء للخضروات'),

('tenant-sahool-main'::UUID, 'f5555555-5555-5555-5555-555555555555'::UUID, '55555555-1111-1111-1111-111111111111'::UUID,
    'INCOME', 'HARVEST_SALE', 'Onions', 980000.00,
    'Onion harvest sale - 2000 kg', 'بيع محصول البصل - 2000 كجم',
    CURRENT_DATE - INTERVAL '2 weeks', 'CASH',
    'Local Market', 'السوق المحلي'),

-- Government subsidies
('tenant-sahool-main'::UUID, 'f1111111-1111-1111-1111-111111111111'::UUID, '11111111-1111-1111-1111-111111111111'::UUID,
    'INCOME', 'SUBSIDY', 'Agricultural Support', 100000.00,
    'Government agricultural support program', 'برنامج الدعم الزراعي الحكومي',
    CURRENT_DATE - INTERVAL '2 months', 'BANK_TRANSFER',
    'Ministry of Agriculture', 'وزارة الزراعة'),

('tenant-sahool-main'::UUID, 'f4444444-4444-4444-4444-444444444444'::UUID, '44444444-1111-1111-1111-111111111111'::UUID,
    'INCOME', 'SUBSIDY', 'Seed Distribution', 75000.00,
    'Subsidized seed distribution program', 'برنامج توزيع البذور المدعومة',
    CURRENT_DATE - INTERVAL '3 months', 'BANK_TRANSFER',
    'Ministry of Agriculture', 'وزارة الزراعة');

-- ========================================
-- INSERT SAMPLE INVOICES
-- ========================================

-- Purchase invoice (expense)
INSERT INTO invoices (
    tenant_id, invoice_number, invoice_type, status,
    customer_vendor_name, customer_vendor_name_ar,
    issue_date, due_date, paid_date,
    subtotal, tax_amount, discount_amount, total_amount, amount_paid
)
VALUES
('tenant-sahool-main'::UUID, 'INV-PURCH-2024-001', 'PURCHASE', 'paid',
    'Yemen Agricultural Supplies Co.', 'شركة اليمن للمستلزمات الزراعية',
    CURRENT_DATE - INTERVAL '5 months', CURRENT_DATE - INTERVAL '4 months + 20 days', CURRENT_DATE - INTERVAL '4 months + 25 days',
    50000.00, 0, 0, 50000.00, 50000.00),

('tenant-sahool-main'::UUID, 'INV-PURCH-2024-002', 'PURCHASE', 'paid',
    'Red Sea Agricultural Import/Export', 'شركة البحر الأحمر للاستيراد والتصدير الزراعي',
    CURRENT_DATE - INTERVAL '3 months', CURRENT_DATE - INTERVAL '2 months + 20 days', CURRENT_DATE - INTERVAL '2 months + 15 days',
    650000.00, 0, 32500.00, 617500.00, 617500.00);

-- Sales invoice (income)
INSERT INTO invoices (
    tenant_id, invoice_number, invoice_type, status,
    customer_vendor_name, customer_vendor_name_ar,
    issue_date, due_date, paid_date,
    subtotal, tax_amount, discount_amount, total_amount, amount_paid
)
VALUES
('tenant-sahool-main'::UUID, 'INV-SALE-2024-001', 'SALE', 'paid',
    'Al-Salam Grain Trading', 'تجارة الحبوب السلام',
    CURRENT_DATE - INTERVAL '1 month', CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE - INTERVAL '10 days',
    450000.00, 0, 0, 450000.00, 450000.00),

('tenant-sahool-main'::UUID, 'INV-SALE-2024-002', 'SALE', 'paid',
    'Yemen Coffee Exporters', 'مصدرو البن اليمني',
    CURRENT_DATE - INTERVAL '2 weeks', CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE - INTERVAL '1 day',
    1800000.00, 0, 0, 1800000.00, 1800000.00),

('tenant-sahool-main'::UUID, 'INV-SALE-2024-003', 'SALE', 'pending',
    'Sana\'a Vegetable Market', 'سوق صنعاء للخضروات',
    CURRENT_DATE - INTERVAL '1 week', CURRENT_DATE + INTERVAL '1 week', NULL,
    1850000.00, 0, 0, 1850000.00, 0);

-- Verification queries
SELECT
    transaction_type,
    category,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    currency
FROM transactions
GROUP BY transaction_type, category, currency
ORDER BY transaction_type, total_amount DESC;

SELECT
    u.name as farmer,
    COUNT(t.id) as transaction_count,
    SUM(CASE WHEN t.transaction_type = 'INCOME' THEN t.amount ELSE 0 END) as total_income,
    SUM(CASE WHEN t.transaction_type = 'EXPENSE' THEN t.amount ELSE 0 END) as total_expenses,
    SUM(CASE WHEN t.transaction_type = 'INCOME' THEN t.amount ELSE -t.amount END) as net_profit
FROM transactions t
JOIN users u ON t.user_id = u.id
GROUP BY u.id, u.name
ORDER BY net_profit DESC;

SELECT
    plan_type,
    COUNT(*) as subscriber_count,
    SUM(price_per_cycle) as monthly_revenue,
    SUM(price_per_cycle * 12) as annual_revenue_projection
FROM subscriptions
WHERE status = 'active'
GROUP BY plan_type
ORDER BY monthly_revenue DESC;

SELECT
    invoice_type,
    status,
    COUNT(*) as count,
    SUM(total_amount) as total,
    SUM(amount_paid) as paid,
    SUM(total_amount - amount_paid) as outstanding
FROM invoices
GROUP BY invoice_type, status
ORDER BY invoice_type, status;
