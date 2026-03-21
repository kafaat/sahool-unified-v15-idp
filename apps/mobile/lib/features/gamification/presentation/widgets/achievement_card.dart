import 'package:flutter/material.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/achievement.dart';

/// Achievement card widget - بطاقة الإنجاز
class AchievementCard extends StatelessWidget {
  final Achievement achievement;
  final VoidCallback? onTap;

  const AchievementCard({
    super.key,
    required this.achievement,
    this.onTap,
  });

  Color get _tierColor {
    switch (achievement.tier) {
      case AchievementTier.bronze:
        return const Color(0xFFCD7F32);
      case AchievementTier.silver:
        return const Color(0xFFC0C0C0);
      case AchievementTier.gold:
        return SahoolColors.harvestGold;
      case AchievementTier.platinum:
        return const Color(0xFFE5E4E2);
      case AchievementTier.diamond:
        return SahoolColors.info;
    }
  }

  String get _tierLabel {
    switch (achievement.tier) {
      case AchievementTier.bronze:
        return 'برونزي';
      case AchievementTier.silver:
        return 'فضي';
      case AchievementTier.gold:
        return 'ذهبي';
      case AchievementTier.platinum:
        return 'بلاتيني';
      case AchievementTier.diamond:
        return 'ماسي';
    }
  }

  IconData get _iconData {
    switch (achievement.iconName) {
      case 'water_drop':
        return Icons.water_drop;
      case 'pest_control':
        return Icons.pest_control;
      case 'visibility':
        return Icons.visibility;
      case 'groups':
        return Icons.groups;
      case 'school':
        return Icons.school;
      case 'task_alt':
        return Icons.task_alt;
      default:
        return Icons.emoji_events;
    }
  }

  @override
  Widget build(BuildContext context) {
    final unlocked = achievement.isUnlocked;
    final progress = achievement.progressPercent.clamp(0.0, 1.0);

    return GestureDetector(
      onTap: onTap,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: unlocked ? Colors.white : SahoolColors.warmCream,
          borderRadius: BorderRadius.circular(SahoolRadius.large),
          border: Border.all(
            color: unlocked ? _tierColor : Colors.grey.shade300,
            width: unlocked ? 2.0 : 1.0,
          ),
          boxShadow: unlocked ? SahoolShadows.small : null,
        ),
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.all(SahoolSpacing.md),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Icon with circular progress
                  SizedBox(
                    width: 56,
                    height: 56,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        CircularProgressIndicator(
                          value: progress,
                          strokeWidth: 3.0,
                          backgroundColor: Colors.grey.shade200,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            unlocked ? SahoolColors.success : _tierColor,
                          ),
                        ),
                        Icon(
                          _iconData,
                          size: 28,
                          color: unlocked
                              ? _tierColor
                              : SahoolColors.textSecondary,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: SahoolSpacing.sm),
                  // Title
                  Text(
                    achievement.title,
                    textAlign: TextAlign.center,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: unlocked
                          ? SahoolColors.textDark
                          : SahoolColors.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 2),
                  // Progress text
                  Text(
                    '${achievement.progress.current}/${achievement.progress.target}',
                    style: const TextStyle(
                      fontSize: 11,
                      color: SahoolColors.textSecondary,
                    ),
                  ),
                  const SizedBox(height: SahoolSpacing.xs),
                  // Points
                  Text(
                    '+${achievement.pointsValue}',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: unlocked
                          ? SahoolColors.success
                          : SahoolColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            // Tier badge - شارة المستوى
            Positioned(
              top: 6,
              left: 6,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: _tierColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(SahoolRadius.small),
                  border: Border.all(color: _tierColor, width: 0.5),
                ),
                child: Text(
                  _tierLabel,
                  style: TextStyle(
                    fontSize: 9,
                    fontWeight: FontWeight.bold,
                    color: _tierColor,
                  ),
                ),
              ),
            ),
            // Locked overlay - طبقة القفل
            if (!unlocked && progress < 1.0)
              Positioned.fill(
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.45),
                    borderRadius: BorderRadius.circular(SahoolRadius.large),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
