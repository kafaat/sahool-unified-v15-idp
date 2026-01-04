# دليل تكامل API لتطبيق سهول الموبايل
# SAHOOL Mobile App API Integration Guide

## نظرة عامة | Overview

يستخدم نظام سهول **Kong API Gateway** كبوابة موحدة لجميع الخدمات المصغرة (39+ خدمة).
البوابة تعمل على المنفذ `8000` وتوفر:

- مصادقة JWT موحدة
- تحديد معدل الطلبات حسب باقة الاشتراك
- التحكم في الوصول (ACL)
- CORS للمتصفحات والتطبيقات
- رؤوس أمان متقدمة

---

## التكوين الأساسي | Base Configuration

```dart
// lib/core/config/api_config.dart

class ApiConfig {
  // Production
  static const String baseUrl = 'https://api.sahool.app';

  // Development
  static const String devBaseUrl = 'http://localhost:8000';

  // WebSocket
  static const String wsUrl = 'wss://api.sahool.app/api/v1/ws';
  static const String devWsUrl = 'ws://localhost:8081';

  // API Version
  static const String apiVersion = 'v1';

  // Timeouts (milliseconds)
  static const int connectTimeout = 15000;
  static const int receiveTimeout = 60000;
  static const int sendTimeout = 30000;
}
```

---

## المصادقة | Authentication

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "iss": "sahool-auth",
    "sub": "user-id",
    "aud": "sahool-api",
    "exp": 1234567890,
    "iat": 1234567890,
    "tier": "starter|professional|enterprise|research",
    "tenant_id": "tenant-uuid",
    "permissions": ["fields:read", "fields:write", ...]
  }
}
```

### نقاط المصادقة | Auth Endpoints

| Endpoint | Method | Rate Limit | Description |
|----------|--------|------------|-------------|
| `/api/v1/auth/login` | POST | 5/min, 20/hour | تسجيل الدخول |
| `/api/v1/auth/register` | POST | 10/min, 50/hour | التسجيل |
| `/api/v1/auth/refresh` | POST | 10/min, 100/hour | تجديد التوكن |
| `/api/v1/auth/password-reset` | POST | 3/min, 10/hour | إعادة تعيين كلمة المرور |
| `/api/v1/auth/forgot-password` | POST | 3/min, 10/hour | نسيت كلمة المرور |

### تنفيذ Dio Interceptor

```dart
// lib/core/http/auth_interceptor.dart

class AuthInterceptor extends Interceptor {
  final AuthService _authService;

