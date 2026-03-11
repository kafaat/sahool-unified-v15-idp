# SAHOOL Atmosphere | سهول الغلاف الجوي

## Overview | نظرة عامة

**English:** SAHOOL Atmosphere is a companion weather and atmospheric monitoring app for the SAHOOL agricultural platform. It provides real-time weather data, atmospheric conditions, and field-level environmental insights for farmers. The app features holographic field cards with gyroscope-based parallax, voice-first Arabic interface, and a bio-luminescent design language optimized for outdoor use in the Middle East.

**العربية:** تطبيق سهول الغلاف الجوي هو تطبيق مرافق لمراقبة الطقس والظروف الجوية ضمن منصة سهول الزراعية. يوفر بيانات الطقس الفورية والظروف الجوية ورؤى بيئية على مستوى الحقل للمزارعين. يتميز التطبيق ببطاقات حقول هولوغرافية مع تأثير ثلاثي الأبعاد بالجيروسكوب وواجهة صوتية عربية أولاً ولغة تصميم بيولومينية مُحسّنة للاستخدام الخارجي في الشرق الأوسط.

## Version | الإصدار

- **Version**: 16.0.0+1
- **Flutter**: 3.27.x (Dart SDK >=3.2.0 <4.0.0)
- **Platform**: SAHOOL National Agricultural Intelligence Platform
- **Owner**: KAFAAT
- **License**: Proprietary

## Features | المميزات

### Weather Monitoring | مراقبة الطقس

- **Real-time weather display** | عرض الطقس الفوري: Temperature, humidity, wind speed, and current conditions
- **Location-aware forecasts** | تنبؤات حسب الموقع: Localized weather data for farm areas
- **Atmospheric conditions** | الظروف الجوية: Humidity percentages, wind direction and speed

### Interactive Field Map | خريطة الحقول التفاعلية

- **Satellite and street map layers** | طبقات القمر الصناعي والخرائط: Toggle between ArcGIS satellite imagery and OpenStreetMap
- **NDVI overlay** | طبقة NDVI: Color-coded vegetation health visualization (healthy >0.6, stressed 0.4-0.6, critical <0.4)
- **Field polygon rendering** | رسم مضلعات الحقول: Geospatial field boundaries with color-coded health status
- **Field selection panel** | لوحة تفاصيل الحقل: Tap a field to view area, moisture, temperature, and sunlight data
- **Yemen region centered** | تركيز على منطقة اليمن: Default map view centered on Sanaa area

### Holographic Field Cards | بطاقات الحقول الهولوغرافية

- **Gyroscope-based 3D parallax** | تأثير ثلاثي الأبعاد بالجيروسكوب: Cards tilt based on device accelerometer data
- **Status-based glow effects** | تأثيرات توهج حسب الحالة: Active (green), Warning (amber), Alert (red), Inactive (gray)
- **Real-time metrics** | مقاييس فورية: Soil moisture, temperature, and sunlight percentage per field
- **Glassmorphism design** | تصميم زجاجي: Frosted glass UI with translucent overlays

### Voice-First Interface | واجهة الصوت أولاً

- **Arabic speech recognition** | التعرف على الكلام العربي: Voice commands in Arabic via `speech_to_text`
- **Voice-triggered field queries** | استعلامات الحقل الصوتية: Ask about field status, start irrigation, show alerts
- **Animated pulse feedback** | تغذية راجعة متحركة: Visual pulse animation while listening
- **Haptic feedback patterns** | أنماط ردود فعل لمسية: Distinct haptic patterns for different interactions

### Live Dashboard | لوحة التحكم المباشرة

- **Active fields count** | عدد الحقول النشطة: Real-time count of monitored fields
- **Sensor monitoring** | مراقبة المستشعرات: Total active sensor count
- **Crop health percentage** | نسبة صحة المحاصيل: Platform-wide crop health aggregation
- **Water savings metric** | مقياس توفير المياه: Water usage optimization tracking
- **Time-based Arabic greetings** | تحيات عربية حسب الوقت: Morning, afternoon, and evening greetings

