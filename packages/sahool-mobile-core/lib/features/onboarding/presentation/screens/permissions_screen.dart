import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../widgets/onboarding_page.dart';
import '../widgets/permission_item.dart';
import '../../state/onboarding_providers.dart';

/// SAHOOL Permissions Screen
/// شاشة الأذونات
///
/// Requests necessary permissions for the app to function
/// تطلب الأذونات اللازمة لعمل التطبيق

class PermissionsScreen extends ConsumerStatefulWidget {
  /// Callback when permissions are granted/skipped
  final VoidCallback? onComplete;

  /// Callback when user goes back
  final VoidCallback? onBack;

  const PermissionsScreen({
    super.key,
    this.onComplete,
    this.onBack,
  });

  @override
  ConsumerState<PermissionsScreen> createState() => _PermissionsScreenState();
}

class _PermissionsScreenState extends ConsumerState<PermissionsScreen> {
  final Set<String> _loadingPermissions = {};
  bool _isRequestingAll = false;

  @override
  void initState() {
    super.initState();
    // Check current permission status on load
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(onboardingControllerProvider.notifier).checkAllPermissionsStatus();
    });
  }

  Future<void> _requestPermission(String permissionId) async {
    setState(() {
      _loadingPermissions.add(permissionId);
    });

    try {
      await ref.read(onboardingControllerProvider.notifier)
          .requestPermission(permissionId);
    } finally {
      if (mounted) {
        setState(() {
          _loadingPermissions.remove(permissionId);
        });
      }
    }
  }

  Future<void> _requestAllPermissions() async {
    setState(() {
      _isRequestingAll = true;
    });

    try {
      await ref.read(onboardingControllerProvider.notifier)
          .requestAllPermissions();
    } finally {
      if (mounted) {
        setState(() {
          _isRequestingAll = false;
        });
      }
    }
  }

  void _onContinue() {
    final allRequired = ref.read(allRequiredPermissionsGrantedProvider);
    if (allRequired) {
      widget.onComplete?.call();
    } else {
      // Show dialog to confirm skipping required permissions
      _showSkipConfirmation();
    }
  }

  void _showSkipConfirmation() {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: const Text('أذونات مطلوبة'),
          content: const Text(
            'بعض الميزات قد لا تعمل بشكل صحيح بدون تفعيل الأذونات المطلوبة. هل تريد المتابعة؟',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('إلغاء'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                widget.onComplete?.call();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.warning,
              ),
              child: const Text('متابعة على أي حال'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final permissions = ref.watch(onboardingPermissionsListProvider);
    final allRequired = ref.watch(allRequiredPermissionsGrantedProvider);
    final allGranted = permissions.every((p) => p.isGranted);

    return OnboardingPage(
      showBackButton: true,
      onBack: widget.onBack,
      skipText: 'تخطي',
      onSkip: () => widget.onComplete?.call(),
      progress: 0.4,
      primaryButtonText: allRequired ? 'متابعة' : 'متابعة على أي حال',
      onPrimaryAction: _onContinue,
      title: 'الأذونات المطلوبة',
      subtitle: 'نحتاج بعض الأذونات لتقديم أفضل تجربة لك',
      illustration: const SizedBox(
        height: 120,
        child: Center(
          child: Icon(
            Icons.security_rounded,
            size: 80,
            color: SahoolColors.primary,
          ),
        ),
      ),
      child: Column(
        children: [
          // Enable all button
          EnableAllPermissionsButton(
            onPressed: _requestAllPermissions,
            isLoading: _isRequestingAll,
            allGranted: allGranted,
            isArabic: true,
          ),

          const SizedBox(height: 24),

          // Permission list
          PermissionList(
            permissions: permissions,
            loadingPermissions: _loadingPermissions,
            isArabic: true,
            onPermissionRequest: _requestPermission,
          ),

          const SizedBox(height: 16),

          // Info text
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: SahoolColors.info.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.info_outline_rounded,
                  color: SahoolColors.info,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'يمكنك تغيير هذه الأذونات لاحقاً من إعدادات الجهاز',
                    style: TextStyle(
                      color: Colors.grey[700],
                      fontSize: 13,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
