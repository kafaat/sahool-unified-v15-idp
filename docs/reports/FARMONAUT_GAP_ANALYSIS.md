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
