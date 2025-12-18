-- Astral calendar seeds (kernel v14.1) loaded into default DB
-- NOTE: These are inserted into the current database; if you use per-service DBs, adapt accordingly.


-- ===== 01_stars.sql =====
-- SAHOOL Platform v14 - Seed Data
-- 01: النجوم الزراعية فقط
-- ✅ Idempotent: ON CONFLICT DO NOTHING

-- ============================================
-- النجوم الزراعية الـ 28
-- Reference: docs/calendar/ASSUMPTIONS.md
-- ============================================

INSERT INTO agricultural_stars (id, name_ar, name_en, order_in_year, start_day_of_year, duration_days, season, astronomical_mansion, mansions, weather_pattern, created_at) VALUES

-- فصل الشتاء (يبدأ من يناير)
('star_naaim', 'النعايم', 'Al-Naaim', 1, 1, 13, 'شتاء', 'النعايم', ARRAY['النعايم'], 'اشتداد البرد', NOW()),
('star_baldah', 'البلدة', 'Al-Baldah', 2, 14, 13, 'شتاء', 'البلدة', ARRAY['البلدة'], NULL, NOW()),
('star_saad_dhabih', 'سعد الذابح', 'Saad Al-Dhabih', 3, 27, 13, 'شتاء', 'سعد الذابح', ARRAY['سعد الذابح'], NULL, NOW()),
('star_saad_bula', 'سعد بلع', 'Saad Bula', 4, 40, 13, 'شتاء', 'سعد بلع', ARRAY['سعد بلع'], 'نهاية الشتاء', NOW()),

-- فصل الربيع
('star_saad_soud', 'سعد السعود', 'Saad Al-Soud', 5, 53, 13, 'ربيع', 'سعد السعود', ARRAY['سعد السعود'], 'بداية الدفء', NOW()),
('star_saad_akhbiyah', 'سعد الأخبية', 'Saad Al-Akhbiyah', 6, 66, 13, 'ربيع', 'سعد الأخبية', ARRAY['سعد الأخبية'], NULL, NOW()),
('star_fargh_muqaddam', 'الفرغ المقدم', 'Al-Fargh Muqaddam', 7, 79, 13, 'ربيع', 'الفرغ المقدم', ARRAY['الفرغ المقدم'], NULL, NOW()),
('star_fargh_muakhkhar', 'الفرغ المؤخر', 'Al-Fargh Muakhkhar', 8, 92, 13, 'ربيع', 'الفرغ المؤخر', ARRAY['الفرغ المؤخر'], NULL, NOW()),
('star_batn_hut', 'بطن الحوت', 'Batn Al-Hut', 9, 105, 13, 'ربيع', 'بطن الحوت', ARRAY['بطن الحوت'], NULL, NOW()),
('star_sharatan', 'الشرطان', 'Al-Sharatan', 10, 118, 13, 'ربيع', 'الشرطان', ARRAY['الشرطان'], 'اعتدال الجو', NOW()),
('star_butain', 'البطين', 'Al-Butain', 11, 131, 13, 'ربيع', 'البطين', ARRAY['البطين'], 'نهاية الربيع', NOW()),

-- فصل الصيف (القيظ)
('star_thuraya', 'الثريا', 'Pleiades', 12, 144, 13, 'صيف', 'الثريا', ARRAY['الثريا'], 'بدء الحر', NOW()),
('star_dabaran', 'الدبران', 'Aldebaran', 13, 157, 13, 'صيف', 'الدبران', ARRAY['الدبران'], NULL, NOW()),
('star_haqaa', 'الهقعة', 'Al-Haqaa', 14, 170, 13, 'صيف', 'الهقعة', ARRAY['الهقعة'], 'ذروة القيظ', NOW()),
('star_hanaa', 'الهنعة', 'Al-Hanaa', 15, 183, 13, 'صيف', 'الهنعة', ARRAY['الهنعة'], NULL, NOW()),
('star_dhiraa', 'الذراع', 'Al-Dhiraa', 16, 196, 13, 'صيف', 'الذراع', ARRAY['الذراع'], NULL, NOW()),

-- فصل الخريف
('star_alab', 'العلب', 'Al-Alab', 17, 197, 13, 'خريف', 'الذراع', ARRAY['الذراع'], 'بداية موسم الأمطار', NOW()),
('star_nathra', 'النثرة', 'Al-Nathra', 18, 210, 13, 'خريف', 'النثرة', ARRAY['النثرة'], NULL, NOW()),
('star_tarfa', 'الطرفة', 'Al-Tarfa', 19, 223, 13, 'خريف', 'الطرفة', ARRAY['الطرفة'], NULL, NOW()),
('star_suhail', 'سهيل', 'Suhail/Canopus', 20, 236, 52, 'خريف', 'الزبرة', ARRAY['الزبرة', 'الجبهة', 'الطرفة', 'الصرفة'], 'ذروة موسم الأمطار - أربعة روابع', NOW()),
('star_ghafr', 'الغفر', 'Al-Ghafr', 21, 288, 13, 'خريف', 'الغفر', ARRAY['الغفr'], NULL, NOW()),
('star_zubanaa', 'الزبانا', 'Al-Zubanaa', 22, 301, 13, 'خريف', 'الزبانا', ARRAY['الزبانا'], 'نهاية الخريف', NOW()),

