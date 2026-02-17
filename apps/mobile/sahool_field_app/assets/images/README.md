# دليل الصور | Images Directory

## الصور المطلوبة | Required Images

### شعار التطبيق | App Logo
- **الملف | File:** `sahool_logo.png`
- **الأبعاد | Dimensions:** 512x512 px
- **الاستخدام | Usage:** Profile screen, splash screen
- **النوع | Type:** PNG with transparency
- **الحالة | Status:** ❌ مفقود | Missing

### الخلفيات | Backgrounds
- **الاستخدام | Usage:** Empty states, loading screens
- **النوع | Type:** PNG/WebP
- **الحالة | Status:** اختياري | Optional

## إرشادات التصميم | Design Guidelines

### الشعار | Logo
- الأبعاد الدنيا: 256x256 px | Minimum dimensions: 256x256 px
- خلفية شفافة | Transparent background
- ألوان العلامة التجارية: #367C2B (أخضر) | Brand colors: #367C2B (green)
- صيغة PNG مع alpha channel | PNG format with alpha channel

### الصور العامة | General Images
- جودة عالية (72-300 DPI) | High quality (72-300 DPI)
- تحسين الحجم (< 500 KB) | Optimized size (< 500 KB)
- دعم شاشات Retina (@2x, @3x) | Retina support (@2x, @3x)

## الاستخدام في الكود | Usage in Code

```dart
// شعار التطبيق
Image.asset('assets/images/sahool_logo.png')

// مع معالجة الأخطاء
Image.asset(
  'assets/images/sahool_logo.png',
  errorBuilder: (context, error, stackTrace) {
    return Icon(Icons.agriculture, size: 48);
  },
)
```

## الحالة الحالية | Current Status

| الملف | File | الحالة | Status | الأولوية | Priority |
|-------|------|--------|--------|----------|----------|
| sahool_logo.png | Logo | ❌ مفقود | Missing | P0 حرج | P0 Critical |

## الخطوات التالية | Next Steps

1. تصميم شعار التطبيق | Design app logo
2. تصدير بصيغة PNG | Export as PNG
3. تحسين الحجم | Optimize size
4. إضافة إلى المجلد | Add to directory
5. تحديث pubspec.yaml | Update pubspec.yaml
