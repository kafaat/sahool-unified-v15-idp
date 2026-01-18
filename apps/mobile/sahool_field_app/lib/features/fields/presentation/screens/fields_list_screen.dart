import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/auth/auth_service.dart';
import '../../../../core/di/providers.dart';
import '../../../field/domain/entities/field.dart';
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
  bool _isRefreshing = false;

  /// Map domain Field entity to FieldEntity for UI
  /// تحويل كيان الحقل من المستودع إلى كيان العرض
  FieldEntity _mapDomainToUiEntity(Field field) {
    // Calculate health score from NDVI value
    final healthScore = field.ndviCurrent ?? 0.0;

    // Map domain status string to UI FieldStatus enum
    FieldStatus status;
    switch (field.status?.toLowerCase()) {
      case 'fallow':
        status = FieldStatus.fallow;
        break;
      case 'preparing':
        status = FieldStatus.preparing;
        break;
      case 'harvested':
        status = FieldStatus.harvested;
        break;
      case 'inactive':
        status = FieldStatus.inactive;
        break;
      default:
        status = FieldStatus.active;
    }

    return FieldEntity(
      id: field.id,
      tenantId: field.tenantId,
      name: field.name,
      farmId: field.farmId,
      areaHectares: field.areaHectares,
      cropType: field.cropType ?? 'غير محدد',
      healthScore: healthScore,
      ndviValue: field.ndviCurrent,
      status: status,
      center: field.centroid != null
          ? GeoLocation(
              latitude: field.centroid!.latitude,
              longitude: field.centroid!.longitude,
            )
          : null,
      createdAt: field.createdAt,
      updatedAt: field.updatedAt,
    );
  }

  /// Filter and sort fields based on current criteria
  /// تصفية وترتيب الحقول حسب المعايير الحالية
  List<FieldEntity> _filterAndSortFields(List<FieldEntity> fields) {
    var filteredFields = fields.where((f) {
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

  /// Refresh fields from the API
  /// تحديث الحقول من الخادم
  Future<void> _refreshFieldsFromApi() async {
    if (_isRefreshing) return;

    setState(() => _isRefreshing = true);

    try {
      final authState = ref.read(authStateProvider);
      final tenantId = authState.user?.tenantId;

      if (tenantId == null) {
        // User not authenticated, show error
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('يرجى تسجيل الدخول أولاً'),
              backgroundColor: Colors.red,
            ),
          );
        }
        return;
      }

      // Fetch fresh data from the API and update local database
      final repo = ref.read(fieldsRepoProvider);
      final refreshedCount = await repo.refreshFromServer(tenantId);

      // Invalidate the providers to trigger UI refresh with new data
      ref.invalidate(fieldsStreamProvider(tenantId));
      ref.invalidate(allFieldsProvider(tenantId));

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('تم تحديث $refreshedCount حقل'),
            backgroundColor: const Color(0xFF367C2B),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل التحديث: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isRefreshing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Get authenticated user's tenant ID
    final authState = ref.watch(authStateProvider);
    final tenantId = authState.user?.tenantId;

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
        body: tenantId == null
            ? _buildUnauthenticatedState()
            : _buildAuthenticatedBody(tenantId),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _addField,
          backgroundColor: const Color(0xFF367C2B),
          icon: const Icon(Icons.add),
          label: const Text('حقل جديد'),
        ),
      ),
    );
  }

  /// Build UI when user is not authenticated
  /// واجهة عندما لا يكون المستخدم مسجل الدخول
  Widget _buildUnauthenticatedState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.lock_outline, size: 80, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            'يرجى تسجيل الدخول',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'سجل دخولك لعرض الحقول',
            style: TextStyle(color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  /// Build body for authenticated users with fields data from providers
  /// بناء المحتوى للمستخدمين المصادق عليهم مع بيانات الحقول من المزودات
  Widget _buildAuthenticatedBody(String tenantId) {
    // Watch the fields stream for live updates from the local database
    final fieldsStream = ref.watch(fieldsStreamProvider(tenantId));

    return fieldsStream.when(
      data: (domainFields) {
        // Map domain fields to UI entities
        final fields = domainFields
            .where((f) => !f.isDeleted) // Filter out soft-deleted fields
            .map(_mapDomainToUiEntity)
            .toList();

        // Apply search, filter, and sort
        final filteredFields = _filterAndSortFields(fields);

        return Column(
          children: [
            // Search and filters
            _buildSearchAndFilters(),

            // Stats bar
            _buildStatsBar(filteredFields),

            // Fields list/grid with pull-to-refresh
            Expanded(
              child: RefreshIndicator(
                onRefresh: _refreshFieldsFromApi,
                child: filteredFields.isEmpty
                    ? _buildEmptyState()
                    : _isGridView
                        ? _buildGridView(filteredFields)
                        : _buildListView(filteredFields),
              ),
            ),
          ],
        );
      },
      loading: () => const Center(
        child: CircularProgressIndicator(
          valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF367C2B)),
        ),
      ),
      error: (error, stack) => _buildErrorState(error, tenantId),
    );
  }

  /// Build error state with retry button
  /// بناء حالة الخطأ مع زر إعادة المحاولة
  Widget _buildErrorState(Object error, String tenantId) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 80, color: Colors.red[300]),
          const SizedBox(height: 16),
          Text(
            'حدث خطأ في تحميل الحقول',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            error.toString(),
            style: TextStyle(color: Colors.grey[500]),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () {
              ref.invalidate(fieldsStreamProvider(tenantId));
            },
            icon: const Icon(Icons.refresh),
            label: const Text('إعادة المحاولة'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF367C2B),
              foregroundColor: Colors.white,
            ),
          ),
        ],
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

  Widget _buildStatsBar(List<FieldEntity> filteredFields) {
    final totalArea = filteredFields.fold<double>(
      0,
      (sum, f) => sum + f.areaHectares,
    );
    final avgHealth = filteredFields.isEmpty
        ? 0.0
        : filteredFields.fold<double>(0, (sum, f) => sum + f.healthScore) /
            filteredFields.length;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: Colors.grey[50],
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem(
            icon: Icons.landscape,
            label: 'الحقول',
            value: '${filteredFields.length}',
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

  Widget _buildListView(List<FieldEntity> filteredFields) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: filteredFields.length,
      itemBuilder: (context, index) {
        final field = filteredFields[index];
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

  Widget _buildGridView(List<FieldEntity> filteredFields) {
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 0.85,
      ),
      itemCount: filteredFields.length,
      itemBuilder: (context, index) {
        final field = filteredFields[index];
        return EnhancedFieldCard(
          field: field,
          isCompact: true,
          onTap: () => _openFieldDetails(field),
        );
      },
    );
  }

  Widget _buildEmptyState() {
    // Use ListView for proper RefreshIndicator support (needs scrollable child)
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      children: [
        SizedBox(
          height: MediaQuery.of(context).size.height * 0.5,
          child: Center(
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
                  _searchQuery.isNotEmpty || _selectedCrop != null
                      ? 'اسحب للتحديث أو غير معايير البحث'
                      : 'اسحب للتحديث من الخادم أو أضف حقلاً جديداً',
                  style: TextStyle(color: Colors.grey[500]),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ],
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
