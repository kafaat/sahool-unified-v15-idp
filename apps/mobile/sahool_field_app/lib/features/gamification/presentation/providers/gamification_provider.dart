/// SAHOOL Gamification Provider
/// مزود بيانات الإنجازات

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/repo/gamification_repository.dart';
import '../../domain/models/achievement.dart';

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

/// مزود حالة الإنجازات
class GamificationNotifier extends StateNotifier<GamificationState> {
  final GamificationRepository _repository;

  GamificationNotifier(this._repository) : super(const GamificationState());

  /// تحميل ملف الإنجازات
  Future<void> loadProfile({String userId = 'user-001'}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final profile = await _repository.fetchProfile(userId);
      state = state.copyWith(
        isLoading: false,
        profile: profile,
        achievements: profile.achievements,
        streaks: profile.streaks,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// المطالبة بمكافأة إنجاز
  Future<void> claimReward(String achievementId) async {
    final achievements = List<Achievement>.from(state.achievements);
    final index = achievements.indexWhere((a) => a.id == achievementId);
    if (index != -1 && !achievements[index].isUnlocked) {
      achievements[index] = Achievement(
        id: achievements[index].id,
        title: achievements[index].title,
        titleEn: achievements[index].titleEn,
        description: achievements[index].description,
        category: achievements[index].category,
        tier: achievements[index].tier,
        iconName: achievements[index].iconName,
        pointsValue: achievements[index].pointsValue,
        progress: achievements[index].progress,
        unlockedAt: DateTime.now(),
      );
      state = state.copyWith(achievements: achievements);
    }
  }

  /// جلب لوحة المتصدرين
  Future<void> getLeaderboard(LeaderboardPeriod period) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final leaderboard = await _repository.fetchLeaderboard(period);
      state = state.copyWith(
        isLoading: false,
        leaderboard: leaderboard,
        leaderboardPeriod: period,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// تحديث سلسلة متتابعة
  Future<void> updateStreak(String streakId) async {
    final streaks = List<Streak>.from(state.streaks);
    final index = streaks.indexWhere((s) => s.id == streakId);
    if (index != -1) {
      final streak = streaks[index];
      final newCurrentDays = streak.currentDays + 1;
      final newBestDays =
          newCurrentDays > streak.bestDays ? newCurrentDays : streak.bestDays;
      streaks[index] = Streak(
        id: streak.id,
        title: streak.title,
        description: streak.description,
        type: streak.type,
        currentDays: newCurrentDays,
        bestDays: newBestDays,
        lastActivityDate: DateTime.now(),
        isActive: true,
      );
      state = state.copyWith(streaks: streaks);
    }
  }
}

/// Gamification Repository Provider
final gamificationRepositoryProvider = Provider<GamificationRepository>((ref) {
  return GamificationRepository();
});

/// Gamification State Notifier Provider
final gamificationNotifierProvider =
    StateNotifierProvider<GamificationNotifier, GamificationState>((ref) {
  final repo = ref.watch(gamificationRepositoryProvider);
  return GamificationNotifier(repo);
});
