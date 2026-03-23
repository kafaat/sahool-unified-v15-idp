# SAHOOL Mobile App - Localization (l10n)

This directory contains the localization files for the SAHOOL mobile application, providing comprehensive Arabic and English translations.

## Files Structure

```
lib/l10n/
├── app_ar.arb          # Arabic translations (1000+ strings)
├── app_en.arb          # English translations (1000+ strings)
├── l10n.dart           # Localization configuration & utilities
└── README.md           # This file

l10n.yaml               # Flutter l10n generation config (root level)
```

## Supported Languages

- **Arabic (ar)** - Primary language for Yemen (RTL)
- **English (en)** - Secondary language (LTR)

## Translation Categories

The ARB files include comprehensive translations for:

### Core Features

- **Common**: Buttons, labels, errors, confirmations
- **Navigation**: Menu items, tabs, breadcrumbs
- **Authentication**: Login, signup, password management

### Agricultural Features

- **Fields**: Field management, boundaries, coordinates
- **Crops**: Yemen-specific crops (wheat, barley, sorghum, qat, coffee, etc.)
- **Soil**: Soil types, nutrients, analysis
- **Weather**: Forecasts, conditions, alerts
- **Satellite**: NDVI, imagery, vegetation health

### Precision Agriculture

- **VRA (Variable Rate Application)**: Prescription maps, zones, rates
- **GDD (Growing Degree Days)**: Growth stages, thermal time
- **Spray**: Recommendations, timing, conditions
- **Rotation**: Crop rotation plans, compatibility
- **Profitability**: Financial analysis, costs, revenue

### Management

- **Inventory**: Stock management, movements, suppliers
- **Equipment**: Machinery, maintenance, booking
- **Tasks**: Task management, assignments, tracking
- **Chat**: Messaging, conversations, groups

### System

- **Settings**: App preferences, sync, security
- **Notifications**: Alerts, push notifications
- **Analytics**: Reports, charts, statistics
- **Errors**: Validation, network, server errors

## Usage

### 1. Setup (Already Done)

The localization is already configured in `pubspec.yaml`:

```yaml
flutter:
  generate: true
```

### 2. Generate Localization Code

Run this command to generate localization code from ARB files:

```bash
flutter gen-l10n
```

This generates code in `lib/generated/l10n/` directory.

### 3. Use in App

Import and use in your Flutter app:

```dart
import 'package:flutter/material.dart';
import 'package:sahool_field_app/l10n/l10n.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      // Localization delegates
      localizationsDelegates: AppLocalizations.localizationsDelegates,

      // Supported locales
      supportedLocales: AppLocalizations.supportedLocales,

      // Locale resolution
      localeResolutionCallback: AppLocalizations.localeResolutionCallback,

      // Default to Arabic for Yemen
      locale: const Locale('ar', ''),

      home: HomeScreen(),
    );
  }
}
```

### 4. Access Translations in Widgets

```dart
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Column(
      children: [
        Text(l10n.appName),        // "سهول" or "SAHOOL"
        Text(l10n.fields),         // "الحقول" or "Fields"
        Text(l10n.weather),        // "الطقس" or "Weather"
        Text(l10n.satellite),      // "الأقمار الصناعية" or "Satellite"
      ],
    );
  }
}
```

### 5. RTL/LTR Support

The app automatically handles RTL (Right-to-Left) for Arabic:

```dart
// Check if current locale is RTL
bool isRTL = context.isRTL;

// Get text direction
TextDirection direction = context.textDirection;

// Use directional padding
EdgeInsets padding = LocalizedLayout(context).edgeInsets(
  start: 16,  // Right in RTL, Left in LTR
  end: 8,     // Left in RTL, Right in LTR
  top: 12,
  bottom: 12,
);
```

### 6. Number Formatting

Format numbers with locale-aware formatting:

