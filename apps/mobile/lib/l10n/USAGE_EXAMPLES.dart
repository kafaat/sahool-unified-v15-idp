// SAHOOL Mobile App - Localization Usage Examples
// This file demonstrates how to use the localization system

import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'l10n.dart';

// ============================================================================
// EXAMPLE 1: Basic Text Localization
// ============================================================================

class BasicLocalizationExample extends StatelessWidget {
  const BasicLocalizationExample({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Get localization instance
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.appName), // "سهول" or "SAHOOL"
      ),
      body: Column(
        children: [
          Text(l10n.home), // "الرئيسية" or "Home"
          Text(l10n.fields), // "الحقول" or "Fields"
          Text(l10n.weather), // "الطقس" or "Weather"
          Text(l10n.satellite), // "الأقمار الصناعية" or "Satellite"
        ],
      ),
    );
  }
}

// ============================================================================
// EXAMPLE 2: Navigation Menu with Localization
// ============================================================================

class LocalizedNavigationMenu extends StatelessWidget {
  const LocalizedNavigationMenu({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Drawer(
      child: ListView(
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(color: Colors.green),
            child: Text(
              l10n.appTitle,
              style: const TextStyle(color: Colors.white, fontSize: 24),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.home),
            title: Text(l10n.home),
            onTap: () => Navigator.pop(context),
          ),
          ListTile(
            leading: const Icon(Icons.agriculture),
            title: Text(l10n.fields),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.cloud),
            title: Text(l10n.weather),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.satellite),
            title: Text(l10n.satellite),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.map),
            title: Text(l10n.vra),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.thermostat),
            title: Text(l10n.gdd),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.water_drop),
            title: Text(l10n.spray),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.repeat),
            title: Text(l10n.rotation),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.trending_up),
            title: Text(l10n.profitability),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.inventory),
            title: Text(l10n.inventory),
            onTap: () {},
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// EXAMPLE 3: RTL-Aware Layout
// ============================================================================

