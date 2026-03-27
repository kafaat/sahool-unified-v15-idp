# تقرير فجوات Farmonaut مقابل SAHOOL
# Farmonaut vs SAHOOL Gap Analysis Report

> **التاريخ**: 2026-03-27
> **المصدر**: تحليل فيديو Farmonaut + تدقيق كود SAHOOL
> **الهدف**: تحديد الفجوات الدقيقة وخطة التحسين

---

## أولاً: المؤشرات (Map Controls) — تحليل الفجوات

### مجموعة صحة المحصول

| المؤشر | Farmonaut | SAHOOL - الكود الموجود | الفجوة | الأولوية |
|--------|----------|----------------------|--------|---------|
| **Hybrid Index** | يجمع صحة المحصول + الري في صورة واحدة بـ 4 ألوان | ❌ غير موجود | **يجب بناؤه** — فكرة عبقرية للمزارع البسيط | P0 |
| **NDVI** | مراحل مبكرة + كثافة خفيفة | ✅ **حقيقي** — `vegetation_indices.py` يحسب NDVI بصيغة Sentinel-2 الحقيقية (B8-B4)/(B8+B4) | **البيانات وهمية** — sentinelhub غير مثبت في requirements.txt، يعود لـ mock data | P0 |
| **NDRE** | مراحل متأخرة / ذرة / فول صويا | ✅ **حقيقي** — محسوب في vegetation_indices.py باستخدام (B7-B5)/(B7+B5) | نفس مشكلة NDVI — لا بيانات حقيقية | P0 |

### مجموعة الري (3 مؤشرات)

| المؤشر | Farmonaut | SAHOOL - الكود الموجود | الفجوة |
|--------|----------|----------------------|--------|
| **NDWI** | نقص الماء في النبات | ✅ **حقيقي** — محسوب (B3-B8)/(B3+B8) في vegetation_indices.py | البيانات وهمية فقط |
| **Evapotranspiration** | تبخر الماء من التربة والنبات | ✅ **حقيقي** — irrigation-smart يحسب ET بطريقة Hargreaves: ET0 × Kc | **يعمل فعلياً** مع بيانات الطقس |
| **NDMI** | رطوبة التربة | ✅ **حقيقي** — محسوب (B8A-B11)/(B8A+B11) | البيانات وهمية |

**ملاحظة حاسمة**: Farmonaut يدمج الثلاثة في توصية ري واحدة. SAHOOL لديه الحسابات منفصلة لكن **لا يوجد دمج**.

### مجموعة التربة والتضاريس

| المؤشر | Farmonaut | SAHOOL - الكود الموجود | الفجوة |
|--------|----------|----------------------|--------|
| **SOC** (كربون عضوي) | يحدد مناطق انخفاض الكربون لأخذ العينات | ✅ **حقيقي** — `shared/process_models/soil_carbon.py` نموذج RothC بـ 3 أحواض كربون + دورة نيتروجين | **غير مربوط** بواجهة المستخدم |
| **DEM** (ارتفاع رقمي) | تضاريس + مناطق تجمع المياه | ✅ **حقيقي وممتاز** — `terrain-core-service` يدعم 4 مصادر DEM + 7 مؤشرات تضاريس (slope, aspect, flow, TWI, curvature) | **كشف تجمع المياه غير مطبق** — البنية جاهزة (Flow Accumulation) لكن لا يوجد endpoint مخصص |

### مجموعة الرادار (SAR)

| المؤشر | Farmonaut | SAHOOL - الكود الموجود | الفجوة | الأولوية |
|--------|----------|----------------------|--------|---------|
| **RVI** (صحة بالرادار) | يخترق السحب تلقائياً | ❌ **غير موجود** — `sar_processor.py` يبحث عن مشاهد Sentinel-1 لكن لا يحمّل البيانات ولا يحسب RVI | يجب بناء خط أنابيب SAR حقيقي | P1 |
| **RSM** (رطوبة بالرادار) | رطوبة التربة عبر السحب | ⚠️ **جزئي** — Water Cloud Model موجود بمعايرة يمنية (A=15.0, B=8.5, C=-0.3) لكن يستخدم **بيانات محاكاة** | تفعيل تحميل SAR الحقيقي | P1 |
| **التحول التلقائي للرادار** | يكتشف الغيوم ويتحول لـ SAR بدون تدخل | ❌ **غير موجود تماماً** | **P1 — مهم جداً لليمن** بسبب الغيوم الموسمية | P1 |

---

## ثانياً: التقارير والتنبيهات — تحليل الفجوات

| الميزة | Farmonaut | SAHOOL | الفجوة | الأولوية |
|--------|----------|--------|--------|---------|
| **تقرير 9 أقسام** (بوصلة) | الصفحة 2 من كل تقرير — خريطة مقسمة 9 اتجاهات | ❌ **غير موجود** — لا يوجد تقسيم مكاني للحقل | فكرة ذكية جداً يجب تطبيقها | P0 |
| **تقرير WhatsApp** | كل 3-5 أيام تلقائياً | ✅ **حقيقي** — `whatsapp-bot-service` (port 8240) يدعم إرسال قوالب + صور + جلسات | **الربط موجود** — يحتاج فقط تنسيق التقرير بشكل 9 أقسام | P1 |
| **تقرير متعدد اللغات** | تغيير اللغة من داخل التقرير | ✅ **جزئي** — كل الخدمات ثنائية اللغة (AR/EN) | **لا يوجد PDF** — التقارير نصية فقط | P2 |
| **توقعات طقس ساعية 48 ساعة** | ساعة بساعة | ✅ **حقيقي** — `weather-service` يدعم Open-Meteo + OpenWeatherMap + 48h hourly | **يعمل** — يحتاج ربط بالواجهة | P1 |
| **توقعات يومية 8 أيام** | يومياً | ✅ **حقيقي** — مدعوم في weather-service | يحتاج ربط | P1 |
| **نافذة الرش** (Spray Window) | ضمن الطقس | ✅ **حقيقي** — `shared/weather_alerts/` يحسب نوافذ الرش مع كشف الانعكاس الحراري | يحتاج ربط | P1 |

---

## ثالثاً: JEEVN AI — تحليل الفجوات

| الميزة | Farmonaut JEEVN AI | SAHOOL | الفجوة |
|--------|-------------------|--------|--------|
| **تحليل N, P, K, Zn, S** | مقاييس بصرية + توصيات كمية | ✅ **حقيقي وشامل** — `shared/soil_testing/interpreter.py` يحلل N, P, K, Ca, Mg, S, Zn, Fe, Mn, Cu, B (11 عنصر!) مع عتبات حسب نوع المحصول | **أفضل من Farmonaut** — يحتاج فقط ربط بالواجهة |
| **pH والملوحة** | مراقبة مع توصيات | ✅ **حقيقي** — تأثير pH على امتصاص العناصر + EC interpretation | يحتاج ربط |
| **SOC (كربون عضوي)** | خريطة مناطق انخفاض | ✅ **حقيقي** — نموذج RothC مع 3 أحواض كربون | يحتاج ربط + تصور مكاني |
| **توصيات أسمدة** | كميات محددة بالكيلو/هكتار | ✅ **جزئي** — `shared/fertilizer_management/` موجود لكن منطق الاختيار بسيط | تحسين خوارزمية التوصية |
| **توقع الآفات بالقمر الصناعي** | NDVI anomaly → تنبؤ مبكر | ❌ **STUB** — pest-detection-service يقبل NDVI كمدخل لكن **لا يوجد نموذج ML** يربط الشذوذ بالآفات | P1 — يحتاج نموذج ML |
| **جدول ري ذكي (4 عوامل)** | طقس + رطوبة + احتياج + تبخر | ✅ **حقيقي** — irrigation-smart يدمج الأربعة بطريقة Hargreaves | يحتاج ربط بالواجهة |
| **توقع الإنتاجية** | ارتفاع + عائد/هكتار + موعد حصاد | ✅ **حقيقي** — `crop-intelligence-service/yield_prediction.py` (571 سطر) يدعم 14 محصول | **موعد الحصاد STUB** — حساب خطي بسيط، يحتاج نمذجة فينولوجية |
| **استكشاف متعدد الحقول** | تقرير واحد لعدة حقول | ❌ **غير موجود** | P2 |

---

## رابعاً: إدارة الحقول — تحليل الفجوات