  AuthInterceptor(this._authService);

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _authService.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    options.headers['X-Request-ID'] = const Uuid().v4();
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      try {
        await _authService.refreshToken();
        final newToken = await _authService.getAccessToken();
        err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
        final response = await Dio().fetch(err.requestOptions);
        handler.resolve(response);
        return;
      } catch (e) {
        await _authService.logout();
      }
    }
    handler.next(err);
  }
}
```

---

## باقات الاشتراك والصلاحيات | Subscription Tiers & Permissions

### Starter Package (المزارعون الصغار)

| الخدمة | Endpoint | Rate Limit | الوصف |
|--------|----------|------------|-------|
| **Field Core** | `/api/v1/fields` | 100/min, 5000/hour | إدارة الحقول الأساسية |
| **Weather** | `/api/v1/weather` | 100/min | بيانات الطقس الحالية والتوقعات |
| **Calendar** | `/api/v1/calendar` | 100/min | التقويم الفلكي اليمني |
| **Advice** | `/api/v1/advice` | 100/min | الاستشارات الزراعية الأساسية |
| **Notifications** | `/api/v1/notifications` | 100/min | الإشعارات |

### Professional Package (المزارعون المحترفون)

*يشمل جميع خدمات Starter بالإضافة إلى:*

| الخدمة | Endpoint | Rate Limit | الوصف |
|--------|----------|------------|-------|
| **Satellite** | `/api/v1/satellite` | 1000/min, 50000/hour | صور الأقمار الصناعية |
| **NDVI** | `/api/v1/ndvi` | 1000/min | تحليل مؤشر النباتات |
| **NDVI Processor** | `/api/v1/ndvi-processor` | 1000/min | معالجة NDVI المتقدمة |
| **Crop Health** | `/api/v1/crop-health` | 1000/min | تحليل صحة المحاصيل بالذكاء الاصطناعي |
| **Irrigation** | `/api/v1/irrigation` | 1000/min | الري الذكي |
| **Virtual Sensors** | `/api/v1/sensors/virtual` | 1000/min | المستشعرات الافتراضية (ET0) |
| **Yield** | `/api/v1/yield` | 1000/min | توقع الإنتاجية |
| **Fertilizer** | `/api/v1/fertilizer` | 1000/min | توصيات التسميد |
| **Inventory** | `/api/v1/inventory` | 1000/min | إدارة المخزون |
| **Equipment** | `/api/v1/equipment` | 1000/min | إدارة المعدات |
| **Weather Advanced** | `/api/v1/weather/advanced` | 1000/min | الطقس المتقدم |
| **Indicators** | `/api/v1/indicators` | 1000/min | المؤشرات الزراعية |
| **Providers** | `/api/v1/providers` | 500/min | تكوين المزودين |

### Enterprise Package (الشركات الزراعية)

*يشمل جميع خدمات Professional بالإضافة إلى:*

| الخدمة | Endpoint | Rate Limit | الوصف |
|--------|----------|------------|-------|
| **AI Advisor** | `/api/v1/ai-advisor` | 10000/min, 500000/hour | المستشار الذكي متعدد الوكلاء |
| **IoT Gateway** | `/api/v1/iot` | 10000/min | بوابة إنترنت الأشياء |
| **IoT Service** | `/api/v1/iot-service` | 10000/min | خدمة IoT المتقدمة |
| **Research** | `/api/v1/research` | 10000/min | إدارة الأبحاث العلمية |
| **Marketplace** | `/api/v1/marketplace` | 10000/min | السوق الزراعي |
| **Billing** | `/api/v1/billing` | 1000/min | الفوترة والمدفوعات |
| **Disaster** | `/api/v1/disaster` | 10000/min | تقييم الكوارث |
| **Crop Model** | `/api/v1/crop-model` | 10000/min | نماذج نمو المحاصيل (WOFOST) |
| **LAI** | `/api/v1/lai` | 10000/min | تقدير مؤشر مساحة الورق |
| **Yield Prediction** | `/api/v1/yield-prediction` | 10000/min | توقع الإنتاجية المتقدم |

### Shared Services (جميع الباقات)

| الخدمة | Endpoint | Rate Limit | الوصف |
|--------|----------|------------|-------|
| **WebSocket** | `/api/v1/ws` | 5000/min | التحديثات الفورية |
| **Field Ops** | `/api/v1/field-ops` | 1000/min | عمليات الحقول |
| **Field Service** | `/api/v1/field-service` | 1000/min | خدمة الحقول |
| **Tasks** | `/api/v1/tasks` | 1000/min | إدارة المهام |
| **Alerts** | `/api/v1/alerts` | 1000/min | التنبيهات |
| **Chat** | `/api/v1/chat` | 2000/min | المحادثات |
| **Community Chat** | `/api/v1/community/chat` | 2000/min | محادثة المجتمع |
| **Field Chat** | `/api/v1/field/chat` | 2000/min | محادثة الحقل |
| **Health Check** | `/health`, `/ping` | Unlimited | فحص صحة النظام |

---

## خريطة الخدمات الداخلية | Internal Services Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Kong API Gateway (Port 8000)                        │
│                              البوابة الموحدة                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│   STARTER TIER      │   │  PROFESSIONAL TIER  │   │   ENTERPRISE TIER   │
│   الباقة الأساسية    │   │   الباقة المتوسطة    │   │   الباقة المتقدمة    │
└─────────────────────┘   └─────────────────────┘   └─────────────────────┘
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Backend Services                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────┐ │
│  │ field-management     │  │ weather-service      │  │ ai-advisor         │ │
│  │ :3000                │  │ :8092                │  │ :8112              │ │
│  │ إدارة الحقول الموحدة  │  │ خدمة الطقس الموحدة   │  │ المستشار الذكي      │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────┘ │
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────┐ │
│  │ vegetation-analysis  │  │ crop-intelligence    │  │ advisory-service   │ │
│  │ :8090                │  │ :8095                │  │ :8093              │ │
│  │ تحليل النباتات       │  │ ذكاء المحاصيل        │  │ الاستشارات         │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────┘ │
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────┐ │
│  │ yield-prediction     │  │ irrigation-smart     │  │ iot-gateway        │ │
│  │ :8098                │  │ :8094                │  │ :8106              │ │
│  │ توقع الإنتاجية       │  │ الري الذكي           │  │ بوابة IoT          │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────┘ │
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────┐ │
│  │ notification-service │  │ billing-core         │  │ marketplace        │ │
│  │ :8110                │  │ :8089                │  │ :3010              │ │
│  │ الإشعارات            │  │ الفوترة              │  │ السوق              │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────┘ │
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────┐ │
│  │ ws-gateway           │  │ chat-service         │  │ research-core      │ │
│  │ :8081                │  │ :8114                │  │ :3015              │ │
│  │ WebSocket            │  │ المحادثات            │  │ الأبحاث            │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Infrastructure Services                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  PostgreSQL   │  Redis   │  NATS   │  MQTT   │  Qdrant   │  Milvus          │
│  :5432        │  :6379   │  :4222  │  :1883  │  :6333    │  :19530          │
│  قاعدة البيانات│  التخزين │  الرسائل │  IoT    │  Vector   │  Vector DB       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## تفاصيل كل Endpoint | Endpoint Details

### 1. Field Management - إدارة الحقول

```dart
// GET /api/v1/fields - قائمة الحقول
// POST /api/v1/fields - إنشاء حقل جديد
// GET /api/v1/fields/{id} - تفاصيل حقل
// PUT /api/v1/fields/{id} - تحديث حقل
// DELETE /api/v1/fields/{id} - حذف حقل

