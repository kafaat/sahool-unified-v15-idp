-- SAHOOL Inventory Seed Data
-- Sample inventory items, suppliers, and stock movements

-- Clean existing data (optional - comment out for production)
-- TRUNCATE TABLE suppliers, inventory_items, stock_movements CASCADE;

-- Create tables if not exist
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),
    contact_name VARCHAR(200),
    phone VARCHAR(50),
    email VARCHAR(200),
    address TEXT,
    governorate VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Yemen',
    rating DECIMAL(3, 2) CHECK (rating >= 0 AND rating <= 5),
    lead_time_days INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(100) UNIQUE NOT NULL,
    barcode VARCHAR(100),
    name_en VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200) NOT NULL,
    description_en TEXT,
    description_ar TEXT,
    category VARCHAR(50) NOT NULL, -- SEED, FERTILIZER, PESTICIDE, etc.
    subcategory VARCHAR(100),
    unit VARCHAR(20) NOT NULL, -- KG, LITER, PIECE, etc.
    unit_size DECIMAL(10, 3) DEFAULT 1.0,
    current_quantity DECIMAL(12, 3) DEFAULT 0,
    reserved_quantity DECIMAL(12, 3) DEFAULT 0,
    reorder_level DECIMAL(12, 3),
    reorder_quantity DECIMAL(12, 3),
    unit_cost DECIMAL(12, 2),
    selling_price DECIMAL(12, 2),
    currency VARCHAR(10) DEFAULT 'YER',
    supplier_id UUID REFERENCES suppliers(id),
    warehouse_id UUID,
    storage_location VARCHAR(100),
    expiry_date DATE,
    last_restocked TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID REFERENCES inventory_items(id) NOT NULL,
    movement_type VARCHAR(50) NOT NULL, -- PURCHASE, SALE, FIELD_APPLICATION, etc.
    quantity DECIMAL(12, 3) NOT NULL,
    previous_qty DECIMAL(12, 3),
    new_qty DECIMAL(12, 3),
    unit_cost DECIMAL(12, 2),
    total_cost DECIMAL(12, 2),
    reference_type VARCHAR(50), -- e.g., 'purchase_order', 'field_application'
    reference_id UUID,
    field_id UUID,
    crop_season_id UUID,
    performed_by UUID,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- INSERT SUPPLIERS
-- ========================================

INSERT INTO suppliers (id, name, name_ar, contact_name, phone, email, address, governorate, rating, lead_time_days)
VALUES
('s1111111-1111-1111-1111-111111111111', 'Yemen Agricultural Supplies Co.', 'شركة اليمن للمستلزمات الزراعية',
 'Ahmed Al-Hamdi', '+967-777-100100', 'info@yemenagrisupply.ye', 'Industrial Area, Sana''a', 'صنعاء', 4.5, 7),

('s2222222-2222-2222-2222-222222222222', 'Al-Thawra Seeds & Fertilizers', 'الثورة للبذور والأسمدة',
 'Mohammed Al-Dailami', '+967-777-200200', 'sales@althawra-agri.ye', 'Taiz Road, Sana''a', 'صنعاء', 4.2, 10),

('s3333333-3333-3333-3333-333333333333', 'Red Sea Agricultural Import/Export', 'شركة البحر الأحمر للاستيراد والتصدير الزراعي',
 'Hassan Al-Hudaydi', '+967-777-300300', 'contact@redsea-agri.ye', 'Port Area, Al-Hudaydah', 'الحديدة', 4.7, 14),

('s4444444-4444-4444-4444-444444444444', 'Hadramout Farming Solutions', 'حلول حضرموت الزراعية',
 'Ali Al-Kathiri', '+967-777-400400', 'info@hadramout-farm.ye', 'Al-Mukalla City, Hadramout', 'حضرموت', 4.0, 12),

('s5555555-5555-5555-5555-555555555555', 'Green Yemen Trading', 'اليمن الأخضر للتجارة',
 'Fatima Al-Sharif', '+967-777-500500', 'sales@greenyemen.ye', 'Downtown, Ibb', 'إب', 4.3, 8),

('s6666666-6666-6666-6666-666666666666', 'International Agro Tech Yemen', 'اليمن للتكنولوجيا الزراعية الدولية',
 'Dr. Khalid Al-Amri', '+967-777-600600', 'info@iatyemen.com', 'Science Park, Sana''a', 'صنعاء', 4.8, 21);

-- ========================================
-- INSERT INVENTORY ITEMS - SEEDS
-- ========================================

