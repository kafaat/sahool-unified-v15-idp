/// Advisory History Screen
/// شاشة سجل التوصيات
///
/// Shows history of all AI-generated advisories with filtering
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/config/theme.dart';
import '../../domain/models/advisory.dart';
import '../../state/ai_advisor_providers.dart';
import '../widgets/advisory_card.dart';

class AdvisoryHistoryScreen extends ConsumerStatefulWidget {
  final String? fieldId;
  final AdvisoryType? filterType;

  const AdvisoryHistoryScreen({
    super.key,
    this.fieldId,
    this.filterType,
  });

  @override
  ConsumerState<AdvisoryHistoryScreen> createState() => _AdvisoryHistoryScreenState();
}

class _AdvisoryHistoryScreenState extends ConsumerState<AdvisoryHistoryScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  AdvisoryType? _selectedType;
  AdvisoryStatus? _selectedStatus;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _selectedType = widget.filterType;

    // Load advisory history
    Future.microtask(() {
      ref.read(advisoryHistoryProvider.notifier).loadHistory(
        fieldId: widget.fieldId,
        type: widget.filterType,
      );
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(advisoryHistoryProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('سجل التوصيات'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'الكل'),
            Tab(text: 'قيد الانتظار'),
            Tab(text: 'مطبقة'),
          ],
          onTap: (index) {
            setState(() {
              switch (index) {
                case 0:
                  _selectedStatus = null;
                  break;
                case 1:
                  _selectedStatus = AdvisoryStatus.pending;
                  break;
                case 2:
                  _selectedStatus = AdvisoryStatus.applied;
                  break;
              }
            });
            _refreshList();
          },
        ),
        actions: [
          // Filter button
          IconButton(
            icon: Badge(
              isLabelVisible: _selectedType != null,
              child: const Icon(Icons.filter_list),
            ),
            onPressed: () => _showFilterSheet(context),
            tooltip: 'تصفية',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshList,
        child: state.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => Center(child: Text(error.toString())),
          data: (advisories) => advisories.isEmpty
              ? _buildEmptyState()
              : _buildAdvisoryList(advisories),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.history,
            size: 64,
            color: Colors.grey[300],
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد توصيات',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'اسأل المستشار الذكي للحصول على توصيات',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => context.pop(),
            icon: const Icon(Icons.psychology),
            label: const Text('اسأل المستشار'),
          ),
        ],
      ),
    );
  }

  Widget _buildAdvisoryList(List<Advisory> advisories) {
    // Filter by status if selected
    var filteredAdvisories = advisories;
    if (_selectedStatus != null) {
      filteredAdvisories = advisories
          .where((a) => a.status == _selectedStatus)
          .toList();
    }

    // Group by date
    final grouped = _groupByDate(filteredAdvisories);

    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 8),
      itemCount: grouped.length,
      itemBuilder: (context, index) {
        final entry = grouped.entries.elementAt(index);
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Date header
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Text(
                entry.key,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Colors.grey[600],
                ),
              ),
            ),
            // Advisories for this date
            ...entry.value.map((advisory) => AdvisoryCard(
              advisory: advisory,
              onTap: () => context.push('/ai-advisor/details/${advisory.id}'),
              onApply: advisory.status == AdvisoryStatus.pending
                  ? () => _markAsApplied(advisory.id)
                  : null,
              onDismiss: advisory.status == AdvisoryStatus.pending
                  ? () => _dismissAdvisory(advisory.id)
                  : null,
            )),
          ],
        );
      },
    );
  }

  Map<String, List<Advisory>> _groupByDate(List<Advisory> advisories) {
    final grouped = <String, List<Advisory>>{};

    for (final advisory in advisories) {
      final dateKey = _formatDateHeader(advisory.createdAt);
      grouped.putIfAbsent(dateKey, () => []).add(advisory);
    }

    return grouped;
  }

  String _formatDateHeader(DateTime date) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final advisoryDate = DateTime(date.year, date.month, date.day);

    if (advisoryDate == today) {
      return 'اليوم';
    } else if (advisoryDate == yesterday) {
      return 'أمس';
    } else if (now.difference(date).inDays < 7) {
      final weekdays = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];
      return weekdays[date.weekday % 7];
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }

  void _showFilterSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => StatefulBuilder(
        builder: (context, setSheetState) => SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'تصفية التوصيات',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    TextButton(
                      onPressed: () {
                        setSheetState(() {
                          _selectedType = null;
                        });
                        setState(() {
                          _selectedType = null;
                        });
                        _refreshList();
                      },
                      child: const Text('إعادة تعيين'),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Type filter
                const Text(
                  'نوع التوصية',
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: AdvisoryType.values.map((type) {
                    final isSelected = _selectedType == type;
                    return FilterChip(
                      label: Text(_getTypeLabel(type)),
                      selected: isSelected,
                      onSelected: (selected) {
                        setSheetState(() {
                          _selectedType = selected ? type : null;
                        });
                        setState(() {
                          _selectedType = selected ? type : null;
                        });
                      },
                      selectedColor: SahoolTheme.primary.withValues(alpha: 0.2),
                      checkmarkColor: SahoolTheme.primary,
                    );
                  }).toList(),
                ),

                const SizedBox(height: 24),

                // Apply button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                      _refreshList();
                    },
                    child: const Text('تطبيق'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _getTypeLabel(AdvisoryType type) {
    switch (type) {
      case AdvisoryType.irrigation:
        return 'الري';
      case AdvisoryType.fertilization:
        return 'التسميد';
      case AdvisoryType.pestControl:
        return 'الآفات';
      case AdvisoryType.diseaseControl:
        return 'الأمراض';
      case AdvisoryType.harvest:
        return 'الحصاد';
      case AdvisoryType.planting:
        return 'الزراعة';
      case AdvisoryType.weather:
        return 'الطقس';
      case AdvisoryType.general:
        return 'عام';
    }
  }

  Future<void> _refreshList() async {
    await ref.read(advisoryHistoryProvider.notifier).refresh(
      fieldId: widget.fieldId,
    );
  }

  void _markAsApplied(String advisoryId) {
    ref.read(advisoriesProvider.notifier).updateAdvisoryStatus(advisoryId, AdvisoryStatus.applied);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم تعيين التوصية كمطبقة'),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _dismissAdvisory(String advisoryId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تجاهل التوصية'),
        content: const Text('هل أنت متأكد من تجاهل هذه التوصية؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ref.read(advisoriesProvider.notifier).updateAdvisoryStatus(advisoryId, AdvisoryStatus.dismissed);

              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('تم تجاهل التوصية'),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange,
            ),
            child: const Text('تجاهل'),
          ),
        ],
      ),
    );
  }
}
