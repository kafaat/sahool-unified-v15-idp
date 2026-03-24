/// Farmers List Screen
/// شاشة قائمة المزارعين
///
/// Displays all farmers with search and filter capabilities
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/models/farmer_profile.dart';
import '../../state/crm_providers.dart';
import '../widgets/farmer_card.dart';
import 'farmer_profile_screen.dart';

/// Farmers List Screen
/// شاشة عرض جميع المزارعين
class FarmersListScreen extends ConsumerStatefulWidget {
  const FarmersListScreen({super.key});

  @override
  ConsumerState<FarmersListScreen> createState() => _FarmersListScreenState();
}

class _FarmersListScreenState extends ConsumerState<FarmersListScreen> {
  final _searchController = TextEditingController();
  bool _isSearching = false;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final filter = ref.watch(farmerFilterProvider);
    final farmersAsync = ref.watch(farmersListProvider(filter));

    return Scaffold(
      appBar: _buildAppBar(context, filter),
      body: Column(
        children: [
          // Filter chips
          if (filter.hasFilters) _buildFilterChips(filter),

          // Farmers list
          Expanded(
            child: farmersAsync.when(
              data: (farmers) => _buildFarmersList(farmers),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => _buildError(error),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _navigateToAddFarmer(context),
        backgroundColor: const Color(0xFF367C2B),
        child: const Icon(Icons.person_add, color: Colors.white),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(BuildContext context, FarmerFilter filter) {
    if (_isSearching) {
      return AppBar(
        backgroundColor: Colors.white,
        elevation: 1,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black87),
          onPressed: () {
            setState(() {
              _isSearching = false;
              _searchController.clear();
            });
            ref.read(farmerFilterProvider.notifier).state =
                filter.copyWith(clearSearch: true);
          },
        ),
        title: TextField(
          controller: _searchController,
          autofocus: true,
          decoration: const InputDecoration(
            hintText: 'بحث عن مزارع...',
            border: InputBorder.none,
          ),
          onChanged: (value) {
            ref.read(farmerFilterProvider.notifier).state =
                filter.copyWith(search: value.isEmpty ? null : value);
          },
        ),
        actions: [
          if (_searchController.text.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.clear, color: Colors.black87),
              onPressed: () {
                _searchController.clear();
                ref.read(farmerFilterProvider.notifier).state =
                    filter.copyWith(clearSearch: true);
              },
            ),
        ],
      );
    }

    return AppBar(
      title: const Text('المزارعين'),
      actions: [
        IconButton(
          icon: const Icon(Icons.search),
          onPressed: () => setState(() => _isSearching = true),
        ),
        IconButton(
          icon: Badge(
            isLabelVisible: filter.hasFilters,
            child: const Icon(Icons.filter_list),
          ),
          onPressed: () => _showFilterSheet(context, filter),
        ),
        IconButton(
          icon: const Icon(Icons.sort),
          onPressed: () => _showSortOptions(context, filter),
        ),
      ],
    );
  }

  Widget _buildFilterChips(FarmerFilter filter) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            if (filter.status != null)
              _buildFilterChip(
                label: _getStatusLabel(filter.status!),
                onRemove: () {
                  ref.read(farmerFilterProvider.notifier).state =
                      filter.copyWith(clearStatus: true);
                },
              ),
            if (filter.segment != null)
              _buildFilterChip(
                label: _getSegmentLabel(filter.segment!),
                onRemove: () {
                  ref.read(farmerFilterProvider.notifier).state =
                      filter.copyWith(clearSegment: true);
                },
              ),
            if (filter.governorate != null)
              _buildFilterChip(
                label: filter.governorate!,
                onRemove: () {
                  ref.read(farmerFilterProvider.notifier).state =
                      filter.copyWith(clearGovernorate: true);
                },
              ),
            const SizedBox(width: 8),
            TextButton(
              onPressed: () {
                ref.read(farmerFilterProvider.notifier).state =
                    filter.clear();
              },
              child: const Text('مسح الكل'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterChip({
    required String label,
    required VoidCallback onRemove,
  }) {
    return Padding(
      padding: const EdgeInsets.only(left: 8),
      child: Chip(
        label: Text(label, style: const TextStyle(fontSize: 12)),
        deleteIcon: const Icon(Icons.close, size: 16),
        onDeleted: onRemove,
        backgroundColor: const Color(0xFF367C2B).withValues(alpha: 0.1),
        labelStyle: const TextStyle(color: Color(0xFF367C2B)),
        deleteIconColor: const Color(0xFF367C2B),
      ),
    );
  }

  Widget _buildFarmersList(List<FarmerProfile> farmers) {
    if (farmers.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.people_outline, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'لا يوجد مزارعين',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: () => _navigateToAddFarmer(context),
              icon: const Icon(Icons.add),
              label: const Text('إضافة مزارع'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(farmersListProvider);
      },
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: farmers.length,
        itemBuilder: (context, index) {
          final farmer = farmers[index];
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: FarmerCard(
              farmer: farmer,
              onTap: () => _navigateToFarmerProfile(context, farmer.id),
              onCall: () => _callFarmer(farmer),
              onWhatsApp: () => _openWhatsApp(farmer),
            ),
          );
        },
      ),
    );
  }

  Widget _buildError(Object error) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
          const SizedBox(height: 16),
          Text(
            error.toString(),
            style: TextStyle(color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => ref.invalidate(farmersListProvider),
            child: const Text('إعادة المحاولة'),
          ),
        ],
      ),
    );
  }

  void _showFilterSheet(BuildContext context, FarmerFilter filter) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        maxChildSize: 0.9,
        minChildSize: 0.4,
        expand: false,
        builder: (context, scrollController) => _FilterSheet(
          filter: filter,
          scrollController: scrollController,
          onApply: (newFilter) {
            ref.read(farmerFilterProvider.notifier).state = newFilter;
            Navigator.pop(context);
          },
        ),
      ),
    );
  }

  void _showSortOptions(BuildContext context, FarmerFilter filter) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.access_time),
              title: const Text('الأحدث'),
              trailing: filter.sortBy == null || filter.sortBy == 'updated_at'
                  ? const Icon(Icons.check, color: Color(0xFF367C2B))
                  : null,
              onTap: () {
                ref.read(farmerFilterProvider.notifier).state =
                    filter.copyWith(sortBy: 'updated_at', sortOrder: 'desc');
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.sort_by_alpha),
              title: const Text('الاسم (أ-ي)'),
              trailing: filter.sortBy == 'name' && filter.sortOrder == 'asc'
                  ? const Icon(Icons.check, color: Color(0xFF367C2B))
                  : null,
              onTap: () {
                ref.read(farmerFilterProvider.notifier).state =
                    filter.copyWith(sortBy: 'name', sortOrder: 'asc');
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.touch_app),
              title: const Text('آخر تفاعل'),
              trailing: filter.sortBy == 'last_interaction_at'
                  ? const Icon(Icons.check, color: Color(0xFF367C2B))
                  : null,
              onTap: () {
                ref.read(farmerFilterProvider.notifier).state = filter.copyWith(
                    sortBy: 'last_interaction_at', sortOrder: 'desc');
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.landscape),
              title: const Text('المساحة'),
              trailing: filter.sortBy == 'total_area_hectares'
                  ? const Icon(Icons.check, color: Color(0xFF367C2B))
                  : null,
              onTap: () {
                ref.read(farmerFilterProvider.notifier).state = filter.copyWith(
                    sortBy: 'total_area_hectares', sortOrder: 'desc');
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _navigateToAddFarmer(BuildContext context) {
    // Navigate to add farmer screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('إضافة مزارع جديد')),
    );
  }

  void _navigateToFarmerProfile(BuildContext context, String farmerId) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => FarmerProfileScreen(farmerId: farmerId),
      ),
    );
  }

  void _callFarmer(FarmerProfile farmer) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('جاري الاتصال بـ ${farmer.displayName}')),
    );
  }

  void _openWhatsApp(FarmerProfile farmer) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('فتح واتساب مع ${farmer.displayName}')),
    );
  }

  String _getStatusLabel(FarmerStatus status) {
    switch (status) {
      case FarmerStatus.active:
        return 'نشط';
      case FarmerStatus.inactive:
        return 'غير نشط';
      case FarmerStatus.pending:
        return 'قيد المراجعة';
      case FarmerStatus.suspended:
        return 'موقوف';
    }
  }

  String _getSegmentLabel(FarmerSegment segment) {
    switch (segment) {
      case FarmerSegment.premium:
        return 'مميز';
      case FarmerSegment.regular:
        return 'عادي';
      case FarmerSegment.newFarmer:
        return 'جديد';
      case FarmerSegment.potential:
        return 'محتمل';
    }
  }
}

