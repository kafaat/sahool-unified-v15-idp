import 'package:flutter/material.dart';
import '../widgets.dart';

/// SAHOOL Widget Showcase
/// عرض توضيحي لجميع المكونات المتاحة
///
/// This file demonstrates usage of all SAHOOL UI components
/// for error handling, loading states, and empty states

// ═══════════════════════════════════════════════════════════════════════════
// Error Handling Examples
// ═══════════════════════════════════════════════════════════════════════════

class ErrorBoundaryExample extends StatelessWidget {
  const ErrorBoundaryExample({super.key});

  @override
  Widget build(BuildContext context) {
    return SahoolErrorBoundary(
      child: const MyRiskyWidget(),
      onError: (error, stackTrace) {
        // Log error to analytics
        debugPrint('Error caught: $error');
      },
      errorBuilder: (error, retry) {
        return SahoolTypedErrorView(
          error: error,
          onRetry: retry,
          showDetails: false,
        );
      },
    );
  }
}

class MyRiskyWidget extends StatelessWidget {
  const MyRiskyWidget({super.key});

  @override
  Widget build(BuildContext context) {
    // Widget that might throw errors
    return const Center(child: Text('محتوى التطبيق'));
  }
}

class ErrorViewExample extends StatelessWidget {
  const ErrorViewExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('مثال على عرض الأخطاء')),
      body: SahoolErrorView(
        error: Exception('Network error occurred'),
        onRetry: () {
          // Retry logic here
          debugPrint('إعادة المحاولة...');
        },
      ),
    );
  }
}

class InlineErrorExample extends StatelessWidget {
  const InlineErrorExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const Text('بعض المحتوى'),
          const SizedBox(height: 16),
          SahoolInlineError(
            message: 'فشل تحميل البيانات',
            onRetry: () {
              debugPrint('إعادة تحميل البيانات');
            },
          ),
        ],
      ),
    );
  }
}

class NetworkErrorExample extends StatelessWidget {
  const NetworkErrorExample({super.key});

  @override
  Widget build(BuildContext context) {
    return SahoolNetworkError(
      onRetry: () {
        debugPrint('محاولة إعادة الاتصال');
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Loading States Examples
// ═══════════════════════════════════════════════════════════════════════════

class ShimmerExample extends StatelessWidget {
  const ShimmerExample({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: const [
        // Shimmer cards
        SahoolShimmerCard(height: 120),
        SizedBox(height: 16),
        SahoolShimmerCard(height: 200),
        SizedBox(height: 16),

        // Shimmer list
        SahoolShimmerList(itemCount: 3),
      ],
    );
  }
}

class LoadingOverlayExample extends StatefulWidget {
  const LoadingOverlayExample({super.key});

  @override
  State<LoadingOverlayExample> createState() => _LoadingOverlayExampleState();
}

class _LoadingOverlayExampleState extends State<LoadingOverlayExample> {
  bool _isLoading = false;

  Future<void> _performAction() async {
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 2));
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('مثال على التحميل')),
      body: SahoolLoadingOverlay(
        isLoading: _isLoading,
        message: 'جاري التحميل...',
        child: Center(
          child: ElevatedButton(
            onPressed: _performAction,
            child: const Text('بدء العملية'),
          ),
        ),
      ),
    );
  }
}

class LoadingButtonExample extends StatefulWidget {
  const LoadingButtonExample({super.key});

  @override
  State<LoadingButtonExample> createState() => _LoadingButtonExampleState();
}

class _LoadingButtonExampleState extends State<LoadingButtonExample> {
  bool _isLoading = false;

  Future<void> _submit() async {
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 2));
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SahoolLoadingButton(
        onPressed: _submit,
        isLoading: _isLoading,
        child: const Text('حفظ'),
      ),
    );
  }
}

class SkeletonLoadingExample extends StatelessWidget {
  const SkeletonLoadingExample({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: const [
        // Profile skeleton
        SahoolProfileHeaderSkeleton(),

        Divider(),

        // List item skeletons
        SahoolListItemSkeleton(),
        SahoolListItemSkeleton(),
        SahoolListItemSkeleton(),

        Divider(),

        // Field card skeleton
        SahoolFieldCardSkeleton(),
      ],
    );
  }
}

class AsyncBuilderExample extends StatelessWidget {
  const AsyncBuilderExample({super.key});

  Future<String> _fetchData() async {
    await Future.delayed(const Duration(seconds: 2));
    return 'البيانات المحملة';
  }