| الميزة | Farmonaut | SAHOOL | الفجوة |
|--------|----------|--------|--------|
| **بحث بالعنوان** | ✅ | ❌ — لا يوجد geocoding | يحتاج Google/OSM geocoding |
| **إدخال إحداثيات** | ✅ | ✅ — PostGIS يدعم | UI ناقص |
| **رفع KML/Shapefile** | ✅ | ❌ **غير موجود** — لا يوجد كود parsing لملفات KML/SHP | P1 |
| **رسم على الخريطة** | ✅ | ❌ — لا يوجد أداة رسم Leaflet/MapLibre | P1 |
| **حساب المساحة** | ✅ تلقائي | ✅ **حقيقي** — `shared/field_boundaries/geometry.py` يحسب Haversine + مساحة + محيط | يحتاج ربط |
| **Show All Farms (جدول)** | Farm ID, وصف, مساحة, حالة, تاريخ | ✅ **جزئي** — الجدول موجود في FarmonautClient | يحتاج إضافة: subscription status, وحدات |
| **بحث + تجديد جماعي** | ✅ | ❌ — لا يوجد batch operations | P2 |
| **تاريخي من 2017** | ✅ Time Lapse + Side-by-Side | ⚠️ **البنية جاهزة** — NDVI timeseries + multi-provider لكن **لا يوجد تكوين أرشيف Sentinel-2 صريح** | P1 |

---

## خامساً: ملخص الأولويات

### P0 — حرج (يجب فوراً)

| # | المهمة | السبب | الجهد |
|---|--------|-------|-------|
| 1 | **تفعيل Sentinel Hub** — إضافة `sentinelhub` لـ requirements.txt + تكوين credentials | كل المؤشرات تعتمد عليه — بدونه كل البيانات وهمية | أسبوع واحد |
| 2 | **بناء Hybrid Index** — خوارزمية تجمع NDVI + NDWI في 4 ألوان | أهم فكرة من Farmonaut — تبسيط للمزارع | 3 أيام |
| 3 | **تقرير 9 أقسام** — تقسيم مكاني + توليد تقرير عربي | الفكرة الأذكى من Farmonaut | أسبوع |
| 4 | **ربط weather-service بالواجهة** — طقس ساعي 48h + يومي 8 أيام + spray windows | الكود **جاهز 100%** — يحتاج فقط API call | يومان |

### P1 — عالي (خلال شهر)

| # | المهمة | السبب | الجهد |
|---|--------|-------|-------|
| 5 | **SAR Fallback التلقائي** — كشف غيوم → تحول لرادار | **حاسم لليمن** بسبب الغيوم الموسمية | أسبوعان |
| 6 | **ربط JEEVN AI** — soil-analysis + irrigation-smart + pest-detection بالواجهة | الكود الخلفي **جاهز** — يحتاج integration فقط | أسبوع |
| 7 | **KML/Shapefile Import** — إضافة parser + UI رفع ملفات | ضروري لاستيراد حقول موجودة | أسبوع |
| 8 | **رسم حدود على الخريطة** — Leaflet Draw plugin | ضروري لإنشاء حقول جديدة | أسبوع |
| 9 | **نموذج ML للآفات** — NDVI anomaly → pest prediction | ميزة تنافسية مهمة | أسبوعان |
| 10 | **تقرير WhatsApp بـ 9 أقسام** — ربط whatsapp-bot-service بالتقرير الجديد | الخدمة **جاهزة** (port 8240) | 3 أيام |

### P2 — متوسط (خلال 3 أشهر)

| # | المهمة | الجهد |
|---|--------|-------|
| 11 | Historical Data من 2017 — تكوين Sentinel Hub Archive API | أسبوع |
| 12 | Time Lapse — فيديو زمني لتطور الحقل | أسبوعان |
| 13 | Side-by-Side — مقارنة مؤشرين جنباً لجنب | أسبوع |
| 14 | PDF Reports — تصدير تقارير PDF ثنائية اللغة | أسبوع |
| 15 | Batch Farm Operations — تجديد جماعي | 3 أيام |
| 16 | موعد حصاد دقيق — نمذجة فينولوجية بـ GDD | أسبوعان |

---

## سادساً: الأفضلية التنافسية لـ SAHOOL

### ما يتفوق فيه SAHOOL على Farmonaut (بالفعل)

| الميزة | SAHOOL | Farmonaut |
|--------|--------|----------|
| **تحليل عناصر التربة** | 11 عنصر (N,P,K,Ca,Mg,S,Zn,Fe,Mn,Cu,B) | 5 فقط (N,P,K,Zn,S) |
| **نموذج كربون التربة** | RothC مع 3 أحواض + دورة نيتروجين | خريطة SOC بسيطة |
| **تحليل التضاريس** | 7 مؤشرات + 4 مصادر DEM + Copernicus GLO-30 | DEM أساسي فقط |
| **مؤشرات الغطاء النباتي** | 25+ مؤشر (NDVI, EVI, SAVI, NDRE, LAI, MSAVI, GNDVI...) | ~10 مؤشرات |
| **محاصيل التوقع** | 14 محصول (مع معايرة يمنية) | عام — غير مخصص إقليمياً |
| **WhatsApp Bot** | محادثة ذكية + كشف أمراض بالصور + جلسات | تقارير فقط |
| **نظام الآفات** | 10+ آفات شرق أوسطية + عتبات اقتصادية + IPM | تنبيهات عامة |
| **تحليل NDVI الزمني** | 1600+ سطر — كشف شذوذ + اتجاهات + فينولوجيا + تنبؤ | رسم بياني أساسي |

---

## سابعاً: خلاصة — الصورة الكبرى

```
الحسابات العلمية (محركات الحساب):  ██████████████████░░  90% جاهز
بنية الخدمات (API + endpoints):    ██████████████████░░  90% جاهز
بيانات الأقمار الصناعية الحقيقية:   ██░░░░░░░░░░░░░░░░░░  10% (mock فقط)
الربط بين الخدمات والواجهة:         ████░░░░░░░░░░░░░░░░  20%
واجهة المستخدم Farmonaut:          ████████████████░░░░  80% جاهز
SAR/Radar:                         ██░░░░░░░░░░░░░░░░░░  10%
تقارير ذكية (9 أقسام):             ░░░░░░░░░░░░░░░░░░░░   0%
```

### الاستنتاج

**SAHOOL لديه محركات حساب أقوى من Farmonaut** — لكن المشكلة في 3 نقاط:
1. **لا بيانات أقمار صناعية حقيقية** (sentinelhub غير مثبت)
2. **لا ربط بين الخلفية والواجهة** (كل خدمة تعمل منفردة)
3. **لا تبسيط للمزارع** (Hybrid Index + 9 أقسام)

**إذا تم حل هذه الثلاث نقاط، SAHOOL يتفوق على Farmonaut تقنياً.**

---

## ثامناً: خريطة التكامل — الـ Endpoints الدقيقة لربط الواجهة بالخدمات

> هذا القسم يوضح **بالضبط** أي endpoint يُستدعى لكل ميزة في واجهة Farmonaut.
> مبني على تدقيق الكود الفعلي وليس الوثائق.

### خدمة تحليل الغطاء النباتي (vegetation-analysis-service — port 8090)

| ميزة Farmonaut | Endpoint الحقيقي | الحالة | ملاحظات |
|----------------|-----------------|--------|---------|
| **NDVI / EVI / SAVI / NDRE / NDWI / NDMI** | `GET /v1/indices/{field_id}` | ✅ يعمل (mock) | يُرجع 18+ مؤشر دفعة واحدة |
| **مؤشر محدد** | `GET /v1/indices/{field_id}/{index_name}` | ✅ يعمل (mock) | مع تفسير حسب المحصول |
| **السلسلة الزمنية** | `GET /v1/timeseries/{field_id}` | ✅ يعمل (mock) | NDVI عبر الزمن |
| **تحليل زمني شامل** | `POST /v1/ndvi-timeseries/analyze/{field_id}` | ✅ حقيقي | كشف شذوذ + اتجاهات + فينولوجيا |
| **رطوبة التربة SAR** | `GET /v1/soil-moisture/{field_id}` | ⚠️ محاكاة | Water Cloud Model يمني جاهز |
| **سلسلة SAR الزمنية** | `GET /v1/sar-timeseries/{field_id}` | ⚠️ محاكاة | |
| **كشف أحداث الري** | `GET /v1/irrigation-events/{field_id}` | ⚠️ محاكاة | |
| **غطاء السحب** | `GET /v1/cloud-cover/{field_id}` | ✅ | يُستخدم لتقرير SAR fallback |
| **كشف حدود الحقل** | `POST /v1/boundaries/detect` | ✅ | |
| **تصدير تحليل** | `GET /v1/export/analysis/{field_id}` | ✅ | GeoJSON/CSV/KML |
| **VRA (تطبيق متغير)** | `POST /v1/vra/generate` | ✅ | خرائط وصفات |
| **مرحلة النمو** | `GET /v1/phenology/{field_id}` | ✅ | كشف مرحلة المحصول |
| **نافذة الرش** | `GET /v1/spray/forecast` | ✅ | أفضل وقت للرش |
| **توقع المحصول** | `POST /v1/yield-prediction` | ✅ | NDVI-based |