-- العودة للشتاء (نهاية السنة)
('star_iklil', 'الإكليل', 'Al-Iklil', 23, 314, 13, 'شتاء', 'الإكليل', ARRAY['الإكليل'], 'بداية البرد', NOW()),
('star_qalb', 'القلب', 'Qalb/Antares', 24, 327, 13, 'شتاء', 'القلب', ARRAY['القلب'], 'أطول ليلة في السنة', NOW()),
('star_shawla', 'الشولة', 'Al-Shawla', 25, 340, 13, 'شتاء', 'الشولة', ARRAY['الشولة'], NULL, NOW()),
('star_naaim_end', 'النعايم الثانية', 'Al-Naaim End', 26, 353, 13, 'شتاء', 'النعايم', ARRAY['النعايم'], 'نهاية السنة', NOW())

ON CONFLICT (id) DO NOTHING;



-- ===== 02_proverbs.sql =====
-- SAHOOL Platform v14 - Seed Data
-- 02: الأمثال الشعبية
-- ✅ Idempotent: ON CONFLICT DO NOTHING

INSERT INTO folk_proverbs (id, text, meaning, star_id, crop_types, regions, action_type, reliability_score, created_at) VALUES

-- أمثال العلب (أهم النجوم زراعياً)
('prv_alab_001', 
 'ما قيظ إلا قيظ العلب؛ لا ظمأ قبله ولا روى بعده', 
 'الذرة تتحمل العطش في كل النجوم إلا العلب، فإن لم تمطر فيه هلك الزرع', 
 'star_alab', 
 ARRAY['ذرة', 'ذرة رفيعة'], 
 ARRAY['المرتفعات', 'تهامة'], 
 'ري', 
 0.90, NOW()),

('prv_alab_002', 
 'العلب نهر الخريف وعموده', 
 'نجم العلب هو أهم فترة لسقوط أمطار الخريف', 
 'star_alab', 
 ARRAY[]::text[], 
 ARRAY['المرتفعات'], 
 'عام', 
 0.85, NOW()),

('prv_alab_003', 
 'ثورك والعلب', 
 'وقت حرث الجنيد (بين أتلام الزرع) يكون في نجم العلب', 
 'star_alab', 
 ARRAY['ذرة'], 
 ARRAY['المرتفعات'], 
 'حرث', 
 0.80, NOW()),

('prv_alab_004', 
 'ياتلمة الزين لا قالوا خلب؛ ينتلم بالرمح ويظهر بالعلب', 
 'أفضل وقت لبذر البر والشعير هو نجم الرمح ليظهر في العلب', 
 'star_alab', 
 ARRAY['بر', 'شعير'], 
 ARRAY['المرتفعات'], 
 'بذر', 
 0.85, NOW()),

('prv_alab_005', 
 'لف القرط؛ لقيظ العلب', 
 'احتفظ ببقايا علف المواشي لأنك ستحتاجها في العلب', 
 'star_alab', 
 ARRAY['علف'], 
 ARRAY['المرتفعات', 'تهامة'], 
 'تخزين', 
 0.75, NOW()),

-- أمثال سهيل
('prv_suhail_001', 
 'ما في النجوم إلا سهيل؛ في ليلته سبعين سيل', 
 'نجم سهيل يأتي معه أمطار غزيرة جداً', 
 'star_suhail', 
 ARRAY[]::text[], 
 ARRAY['المرتفعات', 'تهامة', 'حضرموت'], 
 'عام', 
 0.90, NOW()),

('prv_suhail_002', 
 'طلع سهيل وبرد الليل', 
 'عند طلوع سهيل يبدأ برد الليل', 
 'star_suhail', 
 ARRAY[]::text[], 
 ARRAY['المرتفعات'], 
 'عام', 
 0.85, NOW()),

('prv_suhail_003', 
 'إذا طلع سهيل رفع كيل ووضع كيل', 
 'عند طلوع سهيل ينتهي محصول ويبدأ محصول آخر', 
 'star_suhail', 
 ARRAY[]::text[], 
 ARRAY['المرتفعات', 'تهامة'], 
 'حصاد', 
 0.80, NOW()),

