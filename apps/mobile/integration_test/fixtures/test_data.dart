/// SAHOOL Integration Test - Test Data Fixtures
/// بيانات الاختبار الثابتة

/// Test user credentials
/// بيانات المستخدمين للاختبار
class TestUsers {
  // Valid test user
  static const String validEmail = 'test@sahool.app';
  static const String validPhone = '+967771234567';
  static const String validPassword = 'Test@1234';
  static const String validUsername = 'أحمد المزارع';

  // Invalid credentials for negative testing
  static const String invalidEmail = 'invalid@sahool.app';
  static const String invalidPassword = 'wrong_password';
  static const String weakPassword = '123';

  // Admin user
  static const String adminEmail = 'admin@sahool.app';
  static const String adminPassword = 'Admin@1234';

  // Demo user with existing data
  static const String demoEmail = 'demo@sahool.app';
  static const String demoPassword = 'Demo@1234';
  static const String demoUserId = 'demo-user-001';
}

/// Sample field data for testing
/// بيانات الحقول النموذجية للاختبار
class TestFields {
  static const field1 = {
    'id': 'field-test-001',
    'name': 'حقل القمح التجريبي',
    'nameEn': 'Test Wheat Field',
    'area': 5.5, // hectares
    'cropType': 'wheat',
    'cropTypeAr': 'قمح',
    'location': {
      'latitude': 15.3694,
      'longitude': 44.1910,
      'governorate': 'صنعاء',
      'district': 'همدان',
    },
    'polygon': [
      {'lat': 15.3694, 'lng': 44.1910},
      {'lat': 15.3704, 'lng': 44.1920},
      {'lat': 15.3704, 'lng': 44.1900},
      {'lat': 15.3694, 'lng': 44.1900},
    ],
    'soilType': 'clay_loam',
    'irrigationType': 'drip',
  };

  static const field2 = {
    'id': 'field-test-002',
    'name': 'حقل الذرة الشامية',
    'nameEn': 'Test Corn Field',
    'area': 3.2,
    'cropType': 'corn',
    'cropTypeAr': 'ذرة',
    'location': {
      'latitude': 15.3750,
      'longitude': 44.2000,
      'governorate': 'صنعاء',
      'district': 'معين',
    },
    'polygon': [
      {'lat': 15.3750, 'lng': 44.2000},
      {'lat': 15.3760, 'lng': 44.2010},
      {'lat': 15.3760, 'lng': 44.1990},
      {'lat': 15.3750, 'lng': 44.1990},
    ],
    'soilType': 'sandy_loam',
    'irrigationType': 'sprinkler',
  };

  static const newFieldData = {
    'name': 'حقل اختبار جديد',
    'nameEn': 'New Test Field',
    'area': 2.0,
    'cropType': 'tomato',
    'cropTypeAr': 'طماطم',
    'location': {
      'latitude': 15.3800,
      'longitude': 44.2100,
      'governorate': 'صنعاء',
      'district': 'صنعاء القديمة',
    },
    'soilType': 'loam',
    'irrigationType': 'flood',
  };
}

/// Sample inventory test data
/// بيانات المخزون النموذجية للاختبار
class TestInventory {
  static const fertilizer1 = {
    'id': 'inv-test-001',
    'name': 'سماد اليوريا',
    'nameEn': 'Urea Fertilizer',
    'category': 'fertilizer',
    'categoryAr': 'أسمدة',
    'quantity': 500.0,
    'unit': 'kg',
    'unitPrice': 150.0,
    'reorderLevel': 100.0,
    'supplier': 'شركة الأسمدة اليمنية',
    'expiryDate': '2025-12-31',
  };

  static const pesticide1 = {
    'id': 'inv-test-002',
    'name': 'مبيد حشري عضوي',
    'nameEn': 'Organic Pesticide',
    'category': 'pesticide',
    'categoryAr': 'مبيدات',
    'quantity': 20.0,
    'unit': 'liter',
    'unitPrice': 450.0,
    'reorderLevel': 5.0,
    'supplier': 'المركز الزراعي',
    'expiryDate': '2025-06-30',
  };