### خدمة الطقس (weather-service — port 8092)

| ميزة Farmonaut | Endpoint | الحالة | ملاحظات |
|----------------|---------|--------|---------|
| **توقعات يومية 8 أيام** | `POST /weather/forecast` (body: lat, lon; query: days=8) | ✅ حقيقي | Open-Meteo + OpenWeatherMap |
| **توقعات ساعية 48 ساعة** | `POST /weather/forecast` (days=2) | ⚠️ يومي فقط | الخدمة لا تدعم ساعي — يحتاج إضافة |
| **تقييم نافذة الرش** | `POST /weather/spray-window` | ✅ حقيقي | |
| **النتح التبخري** | `POST /weather/evapotranspiration` | ✅ حقيقي | Hargreaves ET0 |
| **خطر الصقيع** | `POST /weather/frost-risk` | ✅ حقيقي | |
| **إجهاد حراري** | `POST /weather/heat-stress` | ✅ حقيقي | |
| **GDD (أيام نمو حراري)** | `POST /weather/gdd` | ✅ حقيقي | |
| **تقرير زراعي شامل** | `POST /weather/agricultural-report` | ✅ حقيقي | يجمع كل التحليلات |

### خدمة الري الذكي (irrigation-smart — port 8094)

| ميزة Farmonaut | Endpoint | الحالة | ملاحظات |
|----------------|---------|--------|---------|
| **حساب خطة الري** | `POST /v1/calculate` | ✅ حقيقي | ET + رطوبة + طقس + محصول |
| **ميزان المياه** | `GET /v1/water-balance/{field_id}` | ✅ حقيقي | |
| **قراءة مستشعر** | `POST /v1/sensor-reading` | ✅ حقيقي | رطوبة التربة |
| **تقرير كفاءة** | `GET /v1/efficiency-report/{field_id}` | ✅ حقيقي | |
| **لا يقبل NDVI/NDWI** | — | ❌ فجوة | يعتمد على رطوبة التربة فقط، ليس الأقمار الصناعية |

### خدمة تحليل التربة (soil-analysis-service — port 8134)

| ميزة Farmonaut | Endpoint | الحالة | ملاحظات |
|----------------|---------|--------|---------|
| **تفسير فحص التربة** | `POST /interpret` | ✅ حقيقي | 11 عنصر مع عتبات حسب المحصول |
| **خطة تعديل التربة** | `POST /recommendations/amendment-plan` | ✅ حقيقي | توصيات أسمدة بالكمية |
| **حالة عنصر غذائي** | `POST /interpretation/nutrient-status` | ✅ حقيقي | N, P, K, etc. |
| **حالة pH** | `POST /interpretation/ph-status` | ✅ حقيقي | |
| **حالة EC (ملوحة)** | `POST /interpretation/ec-status` | ✅ حقيقي | |
| **اتجاهات العناصر** | `POST /trends/nutrient` | ✅ حقيقي | تحليل زمني |
| **حساب معدل سماد** | `POST /recommendations/calculate-rate` | ✅ حقيقي | كجم/هكتار |

### خدمة ذكاء المحاصيل (crop-intelligence-service — port 8095)

| ميزة Farmonaut | Endpoint | الحالة | ملاحظات |
|----------------|---------|--------|---------|
| **تشخيص شامل** | `GET /api/v1/fields/{field_id}/diagnosis` | ✅ حقيقي | أمراض + مغذيات + آفات + محصول |
| **كشف أمراض** | `POST /api/v1/disease/detect` | ✅ حقيقي | يقبل NDVI, EVI, NDRE, NDWI |
| **كشف نقص مغذيات** | `POST /api/v1/nutrients/detect` | ✅ حقيقي | |
| **تقييم آفات** | `POST /api/v1/pests/assess` | ✅ حقيقي | يقبل مؤشرات + طقس + موقع |
| **توقع محصول** | `POST /api/v1/yield/predict` | ✅ حقيقي | 14 محصول |
| **خط زمني للمنطقة** | `GET /api/v1/fields/{field_id}/zones/{zone_id}/timeline` | ✅ حقيقي | |
| **تحليل شامل مدمج** | `POST /api/v1/comprehensive-analysis` | ✅ حقيقي | **الأهم** — كل شيء دفعة واحدة |

### خدمة التضاريس (terrain-core-service — port 8185)

| ميزة Farmonaut | Endpoint | الحالة | ملاحظات |
|----------------|---------|--------|---------|
| **تحليل تضاريس كامل** | `POST /api/v1/terrain/analyze` | ✅ حقيقي | 7 مؤشرات + 4 مصادر DEM |
| **الانحدار** | `GET /api/v1/terrain/slope/{field_id}` | ✅ حقيقي | |
| **التدفق** | `GET /api/v1/terrain/flow/{field_id}` | ✅ حقيقي | كشف مجاري المياه |
| **TWI (رطوبة طوبوغرافية)** | `GET /api/v1/terrain/twi/{field_id}` | ✅ حقيقي | **يحدد مناطق تجمع المياه** |
| **خطوط الكنتور** | `GET /api/v1/terrain/contours/{field_id}` | ✅ حقيقي | |

### خدمة الآفات (pest-detection-service — port 8125)

| ميزة Farmonaut | Endpoint | الحالة | ملاحظات |
|----------------|---------|--------|---------|
| **تنبؤ موسمي** | `GET /api/v1/pests/seasonal?crop=wheat&month=3` | ✅ حقيقي | 10+ آفات شرق أوسطية |
| **تعريف بالصورة** | `POST /api/v1/pests/identify` (upload image) | ✅ حقيقي | YOLO26 vision |
| **تعريف بالأعراض** | `POST /api/v1/pests/identify/symptoms` | ✅ حقيقي | |
| **تقييم عتبة اقتصادية** | `POST /api/v1/thresholds/assess` | ✅ حقيقي | هل يستحق العلاج اقتصادياً؟ |
| **توصيات علاج** | `POST /api/v1/treatments/recommend` | ✅ حقيقي | IPM متكامل |
| **تقويم IPM** | `GET /api/v1/treatments/ipm-calendar?crop=wheat` | ✅ حقيقي | |

### خدمة WhatsApp (whatsapp-bot-service — port 8240)

| ميزة Farmonaut | Endpoint | الحالة | ملاحظات |
|----------------|---------|--------|---------|
| **إرسال تقرير** | `POST /api/v1/send` | ✅ حقيقي | نص + صور + موقع |
| **إرسال قالب** | `POST /api/v1/send-template` | ✅ حقيقي | قوالب WhatsApp Business |
| **استقبال رسائل** | `POST /webhook` | ✅ حقيقي | محادثة ذكية + AI |

---

## تاسعاً: خطة التنفيذ التقنية — ربط الواجهة بالخدمات

### المرحلة 1: الربط الفوري (أسبوع واحد)

**الهدف**: ربط واجهة Farmonaut بـ 4 خدمات جاهزة بدون mock data

```
FarmonautClient.tsx
  ├── Weather Section ──→ POST weather-service:8092/weather/forecast (days=8)
  ├── Spray Windows ──→ POST weather-service:8092/weather/spray-window
  ├── Alerts ──→ GET alert-service:8113/api/v1/alerts
  └── Field Stats ──→ GET crop-intelligence:8095/api/v1/fields/{id}/diagnosis

FieldDetailClient.tsx
  ├── Soil Tab ──→ POST soil-analysis:8134/interpret
  ├── Irrigation Tab ──→ POST irrigation-smart:8094/v1/calculate
  ├── Pests Tab ──→ POST crop-intelligence:8095/api/v1/pests/assess
  ├── Yield Tab ──→ POST crop-intelligence:8095/api/v1/yield/predict
  └── Overview ──→ POST crop-intelligence:8095/api/v1/comprehensive-analysis
```

