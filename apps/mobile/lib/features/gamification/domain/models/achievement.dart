/// SAHOOL Achievement Models
/// نماذج الإنجازات
///
/// Features:
/// - Professional achievements (non-childish)
/// - Progress tracking
/// - Streaks and milestones
/// - Leaderboards

/// إنجاز
class Achievement {
  final String id;
  final String title;
  final String titleEn;
  final String description;
  final AchievementCategory category;
  final AchievementTier tier;
  final String iconName;
  final int pointsValue;
  final AchievementProgress progress;
  final DateTime? unlockedAt;

  const Achievement({
    required this.id,
    required this.title,
    required this.titleEn,
    required this.description,
    required this.category,
    required this.tier,
    required this.iconName,
    required this.pointsValue,
    required this.progress,
    this.unlockedAt,
  });

  bool get isUnlocked => unlockedAt != null;
  double get progressPercent => progress.current / progress.target;

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'titleEn': titleEn,
    'description': description,
    'category': category.name,
    'tier': tier.name,
    'iconName': iconName,
    'pointsValue': pointsValue,
    'progress': progress.toJson(),
    'unlockedAt': unlockedAt?.toIso8601String(),
  };

  factory Achievement.fromJson(Map<String, dynamic> json) => Achievement(
    id: json['id'] as String,
    title: json['title'] as String,
    titleEn: json['titleEn'] as String,
    description: json['description'] as String,
    category: AchievementCategory.values.byName(json['category'] as String),
    tier: AchievementTier.values.byName(json['tier'] as String),
    iconName: json['iconName'] as String,
    pointsValue: json['pointsValue'] as int,
    progress: AchievementProgress.fromJson(json['progress'] as Map<String, dynamic>),
    unlockedAt: json['unlockedAt'] != null
        ? DateTime.parse(json['unlockedAt'] as String)
        : null,
  );
}

/// فئة الإنجاز
enum AchievementCategory {
  irrigation,      // الري
  monitoring,      // المراقبة
  tasks,           // المهام
  scouting,        // المسح
  consistency,     // الانتظام
  productivity,    // الإنتاجية
  teamwork,        // العمل الجماعي
  learning,        // التعلم
}

/// مستوى الإنجاز
enum AchievementTier {
  bronze,
  silver,
  gold,
  platinum,
  diamond,
}

/// تقدم الإنجاز
class AchievementProgress {
  final int current;
  final int target;
  final String unit;

  const AchievementProgress({
    required this.current,
    required this.target,
    this.unit = '',
  });

  Map<String, dynamic> toJson() => {
    'current': current,
    'target': target,
    'unit': unit,
  };

  factory AchievementProgress.fromJson(Map<String, dynamic> json) =>
      AchievementProgress(
        current: json['current'] as int,
        target: json['target'] as int,
        unit: json['unit'] as String? ?? '',
      );
}

/// سلسلة متتابعة (Streak)
class Streak {
  final String id;
  final String title;
  final String description;
  final StreakType type;
  final int currentDays;
  final int bestDays;
  final DateTime? lastActivityDate;
  final bool isActive;

  const Streak({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    required this.currentDays,
    required this.bestDays,
    this.lastActivityDate,
    required this.isActive,
  });

  bool get isAtRisk {
    if (lastActivityDate == null) return false;
    final hoursSinceActivity = DateTime.now().difference(lastActivityDate!).inHours;
    return hoursSinceActivity > 20 && hoursSinceActivity < 24;
  }

  bool get isBroken {
    if (lastActivityDate == null) return true;
    return DateTime.now().difference(lastActivityDate!).inHours >= 24;
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'description': description,
    'type': type.name,
    'currentDays': currentDays,
    'bestDays': bestDays,
    'lastActivityDate': lastActivityDate?.toIso8601String(),
    'isActive': isActive,
  };

  factory Streak.fromJson(Map<String, dynamic> json) => Streak(
    id: json['id'] as String,
    title: json['title'] as String,
    description: json['description'] as String,
    type: StreakType.values.byName(json['type'] as String),
    currentDays: json['currentDays'] as int,
    bestDays: json['bestDays'] as int,
    lastActivityDate: json['lastActivityDate'] != null
        ? DateTime.parse(json['lastActivityDate'] as String)
        : null,
    isActive: json['isActive'] as bool,
  );
}

/// نوع السلسلة
enum StreakType {
  dailyLogin,          // تسجيل دخول يومي
  irrigationSchedule,  // ري منتظم
  taskCompletion,      // إكمال المهام
  fieldScouting,       // مسح الحقول
}

