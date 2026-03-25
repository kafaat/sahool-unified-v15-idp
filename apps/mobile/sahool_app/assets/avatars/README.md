# دليل الأفاتار | Avatars Directory

## الأفاتار المطلوبة | Required Avatars

### أفاتار المزارعين | Farmer Avatars
- **farmer1.png** - مزارع افتراضي 1 | Default farmer avatar 1
- **farmer2.png** - مزارع افتراضي 2 | Default farmer avatar 2
- **الاستخدام | Usage:** Community posts, user profiles
- **الأبعاد | Dimensions:** 128x128 px
- **الحالة | Status:** ✅ موجود | Present

### أفاتار الخبراء | Expert Avatars
- **expert1.png** - خبير افتراضي 1 | Default expert avatar 1
- **expert2.png** - خبير افتراضي 2 | Default expert avatar 2
- **الاستخدام | Usage:** Expert replies, advisor screen
- **الأبعاد | Dimensions:** 128x128 px
- **الحالة | Status:** ✅ موجود | Present

## إرشادات التصميم | Design Guidelines

### الأبعاد | Dimensions
- الحجم الأساسي: 128x128 px | Base size: 128x128 px
- @2x: 256x256 px
- @3x: 384x384 px

### النمط | Style
- دائري أو مربع بحواف دائرية | Circular or rounded square
- خلفية شفافة أو لون صلب | Transparent or solid background
- ألوان محايدة | Neutral colors
- أيقونات بسيطة | Simple icons

### الألوان المقترحة | Suggested Colors
- المزارعون: #4CAF50 (أخضر) | Farmers: #4CAF50 (green)
- الخبراء: #2196F3 (أزرق) | Experts: #2196F3 (blue)

## الاستخدام في الكود | Usage in Code

```dart
// عرض أفاتار مع معالجة الأخطاء
CircleAvatar(
  backgroundImage: AssetImage('assets/avatars/farmer1.png'),
  child: Image.asset(
    'assets/avatars/farmer1.png',
    errorBuilder: (context, error, stackTrace) {
      return Icon(Icons.person, size: 32);
    },
  ),
)

// أو استخدام Icon كبديل افتراضي
CircleAvatar(
  backgroundColor: Color(0xFF4CAF50),
  child: Icon(Icons.person, color: Colors.white),
)
```

## البدائل الافتراضية | Default Fallbacks

في حالة عدم توفر الصور، يمكن استخدام:
If images are not available, use:

```dart
// أيقونات Material Icons
Icons.person
Icons.agriculture
Icons.eco
Icons.face

// ألوان تمثيلية
farmer: Color(0xFF4CAF50)
expert: Color(0xFF2196F3)
admin: Color(0xFFFF9800)
```

## الحالة الحالية | Current Status

| الملف | File | الحالة | Status | الأولوية | Priority |
|-------|------|--------|--------|----------|----------|
| farmer1.png | Farmer avatar 1 | ✅ موجود | Present | - | - |
| farmer2.png | Farmer avatar 2 | ✅ موجود | Present | - | - |
| expert1.png | Expert avatar 1 | ✅ موجود | Present | - | - |
| expert2.png | Expert avatar 2 | ✅ موجود | Present | - | - |

## الحل المؤقت | Temporary Solution

حتى يتم تصميم الأفاتار المخصصة، يمكن استخدام أيقونات افتراضية:
Until custom avatars are designed, use default icons:

1. استخدام Material Icons للأفاتار | Use Material Icons for avatars
2. تطبيق ألوان مميزة لكل نوع | Apply distinctive colors per type
3. إضافة معالجة أخطاء في جميع الاستخدامات | Add error handling in all usages

## الخطوات التالية | Next Steps

1. تصميم 4 أفاتار افتراضية | Design 4 default avatars
2. تصدير بصيغة PNG @1x, @2x, @3x | Export as PNG @1x, @2x, @3x
3. تحسين الحجم (< 50 KB) | Optimize size (< 50 KB)
4. إضافة إلى المجلد | Add to directory
5. تحديث pubspec.yaml | Update pubspec.yaml
6. تحديث الكود لمعالجة الأخطاء | Update code for error handling
