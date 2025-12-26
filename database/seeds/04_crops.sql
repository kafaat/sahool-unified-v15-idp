-- SAHOOL Crops Catalog Seed Data
-- Yemen crop catalog with Arabic/English names, GDD, seasons, and prices

-- Clean existing data (optional - comment out for production)
-- TRUNCATE TABLE crop_catalog CASCADE;

-- Create crop catalog table if not exists
CREATE TABLE IF NOT EXISTS crop_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crop_code VARCHAR(50) UNIQUE NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200) NOT NULL,
    scientific_name VARCHAR(200),
    category VARCHAR(50) NOT NULL, -- cereals, legumes, vegetables, fruits, cash_crops
    subcategory VARCHAR(50),

    -- Growing Degree Days (GDD) requirements
    gdd_base_temp_c DECIMAL(5,2) DEFAULT 10.0,
    gdd_upper_temp_c DECIMAL(5,2) DEFAULT 30.0,
    gdd_total_required INTEGER, -- Total GDD needed from planting to harvest

    -- Growing season
    planting_season VARCHAR(100), -- e.g., "March-April, September-October"
    planting_months INTEGER[], -- Array of months [3,4,9,10]
    growing_days_min INTEGER, -- Minimum days to maturity
    growing_days_max INTEGER, -- Maximum days to maturity

    -- Price data (YER per kg)
    price_yer_per_kg_min DECIMAL(10,2),
    price_yer_per_kg_max DECIMAL(10,2),
    price_yer_per_kg_avg DECIMAL(10,2),

    -- Yield data (kg per hectare)
    yield_kg_per_ha_min DECIMAL(10,2),
    yield_kg_per_ha_max DECIMAL(10,2),
    yield_kg_per_ha_avg DECIMAL(10,2),

    -- Water requirements
    water_requirement VARCHAR(20), -- low, medium, high
    drought_tolerance VARCHAR(20), -- low, medium, high

    -- Suitable regions
    suitable_regions TEXT[], -- Array of Yemen regions
    optimal_altitude_min_m INTEGER,
    optimal_altitude_max_m INTEGER,

    -- Additional info
    description_en TEXT,
    description_ar TEXT,
    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- CEREALS (الحبوب)

INSERT INTO crop_catalog (
    crop_code, name_en, name_ar, scientific_name, category, subcategory,
    gdd_base_temp_c, gdd_total_required, growing_days_min, growing_days_max,
    planting_season, planting_months,
    price_yer_per_kg_min, price_yer_per_kg_max, price_yer_per_kg_avg,
    yield_kg_per_ha_min, yield_kg_per_ha_max, yield_kg_per_ha_avg,
    water_requirement, drought_tolerance,
    suitable_regions, optimal_altitude_min_m, optimal_altitude_max_m
) VALUES
('WHEAT-001', 'Wheat', 'قمح', 'Triticum aestivum', 'cereals', 'grains',
    0, 2000, 120, 150, 'October-November', ARRAY[10,11],
    300, 450, 375, 1500, 3500, 2500, 'medium', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 1500, 2500),