  static const seed1 = {
    'id': 'inv-test-003',
    'name': 'بذور قمح محسنة',
    'nameEn': 'Improved Wheat Seeds',
    'category': 'seeds',
    'categoryAr': 'بذور',
    'quantity': 100.0,
    'unit': 'kg',
    'unitPrice': 200.0,
    'reorderLevel': 20.0,
    'supplier': 'مركز البحوث الزراعية',
    'expiryDate': '2025-09-01',
  };

  static const stockMovement = {
    'type': 'out',
    'quantity': 50.0,
    'reason': 'استخدام في الحقل',
    'reasonEn': 'Field Usage',
    'fieldId': 'field-test-001',
    'notes': 'تسميد حقل القمح',
  };

  static const lowStockItem = {
    'id': 'inv-test-004',
    'name': 'أنابيب ري',
    'nameEn': 'Irrigation Pipes',
    'category': 'equipment',
    'categoryAr': 'معدات',
    'quantity': 15.0,
    'unit': 'piece',
    'unitPrice': 85.0,
    'reorderLevel': 20.0,
    'supplier': 'محل المعدات الزراعية',
  };
}

/// Sample VRA prescription data
/// بيانات وصفات الزراعة الدقيقة النموذجية للاختبار
class TestVRA {
  static const prescription1 = {
    'id': 'vra-test-001',
    'name': 'وصفة تسميد متغيرة للقمح',
    'nameEn': 'Variable Rate Fertilizer - Wheat',
    'fieldId': 'field-test-001',
    'fieldName': 'حقل القمح التجريبي',
    'inputType': 'fertilizer',
    'inputTypeAr': 'سماد',
    'product': 'يوريا 46%',
    'targetDate': '2025-03-15',
    'status': 'draft',
    'zones': [
      {
        'zoneId': 1,
        'name': 'منطقة عالية الخصوبة',
        'color': '#4CAF50',
        'rate': 150.0, // kg/ha
        'area': 2.0,
        'ndvi': 0.75,
      },
      {
        'zoneId': 2,
        'name': 'منطقة متوسطة الخصوبة',
        'color': '#FFC107',
        'rate': 200.0,
        'area': 2.5,
        'ndvi': 0.60,
      },
      {
        'zoneId': 3,
        'name': 'منطقة منخفضة الخصوبة',
        'color': '#F44336',
        'rate': 250.0,
        'area': 1.0,
        'ndvi': 0.45,
      },
    ],
    'totalAmount': 487.5, // calculated
    'estimatedCost': 73125.0, // SAR
  };

  static const newPrescription = {
    'name': 'وصفة رش مبيد',
    'nameEn': 'Variable Rate Pesticide',
    'fieldId': 'field-test-002',
    'inputType': 'pesticide',
    'product': 'مبيد حشري',
    'targetDate': '2025-03-20',
  };
}

/// Sample satellite imagery data
/// بيانات صور الأقمار الصناعية النموذجية للاختبار
class TestSatellite {
  static const imagery1 = {
    'fieldId': 'field-test-001',
    'date': '2025-03-01',
    'source': 'Sentinel-2',
    'cloudCoverage': 5.2,
    'ndvi': {
      'min': 0.35,
      'max': 0.82,
      'mean': 0.64,
      'median': 0.66,
    },
    'indices': {
      'ndvi': 0.64,
      'ndmi': 0.45,
      'evi': 0.58,
      'savi': 0.61,
    },
    'zones': [
      {'level': 'high', 'percentage': 35.0, 'color': '#00FF00'},
      {'level': 'medium', 'percentage': 45.0, 'color': '#FFFF00'},
      {'level': 'low', 'percentage': 20.0, 'color': '#FF0000'},
    ],
  };

  static const historicalData = [
    {
      'date': '2025-01-15',
      'ndvi': 0.45,
      'cloudCoverage': 8.5,
    },
    {
      'date': '2025-02-01',
      'ndvi': 0.58,
      'cloudCoverage': 12.0,
    },
    {
      'date': '2025-02-15',
      'ndvi': 0.62,
      'cloudCoverage': 3.2,
    },
    {
      'date': '2025-03-01',
      'ndvi': 0.64,
      'cloudCoverage': 5.2,
    },
  ];
}

/// API endpoints for testing
/// نقاط الاتصال بالخدمات للاختبار
class TestEndpoints {
  static const String baseUrl = 'https://api.sahool.app';
  static const String mockBaseUrl = 'http://localhost:3000';

