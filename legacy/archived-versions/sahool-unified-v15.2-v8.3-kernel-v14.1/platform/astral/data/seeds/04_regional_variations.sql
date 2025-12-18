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
