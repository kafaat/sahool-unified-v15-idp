# 📅 SAHOOL Calendar Assumptions

> توثيق مرجعي للتقويم الزراعي الفلكي اليمني

## 1. المرجع الأساسي (Base Reference)

### التقويم المعتمد

```yaml
Primary Calendar: التقويم الحميري العنسي
Official Since: 2006
Reference: قرار وزاري يمني

Day 1 Reference:
  calendar: Gregorian
  day: January 1st
  note: start_day_of_year is 1-indexed from Jan 1

Year Length: 365 days (366 in leap years)
```

### حساب اليوم من السنة (start_day_of_year)

```python
# Example: العلب starts July 16
# July 16 = Day 197 of year (non-leap year)

from datetime import date

def get_day_of_year(month: int, day: int, year: int = 2025) -> int:
    """Calculate day of year (1-indexed)"""
    return date(year, month, day).timetuple().tm_yday

# July 16 = get_day_of_year(7, 16) = 197
```

## 2. النجوم الزراعية الـ 28

### ترتيب النجوم حسب السنة الميلادية

| # | النجم | التاريخ الميلادي | start_day_of_year | المدة |
|---|-------|------------------|-------------------|-------|
| 1 | النعايم | 1 يناير | 1 | 13 |
| 2 | البلدة | 14 يناير | 14 | 13 |
| 3 | سعد الذابح | 27 يناير | 27 | 13 |
| 4 | سعد بلع | 9 فبراير | 40 | 13 |
| 5 | سعد السعود | 22 فبراير | 53 | 13 |
| 6 | سعد الأخبية | 7 مارس | 66 | 13 |
| 7 | الفرغ المقدم | 20 مارس | 79 | 13 |
| 8 | الفرغ المؤخر | 2 أبريل | 92 | 13 |
| 9 | بطن الحوت | 15 أبريل | 105 | 13 |
| 10 | الشرطان | 28 أبريل | 118 | 13 |
| 11 | البطين | 11 مايو | 131 | 13 |
| 12 | الثريا | 24 مايو | 144 | 13 |
| 13 | الدبران | 6 يونيو | 157 | 13 |
| 14 | الهقعة | 19 يونيو | 170 | 13 |
| 15 | الهنعة | 2 يوليو | 183 | 13 |
| 16 | الذراع | 15 يوليو | 196 | 13 |
| 17 | **العلب** | **16 يوليو** | **197** | 13 |
| 18 | النثرة | 29 يوليو | 210 | 13 |
| 19 | الطرفة | 11 أغسطس | 223 | 13 |
| 20 | **سهيل** | **24 أغسطس** | **236** | 52 |
| 21 | الغفر | 15 أكتوبر | 288 | 13 |
| 22 | الزبانا | 28 أكتوبر | 301 | 13 |
| 23 | الإكليل | 10 نوفمبر | 314 | 13 |
| 24 | القلب | 23 نوفمبر | 327 | 13 |
| 25 | الشولة | 6 ديسمبر | 340 | 13 |
| 26 | النعايم | 19 ديسمبر | 353 | 13 |

> **ملاحظة**: سهيل يستمر 52 يوماً (4 روابع × 13 يوم)

## 3. الاختلافات الإقليمية (Regional Offsets)

### كيفية حساب offset_days

```yaml
Regional Variations:
  
  المرتفعات (Highlands):
    base_calendar: العنسي
    offset_days: 0
    reference: المرجع الأساسي
    
  تهامة (Tihama):
    base_calendar: الواسعي
    offset_days: -4
    note: النجوم تبدأ 4 أيام قبل المرتفعات
    
  حضرموت (Hadramout):
    base_calendar: خاص
    offset_days: +3
    note: النجوم تبدأ 3 أيام بعد المرتفعات
```

### مثال حسابي

```python
def get_star_date_for_region(
    base_day_of_year: int,
    region: str,
    year: int = 2025
) -> date:
    """حساب تاريخ النجم حسب المنطقة"""
    
    offsets = {
        "المرتفعات": 0,
        "تهامة": -4,
        "حضرموت": +3,
    }
    
    offset = offsets.get(region, 0)
    adjusted_day = base_day_of_year + offset
    
    return date(year, 1, 1) + timedelta(days=adjusted_day - 1)

# العلب في المرتفعات: July 16
# العلب في تهامة: July 12 (4 days earlier)
# العلب في حضرموت: July 19 (3 days later)
```

## 4. السنة الكبيسة (Leap Year Handling)

```yaml
Leap Year Rule:
  action: Add 1 day to all dates after Feb 28
  implementation: Use Python's datetime (handles automatically)
  
Code Example:
  # Always use datetime for calculations
  from datetime import date, timedelta
  
  # This handles leap years automatically
  star_date = date(year, 1, 1) + timedelta(days=start_day_of_year - 1)
```

## 5. الفصول الزراعية (Agricultural Seasons)

```yaml
Seasons:
  خريف (Autumn):
    starts: star_alab (العلب)
    start_day: 197
    date: ~July 16
    duration: ~91 days
    
  شتاء (Winter):
    starts: star_iklil (الإكليل)
    start_day: 314
    date: ~November 10
    duration: ~91 days
    
  ربيع (Spring):
    starts: star_saad_soud (سعد السعود)
    start_day: 53
    date: ~February 22
    duration: ~91 days
    
  صيف (Summer):
    starts: star_thuraya (الثريا)
    start_day: 144
    date: ~May 24
    duration: ~53 days (القيظ)
```

## 6. مصادر التوثيق

```yaml
Primary Sources:
  - name: "التقويم الحميري العنسي"
    type: Official Government
    year: 2006
    
  - name: "الروزنامة اليمنية"
    author: "المركز الوطني للمعلومات"
    
  - name: "الأمثال الشعبية الزراعية"
    source: "التراث الشفهي اليمني"
    reliability: Variable (scored per proverb)

Secondary Sources:
  - "منازل القمر والفصول الزراعية" - دراسات محلية
  - مقابلات مع مزارعين في المرتفعات وتهامة
```

## 7. قواعد التحديث

```yaml
Update Rules:
  - أي تغيير في التواريخ يتطلب مراجعة خبير تراث
  - الأمثال الجديدة تبدأ بـ reliability_score = 0.5
  - التحقق من الأمثال يرفع/يخفض الـ score
  - لا يُحذف أي مثل، فقط يُعطّل (is_active = false)
```

## 8. ADR Reference

هذه الافتراضات موثقة في:
- [ADR-001: Calendar System](../adr/ADR-001-calendar-system.md)
- [ADR-002: Regional Variations](../adr/ADR-002-regional-variations.md)
