/// SAHOOL Runtime Permission Usage Examples
/// أمثلة على استخدام نظام الصلاحيات
///
/// This file demonstrates various ways to use the runtime permission system.
/// DO NOT import this file in production code - it's for reference only.

// ignore_for_file: unused_local_variable, unused_element

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'permissions.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Example 1: Simple Permission Request in a Button
// ═══════════════════════════════════════════════════════════════════════════

class Example1TakePhotoButton extends ConsumerWidget {
  const Example1TakePhotoButton({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ElevatedButton.icon(
      onPressed: () async {
        // Request camera permission
        final controller = ref.read(permissionControllerProvider);
        final granted = await controller.requestCamera();

        if (granted) {
          // Permission granted - open camera
          _openCamera(context);
        } else {
          // Permission denied - show message
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('نحتاج إلى صلاحية الكاميرا لالتقاط الصور'),
              ),
            );
          }
        }
      },
      icon: const Icon(Icons.camera_alt),
      label: const Text('التقاط صورة'),
    );
  }

  void _openCamera(BuildContext context) {
    // Open camera implementation
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 2: Using Permission Gate Widget
// ═══════════════════════════════════════════════════════════════════════════

class Example2CameraScreen extends StatelessWidget {
  const Example2CameraScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الكاميرا')),
      body: RuntimePermissionGate(
        permission: PermissionType.camera,
        autoRequest: true, // Automatically request permission
        onPermissionDenied: () {
          debugPrint('Camera permission denied');
        },
        child: const CameraWidget(),
      ),
    );
  }
}

class CameraWidget extends StatelessWidget {
  const CameraWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Camera View'),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 3: Request Multiple Permissions Before Navigation
// ═══════════════════════════════════════════════════════════════════════════

class Example3FieldTaskButton extends ConsumerWidget {
  const Example3FieldTaskButton({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ElevatedButton(
      onPressed: () async {
        // Check if all field operations permissions are granted
        final hasAll = ref.read(hasFieldOperationsPermissionsProvider);

        if (hasAll) {
          // All permissions granted, navigate
          _navigateToFieldTask(context);
        } else {
          // Request missing permissions
          final allGranted = await FieldOperationsPermissionDialog.show(context);

          if (allGranted && context.mounted) {
            _navigateToFieldTask(context);
          }
        }
      },
      child: const Text('بدء العمل الميداني'),
    );
  }

  void _navigateToFieldTask(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const FieldTaskScreen()),
    );
  }
}

class FieldTaskScreen extends StatelessWidget {
  const FieldTaskScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('العمل الميداني')),
      body: const Center(child: Text('Field Task')),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 4: Checking Permission Status with Providers
// ═══════════════════════════════════════════════════════════════════════════

class Example4LocationWidget extends ConsumerWidget {
  const Example4LocationWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch location permission status
    final hasLocation = ref.watch(hasLocationPermissionProvider);