INSERT INTO inventory_items (id, sku, name_en, name_ar, category, subcategory, unit, unit_size, current_quantity, reorder_level, reorder_quantity, unit_cost, selling_price, supplier_id)
VALUES
('i1111111-0001-0001-0001-000000000001', 'SEED-WHEAT-001', 'Wheat Seeds - Improved Variety', 'بذور قمح - صنف محسن', 'SEED', 'Cereals', 'KG', 1.0, 500.0, 100.0, 500.0, 350.00, 450.00, 's1111111-1111-1111-1111-111111111111'),
('i1111111-0001-0001-0001-000000000002', 'SEED-BARLEY-001', 'Barley Seeds - Drought Resistant', 'بذور شعير - مقاوم للجفاف', 'SEED', 'Cereals', 'KG', 1.0, 350.0, 80.0, 400.0, 300.00, 400.00, 's1111111-1111-1111-1111-111111111111'),
('i1111111-0001-0001-0001-000000000003', 'SEED-SORGHUM-001', 'Sorghum Seeds (Dhurra)', 'بذور ذرة رفيعة', 'SEED', 'Cereals', 'KG', 1.0, 280.0, 75.0, 350.0, 320.00, 420.00, 's2222222-2222-2222-2222-222222222222'),
('i1111111-0001-0001-0001-000000000004', 'SEED-CORN-001', 'Hybrid Maize Seeds', 'بذور ذرة شامية هجين', 'SEED', 'Cereals', 'KG', 1.0, 200.0, 50.0, 250.0, 550.00, 700.00, 's2222222-2222-2222-2222-222222222222'),
('i1111111-0001-0001-0001-000000000005', 'SEED-TOMATO-001', 'Tomato Seeds - Heat Tolerant', 'بذور طماطم - تتحمل الحرارة', 'SEED', 'Vegetables', 'GRAM', 100.0, 5000.0, 1000.0, 5000.0, 8.00, 12.00, 's3333333-3333-3333-3333-333333333333'),
('i1111111-0001-0001-0001-000000000006', 'SEED-ONION-001', 'Red Onion Seeds', 'بذور بصل أحمر', 'SEED', 'Vegetables', 'GRAM', 100.0, 3500.0, 800.0, 4000.0, 6.00, 10.00, 's3333333-3333-3333-3333-333333333333'),
('i1111111-0001-0001-0001-000000000007', 'SEED-POTATO-001', 'Potato Seed Tubers', 'درنات بذور البطاطس', 'SEED', 'Vegetables', 'KG', 1.0, 800.0, 200.0, 1000.0, 280.00, 380.00, 's5555555-5555-5555-5555-555555555555'),
('i1111111-0001-0001-0001-000000000008', 'SEED-CUCUMBER-001', 'Cucumber Seeds - F1 Hybrid', 'بذور خيار - هجين من الجيل الأول', 'SEED', 'Vegetables', 'GRAM', 50.0, 2000.0, 500.0, 2500.0, 10.00, 15.00, 's3333333-3333-3333-3333-333333333333'),
('i1111111-0001-0001-0001-000000000009', 'SEED-COFFEE-001', 'Arabica Coffee Seedlings', 'شتلات البن العربي', 'SEED', 'Cash Crops', 'PIECE', 1.0, 500.0, 100.0, 500.0, 150.00, 250.00, 's5555555-5555-5555-5555-555555555555'),
('i1111111-0001-0001-0001-000000000010', 'SEED-DATE-001', 'Date Palm Offshoots', 'فسائل نخيل التمر', 'SEED', 'Tree Fruits', 'PIECE', 1.0, 150.0, 30.0, 150.0, 2500.00, 3500.00, 's4444444-4444-4444-4444-444444444444');

-- ========================================
-- INSERT INVENTORY ITEMS - FERTILIZERS
-- ========================================

