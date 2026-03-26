/// Test Fixtures for SAHOOL Field App
/// بيانات اختبار ثابتة

/// Sample field data for tests
class FieldFixtures {
  static const sampleField = {
    'id': 'field_001',
    'name': 'حقل الشمال',
    'area': 150.5,
    'tenant_id': 'tenant_1',
    'crop_type': 'wheat',
    'status': 'active',
    'location': {
      'lat': 15.3694,
      'lng': 44.1910,
    },
    'polygon': [
      {'lat': 15.370, 'lng': 44.190},
      {'lat': 15.371, 'lng': 44.191},
      {'lat': 15.369, 'lng': 44.192},
    ],
    'created_at': '2024-01-01T00:00:00Z',
    'updated_at': '2024-01-15T00:00:00Z',
  };

  static const sampleFieldsList = [
    {
      'id': 'field_001',
      'name': 'حقل الشمال',
      'area': 150.5,
      'status': 'active',
    },
    {
      'id': 'field_002',
      'name': 'حقل الجنوب',
      'area': 200.0,
      'status': 'active',
    },
    {
      'id': 'field_003',
      'name': 'البيت المحمي',
      'area': 50.0,
      'status': 'inactive',
    },
  ];
}

/// Sample task data for tests
class TaskFixtures {
  static const sampleTask = {
    'id': 'task_001',
    'title': 'ري الحقل الشمالي',
    'description': 'ري الحقل بكمية 500 لتر',
    'status': 'pending',
    'priority': 'high',
    'field_id': 'field_001',
    'assignee_id': 'user_001',
    'due_date': '2024-01-20T10:00:00Z',
    'created_at': '2024-01-01T00:00:00Z',
  };

  static const sampleTasksList = [
    {
      'id': 'task_001',
      'title': 'ري الحقل الشمالي',
      'status': 'pending',
      'priority': 'high',
    },
    {
      'id': 'task_002',
      'title': 'تسميد البيت المحمي',
      'status': 'in_progress',
      'priority': 'medium',
    },
    {
      'id': 'task_003',
      'title': 'حصاد القمح',
      'status': 'completed',
      'priority': 'low',
    },
  ];

  static const pendingTasks = [
    {'id': 'task_001', 'title': 'ري الحقل', 'status': 'pending'},
    {'id': 'task_004', 'title': 'فحص الآفات', 'status': 'pending'},
  ];

  static const completedTasks = [
    {'id': 'task_003', 'title': 'حصاد القمح', 'status': 'completed'},
  ];
}

/// Sample weather data for tests
class WeatherFixtures {
  static const currentWeather = {
    'temperature': 28.5,
    'humidity': 45,
    'description': 'مشمس',
    'wind_speed': 3.5,
    'wind_direction': 'NE',
    'pressure': 1013,
    'uv_index': 7,
    'visibility': 10,
    'feels_like': 30.0,
    'icon': 'sunny',
  };

  static const weatherForecast = [
    {'date': '2024-01-16', 'high': 30, 'low': 18, 'description': 'مشمس'},
    {'date': '2024-01-17', 'high': 28, 'low': 16, 'description': 'غائم جزئياً'},
    {'date': '2024-01-18', 'high': 25, 'low': 14, 'description': 'ممطر'},
  ];
}

/// Sample user data for tests
class UserFixtures {
  static const sampleUser = {
    'id': 'user_001',
    'name': 'أحمد المزارع',
    'email': 'ahmed@example.com',
    'phone': '+967123456789',
    'role': 'farmer',
    'tenant_id': 'tenant_1',
  };

  static const sampleAdminUser = {
    'id': 'admin_001',
    'name': 'مدير النظام',
    'email': 'admin@sahool.app',
    'role': 'admin',
    'tenant_id': 'tenant_1',
  };
}

/// Sample sync data for tests
class SyncFixtures {
  static const pendingOutboxItem = {
    'id': 'outbox_001',
    'entity_type': 'task',
    'entity_id': 'task_001',
    'method': 'POST',
    'api_endpoint': '/tasks',
    'payload': '{"title": "مهمة جديدة"}',
    'retry_count': 0,
    'created_at': '2024-01-15T00:00:00Z',
  };

  static const syncLog = {
    'id': 'log_001',
    'type': 'full_sync',
    'status': 'success',
    'message': 'Synced 5 items',
    'created_at': '2024-01-15T00:00:00Z',
  };
}

/// Sample wallet data for tests
class WalletFixtures {
  static const sampleWallet = {
    'id': 'wallet_001',
    'user_id': 'user_001',
    'balance': 1250.50,
    'credit_score': 720,
    'currency': 'USD',
  };

  static const transactions = [
    {
      'id': 'tx_001',
      'type': 'credit',
      'amount': 500.0,
      'description': 'بيع محصول',
      'date': '2024-01-10T00:00:00Z',
    },
    {
      'id': 'tx_002',
      'type': 'debit',
      'amount': 100.0,
      'description': 'شراء بذور',
      'date': '2024-01-12T00:00:00Z',
    },
  ];
}

/// API Response templates
class ApiResponseFixtures {
  static Map<String, dynamic> success(dynamic data) => {
        'success': true,
        'data': data,
        'message': null,
      };

  static Map<String, dynamic> error(String message, {int code = 400}) => {
        'success': false,
        'data': null,
        'message': message,
        'code': code,
      };

  static Map<String, dynamic> paginated({
    required List<dynamic> items,
    int page = 1,
    int limit = 20,
    int total = 100,
  }) =>
      {
        'success': true,
        'data': items,
        'meta': {
          'page': page,
          'limit': limit,
          'total': total,
          'has_more': (page * limit) < total,
        },
      };
}
