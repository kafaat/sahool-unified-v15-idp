/// SAHOOL Integration Test - Helper Functions
/// دوال مساعدة للاختبارات
library;

import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import '../fixtures/test_data.dart';

/// Helper class for common test operations
/// صنف مساعد للعمليات الشائعة في الاختبارات
class TestHelpers {
  final WidgetTester tester;
  final IntegrationTestWidgetsFlutterBinding binding;

  TestHelpers(this.tester, this.binding);

  // ============================================================================
  // Authentication Helpers
  // دوال مساعدة للمصادقة
  // ============================================================================

  /// Login with test credentials
  /// تسجيل الدخول ببيانات الاختبار
  Future<void> login({
    String? email,
    String? password,
    bool useBiometric = false,
  }) async {
    final testEmail = email ?? TestUsers.validEmail;
    final testPassword = password ?? TestUsers.validPassword;

    // Wait for login screen
    await waitForElement(find.text(ArabicStrings.login));

    if (useBiometric) {
      // Look for biometric login button
      final biometricButton = find.byIcon(Icons.fingerprint);
      if (biometricButton.evaluate().isNotEmpty) {
        await tapElement(biometricButton);
        await pumpAndSettle();
        return;
      }
    }

    // Enter email/phone
    final emailField = find.byType(TextField).first;
    await enterText(emailField, testEmail);
    await pumpAndSettle();

    // Enter password
    final passwordField = find.byType(TextField).last;
    await enterText(passwordField, testPassword);
    await pumpAndSettle();

    // Tap login button
    final loginButton = find.widgetWithText(ElevatedButton, ArabicStrings.login);
    await tapElement(loginButton);

    // Wait for home screen
    await waitForElement(find.text(ArabicStrings.home), timeout: TestConfig.longTimeout);
    await pumpAndSettle();
  }

  /// Logout from the app
  /// تسجيل الخروج من التطبيق
  Future<void> logout() async {
    // Navigate to More section
    await navigateToBottomNavItem(ArabicStrings.more);
    await pumpAndSettle();

    // Scroll to logout button
    await scrollUntilVisible(
      find.text(ArabicStrings.logout),
      scrollable: find.byType(ListView),
    );

    // Tap logout
    await tapElement(find.text(ArabicStrings.logout));
    await pumpAndSettle();

    // Confirm logout if dialog appears
    final confirmButton = find.text(ArabicStrings.confirm);
    if (confirmButton.evaluate().isNotEmpty) {
      await tapElement(confirmButton);
      await pumpAndSettle();
    }

    // Wait for login screen
    await waitForElement(find.text(ArabicStrings.login));
  }

  // ============================================================================
  // Navigation Helpers
  // دوال مساعدة للتنقل
  // ============================================================================

  /// Navigate to bottom navigation item by label
  /// التنقل إلى عنصر في شريط التنقل السفلي
  Future<void> navigateToBottomNavItem(String label) async {
    final navItem = find.text(label);
    await tapElement(navItem);
    await pumpAndSettle();
  }

  /// Navigate back
  /// الرجوع للصفحة السابقة
  Future<void> navigateBack() async {
    final backButton = find.byType(BackButton);
    if (backButton.evaluate().isNotEmpty) {
      await tapElement(backButton);
    } else {
      // Try AppBar back arrow
      final backArrow = find.byIcon(Icons.arrow_back);
      if (backArrow.evaluate().isNotEmpty) {
        await tapElement(backArrow);
      }
    }
    await pumpAndSettle();
  }

  /// Open drawer/menu
  /// فتح القائمة الجانبية
  Future<void> openDrawer() async {
    final scaffoldState = tester.state<ScaffoldState>(find.byType(Scaffold));
    scaffoldState.openDrawer();
    await pumpAndSettle();
  }

  // ============================================================================
  // Widget Interaction Helpers
  // دوال مساعدة للتفاعل مع العناصر
  // ============================================================================

  /// Tap on an element
  /// النقر على عنصر
  Future<void> tapElement(Finder finder, {int index = 0}) async {
    await tester.tap(finder.at(index));
    await pumpAndSettle();
  }

  /// Long press on an element
  /// الضغط الطويل على عنصر
  Future<void> longPressElement(Finder finder, {int index = 0}) async {
    await tester.longPress(finder.at(index));
    await pumpAndSettle();
  }

  /// Enter text into a text field
  /// إدخال نص في حقل نصي
  Future<void> enterText(Finder finder, String text, {int index = 0}) async {
    await tester.enterText(finder.at(index), text);
    await pumpAndSettle();
  }

  /// Clear text from a text field
  /// مسح النص من حقل نصي
  Future<void> clearText(Finder finder, {int index = 0}) async {
    await tester.enterText(finder.at(index), '');
    await pumpAndSettle();
  }

