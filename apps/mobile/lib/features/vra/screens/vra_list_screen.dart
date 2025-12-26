/// VRA List Screen - شاشة قائمة الوصفات
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/vra_models.dart';
import '../providers/vra_provider.dart';
import 'vra_create_screen.dart';
import 'vra_detail_screen.dart';

/// شاشة قائمة الوصفات
class VRAListScreen extends ConsumerStatefulWidget {
  const VRAListScreen({super.key});

  @override
  ConsumerState<VRAListScreen> createState() => _VRAListScreenState();
}

class _VRAListScreenState extends ConsumerState<VRAListScreen> {
  VRAType? _selectedType;
  PrescriptionStatus? _selectedStatus;
  DateTime? _startDate;
  DateTime? _endDate;

  PrescriptionFilter get _currentFilter {
    return PrescriptionFilter(
      vraType: _selectedType,
      status: _selectedStatus,
      startDate: _startDate,
      endDate: _endDate,
    );
  }

  @override
  Widget build(BuildContext context) {
    final prescriptionsAsync = ref.watch(prescriptionListProvider(_currentFilter));
    final statsAsync = ref.watch(vraStatsProvider);
    final locale = Localizations.localeOf(context).languageCode;
    final isRTL = locale == 'ar';

    return Scaffold(
      appBar: AppBar(
        title: Text(isRTL ? 'وصفات التطبيق المتغير' : 'VRA Prescriptions'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(prescriptionListProvider);
          ref.invalidate(vraStatsProvider);
        },
        child: Column(
          children: [
            // إحصائيات سريعة
            statsAsync.when(
              data: (stats) => _buildStatsCard(stats, locale),
              loading: () => const LinearProgressIndicator(),
              error: (_, __) => const SizedBox.shrink(),
            ),

            // الفلاتر النشطة
            if (_currentFilter.hasFilters) _buildActiveFilters(locale),

            // قائمة الوصفات
            Expanded(
              child: prescriptionsAsync.when(
                data: (prescriptions) {
                  if (prescriptions.isEmpty) {
                    return _buildEmptyState(locale);
                  }
                  return ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: prescriptions.length,
                    itemBuilder: (context, index) {
                      return _buildPrescriptionCard(
                        prescriptions[index],
                        locale,
                      );
                    },
                  );
                },
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, stack) => Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
                      const SizedBox(height: 16),
                      Text(
                        error.toString(),
                        style: const TextStyle(fontSize: 16),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: () => ref.invalidate(prescriptionListProvider),
                        icon: const Icon(Icons.refresh),
                        label: Text(isRTL ? 'إعادة المحاولة' : 'Retry'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const VRACreateScreen()),
          );
        },
        icon: const Icon(Icons.add),
        label: Text(isRTL ? 'وصفة جديدة' : 'New Prescription'),
      ),
    );
  }

  Widget _buildStatsCard(VRAStats stats, String locale) {
    final isRTL = locale == 'ar';
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildStatItem(
              stats.totalPrescriptions.toString(),
              isRTL ? 'المجموع' : 'Total',
              Colors.blue,
            ),
            _buildStatItem(
              stats.draftPrescriptions.toString(),
              isRTL ? 'مسودة' : 'Draft',
              Colors.orange,
            ),
            _buildStatItem(
              stats.approvedPrescriptions.toString(),
              isRTL ? 'معتمد' : 'Approved',
              Colors.green,
            ),
            _buildStatItem(
              stats.appliedPrescriptions.toString(),
              isRTL ? 'مطبق' : 'Applied',
              Colors.purple,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String value, String label, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildActiveFilters(String locale) {
    final isRTL = locale == 'ar';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Wrap(
        spacing: 8,
        children: [
          if (_selectedType != null)
            Chip(
              label: Text(_selectedType!.getName(locale)),
              onDeleted: () => setState(() => _selectedType = null),
            ),
          if (_selectedStatus != null)
            Chip(
              label: Text(_selectedStatus!.getName(locale)),
              onDeleted: () => setState(() => _selectedStatus = null),
            ),
          if (_startDate != null || _endDate != null)
            Chip(
              label: Text(
                '${_startDate != null ? DateFormat.yMd(locale).format(_startDate!) : ''} - ${_endDate != null ? DateFormat.yMd(locale).format(_endDate!) : ''}',
              ),
              onDeleted: () => setState(() {
                _startDate = null;
                _endDate = null;
              }),
            ),
          TextButton.icon(
            onPressed: () => setState(() {
              _selectedType = null;
              _selectedStatus = null;
              _startDate = null;
              _endDate = null;
            }),
            icon: const Icon(Icons.clear_all),
            label: Text(isRTL ? 'مسح الكل' : 'Clear All'),
          ),
        ],
      ),
    );
  }

  Widget _buildPrescriptionCard(VRAPrescription prescription, String locale) {
    final isRTL = locale == 'ar';
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => VRADetailScreen(prescriptionId: prescription.prescriptionId),
            ),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      prescription.getDisplayName(locale),
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  _buildStatusChip(prescription.status, locale),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.landscape, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    prescription.getFieldName(locale),
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  const SizedBox(width: 16),
                  Icon(Icons.category, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    prescription.vraType.getName(locale),
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isRTL ? 'المساحة' : 'Area',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                      Text(
                        '${prescription.totalArea.toStringAsFixed(1)} ${isRTL ? 'هكتار' : 'ha'}',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isRTL ? 'المناطق' : 'Zones',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                      Text(
                        prescription.zonesCount.toString(),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isRTL ? 'التاريخ' : 'Date',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                      Text(
                        DateFormat.yMd(locale).format(prescription.createdAt),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(PrescriptionStatus status, String locale) {
    Color color;
    switch (status) {
      case PrescriptionStatus.draft:
        color = Colors.orange;
        break;
      case PrescriptionStatus.approved:
        color = Colors.green;
        break;
      case PrescriptionStatus.applied:
        color = Colors.purple;
        break;
      case PrescriptionStatus.cancelled:
        color = Colors.red;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color),
      ),
      child: Text(
        status.getName(locale),
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildEmptyState(String locale) {
    final isRTL = locale == 'ar';
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.description_outlined, size: 80, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            isRTL ? 'لا توجد وصفات' : 'No prescriptions',
            style: TextStyle(fontSize: 18, color: Colors.grey[600]),
          ),
          const SizedBox(height: 8),
          Text(
            isRTL ? 'اضغط على الزر أدناه لإنشاء وصفة جديدة' : 'Tap the button below to create a new prescription',
            style: TextStyle(fontSize: 14, color: Colors.grey[500]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  void _showFilterDialog() {
    final locale = Localizations.localeOf(context).languageCode;
    final isRTL = locale == 'ar';

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(isRTL ? 'تصفية الوصفات' : 'Filter Prescriptions'),
        content: StatefulBuilder(
          builder: (context, setState) => SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(isRTL ? 'النوع' : 'Type', style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: VRAType.values.map((type) {
                    return FilterChip(
                      label: Text(type.getName(locale)),
                      selected: _selectedType == type,
                      onSelected: (selected) {
                        setState(() => _selectedType = selected ? type : null);
                      },
                    );
                  }).toList(),
                ),
                const SizedBox(height: 16),
                Text(isRTL ? 'الحالة' : 'Status', style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: PrescriptionStatus.values.map((status) {
                    return FilterChip(
                      label: Text(status.getName(locale)),
                      selected: _selectedStatus == status,
                      onSelected: (selected) {
                        setState(() => _selectedStatus = selected ? status : null);
                      },
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                _selectedType = null;
                _selectedStatus = null;
                _startDate = null;
                _endDate = null;
              });
              Navigator.pop(context);
            },
            child: Text(isRTL ? 'مسح' : 'Clear'),
          ),
          FilledButton(
            onPressed: () {
              setState(() {});
              Navigator.pop(context);
            },
            child: Text(isRTL ? 'تطبيق' : 'Apply'),
          ),
        ],
      ),
    );
  }
}
