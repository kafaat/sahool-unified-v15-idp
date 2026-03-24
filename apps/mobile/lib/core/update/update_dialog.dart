/// SAHOOL App Update Dialog UI
/// واجهة مستخدم نافذة تحديث التطبيق
///
/// Features:
/// - Force update dialog (non-dismissable)
/// - Optional update dialog with skip/remind later options
/// - Update banner for non-intrusive notifications
/// - Bilingual support (Arabic/English)
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../theme/sahool_theme.dart';
import 'update_checker.dart';
import 'version_comparator.dart';

/// Show update dialog based on update result
/// عرض نافذة التحديث بناءً على نتيجة التحديث
Future<void> showUpdateDialog(
  BuildContext context, {
  required UpdateCheckResult result,
  required WidgetRef ref,
  bool isArabic = true,
}) async {
  if (!result.updateAvailable) return;
  if (result.skipped || result.remindLater) return;

  if (result.forceUpdate) {
    await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => ForceUpdateDialog(
        result: result,
        ref: ref,
        isArabic: isArabic,
      ),
    );
  } else {
    await showDialog(
      context: context,
      barrierDismissible: true,
      builder: (context) => OptionalUpdateDialog(
        result: result,
        ref: ref,
        isArabic: isArabic,
      ),
    );
  }
}

/// Force update dialog - cannot be dismissed
/// نافذة التحديث الإجباري - لا يمكن إغلاقها
class ForceUpdateDialog extends ConsumerWidget {
  final UpdateCheckResult result;
  final WidgetRef ref;
  final bool isArabic;

  const ForceUpdateDialog({
    super.key,
    required this.result,
    required this.ref,
    required this.isArabic,
  });

