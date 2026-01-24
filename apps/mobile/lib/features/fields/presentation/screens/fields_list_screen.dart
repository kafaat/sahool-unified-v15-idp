import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/accessibility/semantics_helper.dart';
import '../../domain/entities/field_entity.dart';
import '../widgets/enhanced_field_card.dart';
import 'field_details_screen.dart';
import '../../../../core/widgets/loading_states.dart';
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

  // Mock data - في الإنتاج سيأتي من API
  final List<FieldEntity> _fields = [
    FieldEntity(
      id: '1',
      tenantId: 't1',
      name: 'حقل القمح الشمالي',
      areaHectares: 45.5,
      cropType: 'قمح',
      healthScore: 0.85,
      ndviValue: 0.72,
      ndwiValue: -0.05,
      soilType: 'طيني',
      irrigationType: 'محوري',
      plantingDate: DateTime.now().subtract(const Duration(days: 60)),
      expectedHarvest: DateTime.now().add(const Duration(days: 90)),
      status: FieldStatus.active,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    ),
    FieldEntity(
      id: '2',
      tenantId: 't1',
      name: 'حقل الذرة الغربي',
      areaHectares: 60.0,
      cropType: 'ذرة',
      healthScore: 0.72,
      ndviValue: 0.65,
      ndwiValue: -0.12,
      soilType: 'رملي',
      irrigationType: 'تنقيط',
      plantingDate: DateTime.now().subtract(const Duration(days: 45)),
      expectedHarvest: DateTime.now().add(const Duration(days: 75)),
      status: FieldStatus.active,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    ),
    FieldEntity(
      id: '3',
      tenantId: 't1',
      name: 'حقل الشعير',
      areaHectares: 35.0,
      cropType: 'شعير',
      healthScore: 0.45,
      ndviValue: 0.42,
      ndwiValue: -0.25,
      soilType: 'طيني',
      irrigationType: 'غمر',
      plantingDate: DateTime.now().subtract(const Duration(days: 90)),
      expectedHarvest: DateTime.now().add(const Duration(days: 30)),
      status: FieldStatus.active,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    ),
    FieldEntity(
      id: '4',
      tenantId: 't1',
      name: 'حقل البرسيم',
      areaHectares: 50.0,
      cropType: 'برسيم',
      healthScore: 0.92,
      ndviValue: 0.85,
      ndwiValue: 0.02,
      soilType: 'طيني رملي',
      irrigationType: 'محوري',
      status: FieldStatus.active,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    ),
    FieldEntity(
      id: '5',
      tenantId: 't1',
      name: 'حقل النخيل',
      areaHectares: 25.0,
      cropType: 'نخيل',
      healthScore: 0.78,
      ndviValue: 0.68,
      ndwiValue: -0.08,
      soilType: 'رملي',
      irrigationType: 'تنقيط',
      status: FieldStatus.active,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    ),
  ];

  List<FieldEntity> get _filteredFields {
    var fields = _fields.where((f) {
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
    // Simulate API call delay
    // في الإنتاج، استبدل هذا باستدعاء API حقيقي
    await Future.delayed(const Duration(milliseconds: 800));

    // In production, fetch from API:
    // final apiClient = ref.read(apiClientProvider);
    // final response = await apiClient.get('/fields');
    // final newFields = (response.data as List).map((f) => FieldEntity.fromJson(f)).toList();

    // For now, just refresh with updated timestamps
    setState(() {
      for (var i = 0; i < _fields.length; i++) {
        _fields[i] = _fields[i].copyWith(
          updatedAt: DateTime.now(),
        );
      }
    });

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
        body: Column(
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
            color: Colors.grey.withOpacity(0.1),
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
                prefixIcon: ExcludeSemantics(child: const Icon(Icons.search)),
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
        selectedColor: const Color(0xFF367C2B).withOpacity(0.2),
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

  void _openFieldDetails(FieldEntity field) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => FieldDetailsScreen(field: field),
      ),
    );
  }

  void _addField() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('إضافة حقل جديد - قريباً'),
        backgroundColor: Color(0xFF367C2B),
      ),
    );
  }

  Color _getHealthColor(double score) {
    if (score >= 0.7) return Colors.green;
    if (score >= 0.5) return Colors.orange;
    return Colors.red;
  }
}