-- أمثال الثريا
('prv_thuraya_001', 
 'إذا طلعت الثريا لا تأمن السيل والبريا', 
 'عند طلوع الثريا توقع الأمطار والسيول', 
 'star_thuraya', 
 ARRAY[]::text[], 
 ARRAY['تهامة'], 
 'تحذير', 
 0.70, NOW()),

('prv_thuraya_002', 
 'الثريا غرست الحريا', 
 'في الثريا تُغرس أشجار الحريا', 
 'star_thuraya', 
 ARRAY['أشجار'], 
 ARRAY['تهامة'], 
 'غرس', 
 0.75, NOW()),

-- أمثال سعد السعود
('prv_saad_001', 
 'سعد السعود تفتح فيه العود', 
 'في سعد السعود تبدأ الأشجار في الإزهار', 
 'star_saad_soud', 
 ARRAY['أشجار'], 
 ARRAY['المرتفعات'], 
 'عام', 
 0.80, NOW()),

('prv_saad_002', 
 'سعد السعود تدب فيه المياه في العود', 
 'في سعد السعود تبدأ الحياة في الأشجار', 
 'star_saad_soud', 
 ARRAY['أشجار'], 
 ARRAY['المرتفعات', 'تهامة'], 
 'عام', 
 0.85, NOW()),

-- أمثال القلب
('prv_qalb_001', 
 'إذا طلع القلب جاء الشتاء بلا ريب', 
 'طلوع القلب علامة دخول الشتاء', 
 'star_qalb', 
 ARRAY[]::text[], 
 ARRAY['المرتفعات', 'تهامة'], 
 'عام', 
 0.85, NOW()),

-- أمثال النثرة
('prv_nathra_001', 
 'إذا طلعت النثرة شدد السقيا', 
 'في النثرة يجب زيادة الري', 
 'star_nathra', 
 ARRAY[]::text[], 
 ARRAY['المرتفعات'], 
 'ري', 
 0.75, NOW()),

-- أمثال الشرطان
('prv_sharatan_001', 
 'الشرطان يشرط الماء شرط', 
 'في الشرطان تقل المياه ويجب ترشيدها', 
 'star_sharatan', 
 ARRAY[]::text[], 
 ARRAY['المرتفعات'], 
 'ري', 
 0.70, NOW())

ON CONFLICT (id) DO NOTHING;



-- ===== 03_planting_rules.sql =====
-- SAHOOL Platform v14 - Seed Data
-- 03: قواعد الزراعة
-- ✅ Idempotent: ON CONFLICT DO NOTHING

INSERT INTO planting_rules (id, star_id, crop_type, growth_stage, action, condition, related_proverb, source, priority, created_at) VALUES

-- قواعد العلب
('rule_alab_001', 'star_alab', 'بر', NULL, 'بذر', 'إذا سالت الأرض من الأمطار', 'ياتلمة الزين لا قالوا خلب', 'تراث', 1, NOW()),
('rule_alab_002', 'star_alab', 'شعير', NULL, 'بذر', 'إذا سالت الأرض من الأمطار', NULL, 'تراث', 1, NOW()),
('rule_alab_003', 'star_alab', 'ذرة', 'نمو خضري', 'حرث الجنيد', NULL, 'ثورك والعلب', 'تراث', 1, NOW()),
('rule_alab_004', 'star_alab', 'ذرة', NULL, 'مراقبة الري', 'تأكد من توفر الماء الكافي', 'ما قيظ إلا قيظ العلب', 'تراث', 1, NOW()),
('rule_alab_005', 'star_alab', 'علف', NULL, 'تخزين', 'احتفظ ببقايا العلف', 'لف القرط لقيظ العلب', 'تراث', 2, NOW()),

-- قواعد سهيل
('rule_suhail_001', 'star_suhail', 'ذرة', NULL, 'مراقبة السيول', 'توقع أمطار غزيرة', 'ما في النجوم إلا سهيل', 'تراث', 1, NOW()),
('rule_suhail_002', 'star_suhail', 'جميع المحاصيل', NULL, 'تصريف المياه', 'تأكد من عدم تجمع المياه', NULL, 'علمي', 1, NOW()),
('rule_suhail_003', 'star_suhail', 'ذرة', 'إثمار', 'حصاد مبكر', 'إذا كان المحصول جاهزاً قبل الأمطار', 'رفع كيل ووضع كيل', 'تراث', 2, NOW()),

-- قواعد الثريا
('rule_thuraya_001', 'star_thuraya', 'أشجار', NULL, 'غرس', NULL, 'الثريا غرست الحريا', 'تراث', 2, NOW()),
('rule_thuraya_002', 'star_thuraya', 'جميع المحاصيل', NULL, 'تحضير للحر', 'توفير الظل والماء الكافي', NULL, 'علمي', 1, NOW()),

