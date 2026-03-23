// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOOL ATMOSPHERE - Fields List Screen
// شاشة قائمة الحقول
// ═══════════════════════════════════════════════════════════════════════════════════════
//
// Features:
// - Glassmorphism field cards
// - Search and filter
// - Stats summary
// - Quick actions
//
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/atmosphere_theme.dart';
import '../models/field_model.dart';
import '../widgets/holographic_field_card.dart';
import 'field_map_screen.dart';

/// Fields List Screen
/// شاشة قائمة الحقول
class FieldsListScreen extends StatefulWidget {
  const FieldsListScreen({super.key});

  @override
  State<FieldsListScreen> createState() => _FieldsListScreenState();
}

class _FieldsListScreenState extends State<FieldsListScreen> {
  final TextEditingController _searchController = TextEditingController();

  /// Filter by crop type
  CropType? _selectedCropType;

  /// Filter by health status
  FieldHealthStatus? _selectedHealthStatus;

  /// Sort option
  _SortOption _sortOption = _SortOption.name;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  List<FieldModel> get _filteredFields {
    var fields = SampleFields.all;

    // Search filter
    if (_searchController.text.isNotEmpty) {
      final query = _searchController.text.toLowerCase();
      fields = fields.where((f) {
        return f.nameAr.toLowerCase().contains(query) ||
            f.nameEn.toLowerCase().contains(query) ||
            f.cropType.nameAr.contains(query) ||
            f.cropType.nameEn.toLowerCase().contains(query);
      }).toList();
    }

    // Crop type filter
    if (_selectedCropType != null) {
      fields = fields.where((f) => f.cropType == _selectedCropType).toList();
    }

    // Health status filter
    if (_selectedHealthStatus != null) {
      fields =
          fields.where((f) => f.healthStatus == _selectedHealthStatus).toList();
    }

    // Sort
    switch (_sortOption) {
      case _SortOption.name:
        fields.sort((a, b) => a.nameAr.compareTo(b.nameAr));
        break;
      case _SortOption.area:
        fields.sort((a, b) => b.areaHectares.compareTo(a.areaHectares));
        break;
      case _SortOption.health:
        fields.sort((a, b) => b.ndviValue.compareTo(a.ndviValue));
        break;
      case _SortOption.alerts:
        fields.sort((a, b) {
          if (a.hasAlerts && !b.hasAlerts) return -1;
          if (!a.hasAlerts && b.hasAlerts) return 1;
          return b.pendingTasks.compareTo(a.pendingTasks);
        });
        break;
    }

    return fields;
  }