('BARLEY-001', 'Barley', 'شعير', 'Hordeum vulgare', 'cereals', 'grains',
    0, 1800, 90, 120, 'October-December', ARRAY[10,11,12],
    250, 400, 325, 1200, 3000, 2100, 'low', 'high',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار', 'حضرموت'], 1000, 2800),

('SORGHUM-001', 'Sorghum (Dhurra)', 'ذرة رفيعة', 'Sorghum bicolor', 'cereals', 'grains',
    10, 1600, 90, 130, 'April-May, August-September', ARRAY[4,5,8,9],
    280, 420, 350, 1500, 4000, 2750, 'low', 'high',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة', 'حضرموت'], 500, 2200),

('MILLET-001', 'Pearl Millet (Dukhn)', 'دخن', 'Pennisetum glaucum', 'cereals', 'grains',
    10, 1400, 75, 90, 'March-May', ARRAY[3,4,5],
    300, 500, 400, 800, 2500, 1650, 'low', 'very_high',
    ARRAY['الحديدة', 'حضرموت', 'صنعاء'], 0, 1800),

('CORN-001', 'Maize', 'ذرة شامية', 'Zea mays', 'cereals', 'grains',
    10, 1700, 90, 120, 'March-April, July-August', ARRAY[3,4,7,8],
    350, 550, 450, 2000, 6000, 4000, 'high', 'low',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة'], 800, 2000);

-- LEGUMES (البقوليات)

INSERT INTO crop_catalog (
    crop_code, name_en, name_ar, scientific_name, category, subcategory,
    gdd_base_temp_c, gdd_total_required, growing_days_min, growing_days_max,
    planting_season, planting_months,
    price_yer_per_kg_min, price_yer_per_kg_max, price_yer_per_kg_avg,
    yield_kg_per_ha_min, yield_kg_per_ha_max, yield_kg_per_ha_avg,
    water_requirement, drought_tolerance,
    suitable_regions, optimal_altitude_min_m, optimal_altitude_max_m
) VALUES
('LENTIL-001', 'Lentils', 'عدس', 'Lens culinaris', 'legumes', 'pulses',
    5, 1400, 100, 130, 'October-November', ARRAY[10,11],
    600, 900, 750, 800, 1800, 1300, 'low', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 1500, 2500),

('CHICKPEA-001', 'Chickpeas', 'حمص', 'Cicer arietinum', 'legumes', 'pulses',
    5, 1600, 110, 140, 'October-November', ARRAY[10,11],
    650, 950, 800, 900, 2000, 1450, 'low', 'high',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 1200, 2400),

('FABA-BEAN-001', 'Faba Beans (Ful)', 'فول', 'Vicia faba', 'legumes', 'pulses',
    5, 1500, 120, 180, 'September-November', ARRAY[9,10,11],
    500, 800, 650, 1500, 3500, 2500, 'medium', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 1000, 2300),

('COWPEA-001', 'Cowpea (Lubia)', 'لوبيا', 'Vigna unguiculata', 'legumes', 'pulses',
    10, 1300, 60, 90, 'March-May', ARRAY[3,4,5],
    450, 700, 575, 1000, 2500, 1750, 'medium', 'high',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة'], 500, 2000),

('PEANUT-001', 'Peanuts (Groundnut)', 'فول سوداني', 'Arachis hypogaea', 'legumes', 'oilseeds',
    12, 1800, 120, 150, 'March-April', ARRAY[3,4],
    700, 1100, 900, 1200, 3000, 2100, 'medium', 'medium',
    ARRAY['الحديدة', 'حضرموت', 'تعز'], 0, 1500);

-- VEGETABLES (الخضروات)

INSERT INTO crop_catalog (
    crop_code, name_en, name_ar, scientific_name, category, subcategory,
    gdd_base_temp_c, gdd_total_required, growing_days_min, growing_days_max,
    planting_season, planting_months,
    price_yer_per_kg_min, price_yer_per_kg_max, price_yer_per_kg_avg,
    yield_kg_per_ha_min, yield_kg_per_ha_max, yield_kg_per_ha_avg,
    water_requirement, drought_tolerance,
    suitable_regions, optimal_altitude_min_m, optimal_altitude_max_m
) VALUES
('TOMATO-001', 'Tomato', 'طماطم', 'Solanum lycopersicum', 'vegetables', 'fruiting',
    10, 1500, 90, 120, 'Year-round (varies by region)', ARRAY[1,2,3,4,5,6,7,8,9,10,11,12],
    250, 600, 425, 20000, 80000, 50000, 'high', 'low',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة', 'حضرموت'], 0, 2200),

('ONION-001', 'Onion', 'بصل', 'Allium cepa', 'vegetables', 'bulbs',
    6, 1200, 100, 150, 'September-November, February-March', ARRAY[2,3,9,10,11],
    200, 450, 325, 15000, 50000, 32500, 'medium', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة', 'حضرموت'], 0, 2400),

('POTATO-001', 'Potato', 'بطاطس', 'Solanum tuberosum', 'vegetables', 'tubers',
    7, 1400, 90, 120, 'February-March, August-September', ARRAY[2,3,8,9],
    180, 400, 290, 15000, 45000, 30000, 'high', 'low',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 1500, 2500),

('CARROT-001', 'Carrot', 'جزر', 'Daucus carota', 'vegetables', 'roots',
    7, 1100, 70, 100, 'September-February', ARRAY[9,10,11,12,1,2],
    220, 480, 350, 20000, 60000, 40000, 'medium', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 1000, 2400),

('CUCUMBER-001', 'Cucumber', 'خيار', 'Cucumis sativus', 'vegetables', 'fruiting',
    12, 1000, 50, 70, 'March-May, August-October', ARRAY[3,4,5,8,9,10],
    200, 500, 350, 15000, 50000, 32500, 'high', 'low',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة'], 0, 2000),

('EGGPLANT-001', 'Eggplant', 'باذنجان', 'Solanum melongena', 'vegetables', 'fruiting',
    12, 1400, 90, 120, 'March-May', ARRAY[3,4,5],
    250, 550, 400, 15000, 45000, 30000, 'medium', 'low',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة'], 0, 2000),

('PEPPER-001', 'Bell Pepper', 'فلفل حلو', 'Capsicum annuum', 'vegetables', 'fruiting',
    12, 1500, 90, 120, 'March-May', ARRAY[3,4,5],
    400, 800, 600, 15000, 40000, 27500, 'medium', 'low',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة'], 0, 2000),

('OKRA-001', 'Okra (Bamya)', 'بامية', 'Abelmoschus esculentus', 'vegetables', 'fruiting',
    15, 1200, 50, 70, 'March-June', ARRAY[3,4,5,6],
    300, 650, 475, 8000, 25000, 16500, 'medium', 'medium',
    ARRAY['الحديدة', 'تعز', 'صنعاء'], 0, 1800),

('SQUASH-001', 'Squash (Kousa)', 'كوسة', 'Cucurbita pepo', 'vegetables', 'fruiting',
    12, 900, 45, 60, 'March-May, August-October', ARRAY[3,4,5,8,9,10],
    220, 500, 360, 12000, 35000, 23500, 'medium', 'low',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة'], 0, 2000),

('LETTUCE-001', 'Lettuce', 'خس', 'Lactuca sativa', 'vegetables', 'leafy',
    5, 800, 50, 80, 'September-March', ARRAY[9,10,11,12,1,2,3],
    300, 700, 500, 15000, 40000, 27500, 'medium', 'low',
    ARRAY['صنعاء', 'تعز', 'إب'], 1000, 2400),

('CABBAGE-001', 'Cabbage', 'ملفوف', 'Brassica oleracea var. capitata', 'vegetables', 'leafy',
    5, 1200, 90, 120, 'September-November', ARRAY[9,10,11],
    180, 400, 290, 25000, 70000, 47500, 'medium', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 1200, 2400),

('SPINACH-001', 'Spinach', 'سبانخ', 'Spinacia oleracea', 'vegetables', 'leafy',
    5, 700, 40, 60, 'September-March', ARRAY[9,10,11,12,1,2,3],
    250, 600, 425, 10000, 30000, 20000, 'medium', 'low',
    ARRAY['صنعاء', 'تعز', 'إب'], 1000, 2400);

-- FRUITS (الفواكه)

INSERT INTO crop_catalog (
    crop_code, name_en, name_ar, scientific_name, category, subcategory,
    gdd_base_temp_c, gdd_total_required, growing_days_min, growing_days_max,
    planting_season, planting_months,
    price_yer_per_kg_min, price_yer_per_kg_max, price_yer_per_kg_avg,
    yield_kg_per_ha_min, yield_kg_per_ha_max, yield_kg_per_ha_avg,
    water_requirement, drought_tolerance,
    suitable_regions, optimal_altitude_min_m, optimal_altitude_max_m
) VALUES
('DATE-001', 'Date Palm', 'نخيل التمر', 'Phoenix dactylifera', 'fruits', 'tree_fruits',
    10, NULL, 1460, 1825, 'Year-round (perennial)', ARRAY[1,2,3,4,5,6,7,8,9,10,11,12],
    800, 2500, 1650, 4000, 12000, 8000, 'low', 'very_high',
    ARRAY['حضرموت', 'المهرة', 'شبوة', 'الحديدة'], 0, 1200),

('MANGO-001', 'Mango', 'مانجو', 'Mangifera indica', 'fruits', 'tree_fruits',
    15, NULL, 1460, 1825, 'Year-round (perennial)', ARRAY[1,2,3,4,5,6,7,8,9,10,11,12],
    600, 1800, 1200, 5000, 20000, 12500, 'medium', 'medium',
    ARRAY['الحديدة', 'حضرموت', 'تعز'], 0, 1000),

('BANANA-001', 'Banana', 'موز', 'Musa spp.', 'fruits', 'tree_fruits',
    14, NULL, 270, 365, 'Year-round (perennial)', ARRAY[1,2,3,4,5,6,7,8,9,10,11,12],
    400, 1000, 700, 15000, 50000, 32500, 'very_high', 'low',
    ARRAY['الحديدة', 'حضرموت', 'تعز'], 0, 800),

('GRAPE-001', 'Grape', 'عنب', 'Vitis vinifera', 'fruits', 'vine_fruits',
    10, 2800, 180, 240, 'February-March (perennial)', ARRAY[2,3],
    800, 2000, 1400, 8000, 25000, 16500, 'medium', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 1200, 2500),

('PAPAYA-001', 'Papaya', 'بابايا', 'Carica papaya', 'fruits', 'tree_fruits',
    15, NULL, 270, 365, 'Year-round', ARRAY[1,2,3,4,5,6,7,8,9,10,11,12],
    350, 900, 625, 20000, 60000, 40000, 'high', 'low',
    ARRAY['الحديدة', 'حضرموت', 'تعز'], 0, 800),

('CITRUS-ORANGE-001', 'Orange', 'برتقال', 'Citrus sinensis', 'fruits', 'citrus',
    12, NULL, 1095, 1460, 'February-March (perennial)', ARRAY[2,3],
    450, 1200, 825, 15000, 40000, 27500, 'medium', 'medium',
    ARRAY['الحديدة', 'تعز', 'صنعاء'], 200, 1500),

('CITRUS-LEMON-001', 'Lemon', 'ليمون', 'Citrus limon', 'fruits', 'citrus',
    12, NULL, 1095, 1460, 'Year-round (perennial)', ARRAY[1,2,3,4,5,6,7,8,9,10,11,12],
    400, 1100, 750, 12000, 35000, 23500, 'medium', 'medium',
    ARRAY['الحديدة', 'تعز', 'صنعاء'], 0, 1500),

('WATERMELON-001', 'Watermelon', 'بطيخ', 'Citrullus lanatus', 'fruits', 'melons',
    15, 1100, 80, 100, 'March-May', ARRAY[3,4,5],
    150, 400, 275, 20000, 60000, 40000, 'high', 'medium',
    ARRAY['الحديدة', 'حضرموت', 'تعز', 'صنعاء'], 0, 1500),

('MELON-001', 'Melon (Cantaloupe)', 'شمام', 'Cucumis melo', 'fruits', 'melons',
    15, 1000, 70, 90, 'March-May', ARRAY[3,4,5],
    200, 500, 350, 15000, 45000, 30000, 'high', 'medium',
    ARRAY['الحديدة', 'حضرموت', 'تعز'], 0, 1500),

('GUAVA-001', 'Guava', 'جوافة', 'Psidium guajava', 'fruits', 'tree_fruits',
    13, NULL, 1095, 1460, 'Year-round (perennial)', ARRAY[1,2,3,4,5,6,7,8,9,10,11,12],
    350, 900, 625, 10000, 30000, 20000, 'medium', 'medium',
    ARRAY['الحديدة', 'حضرموت', 'تعز'], 0, 1200),

('POMEGRANATE-001', 'Pomegranate', 'رمان', 'Punica granatum', 'fruits', 'tree_fruits',
    10, NULL, 180, 240, 'February-March (perennial)', ARRAY[2,3],
    700, 1800, 1250, 8000, 20000, 14000, 'low', 'high',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 800, 2200);

-- CASH CROPS (المحاصيل النقدية)

INSERT INTO crop_catalog (
    crop_code, name_en, name_ar, scientific_name, category, subcategory,
    gdd_base_temp_c, gdd_total_required, growing_days_min, growing_days_max,
    planting_season, planting_months,
    price_yer_per_kg_min, price_yer_per_kg_max, price_yer_per_kg_avg,
    yield_kg_per_ha_min, yield_kg_per_ha_max, yield_kg_per_ha_avg,
    water_requirement, drought_tolerance,
    suitable_regions, optimal_altitude_min_m, optimal_altitude_max_m
) VALUES
('COFFEE-ARABICA-001', 'Arabica Coffee', 'بن عربي', 'Coffea arabica', 'cash_crops', 'beverages',
    10, NULL, 1095, 1460, 'Year-round (perennial)', ARRAY[1,2,3,4,5,6,7,8,9,10,11,12],
    4000, 12000, 8000, 500, 2000, 1250, 'high', 'low',
    ARRAY['تعز', 'إب', 'صنعاء', 'الحديدة'], 1000, 2400),

('QAAT-001', 'Qat (Khat)', 'قات', 'Catha edulis', 'cash_crops', 'stimulants',
    10, NULL, 1460, 1825, 'Year-round (perennial)', ARRAY[1,2,3,4,5,6,7,8,9,10,11,12],
    1500, 5000, 3250, 2000, 8000, 5000, 'high', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 1200, 2800),

('COTTON-001', 'Cotton', 'قطن', 'Gossypium spp.', 'cash_crops', 'fibers',
    12, 2200, 150, 180, 'March-April', ARRAY[3,4],
    600, 1200, 900, 800, 2500, 1650, 'medium', 'medium',
    ARRAY['الحديدة', 'حضرموت', 'أبين'], 0, 1000),

('SESAME-001', 'Sesame', 'سمسم', 'Sesamum indicum', 'cash_crops', 'oilseeds',
    15, 1300, 90, 120, 'April-May', ARRAY[4,5],
    1200, 2500, 1850, 300, 800, 550, 'low', 'very_high',
    ARRAY['الحديدة', 'حضرموت', 'تعز'], 0, 1500),

('TOBACCO-001', 'Tobacco', 'تبغ', 'Nicotiana tabacum', 'cash_crops', 'stimulants',
    10, 1800, 90, 120, 'February-April', ARRAY[2,3,4],
    800, 2000, 1400, 1500, 3000, 2250, 'medium', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب'], 1000, 2200);

-- HERBS & SPICES (الأعشاب والتوابل)

INSERT INTO crop_catalog (
    crop_code, name_en, name_ar, scientific_name, category, subcategory,
    gdd_base_temp_c, gdd_total_required, growing_days_min, growing_days_max,
    planting_season, planting_months,
    price_yer_per_kg_min, price_yer_per_kg_max, price_yer_per_kg_avg,
    yield_kg_per_ha_min, yield_kg_per_ha_max, yield_kg_per_ha_avg,
    water_requirement, drought_tolerance,
    suitable_regions, optimal_altitude_min_m, optimal_altitude_max_m
) VALUES
('CORIANDER-001', 'Coriander', 'كزبرة', 'Coriandrum sativum', 'herbs_spices', 'herbs',
    7, 900, 40, 60, 'September-March', ARRAY[9,10,11,12,1,2,3],
    800, 2000, 1400, 800, 2000, 1400, 'low', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب'], 1000, 2400),

('CUMIN-001', 'Cumin', 'كمون', 'Cuminum cyminum', 'herbs_spices', 'spices',
    8, 1000, 100, 120, 'October-November', ARRAY[10,11],
    2000, 5000, 3500, 400, 800, 600, 'low', 'high',
    ARRAY['صنعاء', 'تعز', 'حضرموت'], 800, 2000),

('FENUGREEK-001', 'Fenugreek (Hilba)', 'حلبة', 'Trigonella foenum-graecum', 'herbs_spices', 'herbs',
    5, 900, 90, 120, 'October-November', ARRAY[10,11],
    1000, 2500, 1750, 800, 1800, 1300, 'low', 'high',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 1000, 2500),

('BASIL-001', 'Basil', 'ريحان', 'Ocimum basilicum', 'herbs_spices', 'herbs',
    10, 800, 60, 90, 'March-May', ARRAY[3,4,5],
    1500, 3500, 2500, 1000, 2500, 1750, 'medium', 'low',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة'], 0, 2000),

('MINT-001', 'Mint', 'نعناع', 'Mentha spp.', 'herbs_spices', 'herbs',
    5, 700, 60, 90, 'February-May, September-October', ARRAY[2,3,4,5,9,10],
    1200, 3000, 2100, 2000, 5000, 3500, 'high', 'low',
    ARRAY['صنعاء', 'تعز', 'إب'], 800, 2200),

('PARSLEY-001', 'Parsley', 'بقدونس', 'Petroselinum crispum', 'herbs_spices', 'herbs',
    5, 800, 70, 90, 'September-March', ARRAY[9,10,11,12,1,2,3],
    1000, 2500, 1750, 1500, 4000, 2750, 'medium', 'low',
    ARRAY['صنعاء', 'تعز', 'إب'], 1000, 2200);

-- FORAGE CROPS (محاصيل العلف)

INSERT INTO crop_catalog (
    crop_code, name_en, name_ar, scientific_name, category, subcategory,
    gdd_base_temp_c, gdd_total_required, growing_days_min, growing_days_max,
    planting_season, planting_months,
    price_yer_per_kg_min, price_yer_per_kg_max, price_yer_per_kg_avg,
    yield_kg_per_ha_min, yield_kg_per_ha_max, yield_kg_per_ha_avg,
    water_requirement, drought_tolerance,
    suitable_regions, optimal_altitude_min_m, optimal_altitude_max_m
) VALUES
('ALFALFA-001', 'Alfalfa (Lucerne)', 'برسيم حجازي', 'Medicago sativa', 'forage', 'perennial',
    5, NULL, 60, 90, 'September-November (perennial)', ARRAY[9,10,11],
    100, 250, 175, 8000, 25000, 16500, 'high', 'medium',
    ARRAY['صنعاء', 'تعز', 'إب', 'ذمار'], 800, 2400),

('CLOVER-001', 'Egyptian Clover (Berseem)', 'برسيم مصري', 'Trifolium alexandrinum', 'forage', 'annual',
    5, 900, 60, 90, 'September-November', ARRAY[9,10,11],
    80, 200, 140, 10000, 30000, 20000, 'high', 'low',
    ARRAY['صنعاء', 'تعز', 'إب', 'الحديدة'], 0, 2200),

('RHODES-GRASS-001', 'Rhodes Grass', 'حشيش رودس', 'Chloris gayana', 'forage', 'perennial',
    10, NULL, 60, 90, 'March-May (perennial)', ARRAY[3,4,5],
    70, 180, 125, 8000, 20000, 14000, 'medium', 'high',
    ARRAY['الحديدة', 'حضرموت', 'تعز'], 0, 1500);

-- Verification queries
SELECT
    category,
    COUNT(*) as crop_count,
    ROUND(AVG(price_yer_per_kg_avg)::numeric, 2) as avg_price,
    ROUND(AVG(yield_kg_per_ha_avg)::numeric, 2) as avg_yield
FROM crop_catalog
GROUP BY category
ORDER BY category;

SELECT
    name_en,
    name_ar,
    category,
    price_yer_per_kg_avg,
    yield_kg_per_ha_avg,
    water_requirement,
    drought_tolerance
FROM crop_catalog
ORDER BY category, name_en;