class FieldService {
  final Dio _dio;

  Future<List<Field>> getFields({int page = 1, int limit = 20}) async {
    final response = await _dio.get('/api/v1/fields', queryParameters: {
      'page': page,
      'limit': limit,
    });
    return (response.data['data'] as List)
        .map((e) => Field.fromJson(e))
        .toList();
  }

  Future<Field> createField(FieldCreateRequest request) async {
    final response = await _dio.post('/api/v1/fields', data: request.toJson());
    return Field.fromJson(response.data['data']);
  }

  Future<Field> getFieldById(String id) async {
    final response = await _dio.get('/api/v1/fields/$id');
    return Field.fromJson(response.data['data']);
  }
}
```

### 2. Weather Service - خدمة الطقس

```dart
// GET /api/v1/weather/current?lat={lat}&lon={lon}
// GET /api/v1/weather/forecast?lat={lat}&lon={lon}&days={days}
// GET /api/v1/weather/history?lat={lat}&lon={lon}&from={date}&to={date}
// GET /api/v1/weather/alerts?lat={lat}&lon={lon}

class WeatherService {
  final Dio _dio;

  Future<CurrentWeather> getCurrentWeather(double lat, double lon) async {
    final response = await _dio.get('/api/v1/weather/current',
      queryParameters: {'lat': lat, 'lon': lon});
    return CurrentWeather.fromJson(response.data['data']);
  }

  Future<List<WeatherForecast>> getForecast(double lat, double lon, {int days = 7}) async {
    final response = await _dio.get('/api/v1/weather/forecast',
      queryParameters: {'lat': lat, 'lon': lon, 'days': days});
    return (response.data['data'] as List)
        .map((e) => WeatherForecast.fromJson(e))
        .toList();
  }
}
```

### 3. Satellite & NDVI - الأقمار الصناعية

```dart
// GET /api/v1/satellite/imagery?field_id={id}&date={date}
// GET /api/v1/ndvi/analysis?field_id={id}&date={date}
// GET /api/v1/ndvi/timeseries?field_id={id}&from={date}&to={date}

class SatelliteService {
  final Dio _dio;

  Future<SatelliteImagery> getImagery(String fieldId, DateTime date) async {
    final response = await _dio.get('/api/v1/satellite/imagery',
      queryParameters: {
        'field_id': fieldId,
        'date': date.toIso8601String()
      });
    return SatelliteImagery.fromJson(response.data['data']);
  }

