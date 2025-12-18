// ============================================
// SAHOOL - Auth Interceptor
// معترض المصادقة للطلبات
// ============================================

import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthInterceptor extends Interceptor {
  final _storage = const FlutterSecureStorage();
  
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // Skip auth for public endpoints
    final publicEndpoints = [
      '/auth/login',
      '/auth/register',
      '/auth/forgot-password',
      '/auth/reset-password',
      '/public/',
    ];

    final isPublic = publicEndpoints.any((ep) => options.path.contains(ep));
    
    if (!isPublic) {
      final accessToken = await _storage.read(key: _accessTokenKey);
      if (accessToken != null) {
        options.headers['Authorization'] = 'Bearer $accessToken';
      }
    }

    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Token expired, try to refresh
      final refreshed = await _refreshToken();
      
      if (refreshed) {
        // Retry the original request
        final accessToken = await _storage.read(key: _accessTokenKey);
        err.requestOptions.headers['Authorization'] = 'Bearer $accessToken';
        
        try {
          final response = await Dio().fetch(err.requestOptions);
          handler.resolve(response);
          return;
        } catch (e) {
          // Refresh failed, logout
          await _logout();
        }
      } else {
        await _logout();
      }
    }
    
    handler.next(err);
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.read(key: _refreshTokenKey);
      if (refreshToken == null) return false;

      final dio = Dio();
      final response = await dio.post(
        'http://localhost:3000/api/v1/auth/refresh',
        data: {'refreshToken': refreshToken},
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        await _storage.write(key: _accessTokenKey, value: data['accessToken']);
        await _storage.write(key: _refreshTokenKey, value: data['refreshToken']);
        return true;
      }
      
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<void> _logout() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
    // TODO: Navigate to login screen
  }

  // ============================================
  // Static methods for token management
  // ============================================

  static Future<void> saveTokens(String accessToken, String refreshToken) async {
    const storage = FlutterSecureStorage();
    await storage.write(key: _accessTokenKey, value: accessToken);
    await storage.write(key: _refreshTokenKey, value: refreshToken);
  }

  static Future<void> clearTokens() async {
    const storage = FlutterSecureStorage();
    await storage.delete(key: _accessTokenKey);
    await storage.delete(key: _refreshTokenKey);
  }

  static Future<bool> hasValidToken() async {
    const storage = FlutterSecureStorage();
    final token = await storage.read(key: _accessTokenKey);
    return token != null;
  }
}
