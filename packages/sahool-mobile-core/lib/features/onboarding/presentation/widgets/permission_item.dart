import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../domain/onboarding_step.dart';

/// SAHOOL Permission Item Widget
/// ويدجت عنصر الإذن
///
/// Displays a permission request item with icon, description, and status
/// يعرض عنصر طلب إذن مع أيقونة ووصف وحالة

class PermissionItem extends StatelessWidget {
  /// Permission data
  final OnboardingPermission permission;

  /// Callback when permission is requested
  final VoidCallback? onRequest;

  /// Whether the item is loading
  final bool isLoading;

  /// Whether to use Arabic text
  final bool isArabic;

  const PermissionItem({
    super.key,
    required this.permission,
    this.onRequest,
    this.isLoading = false,
    this.isArabic = true,
  });

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: permission.isGranted
                ? SahoolColors.success.withValues(alpha: 0.3)
                : Colors.grey[200]!,
            width: 1.5,
          ),
          boxShadow: [
            BoxShadow(
              color: permission.isGranted
                  ? SahoolColors.success.withValues(alpha: 0.1)
                  : Colors.black.withValues(alpha: 0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Icon
              _buildIcon(),
              const SizedBox(width: 16),

              // Text content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            permission.getName(isArabic: isArabic),
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: SahoolColors.textDark,
                            ),
                          ),
                        ),
                        if (permission.isRequired)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: SahoolColors.warning.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              isArabic ? 'مطلوب' : 'Required',
                              style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: SahoolColors.warning,
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      permission.getDescription(isArabic: isArabic),
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey[600],
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),

              // Action button or status
              _buildAction(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildIcon() {
    IconData iconData;
    switch (permission.iconName) {
      case 'location_on':
        iconData = Icons.location_on_rounded;
        break;
      case 'notifications':
        iconData = Icons.notifications_rounded;
        break;
      case 'camera_alt':
        iconData = Icons.camera_alt_rounded;
        break;
      default:
        iconData = Icons.security_rounded;
    }

    return Container(
      width: 56,
      height: 56,
      decoration: BoxDecoration(
        color: permission.isGranted
            ? SahoolColors.success.withValues(alpha: 0.1)
            : SahoolColors.primary.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Icon(
        iconData,
        size: 28,
        color:
            permission.isGranted ? SahoolColors.success : SahoolColors.primary,
      ),
    );
  }

  Widget _buildAction() {
    if (permission.isGranted) {
      return Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: SahoolColors.success.withValues(alpha: 0.1),
          shape: BoxShape.circle,
        ),
        child: const Icon(
          Icons.check_rounded,
          color: SahoolColors.success,
          size: 24,
        ),
      );
    }

    if (isLoading) {
      return const SizedBox(
        width: 40,
        height: 40,
        child: Center(
          child: SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: SahoolColors.primary,
            ),
          ),
        ),
      );
    }

    return SizedBox(
      height: 40,
      child: ElevatedButton(
        onPressed: onRequest,
        style: ElevatedButton.styleFrom(
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0,
        ),
        child: Text(
          isArabic ? 'تفعيل' : 'Enable',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
          ),
        ),
      ),
    );
  }
}

/// Permission list widget
/// ويدجت قائمة الأذونات
class PermissionList extends StatelessWidget {
  /// List of permissions
  final List<OnboardingPermission> permissions;

  /// Callback when a permission is requested
  final void Function(String permissionId)? onPermissionRequest;

  /// Set of loading permission IDs
  final Set<String> loadingPermissions;

  /// Whether to use Arabic text
  final bool isArabic;

  const PermissionList({
    super.key,
    required this.permissions,
    this.onPermissionRequest,
    this.loadingPermissions = const {},
    this.isArabic = true,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: permissions.map((permission) {
        return PermissionItem(
          permission: permission,
          isLoading: loadingPermissions.contains(permission.id),
          isArabic: isArabic,
          onRequest: onPermissionRequest != null
              ? () => onPermissionRequest!(permission.id)
              : null,
        );
      }).toList(),
    );
  }
}

/// Enable all permissions button
/// زر تفعيل جميع الأذونات
class EnableAllPermissionsButton extends StatelessWidget {
  /// Callback when button is pressed
  final VoidCallback? onPressed;

  /// Whether the button is loading
  final bool isLoading;

  /// Whether all permissions are granted
  final bool allGranted;

  /// Whether to use Arabic text
  final bool isArabic;

  const EnableAllPermissionsButton({
    super.key,
    this.onPressed,
    this.isLoading = false,
    this.allGranted = false,
    this.isArabic = true,
  });

  @override
  Widget build(BuildContext context) {
    if (allGranted) {
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.check_circle_rounded,
              color: SahoolColors.success,
              size: 24,
            ),
            const SizedBox(width: 8),
            Text(
              isArabic
                  ? 'تم تفعيل جميع الأذونات'
                  : 'All permissions enabled',
              style: const TextStyle(
                color: SahoolColors.success,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: OutlinedButton.icon(
        onPressed: isLoading ? null : onPressed,
        icon: isLoading
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: SahoolColors.primary,
                ),
              )
            : const Icon(Icons.security_rounded),
        label: Text(
          isArabic ? 'تفعيل جميع الأذونات' : 'Enable All Permissions',
        ),
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}