  Future<NdviAnalysis> getNdviAnalysis(String fieldId, DateTime date) async {
    final response = await _dio.get('/api/v1/ndvi/analysis',
      queryParameters: {
        'field_id': fieldId,
        'date': date.toIso8601String()
      });
    return NdviAnalysis.fromJson(response.data['data']);
  }
}
```

### 4. Crop Health AI - صحة المحاصيل

```dart
// POST /api/v1/crop-health/analyze - تحليل صورة
// GET /api/v1/crop-health/diseases - قائمة الأمراض
// GET /api/v1/crop-health/history?field_id={id}

class CropHealthService {
  final Dio _dio;

  Future<CropHealthAnalysis> analyzeImage(File imageFile, String fieldId) async {
    final formData = FormData.fromMap({
      'image': await MultipartFile.fromFile(imageFile.path),
      'field_id': fieldId,
    });
    final response = await _dio.post('/api/v1/crop-health/analyze',
      data: formData,
      options: Options(
        sendTimeout: const Duration(seconds: 120),
        receiveTimeout: const Duration(seconds: 120),
      ));
    return CropHealthAnalysis.fromJson(response.data['data']);
  }
}
```

### 5. AI Advisor - المستشار الذكي

```dart
// POST /api/v1/ai-advisor/query - استعلام ذكي
// POST /api/v1/ai-advisor/chat - محادثة
// GET /api/v1/ai-advisor/recommendations?field_id={id}

class AiAdvisorService {
  final Dio _dio;

  Future<AiResponse> query(String question, {String? fieldId, String? context}) async {
    final response = await _dio.post('/api/v1/ai-advisor/query',
      data: {
        'question': question,
        'field_id': fieldId,
        'context': context,
        'language': 'ar', // العربية
      },
      options: Options(
        sendTimeout: const Duration(seconds: 180),
        receiveTimeout: const Duration(seconds: 180),
      ));
    return AiResponse.fromJson(response.data['data']);
  }

  Stream<String> chatStream(String message, String conversationId) async* {
    // WebSocket streaming for real-time responses
    final channel = WebSocketChannel.connect(
      Uri.parse('${ApiConfig.wsUrl}/ai-advisor/chat'));

    channel.sink.add(jsonEncode({
      'message': message,
      'conversation_id': conversationId,
    }));

    await for (final data in channel.stream) {
      yield jsonDecode(data)['chunk'];
    }
  }
}
```

### 6. Irrigation - الري الذكي

```dart
// GET /api/v1/irrigation/schedule?field_id={id}
// POST /api/v1/irrigation/calculate - حساب احتياجات الري
// GET /api/v1/irrigation/history?field_id={id}

class IrrigationService {
  final Dio _dio;

  Future<IrrigationSchedule> getSchedule(String fieldId) async {
    final response = await _dio.get('/api/v1/irrigation/schedule',
      queryParameters: {'field_id': fieldId});
    return IrrigationSchedule.fromJson(response.data['data']);
  }

  Future<IrrigationCalculation> calculateNeeds(IrrigationRequest request) async {
    final response = await _dio.post('/api/v1/irrigation/calculate',
      data: request.toJson());
    return IrrigationCalculation.fromJson(response.data['data']);
  }
}
```

### 7. IoT Gateway - بوابة إنترنت الأشياء

```dart
// GET /api/v1/iot/devices?field_id={id}
// GET /api/v1/iot/sensors/{device_id}/readings
// POST /api/v1/iot/devices/{device_id}/command

class IoTService {
  final Dio _dio;

  Future<List<IoTDevice>> getDevices(String fieldId) async {
    final response = await _dio.get('/api/v1/iot/devices',
      queryParameters: {'field_id': fieldId});
    return (response.data['data'] as List)
        .map((e) => IoTDevice.fromJson(e))
        .toList();
  }

  Future<List<SensorReading>> getSensorReadings(String deviceId, {
    DateTime? from,
    DateTime? to,
  }) async {
    final response = await _dio.get('/api/v1/iot/sensors/$deviceId/readings',
      queryParameters: {
        if (from != null) 'from': from.toIso8601String(),
        if (to != null) 'to': to.toIso8601String(),
      });
    return (response.data['data'] as List)
        .map((e) => SensorReading.fromJson(e))
        .toList();
  }

