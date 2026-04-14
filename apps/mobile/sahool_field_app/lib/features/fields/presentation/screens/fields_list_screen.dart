import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/config/env_config.dart';
import '../../../../core/widgets/error_boundary.dart';
import '../../../../core/widgets/empty_states.dart';
import '../../../../core/widgets/shimmer_skeletons.dart';
import '../../../field/domain/mappers/field_mapper.dart';
import '../../../field/presentation/providers/field_controller.dart';
import '../../domain/entities/field_entity.dart';
import '../widgets/enhanced_field_card.dart';

/// شاشة قائمة الحقول
/// Fields List Screen
class FieldsListScreen extends ConsumerStatefulWidget {
  const FieldsListScreen({super.key});

  @override
  ConsumerState<FieldsListScreen> createState() => _FieldsListScreenState();
}

class _FieldsListScreenState extends ConsumerState<FieldsListScreen> {
  String _searchQuery = '';
  String? _selectedCrop;
  FieldStatus? _selectedStatus;
  String _sortBy = 'name';
  bool _isGridView = false;

  /// Get current tenant ID
  String get _tenantId => EnvConfig.defaultTenantId;

  /// Get filtered and sorted fields
  List<FieldEntity> _getFilteredFields(List<FieldEntity> fields) {
    final filteredFields = fields.where((f) {
      if (_searchQuery.isNotEmpty &&
          !f.name.toLowerCase().contains(_searchQuery.toLowerCase())) {
        return false;
      }
      if (_selectedCrop != null && f.cropType != _selectedCrop) {
        return false;
      }
      if (_selectedStatus != null && f.status != _selectedStatus) {
        return false;
      }
      return true;
    }).toList();

    // Sort
    switch (_sortBy) {
      case 'name':
        filteredFields.sort((a, b) => a.name.compareTo(b.name));
        break;
      case 'area':
        filteredFields.sort((a, b) => b.areaHectares.compareTo(a.areaHectares));
        break;
      case 'health':
        filteredFields.sort((a, b) => b.healthScore.compareTo(a.healthScore));
        break;
    }

    return filteredFields;
  }

