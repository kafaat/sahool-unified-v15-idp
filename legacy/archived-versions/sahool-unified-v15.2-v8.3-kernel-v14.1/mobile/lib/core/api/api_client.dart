// ============================================
// SAHOOL - API Client
// عميل الاتصال بالخادم
// ============================================

import 'package:dio/dio.dart';

class ApiClient {
  final Dio _dio;

  ApiClient(this._dio);

  // ============================================
  // AUTH
  // ============================================

  Future<Response> login(String email, String password) async {
    return _dio.post('/auth/login', data: {
      'email': email,
      'password': password,
    });
  }

  Future<Response> register({
    required String email,
    required String password,
    required String fullName,
    String? phone,
  }) async {
    return _dio.post('/auth/register', data: {
      'email': email,
      'password': password,
      'fullName': fullName,
      'phone': phone,
    });
  }

  Future<Response> refreshToken(String refreshToken) async {
    return _dio.post('/auth/refresh', data: {
      'refreshToken': refreshToken,
    });
  }

  Future<Response> logout(String refreshToken) async {
    return _dio.post('/auth/logout', data: {
      'refreshToken': refreshToken,
    });
  }

  Future<Response> getProfile() async {
    return _dio.get('/auth/me');
  }

  // ============================================
  // FIELDS
  // ============================================

  Future<Response> getFields() async {
    return _dio.get('/fields');
  }

  Future<Response> getField(String id) async {
    return _dio.get('/fields/$id');
  }

  Future<Response> createField(Map<String, dynamic> data) async {
    return _dio.post('/fields', data: data);
  }

  Future<Response> updateField(String id, Map<String, dynamic> data) async {
    return _dio.put('/fields/$id', data: data);
  }

  Future<Response> deleteField(String id) async {
    return _dio.delete('/fields/$id');
  }

  // ============================================
  // CALENDAR
  // ============================================

  Future<Response> getCurrentNaw() async {
    return _dio.get('/calendar/current');
  }

  Future<Response> getNawByDate(String date) async {
    return _dio.get('/calendar/date/$date');
  }

  Future<Response> getAllAnwa() async {
    return _dio.get('/calendar/anwa');
  }

  Future<Response> getCropRecommendations(String cropName) async {
    return _dio.get('/calendar/crop/$cropName');
  }

  // ============================================
  // ADVISOR
  // ============================================

  Future<Response> getAgents() async {
    return _dio.get('/advisor/agents');
  }

  Future<Response> consultAgent(String agentId, String query, Map<String, dynamic> context) async {
    return _dio.post('/advisor/consult/$agentId', data: {
      'query': query,
      'context': context,
    });
  }

  Future<Response> getFieldRecommendations(String fieldId) async {
    return _dio.post('/advisor/field/$fieldId/recommend');
  }

  // ============================================
  // TASKS
  // ============================================

  Future<Response> getTasks({String? status, String? fieldId}) async {
    return _dio.get('/tasks', queryParameters: {
      if (status != null) 'status': status,
      if (fieldId != null) 'fieldId': fieldId,
    });
  }

  Future<Response> createTask(Map<String, dynamic> data) async {
    return _dio.post('/tasks', data: data);
  }

  Future<Response> updateTask(String id, Map<String, dynamic> data) async {
    return _dio.put('/tasks/$id', data: data);
  }

  Future<Response> completeTask(String id, {String? notes}) async {
    return _dio.post('/tasks/$id/complete', data: {
      'notes': notes,
    });
  }

  // ============================================
  // WEATHER
  // ============================================

  Future<Response> getCurrentWeather(String locationId) async {
    return _dio.get('/weather/current/$locationId');
  }

  Future<Response> getWeatherForecast(String locationId) async {
    return _dio.get('/weather/forecast/$locationId');
  }

  // ============================================
  // NDVI
  // ============================================

  Future<Response> getFieldNDVI(String fieldId) async {
    return _dio.get('/ndvi/field/$fieldId');
  }

  Future<Response> getNDVIHistory(String fieldId, {int? limit}) async {
    return _dio.get('/ndvi/field/$fieldId/history', queryParameters: {
      if (limit != null) 'limit': limit,
    });
  }

  // ============================================
  // ALERTS
  // ============================================

  Future<Response> getAlerts({String? status}) async {
    return _dio.get('/alerts', queryParameters: {
      if (status != null) 'status': status,
    });
  }

  Future<Response> acknowledgeAlert(String id) async {
    return _dio.post('/alerts/$id/acknowledge');
  }
}