  /// Scroll until widget is visible
  /// التمرير حتى ظهور العنصر
  Future<void> scrollUntilVisible(
    Finder finder, {
    required Finder scrollable,
    double delta = 300,
    int maxScrolls = 50,
  }) async {
    await tester.scrollUntilVisible(
      finder,
      delta,
      scrollable: scrollable,
      maxScrolls: maxScrolls,
    );
    await pumpAndSettle();
  }

  /// Scroll down
  /// التمرير للأسفل
  Future<void> scrollDown({double pixels = 300}) async {
    await tester.drag(find.byType(ListView).first, Offset(0, -pixels));
    await pumpAndSettle();
  }

  /// Scroll up
  /// التمرير للأعلى
  Future<void> scrollUp({double pixels = 300}) async {
    await tester.drag(find.byType(ListView).first, Offset(0, pixels));
    await pumpAndSettle();
  }

  /// Swipe left (RTL: swipe to next)
  /// التمرير لليسار
  Future<void> swipeLeft(Finder finder) async {
    await tester.drag(finder, const Offset(-300, 0));
    await pumpAndSettle();
  }

  /// Swipe right (RTL: swipe to previous)
  /// التمرير لليمين
  Future<void> swipeRight(Finder finder) async {
    await tester.drag(finder, const Offset(300, 0));
    await pumpAndSettle();
  }

  // ============================================================================
  // Wait & Timing Helpers
  // دوال مساعدة للانتظار والتوقيت
  // ============================================================================

  /// Wait for element to appear
  /// الانتظار حتى ظهور عنصر
  Future<void> waitForElement(
    Finder finder, {
    Duration timeout = TestConfig.mediumTimeout,
  }) async {
    await tester.pumpAndSettle(timeout);
    expect(finder, findsOneWidget);
  }

  /// Wait for element to disappear
  /// الانتظار حتى اختفاء عنصر
  Future<void> waitForElementToDisappear(
    Finder finder, {
    Duration timeout = TestConfig.mediumTimeout,
  }) async {
    final endTime = DateTime.now().add(timeout);
    while (DateTime.now().isBefore(endTime)) {
      await tester.pump(const Duration(milliseconds: 100));
      if (finder.evaluate().isEmpty) {
        return;
      }
    }
    expect(finder, findsNothing);
  }

  /// Pump and settle
  /// معالجة جميع الإطارات والانتظار حتى الاستقرار
  Future<void> pumpAndSettle([Duration duration = const Duration(milliseconds: 100)]) async {
    await tester.pumpAndSettle(duration);
  }

  /// Wait for specific duration
  /// الانتظار لمدة محددة
  Future<void> wait(Duration duration) async {
    await Future.delayed(duration);
    await pumpAndSettle();
  }

  // ============================================================================
  // Assertion Helpers
  // دوال مساعدة للتحقق
  // ============================================================================

  /// Verify element exists
  /// التحقق من وجود عنصر
  void verifyElementExists(Finder finder, {String? message}) {
    expect(finder, findsWidgets, reason: message);
  }

  /// Verify element does not exist
  /// التحقق من عدم وجود عنصر
  void verifyElementNotExists(Finder finder, {String? message}) {
    expect(finder, findsNothing, reason: message);
  }

  /// Verify text exists
  /// التحقق من وجود نص
  void verifyTextExists(String text, {String? message}) {
    expect(find.text(text), findsWidgets, reason: message);
  }

  /// Verify text contains
  /// التحقق من احتواء النص
  void verifyTextContains(String text, {String? message}) {
    expect(
      find.textContaining(text, findRichText: true),
      findsWidgets,
      reason: message,
    );
  }

  // ============================================================================
  // Screenshot Helpers
  // دوال مساعدة للقطات الشاشة
  // ============================================================================

  /// Capture screenshot
  /// التقاط لقطة شاشة
  Future<void> takeScreenshot(String name) async {
    if (kIsWeb) {
      debugPrint('⚠️ Screenshots not supported on web');
      return;
    }

    try {
      // Create screenshots directory
      final screenshotDir = Directory('${TestConfig.screenshotDir}/integration');
      if (!screenshotDir.existsSync()) {
        screenshotDir.createSync(recursive: true);
      }

      // Take screenshot
      await binding.takeScreenshot(name);
      debugPrint('📸 Screenshot saved: $name');
    } catch (e) {
      debugPrint('⚠️ Screenshot failed: $e');
    }
  }

  /// Capture screenshot on failure
  /// التقاط لقطة شاشة عند الفشل
  Future<void> captureOnFailure(String testName, Future<void> Function() test) async {
    try {
      await test();
    } catch (e) {
      if (TestConfig.captureScreenshotsOnFailure) {
        final timestamp = DateTime.now().millisecondsSinceEpoch;
        await takeScreenshot('failure_${testName}_$timestamp');
      }
      rethrow;
    }
  }

