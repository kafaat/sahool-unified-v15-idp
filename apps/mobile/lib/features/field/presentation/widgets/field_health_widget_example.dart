import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../domain/entities/field.dart';
import 'field_health_widget.dart';

/// Example usage of FieldHealthWidget
/// مثال على استخدام ويدجت صحة الحقل
///
/// This file demonstrates different ways to use the FieldHealthWidget
/// in your application.

// ============================================================================
// Example 1: In a Field Details Screen
// ============================================================================

class FieldDetailsScreenExample extends ConsumerWidget {
  final String fieldId;

  const FieldDetailsScreenExample({
    super.key,
    required this.fieldId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get field data from provider
    final fieldsState = ref.watch(fieldsStreamProvider('your-tenant-id'));

    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل الحقل / Field Details'),
      ),
      body: fieldsState.when(
        data: (fields) {
          final field = fields.firstWhere(
            (f) => f.id == fieldId,
            orElse: () => _createMockField(),
          );

          return SingleChildScrollView(
            child: Column(
              children: [
                const SizedBox(height: 16),

                // Full Health Widget
                FieldHealthWidget(field: field),

                const SizedBox(height: 16),

                // Other field information...
                _buildFieldInfo(context, field),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('Error: $error'),
        ),
      ),
    );
  }

  Widget _buildFieldInfo(BuildContext context, Field field) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: SahoolShadows.small,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'معلومات الحقل / Field Information',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 16),
          _buildInfoRow('الاسم / Name', field.name),
          _buildInfoRow('المحصول / Crop', field.cropType ?? 'غير محدد'),
          _buildInfoRow(
            'المساحة / Area',
            '${field.areaHectares.toStringAsFixed(2)} هكتار',
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}

// ============================================================================
// Example 2: In a Field List (Compact Mode)
// ============================================================================

class FieldListScreenExample extends ConsumerWidget {
  const FieldListScreenExample({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fieldsState = ref.watch(fieldsStreamProvider('your-tenant-id'));

    return Scaffold(
      appBar: AppBar(
        title: const Text('حقولي / My Fields'),
      ),
      body: fieldsState.when(
        data: (fields) {
          if (fields.isEmpty) {
            return const Center(
              child: Text('لا توجد حقول / No fields'),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: fields.length,
            itemBuilder: (context, index) {
              final field = fields[index];
              return Column(
                children: [
                  // Field Card with Compact Health Widget
                  Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: SahoolShadows.medium,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Field Header
                        Padding(
                          padding: const EdgeInsets.all(16),
                          child: Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: SahoolColors.primary.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(
                                  Icons.agriculture_rounded,
                                  color: SahoolColors.primary,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      field.name,
                                      style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    Text(
                                      field.cropType ?? 'غير محدد',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Icon(
                                Icons.chevron_left_rounded,
                                color: Colors.grey[400],
                              ),
                            ],
                          ),
                        ),

                        // Compact Health Widget
                        FieldHealthWidget(
                          field: field,
                          compact: true,
                        ),

                        const SizedBox(height: 8),
                      ],
                    ),
                  ),
                ],
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('Error: $error'),
        ),
      ),
    );
  }
}

// ============================================================================
// Example 3: In a Dashboard/Home Screen
// ============================================================================

class DashboardScreenExample extends ConsumerWidget {
  const DashboardScreenExample({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fieldsState = ref.watch(fieldsStreamProvider('your-tenant-id'));

    return Scaffold(
      appBar: AppBar(
        title: const Text('لوحة التحكم / Dashboard'),
      ),
      body: fieldsState.when(
        data: (fields) {
          // Get fields that need attention
          final fieldsNeedingAttention = fields.where((f) => f.needsAttention).toList();

          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 16),

                // Section: Fields Needing Attention
                if (fieldsNeedingAttention.isNotEmpty) ...[
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Row(
                      children: [
                        Icon(
                          Icons.warning_rounded,
                          color: SahoolColors.warning,
                          size: 24,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'حقول تحتاج انتباه / Fields Need Attention',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Horizontal Scroll of Field Health Widgets
                  SizedBox(
                    height: 200,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: fieldsNeedingAttention.length,
                      itemBuilder: (context, index) {
                        final field = fieldsNeedingAttention[index];
                        return SizedBox(
                          width: MediaQuery.of(context).size.width - 32,
                          child: FieldHealthWidget(field: field),
                        );
                      },
                    ),
                  ),

                  const SizedBox(height: 24),
                ],

                // Section: All Fields Overview
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Text(
                    'جميع الحقول / All Fields',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ),
                const SizedBox(height: 12),

                // Grid of Compact Health Widgets
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 1.5,
                    ),
                    itemCount: fields.length,
                    itemBuilder: (context, index) {
                      final field = fields[index];
                      return FieldHealthWidget(
                        field: field,
                        compact: true,
                      );
                    },
                  ),
                ),

                const SizedBox(height: 24),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('Error: $error'),
        ),
      ),
    );
  }
}

// ============================================================================
// Example 4: Standalone Usage with Mock Data
// ============================================================================

class StandaloneExample extends StatelessWidget {
  const StandaloneExample({super.key});

  @override
  Widget build(BuildContext context) {
    final mockField = _createMockField();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Health Widget Demo'),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 16),

            // Full Mode
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'Full Mode (Expandable)',
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
            FieldHealthWidget(field: mockField),

            const SizedBox(height: 32),

            // Compact Mode
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'Compact Mode',
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: FieldHealthWidget(
                field: mockField,
                compact: true,
              ),
            ),

            const SizedBox(height: 32),

            // Dark Mode Preview
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'Dark Mode Preview',
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
            Container(
              color: SahoolColors.backgroundDark,
              padding: const EdgeInsets.all(16),
              child: Theme(
                data: SahoolTheme.darkTheme,
                child: FieldHealthWidget(field: mockField),
              ),
            ),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

// ============================================================================
// Helper: Mock Data Provider (for testing/demo)
// ============================================================================

// Mock provider for fields stream (replace with actual provider in production)
final fieldsStreamProvider =
    StreamProvider.family<List<Field>, String>((ref, tenantId) {
  // Return mock data stream
  return Stream.value([
    _createMockField(
      id: '1',
      name: 'حقل القمح الشمالي',
      cropType: 'قمح',
      ndvi: 0.75,
      pendingTasks: 2,
    ),
    _createMockField(
      id: '2',
      name: 'حقل الذرة الجنوبي',
      cropType: 'ذرة',
      ndvi: 0.45,
      pendingTasks: 6,
    ),
    _createMockField(
      id: '3',
      name: 'حقل الخضروات',
      cropType: 'خضروات',
      ndvi: 0.35,
      pendingTasks: 8,
    ),
  ]);
});

Field _createMockField({
  String? id,
  String? name,
  String? cropType,
  double? ndvi,
  int? pendingTasks,
}) {
  return Field(
    id: id ?? 'mock-field-1',
    tenantId: 'mock-tenant',
    name: name ?? 'حقل تجريبي',
    cropType: cropType ?? 'قمح',
    areaHectares: 2.5,
    ndviCurrent: ndvi ?? 0.72,
    ndviUpdatedAt: DateTime.now().subtract(const Duration(days: 3)),
    pendingTasks: pendingTasks ?? 3,
    createdAt: DateTime.now().subtract(const Duration(days: 90)),
    updatedAt: DateTime.now(),
  );
}
