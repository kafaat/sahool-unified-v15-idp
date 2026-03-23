import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/accessibility/semantics_helper.dart';
import '../../../../core/di/providers.dart';
import '../../../../core/iam/iam_providers.dart';
import '../../domain/entities/field_entity.dart';
import '../widgets/enhanced_field_card.dart';
import 'field_details_screen.dart';
import '../../../../core/widgets/loading_states.dart';
import '../../../../core/widgets/domain_skeletons.dart';
import '../../../../core/widgets/sahool_skeleton.dart';
import '../../../../core/widgets/empty_states.dart';

/// شاشة قائمة الحقول
/// Fields List Screen with Accessibility Support
///
/// Accessibility Features:
/// - Semantic labels for all interactive elements
/// - Screen reader announcements for list updates
/// - Proper heading hierarchy
/// - Focus management for keyboard navigation
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

  List<FieldEntity> _fields = [];
  bool _isLoading = true;
  String? _loadError;

  @override
  void initState() {
    super.initState();
    _loadFields();
  }

  Future<void> _loadFields() async {
    setState(() {
      _isLoading = true;
      _loadError = null;
    });

    try {
      final tenant = ref.read(currentTenantProvider);
      final tenantId = tenant?.id ?? 'default';
      final repo = ref.read(fieldsRepoProvider);
      final domainFields = await repo.getAllFields(tenantId);

      // Map domain Field entities to FieldEntity for the UI
      final now = DateTime.now();
      setState(() {
        _fields = domainFields.map((f) {
          final ndvi = f.ndviCurrent ?? 0.0;
          double healthScore;
          if (ndvi >= 0.6) {
            healthScore = 0.8 + (ndvi - 0.6) * 0.5;
          } else if (ndvi >= 0.4) {
            healthScore = 0.5 + (ndvi - 0.4) * 1.5;
          } else if (ndvi > 0) {
            healthScore = ndvi;
          } else {
            healthScore = 0.0;
          }

          return FieldEntity(
            id: f.id,
            tenantId: f.tenantId,
            name: f.name,
            farmId: f.farmId,
            areaHectares: f.areaHectares,
            cropType: f.cropType ?? 'غير محدد',
            healthScore: healthScore.clamp(0.0, 1.0),
            ndviValue: f.ndviCurrent,
            soilType: null,
            irrigationType: null,
            status: FieldStatus.active,
            createdAt: f.createdAt,
            updatedAt: f.updatedAt,
          );
        }).toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _loadError = 'فشل تحميل الحقول: $e';
      });
    }
  }

  List<FieldEntity> get _filteredFields {
    final fields = _fields.where((f) {
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
        fields.sort((a, b) => a.name.compareTo(b.name));
        break;
      case 'area':
        fields.sort((a, b) => b.areaHectares.compareTo(a.areaHectares));
        break;
      case 'health':
        fields.sort((a, b) => b.healthScore.compareTo(a.healthScore));
        break;
    }

    return fields;
  }

  /// Refresh fields from API
  /// تحديث الحقول من الخادم
  Future<void> _refreshFields() async {
    try {
      final tenant = ref.read(currentTenantProvider);
      final tenantId = tenant?.id ?? 'default';
      final repo = ref.read(fieldsRepoProvider);

      // Try to refresh from server first
      try {
        await repo.refreshFromServer(tenantId);
      } catch (_) {
        // If server refresh fails (offline), just reload from local DB
      }

      // Reload from local DB
      await _loadFields();

      // Show refresh confirmation
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
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Semantics(
            header: true,
            child: const Text('الحقول'),
          ),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            // Toggle view with accessibility
            Semantics(
              label: _isGridView ? SahoolSemantics.listViewButton : SahoolSemantics.gridViewButton,
              button: true,
              child: IconButton(
                icon: Icon(_isGridView ? Icons.list : Icons.grid_view),
                onPressed: () {
                  setState(() => _isGridView = !_isGridView);
                  // Announce view change to screen readers
                  AnnouncementHelper.announce(
                    context,
                    _isGridView ? 'تم التبديل إلى عرض الشبكة' : 'تم التبديل إلى عرض القائمة',
                  );
                },
                tooltip: _isGridView ? 'عرض قائمة' : 'عرض شبكة',
              ),
            ),
            // Sort with accessibility
            Semantics(
              label: SahoolSemantics.sortButton,
              button: true,
              child: PopupMenuButton<String>(
                icon: const Icon(Icons.sort),
                tooltip: 'ترتيب',
                onSelected: (value) {
                  setState(() => _sortBy = value);
                  // Announce sort change
                  String sortLabel;
                  switch (value) {
                    case 'name':
                      sortLabel = 'الاسم';
                      break;
                    case 'area':
                      sortLabel = 'المساحة';
                      break;
                    case 'health':
                      sortLabel = 'الصحة';
                      break;
                    default:
                      sortLabel = value;
                  }
                  AnnouncementHelper.announce(context, 'تم الترتيب حسب $sortLabel');
                },
                itemBuilder: (context) => [
                  PopupMenuItem(
                    value: 'name',
                    child: Row(
                      children: [
                        Icon(Icons.sort_by_alpha,
                            color: _sortBy == 'name' ? const Color(0xFF367C2B) : null),
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
                            color: _sortBy == 'area' ? const Color(0xFF367C2B) : null),
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
                            color: _sortBy == 'health' ? const Color(0xFF367C2B) : null),
                        const SizedBox(width: 8),
                        const Text('الصحة'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        body: _isLoading
            ? SahoolSkeletonList(
                itemCount: 5,
                padding: const EdgeInsets.all(16),
                itemBuilder: (_) => const FieldCardSkeleton(),
              )
            : _loadError != null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.error_outline, size: 48, color: Colors.grey[400]),
                        const SizedBox(height: 16),
                        Text(_loadError!, style: TextStyle(color: Colors.grey[600])),
                        const SizedBox(height: 16),
                        ElevatedButton.icon(
                          onPressed: _loadFields,
                          icon: const Icon(Icons.refresh),
                          label: const Text('إعادة المحاولة'),
                        ),
                      ],
                    ),
                  )
                : Column(
                    children: [
                      // Search and filters
                      _buildSearchAndFilters(),

                      // Stats bar with live region for dynamic updates
                      Semantics(
                        liveRegion: true,
                        child: _buildStatsBar(),
                      ),

                      // Fields list/grid
                      Expanded(
                        child: SahoolRefreshIndicator(
                          onRefresh: _refreshFields,
                          child: _isGridView ? _buildGridView() : _buildListView(),
                        ),
                      ),
                    ],
                  ),
        floatingActionButton: Semantics(
          label: SahoolSemantics.addFieldButton,
          button: true,
          child: FloatingActionButton.extended(
            onPressed: _addField,
            backgroundColor: const Color(0xFF367C2B),
            icon: const Icon(Icons.add),
            label: const Text('حقل جديد'),
          ),
        ),
      ),
    );
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
          // Search with accessibility
          Semantics(
            label: SahoolSemantics.searchField,
            textField: true,
            child: TextField(
              decoration: InputDecoration(
                hintText: 'ابحث عن حقل...',
                prefixIcon: const ExcludeSemantics(child: Icon(Icons.search)),
                suffixIcon: _searchQuery.isNotEmpty
                    ? Semantics(
                        label: SahoolSemantics.clearFilter,
                        button: true,
                        child: IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            setState(() => _searchQuery = '');
                            AnnouncementHelper.announce(context, 'تم مسح البحث');
                          },
                          tooltip: 'مسح البحث',
                        ),
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Colors.grey[100],
              ),
              onChanged: (value) {
                setState(() => _searchQuery = value);
                // Announce search results count after debounce
                if (value.length > 2) {
                  AnnouncementHelper.announceListUpdate(
                    context,
                    _filteredFields.length,
                    'حقل',
                  );
                }
              },
            ),
          ),

          const SizedBox(height: 12),

          // Filter chips with accessibility
          Semantics(
            label: 'فلترة حسب نوع المحصول',
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildFilterChip(
                    label: 'الكل',
                    semanticLabel: 'عرض كل الحقول',
                    selected: _selectedCrop == null,
                    onSelected: (_) {
                      setState(() => _selectedCrop = null);
                      AnnouncementHelper.announce(context, 'عرض كل الحقول');
                    },
                  ),
                  const SizedBox(width: 8),
                  _buildFilterChip(
                    label: 'قمح',
                    semanticLabel: 'فلترة حسب القمح',
                    selected: _selectedCrop == 'قمح',
                    onSelected: (_) {
                      setState(() => _selectedCrop = 'قمح');
                      AnnouncementHelper.announce(context, 'فلترة حسب القمح');
                    },
                  ),
                  const SizedBox(width: 8),
                  _buildFilterChip(
                    label: 'ذرة',
                    semanticLabel: 'فلترة حسب الذرة',
                    selected: _selectedCrop == 'ذرة',
                    onSelected: (_) {
                      setState(() => _selectedCrop = 'ذرة');
                      AnnouncementHelper.announce(context, 'فلترة حسب الذرة');
                    },
                  ),
                  const SizedBox(width: 8),
                  _buildFilterChip(
                    label: 'برسيم',
                    semanticLabel: 'فلترة حسب البرسيم',
                    selected: _selectedCrop == 'برسيم',
                    onSelected: (_) {
                      setState(() => _selectedCrop = 'برسيم');
                      AnnouncementHelper.announce(context, 'فلترة حسب البرسيم');
                    },
                  ),
                  const SizedBox(width: 8),
                  _buildFilterChip(
                    label: 'نخيل',
                    semanticLabel: 'فلترة حسب النخيل',
                    selected: _selectedCrop == 'نخيل',
                    onSelected: (_) {
                      setState(() => _selectedCrop = 'نخيل');
                      AnnouncementHelper.announce(context, 'فلترة حسب النخيل');
                    },
                  ),
                ],
              ),
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
    String? semanticLabel,
  }) {
    return Semantics(
      label: semanticLabel ?? label,
      selected: selected,
      button: true,
      child: FilterChip(
        label: Text(label),
        selected: selected,
        onSelected: onSelected,
        selectedColor: const Color(0xFF367C2B).withValues(alpha: 0.2),
        checkmarkColor: const Color(0xFF367C2B),
      ),
    );
  }

  Widget _buildStatsBar() {
    final totalArea = _filteredFields.fold<double>(
      0,
      (sum, f) => sum + f.areaHectares,
    );
    final avgHealth = _filteredFields.isEmpty
        ? 0.0
        : _filteredFields.fold<double>(0, (sum, f) => sum + f.healthScore) /
            _filteredFields.length;

    final healthLabel = SahoolSemantics.getHealthLabel(avgHealth);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: Colors.grey[50],
      child: MergeSemantics(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildStatItem(
              icon: Icons.landscape,
              label: 'الحقول',
              value: '${_filteredFields.length}',
              semanticLabel: '${_filteredFields.length} حقل معروض',
            ),
            _buildStatItem(
              icon: Icons.square_foot,
              label: 'المساحة',
              value: '${totalArea.toStringAsFixed(0)} هـ',
              semanticLabel: 'إجمالي المساحة ${totalArea.toStringAsFixed(0)} هكتار',
            ),
            _buildStatItem(
              icon: Icons.favorite,
              label: 'متوسط الصحة',
              value: '${(avgHealth * 100).round()}%',
              valueColor: _getHealthColor(avgHealth),
              semanticLabel: 'متوسط صحة الحقول ${(avgHealth * 100).round()}%، $healthLabel',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String label,
    required String value,
    Color? valueColor,
    String? semanticLabel,
  }) {
    return Semantics(
      label: semanticLabel ?? '$label: $value',
      child: Column(
        children: [
          ExcludeSemantics(
            child: Icon(icon, color: const Color(0xFF367C2B), size: 20),
          ),
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
      ),
    );
  }

  Widget _buildListView() {
    if (_filteredFields.isEmpty) {
      return _buildEmptyState();
    }

    return Semantics(
      label: 'قائمة الحقول، ${_filteredFields.length} حقل',
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _filteredFields.length,
        itemBuilder: (context, index) {
          final field = _filteredFields[index];
          final healthLabel = SahoolSemantics.getHealthLabel(field.healthScore);
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Semantics(
              label: '${field.name}، ${field.cropType}، ${field.areaHectares.toStringAsFixed(1)} هكتار، $healthLabel',
              hint: 'اضغط لعرض تفاصيل الحقل',
              button: true,
              child: EnhancedFieldCard(
                field: field,
                onTap: () => _openFieldDetails(field),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildGridView() {
    if (_filteredFields.isEmpty) {
      return _buildEmptyState();
    }

    return Semantics(
      label: 'شبكة الحقول، ${_filteredFields.length} حقل',
      child: GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 0.85,
        ),
        itemCount: _filteredFields.length,
        itemBuilder: (context, index) {
          final field = _filteredFields[index];
          final healthLabel = SahoolSemantics.getHealthLabel(field.healthScore);
          return Semantics(
            label: '${field.name}، ${field.cropType}، $healthLabel',
            hint: 'اضغط لعرض تفاصيل الحقل',
            button: true,
            child: EnhancedFieldCard(
              field: field,
              isCompact: true,
              onTap: () => _openFieldDetails(field),
            ),
          );
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    // Show search results empty state if searching
    if (_searchQuery.isNotEmpty || _selectedCrop != null) {
      return NoSearchResultsEmptyState(
        searchQuery: _searchQuery.isNotEmpty ? _searchQuery : _selectedCrop,
        onClear: () => setState(() {
          _searchQuery = '';
          _selectedCrop = null;
        }),
      );
    }

    // Show no fields empty state
    return NoFieldsEmptyState(
      onAddField: _addField,
    );
  }

  Future<void> _openFieldDetails(FieldEntity field) async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => FieldDetailsScreen(field: field),
      ),
    );
    // Reload fields if a field was deleted or modified
    if (result == 'deleted' && mounted) {
      unawaited(_loadFields());
    }
  }

  Future<void> _addField() async {
    final result = await Navigator.pushNamed(context, '/field-form');
    // Reload fields if a field was created
    if (result == true && mounted) {
      unawaited(_loadFields());
    }
  }

  Color _getHealthColor(double score) {
    if (score >= 0.7) return Colors.green;
    if (score >= 0.5) return Colors.orange;
    return Colors.red;
  }
}
