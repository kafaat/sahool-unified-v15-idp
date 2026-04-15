import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/gamification/presentation/providers/gamification_provider.dart';
import 'package:sahool_field_app/features/gamification/data/repo/gamification_repository.dart';
import 'package:sahool_field_app/features/gamification/domain/models/achievement.dart';

class MockGamificationRepository extends Mock
    implements GamificationRepository {}

void main() {
  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  Achievement _makeAchievement({
    String id = 'ach-001',
    bool unlocked = false,
  }) {
    return Achievement(
      id: id,
      title: 'إنجاز',
      titleEn: 'Achievement',
      description: 'Test achievement',
      category: AchievementCategory.irrigation,
      tier: AchievementTier.gold,
      iconName: 'water_drop',
      pointsValue: 500,
      progress: const AchievementProgress(current: 50, target: 100, unit: 'tasks'),
      unlockedAt: unlocked ? DateTime(2026, 1, 1) : null,
    );
  }

  Streak _makeStreak({
    String id = 'streak-001',
    int currentDays = 5,
    int bestDays = 10,
    bool isActive = true,
  }) {
    return Streak(
      id: id,
      title: 'Daily Login',
      description: 'Log in daily',
      type: StreakType.dailyLogin,
      currentDays: currentDays,
      bestDays: bestDays,
      lastActivityDate: DateTime.now(),
      isActive: isActive,
    );
  }

  UserGamificationProfile _makeProfile({
    String userId = 'user-001',
    List<Achievement>? achievements,
    List<Streak>? streaks,
  }) {
    return UserGamificationProfile(
      userId: userId,
      totalPoints: 2500,
      level: 2,
      rank: 'intermediate',
      achievements: achievements ?? [_makeAchievement(), _makeAchievement(id: 'ach-002', unlocked: true)],
      streaks: streaks ?? [_makeStreak()],
      milestones: const [],
      lastUpdated: DateTime(2026, 3, 15),
    );
  }

  List<LeaderboardEntry> _makeLeaderboard() {
    return [
      const LeaderboardEntry(
        userId: 'user-001',
        userName: 'Ahmed',
        rank: 1,
        points: 5000,
        level: 5,
        isCurrentUser: true,
      ),
      const LeaderboardEntry(
        userId: 'user-002',
        userName: 'Ali',
        rank: 2,
        points: 4000,
        level: 4,
      ),
    ];
  }

  // ---------------------------------------------------------------------------
  // GamificationState
  // ---------------------------------------------------------------------------
  group('GamificationState', () {
    test('default state has correct defaults', () {
      const state = GamificationState();

      expect(state.profile, isNull);
      expect(state.achievements, isEmpty);
      expect(state.streaks, isEmpty);
      expect(state.leaderboard, isEmpty);
      expect(state.leaderboardPeriod, LeaderboardPeriod.weekly);
      expect(state.isLoading, false);
      expect(state.error, isNull);
    });

    test('copyWith preserves values when no arguments are passed', () {
      final state = GamificationState(
        profile: _makeProfile(),
        achievements: [_makeAchievement()],
        streaks: [_makeStreak()],
        leaderboard: _makeLeaderboard(),
        leaderboardPeriod: LeaderboardPeriod.monthly,
        isLoading: true,
        error: 'some error',
      );

      final copied = state.copyWith();

      expect(copied.profile, state.profile);
      expect(copied.achievements, state.achievements);
      expect(copied.streaks, state.streaks);
      expect(copied.leaderboard, state.leaderboard);
      expect(copied.leaderboardPeriod, LeaderboardPeriod.monthly);
      expect(copied.isLoading, true);
      // Note: copyWith passes null for error when not specified, clearing it
    });

    test('copyWith overrides specific values', () {
      const state = GamificationState(isLoading: false);
      final copied = state.copyWith(isLoading: true, error: 'new error');

      expect(copied.isLoading, true);
      expect(copied.error, 'new error');
    });

    test('copyWith can change leaderboardPeriod', () {
      const state = GamificationState(leaderboardPeriod: LeaderboardPeriod.weekly);
      final copied = state.copyWith(leaderboardPeriod: LeaderboardPeriod.daily);

      expect(copied.leaderboardPeriod, LeaderboardPeriod.daily);
    });

    test('copyWith clears error when not specified', () {
      const state = GamificationState(error: 'old error');
      final copied = state.copyWith(isLoading: false);

      // The copyWith implementation sets error to the passed value (null by default)
      expect(copied.error, isNull);
    });
  });

  // ---------------------------------------------------------------------------
  // GamificationNotifier
  // ---------------------------------------------------------------------------
  group('GamificationNotifier', () {
    late MockGamificationRepository mockRepo;
    late GamificationNotifier notifier;

    setUp(() {
      mockRepo = MockGamificationRepository();
      notifier = GamificationNotifier(mockRepo);
    });

    test('initial state is default GamificationState', () {
      expect(notifier.state.profile, isNull);
      expect(notifier.state.achievements, isEmpty);
      expect(notifier.state.streaks, isEmpty);
      expect(notifier.state.leaderboard, isEmpty);
      expect(notifier.state.isLoading, false);
      expect(notifier.state.error, isNull);
    });

    group('loadProfile', () {
      test('sets profile and achievements on success', () async {
        final profile = _makeProfile();
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);

        await notifier.loadProfile();

        expect(notifier.state.isLoading, false);
        expect(notifier.state.profile, profile);
        expect(notifier.state.achievements.length, profile.achievements.length);
        expect(notifier.state.streaks.length, profile.streaks.length);
        expect(notifier.state.error, isNull);
      });

      test('sets isLoading true during load', () async {
        final profile = _makeProfile();
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);

        final future = notifier.loadProfile();

        // Immediately after call, should be loading
        expect(notifier.state.isLoading, true);
        expect(notifier.state.error, isNull);

        await future;

        expect(notifier.state.isLoading, false);
      });

      test('sets error on failure', () async {
        when(() => mockRepo.fetchProfile('user-001'))
            .thenThrow(Exception('Network error'));

        await notifier.loadProfile();

        expect(notifier.state.isLoading, false);
        expect(notifier.state.profile, isNull);
        expect(notifier.state.error, isNotNull);
        expect(notifier.state.error, contains('Network error'));
      });

      test('uses custom userId', () async {
        final profile = _makeProfile(userId: 'user-999');
        when(() => mockRepo.fetchProfile('user-999'))
            .thenAnswer((_) async => profile);

        await notifier.loadProfile(userId: 'user-999');

        expect(notifier.state.profile?.userId, 'user-999');
        verify(() => mockRepo.fetchProfile('user-999')).called(1);
      });

      test('clears previous error on new load', () async {
        // First call fails
        when(() => mockRepo.fetchProfile('user-001'))
            .thenThrow(Exception('First error'));
        await notifier.loadProfile();
        expect(notifier.state.error, isNotNull);

        // Second call succeeds
        final profile = _makeProfile();
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);
        await notifier.loadProfile();

        expect(notifier.state.error, isNull);
        expect(notifier.state.profile, profile);
      });
    });

    group('claimReward', () {
      test('unlocks achievement by setting unlockedAt', () async {
        final profile = _makeProfile(
          achievements: [_makeAchievement(id: 'ach-001', unlocked: false)],
        );
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);
        await notifier.loadProfile();

        await notifier.claimReward('ach-001');

        final claimed = notifier.state.achievements
            .firstWhere((a) => a.id == 'ach-001');
        expect(claimed.isUnlocked, true);
        expect(claimed.unlockedAt, isNotNull);
      });

      test('does nothing for already unlocked achievement', () async {
        final profile = _makeProfile(
          achievements: [_makeAchievement(id: 'ach-001', unlocked: true)],
        );
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);
        await notifier.loadProfile();

        final originalUnlockedAt = notifier.state.achievements
            .firstWhere((a) => a.id == 'ach-001')
            .unlockedAt;

        await notifier.claimReward('ach-001');

        final afterClaim = notifier.state.achievements
            .firstWhere((a) => a.id == 'ach-001');
        expect(afterClaim.unlockedAt, originalUnlockedAt);
      });

      test('does nothing for non-existent achievement id', () async {
        final profile = _makeProfile(
          achievements: [_makeAchievement(id: 'ach-001')],
        );
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);
        await notifier.loadProfile();

        await notifier.claimReward('non-existent');

        // State should remain unchanged
        expect(notifier.state.achievements.length, 1);
        expect(notifier.state.achievements.first.isUnlocked, false);
      });
    });

    group('getLeaderboard', () {
      test('sets leaderboard data on success', () async {
        final leaderboard = _makeLeaderboard();
        when(() => mockRepo.fetchLeaderboard(LeaderboardPeriod.weekly))
            .thenAnswer((_) async => leaderboard);

        await notifier.getLeaderboard(LeaderboardPeriod.weekly);

        expect(notifier.state.isLoading, false);
        expect(notifier.state.leaderboard.length, 2);
        expect(notifier.state.leaderboard[0].userId, 'user-001');
        expect(notifier.state.leaderboard[1].userId, 'user-002');
        expect(notifier.state.error, isNull);
      });

      test('changes leaderboardPeriod', () async {
        when(() => mockRepo.fetchLeaderboard(LeaderboardPeriod.monthly))
            .thenAnswer((_) async => []);

        await notifier.getLeaderboard(LeaderboardPeriod.monthly);

        expect(notifier.state.leaderboardPeriod, LeaderboardPeriod.monthly);
      });

      test('sets error on failure', () async {
        when(() => mockRepo.fetchLeaderboard(LeaderboardPeriod.daily))
            .thenThrow(Exception('Leaderboard error'));

        await notifier.getLeaderboard(LeaderboardPeriod.daily);

        expect(notifier.state.isLoading, false);
        expect(notifier.state.error, isNotNull);
        expect(notifier.state.error, contains('Leaderboard error'));
      });

      test('sets isLoading during fetch', () async {
        when(() => mockRepo.fetchLeaderboard(LeaderboardPeriod.allTime))
            .thenAnswer((_) async => _makeLeaderboard());

        final future = notifier.getLeaderboard(LeaderboardPeriod.allTime);

        expect(notifier.state.isLoading, true);

        await future;

        expect(notifier.state.isLoading, false);
      });
    });

    group('updateStreak', () {
      test('increments currentDays by 1', () async {
        final profile = _makeProfile(
          streaks: [_makeStreak(id: 'streak-001', currentDays: 5, bestDays: 10)],
        );
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);
        await notifier.loadProfile();

        await notifier.updateStreak('streak-001');

        final updated = notifier.state.streaks
            .firstWhere((s) => s.id == 'streak-001');
        expect(updated.currentDays, 6);
      });

      test('updates bestDays when currentDays exceeds it', () async {
        final profile = _makeProfile(
          streaks: [_makeStreak(id: 'streak-001', currentDays: 10, bestDays: 10)],
        );
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);
        await notifier.loadProfile();

        await notifier.updateStreak('streak-001');

        final updated = notifier.state.streaks
            .firstWhere((s) => s.id == 'streak-001');
        expect(updated.currentDays, 11);
        expect(updated.bestDays, 11);
      });

      test('does not update bestDays when currentDays does not exceed it', () async {
        final profile = _makeProfile(
          streaks: [_makeStreak(id: 'streak-001', currentDays: 3, bestDays: 10)],
        );
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);
        await notifier.loadProfile();

        await notifier.updateStreak('streak-001');

        final updated = notifier.state.streaks
            .firstWhere((s) => s.id == 'streak-001');
        expect(updated.currentDays, 4);
        expect(updated.bestDays, 10);
      });

      test('sets isActive to true', () async {
        final profile = _makeProfile(
          streaks: [_makeStreak(id: 'streak-001', isActive: false, currentDays: 0, bestDays: 5)],
        );
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);
        await notifier.loadProfile();

        await notifier.updateStreak('streak-001');

        final updated = notifier.state.streaks
            .firstWhere((s) => s.id == 'streak-001');
        expect(updated.isActive, true);
      });

      test('updates lastActivityDate', () async {
        final profile = _makeProfile(
          streaks: [_makeStreak(id: 'streak-001', currentDays: 1, bestDays: 5)],
        );
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);
        await notifier.loadProfile();

        final beforeUpdate = DateTime.now();
        await notifier.updateStreak('streak-001');

        final updated = notifier.state.streaks
            .firstWhere((s) => s.id == 'streak-001');
        expect(updated.lastActivityDate, isNotNull);
        // lastActivityDate should be close to now
        expect(
          updated.lastActivityDate!.difference(beforeUpdate).inSeconds.abs(),
          lessThan(2),
        );
      });

      test('does nothing for non-existent streak id', () async {
        final profile = _makeProfile(
          streaks: [_makeStreak(id: 'streak-001', currentDays: 5, bestDays: 10)],
        );
        when(() => mockRepo.fetchProfile('user-001'))
            .thenAnswer((_) async => profile);
        await notifier.loadProfile();

        await notifier.updateStreak('non-existent');

        // State unchanged
        final streak = notifier.state.streaks
            .firstWhere((s) => s.id == 'streak-001');
        expect(streak.currentDays, 5);
      });
    });
  });

  // ---------------------------------------------------------------------------
  // GamificationRepository
  // ---------------------------------------------------------------------------
  group('GamificationRepository', () {
    test('fetchProfile returns mock profile on DioException', () async {
      // Using default Dio which will fail to connect, triggering DioException fallback
      final repo = GamificationRepository();
      final profile = await repo.fetchProfile('user-test');

      expect(profile, isNotNull);
      expect(profile.userId, 'user-test');
      expect(profile.totalPoints, 0);
      expect(profile.level, 1);
      expect(profile.rank, 'beginner');
      expect(profile.achievements, isEmpty);
      expect(profile.streaks, isEmpty);
      expect(profile.milestones, isEmpty);
    });

    test('fetchLeaderboard returns empty list on DioException', () async {
      final repo = GamificationRepository();
      final leaderboard = await repo.fetchLeaderboard(LeaderboardPeriod.weekly);

      expect(leaderboard, isNotNull);
      expect(leaderboard, isEmpty);
    });
  });
}