/// معلم (Milestone)
class Milestone {
  final String id;
  final String title;
  final String description;
  final int targetValue;
  final int currentValue;
  final String unit;
  final DateTime? achievedAt;
  final int rewardPoints;

  const Milestone({
    required this.id,
    required this.title,
    required this.description,
    required this.targetValue,
    required this.currentValue,
    required this.unit,
    this.achievedAt,
    required this.rewardPoints,
  });

  bool get isAchieved => achievedAt != null;
  double get progressPercent => currentValue / targetValue;

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'description': description,
    'targetValue': targetValue,
    'currentValue': currentValue,
    'unit': unit,
    'achievedAt': achievedAt?.toIso8601String(),
    'rewardPoints': rewardPoints,
  };

  factory Milestone.fromJson(Map<String, dynamic> json) => Milestone(
    id: json['id'] as String,
    title: json['title'] as String,
    description: json['description'] as String,
    targetValue: json['targetValue'] as int,
    currentValue: json['currentValue'] as int,
    unit: json['unit'] as String,
    achievedAt: json['achievedAt'] != null
        ? DateTime.parse(json['achievedAt'] as String)
        : null,
    rewardPoints: json['rewardPoints'] as int,
  );
}

/// ملف المستخدم في نظام الإنجازات
class UserGamificationProfile {
  final String odoo;
  final int totalPoints;
  final int level;
  final String rank;
  final List<Achievement> achievements;
  final List<Streak> streaks;
  final List<Milestone> milestones;
  final DateTime lastUpdated;

  const UserGamificationProfile({
    required this.userId,
    required this.totalPoints,
    required this.level,
    required this.rank,
    required this.achievements,
    required this.streaks,
    required this.milestones,
    required this.lastUpdated,
  });

  int get unlockedAchievements => achievements.where((a) => a.isUnlocked).length;
  int get activeStreaks => streaks.where((s) => s.isActive).length;

  int get pointsToNextLevel {
    final nextLevelPoints = (level + 1) * 1000;
    return nextLevelPoints - totalPoints;
  }

  double get levelProgress {
    final currentLevelBase = level * 1000;
    final nextLevelPoints = (level + 1) * 1000;
    return (totalPoints - currentLevelBase) / (nextLevelPoints - currentLevelBase);
  }

  Map<String, dynamic> toJson() => {
    'userId': odoo,
    'totalPoints': totalPoints,
    'level': level,
    'rank': rank,
    'achievements': achievements.map((a) => a.toJson()).toList(),
    'streaks': streaks.map((s) => s.toJson()).toList(),
    'milestones': milestones.map((m) => m.toJson()).toList(),
    'lastUpdated': lastUpdated.toIso8601String(),
  };

  factory UserGamificationProfile.fromJson(Map<String, dynamic> json) =>
      UserGamificationProfile(
        userId: json['userId'] as String,
        totalPoints: json['totalPoints'] as int,
        level: json['level'] as int,
        rank: json['rank'] as String,
        achievements: (json['achievements'] as List)
            .map((a) => Achievement.fromJson(a as Map<String, dynamic>))
            .toList(),
        streaks: (json['streaks'] as List)
            .map((s) => Streak.fromJson(s as Map<String, dynamic>))
            .toList(),
        milestones: (json['milestones'] as List)
            .map((m) => Milestone.fromJson(m as Map<String, dynamic>))
            .toList(),
        lastUpdated: DateTime.parse(json['lastUpdated'] as String),
      );
}

/// ترتيب في لوحة المتصدرين
class LeaderboardEntry {
  final String odoo;
  final String userName;
  final String? avatarUrl;
  final int rank;
  final int points;
  final int level;
  final bool isCurrentUser;

  const LeaderboardEntry({
    required this.userId,
    required this.userName,
    this.avatarUrl,
    required this.rank,
    required this.points,
    required this.level,
    this.isCurrentUser = false,
  });

  Map<String, dynamic> toJson() => {
    'userId': odoo,
    'userName': userName,
    'avatarUrl': avatarUrl,
    'rank': rank,
    'points': points,
    'level': level,
    'isCurrentUser': isCurrentUser,
  };

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) =>
      LeaderboardEntry(
        userId: json['userId'] as String,
        userName: json['userName'] as String,
        avatarUrl: json['avatarUrl'] as String?,
        rank: json['rank'] as int,
        points: json['points'] as int,
        level: json['level'] as int,
        isCurrentUser: json['isCurrentUser'] as bool? ?? false,
      );
}

/// فترة لوحة المتصدرين
enum LeaderboardPeriod {
  daily,
  weekly,
  monthly,
  allTime,
}