  // Auth endpoints
  static const String login = '/api/v1/auth/login';
  static const String register = '/api/v1/auth/register';
  static const String logout = '/api/v1/auth/logout';
  static const String refreshToken = '/api/v1/auth/refresh';

  // Fields endpoints
  static const String fields = '/api/v1/fields';
  static String fieldById(String id) => '/api/v1/fields/$id';

  // Inventory endpoints
  static const String inventory = '/api/v1/inventory';
  static String inventoryById(String id) => '/api/v1/inventory/$id';
  static const String stockMovements = '/api/v1/inventory/movements';

  // VRA endpoints
  static const String vra = '/api/v1/vra/prescriptions';
  static String vraById(String id) => '/api/v1/vra/prescriptions/$id';

  // Satellite endpoints
  static const String satellite = '/api/v1/satellite';
  static String satelliteByField(String fieldId) =>
      '/api/v1/satellite/fields/$fieldId';
}

/// Test configuration
/// إعدادات الاختبار
class TestConfig {
  // Timeouts
  static const Duration shortTimeout = Duration(seconds: 5);
  static const Duration mediumTimeout = Duration(seconds: 10);
  static const Duration longTimeout = Duration(seconds: 30);

  // Test delays
  static const Duration shortDelay = Duration(milliseconds: 500);
  static const Duration mediumDelay = Duration(seconds: 1);
  static const Duration longDelay = Duration(seconds: 2);

  // Retry configuration
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 2);

  // Screenshot configuration
  static const String screenshotDir = 'screenshots';
  static const bool captureScreenshotsOnFailure = true;
  static const bool captureScreenshotsOnSuccess = false;

  // Test modes
  static const bool useMockData = true;
  static const bool enableNetworkStubbing = true;
  static const bool runInHeadlessMode = false;
}

/// Common Arabic UI strings for element finding
/// النصوص العربية الشائعة للعناصر
class ArabicStrings {
  // Navigation
  static const String home = 'الرئيسية';
  static const String fields = 'الحقول';
  static const String tasks = 'المهام';
  static const String equipment = 'المعدات';
  static const String marketplace = 'السوق';
  static const String wallet = 'المحفظة';
  static const String community = 'المجتمع';
  static const String more = 'المزيد';

  // Auth
  static const String login = 'تسجيل الدخول';
  static const String logout = 'تسجيل الخروج';
  static const String register = 'تسجيل جديد';
  static const String email = 'البريد الإلكتروني';
  static const String password = 'كلمة المرور';
  static const String phone = 'رقم الهاتف';
  static const String username = 'اسم المستخدم';

  // Common actions
  static const String add = 'إضافة';
  static const String edit = 'تعديل';
  static const String delete = 'حذف';
  static const String save = 'حفظ';
  static const String cancel = 'إلغاء';
  static const String confirm = 'تأكيد';
  static const String search = 'بحث';
  static const String filter = 'تصفية';
  static const String export = 'تصدير';
  static const String refresh = 'تحديث';

  // Field management
  static const String newField = 'حقل جديد';
  static const String fieldName = 'اسم الحقل';
  static const String fieldArea = 'مساحة الحقل';
  static const String cropType = 'نوع المحصول';
  static const String location = 'الموقع';

  // Inventory
  static const String inventory = 'المخزون';
  static const String stockMovement = 'حركة مخزون';
  static const String lowStock = 'مخزون منخفض';
  static const String quantity = 'الكمية';
  static const String unit = 'الوحدة';

  // VRA
  static const String vra = 'الزراعة الدقيقة';
  static const String prescription = 'وصفة';
  static const String newPrescription = 'وصفة جديدة';
  static const String zones = 'المناطق';
  static const String rate = 'المعدل';

  // Satellite
  static const String satellite = 'الصور الفضائية';
  static const String ndvi = 'مؤشر NDVI';
  static const String imagery = 'الصور';
  static const String historical = 'السجل التاريخي';

  // Status messages
  static const String loading = 'جارِ التحميل...';
  static const String success = 'تم بنجاح';
  static const String error = 'حدث خطأ';
  static const String noData = 'لا توجد بيانات';
  static const String offline = 'وضع عدم الاتصال';
  static const String syncing = 'جارِ المزامنة...';
}
