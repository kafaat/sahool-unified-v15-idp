# SAHOOL Mobile App - Localization Integration Guide

This guide shows how to integrate the Arabic/English localization into your existing SAHOOL mobile app.

## Step 1: Generate Localization Code

Run this command in the mobile app directory:

```bash
cd /home/user/sahool-unified-v15-idp/apps/mobile
flutter gen-l10n
```

This creates generated files in `lib/generated/l10n/`.

## Step 2: Update app.dart

Find your `SahoolFieldApp` class in `/home/user/sahool-unified-v15-idp/apps/mobile/lib/app.dart` and update it:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'l10n/l10n.dart';

class SahoolFieldApp extends StatelessWidget {
  const SahoolFieldApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      // Existing settings
      title: 'SAHOOL',
      debugShowCheckedModeBanner: false,

      // ADD THESE LOCALIZATION SETTINGS
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      localeResolutionCallback: AppLocalizations.localeResolutionCallback,
      locale: const Locale('ar', ''), // Default to Arabic for Yemen

      // Theme with Arabic font support
      theme: ThemeData(
        primarySwatch: Colors.green,
        fontFamily: 'IBMPlexSansArabic', // Already configured in pubspec.yaml
        useMaterial3: true,
      ),

      // Your existing routing/navigation
      // ... rest of your app configuration
    );
  }
}
```

## Step 3: Use Localization in Existing Screens

### Example: Update Home Screen

**Before (hardcoded strings):**
```dart
class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Home')),
      body: Text('Welcome to SAHOOL'),
    );
  }
}
```

**After (localized):**
```dart
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(title: Text(l10n.home)),
      body: Text(l10n.welcomeMessage),
    );
  }
}
```

### Example: Update Navigation Drawer

**Before:**
```dart
Drawer(
  child: ListView(
    children: [
      ListTile(title: Text('Fields'), onTap: () {}),
      ListTile(title: Text('Weather'), onTap: () {}),
      ListTile(title: Text('Satellite'), onTap: () {}),
    ],
  ),
)
```

**After:**
```dart
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

Drawer(
  child: ListView(
    children: [
      DrawerHeader(
        child: Text(AppLocalizations.of(context)!.appName),
      ),
      ListTile(
        leading: Icon(Icons.agriculture),
        title: Text(AppLocalizations.of(context)!.fields),
        onTap: () {},
      ),
      ListTile(
        leading: Icon(Icons.cloud),
        title: Text(AppLocalizations.of(context)!.weather),
        onTap: () {},
      ),
      ListTile(
        leading: Icon(Icons.satellite),
        title: Text(AppLocalizations.of(context)!.satellite),
        onTap: () {},
      ),
    ],
  ),
)
```

## Step 4: Add Language Switcher

Add this to your settings screen:

```dart
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LanguageSettings extends StatefulWidget {
  @override
  State<LanguageSettings> createState() => _LanguageSettingsState();
}

class _LanguageSettingsState extends State<LanguageSettings> {
  String _currentLanguage = 'ar';

  @override
  void initState() {
    super.initState();
    _loadLanguage();
  }