  @override
  Widget build(BuildContext context) {
    return SahoolAsyncBuilder<String>(
      future: _fetchData(),
      builder: (data) {
        return Center(child: Text(data));
      },
      loadingWidget: const SahoolLoadingScreen(
        message: 'جاري تحميل البيانات...',
      ),
      errorBuilder: (error) {
        return SahoolErrorView(
          error: error,
          onRetry: () {
            // Retry logic
          },
        );
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Empty States Examples
// ═══════════════════════════════════════════════════════════════════════════

class EmptyStateExample extends StatelessWidget {
  const EmptyStateExample({super.key});

  @override
  Widget build(BuildContext context) {
    return SahoolEmptyState(
      icon: Icons.inbox_rounded,
      title: 'لا توجد عناصر',
      message: 'لم يتم العثور على أي عناصر لعرضها',
      actionLabel: 'إضافة عنصر',
      onAction: () {
        debugPrint('إضافة عنصر جديد');
      },
    );
  }
}

class PredefinedEmptyStatesExample extends StatelessWidget {
  const PredefinedEmptyStatesExample({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        // No Fields
        SizedBox(
          height: 300,
          child: NoFieldsEmptyState(
            onAddField: () => debugPrint('إضافة حقل'),
          ),
        ),
        const Divider(),

        // No Tasks
        SizedBox(
          height: 300,
          child: NoTasksEmptyState(
            onAddTask: () => debugPrint('إضافة مهمة'),
          ),
        ),
        const Divider(),

        // No Data
        SizedBox(
          height: 300,
          child: NoDataEmptyState(
            onRefresh: () => debugPrint('تحديث البيانات'),
          ),
        ),
        const Divider(),

        // No Connection
        SizedBox(
          height: 300,
          child: NoConnectionEmptyState(
            onRetry: () => debugPrint('إعادة الاتصال'),
          ),
        ),
        const Divider(),

        // No Search Results
        const SizedBox(
          height: 300,
          child: NoSearchResultsEmptyState(
            searchQuery: 'محصول',
          ),
        ),
      ],
    );
  }
}

class CompactEmptyStateExample extends StatelessWidget {
  const CompactEmptyStateExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: SahoolCompactEmptyState(
        icon: Icons.description_outlined,
        message: 'لا توجد مستندات',
        actionLabel: 'إضافة',
        onAction: () => debugPrint('إضافة مستند'),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Complete Screen Examples
// ═══════════════════════════════════════════════════════════════════════════

class FieldListScreen extends StatefulWidget {
  const FieldListScreen({super.key});

  @override
  State<FieldListScreen> createState() => _FieldListScreenState();
}

class _FieldListScreenState extends State<FieldListScreen> {
  bool _isLoading = true;
  bool _hasError = false;
  List<String> _fields = [];

  @override
  void initState() {
    super.initState();
    _loadFields();
  }

  Future<void> _loadFields() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
    });

    try {
      await Future.delayed(const Duration(seconds: 2));
      // Simulate loading
      setState(() {
        _fields = []; // Empty list for demonstration
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _hasError = true;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الحقول')),
      body: SahoolRefreshIndicator(
        onRefresh: _loadFields,
        child: _buildBody(),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          debugPrint('إضافة حقل جديد');
        },
        icon: const Icon(Icons.add),
        label: const Text('إضافة حقل'),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return ListView(
        children: const [
          SahoolFieldCardSkeleton(),
          SahoolFieldCardSkeleton(),
          SahoolFieldCardSkeleton(),
        ],
      );
    }

    if (_hasError) {
      return SahoolNetworkError(
        onRetry: _loadFields,
      );
    }

    if (_fields.isEmpty) {
      return NoFieldsEmptyState(
        onAddField: () {
          debugPrint('إضافة أول حقل');
        },
      );
    }

    return ListView.builder(
      itemCount: _fields.length,
      itemBuilder: (context, index) {
        return ListTile(
          title: Text(_fields[index]),
        );
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// RTL Support Example
// ═══════════════════════════════════════════════════════════════════════════

class RTLSupportExample extends StatelessWidget {
  const RTLSupportExample({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      // RTL configuration for Arabic
      locale: const Locale('ar', 'SA'),
      supportedLocales: const [
        Locale('ar', 'SA'),
        Locale('en', 'US'),
      ],
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: child ?? const SizedBox(),
        );
      },
      home: Scaffold(
        appBar: AppBar(title: const Text('دعم اللغة العربية')),
        body: SahoolRTLEmptyState(
          child: NoFieldsEmptyState(
            onAddField: () => debugPrint('إضافة حقل'),
          ),
        ),
      ),
    );
  }
}