/// Filter Sheet Widget
class _FilterSheet extends StatefulWidget {
  final FarmerFilter filter;
  final ScrollController scrollController;
  final Function(FarmerFilter) onApply;

  const _FilterSheet({
    required this.filter,
    required this.scrollController,
    required this.onApply,
  });

  @override
  State<_FilterSheet> createState() => _FilterSheetState();
}

class _FilterSheetState extends State<_FilterSheet> {
  late FarmerStatus? _status;
  late FarmerSegment? _segment;
  late String? _governorate;

  @override
  void initState() {
    super.initState();
    _status = widget.filter.status;
    _segment = widget.filter.segment;
    _governorate = widget.filter.governorate;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Header
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              const Text(
                'الفلترة',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              TextButton(
                onPressed: () {
                  setState(() {
                    _status = null;
                    _segment = null;
                    _governorate = null;
                  });
                },
                child: const Text('مسح'),
              ),
            ],
          ),
        ),
        const Divider(height: 1),

        // Content
        Expanded(
          child: ListView(
            controller: widget.scrollController,
            padding: const EdgeInsets.all(16),
            children: [
              // Status filter
              _buildSectionTitle('الحالة'),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: FarmerStatus.values.map((status) {
                  final isSelected = _status == status;
                  return ChoiceChip(
                    label: Text(_getStatusLabel(status)),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        _status = selected ? status : null;
                      });
                    },
                    selectedColor: const Color(0xFF367C2B).withValues(alpha: 0.2),
                  );
                }).toList(),
              ),

              const SizedBox(height: 24),

              // Segment filter
              _buildSectionTitle('الشريحة'),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: FarmerSegment.values.map((segment) {
                  final isSelected = _segment == segment;
                  return ChoiceChip(
                    label: Text(_getSegmentLabel(segment)),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        _segment = selected ? segment : null;
                      });
                    },
                    selectedColor: const Color(0xFF367C2B).withValues(alpha: 0.2),
                  );
                }).toList(),
              ),

              const SizedBox(height: 24),

              // Governorate filter
              _buildSectionTitle('المحافظة'),
              DropdownButtonFormField<String>(
                value: _governorate,
                decoration: const InputDecoration(
                  hintText: 'اختر المحافظة',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'صنعاء', child: Text('صنعاء')),
                  DropdownMenuItem(value: 'عدن', child: Text('عدن')),
                  DropdownMenuItem(value: 'تعز', child: Text('تعز')),
                  DropdownMenuItem(value: 'الحديدة', child: Text('الحديدة')),
                  DropdownMenuItem(value: 'إب', child: Text('إب')),
                  DropdownMenuItem(value: 'ذمار', child: Text('ذمار')),
                ],
                onChanged: (value) {
                  setState(() {
                    _governorate = value;
                  });
                },
              ),
            ],
          ),
        ),

        // Apply button
        Padding(
          padding: const EdgeInsets.all(16),
          child: SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                widget.onApply(
                  widget.filter.copyWith(
                    status: _status,
                    segment: _segment,
                    governorate: _governorate,
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF367C2B),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: const Text('تطبيق'),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  String _getStatusLabel(FarmerStatus status) {
    switch (status) {
      case FarmerStatus.active:
        return 'نشط';
      case FarmerStatus.inactive:
        return 'غير نشط';
      case FarmerStatus.pending:
        return 'قيد المراجعة';
      case FarmerStatus.suspended:
        return 'موقوف';
    }
  }

  String _getSegmentLabel(FarmerSegment segment) {
    switch (segment) {
      case FarmerSegment.premium:
        return 'مميز';
      case FarmerSegment.regular:
        return 'عادي';
      case FarmerSegment.newFarmer:
        return 'جديد';
      case FarmerSegment.potential:
        return 'محتمل';
    }
  }
}

