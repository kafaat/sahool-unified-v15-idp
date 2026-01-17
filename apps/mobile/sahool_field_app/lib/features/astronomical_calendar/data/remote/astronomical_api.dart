/// SAHOOL Astronomical Calendar API Client
/// عميل API التقويم الفلكي

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';
import '../../domain/entities/astronomical_entities.dart';

/// API Client للتقويم الفلكي
/// Routes through Kong Gateway on port 8000
class AstronomicalCalendarApi {
  final http.Client _client;
  final String? _authToken;

  AstronomicalCalendarApi({
    http.Client? client,
    String? authToken,
  })  : _client = client ?? http.Client(),
        _authToken = authToken;

  Map<String, String> get _headers => {
        ...ApiConfig.defaultHeaders,
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
      };

  /// Base URL for astronomical calendar via Kong Gateway
  /// Kong route: /api/v1/astronomy → astronomical-calendar-service
  String get _baseUrl => '${ApiConfig.baseUrl}/api/v1/astronomy';

  // ═══════════════════════════════════════════════════════════════════════════
  // التقويم اليومي
  // ═══════════════════════════════════════════════════════════════════════════

  /// الحصول على بيانات اليوم
  Future<DailyAstronomicalData> getToday() async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/v1/today'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return DailyAstronomicalData.fromJson(json);
    } else {
      throw AstronomicalApiException(
        'فشل جلب بيانات اليوم',
        statusCode: response.statusCode,
      );
    }
  }

  /// الحصول على بيانات تاريخ محدد
  Future<DailyAstronomicalData> getDate(String dateStr) async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/v1/date/$dateStr'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return DailyAstronomicalData.fromJson(json);
    } else {
      throw AstronomicalApiException(
        'فشل جلب بيانات التاريخ',
        statusCode: response.statusCode,
      );
    }
  }

  /// الحصول على التوقعات الأسبوعية
  Future<WeeklyForecast> getWeeklyForecast({String? startDate}) async {
    final uri = Uri.parse('$_baseUrl/v1/week').replace(
      queryParameters: startDate != null ? {'start_date': startDate} : null,
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return WeeklyForecast.fromJson(json);
    } else {
      throw AstronomicalApiException(
        'فشل جلب التوقعات الأسبوعية',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الفلك
  // ═══════════════════════════════════════════════════════════════════════════

  /// الحصول على مرحلة القمر
  Future<MoonPhase> getMoonPhase({String? dateStr}) async {
    final uri = Uri.parse('$_baseUrl/v1/moon-phase').replace(
      queryParameters: dateStr != null ? {'date_str': dateStr} : null,
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return MoonPhase.fromJson(json);
    } else {
      throw AstronomicalApiException(
        'فشل جلب مرحلة القمر',
        statusCode: response.statusCode,
      );
    }
  }

  /// الحصول على المنزلة القمرية
  Future<LunarMansion> getLunarMansion({String? dateStr}) async {
    final uri = Uri.parse('$_baseUrl/v1/lunar-mansion').replace(
      queryParameters: dateStr != null ? {'date_str': dateStr} : null,
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return LunarMansion.fromJson(json);
    } else {
      throw AstronomicalApiException(
        'فشل جلب المنزلة القمرية',
        statusCode: response.statusCode,
      );
    }
  }

  /// الحصول على قائمة المنازل القمرية
  Future<List<Map<String, dynamic>>> getLunarMansions() async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/v1/lunar-mansions'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return List<Map<String, dynamic>>.from(json['mansions'] ?? []);
    } else {
      throw AstronomicalApiException(
        'فشل جلب قائمة المنازل',
        statusCode: response.statusCode,
      );
    }
  }

  /// الحصول على التاريخ الهجري
  Future<HijriDate> getHijriDate({String? dateStr}) async {
    final uri = Uri.parse('$_baseUrl/v1/hijri').replace(
      queryParameters: dateStr != null ? {'date_str': dateStr} : null,
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return HijriDate.fromJson(json);
    } else {
      throw AstronomicalApiException(
        'فشل جلب التاريخ الهجري',
        statusCode: response.statusCode,
      );
    }
  }

  /// الحصول على البرج الشمسي
  Future<ZodiacInfo> getZodiac({String? dateStr}) async {
    final uri = Uri.parse('$_baseUrl/v1/zodiac').replace(
      queryParameters: dateStr != null ? {'date_str': dateStr} : null,
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return ZodiacInfo.fromJson(json);
    } else {
      throw AstronomicalApiException(
        'فشل جلب البرج',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // المحاصيل
  // ═══════════════════════════════════════════════════════════════════════════

  /// الحصول على تقويم محصول
  Future<CropCalendar> getCropCalendar(String cropName) async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/v1/crop-calendar/$cropName'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return CropCalendar.fromJson(json);
    } else {
      throw AstronomicalApiException(
        'فشل جلب تقويم المحصول',
        statusCode: response.statusCode,
      );
    }
  }

  /// الحصول على قائمة المحاصيل
  Future<List<Map<String, String>>> getSupportedCrops() async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/v1/crops'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return (json['crops'] as List)
          .map((c) => Map<String, String>.from(c))
          .toList();
    } else {
      throw AstronomicalApiException(
        'فشل جلب قائمة المحاصيل',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // البحث
  // ═══════════════════════════════════════════════════════════════════════════

  /// البحث عن أفضل الأيام لنشاط معين
  Future<BestDaysResult> getBestDays({
    required String activity,
    int days = 30,
  }) async {
    final uri = Uri.parse('$_baseUrl/v1/best-days').replace(
      queryParameters: {
        'activity': activity,
        'days': days.toString(),
      },
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return BestDaysResult.fromJson(json);
    } else {
      throw AstronomicalApiException(
        'فشل البحث عن أفضل الأيام',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // المراجع
  // ═══════════════════════════════════════════════════════════════════════════

  /// الحصول على الموسم الحالي
  Future<SeasonInfo> getCurrentSeason() async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/v1/current-season'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return SeasonInfo.fromJson(json);
    } else {
      throw AstronomicalApiException(
        'فشل جلب الموسم الحالي',
        statusCode: response.statusCode,
      );
    }
  }

  /// الحصول على قائمة المواسم
  Future<Map<String, dynamic>> getSeasons() async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/v1/seasons'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return json['seasons'] as Map<String, dynamic>;
    } else {
      throw AstronomicalApiException(
        'فشل جلب قائمة المواسم',
        statusCode: response.statusCode,
      );
    }
  }

  /// الحصول على قائمة الأشهر الهجرية
  Future<Map<String, dynamic>> getHijriMonths() async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/v1/hijri-months'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return json['months'] as Map<String, dynamic>;
    } else {
      throw AstronomicalApiException(
        'فشل جلب الأشهر الهجرية',
        statusCode: response.statusCode,
      );
    }
  }

  /// الحصول على الأبراج مع الخصوبة
  Future<Map<String, dynamic>> getZodiacFarming() async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/v1/zodiac-farming'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return json['zodiac_signs'] as Map<String, dynamic>;
    } else {
      throw AstronomicalApiException(
        'فشل جلب الأبراج',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // التكامل
  // ═══════════════════════════════════════════════════════════════════════════

  /// الحصول على بيانات متكاملة مع الطقس
  Future<Map<String, dynamic>> getIntegratedData({
    required String locationId,
    String? dateStr,
  }) async {
    final queryParams = <String, String>{'location_id': locationId};
    if (dateStr != null) queryParams['date_str'] = dateStr;

    final uri = Uri.parse('$_baseUrl/v1/integration/weather').replace(
      queryParameters: queryParams,
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw AstronomicalApiException(
        'فشل جلب البيانات المتكاملة',
        statusCode: response.statusCode,
      );
    }
  }

  void dispose() {
    _client.close();
  }
}

/// استثناء API التقويم الفلكي
class AstronomicalApiException implements Exception {
  final String message;
  final int? statusCode;

  AstronomicalApiException(this.message, {this.statusCode});

  @override
  String toString() =>
      'AstronomicalApiException: $message (code: $statusCode)';
}
