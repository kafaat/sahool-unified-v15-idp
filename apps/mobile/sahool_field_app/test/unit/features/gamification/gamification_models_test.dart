import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/gamification/domain/models/achievement.dart';

void main() {
  // ---------------------------------------------------------------------------
  // Achievement
  // ---------------------------------------------------------------------------
  group('Achievement', () {
    Achievement _makeAchievement({DateTime? unlockedAt, int current = 50, int target = 100}) {
      return Achievement(
        id: 'ach-001',
        title: 'خبير الري',
        titleEn: 'Irrigation Expert',
        description: 'Complete 100 irrigation tasks',
        category: AchievementCategory.irrigation,
        tier: AchievementTier.gold,
        iconName: 'water_drop',
        pointsValue: 500,
        progress: AchievementProgress(current: current, target: target, unit: 'tasks'),
        unlockedAt: unlockedAt,
      );
    }

    test('construction sets all fields correctly', () {
      final now = DateTime(2026, 3, 1);
      final achievement = _makeAchievement(unlockedAt: now);

      expect(achievement.id, 'ach-001');
      expect(achievement.title, 'خبير الري');
      expect(achievement.titleEn, 'Irrigation Expert');
      expect(achievement.description, 'Complete 100 irrigation tasks');
      expect(achievement.category, AchievementCategory.irrigation);
      expect(achievement.tier, AchievementTier.gold);
      expect(achievement.iconName, 'water_drop');
      expect(achievement.pointsValue, 500);
      expect(achievement.progress.current, 50);
      expect(achievement.progress.target, 100);
      expect(achievement.unlockedAt, now);
    });

    test('isUnlocked returns true when unlockedAt is set', () {
      final achievement = _makeAchievement(unlockedAt: DateTime(2026, 1, 1));
      expect(achievement.isUnlocked, true);
    });

    test('isUnlocked returns false when unlockedAt is null', () {
      final achievement = _makeAchievement(unlockedAt: null);
      expect(achievement.isUnlocked, false);
    });

    test('progressPercent calculates correctly (50/100 = 0.5)', () {
      final achievement = _makeAchievement(current: 50, target: 100);
      expect(achievement.progressPercent, 0.5);
    });

    test('progressPercent for 75/100 = 0.75', () {
      final achievement = _makeAchievement(current: 75, target: 100);
      expect(achievement.progressPercent, 0.75);
    });

    test('progressPercent for 100/100 = 1.0', () {
      final achievement = _makeAchievement(current: 100, target: 100);
      expect(achievement.progressPercent, 1.0);
    });

    test('toJson produces correct map', () {
      final now = DateTime(2026, 3, 1);
      final achievement = _makeAchievement(unlockedAt: now);
      final json = achievement.toJson();

      expect(json['id'], 'ach-001');
      expect(json['title'], 'خبير الري');
      expect(json['titleEn'], 'Irrigation Expert');
      expect(json['category'], 'irrigation');
      expect(json['tier'], 'gold');
      expect(json['iconName'], 'water_drop');
      expect(json['pointsValue'], 500);
      expect(json['progress'], isA<Map<String, dynamic>>());
      expect(json['unlockedAt'], now.toIso8601String());
    });

    test('toJson sets unlockedAt to null when not unlocked', () {
      final achievement = _makeAchievement(unlockedAt: null);
      final json = achievement.toJson();
      expect(json['unlockedAt'], isNull);
    });

    test('fromJson reconstructs Achievement correctly', () {
      final json = <String, dynamic>{
        'id': 'ach-002',
        'title': 'مراقب المحاصيل',
        'titleEn': 'Crop Monitor',
        'description': 'Monitor 50 fields',
        'category': 'monitoring',
        'tier': 'silver',
        'iconName': 'visibility',
        'pointsValue': 300,
        'progress': {'current': 25, 'target': 50, 'unit': 'fields'},
        'unlockedAt': '2026-02-15T00:00:00.000',
      };

      final achievement = Achievement.fromJson(json);
      expect(achievement.id, 'ach-002');
      expect(achievement.title, 'مراقب المحاصيل');
      expect(achievement.titleEn, 'Crop Monitor');
      expect(achievement.description, 'Monitor 50 fields');
      expect(achievement.category, AchievementCategory.monitoring);
      expect(achievement.tier, AchievementTier.silver);
      expect(achievement.iconName, 'visibility');
      expect(achievement.pointsValue, 300);
      expect(achievement.progress.current, 25);
      expect(achievement.progress.target, 50);
      expect(achievement.progress.unit, 'fields');
      expect(achievement.unlockedAt, isNotNull);
    });

    test('fromJson with null unlockedAt', () {
      final json = <String, dynamic>{
        'id': 'ach-003',
        'title': 'test',
        'titleEn': 'test',
        'description': 'desc',
        'category': 'tasks',
        'tier': 'bronze',
        'iconName': 'icon',
        'pointsValue': 100,
        'progress': {'current': 0, 'target': 10, 'unit': ''},
        'unlockedAt': null,
      };

      final achievement = Achievement.fromJson(json);
      expect(achievement.unlockedAt, isNull);
      expect(achievement.isUnlocked, false);
    });

    test('toJson then fromJson roundtrip preserves all data', () {
      final now = DateTime(2026, 3, 1);
      final original = _makeAchievement(unlockedAt: now);
      final json = original.toJson();
      final restored = Achievement.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.title, original.title);
      expect(restored.titleEn, original.titleEn);
      expect(restored.description, original.description);
      expect(restored.category, original.category);
      expect(restored.tier, original.tier);
      expect(restored.iconName, original.iconName);
      expect(restored.pointsValue, original.pointsValue);
      expect(restored.progress.current, original.progress.current);
      expect(restored.progress.target, original.progress.target);
      expect(restored.progress.unit, original.progress.unit);
      expect(restored.unlockedAt, original.unlockedAt);
    });

    test('toJson then fromJson roundtrip with null unlockedAt', () {
      final original = _makeAchievement(unlockedAt: null);
      final json = original.toJson();
      final restored = Achievement.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.unlockedAt, isNull);
    });
  });

  // ---------------------------------------------------------------------------
  // AchievementCategory
  // ---------------------------------------------------------------------------
  group('AchievementCategory', () {
    test('has exactly 8 values', () {
      expect(AchievementCategory.values.length, 8);
    });

    test('contains all expected values', () {
      expect(AchievementCategory.values, containsAll([
        AchievementCategory.irrigation,
        AchievementCategory.monitoring,
        AchievementCategory.tasks,
        AchievementCategory.scouting,
        AchievementCategory.consistency,
        AchievementCategory.productivity,
        AchievementCategory.teamwork,
        AchievementCategory.learning,
      ]));
    });
  });

  // ---------------------------------------------------------------------------
  // AchievementTier
  // ---------------------------------------------------------------------------
  group('AchievementTier', () {
    test('has exactly 5 values', () {
      expect(AchievementTier.values.length, 5);
    });

    test('contains all expected values', () {
      expect(AchievementTier.values, containsAll([
        AchievementTier.bronze,
        AchievementTier.silver,
        AchievementTier.gold,
        AchievementTier.platinum,
        AchievementTier.diamond,
      ]));
    });
  });

  // ---------------------------------------------------------------------------
  // AchievementProgress
  // ---------------------------------------------------------------------------
  group('AchievementProgress', () {
    test('construction with all fields', () {
      const progress = AchievementProgress(current: 10, target: 20, unit: 'fields');
      expect(progress.current, 10);
      expect(progress.target, 20);
      expect(progress.unit, 'fields');
    });

    test('unit defaults to empty string', () {
      const progress = AchievementProgress(current: 5, target: 10);
      expect(progress.unit, '');
    });

    test('toJson produces correct map', () {
      const progress = AchievementProgress(current: 3, target: 7, unit: 'tasks');
      final json = progress.toJson();
      expect(json['current'], 3);
      expect(json['target'], 7);
      expect(json['unit'], 'tasks');
    });

    test('fromJson reconstructs correctly', () {
      final json = <String, dynamic>{'current': 15, 'target': 30, 'unit': 'hectares'};
      final progress = AchievementProgress.fromJson(json);
      expect(progress.current, 15);
      expect(progress.target, 30);
      expect(progress.unit, 'hectares');
    });

    test('fromJson with missing unit defaults to empty string', () {
      final json = <String, dynamic>{'current': 1, 'target': 5};
      final progress = AchievementProgress.fromJson(json);
      expect(progress.unit, '');
    });

    test('toJson then fromJson roundtrip', () {
      const original = AchievementProgress(current: 42, target: 100, unit: 'items');
      final json = original.toJson();
      final restored = AchievementProgress.fromJson(json);
      expect(restored.current, original.current);
      expect(restored.target, original.target);
      expect(restored.unit, original.unit);
    });
  });

  // ---------------------------------------------------------------------------
  // Streak
  // ---------------------------------------------------------------------------
  group('Streak', () {
    Streak _makeStreak({
      DateTime? lastActivityDate,
      int currentDays = 5,
      int bestDays = 10,
      bool isActive = true,
    }) {
      return Streak(
        id: 'streak-001',
        title: 'تسجيل يومي',
        description: 'Log in every day',
        type: StreakType.dailyLogin,
        currentDays: currentDays,
        bestDays: bestDays,
        lastActivityDate: lastActivityDate,
        isActive: isActive,
      );
    }

    test('construction sets all fields', () {
      final now = DateTime(2026, 3, 1);
      final streak = _makeStreak(lastActivityDate: now);

      expect(streak.id, 'streak-001');
      expect(streak.title, 'تسجيل يومي');
      expect(streak.description, 'Log in every day');
      expect(streak.type, StreakType.dailyLogin);
      expect(streak.currentDays, 5);
      expect(streak.bestDays, 10);
      expect(streak.lastActivityDate, now);
      expect(streak.isActive, true);
    });

    test('isAtRisk returns true when 21 hours ago', () {
      final streak = _makeStreak(
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 21)),
      );
      expect(streak.isAtRisk, true);
    });

    test('isAtRisk returns false when 19 hours ago', () {
      final streak = _makeStreak(
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 19)),
      );
      expect(streak.isAtRisk, false);
    });

    test('isAtRisk returns false when 23 hours ago (still at risk)', () {
      final streak = _makeStreak(
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 23)),
      );
      // 23 > 20 && 23 < 24 => true
      expect(streak.isAtRisk, true);
    });

    test('isAtRisk returns false when lastActivityDate is null', () {
      final streak = _makeStreak(lastActivityDate: null);
      expect(streak.isAtRisk, false);
    });

    test('isAtRisk returns false when exactly 24 hours ago', () {
      final streak = _makeStreak(
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 24)),
      );
      // 24 is NOT < 24, so false
      expect(streak.isAtRisk, false);
    });

    test('isAtRisk returns false when exactly 20 hours ago', () {
      final streak = _makeStreak(
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 20)),
      );
      // 20 is NOT > 20, so false
      expect(streak.isAtRisk, false);
    });

    test('isBroken returns true when 25 hours ago', () {
      final streak = _makeStreak(
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 25)),
      );
      expect(streak.isBroken, true);
    });

    test('isBroken returns false when 23 hours ago', () {
      final streak = _makeStreak(
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 23)),
      );
      expect(streak.isBroken, false);
    });

    test('isBroken returns true when lastActivityDate is null', () {
      final streak = _makeStreak(lastActivityDate: null);
      expect(streak.isBroken, true);
    });

    test('isBroken returns true when exactly 24 hours ago', () {
      final streak = _makeStreak(
        lastActivityDate: DateTime.now().subtract(const Duration(hours: 24)),
      );
      // 24 >= 24 => true
      expect(streak.isBroken, true);
    });

    test('toJson produces correct map', () {
      final now = DateTime(2026, 3, 10, 8, 0, 0);
      final streak = _makeStreak(lastActivityDate: now);
      final json = streak.toJson();

      expect(json['id'], 'streak-001');
      expect(json['title'], 'تسجيل يومي');
      expect(json['description'], 'Log in every day');
      expect(json['type'], 'dailyLogin');
      expect(json['currentDays'], 5);
      expect(json['bestDays'], 10);
      expect(json['lastActivityDate'], now.toIso8601String());
      expect(json['isActive'], true);
    });

    test('toJson with null lastActivityDate', () {
      final streak = _makeStreak(lastActivityDate: null);
      final json = streak.toJson();
      expect(json['lastActivityDate'], isNull);
    });

    test('fromJson reconstructs correctly', () {
      final json = <String, dynamic>{
        'id': 'streak-002',
        'title': 'ري منتظم',
        'description': 'Irrigate on schedule',
        'type': 'irrigationSchedule',
        'currentDays': 7,
        'bestDays': 14,
        'lastActivityDate': '2026-03-10T08:00:00.000',
        'isActive': true,
      };

      final streak = Streak.fromJson(json);
      expect(streak.id, 'streak-002');
      expect(streak.title, 'ري منتظم');
      expect(streak.type, StreakType.irrigationSchedule);
      expect(streak.currentDays, 7);
      expect(streak.bestDays, 14);
      expect(streak.lastActivityDate, isNotNull);
      expect(streak.isActive, true);
    });

    test('fromJson with null lastActivityDate', () {
      final json = <String, dynamic>{
        'id': 'streak-003',
        'title': 'test',
        'description': 'desc',
        'type': 'taskCompletion',
        'currentDays': 0,
        'bestDays': 0,
        'lastActivityDate': null,
        'isActive': false,
      };

      final streak = Streak.fromJson(json);
      expect(streak.lastActivityDate, isNull);
    });

    test('toJson then fromJson roundtrip', () {
      final now = DateTime(2026, 3, 10);
      final original = _makeStreak(lastActivityDate: now);
      final json = original.toJson();
      final restored = Streak.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.title, original.title);
      expect(restored.description, original.description);
      expect(restored.type, original.type);
      expect(restored.currentDays, original.currentDays);
      expect(restored.bestDays, original.bestDays);
      expect(restored.lastActivityDate, original.lastActivityDate);
      expect(restored.isActive, original.isActive);
    });
  });

  // ---------------------------------------------------------------------------
  // StreakType
  // ---------------------------------------------------------------------------
  group('StreakType', () {
    test('has exactly 4 values', () {
      expect(StreakType.values.length, 4);
    });

    test('contains all expected values', () {
      expect(StreakType.values, containsAll([
        StreakType.dailyLogin,
        StreakType.irrigationSchedule,
        StreakType.taskCompletion,
        StreakType.fieldScouting,
      ]));
    });
  });

  // ---------------------------------------------------------------------------
  // Milestone
  // ---------------------------------------------------------------------------
  group('Milestone', () {
    Milestone _makeMilestone({DateTime? achievedAt, int currentValue = 30, int targetValue = 100}) {
      return Milestone(
        id: 'ms-001',
        title: 'First 100 Hectares',
        description: 'Manage 100 hectares total',
        targetValue: targetValue,
        currentValue: currentValue,
        unit: 'hectares',
        achievedAt: achievedAt,
        rewardPoints: 1000,
      );
    }

    test('construction sets all fields', () {
      final now = DateTime(2026, 2, 1);
      final milestone = _makeMilestone(achievedAt: now);

      expect(milestone.id, 'ms-001');
      expect(milestone.title, 'First 100 Hectares');
      expect(milestone.description, 'Manage 100 hectares total');
      expect(milestone.targetValue, 100);
      expect(milestone.currentValue, 30);
      expect(milestone.unit, 'hectares');
      expect(milestone.achievedAt, now);
      expect(milestone.rewardPoints, 1000);
    });

    test('isAchieved returns true when achievedAt is set', () {
      final milestone = _makeMilestone(achievedAt: DateTime(2026, 1, 15));
      expect(milestone.isAchieved, true);
    });

    test('isAchieved returns false when achievedAt is null', () {
      final milestone = _makeMilestone(achievedAt: null);
      expect(milestone.isAchieved, false);
    });

    test('progressPercent calculates correctly (30/100 = 0.3)', () {
      final milestone = _makeMilestone(currentValue: 30, targetValue: 100);
      expect(milestone.progressPercent, 0.3);
    });

    test('progressPercent for 100/100 = 1.0', () {
      final milestone = _makeMilestone(currentValue: 100, targetValue: 100);
      expect(milestone.progressPercent, 1.0);
    });

    test('progressPercent for 0/100 = 0.0', () {
      final milestone = _makeMilestone(currentValue: 0, targetValue: 100);
      expect(milestone.progressPercent, 0.0);
    });

    test('toJson produces correct map', () {
      final now = DateTime(2026, 2, 1);
      final milestone = _makeMilestone(achievedAt: now);
      final json = milestone.toJson();

      expect(json['id'], 'ms-001');
      expect(json['title'], 'First 100 Hectares');
      expect(json['description'], 'Manage 100 hectares total');
      expect(json['targetValue'], 100);
      expect(json['currentValue'], 30);
      expect(json['unit'], 'hectares');
      expect(json['achievedAt'], now.toIso8601String());
      expect(json['rewardPoints'], 1000);
    });

    test('toJson with null achievedAt', () {
      final milestone = _makeMilestone(achievedAt: null);
      final json = milestone.toJson();
      expect(json['achievedAt'], isNull);
    });

    test('fromJson reconstructs correctly', () {
      final json = <String, dynamic>{
        'id': 'ms-002',
        'title': 'Water Saver',
        'description': 'Save 1000m3 of water',
        'targetValue': 1000,
        'currentValue': 500,
        'unit': 'm3',
        'achievedAt': '2026-03-01T00:00:00.000',
        'rewardPoints': 2000,
      };

      final milestone = Milestone.fromJson(json);
      expect(milestone.id, 'ms-002');
      expect(milestone.title, 'Water Saver');
      expect(milestone.targetValue, 1000);
      expect(milestone.currentValue, 500);
      expect(milestone.unit, 'm3');
      expect(milestone.achievedAt, isNotNull);
      expect(milestone.rewardPoints, 2000);
    });

    test('fromJson with null achievedAt', () {
      final json = <String, dynamic>{
        'id': 'ms-003',
        'title': 'test',
        'description': 'desc',
        'targetValue': 10,
        'currentValue': 0,
        'unit': 'items',
        'achievedAt': null,
        'rewardPoints': 50,
      };

      final milestone = Milestone.fromJson(json);
      expect(milestone.achievedAt, isNull);
      expect(milestone.isAchieved, false);
    });

    test('toJson then fromJson roundtrip', () {
      final now = DateTime(2026, 2, 1);
      final original = _makeMilestone(achievedAt: now);
      final json = original.toJson();
      final restored = Milestone.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.title, original.title);
      expect(restored.description, original.description);
      expect(restored.targetValue, original.targetValue);
      expect(restored.currentValue, original.currentValue);
      expect(restored.unit, original.unit);
      expect(restored.achievedAt, original.achievedAt);
      expect(restored.rewardPoints, original.rewardPoints);
    });
  });

  // ---------------------------------------------------------------------------
  // UserGamificationProfile
  // ---------------------------------------------------------------------------
  group('UserGamificationProfile', () {
    Achievement _makeAch({bool unlocked = false}) {
      return Achievement(
        id: 'ach-${unlocked ? "u" : "l"}',
        title: 'Title',
        titleEn: 'Title EN',
        description: 'Desc',
        category: AchievementCategory.tasks,
        tier: AchievementTier.bronze,
        iconName: 'icon',
        pointsValue: 100,
        progress: const AchievementProgress(current: 5, target: 10),
        unlockedAt: unlocked ? DateTime(2026, 1, 1) : null,
      );
    }

    Streak _makeStrk({bool active = true}) {
      return Streak(
        id: 'strk-$active',
        title: 'Streak',
        description: 'Desc',
        type: StreakType.dailyLogin,
        currentDays: 3,
        bestDays: 7,
        lastActivityDate: DateTime.now(),
        isActive: active,
      );
    }

    Milestone _makeMs() {
      return const Milestone(
        id: 'ms-001',
        title: 'Milestone',
        description: 'Desc',
        targetValue: 100,
        currentValue: 50,
        unit: 'units',
        rewardPoints: 500,
      );
    }

    UserGamificationProfile _makeProfile({
      int totalPoints = 2500,
      int level = 2,
      List<Achievement>? achievements,
      List<Streak>? streaks,
      List<Milestone>? milestones,
    }) {
      return UserGamificationProfile(
        userId: 'user-001',
        totalPoints: totalPoints,
        level: level,
        rank: 'intermediate',
        achievements: achievements ?? [_makeAch(unlocked: true), _makeAch(unlocked: false)],
        streaks: streaks ?? [_makeStrk(active: true), _makeStrk(active: false)],
        milestones: milestones ?? [_makeMs()],
        lastUpdated: DateTime(2026, 3, 15),
      );
    }

    test('construction sets all fields', () {
      final profile = _makeProfile();

      expect(profile.userId, 'user-001');
      expect(profile.totalPoints, 2500);
      expect(profile.level, 2);
      expect(profile.rank, 'intermediate');
      expect(profile.achievements.length, 2);
      expect(profile.streaks.length, 2);
      expect(profile.milestones.length, 1);
      expect(profile.lastUpdated, DateTime(2026, 3, 15));
    });

    test('unlockedAchievements counts only unlocked', () {
      final profile = _makeProfile(
        achievements: [
          _makeAch(unlocked: true),
          _makeAch(unlocked: true),
          _makeAch(unlocked: false),
        ],
      );
      expect(profile.unlockedAchievements, 2);
    });

    test('unlockedAchievements returns 0 when none unlocked', () {
      final profile = _makeProfile(
        achievements: [_makeAch(unlocked: false), _makeAch(unlocked: false)],
      );
      expect(profile.unlockedAchievements, 0);
    });

    test('activeStreaks counts only active', () {
      final profile = _makeProfile(
        streaks: [
          _makeStrk(active: true),
          _makeStrk(active: true),
          _makeStrk(active: false),
        ],
      );
      expect(profile.activeStreaks, 2);
    });

    test('activeStreaks returns 0 when none active', () {
      final profile = _makeProfile(
        streaks: [_makeStrk(active: false)],
      );
      expect(profile.activeStreaks, 0);
    });

    test('pointsToNextLevel calculation (level=2, points=2500)', () {
      // nextLevelPoints = (2+1)*1000 = 3000, 3000 - 2500 = 500
      final profile = _makeProfile(level: 2, totalPoints: 2500);
      expect(profile.pointsToNextLevel, 500);
    });

    test('pointsToNextLevel at level boundary', () {
      // level=1, points=2000 => next = 2000, 2000-2000 = 0
      final profile = _makeProfile(level: 1, totalPoints: 2000);
      expect(profile.pointsToNextLevel, 0);
    });

    test('levelProgress calculation (level=2, points=2500)', () {
      // currentLevelBase = 2*1000 = 2000
      // nextLevelPoints = 3*1000 = 3000
      // (2500-2000) / (3000-2000) = 500/1000 = 0.5
      final profile = _makeProfile(level: 2, totalPoints: 2500);
      expect(profile.levelProgress, 0.5);
    });

    test('levelProgress at start of level', () {
      // level=3, points=3000 => (3000-3000)/(4000-3000) = 0.0
      final profile = _makeProfile(level: 3, totalPoints: 3000);
      expect(profile.levelProgress, 0.0);
    });

    test('levelProgress near end of level', () {
      // level=1, points=1900 => (1900-1000)/(2000-1000) = 900/1000 = 0.9
      final profile = _makeProfile(level: 1, totalPoints: 1900);
      expect(profile.levelProgress, 0.9);
    });

    test('toJson produces correct map', () {
      final profile = _makeProfile(achievements: [], streaks: [], milestones: []);
      final json = profile.toJson();

      expect(json['userId'], 'user-001');
      expect(json['totalPoints'], 2500);
      expect(json['level'], 2);
      expect(json['rank'], 'intermediate');
      expect(json['achievements'], isA<List>());
      expect(json['streaks'], isA<List>());
      expect(json['milestones'], isA<List>());
      expect(json['lastUpdated'], DateTime(2026, 3, 15).toIso8601String());
    });

    test('toJson includes nested achievement objects', () {
      final profile = _makeProfile(
        achievements: [_makeAch(unlocked: true)],
        streaks: [],
        milestones: [],
      );
      final json = profile.toJson();
      final achievementsList = json['achievements'] as List;
      expect(achievementsList.length, 1);
      expect(achievementsList[0]['id'], isA<String>());
    });

    test('fromJson reconstructs correctly', () {
      final json = <String, dynamic>{
        'userId': 'user-002',
        'totalPoints': 5000,
        'level': 5,
        'rank': 'expert',
        'achievements': <Map<String, dynamic>>[],
        'streaks': <Map<String, dynamic>>[],
        'milestones': <Map<String, dynamic>>[],
        'lastUpdated': '2026-03-15T00:00:00.000',
      };

      final profile = UserGamificationProfile.fromJson(json);
      expect(profile.userId, 'user-002');
      expect(profile.totalPoints, 5000);
      expect(profile.level, 5);
      expect(profile.rank, 'expert');
      expect(profile.achievements, isEmpty);
      expect(profile.streaks, isEmpty);
      expect(profile.milestones, isEmpty);
    });

    test('toJson then fromJson roundtrip with nested data', () {
      final original = _makeProfile();
      final json = original.toJson();
      final restored = UserGamificationProfile.fromJson(json);

      expect(restored.userId, original.userId);
      expect(restored.totalPoints, original.totalPoints);
      expect(restored.level, original.level);
      expect(restored.rank, original.rank);
      expect(restored.achievements.length, original.achievements.length);
      expect(restored.streaks.length, original.streaks.length);
      expect(restored.milestones.length, original.milestones.length);
      expect(restored.lastUpdated, original.lastUpdated);
    });
  });

  // ---------------------------------------------------------------------------
  // LeaderboardEntry
  // ---------------------------------------------------------------------------
  group('LeaderboardEntry', () {
    test('construction sets all fields', () {
      const entry = LeaderboardEntry(
        userId: 'user-001',
        userName: 'Ahmed',
        avatarUrl: 'https://example.com/avatar.png',
        rank: 1,
        points: 5000,
        level: 5,
        isCurrentUser: true,
      );

      expect(entry.userId, 'user-001');
      expect(entry.userName, 'Ahmed');
      expect(entry.avatarUrl, 'https://example.com/avatar.png');
      expect(entry.rank, 1);
      expect(entry.points, 5000);
      expect(entry.level, 5);
      expect(entry.isCurrentUser, true);
    });

    test('isCurrentUser defaults to false', () {
      const entry = LeaderboardEntry(
        userId: 'user-002',
        userName: 'Ali',
        rank: 2,
        points: 4000,
        level: 4,
      );
      expect(entry.isCurrentUser, false);
    });

    test('avatarUrl defaults to null', () {
      const entry = LeaderboardEntry(
        userId: 'user-003',
        userName: 'Omar',
        rank: 3,
        points: 3000,
        level: 3,
      );
      expect(entry.avatarUrl, isNull);
    });

    test('toJson produces correct map', () {
      const entry = LeaderboardEntry(
        userId: 'user-001',
        userName: 'Ahmed',
        avatarUrl: 'https://example.com/avatar.png',
        rank: 1,
        points: 5000,
        level: 5,
        isCurrentUser: true,
      );
      final json = entry.toJson();

      expect(json['userId'], 'user-001');
      expect(json['userName'], 'Ahmed');
      expect(json['avatarUrl'], 'https://example.com/avatar.png');
      expect(json['rank'], 1);
      expect(json['points'], 5000);
      expect(json['level'], 5);
      expect(json['isCurrentUser'], true);
    });

    test('toJson with null avatarUrl', () {
      const entry = LeaderboardEntry(
        userId: 'user-002',
        userName: 'Ali',
        rank: 2,
        points: 4000,
        level: 4,
      );
      final json = entry.toJson();
      expect(json['avatarUrl'], isNull);
    });

    test('fromJson reconstructs correctly', () {
      final json = <String, dynamic>{
        'userId': 'user-004',
        'userName': 'Khalid',
        'avatarUrl': null,
        'rank': 4,
        'points': 2000,
        'level': 2,
        'isCurrentUser': false,
      };

      final entry = LeaderboardEntry.fromJson(json);
      expect(entry.userId, 'user-004');
      expect(entry.userName, 'Khalid');
      expect(entry.avatarUrl, isNull);
      expect(entry.rank, 4);
      expect(entry.points, 2000);
      expect(entry.level, 2);
      expect(entry.isCurrentUser, false);
    });

    test('fromJson defaults isCurrentUser to false when missing', () {
      final json = <String, dynamic>{
        'userId': 'user-005',
        'userName': 'Faisal',
        'rank': 5,
        'points': 1500,
        'level': 1,
      };

      final entry = LeaderboardEntry.fromJson(json);
      expect(entry.isCurrentUser, false);
    });

    test('toJson then fromJson roundtrip', () {
      const original = LeaderboardEntry(
        userId: 'user-001',
        userName: 'Ahmed',
        avatarUrl: 'https://example.com/avatar.png',
        rank: 1,
        points: 5000,
        level: 5,
        isCurrentUser: true,
      );
      final json = original.toJson();
      final restored = LeaderboardEntry.fromJson(json);

      expect(restored.userId, original.userId);
      expect(restored.userName, original.userName);
      expect(restored.avatarUrl, original.avatarUrl);
      expect(restored.rank, original.rank);
      expect(restored.points, original.points);
      expect(restored.level, original.level);
      expect(restored.isCurrentUser, original.isCurrentUser);
    });

    test('toJson then fromJson roundtrip with null avatarUrl', () {
      const original = LeaderboardEntry(
        userId: 'user-002',
        userName: 'Ali',
        rank: 2,
        points: 4000,
        level: 4,
      );
      final json = original.toJson();
      final restored = LeaderboardEntry.fromJson(json);

      expect(restored.avatarUrl, isNull);
      expect(restored.isCurrentUser, false);
    });
  });

  // ---------------------------------------------------------------------------
  // LeaderboardPeriod
  // ---------------------------------------------------------------------------
  group('LeaderboardPeriod', () {
    test('has exactly 4 values', () {
      expect(LeaderboardPeriod.values.length, 4);
    });

    test('contains all expected values', () {
      expect(LeaderboardPeriod.values, containsAll([
        LeaderboardPeriod.daily,
        LeaderboardPeriod.weekly,
        LeaderboardPeriod.monthly,
        LeaderboardPeriod.allTime,
      ]));
    });
  });
}
