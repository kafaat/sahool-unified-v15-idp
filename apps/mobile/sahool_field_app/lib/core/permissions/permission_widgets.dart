import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'permission_service.dart';
import 'permission_provider.dart';

/// SAHOOL Permission Widgets
/// ودجات صلاحيات النظام
///
/// Reusable widgets for permission UI

// ═══════════════════════════════════════════════════════════════════════════
// Permission Gate Widget
// ═══════════════════════════════════════════════════════════════════════════

/// Widget that shows/hides content based on runtime permission status
///
/// Example:
/// ```dart
/// RuntimePermissionGate(
///   permission: PermissionType.camera,
///   child: CameraButton(),
///   onPermissionDenied: () => print('Camera denied'),
/// )
/// ```
class RuntimePermissionGate extends ConsumerWidget {
  final PermissionType permission;
  final Widget child;
  final Widget? fallback;
  final VoidCallback? onPermissionDenied;
  final bool autoRequest;

  const RuntimePermissionGate({
    super.key,
    required this.permission,
    required this.child,
    this.fallback,
    this.onPermissionDenied,
    this.autoRequest = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(permissionStateProvider);

    final isGranted = state.isGranted(permission);

    if (isGranted) {
      return child;
    }

    // Auto-request permission if enabled
    if (autoRequest && !state.isLoading) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _requestPermission(ref);
      });
    }

    return fallback ??
        Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                permission.icon,
                size: 48,
                color: Theme.of(context).colorScheme.error,
              ),
              const SizedBox(height: 16),
              Text(
                'صلاحية ${permission.arabicName} مطلوبة',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              FilledButton.icon(
                onPressed: () => _requestPermission(ref),
                icon: const Icon(Icons.security),
                label: const Text('طلب الصلاحية'),
              ),
            ],
          ),
        );
  }

  Future<void> _requestPermission(WidgetRef ref) async {
    final controller = ref.read(permissionControllerProvider);
    bool granted = false;

    switch (permission) {
      case PermissionType.location:
        granted = await controller.requestLocation();
        break;
      case PermissionType.camera:
        granted = await controller.requestCamera();
        break;
      case PermissionType.storage:
      case PermissionType.photos:
        granted = await controller.requestStorage();
        break;
      case PermissionType.notification:
        granted = await controller.requestNotification();
        break;
    }

    if (!granted && onPermissionDenied != null) {
      onPermissionDenied!();
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Permission Request Button
// ═══════════════════════════════════════════════════════════════════════════

/// Button that requests a specific permission
class PermissionRequestButton extends ConsumerWidget {
  final PermissionType permission;
  final String? label;
  final VoidCallback? onGranted;
  final VoidCallback? onDenied;

  const PermissionRequestButton({
    super.key,
    required this.permission,
    this.label,
    this.onGranted,
    this.onDenied,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(permissionStateProvider);
    final isGranted = state.isGranted(permission);

    if (isGranted) {
      return FilledButton.icon(
        onPressed: null,
        icon: const Icon(Icons.check_circle),
        label: Text('${permission.arabicName} ممنوحة'),
      );
    }

    return FilledButton.icon(
      onPressed: () => _requestPermission(context, ref),
      icon: Icon(permission.icon),
      label: Text(label ?? 'طلب ${permission.arabicName}'),
    );
  }

  Future<void> _requestPermission(BuildContext context, WidgetRef ref) async {
    final controller = ref.read(permissionControllerProvider);
    final service = ref.read(permissionServiceProvider);
    bool granted = false;

    switch (permission) {
      case PermissionType.location:
        granted = await service.requestLocationPermission(context: context);
        break;
      case PermissionType.camera:
        granted = await service.requestCameraPermission(context: context);
        break;
      case PermissionType.storage:
      case PermissionType.photos:
        granted = await service.requestStoragePermission(context: context);
        break;
      case PermissionType.notification:
        granted = await service.requestNotificationPermission(context: context);
        break;
    }

    // Update state
    await controller.refresh();

    if (granted && onGranted != null) {
      onGranted!();
    } else if (!granted && onDenied != null) {
      onDenied!();
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Permission Status Card
// ═══════════════════════════════════════════════════════════════════════════

/// Card showing permission status with action button
class PermissionStatusCard extends ConsumerWidget {
  final PermissionType permission;
  final String? description;

  const PermissionStatusCard({
    super.key,
    required this.permission,
    this.description,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(permissionStateProvider);
    final status = state.permissions[permission];
    final isGranted = status?.isGranted ?? false;
    final isPermanentlyDenied = status?.isPermanentlyDenied ?? false;

    return Card(
      child: ListTile(
        leading: Icon(
          permission.icon,
          color: isGranted
              ? Theme.of(context).colorScheme.primary
              : Theme.of(context).colorScheme.error,
        ),
        title: Text(permission.arabicName),
        subtitle: Text(
          description ?? _getStatusText(status),
          style: TextStyle(
            color: isGranted ? Colors.green : Colors.red,
          ),
        ),
        trailing: _buildActionButton(context, ref, isGranted, isPermanentlyDenied),
      ),
    );
  }

  String _getStatusText(PermissionStatus? status) {
    if (status == null) return 'غير معروف';

    switch (status) {
      case PermissionStatus.granted:
        return 'ممنوحة ✓';
      case PermissionStatus.denied:
        return 'مرفوضة';
      case PermissionStatus.permanentlyDenied:
        return 'مرفوضة نهائياً';
      case PermissionStatus.restricted:
        return 'محظورة';
      case PermissionStatus.limited:
        return 'محدودة';
      case PermissionStatus.provisional:
        return 'مؤقتة';
    }
  }

  Widget? _buildActionButton(
    BuildContext context,
    WidgetRef ref,
    bool isGranted,
    bool isPermanentlyDenied,
  ) {
    if (isGranted) {
      return const Icon(Icons.check_circle, color: Colors.green);
    }

    if (isPermanentlyDenied) {
      return TextButton(
        onPressed: () {
          final service = ref.read(permissionServiceProvider);
          service.openSettings();
        },
        child: const Text('إعدادات'),
      );
    }

    return PermissionRequestButton(
      permission: permission,
      label: 'السماح',
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// All Permissions Overview
// ═══════════════════════════════════════════════════════════════════════════

/// Widget showing all app permissions status
class PermissionsOverview extends ConsumerWidget {
  final bool showOnlyRequired;

  const PermissionsOverview({
    super.key,
    this.showOnlyRequired = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(permissionStateProvider);

    if (state.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    final permissionsToShow = showOnlyRequired
        ? [
            PermissionType.location,
            PermissionType.camera,
            PermissionType.storage,
          ]
        : PermissionType.values;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ...permissionsToShow.map(
          (type) => PermissionStatusCard(permission: type),
        ),
        const SizedBox(height: 16),
        _buildSummary(context, state, permissionsToShow),
      ],
    );
  }

  Widget _buildSummary(
    BuildContext context,
    PermissionState state,
    List<PermissionType> permissions,
  ) {
    final grantedCount = permissions
        .where((type) => state.isGranted(type))
        .length;
    final totalCount = permissions.length;

    return Card(
      color: grantedCount == totalCount
          ? Theme.of(context).colorScheme.primaryContainer
          : Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              '$grantedCount من $totalCount صلاحيات ممنوحة',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            if (grantedCount < totalCount) ...[
              const SizedBox(height: 8),
              FilledButton(
                onPressed: () async {
                  final controller = ref.read(permissionControllerProvider);
                  await controller.requestAllPermissions();
                },
                child: const Text('طلب جميع الصلاحيات'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Field Operations Permission Check
// ═══════════════════════════════════════════════════════════════════════════

/// Dialog for requesting field operations permissions
class FieldOperationsPermissionDialog extends ConsumerWidget {
  const FieldOperationsPermissionDialog({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final missingPermissions =
        ref.watch(missingFieldOperationsPermissionsProvider);

    if (missingPermissions.isEmpty) {
      // All permissions granted
      Navigator.pop(context, true);
      return const SizedBox.shrink();
    }

    return AlertDialog(
      icon: const Icon(Icons.security, size: 48),
      title: const Text('صلاحيات مطلوبة'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'نحتاج إلى الصلاحيات التالية للعمل الميداني:',
            textAlign: TextAlign.right,
          ),
          const SizedBox(height: 16),
          ...missingPermissions.map(
            (type) => ListTile(
              leading: Icon(type.icon),
              title: Text(type.arabicName),
              dense: true,
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: const Text('إلغاء'),
        ),
        FilledButton(
          onPressed: () async {
            final controller = ref.read(permissionControllerProvider);
            await controller.requestFieldOperationsPermissions();

            // Check again
            final stillMissing =
                ref.read(missingFieldOperationsPermissionsProvider);

            if (context.mounted) {
              Navigator.pop(context, stillMissing.isEmpty);
            }
          },
          child: const Text('متابعة'),
        ),
      ],
    );
  }

  /// Show the dialog and return true if all permissions granted
  static Future<bool> show(BuildContext context) async {
    final result = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (context) => const FieldOperationsPermissionDialog(),
    );

    return result ?? false;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Permission Required Screen
// ═══════════════════════════════════════════════════════════════════════════

/// Full screen for requesting permissions (useful for onboarding)
class PermissionRequiredScreen extends ConsumerWidget {
  final List<PermissionType> requiredPermissions;
  final VoidCallback? onAllGranted;

  const PermissionRequiredScreen({
    super.key,
    this.requiredPermissions = const [
      PermissionType.location,
      PermissionType.camera,
      PermissionType.storage,
    ],
    this.onAllGranted,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(permissionStateProvider);
    final allGranted = requiredPermissions.every((type) => state.isGranted(type));

    if (allGranted && onAllGranted != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        onAllGranted!();
      });
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('صلاحيات التطبيق'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(Icons.security, size: 64),
              const SizedBox(height: 24),
              Text(
                'نحتاج إلى بعض الصلاحيات',
                style: Theme.of(context).textTheme.headlineSmall,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'للحصول على أفضل تجربة، يرجى السماح بالصلاحيات التالية:',
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              Expanded(
                child: ListView(
                  children: requiredPermissions
                      .map((type) => PermissionStatusCard(permission: type))
                      .toList(),
                ),
              ),
              const SizedBox(height: 16),
              if (!allGranted)
                FilledButton.icon(
                  onPressed: () async {
                    final controller = ref.read(permissionControllerProvider);

                    for (final type in requiredPermissions) {
                      switch (type) {
                        case PermissionType.location:
                          await controller.requestLocation();
                          break;
                        case PermissionType.camera:
                          await controller.requestCamera();
                          break;
                        case PermissionType.storage:
                        case PermissionType.photos:
                          await controller.requestStorage();
                          break;
                        case PermissionType.notification:
                          await controller.requestNotification();
                          break;
                      }
                    }
                  },
                  icon: const Icon(Icons.check),
                  label: const Text('طلب الصلاحيات'),
                ),
              if (allGranted)
                FilledButton.icon(
                  onPressed: onAllGranted,
                  icon: const Icon(Icons.check_circle),
                  label: const Text('متابعة'),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
