import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/models/achievement.dart';

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
  GamificationNotifier() : super(const GamificationState());

  /// Load user gamification profile - تحميل ملف المستخدم
  Future<void> loadProfile() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      // Simulate network delay
      await Future<void>.delayed(const Duration(milliseconds: 600));
      final profile = _buildMockProfile();
      state = state.copyWith(
        profile: profile,
        achievements: profile.achievements,
        streaks: profile.streaks,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
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
  Future<void> getLeaderboard(LeaderboardPeriod period) async {
    state = state.copyWith(isLoading: true, leaderboardPeriod: period);
    await Future<void>.delayed(const Duration(milliseconds: 400));
    state = state.copyWith(
      leaderboard: _buildMockLeaderboard(),
      isLoading: false,
    );
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
  (ref) => GamificationNotifier(),
);
