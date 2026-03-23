import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import '../../../../core/config/theme.dart';

/// Profile Header Widget for Settings
/// رأس الملف الشخصي للإعدادات
class ProfileHeader extends StatelessWidget {
  /// User display name
  final String name;

  /// User email or phone
  final String? email;

  /// User farm/organization name
  final String? farmName;

  /// Profile image URL
  final String? avatarUrl;

  /// Membership/subscription tier
  final String? tier;

  /// Callback when edit is pressed
  final VoidCallback? onEditPressed;

  /// Callback when avatar is pressed
  final VoidCallback? onAvatarPressed;

  /// Whether the user is verified
  final bool isVerified;

  const ProfileHeader({
    super.key,
    required this.name,
    this.email,
    this.farmName,
    this.avatarUrl,
    this.tier,
    this.onEditPressed,
    this.onAvatarPressed,
    this.isVerified = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topRight,
          end: Alignment.bottomLeft,
          colors: [
            SahoolTheme.primary,
            SahoolTheme.primaryDark,
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: SahoolTheme.primary.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              // Avatar
              GestureDetector(
                onTap: onAvatarPressed,
                child: Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: Colors.white.withOpacity(0.3),
                      width: 3,
                    ),
                  ),
                  child: avatarUrl != null
                      ? ClipOval(
                          child: CachedNetworkImage(
                            imageUrl: avatarUrl!,
                            fit: BoxFit.cover,
                            errorWidget: (_, __, ___) => _buildAvatarPlaceholder(),
                          ),
                        )
                      : _buildAvatarPlaceholder(),
                ),
              ),
              const SizedBox(width: 16),

              // User info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            name,
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        if (isVerified) ...[
                          const SizedBox(width: 6),
                          const Icon(
                            Icons.verified,
                            color: Colors.white,
                            size: 18,
                          ),
                        ],
                      ],
                    ),
                    if (farmName != null) ...[
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(
                            Icons.location_on_outlined,
                            color: Colors.white.withOpacity(0.8),
                            size: 14,
                          ),
                          const SizedBox(width: 4),
                          Flexible(
                            child: Text(
                              farmName!,
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.white.withOpacity(0.9),
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ],
                    if (email != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        email!,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.white.withOpacity(0.7),
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),

              // Edit button
              if (onEditPressed != null)
                IconButton(
                  onPressed: onEditPressed,
                  icon: const Icon(Icons.edit_outlined),
                  color: Colors.white,
                  style: IconButton.styleFrom(
                    backgroundColor: Colors.white.withOpacity(0.2),
                  ),
                ),
            ],
          ),

          // Membership tier badge
          if (tier != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.15),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: Colors.white.withOpacity(0.3),
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    _getTierIcon(tier!),
                    color: _getTierColor(tier!),
                    size: 18,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    tier!,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: _getTierColor(tier!),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAvatarPlaceholder() {
    return Center(
      child: Text(
        name.isNotEmpty ? name[0].toUpperCase() : '?',
        style: const TextStyle(
          fontSize: 28,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
    );
  }

  IconData _getTierIcon(String tier) {
    switch (tier.toLowerCase()) {
      case 'enterprise':
      case 'مؤسسي':
        return Icons.diamond_outlined;
      case 'professional':
      case 'احترافي':
        return Icons.workspace_premium_outlined;
      case 'starter':
      case 'مبتدئ':
        return Icons.stars_outlined;
      default:
        return Icons.account_circle_outlined;
    }
  }

  Color _getTierColor(String tier) {
    switch (tier.toLowerCase()) {
      case 'enterprise':
      case 'مؤسسي':
        return Colors.amber;
      case 'professional':
      case 'احترافي':
        return Colors.lightBlueAccent;
      case 'starter':
      case 'مبتدئ':
        return Colors.white;
      default:
        return Colors.white70;
    }
  }
}

/// Compact Profile Header
/// رأس ملف شخصي مضغوط
class CompactProfileHeader extends StatelessWidget {
  final String name;
  final String? subtitle;
  final String? avatarUrl;
  final VoidCallback? onTap;

  const CompactProfileHeader({
    super.key,
    required this.name,
    this.subtitle,
    this.avatarUrl,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Avatar
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: SahoolTheme.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: avatarUrl != null
                    ? ClipOval(
                        child: CachedNetworkImage(
                          imageUrl: avatarUrl!,
                          fit: BoxFit.cover,
                          errorWidget: (_, __, ___) => _buildPlaceholder(),
                        ),
                      )
                    : _buildPlaceholder(),
              ),
              const SizedBox(width: 12),

              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.bold,
                        color: isDark ? Colors.white : Colors.black87,
                      ),
                    ),
                    if (subtitle != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        subtitle!,
                        style: TextStyle(
                          fontSize: 14,
                          color: isDark ? Colors.grey[400] : Colors.grey[600],
                        ),
                      ),
                    ],
                  ],
                ),
              ),

              // Arrow
              if (onTap != null)
                Icon(
                  Icons.chevron_left_rounded,
                  color: isDark ? Colors.grey[600] : Colors.grey[400],
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPlaceholder() {
    return const Center(
      child: Icon(
        Icons.person_rounded,
        color: SahoolTheme.primary,
        size: 28,
      ),
    );
  }
}