  Future<void> sendCommand(String deviceId, IoTCommand command) async {
    await _dio.post('/api/v1/iot/devices/$deviceId/command',
      data: command.toJson());
  }
}
```

### 8. WebSocket - التحديثات الفورية

```dart
// WS /api/v1/ws - WebSocket Gateway

class WebSocketService {
  WebSocketChannel? _channel;
  final AuthService _authService;

  Future<void> connect() async {
    final token = await _authService.getAccessToken();
    _channel = WebSocketChannel.connect(
      Uri.parse('${ApiConfig.wsUrl}?token=$token'),
    );

    _channel!.stream.listen(
      _handleMessage,
      onError: _handleError,
      onDone: _handleDisconnect,
    );
  }

  void subscribe(String topic) {
    _channel?.sink.add(jsonEncode({
      'action': 'subscribe',
      'topic': topic,
    }));
  }

  void _handleMessage(dynamic message) {
    final data = jsonDecode(message);
    switch (data['type']) {
      case 'weather.update':
        // Handle weather update
        break;
      case 'field.alert':
        // Handle field alert
        break;
      case 'iot.reading':
        // Handle IoT reading
        break;
    }
  }
}
```

---

## معالجة الأخطاء | Error Handling

### HTTP Status Codes

| Code | Description | الوصف |
|------|-------------|-------|
| 200 | OK | نجاح |
| 201 | Created | تم الإنشاء |
| 400 | Bad Request | طلب غير صالح |
| 401 | Unauthorized | غير مصرح |
| 403 | Forbidden | ممنوع (باقة غير كافية) |
| 404 | Not Found | غير موجود |
| 429 | Too Many Requests | تجاوز حد الطلبات |
| 500 | Internal Server Error | خطأ في الخادم |
| 503 | Service Unavailable | الخدمة غير متاحة |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "FIELD_NOT_FOUND",
    "message": "Field with ID 'xyz' was not found",
    "message_ar": "الحقل بالمعرف 'xyz' غير موجود",
    "details": {}
  },
  "request_id": "uuid-xxx"
}
```

### Dart Error Handler

```dart
class ApiErrorHandler {
  static AppException handleDioError(DioException error) {
    switch (error.response?.statusCode) {
      case 401:
        return UnauthorizedException('Session expired. Please login again.');
      case 403:
        return ForbiddenException('Your subscription does not include this feature.');
      case 429:
        final retryAfter = error.response?.headers.value('Retry-After');
        return RateLimitException('Too many requests. Retry after $retryAfter seconds.');
      case 500:
        return ServerException('Server error. Please try again later.');
      default:
        return UnknownException(error.message ?? 'Unknown error');
    }
  }
}
```

---

## Rate Limiting Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
Retry-After: 60
```

---

## Security Headers

جميع الاستجابات تتضمن:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Request-ID: uuid-xxx
```

---

## CORS Configuration

الأصول المسموح بها:

- `https://sahool.app`
- `https://www.sahool.app`
- `https://admin.sahool.app`
- `https://api.sahool.app`
- `https://staging.sahool.app`
- `http://localhost:3000` (Development)
- `http://localhost:5173` (Development)
- `http://localhost:8080` (Development)

---

## Best Practices

### 1. Caching

```dart
class CachedApiService {
  final Dio _dio;
  final Box _cache;

  Future<T> getCached<T>(
    String endpoint,
    Duration ttl,
    T Function(Map<String, dynamic>) fromJson,
  ) async {
    final cacheKey = endpoint.hashCode.toString();
    final cached = _cache.get(cacheKey);

    if (cached != null && cached['expiry'] > DateTime.now().millisecondsSinceEpoch) {
      return fromJson(cached['data']);
    }

    final response = await _dio.get(endpoint);
    _cache.put(cacheKey, {
      'data': response.data,
      'expiry': DateTime.now().add(ttl).millisecondsSinceEpoch,
    });

    return fromJson(response.data);
  }
}
```

### 2. Offline Support