### Service Health Monitoring | مراقبة صحة الخدمات

- **Backend health checks** | فحوصات صحة الخدمات الخلفية: Monitors Fields, Weather, NDVI, and Tasks services
- **Latency tracking** | تتبع زمن الاستجابة: Per-service latency with color-coded thresholds
- **Auto-refresh** | تحديث تلقائي: Health checks every 60 seconds
- **Compact and expanded views** | عرض مختصر وموسع: Adaptable widget display

### Device Security | أمان الجهاز

- **Root/Jailbreak detection** | كشف الروت والجيلبريك: Detects compromised devices via `safe_device`
- **Emulator detection** | كشف المحاكي: Identifies simulator/emulator environments
- **Threat level classification** | تصنيف مستوى التهديد: None, Low, Medium, High, Unknown
- **Bilingual threat messages** | رسائل تهديد ثنائية اللغة: Arabic and English security warnings

### Theming | السمات

- **Light and dark modes** | الوضع النهاري والليلي: Full light/dark theme support with system default option
- **Bio-luminescent dark theme** | سمة داكنة بيولومينية: Deep green-black palette for outdoor visibility
- **Industrial theme variant** | سمة صناعية: Alternative industrial design language

## Getting Started | البدء

### Prerequisites | المتطلبات

- Flutter 3.27.x or later
- Dart SDK >=3.2.0 <4.0.0
- Android SDK (API 23+) or Xcode (iOS)

### Installation | التثبيت

```bash
# Navigate to the app directory | الانتقال إلى مجلد التطبيق
cd apps/mobile/sahol_atmosphere

# Install dependencies | تثبيت التبعيات
flutter pub get

# Copy environment file | نسخ ملف البيئة
cp .env.example .env

# Run the app | تشغيل التطبيق
flutter run
```

### Build | البناء

```bash
# Debug APK | نسخة تجريبية
flutter build apk --debug

# Release APK | نسخة إصدار
flutter build apk --release

# Android App Bundle | حزمة أندرويد
flutter build appbundle
```

### Testing | الاختبار

```bash
# Run unit tests | تشغيل اختبارات الوحدة
flutter test

# Run with coverage | تشغيل مع التغطية
flutter test --coverage

# Analyze code | تحليل الكود
flutter analyze
```

## Architecture | الهيكلية

```
lib/
├── main.dart                          # App entry point with security checks
│                                      # نقطة دخول التطبيق مع فحوصات الأمان
├── core/
│   └── security/
│       └── device_security.dart       # Root/jailbreak detection, threat classification
│                                      # كشف الروت والجيلبريك، تصنيف التهديدات
├── models/
│   └── field_model.dart               # Field data model with health status, crop types
│                                      # نموذج بيانات الحقل مع حالة الصحة وأنواع المحاصيل
├── providers/
│   └── theme_provider.dart            # Riverpod theme state (light/dark/system)
│                                      # حالة السمة بـ Riverpod (فاتح/داكن/نظام)
├── screens/
│   ├── dashboard_screen.dart          # Main dashboard with weather, stats, field cards
│   │                                  # لوحة التحكم الرئيسية
│   ├── field_map_screen.dart          # Interactive map with NDVI overlay
│   │                                  # خريطة تفاعلية مع طبقة NDVI
│   └── fields_list_screen.dart        # Field list view
│                                      # عرض قائمة الحقول
├── theme/
│   ├── atmosphere_theme.dart          # Design tokens: colors, spacing, typography, radius
│   │                                  # رموز التصميم: الألوان، التباعد، الخطوط
│   └── industrial_theme.dart          # Industrial design variant
│                                      # سمة التصميم الصناعي
└── widgets/
    ├── holographic_field_card.dart     # 3D parallax field card with gyroscope
    │                                  # بطاقة حقل ثلاثية الأبعاد مع الجيروسكوب
    ├── weather_widget.dart            # Current weather display
    │                                  # عرض الطقس الحالي
    ├── stats_panel.dart               # Live statistics grid
    │                                  # شبكة الإحصائيات المباشرة
    ├── voice_control_button.dart      # Voice control with Arabic speech recognition
    │                                  # التحكم الصوتي مع التعرف على الكلام العربي
    └── service_health_widget.dart     # Backend service health monitoring
                                       # مراقبة صحة الخدمات الخلفية
```

