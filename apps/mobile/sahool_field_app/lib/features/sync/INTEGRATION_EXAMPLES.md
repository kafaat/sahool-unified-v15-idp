# Sync Widgets Integration Examples

## Quick Start

### 1. Import the widgets

```dart
import 'package:sahool_field_app/features/sync/widgets/sync_widgets.dart';
import 'package:sahool_field_app/features/sync/screens/sync_details_screen.dart';
import 'package:sahool_field_app/features/sync/providers/sync_events_provider.dart';
```

### 2. Add to your app

## Example 1: Home Screen with Sync Status

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'features/sync/widgets/sync_widgets.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ساهول'),
        actions: [
          // Minimal sync indicator in app bar
          Padding(
            padding: const EdgeInsets.only(left: 16),
            child: SyncStatusIndicator(
              style: SyncIndicatorStyle.minimal,
              onTap: () => context.push('/sync-details'),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Sync banner (auto-shows when offline/error/conflicts)
          const AnimatedSyncStatusBanner(
            onRetryTap: _handleRetry,
          ),

          // Main content
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // Detailed sync status card
                SyncStatusIndicator(
                  style: SyncIndicatorStyle.detailed,
                  onTap: () => context.push('/sync-details'),
                ),

                const SizedBox(height: 20),

                // Your other content...
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _handleRetry(BuildContext context, WidgetRef ref) async {
    final result = await ref.read(manualSyncTriggerProvider)();
    if (context.mounted && result.success) {
      FloatingSyncStatusBanner.showSuccess(context);
    }
  }
}
```

## Example 2: Fields List Screen

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/sync/widgets/sync_widgets.dart';

class FieldsListScreen extends ConsumerWidget {
  const FieldsListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncStatus = ref.watch(syncStatusProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('الحقول'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(70),
          child: Container(
            padding: const EdgeInsets.all(8),
            child: SyncStatusIndicator(
              style: SyncIndicatorStyle.expanded,
              onTap: () => context.push('/sync-details'),
              showLastSyncTime: true,
              showPendingCount: true,
            ),
          ),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () => _handleRefresh(ref),
        child: ListView.builder(
          itemCount: fields.length,
          itemBuilder: (context, index) {
            return FieldCard(field: fields[index]);
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/field/create'),
        child: const Icon(Icons.add),
      ),
    );
  }

  Future<void> _handleRefresh(WidgetRef ref) async {
    final result = await ref.read(manualSyncTriggerProvider)();
    return;
  }
}
```

## Example 3: Form Screen with Sync Feedback

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/sync/widgets/sync_widgets.dart';

class FieldFormScreen extends ConsumerStatefulWidget {
  const FieldFormScreen({super.key});

  @override
  ConsumerState<FieldFormScreen> createState() => _FieldFormScreenState();
}

class _FieldFormScreenState extends ConsumerState<FieldFormScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isSaving = false;

  @override
  Widget build(BuildContext context) {
    final isOnline = ref.watch(syncStatusProvider).isOnline;

    return Scaffold(
      appBar: AppBar(
        title: const Text('حقل جديد'),
        actions: [
          // Show online status
          SyncStatusIndicator(
            style: SyncIndicatorStyle.compact,
          ),
        ],
      ),
      body: Column(
        children: [
          // Show offline warning if not online
          if (!isOnline)
            SyncStatusBanner(
              dismissible: false,
            ),

          Expanded(
            child: Form(
              key: _formKey,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // Form fields...
                  TextFormField(
                    decoration: const InputDecoration(
                      labelText: 'اسم الحقل',
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'الرجاء إدخال اسم الحقل';
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: 20),

                  // Save button
                  ElevatedButton(
                    onPressed: _isSaving ? null : _handleSave,
                    child: _isSaving
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation(Colors.white),
                            ),
                          )
                        : const Text('حفظ'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _handleSave() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    try {
      // Save form data
      await _saveField();

      // Show syncing message
      if (mounted) {
        FloatingSyncStatusBanner.showSyncing(context);
      }

      // Trigger sync
      final result = await ref.read(manualSyncTriggerProvider)();

      if (mounted) {
        if (result.success) {
          FloatingSyncStatusBanner.showSuccess(
            context,
            message: 'تم حفظ الحقل ومزامنته بنجاح',
          );
          Navigator.pop(context);
        } else {
          FloatingSyncStatusBanner.show(
            context,
            message: 'تم حفظ الحقل محلياً. سيتم المزامنة عند توفر الاتصال.',
            backgroundColor: SahoolColors.warning,
            icon: Icons.cloud_upload,
          );
        }
      }
    } catch (e) {
      if (mounted) {
        FloatingSyncStatusBanner.showError(
          context,
          'حدث خطأ: $e',
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  Future<void> _saveField() async {
    // Your save logic here
    await Future.delayed(const Duration(seconds: 1));
  }
}
```

## Example 4: Settings Screen with Sync Management

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/sync/widgets/sync_widgets.dart';
import 'features/sync/screens/sync_details_screen.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncStatus = ref.watch(syncStatusProvider);
    final pendingCount = ref.watch(pendingItemsCountProvider);
    final conflictsCount = ref.watch(unreadConflictsCountProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('الإعدادات'),
      ),
      body: ListView(
        children: [
          // Sync section
          const ListTile(
            title: Text(
              'المزامنة',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: SahoolColors.primary,
              ),
            ),
          ),

          // Sync status card
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: SyncStatusIndicator(
              style: SyncIndicatorStyle.detailed,
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const SyncDetailsScreen(),
                ),
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Sync now button
          ListTile(
            leading: const Icon(Icons.sync),
            title: const Text('مزامنة الآن'),
            subtitle: Text(
              pendingCount > 0
                  ? '$pendingCount ${pendingCount == 1 ? 'عنصر' : 'عناصر'} في انتظار المزامنة'
                  : 'جميع البيانات متزامنة',
            ),
            trailing: syncStatus.isSyncing
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.chevron_right),
            onTap: syncStatus.isSyncing ? null : () => _handleSync(context, ref),
          ),

          // View sync details
          ListTile(
            leading: const Icon(Icons.history),
            title: const Text('سجل المزامنة'),
            subtitle: const Text('عرض تفاصيل وسجل المزامنة'),
            trailing: conflictsCount > 0
                ? Badge(
                    label: Text('$conflictsCount'),
                    child: const Icon(Icons.chevron_right),
                  )
                : const Icon(Icons.chevron_right),
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => const SyncDetailsScreen(),
              ),
            ),
          ),

          const Divider(),

          // Other settings...
        ],
      ),
    );
  }

  Future<void> _handleSync(BuildContext context, WidgetRef ref) async {
    FloatingSyncStatusBanner.showSyncing(context);

    final result = await ref.read(manualSyncTriggerProvider)();

    if (context.mounted) {
      if (result.success) {
        FloatingSyncStatusBanner.showSuccess(
          context,
          message: 'تمت المزامنة: ${result.uploaded} مرفوع، ${result.downloaded} محمل',
        );
      } else {
        FloatingSyncStatusBanner.showError(
          context,
          result.message ?? 'فشل في المزامنة',
          onRetry: () => _handleSync(context, ref),
        );
      }
    }
  }
}
```

## Example 5: App-wide Integration with Router

```dart
// router.dart
import 'package:go_router/go_router.dart';
import 'features/sync/screens/sync_details_screen.dart';

final router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: '/sync-details',
      builder: (context, state) => const SyncDetailsScreen(),
    ),
    // Other routes...
  ],
);

// main.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'ساهول',
      theme: SahoolTheme.lightTheme,
      routerConfig: router,
      builder: (context, child) {
        return Column(
          children: [
            // Global sync banner
            Consumer(
              builder: (context, ref, _) {
                final isOnline = ref.watch(syncStatusProvider).isOnline;
                if (!isOnline) {
                  return const SyncStatusBanner(dismissible: false);
                }
                return const SizedBox.shrink();
              },
            ),
            Expanded(child: child ?? const SizedBox()),
          ],
        );
      },
    );
  }
}
```

## Example 6: Background Sync Monitoring

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SyncMonitor extends ConsumerStatefulWidget {
  final Widget child;

  const SyncMonitor({super.key, required this.child});

  @override
  ConsumerState<SyncMonitor> createState() => _SyncMonitorState();
}

class _SyncMonitorState extends ConsumerState<SyncMonitor> {
  @override
  void initState() {
    super.initState();
    _listenToSyncStatus();
  }

  void _listenToSyncStatus() {
    // Listen to sync status changes
    ref.listenManual(syncStatusProvider, (previous, next) {
      // Auto-sync completed
      if (previous?.isSyncing == true && !next.isSyncing) {
        if (next.hasError) {
          // Show error
          FloatingSyncStatusBanner.showError(
            context,
            next.lastError ?? 'خطأ في المزامنة',
          );
        }
      }

      // Connection restored
      if (previous?.isOnline == false && next.isOnline) {
        FloatingSyncStatusBanner.show(
          context,
          message: 'تم استعادة الاتصال',
          backgroundColor: SahoolColors.success,
          icon: Icons.wifi,
          duration: const Duration(seconds: 2),
        );

        // Auto-trigger sync
        Future.delayed(const Duration(milliseconds: 500), () {
          ref.read(manualSyncTriggerProvider)();
        });
      }

      // Connection lost
      if (previous?.isOnline == true && !next.isOnline) {
        FloatingSyncStatusBanner.showOffline(context);
      }
    });

    // Listen to new conflicts
    ref.listenManual(unreadConflictsCountProvider, (previous, next) {
      if (next > (previous ?? 0)) {
        FloatingSyncStatusBanner.show(
          context,
          message: 'يوجد ${next} ${next == 1 ? 'تعارض' : 'تعارضات'} جديدة',
          backgroundColor: SahoolColors.warning,
          icon: Icons.warning_amber_rounded,
          onActionTap: () => context.push('/sync-details'),
          actionLabel: 'عرض',
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}

// Usage in main.dart
void main() {
  runApp(
    ProviderScope(
      child: SyncMonitor(
        child: MyApp(),
      ),
    ),
  );
}
```

## Tips & Best Practices

### 1. Choose the Right Style

- **AppBar**: Use `SyncIndicatorStyle.minimal` or `compact`
- **Dashboard**: Use `SyncIndicatorStyle.detailed`
- **List screens**: Use `SyncIndicatorStyle.expanded`
- **Status pages**: Use `SyncIndicatorStyle.detailed`

### 2. Banner Usage

- Use `SyncStatusBanner` for persistent states (offline mode)
- Use `FloatingSyncStatusBanner` for temporary notifications
- Use `AnimatedSyncStatusBanner` for smooth UX

### 3. Provider Access

```dart
// ✅ Good: Watch for UI updates
final syncStatus = ref.watch(syncStatusProvider);

// ✅ Good: Read for one-time operations
final triggerSync = ref.read(manualSyncTriggerProvider);

// ❌ Bad: Don't read in build method
final syncStatus = ref.read(syncStatusProvider); // Won't rebuild
```

### 4. Error Handling

Always provide retry actions:

```dart
FloatingSyncStatusBanner.showError(
  context,
  'فشل في المزامنة',
  onRetry: () => ref.read(manualSyncTriggerProvider)(),
);
```

### 5. Testing

Mock providers in tests:

```dart
testWidgets('Shows offline state', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        syncStatusProvider.overrideWith((ref) {
          return SyncStatusState(isOnline: false);
        }),
      ],
      child: MaterialApp(home: MyScreen()),
    ),
  );

  expect(find.text('غير متصل'), findsOneWidget);
});
```

---

**Last Updated**: 2025-12-30