    return Card(
      child: ListTile(
        leading: Icon(
          Icons.location_on,
          color: hasLocation ? Colors.green : Colors.red,
        ),
        title: Text(hasLocation ? 'الموقع مفعّل' : 'الموقع غير مفعّل'),
        subtitle: Text(
          hasLocation
              ? 'يمكنك الآن تحديد مواقع الحقول'
              : 'الرجاء تفعيل صلاحية الموقع',
        ),
        trailing: hasLocation
            ? const Icon(Icons.check_circle, color: Colors.green)
            : PermissionRequestButton(
                permission: PermissionType.location,
                label: 'تفعيل',
              ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 5: Permissions Settings Screen
// ═══════════════════════════════════════════════════════════════════════════

class Example5PermissionsSettingsScreen extends StatelessWidget {
  const Example5PermissionsSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('الصلاحيات'),
      ),
      body: const SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'صلاحيات التطبيق',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            Text(
              'يحتاج التطبيق إلى هذه الصلاحيات للعمل بشكل صحيح:',
              style: TextStyle(color: Colors.grey),
            ),
            SizedBox(height: 24),
            PermissionsOverview(showOnlyRequired: true),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 6: Onboarding with Permission Request
// ═══════════════════════════════════════════════════════════════════════════

class Example6OnboardingFlow extends StatefulWidget {
  const Example6OnboardingFlow({super.key});

  @override
  State<Example6OnboardingFlow> createState() => _Example6OnboardingFlowState();
}

class _Example6OnboardingFlowState extends State<Example6OnboardingFlow> {
  int _currentPage = 0;

  @override
  Widget build(BuildContext context) {
    if (_currentPage == 2) {
      // Permission request page
      return PermissionRequiredScreen(
        requiredPermissions: const [
          PermissionType.location,
          PermissionType.camera,
          PermissionType.storage,
        ],
        onAllGranted: () {
          // Navigate to main app
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => const MainAppScreen()),
          );
        },
      );
    }

    return Scaffold(
      body: PageView(
        onPageChanged: (page) => setState(() => _currentPage = page),
        children: const [
          OnboardingPage1(),
          OnboardingPage2(),
        ],
      ),
    );
  }
}

class OnboardingPage1 extends StatelessWidget {
  const OnboardingPage1({super.key});

  @override
  Widget build(BuildContext context) => const Placeholder();
}

class OnboardingPage2 extends StatelessWidget {
  const OnboardingPage2({super.key});

  @override
  Widget build(BuildContext context) => const Placeholder();
}

class MainAppScreen extends StatelessWidget {
  const MainAppScreen({super.key});

  @override
  Widget build(BuildContext context) => const Placeholder();
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 7: Using WidgetRef Extension Methods
// ═══════════════════════════════════════════════════════════════════════════

class Example7QuickAccessWidget extends ConsumerWidget {
  const Example7QuickAccessWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      children: [
        // Quick permission check using extension
        if (ref.hasPermission(PermissionType.camera))
          const Text('لديك صلاحية الكاميرا'),

        // Check all field operations permissions
        if (ref.hasFieldOperationsPermissions)
          const Text('جميع صلاحيات العمل الميداني ممنوحة'),

        // Quick permission request
        ElevatedButton(
          onPressed: () async {
            await ref.permissions.requestCamera();
          },
          child: const Text('طلب صلاحية الكاميرا'),
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 8: Handling Permanently Denied Permissions
// ═══════════════════════════════════════════════════════════════════════════

class Example8PermanentlyDeniedHandler extends ConsumerWidget {
  const Example8PermanentlyDeniedHandler({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(permissionStateProvider);
    final permanentlyDenied = state.permanentlyDeniedPermissions;

    if (permanentlyDenied.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'بعض الصلاحيات مرفوضة نهائياً',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            ...permanentlyDenied.map(
              (type) => Text('• ${type.arabicName}'),
            ),
            const SizedBox(height: 8),
            FilledButton.icon(
              onPressed: () {
                ref.read(permissionServiceProvider).openSettings();
              },
              icon: const Icon(Icons.settings),
              label: const Text('فتح الإعدادات'),
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 9: Integrating with Existing Image Picker Code
// ═══════════════════════════════════════════════════════════════════════════

class Example9ImagePickerIntegration extends ConsumerWidget {
  const Example9ImagePickerIntegration({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ElevatedButton.icon(
      onPressed: () async {
        // Check camera permission before using ImagePicker
        final controller = ref.read(permissionControllerProvider);
        final hasCameraPermission = await controller.requestCamera();
        final hasStoragePermission = await controller.requestStorage();

        if (hasCameraPermission && hasStoragePermission && context.mounted) {
          // Now safe to use ImagePicker
          _pickImage(context);
        }
      },
      icon: const Icon(Icons.photo_camera),
      label: const Text('اختيار صورة'),
    );
  }

  Future<void> _pickImage(BuildContext context) async {
    // Use ImagePicker here
    // final picker = ImagePicker();
    // final image = await picker.pickImage(source: ImageSource.camera);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 10: Permission Status in Settings
// ═══════════════════════════════════════════════════════════════════════════

class Example10SettingsIntegration extends ConsumerWidget {
  const Example10SettingsIntegration({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      children: [
        const ListTile(
          title: Text('الإعدادات العامة'),
          leading: Icon(Icons.settings),
        ),
        const Divider(),
        ListTile(
          title: const Text('الصلاحيات'),
          subtitle: const Text('إدارة صلاحيات التطبيق'),
          leading: const Icon(Icons.security),
          trailing: const Icon(Icons.chevron_right),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => const Example5PermissionsSettingsScreen(),
              ),
            );
          },
        ),
        const Divider(),
        PermissionStatusCard(
          permission: PermissionType.location,
          description: 'لتحديد مواقع الحقول',
        ),
        PermissionStatusCard(
          permission: PermissionType.camera,
          description: 'لالتقاط صور المحاصيل',
        ),
        PermissionStatusCard(
          permission: PermissionType.storage,
          description: 'لحفظ الصور والملفات',
        ),
      ],
    );
  }
}