-- قواعد سعد السعود
('rule_saad_001', 'star_saad_soud', 'خضروات', NULL, 'بذر', 'بداية موسم الزراعة الربيعية', NULL, 'علمي', 1, NOW()),
('rule_saad_002', 'star_saad_soud', 'أشجار', NULL, 'تقليم', 'قبل بدء النمو الجديد', 'سعد السعود تفتح فيه العود', 'مدمج', 1, NOW()),
('rule_saad_003', 'star_saad_soud', 'فواكه', NULL, 'تسميد', 'دعم النمو الجديد', NULL, 'علمي', 2, NOW()),

-- قواعد النثرة
('rule_nathra_001', 'star_nathra', 'جميع المحاصيل', NULL, 'زيادة الري', 'بسبب الحرارة العالية', 'إذا طلعت النثرة شدد السقيا', 'تراث', 1, NOW()),

-- قواعد القلب
('rule_qalb_001', 'star_qalb', 'محاصيل شتوية', NULL, 'بذر', 'بداية موسم الزراعة الشتوية', NULL, 'علمي', 1, NOW()),
('rule_qalb_002', 'star_qalb', 'جميع المحاصيل', NULL, 'حماية من البرد', 'توقع انخفاض درجات الحرارة', 'إذا طلع القلب جاء الشتاء', 'مدمج', 1, NOW()),

-- قواعد الشرطان
('rule_sharatan_001', 'star_sharatan', 'جميع المحاصيل', NULL, 'ترشيد الري', 'المياه تقل في هذه الفترة', 'الشرطان يشرط الماء شرط', 'تراث', 1, NOW()),

-- قواعد البطين
('rule_butain_001', 'star_butain', 'خضروات صيفية', NULL, 'بذر', 'تحضير لموسم الصيف', NULL, 'علمي', 1, NOW()),

-- قواعد الهقعة
('rule_haqaa_001', 'star_haqaa', 'جميع المحاصيل', NULL, 'ري صباحي فقط', 'تجنب الري في الظهيرة', NULL, 'علمي', 1, NOW()),
('rule_haqaa_002', 'star_haqaa', 'خضروات', NULL, 'تظليل', 'حماية من الحرارة الشديدة', NULL, 'علمي', 1, NOW())

ON CONFLICT (id) DO NOTHING;



-- ===== 04_regional_variations.sql =====
-- SAHOOL Platform v14 - Seed Data
-- 04: الاختلافات الإقليمية
-- ✅ Idempotent: ON CONFLICT DO NOTHING
-- Reference: docs/calendar/ASSUMPTIONS.md

INSERT INTO star_regional_variations (id, star_id, region, calendar_type, offset_days, local_name, created_at) VALUES

-- تهامة (الواسعي) - offset: -4 days
('var_alab_tihama', 'star_alab', 'تهامة', 'الواسعي', -4, NULL, NOW()),
('var_suhail_tihama', 'star_suhail', 'تهامة', 'الواسعي', -4, NULL, NOW()),
('var_thuraya_tihama', 'star_thuraya', 'تهامة', 'الواسعي', -4, NULL, NOW()),
('var_saad_tihama', 'star_saad_soud', 'تهامة', 'الواسعي', -4, NULL, NOW()),
('var_qalb_tihama', 'star_qalb', 'تهامة', 'الواسعي', -4, NULL, NOW()),
('var_nathra_tihama', 'star_nathra', 'تهامة', 'الواسعي', -4, NULL, NOW()),

-- حضرموت (تقويم خاص) - offset: +3 days
('var_alab_hadramout', 'star_alab', 'حضرموت', 'خاص', 3, NULL, NOW()),
('var_suhail_hadramout', 'star_suhail', 'حضرموت', 'خاص', 3, NULL, NOW()),
('var_thuraya_hadramout', 'star_thuraya', 'حضرموت', 'خاص', 3, NULL, NOW()),
('var_saad_hadramout', 'star_saad_soud', 'حضرموت', 'خاص', 3, NULL, NOW()),
('var_qalb_hadramout', 'star_qalb', 'حضرموت', 'خاص', 3, NULL, NOW()),

-- المرتفعات (العنسي - المرجع) - offset: 0
('var_alab_highlands', 'star_alab', 'المرتفعات', 'العنسي', 0, NULL, NOW()),
('var_suhail_highlands', 'star_suhail', 'المرتفعات', 'العنسي', 0, NULL, NOW()),
('var_thuraya_highlands', 'star_thuraya', 'المرتفعات', 'العنسي', 0, NULL, NOW()),
('var_saad_highlands', 'star_saad_soud', 'المرتفعات', 'العنسي', 0, NULL, NOW()),
('var_qalb_highlands', 'star_qalb', 'المرتفعات', 'العنسي', 0, NULL, NOW())

ON CONFLICT (id) DO NOTHING;