class RTLAwareLayout extends StatelessWidget {
  const RTLAwareLayout({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final layout = LocalizedLayout(context);

    return Container(
      // Direction-aware padding
      padding: layout.edgeInsets(
        start: 16, // Right in RTL, Left in LTR
        end: 8, // Left in RTL, Right in LTR
        top: 12,
        bottom: 12,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Text with appropriate alignment
          Text(
            l10n.fieldDetails,
            textAlign: layout.startAlign, // Right align in RTL
          ),
          const SizedBox(height: 8),
          // Row with directional icon
          Row(
            children: [
              DirectionalIcon(
                Icons.arrow_forward, // Flips in RTL
                color: Colors.blue,
              ),
              const SizedBox(width: 8),
              Text(l10n.next),
            ],
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// EXAMPLE 4: Number Formatting
// ============================================================================

class NumberFormattingExample extends StatelessWidget {
  const NumberFormattingExample({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final numberFormat = LocalizedNumberFormat(Localizations.localeOf(context));

    return Column(
      children: [
        // Field area
        Text(
          '${l10n.fieldArea}: ${numberFormat.format(25.5)} ${l10n.hectares}',
          // Arabic: "مساحة الحقل: ٢٥.٥ هكتار"
          // English: "Field Area: 25.5 Hectares"
        ),

        // Price
        Text(
          '${l10n.price}: ${numberFormat.formatCurrency(150000)}',
          // Arabic: "السعر: ١٥٠٠٠٠.٠٠ ريال"
          // English: "Price: YER 150000.00"
        ),

        // Percentage
        Text(
          '${l10n.humidity}: ${numberFormat.formatPercentage(75.5)}',
          // Arabic: "الرطوبة: %٧٥.٥"
          // English: "Humidity: 75.5%"
        ),
      ],
    );
  }
}

// ============================================================================
// EXAMPLE 5: Language Switcher
// ============================================================================

class LanguageSwitcher extends StatefulWidget {
  const LanguageSwitcher({Key? key}) : super(key: key);

  @override
  State<LanguageSwitcher> createState() => _LanguageSwitcherState();
}

class _LanguageSwitcherState extends State<LanguageSwitcher> {
  late LocaleProvider localeProvider;

  @override
  void initState() {
    super.initState();
    localeProvider = LocaleProvider();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return PopupMenuButton<Locale>(
      icon: const Icon(Icons.language),
      tooltip: l10n.language,
      onSelected: (Locale locale) {
        localeProvider.setLocale(locale);
        // You would typically use a state management solution
        // to rebuild the app with the new locale
      },
      itemBuilder: (BuildContext context) {
        return [
          PopupMenuItem(
            value: const Locale('ar', ''),
            child: Row(
              children: [
                if (localeProvider.locale.languageCode == 'ar')
                  const Icon(Icons.check, color: Colors.green),
                const SizedBox(width: 8),
                const Text('العربية'),
              ],
            ),
          ),
          PopupMenuItem(
            value: const Locale('en', ''),
            child: Row(
              children: [
                if (localeProvider.locale.languageCode == 'en')
                  const Icon(Icons.check, color: Colors.green),
                const SizedBox(width: 8),
                const Text('English'),
              ],
            ),
          ),
        ];
      },
    );
  }
}

// ============================================================================
// EXAMPLE 6: Form with Localized Labels and Validation
// ============================================================================

class LocalizedForm extends StatefulWidget {
  const LocalizedForm({Key? key}) : super(key: key);

  @override
  State<LocalizedForm> createState() => _LocalizedFormState();
}

class _LocalizedFormState extends State<LocalizedForm> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Form(
      key: _formKey,
      child: Column(
        children: [
          // Name field
          TextFormField(
            controller: _nameController,
            decoration: InputDecoration(
              labelText: l10n.fullName,
              hintText: l10n.fullName,
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return l10n.requiredField;
              }
              return null;
            },
          ),

          // Email field
          TextFormField(
            controller: _emailController,
            decoration: InputDecoration(
              labelText: l10n.email,
              hintText: l10n.emailAddress,
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return l10n.requiredField;
              }
              if (!value.contains('@')) {
                return l10n.invalidEmail;
              }
              return null;
            },
          ),

          // Submit button
          ElevatedButton(
            onPressed: () {
              if (_formKey.currentState!.validate()) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(l10n.savedSuccessfully)),
                );
              }
            },
            child: Text(l10n.submit),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    super.dispose();
  }
}

// ============================================================================
// EXAMPLE 7: Dialog with Localized Messages
// ============================================================================

void showLocalizedDialog(BuildContext context) {
  final l10n = AppLocalizations.of(context)!;

  showDialog(
    context: context,
    builder: (BuildContext context) {
      return AlertDialog(
        title: Text(l10n.confirmDelete),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.confirmDeleteMessage),
            const SizedBox(height: 8),
            Text(
              l10n.cannotBeUndone,
              style: const TextStyle(
                color: Colors.red,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(l10n.cancel),
          ),
          ElevatedButton(
            onPressed: () {
              // Perform delete action
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(l10n.deletedSuccessfully)),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: Text(l10n.delete),
          ),
        ],
      );
    },
  );
}

// ============================================================================
// EXAMPLE 8: Weather Widget with Localization
// ============================================================================

class WeatherWidget extends StatelessWidget {
  final double temperature;
  final double humidity;
  final double windSpeed;
  final String condition;

  const WeatherWidget({
    Key? key,
    required this.temperature,
    required this.humidity,
    required this.windSpeed,
    required this.condition,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final numberFormat = LocalizedNumberFormat(Localizations.localeOf(context));

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.currentWeather,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildWeatherItem(
                  context,
                  Icons.thermostat,
                  l10n.temperature,
                  '${numberFormat.format(temperature)}°${l10n.celsius}',
                ),
                _buildWeatherItem(
                  context,
                  Icons.water_drop,
                  l10n.humidity,
                  numberFormat.formatPercentage(humidity),
                ),
                _buildWeatherItem(
                  context,
                  Icons.air,
                  l10n.windSpeed,
                  '${numberFormat.format(windSpeed)} ${l10n.kmPerHour}',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeatherItem(
    BuildContext context,
    IconData icon,
    String label,
    String value,
  ) {
    return Column(
      children: [
        Icon(icon, size: 32, color: Theme.of(context).primaryColor),
        const SizedBox(height: 8),
        Text(label, style: const TextStyle(fontSize: 12)),
        Text(
          value,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}

// ============================================================================
// EXAMPLE 9: Crop List with Yemen-Specific Crops
// ============================================================================

class YemenCropsList extends StatelessWidget {
  const YemenCropsList({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    final crops = [
      l10n.wheat,
      l10n.barley,
      l10n.sorghum,
      l10n.qat,
      l10n.coffee,
      l10n.cotton,
      l10n.sesame,
      l10n.tomato,
      l10n.potato,
      l10n.onion,
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.mainCrops,
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        ...crops.map(
          (crop) => ListTile(
            leading: const Icon(Icons.eco),
            title: Text(crop),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
        ),
      ],
    );
  }
}

// ============================================================================
// EXAMPLE 10: Error Handling with Localized Messages
// ============================================================================

class ErrorHandlingExample extends StatelessWidget {
  const ErrorHandlingExample({Key? key}) : super(key: key);

  void handleError(BuildContext context, Exception error) {
    final l10n = AppLocalizations.of(context)!;
    String message;

    if (error is NetworkException) {
      message = l10n.networkError;
    } else if (error is ValidationException) {
      message = l10n.validationError;
    } else if (error is AuthException) {
      message = l10n.authenticationFailed;
    } else {
      message = l10n.unknownError;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        action: SnackBarAction(
          label: l10n.retry,
          onPressed: () {
            // Retry action
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return const Placeholder();
  }
}

// Custom exceptions for demonstration
class NetworkException implements Exception {}

class ValidationException implements Exception {}

class AuthException implements Exception {}