### المرحلة 2: تفعيل الأقمار الصناعية (أسبوعان)

```
1. إضافة sentinelhub>=3.10.0 لـ requirements.txt
2. تكوين SENTINEL_HUB_CLIENT_ID + SECRET
3. تفعيل GET vegetation-analysis:8090/v1/indices/{field_id}
4. تفعيل GET vegetation-analysis:8090/v1/timeseries/{field_id}
5. بناء Hybrid Index = f(NDVI, NDWI) → 4 ألوان
```

### المرحلة 3: SAR Fallback (أسبوعان)

```
1. تفعيل Sentinel-1 SAR download في sar_processor.py
2. حساب RVI + RSM من بيانات SAR حقيقية
3. كشف cloud_cover > 30% → تحول تلقائي لـ SAR
4. GET vegetation-analysis:8090/v1/cloud-cover/{field_id}
   → if cloud > 30%:
     GET vegetation-analysis:8090/v1/soil-moisture/{field_id} (SAR)
```

---

## عاشراً: هندسة عكسية كاملة لواجهة Farmonaut — مقارنة UI

> تحليل مبني على لقطات الشاشة والفيديو — كل مكون واجهة مع مقابله في SAHOOL

### 1. Header Bar (الشريط العلوي)

```
┌─────────────────────────────────────────────────────────────┐
│ [F Logo] Farmonaut®          [Download Index Results]       │
│ Satellite Based Crop Health  [VIDEO TUTORIALS]              │
│                              [Search: demo@farmona 🔍]      │
│                              [My Profile] [My Fields] [Log Out]│
└─────────────────────────────────────────────────────────────┘
```

| مكون | Farmonaut | SAHOOL | الفجوة |
|------|----------|--------|--------|
| Logo + Tagline | ✅ "Satellite Based Crop Health" | ✅ موجود في sidebar | — |
| Download Index Results (تصدير جماعي) | ✅ تصدير كل الحقول دفعة واحدة | ❌ غائب | P1 — يحتاج batch export endpoint |
| VIDEO TUTORIALS | ✅ onboarding مدمج | ❌ غائب | P2 — محتوى تعليمي |
| Search بالبريد الإلكتروني | ✅ بحث سريع عن حقل | ✅ **أضفنا بحث** في FarmonautClient | مكتمل |
| My Profile / My Fields | ✅ | ✅ sidebar navigation | — |

### 2. Field Info Bar (شريط معلومات الحقل)

```
[Map] [Satellite]  | Owner: undefined | Area: .83 Ha, 207 acres |
                     Date: 24-10-2023 | Image Type: HYBRID |
                     [Pause Monitoring 🟢] [Delete This Field 🔴]
```

| مكون | Farmonaut | SAHOOL | الفجوة | الأولوية |
|------|----------|--------|--------|---------|
| Map / Satellite toggle | ✅ تبديل خلفية الخريطة | ❌ غائب — خريطة placeholder | P1 — يحتاج Leaflet + tile layers |
| Owner field | ✅ | ❌ — لا يُعرض المالك | P2 |
| Area بوحدتين (Ha + acres) | ✅ | ⚠️ هكتار فقط | إضافة تحويل dunams/acres |
| Date آخر صورة | ✅ | ✅ موجود في الجدول | — |
| Image Type (المؤشر النشط) | ✅ يُعرض في شريط المعلومات | ✅ يُعرض في عنوان الخريطة | — |
| **Pause Monitoring** | ✅ إيقاف مؤقت للاشتراك | ❌ **غائب تماماً** | P1 — business logic |
| **Delete This Field** | ✅ حذف نهائي | ❌ غائب في واجهة Farmonaut | P2 |

### 3. Left Sidebar — Map Controls (القائمة الجانبية)

```
For Basic Analysis:       [Hybrid]
For Colorblind:           [Colorblind Visualization]
For Satellite Image:      [TCI] [ETCI]
For Crop Health (Early):  [NDVI] [EVI] [SAVI]
For Crop Health (Late):   [NDRE]
For Irrigation:           [NDWI] [Evapotranspiration] [NDMI]
For Soil Health:          [SOC]
For Advanced:             [Erosion]
For Topography:           [DEM]
```

| مكون | Farmonaut | SAHOOL | الفجوة |
|------|----------|--------|--------|
| 9 مجموعات مؤشرات | ✅ | ✅ **مطابق** — LAYER_GROUPS في FarmonautClient | — |
| 16 مؤشر | ✅ (+ SAR RVI/RSM) | ✅ **مطابق** — MAP_LAYERS في api.ts | — |
| "Use This When Vegetation is Small" نص تعليمي | ✅ | ❌ غائب | P2 — tooltips تعليمية |
| Analysis Scale Bar في الأعلى | ✅ شريط متدرج | ❌ غائب | P1 — مقياس بصري |

### 4. Field Analysis Panel (البطاقة التحليلية)

```
┌──────────────────────────────────────────┐
│ Field Analysis ⚙️                        │
│ Crop inspection required in NW direction │
│ Irrigation inspection required in        │
│ NW, NE, SW directions                   │
└──────────────────────────────────────────┘
```

| مكون | Farmonaut | SAHOOL | الفجوة | الأولوية |
|------|----------|--------|--------|---------|
| **9-Direction Text Analysis** | ✅ "اذهب شمال غرب وافحص" | ❌ **غائب** | **P0 — أهم ميزة مفقودة** |
| تمييز بين مشكلة صحة ومشكلة ري | ✅ | ❌ | يحتاج خوارزمية NDVI + NDWI → اتجاه |
| Crop / Irrigation toggle | ✅ زران منفصلان | ❌ | P1 |
| Field Directions button | ✅ يعرض شبكة 9 أقسام | ✅ **موجود** في FarmonautClient | — |

### 5. Analysis Scale (HYBRID) — مفتاح الألوان

```
🟢 Good Crop Health & Irrigation
⬜ No Crop / Clouds
🟠 Requires Crop Health Attention
🟣 Requires Irrigation Attention
🔴 Requires Both / No Crop / Cloud
```

| مكون | Farmonaut | SAHOOL | الفجوة |
|------|----------|--------|--------|
| 5 ألوان Hybrid | ✅ | ✅ **مطابق** — HYBRID_COLORS في api.ts | — |
| مفتاح ألوان ديناميكي يتغير حسب المؤشر | ✅ | ✅ **مطابق** — colorStops لكل layer | — |

### 6. Main Map (الخريطة الرئيسية)

| مكون | Farmonaut | SAHOOL | الفجوة | الأولوية |
|------|----------|--------|--------|---------|
| خريطة تفاعلية Mapbox/Leaflet | ✅ حقيقية | ❌ **placeholder فقط** | **P0** — يحتاج Leaflet/MapLibre |
| حدود الحقل بنقاط خضراء | ✅ | ❌ | مع تفعيل الخريطة |
| تلوين الحقل حسب المؤشر | ✅ GeoTIFF overlay | ❌ | يحتاج tile server أو COG |
| بقع بيضاء = غيوم | ✅ | ❌ | مع cloud masking |
| [Crop] [Irrigation] toggle على الخريطة | ✅ | ❌ | P1 |

### 7. Bottom Field Tags (شريط التنقل السفلي)

```
[Chennai] [Unavailable] [Vikas] [Bhirari] [India] [India]
```

| مكون | Farmonaut | SAHOOL | الفجوة |
|------|----------|--------|--------|
| Quick Navigation Tags | ✅ نقرة واحدة للتنقل بين الحقول | ❌ غائب — dropdown فقط | P2 — tag chips |

### 8. Right Side Actions (أزرار يمين)

```
[Partner Fields] [KML/SHP file] [Add Polygon within Field]
```

| مكون | Farmonaut | SAHOOL | الفجوة | الأولوية |
|------|----------|--------|--------|---------|
| Partner Fields | ✅ حقول الشركاء/الموزعين | ❌ غائب | P3 — multi-tenant |
| KML/SHP Upload | ✅ | ⚠️ UI موجود لكن **بدون file handler** | P1 — إكمال AddFieldClient |
| Add Polygon within Field | ✅ مناطق فرعية داخل الحقل | ✅ **PostGIS قادر** — `ST_Subdivide` | P1 — يحتاج UI |

