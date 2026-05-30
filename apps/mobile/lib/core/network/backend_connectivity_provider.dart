import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/env_config.dart';

/// Checks if the backend (Kong gateway) is reachable.
/// Returns true if any HTTP response is received, false on connection error.
final backendConnectivityProvider = FutureProvider<bool>((ref) async {
  final baseUrl = EnvConfig.apiBaseUrl; // e.g. http://localhost:8000
  final url = '$baseUrl/api/v1/auth/login';

  try {
    final dio = Dio(BaseOptions(
      connectTimeout: const Duration(seconds: 8),
      receiveTimeout: const Duration(seconds: 8),
      validateStatus: (_) => true, // Accept any HTTP status — we just want a response
    ));
    await dio.get(url);
    return true;
  } on DioException catch (e) {
    // Connection-level errors mean the server is not reachable
    if (e.type == DioExceptionType.connectionError ||
        e.type == DioExceptionType.connectionTimeout) {
      return false;
    }
    // Any other error (4xx, 5xx, receive timeout) still means the server responded
    if (e.response != null) return true;
    return false;
  } catch (_) {
    return false;
  }
});
