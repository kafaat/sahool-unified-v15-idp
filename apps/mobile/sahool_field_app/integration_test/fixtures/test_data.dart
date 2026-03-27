/// Test Data Fixtures for Integration Tests
/// بيانات اختبار ثابتة لاختبارات التكامل
///
/// Centralised test constants used by integration tests that exercise
/// the MockServer (auth flows, API layer, offline sync, etc.).
library;

// ═══════════════════════════════════════════════════════════════════════════
// Test Users
// ═══════════════════════════════════════════════════════════════════════════

/// Pre-defined user credentials for integration tests.
class TestUsers {
  TestUsers._();

  // Valid farmer account
  static const validEmail = 'ahmed@example.com';
  static const validPassword = 'SecurePass123!';
  static const validUsername = 'أحمد المزارع';

  // Admin account
  static const adminEmail = 'admin@sahool.app';
  static const adminPassword = 'AdminPass123!';
  static const adminUsername = 'مدير النظام';

  // Invalid credentials (will trigger 401)
  static const invalidEmail = 'invalid@example.com';
  static const invalidPassword = 'wrong-password';
}

// ═══════════════════════════════════════════════════════════════════════════
// Test Fields
// ═══════════════════════════════════════════════════════════════════════════

/// Pre-defined field data for integration tests.
class TestFields {
  TestFields._();

  static const field1 = {
    'id': 'field-001',
    'name': 'حقل القمح',
    'area_hectares': 10.5,
    'crop_type': 'wheat',
    'status': 'active',
    'tenant_id': 'tenant-001',
  };

  static const field2 = {
    'id': 'field-002',
    'name': 'حقل الشعير',
    'area_hectares': 8.2,
    'crop_type': 'barley',
    'status': 'active',
    'tenant_id': 'tenant-001',
  };

  static const allFields = [field1, field2];
}

// ═══════════════════════════════════════════════════════════════════════════
// Test Tasks
// ═══════════════════════════════════════════════════════════════════════════

/// Pre-defined task data for integration tests.
class TestTasks {
  TestTasks._();

  static const task1 = {
    'id': 'task-001',
    'title': 'ري الحقل الشمالي',
    'status': 'open',
    'priority': 'high',
    'field_id': 'field-001',
    'tenant_id': 'tenant-001',
  };

  static const task2 = {
    'id': 'task-002',
    'title': 'تسميد البيت المحمي',
    'status': 'in_progress',
    'priority': 'medium',
    'field_id': 'field-002',
    'tenant_id': 'tenant-001',
  };

  static const allTasks = [task1, task2];
}

// ═══════════════════════════════════════════════════════════════════════════
// Test Auth Tokens
// ═══════════════════════════════════════════════════════════════════════════

/// Sample tokens for tests that skip the login flow.
const testAuthToken = 'mock-access-token-for-testing';
const testRefreshToken = 'mock-refresh-token-for-testing';

// ═══════════════════════════════════════════════════════════════════════════
// Test Weather
// ═══════════════════════════════════════════════════════════════════════════

/// Pre-defined weather data for integration tests.
class TestWeather {
  TestWeather._();

  static const current = {
    'temperature': 28.5,
    'humidity': 45,
    'description': 'مشمس',
    'wind_speed': 3.5,
    'wind_direction': 'NE',
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Test Alerts
// ═══════════════════════════════════════════════════════════════════════════

/// Pre-defined alert data for integration tests.
class TestAlerts {
  TestAlerts._();

  static const alert1 = {
    'id': 'alert-001',
    'type': 'irrigation',
    'severity': 'warning',
    'title': 'تنبيه ري',
    'message': 'رطوبة التربة منخفضة',
    'field_id': 'field-001',
    'status': 'active',
  };
}