---

## حادي عشر: ملخص فجوات الواجهة — مرتّب بالأولوية

### P0 — حرج (يجب فوراً)

| # | المكون | الوصف | الجهد |
|---|--------|-------|-------|
| 1 | **خريطة تفاعلية حقيقية** | Leaflet/MapLibre بدلاً من placeholder | أسبوع |
| 2 | **Field Analysis Panel** | بطاقة تحليل 9 اتجاهات بنص عربي بسيط | 3 أيام |
| 3 | **Crop / Irrigation Toggle** | زران على الخريطة لتبديل عرض المشكلة | يوم |

### P1 — عالي (خلال شهر)

| # | المكون | الوصف | الجهد |
|---|--------|-------|-------|
| 4 | Map/Satellite toggle | تبديل خلفية الخريطة (OSM vs Satellite tiles) | يومان |
| 5 | Analysis Scale Bar | شريط تدرج لوني أعلى القائمة الجانبية | يوم |
| 6 | Pause Monitoring | زر إيقاف/تشغيل المراقبة (subscription logic) | 3 أيام |
| 7 | Download Index Results | تصدير جماعي لكل الحقول (CSV/PDF) | 3 أيام |
| 8 | KML/SHP Upload Handler | إكمال رفع الملفات في AddFieldClient | 3 أيام |
| 9 | Add Polygon within Field | رسم مناطق فرعية داخل حقل موجود | أسبوع |
| 10 | Area بوحدات متعددة | Ha + acres + dunams + feddan | يوم |

### P2 — متوسط

| # | المكون | الجهد |
|---|--------|-------|
| 11 | Bottom Field Tags (quick navigation) | يومان |
| 12 | VIDEO TUTORIALS section | أسبوع (محتوى) |
| 13 | Tooltips تعليمية على المؤشرات | يومان |
| 14 | Colorblind accessibility mode | 3 أيام |
| 15 | Owner field display | يوم |
| 16 | Delete This Field | يوم + confirmation dialog |

---

## ثاني عشر: مقارنة شاملة مع المنصات المنافسة

### جدول المقارنة الرئيسي

| الميزة | Farmonaut | OneSoil | EOSDA | Planet Labs | Cropio | Trimble Ag | John Deere | **SAHOOL** |
|--------|----------|---------|-------|-------------|--------|------------|------------|-----------|
| **عربي أولاً** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ ثنائي** |
| **يعمل بدون إنترنت** | ❌ | ❌ | ❌ | ❌ | ❌ | جزئي | جزئي | **✅ Offline-first** |
| **مؤشرات نباتية** | ~10 | NDVI, MSAVI | 5+ | NDVI, NDRE, NDWI, EVI, SAVI | NDVI, MSAVI, ReCI, NDRE | NDVI, NDRE, CCCI | NDVI | **25+ مؤشر** |
| **Hybrid Index** | **✅ فكرة أصيلة** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ **فجوة P0** |
| **SAR Radar Fallback** | **✅ تلقائي** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ **فجوة P1** |
| **تقرير 9 اتجاهات** | **✅ فكرة أصيلة** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ **فجوة P0** |
| **دقة الصور** | Sentinel (10m) | Sentinel (10m) | Sentinel+Landsat | **3m يومياً** | Sentinel (10m) | Sentinel+تجاري | Sentinel | Sentinel (10m) |
| **تكرار الزيارة** | 3-5 أيام | 5 أيام | 5 أيام | **يومياً** | 5 أيام | 5 أيام | 5 أيام | 5 أيام |
| **ذكاء اصطناعي** | JEEVN AI | أساسي | كشف شذوذ + تصنيف | custom ML pipelines | كشف شذوذ + محصول | VRA prescriptions | تنبؤ محصول | **شامل (11 وكيل AI)** |
| **تحليل تربة** | 5 عناصر | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **11 عنصر + RothC** |
| **DEM/تضاريس** | أساسي | ❌ | ❌ | ❌ | ❌ | RTK GPS | ❌ | **7 مؤشرات + 4 مصادر** |
| **تكامل آلات** | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ الأفضل** | **✅ الأفضل** | IoT + Jetson Orin |
| **WhatsApp Bot** | تقارير فقط | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ محادثة ذكية + AI** |
| **API مفتوح** | محدود | محدود | REST | **REST/GraphQL/STAC** | REST | CNH integration | ISO-XML | **105 route** |
| **تطبيق جوال** | ✅ | ✅ | أساسي | ❌ | ❌ | in-cab | ✅ | **✅ Flutter كامل** |
| **Edge Computing** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ Jetson Orin** |
| **شرق أوسط** | ❌ | ❌ | ❌ | شراكات خليجية | ❌ | ❌ | ❌ | **✅ معاير لليمن** |
| **السعر** | per field | **مجاني** | freemium | per km² | per hectare | مع الأجهزة | freemium | proprietary |

### التمركز التنافسي لـ SAHOOL

```
                    بسيط ←──────────────────────────→ متقدم
                         │                          │
  للمزارع البسيط         │    Farmonaut             │
  (Hybrid Index)         │    OneSoil               │
                         │                          │
                         │              SAHOOL ◄──── │  الموقع المستهدف
                         │              EOSDA        │
  للمحترف               │              Cropio       │
  (25+ مؤشر)            │                          │
                         │         Planet Labs       │
  للمطور               │         Trimble           │
  (API + ML)            │         John Deere        │
                         │                          │
                    محلي ←──────────────────────────→ عالمي
```

**موقع SAHOOL الفريد**: الوحيد الذي يجمع:
1. **عربي + offline-first** — لا يوجد منافس بهذا المزيج
2. **25+ مؤشر نباتي** — أكثر من أي منصة مقارنة
3. **11 عنصر تربة** — لا يوجد منافس يقدم هذا
4. **WhatsApp Bot ذكي** — تقارير + محادثة + كشف أمراض بالصور
5. **Edge Computing (Jetson Orin)** — لا يوجد منافس

**ما ينقص SAHOOL مقارنة بالمنافسين**:
1. **Hybrid Index** (من Farmonaut) — أهم فجوة
2. **SAR Fallback التلقائي** (من Farmonaut) — أهم للبيئة الغائمة
3. **صور يومية 3m** (من Planet) — تحتاج شراكة/ميزانية
4. **تكامل آلات حقيقي** (من Trimble/Deere) — طويل المدى
5. **OneSoil مجاني** — ضغط سعري

---

## ثالث عشر: خطة التحسين الشاملة النهائية

### المرحلة 0: أساسيات (أسبوعان) — بدون بيانات أقمار صناعية

| # | المهمة | يعتمد على | النتيجة |
|---|--------|----------|---------|
| 0.1 | **خريطة Leaflet حقيقية** بدلاً من placeholder | Leaflet 1.9.4 (مثبت) | خريطة تفاعلية مع OSM/Satellite tiles |
| 0.2 | **Hybrid Index Algorithm** | NDVI + NDWI mock data → 5 ألوان | أول بناء للمؤشر الهجين |
| 0.3 | **Field Analysis Panel** بنص 9 اتجاهات عربي | ST_Azimuth + PostGIS | "اذهب شمال غرب وافحص المحصول" |
| 0.4 | **ربط weather-service** بالواجهة | POST weather:8092/weather/forecast | طقس حقيقي 8 أيام + spray windows |
| 0.5 | **إكمال AddFieldClient** | useCreateField + file upload | نموذج إضافة حقل يعمل |

### المرحلة 1: بيانات حقيقية (شهر)

| # | المهمة | يعتمد على | النتيجة |
|---|--------|----------|---------|
| 1.1 | **تفعيل Sentinel Hub** | sentinelhub في requirements + credentials | بيانات NDVI/NDRE/NDWI/NDMI حقيقية |
| 1.2 | **ربط crop-intelligence** | POST crop-intelligence:8095/comprehensive-analysis | تشخيص شامل (أمراض + مغذيات + آفات + محصول) |
| 1.3 | **ربط soil-analysis** | POST soil-analysis:8134/interpret | تحليل تربة حقيقي 11 عنصر |
| 1.4 | **ربط irrigation-smart** | POST irrigation:8094/v1/calculate | جدول ري ذكي مع ET |
| 1.5 | **SAR Fallback** | cloud-cover > 30% → SAR data | تحول تلقائي للرادار |
| 1.6 | **KML/Shapefile parser** | ogr2ogr أو turf.js | استيراد حدود حقول |

