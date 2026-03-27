import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/achievement.dart';
import '../providers/gamification_provider.dart';
import '../widgets/achievement_card.dart';

/// Achievements screen - شاشة الإنجازات
class AchievementsScreen extends ConsumerStatefulWidget {
  const AchievementsScreen({super.key});

  @override
  ConsumerState<AchievementsScreen> createState() => _AchievementsScreenState();
}

class _AchievementsScreenState extends ConsumerState<AchievementsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    Future.microtask(() {
      ref.read(gamificationProvider.notifier).loadProfile();
      ref.read(gamificationProvider.notifier).getLeaderboard(LeaderboardPeriod.weekly);
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(gamificationProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: SahoolColors.background,
        appBar: AppBar(
          title: const Text('الإنجازات | Achievements'),
          bottom: TabBar(
            controller: _tabController,
            labelColor: SahoolColors.primary,
            unselectedLabelColor: SahoolColors.textSecondary,
            indicatorColor: SahoolColors.primary,
            indicatorWeight: 3,
            tabs: const [
              Tab(text: 'الإنجازات'),
              Tab(text: 'السلاسل'),
              Tab(text: 'المتصدرون'),
            ],
          ),
        ),
        body: state.isLoading && state.profile == null
            ? const Center(child: CircularProgressIndicator())
            : Column(
                children: [
                  if (state.profile != null) _buildHeader(state.profile!),
                  Expanded(
                    child: TabBarView(
                      controller: _tabController,
                      children: [
                        _buildAchievementsTab(state),
                        _buildStreaksTab(state),
                        _buildLeaderboardTab(state),
                      ],
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  /// Points and level header - رأس النقاط والمستوى
  Widget _buildHeader(UserGamificationProfile profile) {
    return Container(
      margin: const EdgeInsets.all(SahoolSpacing.md),
      padding: const EdgeInsets.all(SahoolSpacing.md),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [SahoolColors.forestGreen, SahoolColors.primary],
          begin: Alignment.topRight,
          end: Alignment.bottomLeft,
        ),
        borderRadius: BorderRadius.circular(SahoolRadius.large),
        boxShadow: SahoolShadows.medium,
      ),
      child: Column(
        children: [
          Row(
            children: [
              // Level circle
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withValues(alpha: 0.2),
                  border: Border.all(color: Colors.white, width: 2),
                ),
                child: Center(
                  child: Text(
                    '${profile.level}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: SahoolSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      profile.rank,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${profile.totalPoints} نقطة | ${profile.unlockedAchievements} إنجاز',
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.85),
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
              // Active streaks badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: SahoolColors.harvestGold,
                  borderRadius: BorderRadius.circular(SahoolRadius.circular),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.local_fire_department, color: Colors.white, size: 16),
                    const SizedBox(width: 4),
                    Text(
                      '${profile.activeStreaks}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: SahoolSpacing.md),
          // Level progress bar
          Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'المستوى ${profile.level}',
                    style: TextStyle(color: Colors.white.withValues(alpha: 0.85), fontSize: 12),
                  ),
                  Text(
                    '${profile.pointsToNextLevel} نقطة للمستوى التالي',
                    style: TextStyle(color: Colors.white.withValues(alpha: 0.85), fontSize: 12),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              ClipRRect(
                borderRadius: BorderRadius.circular(SahoolRadius.small),
                child: LinearProgressIndicator(
                  value: profile.levelProgress.clamp(0.0, 1.0),
                  minHeight: 8,
                  backgroundColor: Colors.white.withValues(alpha: 0.2),
                  valueColor: const AlwaysStoppedAnimation<Color>(SahoolColors.harvestGold),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Achievements grid tab - تبويب شبكة الإنجازات
  Widget _buildAchievementsTab(GamificationState state) {
    if (state.achievements.isEmpty) {
      return const Center(
        child: Text('لا توجد إنجازات بعد\nNo achievements yet',
            textAlign: TextAlign.center),
      );
    }
    return GridView.builder(
      padding: const EdgeInsets.all(SahoolSpacing.md),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: SahoolSpacing.md,
        mainAxisSpacing: SahoolSpacing.md,
        childAspectRatio: 0.88,
      ),
      itemCount: state.achievements.length,
      itemBuilder: (context, index) {
        final achievement = state.achievements[index];
        return AchievementCard(
          achievement: achievement,
          onTap: () => _showAchievementDetail(context, achievement),
        );
      },
    );
  }

  /// Streaks tab - تبويب السلاسل المتتابعة
  Widget _buildStreaksTab(GamificationState state) {
    if (state.streaks.isEmpty) {
      return const Center(
        child: Text('لا توجد سلاسل نشطة\nNo active streaks',
            textAlign: TextAlign.center),
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.all(SahoolSpacing.md),
      itemCount: state.streaks.length,
      separatorBuilder: (_, __) => const SizedBox(height: SahoolSpacing.sm),
      itemBuilder: (context, index) => _buildStreakTile(state.streaks[index]),
    );
  }

  Widget _buildStreakTile(Streak streak) {
    final Color statusColor;
    final String statusText;
    if (!streak.isActive || streak.isBroken) {
      statusColor = SahoolColors.danger;
      statusText = 'متوقف | Broken';
    } else if (streak.isAtRisk) {
      statusColor = SahoolColors.warning;
      statusText = 'في خطر | At Risk';
    } else {
      statusColor = SahoolColors.success;
      statusText = 'نشط | Active';
    }

    final IconData streakIcon;
    switch (streak.type) {
      case StreakType.dailyLogin:
        streakIcon = Icons.login;
      case StreakType.irrigationSchedule:
        streakIcon = Icons.water_drop;
      case StreakType.taskCompletion:
        streakIcon = Icons.check_circle;
      case StreakType.fieldScouting:
        streakIcon = Icons.explore;
    }

    return Container(
      padding: const EdgeInsets.all(SahoolSpacing.md),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(SahoolRadius.large),
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        children: [
          // Streak icon
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: statusColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(SahoolRadius.medium),
            ),
            child: Icon(streakIcon, color: statusColor, size: 24),
          ),
          const SizedBox(width: SahoolSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  streak.title,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                const SizedBox(height: 2),
                Text(
                  streak.description,
                  style: const TextStyle(
                    color: SahoolColors.textSecondary,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.local_fire_department, color: statusColor, size: 18),
                  const SizedBox(width: 4),
                  Text(
                    '${streak.currentDays}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                      color: statusColor,
                    ),
                  ),
                ],
              ),
              Text(
                'الأفضل: ${streak.bestDays}',
                style: const TextStyle(
                  color: SahoolColors.textSecondary,
                  fontSize: 11,
                ),
              ),
              const SizedBox(height: 2),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(SahoolRadius.small),
                ),
                child: Text(
                  statusText,
                  style: TextStyle(color: statusColor, fontSize: 10, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Leaderboard tab - تبويب لوحة المتصدرين
  Widget _buildLeaderboardTab(GamificationState state) {
    return Column(
      children: [
        // Period selector
        Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: SahoolSpacing.md,
            vertical: SahoolSpacing.sm,
          ),
          child: Row(
            children: LeaderboardPeriod.values.map((period) {
              final isSelected = period == state.leaderboardPeriod;
              final String label;
              switch (period) {
                case LeaderboardPeriod.daily:
                  label = 'يومي';
                case LeaderboardPeriod.weekly:
                  label = 'أسبوعي';
                case LeaderboardPeriod.monthly:
                  label = 'شهري';
                case LeaderboardPeriod.allTime:
                  label = 'الكل';
              }
              return Expanded(
                child: GestureDetector(
                  onTap: () => ref
                      .read(gamificationProvider.notifier)
                      .getLeaderboard(period),
                  child: Container(
                    margin: const EdgeInsets.symmetric(horizontal: 3),
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      color: isSelected ? SahoolColors.primary : Colors.white,
                      borderRadius: BorderRadius.circular(SahoolRadius.medium),
                      border: Border.all(
                        color: isSelected ? SahoolColors.primary : Colors.grey.shade300,
                      ),
                    ),
                    child: Text(
                      label,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: isSelected ? Colors.white : SahoolColors.textSecondary,
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ),
        // Leaderboard list
        Expanded(
          child: state.leaderboard.isEmpty
              ? const Center(
                  child: Text('لا توجد بيانات\nNo data available',
                      textAlign: TextAlign.center),
                )
              : ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: SahoolSpacing.md),
                  itemCount: state.leaderboard.length,
                  itemBuilder: (context, index) =>
                      _buildLeaderboardTile(state.leaderboard[index]),
                ),
        ),
      ],
    );
  }

  Widget _buildLeaderboardTile(LeaderboardEntry entry) {
    final Color? medalColor;
    switch (entry.rank) {
      case 1:
        medalColor = SahoolColors.harvestGold;
      case 2:
        medalColor = const Color(0xFFC0C0C0);
      case 3:
        medalColor = const Color(0xFFCD7F32);
      default:
        medalColor = null;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: SahoolSpacing.sm),
      padding: const EdgeInsets.symmetric(
        horizontal: SahoolSpacing.md,
        vertical: SahoolSpacing.sm + 4,
      ),
      decoration: BoxDecoration(
        color: entry.isCurrentUser
            ? SahoolColors.primary.withValues(alpha: 0.08)
            : Colors.white,
        borderRadius: BorderRadius.circular(SahoolRadius.medium),
        border: entry.isCurrentUser
            ? Border.all(color: SahoolColors.primary, width: 1.5)
            : null,
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        children: [
          // Rank
          SizedBox(
            width: 32,
            child: medalColor != null
                ? Icon(Icons.emoji_events, color: medalColor, size: 26)
                : Text(
                    '#${entry.rank}',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                      color: SahoolColors.textSecondary,
                    ),
                  ),
          ),
          const SizedBox(width: SahoolSpacing.md),
          // Avatar
          CircleAvatar(
            radius: 20,
            backgroundColor: entry.isCurrentUser
                ? SahoolColors.primary
                : SahoolColors.sageGreen,
            child: Text(
              entry.userName.isNotEmpty ? entry.userName[0] : '?',
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(width: SahoolSpacing.sm),
          // Name and level
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.userName,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                    color: entry.isCurrentUser
                        ? SahoolColors.primary
                        : SahoolColors.textDark,
                  ),
                ),
                Text(
                  'المستوى ${entry.level} | Level ${entry.level}',
                  style: const TextStyle(
                    color: SahoolColors.textSecondary,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
          // Points
          Text(
            '${entry.points}',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
              color: entry.isCurrentUser
                  ? SahoolColors.primary
                  : SahoolColors.forestGreen,
            ),
          ),
        ],
      ),
    );
  }

  /// Achievement detail bottom sheet - تفاصيل الإنجاز
  void _showAchievementDetail(BuildContext context, Achievement achievement) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => Directionality(
        textDirection: TextDirection.rtl,
        child: Padding(
          padding: const EdgeInsets.all(SahoolSpacing.lg),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(height: SahoolSpacing.lg),
              Text(
                achievement.title,
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                achievement.titleEn,
                style: const TextStyle(fontSize: 14, color: SahoolColors.textSecondary),
              ),
              const SizedBox(height: SahoolSpacing.md),
              Text(
                achievement.description,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 15),
              ),
              const SizedBox(height: SahoolSpacing.lg),
              // Progress bar
              ClipRRect(
                borderRadius: BorderRadius.circular(SahoolRadius.small),
                child: LinearProgressIndicator(
                  value: achievement.progressPercent.clamp(0.0, 1.0),
                  minHeight: 10,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    achievement.isUnlocked ? SahoolColors.success : SahoolColors.info,
                  ),
                ),
              ),
              const SizedBox(height: SahoolSpacing.sm),
              Text(
                '${achievement.progress.current} / ${achievement.progress.target} ${achievement.progress.unit}',
                style: const TextStyle(color: SahoolColors.textSecondary, fontSize: 13),
              ),
              const SizedBox(height: SahoolSpacing.md),
              Text(
                '+${achievement.pointsValue} نقطة | Points',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: SahoolColors.success,
                ),
              ),
              const SizedBox(height: SahoolSpacing.lg),
            ],
          ),
        ),
      ),
    );
  }
}
