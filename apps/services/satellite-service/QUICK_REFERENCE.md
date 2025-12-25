# Quick Reference Card | بطاقة مرجعية سريعة
## Vegetation Indices for Yemen Crops | المؤشرات النباتية للمحاصيل اليمنية

---

## 📊 When to Use Which Index | متى تستخدم أي مؤشر

### 🌱 Early Season (البداية - البزوغ)
**Use:** `GNDVI`, `VARI`, `GLI`

| Index | Good Value | Action if Low |
|-------|-----------|---------------|
| GNDVI | > 0.45 | Monitor closely - early stress |
| VARI  | > 0.3  | Check soil moisture |

**بالعربية:**
- **GNDVI > 0.45**: صحي | **< 0.45**: راقب بحرص
- **VARI > 0.3**: جيد | **< 0.3**: تحقق من رطوبة التربة

---

### 🌿 Mid-Season (النمو الخضري)
**Use:** `NDVI`, `NDRE`, `LAI`

| Index | Excellent | Good | Poor | Critical |
|-------|-----------|------|------|----------|
| NDVI  | > 0.7 | 0.5-0.7 | 0.2-0.5 | < 0.2 |
| NDRE  | > 0.35 | 0.25-0.35 | 0.15-0.25 | < 0.15 |
| LAI   | > 4 | 2.5-4 | 1.5-2.5 | < 1.5 |

**Action Guide:**
- **NDRE < 0.25**: Add nitrogen fertilizer | **أضف سماد نيتروجيني**
- **NDVI declining**: Inspect field for disease/pests | **افحص الآفات/الأمراض**
- **LAI < 2**: Low leaf coverage - check nutrition | **غطاء ضعيف - تحقق من التغذية**

---

### 🌺 Flowering & Fruiting (الإزهار والإثمار)
**Use:** `NDRE`, `MCARI`, `NDWI`

| Index | Status | Immediate Action |
|-------|--------|------------------|
| NDWI < 0 | 🚨 CRITICAL | **Irrigate NOW** - **ري فوراً** |
| NDWI 0-0.2 | ⚠️ Warning | Schedule irrigation | **جدول الري** |
| NDWI > 0.2 | ✅ Good | Continue monitoring | **استمر بالمراقبة** |

**بالعربية:**
- **NDWI < 0**: إجهاد مائي حاد - ري عاجل
- **NDRE < 0.2**: نقص كلوروفيل - قد يؤثر على الإنتاج

---

### 🌾 Pre-Harvest (قبل الحصاد)
**Use:** `NDVI`, `NDMI`

**Harvest Timing:**
- **NDVI declining** + **NDMI < 0**: Approaching maturity | **اقتراب النضج**
- **NDVI stable** + **NDMI > 0.1**: Wait 1-2 weeks | **انتظر أسبوع**

---

## 🚨 Emergency Indicators | مؤشرات الطوارئ

### Water Stress | الإجهاد المائي
```
NDWI < -0.2  →  🚨 URGENT IRRIGATION NEEDED
                 ري عاجل مطلوب
```

### Nitrogen Deficiency | نقص النيتروجين
```
NDRE < 0.15  →  ⚠️ APPLY NITROGEN FERTILIZER
                 أضف سماد نيتروجيني
```

### General Health Decline | تدهور الصحة العامة
```
NDVI dropping >0.1 in 1 week  →  🔍 FIELD INSPECTION
                                   فحص ميداني فوري
```

---

## 📱 Mobile Quick Commands

### Get Field Health
```bash
curl "http://satellite:8090/v1/indices/{field_id}?lat=15.37&lon=44.19"
```

### Check Nitrogen Status
```bash
curl "http://satellite:8090/v1/indices/{field_id}/ndre?lat=15.37&lon=44.19&crop_type=wheat&growth_stage=vegetative"
```

### Check Water Stress
```bash
curl "http://satellite:8090/v1/indices/{field_id}/ndwi?lat=15.37&lon=44.19&crop_type=sorghum"
```

---

## 🌾 Crop-Specific Quick Guide

### Wheat (القمح)

| Stage | Best NDVI | Action if Low NDVI | Best NDRE |
|-------|-----------|-------------------|-----------|
| Emergence | > 0.20 | Re-check in 3 days | - |
| Vegetative | > 0.50 | Check water + nitrogen | > 0.25 |
| Reproductive | > 0.60 | Critical - inspect | > 0.30 |
| Maturation | 0.40-0.60 | Normal senescence | - |

### Sorghum (الذرة الرفيعة)

| Stage | Best NDVI | Action if Low NDVI | Best NDRE |
|-------|-----------|-------------------|-----------|
| Emergence | > 0.25 | Monitor daily | - |
| Vegetative | > 0.60 | Increase irrigation | > 0.28 |
| Reproductive | > 0.70 | Critical stage | > 0.32 |
| Maturation | 0.35-0.50 | Normal | - |