  // ============================================================================
  // Field Management Helpers
  // دوال مساعدة لإدارة الحقول
  // ============================================================================

  /// Create new field
  /// إنشاء حقل جديد
  Future<void> createField(Map<String, dynamic> fieldData) async {
    // Navigate to fields section
    await navigateToBottomNavItem(ArabicStrings.home);
    await pumpAndSettle();

    // Look for add field button
    final addButton = find.byIcon(Icons.add);
    await tapElement(addButton);
    await pumpAndSettle();

    // Fill field form
    await enterText(find.byType(TextField).first, fieldData['name'] as String);
    await pumpAndSettle();

    // Save field
    final saveButton = find.text(ArabicStrings.save);
    await tapElement(saveButton);
    await pumpAndSettle();

    // Verify field created
    await waitForElement(find.text(fieldData['name'] as String));
  }

  /// Edit field
  /// تعديل حقل
  Future<void> editField(String fieldName, Map<String, dynamic> updates) async {
    // Find field
    await scrollUntilVisible(
      find.text(fieldName),
      scrollable: find.byType(ListView),
    );

    // Long press to open menu
    await longPressElement(find.text(fieldName));
    await pumpAndSettle();

    // Tap edit
    await tapElement(find.text(ArabicStrings.edit));
    await pumpAndSettle();

    // Update fields
    if (updates.containsKey('name')) {
      final nameField = find.byType(TextField).first;
      await clearText(nameField);
      await enterText(nameField, updates['name'] as String);
    }

    // Save changes
    final saveButton = find.text(ArabicStrings.save);
    await tapElement(saveButton);
    await pumpAndSettle();
  }

  /// Delete field
  /// حذف حقل
  Future<void> deleteField(String fieldName) async {
    // Find field
    await scrollUntilVisible(
      find.text(fieldName),
      scrollable: find.byType(ListView),
    );

    // Long press to open menu
    await longPressElement(find.text(fieldName));
    await pumpAndSettle();

    // Tap delete
    await tapElement(find.text(ArabicStrings.delete));
    await pumpAndSettle();

    // Confirm deletion
    final confirmButton = find.text(ArabicStrings.confirm);
    await tapElement(confirmButton);
    await pumpAndSettle();

    // Verify field deleted
    verifyElementNotExists(find.text(fieldName));
  }

  // ============================================================================
  // Network Helpers
  // دوال مساعدة للشبكة
  // ============================================================================

  /// Toggle offline mode
  /// تبديل وضع عدم الاتصال
  Future<void> toggleOfflineMode() async {
    // This would typically toggle airplane mode or disable network
    // Implementation depends on platform
    debugPrint('⚠️ Offline mode toggle - platform specific');
  }

  /// Wait for network sync
  /// الانتظار حتى مزامنة الشبكة
  Future<void> waitForSync() async {
    // Wait for sync indicator
    final syncIndicator = find.text(ArabicStrings.syncing);
    if (syncIndicator.evaluate().isNotEmpty) {
      await waitForElementToDisappear(syncIndicator, timeout: TestConfig.longTimeout);
    }
    await pumpAndSettle();
  }

  // ============================================================================
  // Utility Helpers
  // دوال مساعدة عامة
  // ============================================================================

  /// Print debug info
  /// طباعة معلومات التصحيح
  void debug(String message) {
    debugPrint('🧪 TEST: $message');
  }

  /// Get widget properties
  /// الحصول على خصائص عنصر
  T getWidget<T extends Widget>(Finder finder) {
    return tester.widget<T>(finder);
  }

  /// Check if widget exists
  /// التحقق من وجود عنصر
  bool widgetExists(Finder finder) {
    return finder.evaluate().isNotEmpty;
  }

  /// Get widget count
  /// الحصول على عدد العناصر
  int getWidgetCount(Finder finder) {
    return finder.evaluate().length;
  }
}

/// Extension methods for easier test writing
/// امتدادات لتسهيل كتابة الاختبارات
extension TestFinderExtensions on Finder {
  /// Check if finder has any widgets
  bool get exists => evaluate().isNotEmpty;

  /// Check if finder has no widgets
  bool get notExists => evaluate().isEmpty;

  /// Get count of widgets
  int get count => evaluate().length;
}

/// Extension methods for WidgetTester
/// امتدادات لـ WidgetTester
extension TestWidgetTesterExtensions on WidgetTester {
  /// Quick pump and settle
  Future<void> settle() async {
    await pumpAndSettle();
  }

  /// Tap with settle
  Future<void> tapAndSettle(Finder finder) async {
    await tap(finder);
    await pumpAndSettle();
  }

  /// Enter text with settle
  Future<void> enterTextAndSettle(Finder finder, String text) async {
    await enterText(finder, text);
    await pumpAndSettle();
  }
}