  /// Refresh fields from server
  /// تحديث الحقول من الخادم
  Future<void> _refreshFields() async {
    final controller = ref.read(fieldControllerProvider(_tenantId).notifier);

    try {
      await controller.refreshFromServer();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم تحديث البيانات'),
            duration: Duration(seconds: 1),
            backgroundColor: Color(0xFF367C2B),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل التحديث: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Watch the field controller state
    final controllerState = ref.watch(fieldControllerProvider(_tenantId));

    // Convert domain fields to FieldEntity for UI display
    final fieldEntities = controllerState.fields.toFieldEntities();
    final filteredFields = _getFilteredFields(fieldEntities);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('الحقول'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            // Sync indicator
            if (controllerState.unsyncedCount > 0)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: Chip(
                  label: Text(
                    '${controllerState.unsyncedCount}',
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                  ),
                  backgroundColor: Colors.orange,
                  avatar: const Icon(Icons.cloud_off,
                      color: Colors.white, size: 16),
                ),
              ),
            // Toggle view
            IconButton(
              icon: Icon(_isGridView ? Icons.list : Icons.grid_view),
              onPressed: () => setState(() => _isGridView = !_isGridView),
              tooltip: _isGridView ? 'عرض قائمة' : 'عرض شبكة',
            ),
            // Sort
            PopupMenuButton<String>(
              icon: const Icon(Icons.sort),
              tooltip: 'ترتيب',
              onSelected: (value) => setState(() => _sortBy = value),
              itemBuilder: (context) => [
                PopupMenuItem(
                  value: 'name',
                  child: Row(
                    children: [
                      Icon(Icons.sort_by_alpha,
                          color: _sortBy == 'name'
                              ? const Color(0xFF367C2B)
                              : null),
                      const SizedBox(width: 8),
                      const Text('الاسم'),
                    ],
                  ),
                ),
                PopupMenuItem(
                  value: 'area',
                  child: Row(
                    children: [
                      Icon(Icons.square_foot,
                          color: _sortBy == 'area'
                              ? const Color(0xFF367C2B)
                              : null),
                      const SizedBox(width: 8),
                      const Text('المساحة'),
                    ],
                  ),
                ),
                PopupMenuItem(
                  value: 'health',
                  child: Row(
                    children: [
                      Icon(Icons.favorite,
                          color: _sortBy == 'health'
                              ? const Color(0xFF367C2B)
                              : null),
                      const SizedBox(width: 8),
                      const Text('الصحة'),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
        body: SahoolErrorBoundary(
          onError: (error, stackTrace) {
            debugPrint('FieldsListScreen error: $error');
          },
          child: Column(
            children: [
              // Error banner with dismissible action
              if (controllerState.error != null)
                MaterialBanner(
                  content: Text(controllerState.error!),
                  backgroundColor: Colors.red.shade100,
                  leading: const Icon(Icons.error_outline, color: Colors.red),
                  actions: [
                    TextButton(
                      onPressed: () => ref
                          .read(fieldControllerProvider(_tenantId).notifier)
                          .clearError(),
                      child: const Text('إغلاق'),
                    ),
                    TextButton(
                      onPressed: () {
                        ref
                            .read(fieldControllerProvider(_tenantId).notifier)
                            .clearError();
                        ref
                            .read(fieldControllerProvider(_tenantId).notifier)
                            .loadFields();
                      },
                      child: const Text('إعادة المحاولة'),
                    ),
                  ],
                ),

              // Search and filters
              _buildSearchAndFilters(),

              // Stats bar (show skeleton during initial load)
              controllerState.isLoading && fieldEntities.isEmpty
                  ? const StatsBarSkeleton()
                  : _buildStatsBar(filteredFields),

              // Refresh progress indicator (only during refresh, not initial load)
              if (controllerState.isRefreshing)
                const LinearProgressIndicator(
                  backgroundColor: Color(0xFFE8F5E9),
                  valueColor: AlwaysStoppedAnimation(Color(0xFF367C2B)),
                ),

              // Fields list/grid
              Expanded(
                child: RefreshIndicator(
                  onRefresh: _refreshFields,
                  color: const Color(0xFF367C2B),
                  child: controllerState.isLoading && fieldEntities.isEmpty
                      ? _buildLoadingState()
                      : _isGridView
                          ? _buildGridView(filteredFields)
                          : _buildListView(filteredFields),
                ),
              ),
            ],
          ),
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _addField,
          backgroundColor: const Color(0xFF367C2B),
          icon: const Icon(Icons.add),
          label: const Text('حقل جديد'),
        ),
      ),
    );
  }

  Widget _buildLoadingState() {
    return FieldsListSkeleton(isGridView: _isGridView);
  }

  Widget _buildSearchAndFilters() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withValues(alpha: 0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // Search
          TextField(
            decoration: InputDecoration(
              hintText: 'ابحث عن حقل...',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () => setState(() => _searchQuery = ''),
                    )
                  : null,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              filled: true,
              fillColor: Colors.grey[100],
            ),
            onChanged: (value) => setState(() => _searchQuery = value),
          ),

          const SizedBox(height: 12),

          // Filter chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildFilterChip(
                  label: 'الكل',
                  selected: _selectedCrop == null,
                  onSelected: (_) => setState(() => _selectedCrop = null),
                ),
                const SizedBox(width: 8),
                _buildFilterChip(
                  label: '🌾 قمح',
                  selected: _selectedCrop == 'قمح',
                  onSelected: (_) => setState(() => _selectedCrop = 'قمح'),
                ),
                const SizedBox(width: 8),
                _buildFilterChip(
                  label: '🌽 ذرة',
                  selected: _selectedCrop == 'ذرة',
                  onSelected: (_) => setState(() => _selectedCrop = 'ذرة'),
                ),
                const SizedBox(width: 8),
                _buildFilterChip(
                  label: '🌿 برسيم',
                  selected: _selectedCrop == 'برسيم',
                  onSelected: (_) => setState(() => _selectedCrop = 'برسيم'),
                ),
                const SizedBox(width: 8),
                _buildFilterChip(
                  label: '🌴 نخيل',
                  selected: _selectedCrop == 'نخيل',
                  onSelected: (_) => setState(() => _selectedCrop = 'نخيل'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip({
    required String label,
    required bool selected,
    required ValueChanged<bool> onSelected,
  }) {
    return FilterChip(
      label: Text(label),
      selected: selected,
      onSelected: onSelected,
      selectedColor: const Color(0xFF367C2B).withValues(alpha: 0.2),
      checkmarkColor: const Color(0xFF367C2B),
    );
  }

  Widget _buildStatsBar(List<FieldEntity> fields) {
    final totalArea = fields.fold<double>(
      0,
      (sum, f) => sum + f.areaHectares,
    );
    final avgHealth = fields.isEmpty
        ? 0.0
        : fields.fold<double>(0, (sum, f) => sum + f.healthScore) /
            fields.length;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: Colors.grey[50],
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem(
            icon: Icons.landscape,
            label: 'الحقول',
            value: '${fields.length}',
          ),
          _buildStatItem(
            icon: Icons.square_foot,
            label: 'المساحة',
            value: '${totalArea.toStringAsFixed(0)} هـ',
          ),
          _buildStatItem(
            icon: Icons.favorite,
            label: 'متوسط الصحة',
            value: '${(avgHealth * 100).round()}%',
            valueColor: _getHealthColor(avgHealth),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String label,
    required String value,
    Color? valueColor,
  }) {
    return Column(
      children: [
        Icon(icon, color: const Color(0xFF367C2B), size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
            color: valueColor ?? Colors.black,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildListView(List<FieldEntity> fields) {
    if (fields.isEmpty) {
      return _buildEmptyState();
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: fields.length,
      itemBuilder: (context, index) {
        final field = fields[index];
        return RepaintBoundary(
          key: ValueKey('field_${field.id}'),
          child: Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: EnhancedFieldCard(
              field: field,
              onTap: () => _openFieldDetails(field),
            ),
          ),
        );
      },
    );
  }

  Widget _buildGridView(List<FieldEntity> fields) {
    if (fields.isEmpty) {
      return _buildEmptyState();
    }

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 0.85,
      ),
      itemCount: fields.length,
      itemBuilder: (context, index) {
        final field = fields[index];
        return RepaintBoundary(
          key: ValueKey('field_grid_${field.id}'),
          child: EnhancedFieldCard(
            field: field,
            isCompact: true,
            onTap: () => _openFieldDetails(field),
          ),
        );
      },
    );
  }

  Widget _buildEmptyState() {
    // Show search-specific empty state when filters are active
    if (_searchQuery.isNotEmpty || _selectedCrop != null) {
      return NoSearchResultsEmptyState(
        searchQuery: _searchQuery.isNotEmpty ? _searchQuery : _selectedCrop,
        onClear: () => setState(() {
          _searchQuery = '';
          _selectedCrop = null;
        }),
      );
    }

    // Show fields-specific empty state
    return NoFieldsEmptyState(onAddField: _addField);
  }

  void _openFieldDetails(FieldEntity field) {
    // Navigate to field details using GoRouter with field ID
    context.push('/field/${field.id}', extra: field);
  }

  void _addField() {
    // Navigate to dedicated field creation form
    context.push('/fields/create', extra: {'tenantId': _tenantId}).then((_) {
      // Refresh fields after returning from form
      ref.read(fieldControllerProvider(_tenantId).notifier).loadFields();
    });
  }

  Color _getHealthColor(double score) {
    if (score >= 0.7) return Colors.green;
    if (score >= 0.5) return Colors.orange;
    return Colors.red;
  }
}
