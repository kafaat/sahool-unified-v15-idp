/// VRA Detail Screen - شاشة تفاصيل الوصفة
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/vra_models.dart';
import '../providers/vra_provider.dart';
import '../widgets/zone_legend_widget.dart';
import '../widgets/zone_map_widget.dart';

/// شاشة تفاصيل الوصفة
class VRADetailScreen extends ConsumerStatefulWidget {
  final String prescriptionId;

  const VRADetailScreen({
    super.key,
    required this.prescriptionId,
  });

  @override
  ConsumerState<VRADetailScreen> createState() => _VRADetailScreenState();
}

class _VRADetailScreenState extends ConsumerState<VRADetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final prescriptionAsync = ref.watch(prescriptionDetailsProvider(widget.prescriptionId));
    final locale = Localizations.localeOf(context).languageCode;
    final isRTL = locale == 'ar';

    return Scaffold(
      appBar: AppBar(
        title: Text(isRTL ? 'تفاصيل الوصفة' : 'Prescription Details'),
        actions: [
          prescriptionAsync.whenOrNull(
            data: (prescription) => _buildActions(prescription, locale),
          ) ?? const SizedBox.shrink(),
        ],
      ),
      body: prescriptionAsync.when(
        data: (prescription) => Column(
          children: [
            // معلومات أساسية
            _buildHeader(prescription, locale),

            // Tabs
            TabBar(
              controller: _tabController,
              tabs: [
                Tab(text: isRTL ? 'الخريطة' : 'Map'),
                Tab(text: isRTL ? 'المناطق' : 'Zones'),
                Tab(text: isRTL ? 'المعلومات' : 'Info'),
              ],
            ),

            // Tab Views
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildMapTab(prescription, locale),
                  _buildZonesTab(prescription, locale),
                  _buildInfoTab(prescription, locale),
                ],
              ),
            ),
          ],
        ),
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
                onPressed: () => ref.invalidate(prescriptionDetailsProvider),
                icon: const Icon(Icons.refresh),
                label: Text(isRTL ? 'إعادة المحاولة' : 'Retry'),
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: prescriptionAsync.whenOrNull(
        data: (prescription) => _buildBottomBar(prescription, locale),
      ),
    );
  }

  Widget _buildActions(VRAPrescription prescription, String locale) {
    final isRTL = locale == 'ar';
    return PopupMenuButton<String>(
      onSelected: (value) async {
        switch (value) {
          case 'export_geojson':
            await _exportPrescription(prescription, 'geojson', locale);
            break;
          case 'export_shapefile':
            await _exportPrescription(prescription, 'shapefile', locale);
            break;
          case 'delete':
            await _deletePrescription(prescription, locale);
            break;
        }
      },
      itemBuilder: (context) => [
        PopupMenuItem(
          value: 'export_geojson',
          child: Row(
            children: [
              const Icon(Icons.download),
              const SizedBox(width: 8),
              Text(isRTL ? 'تصدير GeoJSON' : 'Export GeoJSON'),
            ],
          ),
        ),
        PopupMenuItem(
          value: 'export_shapefile',
          child: Row(
            children: [
              const Icon(Icons.download),
              const SizedBox(width: 8),
              Text(isRTL ? 'تصدير Shapefile' : 'Export Shapefile'),
            ],
          ),
        ),
        if (prescription.status == PrescriptionStatus.draft)
          PopupMenuItem(
            value: 'delete',
            child: Row(
              children: [
                const Icon(Icons.delete, color: Colors.red),
                const SizedBox(width: 8),
                Text(isRTL ? 'حذف' : 'Delete', style: const TextStyle(color: Colors.red)),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildHeader(VRAPrescription prescription, String locale) {
    final isRTL = locale == 'ar';
    return Container(
      padding: const EdgeInsets.all(16),
      color: Theme.of(context).colorScheme.primaryContainer,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  prescription.getDisplayName(locale),
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              _buildStatusChip(prescription.status, locale),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            prescription.getFieldName(locale),
            style: TextStyle(fontSize: 16, color: Colors.grey[700]),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildInfoItem(
                Icons.category,
                prescription.vraType.getName(locale),
                locale,
              ),
              _buildInfoItem(
                Icons.landscape,
                '${prescription.totalArea.toStringAsFixed(1)} ${isRTL ? 'هكتار' : 'ha'}',
                locale,
              ),
              _buildInfoItem(
                Icons.grid_on,
                '${prescription.zonesCount} ${isRTL ? 'منطقة' : 'zones'}',
                locale,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInfoItem(IconData icon, String text, String locale) {
    return Row(
      children: [
        Icon(icon, size: 20),
        const SizedBox(width: 4),
        Text(text, style: const TextStyle(fontSize: 14)),
      ],
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
        color: color.withOpacity(0.2),
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

  Widget _buildMapTab(VRAPrescription prescription, String locale) {
    return Column(
      children: [
        Expanded(
          child: ZoneMapWidget(
            zones: prescription.zones,
            rates: prescription.rates,
          ),
        ),
        ZoneLegendWidget(
          zones: prescription.zones,
          rates: prescription.rates,
          vraType: prescription.vraType,
        ),
      ],
    );
  }

  Widget _buildZonesTab(VRAPrescription prescription, String locale) {
    final isRTL = locale == 'ar';
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: prescription.zones.length,
      itemBuilder: (context, index) {
        final zone = prescription.zones[index];
        final rate = prescription.rates.firstWhere((r) => r.zoneId == zone.zoneId);

        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ExpansionTile(
            title: Text(
              zone.getDisplayName(locale),
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Text(
              '${isRTL ? 'المساحة' : 'Area'}: ${zone.area.toStringAsFixed(2)} ${isRTL ? 'هكتار' : 'ha'}',
            ),
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildZoneStatRow(
                      isRTL ? 'معدل التطبيق' : 'Application Rate',
                      '${rate.rate.toStringAsFixed(2)} ${rate.getUnit(locale)}',
                    ),
                    if (zone.averageNdvi != null)
                      _buildZoneStatRow(
                        isRTL ? 'متوسط NDVI' : 'Average NDVI',
                        zone.averageNdvi!.toStringAsFixed(3),
                      ),
                    if (zone.averageElevation != null)
                      _buildZoneStatRow(
                        isRTL ? 'متوسط الارتفاع' : 'Average Elevation',
                        '${zone.averageElevation!.toStringAsFixed(1)} ${isRTL ? 'م' : 'm'}',
                      ),
                    if (zone.soilType != null)
                      _buildZoneStatRow(
                        isRTL ? 'نوع التربة' : 'Soil Type',
                        zone.getSoilType(locale) ?? '',
                      ),
                    if (rate.cost != null)
                      _buildZoneStatRow(
                        isRTL ? 'التكلفة' : 'Cost',
                        '${rate.getTotalCost(zone.area)?.toStringAsFixed(2)} ${isRTL ? 'ريال' : 'SAR'}',
                      ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildZoneStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey[600])),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildInfoTab(VRAPrescription prescription, String locale) {
    final isRTL = locale == 'ar';
    final dateFormat = DateFormat.yMMMd(locale).add_jm();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildInfoSection(
          isRTL ? 'معلومات عامة' : 'General Information',
          [
            _buildInfoRow(isRTL ? 'الاسم' : 'Name', prescription.getDisplayName(locale)),
            _buildInfoRow(isRTL ? 'الحقل' : 'Field', prescription.getFieldName(locale)),
            _buildInfoRow(isRTL ? 'النوع' : 'Type', prescription.vraType.getName(locale)),
            _buildInfoRow(isRTL ? 'طريقة التقسيم' : 'Zoning Method', prescription.zoningMethod.getName(locale)),
            _buildInfoRow(isRTL ? 'عدد المناطق' : 'Zones Count', prescription.zonesCount.toString()),
            _buildInfoRow(
              isRTL ? 'المساحة الإجمالية' : 'Total Area',
              '${prescription.totalArea.toStringAsFixed(2)} ${isRTL ? 'هكتار' : 'ha'}',
            ),
          ],
        ),
        const SizedBox(height: 16),
        _buildInfoSection(
          isRTL ? 'الكميات والتكاليف' : 'Quantities & Costs',
          [
            _buildInfoRow(
              isRTL ? 'الكمية الإجمالية' : 'Total Quantity',
              prescription.getTotalQuantity().toStringAsFixed(2),
            ),
            _buildInfoRow(
              isRTL ? 'متوسط المعدل' : 'Average Rate',
              prescription.getAverageRate().toStringAsFixed(2),
            ),
            _buildInfoRow(
              isRTL ? 'التكلفة الإجمالية' : 'Total Cost',
              '${prescription.getTotalCost().toStringAsFixed(2)} ${isRTL ? 'ريال' : 'SAR'}',
            ),
          ],
        ),
        const SizedBox(height: 16),
        _buildInfoSection(
          isRTL ? 'التواريخ' : 'Dates',
          [
            _buildInfoRow(isRTL ? 'تاريخ الإنشاء' : 'Created', dateFormat.format(prescription.createdAt)),
            if (prescription.scheduledDate != null)
              _buildInfoRow(
                isRTL ? 'موعد التطبيق' : 'Scheduled',
                dateFormat.format(prescription.scheduledDate!),
              ),
            if (prescription.approvedAt != null)
              _buildInfoRow(
                isRTL ? 'تاريخ الاعتماد' : 'Approved',
                dateFormat.format(prescription.approvedAt!),
              ),
            if (prescription.appliedDate != null)
              _buildInfoRow(
                isRTL ? 'تاريخ التطبيق' : 'Applied',
                dateFormat.format(prescription.appliedDate!),
              ),
          ],
        ),
        const SizedBox(height: 16),
        if (prescription.notes != null)
          _buildInfoSection(
            isRTL ? 'ملاحظات' : 'Notes',
            [
              Text(prescription.getNotes(locale) ?? ''),
            ],
          ),
      ],
    );
  }

  Widget _buildInfoSection(String title, List<Widget> children) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Divider(),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey[600])),
          Flexible(
            child: Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.bold),
              textAlign: TextAlign.end,
            ),
          ),
        ],
      ),
    );
  }

  Widget? _buildBottomBar(VRAPrescription prescription, String locale) {
    final isRTL = locale == 'ar';

    if (prescription.status == PrescriptionStatus.draft) {
      return SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: FilledButton.icon(
            onPressed: () => _approvePrescription(prescription, locale),
            icon: const Icon(Icons.check_circle),
            label: Text(isRTL ? 'اعتماد الوصفة' : 'Approve Prescription'),
            style: FilledButton.styleFrom(
              minimumSize: const Size.fromHeight(48),
            ),
          ),
        ),
      );
    } else if (prescription.status == PrescriptionStatus.approved) {
      return SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: FilledButton.icon(
            onPressed: () => _applyPrescription(prescription, locale),
            icon: const Icon(Icons.play_arrow),
            label: Text(isRTL ? 'تطبيق الوصفة' : 'Apply Prescription'),
            style: FilledButton.styleFrom(
              minimumSize: const Size.fromHeight(48),
            ),
          ),
        ),
      );
    }

    return null;
  }

  Future<void> _approvePrescription(VRAPrescription prescription, String locale) async {
    final isRTL = locale == 'ar';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(isRTL ? 'اعتماد الوصفة' : 'Approve Prescription'),
        content: Text(
          isRTL
              ? 'هل أنت متأكد من اعتماد هذه الوصفة؟'
              : 'Are you sure you want to approve this prescription?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(isRTL ? 'إلغاء' : 'Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(isRTL ? 'اعتماد' : 'Approve'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      final success = await ref.read(vraControllerProvider.notifier).approvePrescription(
            prescription.prescriptionId,
          );

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(isRTL ? 'تم اعتماد الوصفة بنجاح' : 'Prescription approved successfully')),
        );
        ref.invalidate(prescriptionDetailsProvider);
      }
    }
  }

  Future<void> _applyPrescription(VRAPrescription prescription, String locale) async {
    final isRTL = locale == 'ar';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(isRTL ? 'تطبيق الوصفة' : 'Apply Prescription'),
        content: Text(
          isRTL
              ? 'هل أنت متأكد من تطبيق هذه الوصفة؟'
              : 'Are you sure you want to apply this prescription?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(isRTL ? 'إلغاء' : 'Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(isRTL ? 'تطبيق' : 'Apply'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      final success = await ref.read(vraControllerProvider.notifier).applyPrescription(
            prescription.prescriptionId,
            appliedDate: DateTime.now(),
          );

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(isRTL ? 'تم تطبيق الوصفة بنجاح' : 'Prescription applied successfully')),
        );
        ref.invalidate(prescriptionDetailsProvider);
      }
    }
  }

  Future<void> _exportPrescription(VRAPrescription prescription, String format, String locale) async {
    final isRTL = locale == 'ar';

    final result = await ref.read(vraControllerProvider.notifier).exportPrescription(
          prescription.prescriptionId,
          format: format,
        );

    if (result != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isRTL ? 'تم تصدير الوصفة بنجاح' : 'Prescription exported successfully',
          ),
        ),
      );
    }
  }

  Future<void> _deletePrescription(VRAPrescription prescription, String locale) async {
    final isRTL = locale == 'ar';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(isRTL ? 'حذف الوصفة' : 'Delete Prescription'),
        content: Text(
          isRTL
              ? 'هل أنت متأكد من حذف هذه الوصفة؟ لا يمكن التراجع عن هذا الإجراء.'
              : 'Are you sure you want to delete this prescription? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(isRTL ? 'إلغاء' : 'Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: Text(isRTL ? 'حذف' : 'Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      final success = await ref.read(vraControllerProvider.notifier).deletePrescription(
            prescription.prescriptionId,
          );

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(isRTL ? 'تم حذف الوصفة بنجاح' : 'Prescription deleted successfully')),
        );
        Navigator.pop(context);
      }
    }
  }
}