  Future<void> _loadLanguage() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _currentLanguage = prefs.getString('language') ?? 'ar';
    });
  }

  Future<void> _changeLanguage(String languageCode) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('language', languageCode);
    setState(() {
      _currentLanguage = languageCode;
    });
    // Restart app or use state management to rebuild with new locale
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return ListTile(
      leading: Icon(Icons.language),
      title: Text(l10n.language),
      subtitle: Text(_currentLanguage == 'ar' ? 'العربية' : 'English'),
      trailing: Icon(Icons.chevron_right),
      onTap: () {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: Text(l10n.language),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                RadioListTile<String>(
                  title: Text('العربية'),
                  value: 'ar',
                  groupValue: _currentLanguage,
                  onChanged: (value) {
                    Navigator.pop(context);
                    _changeLanguage(value!);
                  },
                ),
                RadioListTile<String>(
                  title: Text('English'),
                  value: 'en',
                  groupValue: _currentLanguage,
                  onChanged: (value) {
                    Navigator.pop(context);
                    _changeLanguage(value!);
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
```

## Step 5: Common Replacements

Here are common strings to replace throughout your app:

| Hardcoded | Localized Key |
|-----------|---------------|
| "Home" | `l10n.home` |
| "Fields" | `l10n.fields` |
| "Weather" | `l10n.weather` |
| "Satellite" | `l10n.satellite` |
| "NDVI" | `l10n.ndvi` |
| "VRA" | `l10n.vra` |
| "GDD" | `l10n.gdd` |
| "Spray" | `l10n.spray` |
| "Rotation" | `l10n.rotation` |
| "Profitability" | `l10n.profitability` |
| "Inventory" | `l10n.inventory` |
| "Settings" | `l10n.settings` |
| "Save" | `l10n.save` |
| "Cancel" | `l10n.cancel` |
| "Delete" | `l10n.delete` |
| "Edit" | `l10n.edit` |
| "Loading..." | `l10n.loading` |
| "Error" | `l10n.error_` |
| "Success" | `l10n.success` |

## Step 6: Test RTL Layout

1. Run app with Arabic:
   ```bash
   flutter run --dart-define=LOCALE=ar
   ```

2. Check these items:
   - Text aligns to the right
   - Icons mirror correctly
   - Navigation drawer opens from right
   - Back button points left
   - Arabic numerals display correctly

3. Test language switching:
   - Go to Settings
   - Change language
   - Verify UI updates

## Step 7: Replace Forms and Validation

**Before:**
```dart
TextFormField(
  decoration: InputDecoration(labelText: 'Name'),
  validator: (value) {
    if (value?.isEmpty ?? true) {
      return 'This field is required';
    }
    return null;
  },
)
```

**After:**
```dart
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

TextFormField(
  decoration: InputDecoration(
    labelText: AppLocalizations.of(context)!.fullName,
  ),
  validator: (value) {
    if (value?.isEmpty ?? true) {
      return AppLocalizations.of(context)!.requiredField;
    }
    return null;
  },
)
```

## Step 8: Update Error Messages

**Before:**
```dart
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(content: Text('Network error occurred')),
);
```

**After:**
```dart
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text(AppLocalizations.of(context)!.networkError),
  ),
);
```

## Step 9: Format Numbers and Currency

**Before:**
```dart
Text('Area: ${area.toStringAsFixed(2)} hectares')
Text('Price: YER ${price.toStringAsFixed(2)}')
```

**After:**
```dart
import 'l10n/l10n.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

final l10n = AppLocalizations.of(context)!;
final numberFormat = LocalizedNumberFormat(Localizations.localeOf(context));

Text('${l10n.fieldArea}: ${numberFormat.format(area, decimalDigits: 2)} ${l10n.hectares}')
Text('${l10n.price}: ${numberFormat.formatCurrency(price)}')
```

## Step 10: Quick Search & Replace

Use these regex patterns to find hardcoded strings:

1. Find hardcoded Text widgets:
   ```
   Text\s*\(\s*['"]([^'"]+)['"]\s*\)
   ```

2. Find hardcoded labels in TextFormField:
   ```
   labelText:\s*['"]([^'"]+)['"]
   ```

3. Find hardcoded AppBar titles:
   ```
   AppBar\s*\(.*?title:\s*Text\s*\(\s*['"]([^'"]+)['"]
   ```

## Testing Checklist

- [ ] Run `flutter gen-l10n` successfully
- [ ] App builds without errors
- [ ] Arabic text displays correctly
- [ ] English text displays correctly
- [ ] RTL layout works (text aligns right, icons mirror)
- [ ] Language switcher works
- [ ] Numbers format correctly (Arabic/English digits)
- [ ] Currency displays correctly (ريال يمني)
- [ ] Navigation menu is localized
- [ ] Forms and validation messages are localized
- [ ] Error messages are localized
- [ ] All screens tested in both languages

## Troubleshooting

### Issue: Generated files not found
**Solution:** Run `flutter gen-l10n` and restart IDE

### Issue: Localization not working
**Solution:** Check that you imported:
```dart
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
```

### Issue: RTL layout broken
**Solution:** Ensure MaterialApp has:
```dart
localizationsDelegates: AppLocalizations.localizationsDelegates,
```

### Issue: Language doesn't persist
**Solution:** Use SharedPreferences to save and load language preference

## Complete Integration Example

See `/home/user/sahool-unified-v15-idp/apps/mobile/lib/l10n/USAGE_EXAMPLES.dart` for 10 complete examples including:
1. Basic localization
2. Navigation menu
3. RTL-aware layouts
4. Number formatting
5. Language switcher
6. Forms and validation
7. Dialogs
8. Weather widgets
9. Crop lists
10. Error handling

## Resources

- **Full Documentation**: `lib/l10n/README.md`
- **Usage Examples**: `lib/l10n/USAGE_EXAMPLES.dart`
- **Setup Guide**: `LOCALIZATION_SETUP.md`
- **Translation Files**: `lib/l10n/app_ar.arb`, `lib/l10n/app_en.arb`

## Summary

1. ✅ Run `flutter gen-l10n`
2. ✅ Update `app.dart` with localization delegates
3. ✅ Import `AppLocalizations` in screens
4. ✅ Replace hardcoded strings with `l10n.key`
5. ✅ Add language switcher
6. ✅ Test RTL layout
7. ✅ Format numbers with `LocalizedNumberFormat`
8. ✅ Verify all features in both languages

**Your app is now ready for Yemeni farmers with full Arabic support! 🌾🇾🇪**