```dart
class OfflineFirstService {
  final Dio _dio;
  final Box _offlineQueue;

  Future<void> queueRequest(String method, String endpoint, dynamic data) async {
    await _offlineQueue.add({
      'method': method,
      'endpoint': endpoint,
      'data': data,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  Future<void> syncOfflineQueue() async {
    final queue = _offlineQueue.values.toList();
    for (final request in queue) {
      try {
        await _dio.request(
          request['endpoint'],
          options: Options(method: request['method']),
          data: request['data'],
        );
        await _offlineQueue.delete(request.key);
      } catch (e) {
        // Keep in queue for next sync
      }
    }
  }
}
```

### 3. Retry Logic

```dart
class RetryInterceptor extends Interceptor {
  final int maxRetries;

  RetryInterceptor({this.maxRetries = 3});

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    final retryCount = err.requestOptions.extra['retryCount'] ?? 0;

    if (retryCount < maxRetries && _shouldRetry(err)) {
      await Future.delayed(Duration(seconds: pow(2, retryCount).toInt()));
      err.requestOptions.extra['retryCount'] = retryCount + 1;

      try {
        final response = await Dio().fetch(err.requestOptions);
        handler.resolve(response);
        return;
      } catch (e) {
        // Continue to next error handler
      }
    }

    handler.next(err);
  }

  bool _shouldRetry(DioException err) {
    return err.type == DioExceptionType.connectionError ||
           err.type == DioExceptionType.connectionTimeout ||
           err.response?.statusCode == 503;
  }
}
```

---

## Environment Configuration

```dart
// lib/core/config/environment.dart

enum Environment { development, staging, production }

class EnvironmentConfig {
  static Environment current = Environment.development;

  static String get baseUrl {
    switch (current) {
      case Environment.development:
        return 'http://localhost:8000';
      case Environment.staging:
        return 'https://staging-api.sahool.app';
      case Environment.production:
        return 'https://api.sahool.app';
    }
  }

  static String get wsUrl {
    switch (current) {
      case Environment.development:
        return 'ws://localhost:8081';
      case Environment.staging:
        return 'wss://staging-api.sahool.app/ws';
      case Environment.production:
        return 'wss://api.sahool.app/ws';
    }
  }
}
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SAHOOL API Quick Reference                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Base URL:     https://api.sahool.app                                        │
│ API Version:  v1                                                            │
│ Auth:         Bearer JWT Token                                              │
│ Content-Type: application/json                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                          STARTER TIER                                        │
│ /api/v1/fields          - Field management                                  │
│ /api/v1/weather         - Weather data                                      │
│ /api/v1/calendar        - Astronomical calendar                             │
│ /api/v1/advice          - Basic advisory                                    │
│ /api/v1/notifications   - Notifications                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                       PROFESSIONAL TIER                                      │
│ /api/v1/satellite       - Satellite imagery                                 │
│ /api/v1/ndvi            - NDVI analysis                                     │
│ /api/v1/crop-health     - AI crop health                                    │
│ /api/v1/irrigation      - Smart irrigation                                  │
│ /api/v1/yield           - Yield prediction                                  │
│ /api/v1/fertilizer      - Fertilizer advice                                 │
│ /api/v1/inventory       - Inventory management                              │
│ /api/v1/equipment       - Equipment tracking                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                        ENTERPRISE TIER                                       │
│ /api/v1/ai-advisor      - Multi-agent AI advisor                            │
│ /api/v1/iot             - IoT gateway                                       │
│ /api/v1/research        - Research management                               │
│ /api/v1/marketplace     - Agricultural marketplace                          │
│ /api/v1/billing         - Billing & payments                                │
│ /api/v1/disaster        - Disaster assessment                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                         SHARED SERVICES                                      │
│ /api/v1/ws              - WebSocket gateway                                 │
│ /api/v1/tasks           - Task management                                   │
│ /api/v1/alerts          - Alert system                                      │
│ /api/v1/chat            - Chat service                                      │
│ /health                 - Health check                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Contact & Support

- **Documentation**: https://docs.sahool.app
- **API Status**: https://status.sahool.app
- **Support**: support@sahool.com

---

*آخر تحديث: يناير 2026*
*Last Updated: January 2026*