INSERT INTO inventory_items (id, sku, name_en, name_ar, category, subcategory, unit, unit_size, current_quantity, reorder_level, reorder_quantity, unit_cost, selling_price, supplier_id)
VALUES
('i2222222-0001-0001-0001-000000000001', 'FERT-NPK-001', 'NPK Fertilizer 20-20-20', 'سماد NPK 20-20-20', 'FERTILIZER', 'Compound', 'BAG', 50.0, 200.0, 50.0, 200.0, 15000.00, 18000.00, 's3333333-3333-3333-3333-333333333333'),
('i2222222-0001-0001-0001-000000000002', 'FERT-UREA-001', 'Urea Fertilizer 46% N', 'سماد يوريا 46% نيتروجين', 'FERTILIZER', 'Nitrogen', 'BAG', 50.0, 350.0, 80.0, 400.0, 12000.00, 14500.00, 's3333333-3333-3333-3333-333333333333'),
('i2222222-0001-0001-0001-000000000003', 'FERT-DAP-001', 'DAP Fertilizer 18-46-0', 'سماد داب 18-46-0', 'FERTILIZER', 'Phosphate', 'BAG', 50.0, 280.0, 70.0, 350.0, 16000.00, 19000.00, 's3333333-3333-3333-3333-333333333333'),
('i2222222-0001-0001-0001-000000000004', 'FERT-COMPOST-001', 'Organic Compost', 'سماد عضوي', 'FERTILIZER', 'Organic', 'BAG', 40.0, 450.0, 100.0, 500.0, 3500.00, 5000.00, 's5555555-5555-5555-5555-555555555555'),
('i2222222-0001-0001-0001-000000000005', 'FERT-MICRO-001', 'Micronutrient Mix', 'خليط العناصر الصغرى', 'FERTILIZER', 'Micronutrients', 'KG', 1.0, 120.0, 30.0, 150.0, 850.00, 1200.00, 's6666666-6666-6666-6666-666666666666'),
('i2222222-0001-0001-0001-000000000006', 'FERT-LIQUID-001', 'Liquid NPK Fertilizer', 'سماد سائل NPK', 'FERTILIZER', 'Liquid', 'LITER', 1.0, 500.0, 100.0, 600.0, 450.00, 650.00, 's6666666-6666-6666-6666-666666666666');

-- ========================================
-- INSERT INVENTORY ITEMS - PESTICIDES
-- ========================================

INSERT INTO inventory_items (id, sku, name_en, name_ar, category, subcategory, unit, unit_size, current_quantity, reorder_level, reorder_quantity, unit_cost, selling_price, supplier_id)
VALUES
('i3333333-0001-0001-0001-000000000001', 'PEST-INSECT-001', 'Malathion Insecticide 50% EC', 'مبيد حشري ملاثيون 50%', 'PESTICIDE', 'Insecticide', 'LITER', 1.0, 150.0, 40.0, 200.0, 2800.00, 3800.00, 's6666666-6666-6666-6666-666666666666'),
('i3333333-0001-0001-0001-000000000002', 'PEST-FUNGI-001', 'Copper Fungicide', 'مبيد فطري نحاسي', 'PESTICIDE', 'Fungicide', 'KG', 1.0, 200.0, 50.0, 250.0, 1800.00, 2500.00, 's6666666-6666-6666-6666-666666666666'),
('i3333333-0001-0001-0001-000000000003', 'PEST-HERB-001', 'Glyphosate Herbicide', 'مبيد أعشاب جليفوسات', 'PESTICIDE', 'Herbicide', 'LITER', 1.0, 180.0, 45.0, 200.0, 2200.00, 3000.00, 's3333333-3333-3333-3333-333333333333'),
('i3333333-0001-0001-0001-000000000004', 'PEST-BIO-001', 'Neem Oil - Organic Pesticide', 'زيت النيم - مبيد عضوي', 'PESTICIDE', 'Organic', 'LITER', 1.0, 120.0, 30.0, 150.0, 1500.00, 2200.00, 's5555555-5555-5555-5555-555555555555'),
('i3333333-0001-0001-0001-000000000005', 'PEST-MITE-001', 'Acaricide for Mites', 'مبيد العناكب', 'PESTICIDE', 'Acaricide', 'LITER', 1.0, 100.0, 25.0, 150.0, 3200.00, 4200.00, 's6666666-6666-6666-6666-666666666666');

-- ========================================
-- INSERT INVENTORY ITEMS - TOOLS & EQUIPMENT
-- ========================================

INSERT INTO inventory_items (id, sku, name_en, name_ar, category, subcategory, unit, unit_size, current_quantity, reorder_level, reorder_quantity, unit_cost, selling_price, supplier_id)
VALUES
('i4444444-0001-0001-0001-000000000001', 'TOOL-HOE-001', 'Agricultural Hoe', 'معول زراعي', 'TOOL', 'Hand Tools', 'PIECE', 1.0, 50.0, 10.0, 50.0, 1200.00, 1800.00, 's1111111-1111-1111-1111-111111111111'),
('i4444444-0001-0001-0001-000000000002', 'TOOL-SPRAYER-001', 'Backpack Sprayer 16L', 'رشاش ظهري 16 لتر', 'TOOL', 'Sprayers', 'PIECE', 1.0, 30.0, 8.0, 40.0, 8500.00, 12000.00, 's1111111-1111-1111-1111-111111111111'),
('i4444444-0001-0001-0001-000000000003', 'TOOL-PRUNER-001', 'Pruning Shears', 'مقص تقليم', 'TOOL', 'Hand Tools', 'PIECE', 1.0, 45.0, 12.0, 50.0, 1800.00, 2500.00, 's2222222-2222-2222-2222-222222222222'),
('i4444444-0001-0001-0001-000000000004', 'EQUIP-PUMP-001', 'Water Pump 2HP', 'مضخة ماء 2 حصان', 'EQUIPMENT_PART', 'Irrigation', 'PIECE', 1.0, 12.0, 3.0, 15.0, 85000.00, 115000.00, 's4444444-4444-4444-4444-444444444444');