  @override
  Widget build(BuildContext context) {
    final fields = _filteredFields;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AtmosphereColors.bgGradient,
        ),
        child: SafeArea(
          child: CustomScrollView(
            physics: const BouncingScrollPhysics(),
            slivers: [
              // App Bar
              _buildAppBar(),

              // Stats Summary
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(AtmosphereSpacing.md),
                  child: _buildStatsSummary(),
                ),
              ),

              // Search and Filters
              SliverToBoxAdapter(
                child: Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: AtmosphereSpacing.md),
                  child: _buildSearchAndFilters(),
                ),
              ),

              // Sort Options
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(AtmosphereSpacing.md),
                  child: _buildSortOptions(),
                ),
              ),

              // Fields List
              SliverPadding(
                padding: const EdgeInsets.symmetric(horizontal: AtmosphereSpacing.md),
                sliver: fields.isEmpty
                    ? SliverToBoxAdapter(child: _buildEmptyState())
                    : SliverList(
                        delegate: SliverChildBuilderDelegate(
                          (context, index) {
                            final field = fields[index];
                            return Padding(
                              padding:
                                  const EdgeInsets.only(bottom: AtmosphereSpacing.md),
                              child: HolographicFieldCard(
                                fieldName: field.nameAr,
                                fieldNameEn: field.nameEn,
                                moisture: field.moisturePercent,
                                temperature: field.temperatureCelsius,
                                sunlight: field.sunlightPercent,
                                status: _mapHealthToStatus(field.healthStatus),
                              ),
                            );
                          },
                          childCount: fields.length,
                        ),
                      ),
              ),

              // Bottom padding
              const SliverToBoxAdapter(
                child: SizedBox(height: 100),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          HapticFeedback.mediumImpact();
          Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => const FieldMapScreen()),
          );
        },
        backgroundColor: AtmosphereColors.success,
        icon: const Icon(Icons.map),
        label: const Text('عرض الخريطة'),
      ),
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      floating: true,
      backgroundColor: Colors.transparent,
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'الحقول',
            style: AtmosphereTypography.displaySmall.copyWith(
              fontWeight: FontWeight.w300,
              letterSpacing: 2,
            ),
          ),
          Text(
            'FIELDS',
            style: AtmosphereTypography.labelSmall.copyWith(
              color: AtmosphereColors.success,
              letterSpacing: 3,
            ),
          ),
        ],
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.add_circle_outline),
          color: AtmosphereColors.success,
          onPressed: () {
            HapticFeedback.lightImpact();
            // Add new field
          },
        ),
      ],
    );
  }

  Widget _buildStatsSummary() {
    final totalFields = SampleFields.all.length;
    final totalArea = SampleFields.totalArea;
    final avgHealth = (SampleFields.averageHealth * 100).round();
    final alertCount = SampleFields.needingAttention.length;

    return Container(
      padding: const EdgeInsets.all(AtmosphereSpacing.md),
      decoration: BoxDecoration(
        gradient: AtmosphereColors.glassGradient,
        borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
        border: Border.all(color: AtmosphereColors.glassBorder),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem(
            value: '$totalFields',
            label: 'الحقول',
            icon: Icons.grass,
            color: AtmosphereColors.success,
          ),
          _buildStatItem(
            value: '${totalArea.toStringAsFixed(1)} هـ',
            label: 'المساحة',
            icon: Icons.straighten,
            color: AtmosphereColors.info,
          ),
          _buildStatItem(
            value: '$avgHealth%',
            label: 'متوسط الصحة',
            icon: Icons.favorite,
            color: _getHealthColor(avgHealth / 100),
          ),
          _buildStatItem(
            value: '$alertCount',
            label: 'تنبيهات',
            icon: Icons.warning_amber,
            color: alertCount > 0 ? AtmosphereColors.alert : AtmosphereColors.success,
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem({
    required String value,
    required String label,
    required IconData icon,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: AtmosphereSpacing.xs),
        Text(
          value,
          style: AtmosphereTypography.headlineSmall.copyWith(color: color),
        ),
        Text(
          label,
          style: AtmosphereTypography.bodySmall,
        ),
      ],
    );
  }

  Widget _buildSearchAndFilters() {
    return Column(
      children: [
        // Search Bar
        Container(
          padding: const EdgeInsets.symmetric(horizontal: AtmosphereSpacing.md),
          decoration: BoxDecoration(
            gradient: AtmosphereColors.glassGradient,
            borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
            border: Border.all(color: AtmosphereColors.glassBorder),
          ),
          child: TextField(
            controller: _searchController,
            style: AtmosphereTypography.bodyMedium,
            decoration: InputDecoration(
              hintText: 'بحث عن حقل...',
              hintStyle: AtmosphereTypography.bodyMedium.copyWith(
                color: AtmosphereColors.textMuted,
              ),
              prefixIcon: const Icon(
                Icons.search,
                color: AtmosphereColors.textMuted,
              ),
              border: InputBorder.none,
              suffixIcon: _searchController.text.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      color: AtmosphereColors.textMuted,
                      onPressed: () {
                        _searchController.clear();
                        setState(() {});
                      },
                    )
                  : null,
            ),
            onChanged: (_) => setState(() {}),
          ),
        ),

        const SizedBox(height: AtmosphereSpacing.md),

        // Filter Chips
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              // Crop type filter
              _buildFilterChip(
                label: 'نوع المحصول',
                value: _selectedCropType?.nameAr,
                onTap: () => _showCropTypeFilter(),
              ),
              const SizedBox(width: AtmosphereSpacing.sm),

              // Health filter
              _buildFilterChip(
                label: 'الحالة الصحية',
                value: _getHealthStatusLabel(_selectedHealthStatus),
                onTap: () => _showHealthFilter(),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildFilterChip({
    required String label,
    String? value,
    required VoidCallback onTap,
  }) {
    final isActive = value != null;
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        onTap();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AtmosphereSpacing.md,
          vertical: AtmosphereSpacing.sm,
        ),
        decoration: BoxDecoration(
          color: isActive
              ? AtmosphereColors.success.withOpacity(0.2)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(AtmosphereRadius.full),
          border: Border.all(
            color: isActive
                ? AtmosphereColors.success
                : AtmosphereColors.glassBorder,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              value ?? label,
              style: AtmosphereTypography.bodySmall.copyWith(
                color: isActive
                    ? AtmosphereColors.success
                    : AtmosphereColors.textSecondary,
              ),
            ),
            if (isActive) ...[
              const SizedBox(width: AtmosphereSpacing.xs),
              GestureDetector(
                onTap: () {
                  setState(() {
                    if (value == _selectedCropType?.nameAr) {
                      _selectedCropType = null;
                    } else {
                      _selectedHealthStatus = null;
                    }
                  });
                },
                child: const Icon(
                  Icons.close,
                  size: 16,
                  color: AtmosphereColors.success,
                ),
              ),
            ] else
              const Icon(
                Icons.arrow_drop_down,
                size: 20,
                color: AtmosphereColors.textMuted,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSortOptions() {
    return Row(
      children: [
        const Text(
          'ترتيب:',
          style: AtmosphereTypography.bodySmall,
        ),
        const SizedBox(width: AtmosphereSpacing.sm),
        Expanded(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: _SortOption.values.map((option) {
                final isActive = _sortOption == option;
                return Padding(
                  padding: const EdgeInsets.only(left: AtmosphereSpacing.sm),
                  child: GestureDetector(
                    onTap: () {
                      HapticFeedback.lightImpact();
                      setState(() => _sortOption = option);
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AtmosphereSpacing.md,
                        vertical: AtmosphereSpacing.xs,
                      ),
                      decoration: BoxDecoration(
                        color: isActive
                            ? AtmosphereColors.success.withOpacity(0.2)
                            : Colors.transparent,
                        borderRadius: BorderRadius.circular(AtmosphereRadius.sm),
                        border: Border.all(
                          color: isActive
                              ? AtmosphereColors.success
                              : AtmosphereColors.glassBorder,
                        ),
                      ),
                      child: Text(
                        option.label,
                        style: AtmosphereTypography.labelSmall.copyWith(
                          color: isActive
                              ? AtmosphereColors.success
                              : AtmosphereColors.textMuted,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SizedBox(height: 60),
          Icon(
            Icons.search_off,
            size: 64,
            color: AtmosphereColors.textMuted.withOpacity(0.5),
          ),
          const SizedBox(height: AtmosphereSpacing.md),
          Text(
            'لا توجد حقول',
            style: AtmosphereTypography.headlineMedium.copyWith(
              color: AtmosphereColors.textMuted,
            ),
          ),
          const SizedBox(height: AtmosphereSpacing.sm),
          const Text(
            'جرب تغيير معايير البحث',
            style: AtmosphereTypography.bodyMedium,
          ),
        ],
      ),
    );
  }

  void _showCropTypeFilter() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(AtmosphereSpacing.lg),
          decoration: const BoxDecoration(
            color: AtmosphereColors.bgSecondary,
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(AtmosphereRadius.xl),
              topRight: Radius.circular(AtmosphereRadius.xl),
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'نوع المحصول',
                style: AtmosphereTypography.headlineLarge,
              ),
              const SizedBox(height: AtmosphereSpacing.lg),
              Wrap(
                spacing: AtmosphereSpacing.sm,
                runSpacing: AtmosphereSpacing.sm,
                children: CropType.values.map((type) {
                  return GestureDetector(
                    onTap: () {
                      setState(() => _selectedCropType = type);
                      Navigator.pop(context);
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AtmosphereSpacing.md,
                        vertical: AtmosphereSpacing.sm,
                      ),
                      decoration: BoxDecoration(
                        color: _selectedCropType == type
                            ? AtmosphereColors.success.withOpacity(0.2)
                            : AtmosphereColors.bgTertiary,
                        borderRadius: BorderRadius.circular(AtmosphereRadius.md),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(type.emoji),
                          const SizedBox(width: AtmosphereSpacing.sm),
                          Text(
                            type.nameAr,
                            style: AtmosphereTypography.bodyMedium,
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: AtmosphereSpacing.lg),
            ],
          ),
        );
      },
    );
  }

  void _showHealthFilter() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(AtmosphereSpacing.lg),
          decoration: const BoxDecoration(
            color: AtmosphereColors.bgSecondary,
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(AtmosphereRadius.xl),
              topRight: Radius.circular(AtmosphereRadius.xl),
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'الحالة الصحية',
                style: AtmosphereTypography.headlineLarge,
              ),
              const SizedBox(height: AtmosphereSpacing.lg),
              ...FieldHealthStatus.values
                  .where((s) => s != FieldHealthStatus.unknown)
                  .map((status) {
                final color = _getHealthStatusColor(status);
                return ListTile(
                  onTap: () {
                    setState(() => _selectedHealthStatus = status);
                    Navigator.pop(context);
                  },
                  leading: Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      color: color,
                      shape: BoxShape.circle,
                    ),
                  ),
                  title: Text(
                    _getHealthStatusLabel(status) ?? '',
                    style: AtmosphereTypography.bodyLarge,
                  ),
                  trailing: _selectedHealthStatus == status
                      ? const Icon(
                          Icons.check,
                          color: AtmosphereColors.success,
                        )
                      : null,
                );
              }),
              const SizedBox(height: AtmosphereSpacing.lg),
            ],
          ),
        );
      },
    );
  }

  FieldStatus _mapHealthToStatus(FieldHealthStatus health) {
    switch (health) {
      case FieldHealthStatus.healthy:
        return FieldStatus.active;
      case FieldHealthStatus.stressed:
        return FieldStatus.warning;
      case FieldHealthStatus.critical:
        return FieldStatus.alert;
      case FieldHealthStatus.unknown:
        return FieldStatus.inactive;
    }
  }

  String? _getHealthStatusLabel(FieldHealthStatus? status) {
    switch (status) {
      case FieldHealthStatus.healthy:
        return 'صحي';
      case FieldHealthStatus.stressed:
        return 'متوسط';
      case FieldHealthStatus.critical:
        return 'حرج';
      case FieldHealthStatus.unknown:
        return 'غير معروف';
      case null:
        return null;
    }
  }

  Color _getHealthStatusColor(FieldHealthStatus status) {
    switch (status) {
      case FieldHealthStatus.healthy:
        return AtmosphereColors.success;
      case FieldHealthStatus.stressed:
        return AtmosphereColors.warning;
      case FieldHealthStatus.critical:
        return AtmosphereColors.alert;
      case FieldHealthStatus.unknown:
        return AtmosphereColors.textMuted;
    }
  }

  Color _getHealthColor(double health) {
    if (health >= 0.6) return AtmosphereColors.success;
    if (health >= 0.4) return AtmosphereColors.warning;
    return AtmosphereColors.alert;
  }
}

enum _SortOption {
  name('الاسم'),
  area('المساحة'),
  health('الصحة'),
  alerts('التنبيهات');

  final String label;
  const _SortOption(this.label);
}