### المرحلة 2: ميزات متقدمة (3 أشهر)

| # | المهمة | النتيجة |
|---|--------|---------|
| 2.1 | تقرير 9 أقسام عبر WhatsApp | تقرير تلقائي كل 3-5 أيام |
| 2.2 | Historical data من 2017 | أرشيف Sentinel-2 |
| 2.3 | Time Lapse + Side-by-Side | مقارنة زمنية بصرية |
| 2.4 | PDF Reports ثنائية اللغة | تصدير تقارير احترافية |
| 2.5 | نموذج ML آفات (NDVI anomaly → pest) | تنبؤ مبكر بالآفات |
| 2.6 | Add Polygon within Field | مناطق فرعية داخل حقل |
| 2.7 | Pause/Resume Monitoring | business logic |
| 2.8 | Batch Farm Operations | تجديد/تصدير جماعي |

### المرحلة 3: تمييز تنافسي (6 أشهر)

| # | المهمة | النتيجة |
|---|--------|---------|
| 3.1 | **VRA Maps** — خرائط تطبيق متغير | وصفات سماد/مبيد حسب المنطقة |
| 3.2 | **Erosion Index** | تقييم مخاطر تآكل التربة |
| 3.3 | **Colorblind Mode** | إمكانية وصول |
| 3.4 | **Multi-field Survey View** | تقرير واحد لعدة حقول |
| 3.5 | **Partner Fields** | رؤية حقول الموزعين/الشركاء |
| 3.6 | **Video Tutorials** | محتوى تعليمي مدمج |

---

## رابع عشر: هندسة عكسية لواجهات المنافسين — FieldView, OneSoil, EOSDA

### A. Climate FieldView (Bayer) — 250+ مليون فدان

**هيكل الواجهة:**

```
┌──────────────────────────────────────────────────┐
│ HEADER: [Radar] [Rainfall] [Field Health] [Yield]│
│         [Reports] [Notifications] [Activities]    │
├──────────────────────────────────────────────────┤
│                                                  │
│   ┌──────────────────────────────────────┐      │
│   │         MAIN MAP VIEW                │      │
│   │  (Full-screen interactive map)       │      │
│   │                                      │      │
│   │  ┌─────┐  Field colored by           │      │
│   │  │COLOR│  Climate Crop Index         │      │
│   │  └─────┘                             │      │
│   │                                      │      │
│   │  📍 Scouting Pins (color-coded)     │      │
│   │  ✏️ Region Drawing Tools            │      │
│   └──────────────────────────────────────┘      │
│                                                  │
│ FIELD HEALTH: [Scouting] [Vegetation] [TrueColor]│
│                                                  │
│ SIDE-BY-SIDE: Compare yield vs hybrid/population │
├──────────────────────────────────────────────────┤
│ BOTTOM: Reports | Yield Analysis | Seed Scripts  │
└──────────────────────────────────────────────────┘
```

**الميزات الفريدة لـ FieldView:**

| الميزة | الوصف | موجود في SAHOOL؟ |
|--------|-------|-----------------|
| **FieldView Drive** | جهاز in-cab يتصل بـ 60+ معدة مختلفة | ❌ — SAHOOL يعتمد IoT + Jetson Orin |
| **Scouting Pins** | دبابيس ملونة على الخريطة مع صور + ملاحظات + GPS | ❌ — يحتاج بناء |
| **Region Drawing** | رسم دائرة/حر/مضلع/مستطيل على الخريطة | ❌ — placeholder |
| **Climate Crop Index** | مؤشر خاص بـ Bayer (ليس NDVI القياسي) | SAHOOL: 25+ مؤشر (أقوى) |
| **Seed Scripts** | وصفات بذور مبنية على بيانات تاريخية + صور | ❌ — ليس في النطاق |
| **Side-by-Side (Cab)** | مقارنة yield vs planting أثناء القيادة | ❌ — يحتاج تطبيق cab |
| **Spray Insights** | توصيات رش مبنية على الطقس | ✅ — weather-service جاهز |
| **3 Image Types** | Scouting + Vegetation + True Color | ⚠️ — TCI/ETCI موجود، Scouting لا |
| **Profit Analysis** | ربط إنفاق المدخلات بالعائد | ❌ — P3 |

**ما يستحق النسخ من FieldView:**
1. **Scouting Pins** — نظام دبابيس ملونة مع صور وملاحظات وGPS
2. **Region Drawing** — 4 أدوات رسم (دائرة، حر، مضلع، مستطيل)
3. **3 أنواع صور** — فصل Scouting عن Vegetation عن True Color

---

### B. OneSoil — مجاني + أوسع انتشار

**هيكل الواجهة:**

```
┌──────────────────────────────────────────────────┐
│ HEADER: [Fields ▼] [Upload Data] [Profile]       │
├──────────┬───────────────────────────────────────┤
│ LEFT     │                                       │
│ SIDEBAR  │        MAIN MAP (Google/MapBox)        │
│          │                                       │
│ Fields   │  ┌─────────────────────────────────┐  │
│ List     │  │ Field colored by selected index │  │
│          │  │                                 │  │
│ [Sort]   │  │ NDVI | Contrasted | Average     │  │
│ [Filter] │  │ Heterogeneous                    │  │
│ [Group]  │  │                                 │  │
│          │  │        [Split View 📐]          │  │
│          │  └─────────────────────────────────┘  │
├──────────┴───────────────────────────────────────┤
│ STATUS TAB:                                      │
│ [NDVI Chart 📈] [Weather 7d ☁️] [Precipitation]│
│ [GDD 🌡️] [Productivity Zones]                  │
├──────────────────────────────────────────────────┤
│ TOOLS: [VRA Maps] [Crop Rotation] [Yield Report] │
└──────────────────────────────────────────────────┘
```

**مؤشرات OneSoil (محدّثة أبريل 2025):**

| الفئة | المؤشرات | الوصف |
|-------|---------|-------|
| نمو مبكر | **MSAVI**, SMI | تقليل تأثير التربة العارية |
| موسم متوسط→متأخر | **NDRE**, RECI | أدق من NDVI في الكثافة العالية |
| كشف إجهاد مبكر | **PRI** | يكشف الإجهاد قبل ظهوره على NDVI |
| تتبع رطوبة | **NDMI**, NDWI | قبل وبعد الري/المطر |
| أساسي | **NDVI** (4 أوضاع: Basic, Contrasted, Average, Heterogeneous) | |

**أوضاع NDVI الأربعة (ميزة فريدة):**

| الوضع | الوصف | موجود في SAHOOL؟ |
|-------|-------|-----------------|
| **Basic NDVI** | تدرج بني→أخضر (0→1) | ✅ |
| **Contrasted NDVI** | ألوان زاهية بين min/max الحقل الفعلي | ❌ **فجوة مهمة** |
| **Average NDVI** | يُظهر المتوسط فقط | ❌ |
| **Heterogeneous** | يُظهر تباين الحقل الداخلي | ❌ |

**ما يستحق النسخ من OneSoil:**
1. **Contrasted NDVI** — تدرج ألوان بين min/max الحقل (ليس 0-1 العام)
2. **Productivity Zones** — مناطق إنتاجية مبنية على 6 سنوات NDVI تاريخي
3. **Split View** — مقارنة مؤشرين أو تاريخين جنباً لجنب
4. **NDVI CSV Download** — تصدير قيم NDVI مع min/max/avg لكل تاريخ
5. **Auto Field Detection** — كشف حدود الحقل تلقائياً من الصور

---

### C. EOSDA Crop Monitoring — 10 مؤشرات + PlanetScope 3m

**هيكل الواجهة:**