### Supported Crop Types | أنواع المحاصيل المدعومة

| Crop | المحصول | Code |
| ---- | ------- | ---- |
| Wheat | قمح | `wheat` |
| Tomato | طماطم | `tomato` |
| Palm | نخيل | `palm` |
| Lettuce | خس | `lettuce` |
| Corn | ذرة | `corn` |
| Barley | شعير | `barley` |
| Cotton | قطن | `cotton` |
| Coffee | بن | `coffee` |
| Grapes | عنب | `grapes` |

## Key Dependencies | التبعيات الرئيسية

| Package | Version | Purpose | الغرض |
| ------- | ------- | ------- | ----- |
| `flutter_riverpod` | ^2.6.1 | State management | إدارة الحالة |
| `sensors_plus` | ^7.0.0 | Gyroscope/accelerometer for parallax | الجيروسكوب للتأثير ثلاثي الأبعاد |
| `flutter_map` | >=8.1.1 <8.2.0 | Interactive field maps | خرائط الحقول التفاعلية |
| `latlong2` | ^0.9.1 | Geographic coordinates | الإحداثيات الجغرافية |
| `geolocator` | ^13.0.2 | Device location | تحديد الموقع |
| `speech_to_text` | ^7.0.0 | Arabic voice recognition | التعرف على الكلام العربي |
| `dio` | ^5.7.0 | HTTP client for API calls | عميل HTTP |
| `fl_chart` | ^0.69.2 | Data visualization charts | مخططات عرض البيانات |
| `glassmorphism` | ^3.0.0 | Frosted glass UI effects | تأثيرات الزجاج المصنفر |
| `flutter_animate` | ^4.3.0 | Declarative animations | الرسوم المتحركة |
| `vibration` | ^1.8.4 | Haptic feedback | ردود الفعل اللمسية |
| `safe_device` | ^1.1.7 | Root/jailbreak detection | كشف الروت والجيلبريك |
| `device_info_plus` | ^10.1.2 | Device information | معلومات الجهاز |
| `connectivity_plus` | ^6.1.1 | Network connectivity | الاتصال بالشبكة |
| `go_router` | ^14.6.2 | Navigation routing | التوجيه والتنقل |
| `flutter_secure_storage` | ^9.2.2 | Secure key storage | التخزين الآمن |
| `shared_preferences` | ^2.3.3 | Local preferences | التفضيلات المحلية |

## Localization | الترجمة

The app supports the following locales with Arabic as the primary language:

| Locale | Language | اللغة |
| ------ | -------- | ----- |
| `ar-SA` | Arabic (Saudi Arabia) - Default | العربية (السعودية) - افتراضي |
| `ar-YE` | Arabic (Yemen) | العربية (اليمن) |
| `en-US` | English (United States) | الإنجليزية (أمريكا) |

## Related Services | الخدمات ذات الصلة

This app connects to the following SAHOOL platform services:

| Service | Port | Purpose | الغرض |
| ------- | ---- | ------- | ----- |
| `weather-service` | 8092 | Weather data | بيانات الطقس |
| `field-management-service` | 3000 | Field operations | إدارة الحقول |
| `vegetation-analysis-service` | 8090 | NDVI analysis | تحليل NDVI |
| `task-service` | 8103 | Task management | إدارة المهام |

## License | الرخصة

Proprietary - KAFAAT. All rights reserved.
