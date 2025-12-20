import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/field_entity.dart';
import '../widgets/enhanced_field_card.dart';
import 'field_details_screen.dart';

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

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('الحقول'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
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
          ],
        ),
        body: Column(
          children: [
            // Search and filters
            _buildSearchAndFilters(),

            // Stats bar
            _buildStatsBar(),

            // Fields list/grid
            Expanded(
              child: RefreshIndicator(
                onRefresh: () async {
                  // TODO: Refresh from API
                },
                child: _isGridView ? _buildGridView() : _buildListView(),
              ),
            ),
          ],
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
      selectedColor: const Color(0xFF367C2B).withOpacity(0.2),
      checkmarkColor: const Color(0xFF367C2B),
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

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: Colors.grey[50],
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem(
            icon: Icons.landscape,
            label: 'الحقول',
            value: '${_filteredFields.length}',
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

  Widget _buildListView() {
    if (_filteredFields.isEmpty) {
      return _buildEmptyState();
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _filteredFields.length,
      itemBuilder: (context, index) {
        final field = _filteredFields[index];
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: EnhancedFieldCard(
            field: field,
            onTap: () => _openFieldDetails(field),
          ),
        );
      },
    );
  }

  Widget _buildGridView() {
    if (_filteredFields.isEmpty) {
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
      itemCount: _filteredFields.length,
      itemBuilder: (context, index) {
        final field = _filteredFields[index];
        return EnhancedFieldCard(
          field: field,
          isCompact: true,
          onTap: () => _openFieldDetails(field),
        );
      },
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.landscape, size: 80, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            _searchQuery.isNotEmpty || _selectedCrop != null
                ? 'لا توجد نتائج'
                : 'لا توجد حقول',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'أضف حقلاً جديداً للبدء',
            style: TextStyle(color: Colors.grey[500]),
          ),
        ],
      ),
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
