import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/config/api_config.dart';
import '../../../../core/utils/app_logger.dart';
import '../../domain/models/achievement.dart';

// =============================================================================
// Repository
// =============================================================================

/// Gamification Repository
/// مستودع بيانات نظام الإنجازات
///
/// Architecture:
/// 1. Try GET /api/v1/gamification/profile from advisory-service (port 8093)
/// 2. On failure (offline/unavailable), fall back to built-in mock data
class GamificationRepository {
  final Dio _dio;

  GamificationRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  /// جلب ملف المستخدم من API أو الرجوع للبيانات المحلية
  Future<UserGamificationProfile> fetchProfile(String userId) async {
    try {
      final response = await _dio.get('/api/v1/gamification/profile/$userId');
      final data = response.data as Map<String, dynamic>;
      return _parseProfile(data);
    } on DioException catch (e) {
      AppLogger.w(
        'Gamification API unavailable (${e.type.name}), using local data',
        tag: 'GAMIFICATION',
      );
      return _buildMockProfile();
    } catch (e) {
      AppLogger.w('Gamification parse error: $e, using local data', tag: 'GAMIFICATION');
      return _buildMockProfile();
    }
  }

  /// جلب لوحة المتصدرين من API أو الرجوع للبيانات المحلية
  Future<List<LeaderboardEntry>> fetchLeaderboard(LeaderboardPeriod period) async {
    try {
      final response = await _dio.get(
        '/api/v1/gamification/leaderboard',
        queryParameters: {'period': period.name},
      );
      final List data = response.data as List;
      return data
          .map((e) => _parseLeaderboardEntry(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      AppLogger.w(
        'Leaderboard API unavailable (${e.type.name}), using local data',
        tag: 'GAMIFICATION',
      );
      return _buildMockLeaderboard();
    } catch (e) {
      AppLogger.w('Leaderboard parse error: $e, using local data', tag: 'GAMIFICATION');
      return _buildMockLeaderboard();
    }
  }

  UserGamificationProfile _parseProfile(Map<String, dynamic> json) {
    final achievementsList = (json['achievements'] as List? ?? [])
        .map((a) => _parseAchievement(a as Map<String, dynamic>))
        .toList();
    final streaksList = (json['streaks'] as List? ?? [])
        .map((s) => _parseStreak(s as Map<String, dynamic>))
        .toList();
    return UserGamificationProfile(
      userId: json['userId'] as String? ?? '',
      totalPoints: (json['totalPoints'] as num?)?.toInt() ?? 0,
      level: (json['level'] as num?)?.toInt() ?? 1,
      rank: json['rank'] as String? ?? 'مزارع جديد',
      achievements: achievementsList,
      streaks: streaksList,
      milestones: const [],
      lastUpdated: json['lastUpdated'] != null
          ? DateTime.tryParse(json['lastUpdated'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  Achievement _parseAchievement(Map<String, dynamic> json) {
    return Achievement(
      id: json['id'] as String,
      title: json['title'] as String? ?? '',
      titleEn: json['titleEn'] as String?,
      description: json['description'] as String? ?? '',
      category: _parseCategory(json['category'] as String?),
      tier: _parseTier(json['tier'] as String?),
      iconName: json['iconName'] as String? ?? 'star',
      pointsValue: (json['pointsValue'] as num?)?.toInt() ?? 0,
      progress: json['progress'] != null
          ? _parseProgress(json['progress'] as Map<String, dynamic>)
          : null,
      unlockedAt: json['unlockedAt'] != null
          ? DateTime.tryParse(json['unlockedAt'] as String)
          : null,
    );
  }

  AchievementProgress? _parseProgress(Map<String, dynamic> json) {
    return AchievementProgress(
      current: (json['current'] as num?)?.toInt() ?? 0,
      target: (json['target'] as num?)?.toInt() ?? 100,
      unit: json['unit'] as String? ?? '',
    );
  }

  Streak _parseStreak(Map<String, dynamic> json) {
    return Streak(
      id: json['id'] as String,
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      type: _parseStreakType(json['type'] as String?),
      currentDays: (json['currentDays'] as num?)?.toInt() ?? 0,
      bestDays: (json['bestDays'] as num?)?.toInt() ?? 0,
      lastActivityDate: json['lastActivityDate'] != null
          ? DateTime.tryParse(json['lastActivityDate'] as String) ?? DateTime.now()
          : DateTime.now(),
      isActive: json['isActive'] as bool? ?? false,
    );
  }

  LeaderboardEntry _parseLeaderboardEntry(Map<String, dynamic> json) {
    return LeaderboardEntry(
      userId: json['userId'] as String,
      userName: json['userName'] as String? ?? '',
      rank: (json['rank'] as num?)?.toInt() ?? 0,
      points: (json['points'] as num?)?.toInt() ?? 0,
      level: (json['level'] as num?)?.toInt() ?? 1,
      isCurrentUser: json['isCurrentUser'] as bool? ?? false,
    );
  }

  AchievementCategory _parseCategory(String? value) {
    switch (value) {
      case 'irrigation': return AchievementCategory.irrigation;
      case 'scouting': return AchievementCategory.scouting;
      case 'monitoring': return AchievementCategory.monitoring;
      case 'teamwork': return AchievementCategory.teamwork;
      case 'learning': return AchievementCategory.learning;
      case 'tasks': return AchievementCategory.tasks;
      default: return AchievementCategory.tasks;
    }
  }

  AchievementTier _parseTier(String? value) {
    switch (value) {
      case 'bronze': return AchievementTier.bronze;
      case 'silver': return AchievementTier.silver;
      case 'gold': return AchievementTier.gold;
      case 'platinum': return AchievementTier.platinum;
      case 'diamond': return AchievementTier.diamond;
      default: return AchievementTier.bronze;
    }
  }

  StreakType _parseStreakType(String? value) {
    switch (value) {
      case 'dailyLogin': return StreakType.dailyLogin;
      case 'irrigationSchedule': return StreakType.irrigationSchedule;
      case 'taskCompletion': return StreakType.taskCompletion;
      default: return StreakType.dailyLogin;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Mock / offline fallback data
  // ─────────────────────────────────────────────────────────────────────────

  UserGamificationProfile _buildMockProfile() {
    return UserGamificationProfile(
      userId: 'user-001',
      totalPoints: 3750,
      level: 3,
      rank: 'مزارع متقدم',
      achievements: _buildMockAchievements(),
      streaks: _buildMockStreaks(),
      milestones: const [],
      lastUpdated: DateTime.now(),
    );
  }

  List<Achievement> _buildMockAchievements() {
    return const [
      Achievement(
        id: 'ach-001', title: 'سيد الري', titleEn: 'Irrigation Master',
        description: 'أكمل 50 دورة ري بنجاح',
        category: AchievementCategory.irrigation, tier: AchievementTier.gold,
        iconName: 'water_drop', pointsValue: 500,
        progress: AchievementProgress(current: 50, target: 50, unit: 'دورة'),
        unlockedAt: null,
      ),
      Achievement(
        id: 'ach-002', title: 'عين الصقر', titleEn: 'Eagle Eye',
        description: 'اكتشف 10 آفات مبكرا',
        category: AchievementCategory.scouting, tier: AchievementTier.silver,
        iconName: 'pest_control', pointsValue: 300,
        progress: AchievementProgress(current: 7, target: 10, unit: 'آفة'),
      ),
      Achievement(
        id: 'ach-003', title: 'الحارس الأمين', titleEn: 'Faithful Guardian',
        description: 'راقب حقولك 30 يوما متتاليا',
        category: AchievementCategory.monitoring, tier: AchievementTier.platinum,
        iconName: 'visibility', pointsValue: 750,
        progress: AchievementProgress(current: 22, target: 30, unit: 'يوم'),
      ),
      Achievement(
        id: 'ach-004', title: 'فريق القمة', titleEn: 'Top Team',
        description: 'شارك في 5 مهام جماعية',
        category: AchievementCategory.teamwork, tier: AchievementTier.bronze,
        iconName: 'groups', pointsValue: 200,
        progress: AchievementProgress(current: 2, target: 5, unit: 'مهمة'),
      ),
      Achievement(
        id: 'ach-005', title: 'طالب العلم', titleEn: 'Knowledge Seeker',
        description: 'أكمل 10 دروس تعليمية',
        category: AchievementCategory.learning, tier: AchievementTier.diamond,
        iconName: 'school', pointsValue: 1000,
        progress: AchievementProgress(current: 3, target: 10, unit: 'درس'),
      ),
      Achievement(
        id: 'ach-006', title: 'منجز المهام', titleEn: 'Task Crusher',
        description: 'أنهِ 100 مهمة ميدانية',
        category: AchievementCategory.tasks, tier: AchievementTier.gold,
        iconName: 'task_alt', pointsValue: 500,
        progress: AchievementProgress(current: 100, target: 100, unit: 'مهمة'),
      ),
    ];
  }

  List<Streak> _buildMockStreaks() {
    return [
      Streak(
        id: 'str-001', title: 'تسجيل يومي', description: 'سجل دخولك كل يوم',
        type: StreakType.dailyLogin, currentDays: 14, bestDays: 21,
        lastActivityDate: DateTime.now(), isActive: true,
      ),
      Streak(
        id: 'str-002', title: 'ري منتظم', description: 'نفذ جدول الري يوميا',
        type: StreakType.irrigationSchedule, currentDays: 7, bestDays: 30,
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 22)),
        isActive: true,
      ),
      Streak(
        id: 'str-003', title: 'إكمال المهام', description: 'أنهِ مهمة واحدة يوميا',
        type: StreakType.taskCompletion, currentDays: 0, bestDays: 12,
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 26)),
        isActive: false,
      ),
    ];
  }

  List<LeaderboardEntry> _buildMockLeaderboard() {
    return const [
      LeaderboardEntry(userId: 'u1', userName: 'أحمد الراشد', rank: 1, points: 8200, level: 8),
      LeaderboardEntry(userId: 'u2', userName: 'محمد العلي', rank: 2, points: 7650, level: 7),
      LeaderboardEntry(userId: 'u3', userName: 'خالد السعيد', rank: 3, points: 6300, level: 6),
      LeaderboardEntry(userId: 'user-001', userName: 'أنت', rank: 4, points: 3750, level: 3, isCurrentUser: true),
      LeaderboardEntry(userId: 'u5', userName: 'فهد الحربي', rank: 5, points: 3100, level: 3),
      LeaderboardEntry(userId: 'u6', userName: 'سعد المطيري', rank: 6, points: 2800, level: 2),
    ];
  }
}

// =============================================================================
// Provider for repository
// =============================================================================

final gamificationRepositoryProvider = Provider<GamificationRepository>((ref) {
  return GamificationRepository();
});

/// Gamification state
/// حالة نظام الإنجازات
class GamificationState {
  final UserGamificationProfile? profile;
  final List<Achievement> achievements;
  final List<Streak> streaks;
  final List<LeaderboardEntry> leaderboard;
  final LeaderboardPeriod leaderboardPeriod;
  final bool isLoading;
  final String? error;

  const GamificationState({
    this.profile,
    this.achievements = const [],
    this.streaks = const [],
    this.leaderboard = const [],
    this.leaderboardPeriod = LeaderboardPeriod.weekly,
    this.isLoading = false,
    this.error,
  });

  GamificationState copyWith({
    UserGamificationProfile? profile,
    List<Achievement>? achievements,
    List<Streak>? streaks,
    List<LeaderboardEntry>? leaderboard,
    LeaderboardPeriod? leaderboardPeriod,
    bool? isLoading,
    String? error,
  }) {
    return GamificationState(
      profile: profile ?? this.profile,
      achievements: achievements ?? this.achievements,
      streaks: streaks ?? this.streaks,
      leaderboard: leaderboard ?? this.leaderboard,
      leaderboardPeriod: leaderboardPeriod ?? this.leaderboardPeriod,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Gamification StateNotifier
/// مزود نظام الإنجازات
class GamificationNotifier extends StateNotifier<GamificationState> {
  final GamificationRepository _repository;

  GamificationNotifier(this._repository) : super(const GamificationState());

  /// Load user gamification profile - تحميل ملف المستخدم
  /// يحاول جلب البيانات من API أولاً ثم يرجع للبيانات المحلية
  Future<void> loadProfile({String userId = 'user-001'}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final profile = await _repository.fetchProfile(userId);
      state = state.copyWith(
        profile: profile,
        achievements: profile.achievements,
        streaks: profile.streaks,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'فشل تحميل الملف الشخصي');
    }
  }

  /// Claim achievement reward - استلام مكافأة الإنجاز
  Future<void> claimReward(String achievementId) async {
    final updated = state.achievements.map((a) {
      if (a.id == achievementId && a.isUnlocked) {
        return Achievement(
          id: a.id,
          title: a.title,
          titleEn: a.titleEn,
          description: a.description,
          category: a.category,
          tier: a.tier,
          iconName: a.iconName,
          pointsValue: a.pointsValue,
          progress: a.progress,
          unlockedAt: a.unlockedAt,
        );
      }
      return a;
    }).toList();
    state = state.copyWith(achievements: updated);
  }

  /// Load leaderboard - تحميل لوحة المتصدرين
  /// يحاول جلب البيانات من API أولاً ثم يرجع للبيانات المحلية
  Future<void> getLeaderboard(LeaderboardPeriod period) async {
    state = state.copyWith(isLoading: true, leaderboardPeriod: period);
    try {
      final leaderboard = await _repository.fetchLeaderboard(period);
      state = state.copyWith(
        leaderboard: leaderboard,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        leaderboard: _buildMockLeaderboard(),
        isLoading: false,
      );
    }
  }

  /// Update streak - تحديث السلسلة المتتابعة
  Future<void> updateStreak(String streakId) async {
    final updated = state.streaks.map((s) {
      if (s.id == streakId) {
        return Streak(
          id: s.id,
          title: s.title,
          description: s.description,
          type: s.type,
          currentDays: s.currentDays + 1,
          bestDays: s.currentDays + 1 > s.bestDays
              ? s.currentDays + 1
              : s.bestDays,
          lastActivityDate: DateTime.now(),
          isActive: true,
        );
      }
      return s;
    }).toList();
    state = state.copyWith(streaks: updated);
  }

  UserGamificationProfile _buildMockProfile() {
    return UserGamificationProfile(
      userId: 'user-001',
      totalPoints: 3750,
      level: 3,
      rank: 'مزارع متقدم',
      achievements: _buildMockAchievements(),
      streaks: _buildMockStreaks(),
      milestones: const [],
      lastUpdated: DateTime.now(),
    );
  }

  List<Achievement> _buildMockAchievements() {
    return const [
      Achievement(
        id: 'ach-001', title: 'سيد الري', titleEn: 'Irrigation Master',
        description: 'أكمل 50 دورة ري بنجاح',
        category: AchievementCategory.irrigation, tier: AchievementTier.gold,
        iconName: 'water_drop', pointsValue: 500,
        progress: AchievementProgress(current: 50, target: 50, unit: 'دورة'),
        unlockedAt: null,
      ),
      Achievement(
        id: 'ach-002', title: 'عين الصقر', titleEn: 'Eagle Eye',
        description: 'اكتشف 10 آفات مبكرا',
        category: AchievementCategory.scouting, tier: AchievementTier.silver,
        iconName: 'pest_control', pointsValue: 300,
        progress: AchievementProgress(current: 7, target: 10, unit: 'آفة'),
      ),
      Achievement(
        id: 'ach-003', title: 'الحارس الأمين', titleEn: 'Faithful Guardian',
        description: 'راقب حقولك 30 يوما متتاليا',
        category: AchievementCategory.monitoring, tier: AchievementTier.platinum,
        iconName: 'visibility', pointsValue: 750,
        progress: AchievementProgress(current: 22, target: 30, unit: 'يوم'),
      ),
      Achievement(
        id: 'ach-004', title: 'فريق القمة', titleEn: 'Top Team',
        description: 'شارك في 5 مهام جماعية',
        category: AchievementCategory.teamwork, tier: AchievementTier.bronze,
        iconName: 'groups', pointsValue: 200,
        progress: AchievementProgress(current: 2, target: 5, unit: 'مهمة'),
      ),
      Achievement(
        id: 'ach-005', title: 'طالب العلم', titleEn: 'Knowledge Seeker',
        description: 'أكمل 10 دروس تعليمية',
        category: AchievementCategory.learning, tier: AchievementTier.diamond,
        iconName: 'school', pointsValue: 1000,
        progress: AchievementProgress(current: 3, target: 10, unit: 'درس'),
      ),
      Achievement(
        id: 'ach-006', title: 'منجز المهام', titleEn: 'Task Crusher',
        description: 'أنهِ 100 مهمة ميدانية',
        category: AchievementCategory.tasks, tier: AchievementTier.gold,
        iconName: 'task_alt', pointsValue: 500,
        progress: AchievementProgress(current: 100, target: 100, unit: 'مهمة'),
      ),
    ];
  }

  List<Streak> _buildMockStreaks() {
    return [
      Streak(
        id: 'str-001', title: 'تسجيل يومي', description: 'سجل دخولك كل يوم',
        type: StreakType.dailyLogin, currentDays: 14, bestDays: 21,
        lastActivityDate: DateTime.now(), isActive: true,
      ),
      Streak(
        id: 'str-002', title: 'ري منتظم', description: 'نفذ جدول الري يوميا',
        type: StreakType.irrigationSchedule, currentDays: 7, bestDays: 30,
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 22)),
        isActive: true,
      ),
      Streak(
        id: 'str-003', title: 'إكمال المهام', description: 'أنهِ مهمة واحدة يوميا',
        type: StreakType.taskCompletion, currentDays: 0, bestDays: 12,
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 26)),
        isActive: false,
      ),
    ];
  }

  List<LeaderboardEntry> _buildMockLeaderboard() {
    return const [
      LeaderboardEntry(userId: 'u1', userName: 'أحمد الراشد', rank: 1, points: 8200, level: 8),
      LeaderboardEntry(userId: 'u2', userName: 'محمد العلي', rank: 2, points: 7650, level: 7),
      LeaderboardEntry(userId: 'u3', userName: 'خالد السعيد', rank: 3, points: 6300, level: 6),
      LeaderboardEntry(userId: 'user-001', userName: 'أنت', rank: 4, points: 3750, level: 3, isCurrentUser: true),
      LeaderboardEntry(userId: 'u5', userName: 'فهد الحربي', rank: 5, points: 3100, level: 3),
      LeaderboardEntry(userId: 'u6', userName: 'سعد المطيري', rank: 6, points: 2800, level: 2),
    ];
  }
}

/// Provider - المزود
final gamificationProvider =
    StateNotifierProvider.autoDispose<GamificationNotifier, GamificationState>(
  (ref) => GamificationNotifier(ref.read(gamificationRepositoryProvider)),
);
