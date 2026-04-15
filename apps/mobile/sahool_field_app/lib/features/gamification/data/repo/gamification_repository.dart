/// SAHOOL Gamification Repository
/// مستودع بيانات الإنجازات

import 'package:dio/dio.dart';
import '../../../../core/contracts/api_endpoints.dart';
import '../../domain/models/achievement.dart';

/// مستودع الإنجازات
class GamificationRepository {
  final Dio _dio;

  GamificationRepository({Dio? dio}) : _dio = dio ?? Dio();

  /// جلب ملف الإنجازات للمستخدم
  Future<UserGamificationProfile> fetchProfile(String userId) async {
    try {
      final response = await _dio.get(GamificationEndpoints.profile(userId));
      return UserGamificationProfile.fromJson(
          response.data as Map<String, dynamic>);
    } on DioException {
      // Return mock profile for offline-first support
      return _mockProfile(userId);
    }
  }

  /// جلب لوحة المتصدرين
  Future<List<LeaderboardEntry>> fetchLeaderboard(
      LeaderboardPeriod period) async {
    try {
      final response = await _dio.get(
        GamificationEndpoints.leaderboard,
        queryParameters: {'period': period.name},
      );
      return (response.data as List)
          .map((e) => LeaderboardEntry.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException {
      // Return mock leaderboard for offline-first support
      return _mockLeaderboard();
    }
  }

  /// Mock profile for offline fallback
  UserGamificationProfile _mockProfile(String userId) {
    return UserGamificationProfile(
      userId: userId,
      totalPoints: 0,
      level: 1,
      rank: 'beginner',
      achievements: [],
      streaks: [],
      milestones: [],
      lastUpdated: DateTime.now(),
    );
  }

  /// Mock leaderboard for offline fallback
  List<LeaderboardEntry> _mockLeaderboard() {
    return [];
  }
}