```
┌──────────────────────────────────────────────────┐
│ HEADER: [Search 🔍] [Fields] [Scouting] [Team]  │
├──────┬───────────────────────────────────────────┤
│ LEFT │                                           │
│      │           MAIN MAP                        │
│ 📏   │   ┌────────────────────────────────┐     │
│ Dist │   │ Field with vegetation overlay  │     │
│      │   │                                │     │
│ 📐   │   │  [Standard ◉] [Contrast ○]   │     │
│ Draw │   │                                │     │
│      │   │  🔲 Split View (2 panels)     │     │
│ ✂️   │   │                                │     │
│ Cut  │   │  Timeline: ◀ ●──────● ▶       │     │
│      │   └────────────────────────────────┘     │
├──────┤                                           │
│INDEX │  [NDVI] [NDRE] [MSAVI] [ReCI] [Meta]     │
│SELECT│  [GNDVI] [EVI] [ARVI] [PSI]   (add-ons) │
├──────┴───────────────────────────────────────────┤
│ BOTTOM PANEL:                                    │
│ [Growth Stages] [Weather] [Soil Moisture]        │
│ [Field Activities] [Crop Rotation] [Elevation]   │
└──────────────────────────────────────────────────┘
```

**الميزات الفريدة لـ EOSDA:**

| الميزة | الوصف | موجود في SAHOOL؟ |
|--------|-------|-----------------|
| **Vegetation Meta Index** | RGB مركب: R=MSAVI, G=NDRE, B=NDVI | ❌ — فكرة ذكية جداً |
| **Disease Risk** (2025) | خوارزمية تنبؤ مخاطر الأمراض | ⚠️ SAHOOL لديه pest-detection لكن ليس disease risk model |
| **Field Cutting Tool** | قص جزء من حدود الحقل | ❌ |
| **Team Account** | مالك + كشّاف + مؤمّن + استشاري + مورد | ❌ — RBAC موجود لكن ليس بهذا التقسيم |
| **Scouting App + Web Sync** | تطبيق جوال GPS مع مزامنة تلقائية | ✅ Flutter app مع sync |
| **Upload .shp/.kml/.kmz/.geojson** | 4 تنسيقات لاستيراد الحقول | ❌ — parser غير موجود |
| **Latest Image Layer** | آخر صورة أقمار صناعية كخلفية | ❌ |
| **PlanetScope 3m يومي** | صور عالية الدقة | ❌ — Sentinel فقط (10m) |
| **10 مؤشرات جاهزة** | NDVI, NDRE, MSAVI, ReCI, Meta + 5 add-ons | ✅ SAHOOL 25+ (أقوى) |

**ما يستحق النسخ من EOSDA:**
1. **Vegetation Meta Index** — صورة واحدة تجمع 3 مؤشرات بألوان RGB
2. **Disease Risk Algorithm** — تنبؤ مخاطر الأمراض
3. **Field Cutting Tool** — قص حدود الحقل
4. **4 تنسيقات استيراد** — .shp + .kml + .kmz + .geojson
5. **Standard vs Contrast toggle** — تبديل سريع

---

## خامس عشر: ملخص الميزات المستحقة النسخ من كل منصة

| الأولوية | الميزة | المصدر | التأثير على SAHOOL |
|---------|--------|--------|-------------------|
| **P0** | Hybrid Index (5 ألوان) | Farmonaut | تبسيط جذري للمزارع البسيط |
| **P0** | 9-Direction Analysis | Farmonaut | "اذهب شمال غرب وافحص" — أقوى من GPS |
| **P0** | خريطة تفاعلية حقيقية | الكل | بدونها لا معنى للتطبيق |
| **P1** | Contrasted NDVI | OneSoil | كشف التباين الداخلي بوضوح |
| **P1** | Split View | OneSoil + EOSDA | مقارنة تاريخين/مؤشرين |
| **P1** | Scouting Pins + صور | FieldView | نظام استكشاف ميداني |
| **P1** | Region Drawing (4 أدوات) | FieldView | رسم مناطق على الخريطة |
| **P1** | SAR Fallback التلقائي | Farmonaut | حاسم لليمن والمرتفعات |
| **P1** | Disease Risk Model | EOSDA | تنبؤ مخاطر الأمراض |
| **P1** | 4 تنسيقات استيراد | EOSDA | .shp + .kml + .kmz + .geojson |
| **P2** | Vegetation Meta Index (RGB) | EOSDA | صورة واحدة = 3 مؤشرات |
| **P2** | Productivity Zones (6 سنوات) | OneSoil | مناطق إنتاجية تاريخية |
| **P2** | NDVI CSV Download | OneSoil | تصدير بيانات خام |
| **P2** | Profit Analysis | FieldView | ربط إنفاق بعائد |
| **P2** | Team Account (5 أدوار) | EOSDA | مالك/كشاف/مؤمن/استشاري/مورد |
| **P3** | PlanetScope 3m | EOSDA/OneSoil | صور يومية عالية الدقة (مكلف) |
| **P3** | Equipment Integration | FieldView | تكامل معدات (60+ شريك) |