### Coffee (البن)

| Stage | Best NDVI | Action if Low | Best NDRE |
|-------|-----------|--------------|-----------|
| Vegetative | > 0.65 | Check soil nutrients | > 0.30 |
| Flowering | > 0.70 | Ensure adequate water | > 0.32 |

### Qat (القات)

| Stage | Best NDVI | Action if Low | Best NDRE |
|-------|-----------|--------------|-----------|
| Growth | > 0.60 | Fertilize + irrigate | > 0.28 |
| Harvest | > 0.65 | Quality will be low | > 0.30 |

---

## 📅 Weekly Monitoring Checklist

### Monday - Get Baseline
- [ ] Check NDVI for overall health
- [ ] Note current growth stage

### Wednesday - Mid-Week Check
- [ ] Check NDWI for water status
- [ ] If vegetative stage: Check NDRE

### Friday - Week Planning
- [ ] Compare to Monday values
- [ ] Plan irrigation for weekend
- [ ] Plan fertilization if needed

---

## 🎯 Decision Tree

```
Start: Check NDVI
    │
    ├─ NDVI < 0.2 → 🚨 URGENT: Field inspection
    │
    ├─ NDVI 0.2-0.4 → Check NDWI
    │   ├─ NDWI < 0 → Irrigate
    │   └─ NDWI > 0 → Check NDRE
    │       ├─ NDRE < 0.2 → Fertilize
    │       └─ NDRE > 0.2 → Monitor
    │
    ├─ NDVI 0.4-0.7 → ✅ Healthy - Continue
    │
    └─ NDVI > 0.7 → ✅ Excellent - Maintain
```

---

## 💡 Pro Tips | نصائح احترافية

### Tip 1: Don't Panic on Single Low Reading
**One low index value might be:**
- Cloud shadow during satellite pass
- Recent irrigation (normal for water indices)
- Sensor calibration variation

**Action:** Check again in 5 days before major decisions

**بالعربية:** لا تقلق من قراءة منخفضة واحدة - قد تكون ظل سحابة أو ري حديث

---

### Tip 2: Combine Multiple Indices
**Best Practice:**
- ✅ Check 3-4 indices before major decision
- ✅ Look at trends over 2-3 weeks
- ✅ Combine satellite + field observation

**Not Recommended:**
- ❌ Decision based on single index
- ❌ Ignoring field conditions

---

### Tip 3: Seasonal Patterns
**Yemen's Growing Seasons:**

**Spring (March-May):** Rapid growth - expect NDVI to increase weekly
**Summer (June-Aug):** Peak biomass - NDVI should be highest
**Fall (Sep-Nov):** Maturation - NDVI decline is normal
**Winter (Dec-Feb):** Emergence for some crops - low NDVI is normal

---

## 📞 Emergency Contacts

**Critical Values - Immediate Action Required:**

| Index | Critical Value | Action | Arabic |
|-------|---------------|--------|---------|
| NDWI | < -0.2 | Irrigate within 12 hours | الري خلال 12 ساعة |
| NDVI | Drop > 0.15 in 1 week | Field inspection today | فحص اليوم |
| NDRE | < 0.10 | Nitrogen fertilizer this week | سماد هذا الأسبوع |

---

## 🔄 Regular Monitoring Frequency

| Crop Stage | Check Frequency | Priority Indices |
|-----------|----------------|------------------|
| Emergence | Daily | GNDVI, VARI |
| Early Vegetative | Every 3 days | NDVI, GNDVI |
| Mid Vegetative | Twice weekly | NDVI, NDRE, NDWI |
| Reproductive | Twice weekly | NDRE, NDWI, MCARI |
| Maturation | Weekly | NDVI, NDMI |

---

## 📖 Index Name Translation

| English | Arabic | Code |
|---------|--------|------|
| Normalized Difference Vegetation Index | مؤشر الفرق الطبيعي للنباتات | NDVI |
| Normalized Difference Red Edge | مؤشر الحافة الحمراء | NDRE |
| Green NDVI | مؤشر NDVI الأخضر | GNDVI |
| Normalized Difference Water Index | مؤشر الفرق الطبيعي للماء | NDWI |
| Leaf Area Index | مؤشر مساحة الأوراق | LAI |
| Normalized Difference Moisture Index | مؤشر رطوبة النبات | NDMI |

---

**Print this card and keep it in the field!**
**اطبع هذه البطاقة واحتفظ بها في الحقل!**

---

*Version: 1.0 | Last Updated: December 2025*
*SAHOOL Satellite Service - Advanced Vegetation Monitoring*
