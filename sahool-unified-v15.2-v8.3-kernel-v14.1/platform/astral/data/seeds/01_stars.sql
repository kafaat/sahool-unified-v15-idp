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
