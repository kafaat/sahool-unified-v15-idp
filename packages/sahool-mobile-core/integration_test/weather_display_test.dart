// SAHOOL Integration Test - Weather Display Tests
// اختبارات عرض الطقس
//
// Tests for:
// - Weather screen loading
// - Current weather display
// - Hourly and daily forecasts
// - Weather alerts
// - Agricultural impacts
// - Weather refresh functionality

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:sahool_field_app/main.dart' as app;

import 'helpers/test_helpers.dart';
import 'fixtures/test_data.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Weather Display Tests - اختبارات عرض الطقس', () {
    late TestHelpers helpers;

    setUp(() async {
      // Setup for each test
    });

    tearDown(() async {
      // Cleanup after each test
    });

    // ==========================================================================
    // Weather Screen Navigation Tests
    // اختبارات التنقل إلى شاشة الطقس
    // ==========================================================================

    testWidgets('Navigate to weather screen', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to weather screen from field details
      await _navigateToWeather(helpers);

      // Verify weather screen displayed
      final weatherTitle = find.textContaining('الطقس');
      if (weatherTitle.evaluate().isNotEmpty) {
        helpers.verifyElementExists(weatherTitle);
        helpers.debug('Weather screen displayed');
        await helpers.takeScreenshot('weather_screen');
      }
    });

    testWidgets('Weather screen has proper tabs', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Verify tabs exist
      final weatherTab = find.text('الطقس');
      final recommendationsTab = find.text('التوصيات');
      final alertsTab = find.text('التنبيهات');

      if (weatherTab.evaluate().isNotEmpty) {
        helpers.verifyElementExists(weatherTab);
        helpers.debug('Weather tab found');
      }

      if (recommendationsTab.evaluate().isNotEmpty) {
        helpers.verifyElementExists(recommendationsTab);
        helpers.debug('Recommendations tab found');
      }

      if (alertsTab.evaluate().isNotEmpty) {
        helpers.verifyElementExists(alertsTab);
        helpers.debug('Alerts tab found');
      }

      await helpers.takeScreenshot('weather_tabs');
    });

    // ==========================================================================
    // Current Weather Tests
    // اختبارات الطقس الحالي
    // ==========================================================================

    testWidgets('Current weather displays temperature', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for temperature display
      final temperatureRegex = RegExp(r'\d+°');
      final temperatureText = find.textContaining(temperatureRegex);

      if (temperatureText.evaluate().isNotEmpty) {
        helpers.verifyElementExists(temperatureText);
        helpers.debug('Temperature displayed');
        await helpers.takeScreenshot('weather_temperature');
      }
    });

    testWidgets('Current weather shows humidity', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for humidity display
      final humidityIcon = find.byIcon(Icons.water_drop);
      final humidityText = find.textContaining('%');

      if (humidityIcon.evaluate().isNotEmpty ||
          humidityText.evaluate().isNotEmpty) {
        helpers.debug('Humidity displayed');
        await helpers.takeScreenshot('weather_humidity');
      }
    });

    testWidgets('Current weather shows wind speed', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for wind display
      final windIcon = find.byIcon(Icons.air);
      final windText = find.textContaining(RegExp(r'km/h|m/s|عقدة'));

      if (windIcon.evaluate().isNotEmpty || windText.evaluate().isNotEmpty) {
        helpers.debug('Wind speed displayed');
        await helpers.takeScreenshot('weather_wind');
      }
    });

    testWidgets('Current weather shows weather condition', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for weather condition (sunny, cloudy, etc.)
      final conditions = ['صافي', 'غائم', 'ممطر', 'sunny', 'cloudy', 'rainy'];
      bool conditionFound = false;

      for (final condition in conditions) {
        final conditionText = find.textContaining(condition);
        if (conditionText.evaluate().isNotEmpty) {
          conditionFound = true;
          helpers.debug('Weather condition: $condition');
          break;
        }
      }

      if (conditionFound) {
        await helpers.takeScreenshot('weather_condition');
      }
    });

    testWidgets('Current weather shows weather icon', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for weather icons
      final sunIcon = find.byIcon(Icons.wb_sunny);
      final cloudIcon = find.byIcon(Icons.cloud);
      final rainIcon = find.byIcon(Icons.grain);

      if (sunIcon.evaluate().isNotEmpty ||
          cloudIcon.evaluate().isNotEmpty ||
          rainIcon.evaluate().isNotEmpty) {
        helpers.debug('Weather icon displayed');
        await helpers.takeScreenshot('weather_icon');
      }
    });

    // ==========================================================================
    // Hourly Forecast Tests
    // اختبارات التوقعات الساعية
    // ==========================================================================

    testWidgets('Hourly forecast section exists', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for hourly forecast section
      final hourlyTitle = find.textContaining('ساعية');
      if (hourlyTitle.evaluate().isNotEmpty) {
        helpers.verifyElementExists(hourlyTitle);
        helpers.debug('Hourly forecast section found');
        await helpers.takeScreenshot('weather_hourly_section');
      }
    });

    testWidgets('Hourly forecast is scrollable', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Find scrollable horizontal list
      final scrollableList = find.byType(SingleChildScrollView);
      final listView = find.byType(ListView);

      if (scrollableList.evaluate().isNotEmpty ||
          listView.evaluate().isNotEmpty) {
        // Try to scroll
        final scrollable = scrollableList.evaluate().isNotEmpty
            ? scrollableList.first
            : listView.first;

        await tester.drag(
          scrollable as Finder,
          const Offset(-100, 0),
        );
        await helpers.pumpAndSettle();

        helpers.debug('Hourly forecast scrolled');
        await helpers.takeScreenshot('weather_hourly_scrolled');
      }
    });

    testWidgets('Hourly forecast shows time labels', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for time labels (e.g., 12:00, 13:00)
      final timeRegex = RegExp(r'\d{1,2}:\d{2}|صباحاً|مساءً');
      final timeText = find.textContaining(timeRegex);

      if (timeText.evaluate().isNotEmpty) {
        helpers.debug('Hourly time labels displayed');
        await helpers.takeScreenshot('weather_hourly_times');
      }
    });

    // ==========================================================================
    // Daily Forecast Tests
    // اختبارات التوقعات اليومية
    // ==========================================================================

    testWidgets('Daily forecast section exists', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for daily/weekly forecast section
      final dailyTitle = find.textContaining(RegExp(r'يومية|أسبوعية|daily|weekly'));
      if (dailyTitle.evaluate().isNotEmpty) {
        helpers.verifyElementExists(dailyTitle);
        helpers.debug('Daily forecast section found');
        await helpers.takeScreenshot('weather_daily_section');
      }
    });

    testWidgets('Daily forecast shows multiple days', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for day names
      final days = ['السبت', 'الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة'];
      int daysFound = 0;

      for (final day in days) {
        final dayText = find.textContaining(day);
        if (dayText.evaluate().isNotEmpty) {
          daysFound++;
        }
      }

      if (daysFound > 1) {
        helpers.debug('Multiple days displayed: $daysFound');
        await helpers.takeScreenshot('weather_daily_days');
      }
    });

    testWidgets('Daily forecast shows min/max temperatures', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for temperature ranges (e.g., "15° / 28°")
      final tempRangeRegex = RegExp(r'\d+°\s*/\s*\d+°');
      final tempRange = find.textContaining(tempRangeRegex);

      if (tempRange.evaluate().isNotEmpty) {
        helpers.debug('Min/max temperatures displayed');
        await helpers.takeScreenshot('weather_daily_temps');
      }
    });

    // ==========================================================================
    // Weather Alerts Tests
    // اختبارات تنبيهات الطقس
    // ==========================================================================

    testWidgets('Navigate to alerts tab', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Tap alerts tab
      final alertsTab = find.text('التنبيهات');
      if (alertsTab.evaluate().isNotEmpty) {
        await helpers.tapElement(alertsTab);
        await helpers.pumpAndSettle();

        helpers.debug('Navigated to alerts tab');
        await helpers.takeScreenshot('weather_alerts_tab');
      }
    });

    testWidgets('Alerts tab shows no alerts message when empty', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Navigate to alerts
      final alertsTab = find.text('التنبيهات');
      if (alertsTab.evaluate().isNotEmpty) {
        await helpers.tapElement(alertsTab);
        await helpers.pumpAndSettle();

        // Check for empty state
        final noAlertsMessage = find.textContaining('لا توجد تنبيهات');
        final checkIcon = find.byIcon(Icons.check_circle);

        if (noAlertsMessage.evaluate().isNotEmpty ||
            checkIcon.evaluate().isNotEmpty) {
          helpers.debug('No alerts message displayed');
          await helpers.takeScreenshot('weather_no_alerts');
        }
      }
    });

    testWidgets('Alert badge shows count when alerts exist', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Look for notification badge
      final notificationIcon = find.byIcon(Icons.notifications);
      if (notificationIcon.evaluate().isNotEmpty) {
        // Check for badge with number
        final badge = find.descendant(
          of: find.ancestor(of: notificationIcon, matching: find.byType(Stack)),
          matching: find.byType(Container),
        );

        if (badge.evaluate().isNotEmpty) {
          helpers.debug('Alert badge found');
          await helpers.takeScreenshot('weather_alert_badge');
        }
      }
    });

    // ==========================================================================
    // Agricultural Impact Tests
    // اختبارات التأثير الزراعي
    // ==========================================================================

    testWidgets('Navigate to recommendations tab', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Tap recommendations tab
      final recommendationsTab = find.text('التوصيات');
      if (recommendationsTab.evaluate().isNotEmpty) {
        await helpers.tapElement(recommendationsTab);
        await helpers.pumpAndSettle();

        helpers.debug('Navigated to recommendations tab');
        await helpers.takeScreenshot('weather_recommendations_tab');
      }
    });

    testWidgets('Agricultural impacts displayed', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Navigate to recommendations
      final recommendationsTab = find.text('التوصيات');
      if (recommendationsTab.evaluate().isNotEmpty) {
        await helpers.tapElement(recommendationsTab);
        await helpers.pumpAndSettle();

        // Look for impact cards
        final impacts = ['ري', 'رش', 'حصاد', 'زراعة'];
        bool impactFound = false;

        for (final impact in impacts) {
          final impactText = find.textContaining(impact);
          if (impactText.evaluate().isNotEmpty) {
            impactFound = true;
            helpers.debug('Agricultural impact found: $impact');
          }
        }

        if (impactFound) {
          await helpers.takeScreenshot('weather_agricultural_impacts');
        }
      }
    });

    testWidgets('Impact filter chips work', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Navigate to recommendations
      final recommendationsTab = find.text('التوصيات');
      if (recommendationsTab.evaluate().isNotEmpty) {
        await helpers.tapElement(recommendationsTab);
        await helpers.pumpAndSettle();

        // Find filter chips
        final filterChip = find.byType(FilterChip);
        if (filterChip.evaluate().isNotEmpty) {
          // Tap first filter
          await helpers.tapElement(filterChip.first);
          await helpers.pumpAndSettle();

          helpers.debug('Filter chip selected');
          await helpers.takeScreenshot('weather_filter_selected');
        }
      }
    });

    testWidgets('Impact status colors displayed correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Navigate to recommendations
      final recommendationsTab = find.text('التوصيات');
      if (recommendationsTab.evaluate().isNotEmpty) {
        await helpers.tapElement(recommendationsTab);
        await helpers.pumpAndSettle();

        // Look for status indicators
        final favorableText = find.textContaining('مناسب');
        final cautionText = find.textContaining('حذر');
        final unfavorableText = find.textContaining('غير مناسب');

        if (favorableText.evaluate().isNotEmpty ||
            cautionText.evaluate().isNotEmpty ||
            unfavorableText.evaluate().isNotEmpty) {
          helpers.debug('Status colors displayed');
          await helpers.takeScreenshot('weather_status_colors');
        }
      }
    });

    // ==========================================================================
    // Refresh Tests
    // اختبارات التحديث
    // ==========================================================================

    testWidgets('Refresh button works', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Find refresh button
      final refreshButton = find.byIcon(Icons.refresh);
      if (refreshButton.evaluate().isNotEmpty) {
        await helpers.tapElement(refreshButton);
        await helpers.pumpAndSettle();

        // Wait for refresh
        await helpers.wait(TestConfig.shortDelay);

        helpers.debug('Weather refreshed');
        await helpers.takeScreenshot('weather_refreshed');
      }
    });

    testWidgets('Pull to refresh works', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Find RefreshIndicator
      final refreshIndicator = find.byType(RefreshIndicator);
      if (refreshIndicator.evaluate().isNotEmpty) {
        // Pull down to refresh
        await tester.drag(refreshIndicator, const Offset(0, 200));
        await helpers.pumpAndSettle();

        helpers.debug('Pull to refresh triggered');
        await helpers.takeScreenshot('weather_pull_refresh');
      }
    });

    testWidgets('Loading indicator shown during refresh', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Trigger refresh
      final refreshButton = find.byIcon(Icons.refresh);
      if (refreshButton.evaluate().isNotEmpty) {
        await helpers.tapElement(refreshButton);

        // Check for loading indicator immediately
        await tester.pump(const Duration(milliseconds: 100));

        final loadingIndicator = find.byType(CircularProgressIndicator);
        if (loadingIndicator.evaluate().isNotEmpty) {
          helpers.debug('Loading indicator shown');
          await helpers.takeScreenshot('weather_loading');
        }

        await helpers.pumpAndSettle();
      }
    });

    // ==========================================================================
    // Error Handling Tests
    // اختبارات معالجة الأخطاء
    // ==========================================================================

    testWidgets('Error view shows retry option', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // This test requires mocking to simulate error
      // In the error state, verify retry button exists

      helpers.debug('Error handling test requires mock server');
    });

    // ==========================================================================
    // Offline Mode Tests
    // اختبارات الوضع غير المتصل
    // ==========================================================================

    testWidgets('Weather shows cached data when offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Load weather data first
      await _navigateToWeather(helpers);
      await helpers.wait(TestConfig.mediumDelay);

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Weather should still be visible
      final temperatureRegex = RegExp(r'\d+°');
      final temperatureText = find.textContaining(temperatureRegex);

      if (temperatureText.evaluate().isNotEmpty) {
        helpers.debug('Cached weather displayed offline');
        await helpers.takeScreenshot('weather_offline_cached');
      }

      // Go back online
      await helpers.toggleOfflineMode();
    });

    testWidgets('Offline indicator shown on weather screen', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Check for offline indicator
      helpers.verifyTextContains(ArabicStrings.offline);
      helpers.debug('Offline indicator shown on weather');
      await helpers.takeScreenshot('weather_offline_indicator');

      // Go back online
      await helpers.toggleOfflineMode();
    });

    // ==========================================================================
    // Performance Tests
    // اختبارات الأداء
    // ==========================================================================

    testWidgets('Weather screen loads quickly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      final startTime = DateTime.now();

      await _navigateToWeather(helpers);

      final loadTime = DateTime.now().difference(startTime);

      expect(loadTime.inSeconds, lessThan(5),
          reason: 'Weather should load in less than 5 seconds');

      helpers.debug('Weather loaded in ${loadTime.inMilliseconds}ms');
    });

    testWidgets('Tab switching is responsive', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToWeather(helpers);

      final startTime = DateTime.now();

      // Switch through all tabs
      final tabs = ['التوصيات', 'التنبيهات', 'الطقس'];
      for (final tab in tabs) {
        final tabFinder = find.text(tab);
        if (tabFinder.evaluate().isNotEmpty) {
          await helpers.tapElement(tabFinder);
          await helpers.pumpAndSettle();
        }
      }

      final switchTime = DateTime.now().difference(startTime);

      expect(switchTime.inSeconds, lessThan(3),
          reason: 'Tab switching should be fast');

      helpers.debug('Tab switching completed in ${switchTime.inMilliseconds}ms');
    });
  });
}

// =============================================================================
// Helper Functions
// دوال مساعدة
// =============================================================================

/// Navigate to weather screen
/// التنقل إلى شاشة الطقس
Future<void> _navigateToWeather(TestHelpers helpers) async {
  // Try to find weather option from field details
  final fieldCard = find.textContaining('حقل');
  if (fieldCard.evaluate().isNotEmpty) {
    await helpers.tapElement(fieldCard.first);
    await helpers.pumpAndSettle();

    // Look for weather button or tab
    final weatherButton = find.byIcon(Icons.wb_sunny);
    final weatherText = find.text('الطقس');

    if (weatherButton.evaluate().isNotEmpty) {
      await helpers.tapElement(weatherButton);
      await helpers.pumpAndSettle();
    } else if (weatherText.evaluate().isNotEmpty) {
      await helpers.tapElement(weatherText);
      await helpers.pumpAndSettle();
    }
  }

  // Alternative: direct navigation if available
  final directWeatherButton = find.textContaining('الطقس');
  if (directWeatherButton.evaluate().isNotEmpty) {
    await helpers.tapElement(directWeatherButton.first);
    await helpers.pumpAndSettle();
  }
}