  @override
  Widget build(BuildContext context, WidgetRef widgetRef) {
    final updateInfo = result.updateInfo;
    final releaseNotes = isArabic
        ? (updateInfo?.releaseNotesAr.isNotEmpty == true
            ? updateInfo!.releaseNotesAr
            : updateInfo?.releaseNotesEn ?? '')
        : updateInfo?.releaseNotesEn ?? '';

    final newFeatures = isArabic
        ? (updateInfo?.newFeaturesAr.isNotEmpty == true
            ? updateInfo!.newFeaturesAr
            : updateInfo?.newFeaturesEn ?? [])
        : updateInfo?.newFeaturesEn ?? [];

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        // Prevent back button from closing the dialog
        if (!didPop) {
          SystemNavigator.pop(); // Close the app instead
        }
      },
      child: Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Critical update icon
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: SahoolColors.danger.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.system_update,
                  color: SahoolColors.danger,
                  size: 48,
                ),
              ),

              const SizedBox(height: 20),

              // Title
              Text(
                isArabic ? 'تحديث مطلوب' : 'Update Required',
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: SahoolColors.textDark,
                ),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 12),

              // Version info
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: SahoolColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${result.currentVersion} → ${updateInfo?.latestVersion ?? ''}',
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: SahoolColors.primary,
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // Description
              Text(
                isArabic
                    ? 'يجب تحديث التطبيق للاستمرار في الاستخدام. يتضمن هذا التحديث تحسينات هامة وإصلاحات أمنية.'
                    : 'You must update the app to continue using it. This update includes important improvements and security fixes.',
                style: const TextStyle(
                  fontSize: 14,
                  color: SahoolColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),

              // Release notes
              if (releaseNotes.isNotEmpty) ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isArabic ? 'ما الجديد:' : "What's New:",
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        releaseNotes,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[700],
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              // New features list
              if (newFeatures.isNotEmpty) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  constraints: const BoxConstraints(maxHeight: 150),
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: newFeatures.length,
                    itemBuilder: (context, index) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(
                              Icons.check_circle,
                              color: SahoolColors.success,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                newFeatures[index],
                                style: const TextStyle(fontSize: 13),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ],

              const SizedBox(height: 24),

              // Update button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () async {
                    await widgetRef
                        .read(updateCheckerProvider.notifier)
                        .openAppStore();
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: SahoolColors.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  icon: const Icon(Icons.download),
                  label: Text(
                    isArabic ? 'تحديث الآن' : 'Update Now',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              // Exit app button
              TextButton(
                onPressed: () {
                  SystemNavigator.pop();
                },
                child: Text(
                  isArabic ? 'إغلاق التطبيق' : 'Exit App',
                  style: const TextStyle(color: SahoolColors.textSecondary),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Optional update dialog - can be dismissed
/// نافذة التحديث الاختياري - يمكن إغلاقها
class OptionalUpdateDialog extends ConsumerWidget {
  final UpdateCheckResult result;
  final WidgetRef ref;
  final bool isArabic;

  const OptionalUpdateDialog({
    super.key,
    required this.result,
    required this.ref,
    required this.isArabic,
  });

  @override
  Widget build(BuildContext context, WidgetRef widgetRef) {
    final updateInfo = result.updateInfo;
    final releaseNotes = isArabic
        ? (updateInfo?.releaseNotesAr.isNotEmpty == true
            ? updateInfo!.releaseNotesAr
            : updateInfo?.releaseNotesEn ?? '')
        : updateInfo?.releaseNotesEn ?? '';

    final newFeatures = isArabic
        ? (updateInfo?.newFeaturesAr.isNotEmpty == true
            ? updateInfo!.newFeaturesAr
            : updateInfo?.newFeaturesEn ?? [])
        : updateInfo?.newFeaturesEn ?? [];

    // Get update type description
    String updateTypeTitle;
    IconData updateIcon;
    Color updateColor;

    switch (result.updateType) {
      case UpdateType.major:
        updateTypeTitle = isArabic ? 'تحديث رئيسي متاح' : 'Major Update Available';
        updateIcon = Icons.new_releases;
        updateColor = SahoolColors.primary;
        break;
      case UpdateType.minor:
        updateTypeTitle = isArabic ? 'تحديث جديد متاح' : 'New Update Available';
        updateIcon = Icons.system_update_alt;
        updateColor = SahoolColors.info;
        break;
      case UpdateType.patch:
        updateTypeTitle =
            isArabic ? 'تحديث تصحيحي متاح' : 'Patch Update Available';
        updateIcon = Icons.security_update;
        updateColor = SahoolColors.success;
        break;
      case UpdateType.none:
        updateTypeTitle =
            isArabic ? 'التطبيق محدث' : 'App is Up to Date';
        updateIcon = Icons.check_circle;
        updateColor = SahoolColors.success;
        break;
    }

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Update icon
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: updateColor.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                updateIcon,
                color: updateColor,
                size: 48,
              ),
            ),

            const SizedBox(height: 20),

            // Title
            Text(
              updateTypeTitle,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: SahoolColors.textDark,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 12),

            // Version info
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: updateColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                '${result.currentVersion} → ${updateInfo?.latestVersion ?? ''}',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: updateColor,
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Description based on update type
            Text(
              _getUpdateDescription(result.updateType, isArabic),
              style: const TextStyle(
                fontSize: 14,
                color: SahoolColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),

            // Release notes
            if (releaseNotes.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isArabic ? 'ما الجديد:' : "What's New:",
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      releaseNotes,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[700],
                      ),
                    ),
                  ],
                ),
              ),
            ],

            // New features list
            if (newFeatures.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                constraints: const BoxConstraints(maxHeight: 120),
                child: ListView.builder(
                  shrinkWrap: true,
                  itemCount: newFeatures.length.clamp(0, 5),
                  itemBuilder: (context, index) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(
                            Icons.star,
                            color: SahoolColors.harvestGold,
                            size: 16,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              newFeatures[index],
                              style: const TextStyle(fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],

            const SizedBox(height: 24),

            // Update button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () async {
                  await widgetRef
                      .read(updateCheckerProvider.notifier)
                      .openAppStore();
                  if (context.mounted) {
                    Navigator.of(context).pop();
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: updateColor,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                icon: const Icon(Icons.download),
                label: Text(
                  isArabic ? 'تحديث الآن' : 'Update Now',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Remind later / Skip buttons
            Row(
              children: [
                // Remind later
                Expanded(
                  child: TextButton(
                    onPressed: () async {
                      await widgetRef
                          .read(updateCheckerProvider.notifier)
                          .remindLater();
                      if (context.mounted) {
                        Navigator.of(context).pop();
                      }
                    },
                    child: Text(
                      isArabic ? 'ذكرني لاحقاً' : 'Remind Later',
                      style: const TextStyle(
                        color: SahoolColors.textSecondary,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ),
                // Skip this version
                Expanded(
                  child: TextButton(
                    onPressed: () async {
                      await widgetRef
                          .read(updateCheckerProvider.notifier)
                          .skipVersion();
                      if (context.mounted) {
                        Navigator.of(context).pop();
                      }
                    },
                    child: Text(
                      isArabic ? 'تخطي هذا الإصدار' : 'Skip This Version',
                      style: const TextStyle(
                        color: SahoolColors.textSecondary,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _getUpdateDescription(UpdateType type, bool isArabic) {
    switch (type) {
      case UpdateType.major:
        return isArabic
            ? 'يتوفر إصدار جديد رئيسي مع تحسينات كبيرة وميزات جديدة. ننصح بشدة بالتحديث.'
            : 'A new major version is available with significant improvements and new features. We highly recommend updating.';
      case UpdateType.minor:
        return isArabic
            ? 'يتوفر تحديث جديد مع ميزات وتحسينات إضافية.'
            : 'A new update is available with additional features and improvements.';
      case UpdateType.patch:
        return isArabic
            ? 'يتوفر تحديث تصحيحي مع إصلاحات للأخطاء وتحسينات في الأداء.'
            : 'A patch update is available with bug fixes and performance improvements.';
      case UpdateType.none:
        return isArabic ? 'تطبيقك محدث!' : 'Your app is up to date!';
    }
  }
}

/// Update banner widget - non-intrusive notification
/// شريط إشعار التحديث - إشعار غير متطفل
class UpdateBanner extends ConsumerWidget {
  final bool isArabic;
  final VoidCallback? onDismiss;

  const UpdateBanner({
    super.key,
    this.isArabic = true,
    this.onDismiss,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final updateState = ref.watch(updateCheckerProvider);
    final result = updateState.lastResult;

    // Don't show if no update available or if skipped/remind later
    if (result == null ||
        !result.updateAvailable ||
        result.forceUpdate ||
        result.skipped ||
        result.remindLater) {
      return const SizedBox.shrink();
    }

    final updateInfo = result.updateInfo;

    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            SahoolColors.primary,
            SahoolColors.primary.withValues(alpha: 0.8),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: SahoolColors.primary.withValues(alpha: 0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {
            showUpdateDialog(
              context,
              result: result,
              ref: ref,
              isArabic: isArabic,
            );
          },
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                // Icon
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.system_update,
                    color: Colors.white,
                    size: 24,
                  ),
                ),

                const SizedBox(width: 16),

                // Text content
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        isArabic ? 'تحديث جديد متاح' : 'New Update Available',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        isArabic
                            ? 'الإصدار ${updateInfo?.latestVersion ?? ''}'
                            : 'Version ${updateInfo?.latestVersion ?? ''}',
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.9),
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),

                // Update button
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    isArabic ? 'تحديث' : 'Update',
                    style: const TextStyle(
                      color: SahoolColors.primary,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),

                // Dismiss button
                if (onDismiss != null) ...[
                  const SizedBox(width: 8),
                  IconButton(
                    onPressed: () {
                      ref.read(updateCheckerProvider.notifier).remindLater();
                      onDismiss?.call();
                    },
                    icon: Icon(
                      Icons.close,
                      color: Colors.white.withValues(alpha: 0.7),
                      size: 20,
                    ),
                    constraints: const BoxConstraints(
                      minWidth: 32,
                      minHeight: 32,
                    ),
                    padding: EdgeInsets.zero,
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// App update wrapper widget - checks for updates and shows dialogs
/// غلاف التحقق من تحديث التطبيق - يتحقق من التحديثات ويعرض النوافذ
class AppUpdateWrapper extends ConsumerStatefulWidget {
  final Widget child;
  final bool isArabic;

  const AppUpdateWrapper({
    super.key,
    required this.child,
    this.isArabic = true,
  });

  @override
  ConsumerState<AppUpdateWrapper> createState() => _AppUpdateWrapperState();
}

class _AppUpdateWrapperState extends ConsumerState<AppUpdateWrapper> {
  bool _hasShownDialog = false;

  @override
  void initState() {
    super.initState();
    // Initialize update checker
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(updateCheckerProvider.notifier).initialize();
    });
  }

  @override
  Widget build(BuildContext context) {
    // Listen for update state changes
    ref.listen<UpdateCheckerState>(updateCheckerProvider, (previous, next) {
      final result = next.lastResult;
      if (result != null && result.updateAvailable && !_hasShownDialog) {
        _hasShownDialog = true;
        // Show dialog after build
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (mounted) {
            showUpdateDialog(
              context,
              result: result,
              ref: ref,
              isArabic: widget.isArabic,
            );
          }
        });
      }
    });

    return widget.child;
  }
}