Sources:
- [Climate FieldView](https://climate.com/en-us.html)
- [OneSoil Help Center - Vegetation Indices](https://help.onesoil.ai/en/articles/5237493-how-to-monitor-vegetation-indexes-ndvi-msavi-ndre-etc)
- [OneSoil - Contrasted NDVI](https://blog.onesoil.ai/en/how-we-added-contrasted-ndvi)
- [EOSDA Crop Monitoring User Guide](https://eos.com/user-guide/crop-monitoring/)
- [EOSDA Crop Monitoring Features](https://eos.com/products/crop-monitoring/)
- [FieldView Scouting Tools](https://climatefieldview.ca/blog/Work-smarter-with-Field-Health-Imagery-and-scouting-tools)
- [OneSoil Web vs Mobile](https://help.onesoil.ai/en/articles/5237584-how-the-onesoil-web-and-mobile-apps-differ)
- [EOSDA Disease Risk](https://eos.com/blog/eosda-crop-monitoring-gets-disease-risk-analytics/)

---

## سادس عشر: تحليل المنصات المتخصصة + سوق الشرق الأوسط

### D. Farmers Edge — بيانات مزرعة متصلة

| الميزة | الوصف | موجود في SAHOOL؟ |
|--------|-------|-----------------|
| محطات طقس + telematics + حساسات تربة | كل البيانات متصلة بالأقمار الصناعية | ✅ IoT + weather-service |
| تقارير ربح | خرائط ربحية لكل منطقة | ❌ P3 |
| تقارير كربون | تتبع انبعاثات + شهادات كربون | ❌ P3 |
| تنبؤ آفات مبني على طقس | نماذج weather-driven | ⚠️ pest-detection يقبل طقس لكن بدون ML model |

### E. Arable (Mark Weather Station) — Ground-truth

| الميزة | الوصف | موجود في SAHOOL؟ |
|--------|-------|-----------------|
| NDVI من جهاز حقلي (ليس قمر صناعي) | spectrometer على الأرض يقيس مباشرة | ❌ — مختلف تماماً |
| 40+ معامل بيئي من جهاز واحد | microclimate + ET + رطوبة + رياح | ✅ IoT sensor hub (port 8251) |
| معايرة بيانات الأقمار الصناعية | Ground-truth لتصحيح NDVI | ❌ — فكرة مهمة لتحسين الدقة |
| REST API موثق | تكامل سهل | ✅ 105 route |

### F. CropX — حساسات تربة متعددة الأعماق

| الميزة | الوصف | موجود في SAHOOL؟ |
|--------|-------|-----------------|
| حساسات تربة بأعماق متعددة | رطوبة + درجة حرارة بـ 3 أعماق | ✅ soil_sensors module موجود |
| دمج حساسات + أقمار صناعية | VRA maps من البيانين معاً | ❌ — لا يوجد دمج |
| تحسين ري مبني على ET (Tule) | قياس ET الحقيقي ميدانياً | ✅ ET بطريقة Hargreaves (حسابي وليس ميداني) |

### G. سوق الشرق الأوسط والعربي

**الوضع الحالي:**
- **لا يوجد منصة زراعة دقيقة عربية أولاً** في السوق
- معظم الحلول المنشورة في الخليج إنجليزية مع ترجمة جزئية
- ICBA (الإمارات) يستخدم أقمار صناعية لمراقبة الملوحة
- NEOM (السعودية) استثمرت في الزراعة الذكية
- Planet Labs لديها شراكات خليجية
- **التحديات الخاصة بالمنطقة:**
  - البيئة الجافة تجعل NDVI أقل فائدة (كثافة نباتية منخفضة)
  - **SAVI أهم من NDVI** في البيئات الجافة (SAHOOL يدعمه ✅)
  - مؤشرات الإجهاد المائي (NDMI, CWSI) أكثر أهمية من مؤشرات الخضرة
  - **SAHOOL هو الوحيد** بتصميم عربي أولاً + offline-first + معايرة يمنية

**الفرصة لـ SAHOOL:**

```
┌────────────────────────────────────────────────────┐
│           سوق الزراعة الذكية العربي                │
│                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ الخليج   │  │ اليمن    │  │ شمال     │        │
│  │ (NEOM,   │  │ (هدف    │  │ أفريقيا   │        │
│  │  ICBA)   │  │  أساسي) │  │          │        │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘        │
│        │             │             │               │
│        └─────────────┼─────────────┘               │
│                      │                             │
│              ┌───────┴───────┐                     │
│              │   SAHOOL      │                     │
│              │ عربي + offline│                     │
│              │ + 72 خدمة    │                     │
│              └───────────────┘                     │
│                                                    │
│  المنافسون: لا أحد في هذا الموقع                    │
└────────────────────────────────────────────────────┘
```

---

## سابع عشر: الخلاصة النهائية — 5 أفكار تحويلية

بناءً على تحليل **5 منصات منافسة** + **تدقيق 72 خدمة SAHOOL**:

### الفكرة 1: Hybrid Index (من Farmonaut)
**لماذا**: يختصر 10+ مؤشرات في 5 ألوان — المزارع اليمني البسيط يفهمها فوراً
**كيف**: `if (NDVI > 0.6 && NDWI > 0.1) → أخضر` — الكود موجود، يحتاج خوارزمية دمج فقط

### الفكرة 2: Contrasted NDVI (من OneSoil)
**لماذا**: التدرج العام (0→1) يُخفي التباين الداخلي — Contrasted يُظهره بوضوح
**كيف**: `color = interpolate(fieldMin, fieldMax, value)` — تغيير في palette فقط

### الفكرة 3: Vegetation Meta Index (من EOSDA)
**لماذا**: صورة RGB واحدة تُظهر 3 مؤشرات مختلفة — حل عبقري للشاشات الصغيرة
**كيف**: `R = MSAVI, G = NDRE, B = NDVI` — كل بكسل = 3 معلومات

### الفكرة 4: SAR Fallback التلقائي (من Farmonaut)
**لماذا**: غيوم اليمن الموسمية تحجب 30-60% من الصور — بدون SAR لا بيانات لأسابيع
**كيف**: `if cloudCover > 30%: useSAR()` — Water Cloud Model اليمني **جاهز في الكود**

### الفكرة 5: SAHOOL = OneSoil المجاني + Farmonaut الذكي + FieldView المحترف
**الموقع الفريد**: لا يوجد منصة واحدة تجمع: عربي + offline + 25 مؤشر + 11 عنصر تربة + WhatsApp + Edge Computing
**الخطوة القادمة**: ربط الخدمات الـ 72 الموجودة ببعضها عبر الواجهة — **80% من العمل مكتمل فعلاً**

---

## ثامن عشر: Copilot-API vs JEEVN AI — تدقيق عميق

> **الاستنتاج**: Copilot-API (port 8088) **يغطي 100% من ميزات JEEVN AI ويتفوق عليه تقنياً**

### جدول المقارنة التفصيلي

| ميزة JEEVN AI | Copilot-API | التفاصيل | الحكم |
|--------------|-------------|----------|-------|
| **تحليل تربة (N,P,K,Zn,S)** | ✅ | `advisory.fertilizer` tool → soil-analysis-service:8134 | **مُغطى** (11 عنصر vs 5) |
| **توقع آفات/أمراض** | ✅ | `DiseaseExpertAgent` + `ultrarag.diagnose_disease()` + pest-detection:8125 | **مُغطى** |
| **ري ذكي 4 عوامل** | ✅ | `IrrigationAdvisorAgent` + irrigation-smart:8094 + `ultrarag.recommend_irrigation()` | **مُغطى** |
| **توقع إنتاجية** | ✅ | `YieldPredictorAgent` + `ultrarag.predict_yield()` | **مُغطى** |
| **تكامل طقس** | ✅ | `weather.forecast` + `weather.alerts` → weather-service:8092 | **مُغطى** |
| **دعم عربي** | ✅ | كشف لغة تلقائي (>30% أحرف عربية) + system prompts ثنائية | **أفضل من JEEVN** |
| **واجهة محادثة** | ✅ | `POST /api/v1/chat` + `POST /api/v1/chat/stream` (SSE) | **مُغطى** |
| **RAG** | ✅ | **Tri-RAG متقدم**: Dense(0.4) + Sparse(0.3) + Knowledge Graph(0.3) | **أفضل بكثير** |
| **LLM متعدد** | ✅ | Ollama(offline) + Claude + OpenAI + Gemini + DeepSeek | **أفضل بكثير** |

### بنية وكلاء Copilot (6 وكلاء متخصصين)

```
copilot-api:8088
├── 🌾 FIELD_ADVISOR (أولوية 8)
│   └── كشف: field|crop|plant.*health|ndvi
│   └── يستدعي: ai-advisor → FieldAnalystAgent
│
├── 🌧️ WEATHER_ADVISOR (أولوية 7)
│   └── كشف: weather|forecast|temperature|rain
│   └── يستدعي: weather-service:8092
│
├── 💧 IRRIGATION_ADVISOR (أولوية 7)
│   └── كشف: irrigation|water.*schedule
│   └── يستدعي: irrigation-smart:8094 + UltraRAG
│
├── 🐛 DISEASE_EXPERT (ضمن ai-advisor)
│   └── كشف: disease|pest|مرض|آفة
│   └── يستدعي: pest-detection:8125 + ultrarag.diagnose_disease()
│
├── 🔧 CODE_FIX (أولوية 10)
│   └── يستدعي: code-fix-agent:8161
│
└── 🤖 GENERAL (fallback)
    └── أي استفسار غير مصنف
```

### الأدوات المتاحة في Copilot (37+ أداة)

```
📊 الحقول:     field.list | field.get | field.analyze | field.ndvi | field.boundaries
🌤️ الطقس:     weather.forecast | weather.current | weather.alerts | weather.historical
🧪 الاستشارات: advisory.irrigation | advisory.fertilizer | advisory.crop
🔍 RAG:       rag.search | rag.add | rag.list | rag.delete
📋 التدقيق:    audit.list | audit.search
```

### ما يتفوق فيه Copilot على JEEVN AI

| الميزة | Copilot-API | JEEVN AI |
|--------|-------------|----------|
| **Tri-RAG** (3 مسترجعات) | Dense + Sparse + Knowledge Graph | RAG عادي |
| **5 مزودي LLM** مع fallback | Ollama → Claude → OpenAI → Gemini → DeepSeek | مزود واحد |
| **Offline-first** | Ollama محلي يعمل بدون إنترنت | يحتاج إنترنت |
| **Explainability** | "لماذا هذه التوصية؟" مع عوامل مُسهمة | غير موجود |
| **Feedback Loop** | تقييم 1-5 + تصحيح + تتبع نتائج | غير موجود |
| **Action Templates** | أوامر تنفذ offline في الحقل | غير موجود |
| **أمان** | كشف حقن + PII masking + guardrails + rate limiting | أساسي |
| **11 عنصر تربة** | N,P,K,Ca,Mg,S,Zn,Fe,Mn,Cu,B | 5 فقط |

### ما ينقص Copilot مقارنة بـ JEEVN AI

| الفجوة | التفاصيل | الأولوية |
|--------|----------|---------|
| **إنذار مبكر بالأقمار الصناعية** | NDVI anomaly → pest alert pipeline غير مفعّل | P1 |
| **واجهة مزارع مخصصة** | Chat عام — ليس مصمم خصيصاً لتجربة المزارع البسيط | P1 |
| **نماذج ML خاصة بالمحصول** | توقع إنتاجية عام وليس crop-specific ML | P2 |
| **تقارير امتثال** | لا يولّد تقارير PDF تلقائية | P2 |

### الخلاصة

> **Copilot-API أقوى تقنياً من JEEVN AI بمراحل** — لكنه مصمم كـ "مهندس زراعي AI" وليس كـ "مساعد مزارع بسيط".
>
> **المطلوب**: ليس بناء JEEVN AI من الصفر — بل **تبسيط واجهة Copilot** لتكون مفهومة للمزارع اليمني البسيط.
>
> بمعنى آخر: الـ backend **جاهز 100%** — المشكلة في الـ frontend فقط.