-- ========================================
-- INSERT INVENTORY ITEMS - IRRIGATION SUPPLIES
-- ========================================

INSERT INTO inventory_items (id, sku, name_en, name_ar, category, subcategory, unit, unit_size, current_quantity, reorder_level, reorder_quantity, unit_cost, selling_price, supplier_id)
VALUES
('i5555555-0001-0001-0001-000000000001', 'IRRIG-DRIP-001', 'Drip Irrigation Tape 16mm', 'شريط تنقيط 16 ملم', 'IRRIGATION_SUPPLY', 'Drip Systems', 'ROLL', 500.0, 80.0, 20.0, 100.0, 12000.00, 16000.00, 's4444444-4444-4444-4444-444444444444'),
('i5555555-0001-0001-0001-000000000002', 'IRRIG-PIPE-001', 'PVC Pipe 3 inch', 'أنابيب PVC 3 بوصة', 'IRRIGATION_SUPPLY', 'Pipes', 'METER', 6.0, 500.0, 100.0, 600.0, 850.00, 1200.00, 's1111111-1111-1111-1111-111111111111'),
('i5555555-0001-0001-0001-000000000003', 'IRRIG-EMITTER-001', 'Drip Emitters 4L/hr', 'منقطات 4 لتر/ساعة', 'IRRIGATION_SUPPLY', 'Drip Systems', 'PIECE', 1.0, 5000.0, 1000.0, 5000.0, 35.00, 55.00, 's4444444-4444-4444-4444-444444444444'),
('i5555555-0001-0001-0001-000000000004', 'IRRIG-SPRINK-001', 'Sprinkler Heads', 'رؤوس رشاشات', 'IRRIGATION_SUPPLY', 'Sprinkler Systems', 'PIECE', 1.0, 200.0, 50.0, 250.0, 450.00, 700.00, 's4444444-4444-4444-4444-444444444444');

-- ========================================
-- INSERT SAMPLE STOCK MOVEMENTS
-- ========================================

-- Stock in movements (purchases)
INSERT INTO stock_movements (item_id, movement_type, quantity, previous_qty, new_qty, unit_cost, total_cost, reference_type, notes)
VALUES
('i1111111-0001-0001-0001-000000000001', 'PURCHASE', 500.0, 0, 500.0, 350.00, 175000.00, 'purchase_order', 'Initial stock purchase'),
('i1111111-0001-0001-0001-000000000002', 'PURCHASE', 350.0, 0, 350.0, 300.00, 105000.00, 'purchase_order', 'Initial stock purchase'),
('i1111111-0001-0001-0001-000000000005', 'PURCHASE', 5000.0, 0, 5000.0, 8.00, 40000.00, 'purchase_order', 'Tomato seeds bulk purchase'),
('i2222222-0001-0001-0001-000000000001', 'PURCHASE', 200.0, 0, 200.0, 15000.00, 3000000.00, 'purchase_order', 'NPK fertilizer stock'),
('i2222222-0001-0001-0001-000000000002', 'PURCHASE', 350.0, 0, 350.0, 12000.00, 4200000.00, 'purchase_order', 'Urea fertilizer stock'),
('i3333333-0001-0001-0001-000000000001', 'PURCHASE', 150.0, 0, 150.0, 2800.00, 420000.00, 'purchase_order', 'Insecticide stock');

-- Update last_restocked
UPDATE inventory_items SET last_restocked = NOW() - INTERVAL '30 days' WHERE current_quantity > 0;

-- Verification queries
SELECT
    name_en,
    name_ar,
    category,
    unit,
    current_quantity,
    CONCAT(unit_cost, ' ', currency) as cost,
    (SELECT name FROM suppliers WHERE id = inventory_items.supplier_id) as supplier
FROM inventory_items
ORDER BY category, name_en;

SELECT
    category,
    COUNT(*) as item_count,
    SUM(current_quantity * unit_cost) as total_value_yer
FROM inventory_items
GROUP BY category
ORDER BY category;

SELECT
    s.name as supplier,
    s.governorate,
    COUNT(i.id) as items_supplied,
    s.rating,
    s.lead_time_days
FROM suppliers s
LEFT JOIN inventory_items i ON s.id = i.supplier_id
GROUP BY s.id, s.name, s.governorate, s.rating, s.lead_time_days
ORDER BY items_supplied DESC;