```dart
final numberFormat = LocalizedNumberFormat(Localizations.localeOf(context));

// Format regular number
String formatted = numberFormat.format(1234.56);
// Arabic: "١٢٣٤.٥٦"
// English: "1234.56"

// Format currency (Yemeni Rial)
String price = numberFormat.formatCurrency(5000);
// Arabic: "٥٠٠٠.٠٠ ريال"
// English: "YER 5000.00"

// Format percentage
String percent = numberFormat.formatPercentage(85.5);
// Arabic: "%٨٥.٥"
// English: "85.5%"
```

### 7. Directional Icons

Use icons that flip for RTL:

```dart
DirectionalIcon(
  Icons.arrow_forward,  // Automatically flips to arrow_back in RTL
  size: 24,
  color: Colors.blue,
  flipForRTL: true,
)
```

### 8. Language Switching

Switch between languages:

```dart
// Using LocaleProvider
final localeProvider = LocaleProvider();

// Toggle between Arabic and English
localeProvider.toggleLocale();

// Set specific language
localeProvider.setArabic();
localeProvider.setEnglish();

// Set any supported locale
localeProvider.setLocale(Locale('ar', ''));
```

## Adding New Translations

### 1. Add to ARB Files

Add the key-value pair to both `app_ar.arb` and `app_en.arb`:

**app_ar.arb:**

```json
{
  "newFeature": "ميزة جديدة",
  "newFeatureDescription": "وصف الميزة الجديدة"
}
```

**app_en.arb:**

```json
{
  "newFeature": "New Feature",
  "newFeatureDescription": "Description of the new feature"
}
```

### 2. Regenerate Code

```bash
flutter gen-l10n
```

### 3. Use in Code

```dart
Text(AppLocalizations.of(context)!.newFeature)
```

## Translation Placeholders

For dynamic content, use placeholders:

**ARB File:**

```json
{
  "greeting": "مرحبا {name}، لديك {count} حقول",
  "@greeting": {
    "description": "Greeting message with name and field count",
    "placeholders": {
      "name": {
        "type": "String"
      },
      "count": {
        "type": "int"
      }
    }
  }
}
```

**Usage:**

```dart
Text(AppLocalizations.of(context)!.greeting('أحمد', 5))
// Output: "مرحبا أحمد، لديك 5 حقول"
```

## Plural Forms

Handle plurals correctly:

**ARB File:**

```json
{
  "fieldCount": "{count, plural, =0{لا توجد حقول} =1{حقل واحد} other{{count} حقول}}",
  "@fieldCount": {
    "description": "Number of fields",
    "placeholders": {
      "count": {
        "type": "int"
      }
    }
  }
}
```

## Best Practices

1. **Always add to both ARB files** - Maintain parity between Arabic and English
2. **Use descriptive keys** - e.g., `fieldAreaHectares` instead of `fa1`
3. **Group related translations** - Use comment sections in ARB files
4. **Test RTL layout** - Ensure UI works correctly in Arabic
5. **Use semantic keys** - Keys should describe the content, not the UI location
6. **Keep translations natural** - Don't translate word-by-word; use natural phrases
7. **Yemen context** - Use Yemen-specific agricultural terms and currency (Yemeni Rial)

## Yemen-Specific Crops

The localization includes common Yemeni crops:

- قمح (Wheat)
- شعير (Barley)
- ذرة رفيعة (Sorghum)
- قات (Qat)
- بن (Coffee)
- قطن (Cotton)
- And many more...

## Tools & Resources

- **Flutter Intl Package**: https://pub.dev/packages/intl
- **Flutter Localization**: https://docs.flutter.dev/development/accessibility-and-localization/internationalization
- **ARB Format**: https://github.com/google/app-resource-bundle/wiki/ApplicationResourceBundleSpecification

## Translation Statistics

- **Total translation keys**: 1000+
- **Arabic strings**: 1000+
- **English strings**: 1000+
- **Coverage**: All major app features

## Support

For translation issues or to add new languages:

1. Create a new ARB file (e.g., `app_fr.arb` for French)
2. Add the locale to `AppLocalizations.supportedLocales`
3. Run `flutter gen-l10n`
4. Test thoroughly with RTL/LTR as needed

---

**Note**: This localization system is designed specifically for Yemen's agricultural sector, with support for local crops, weather patterns, and farming practices.
