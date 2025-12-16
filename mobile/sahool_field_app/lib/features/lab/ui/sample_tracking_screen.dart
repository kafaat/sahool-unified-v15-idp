import 'package:flutter/material.dart';

/// شاشة تتبع العينات
/// Sample Tracking Screen - يعرض رحلة العينة من الحقل للمختبر
class SampleTrackingScreen extends StatefulWidget {
  const SampleTrackingScreen({super.key});

  @override
  State<SampleTrackingScreen> createState() => _SampleTrackingScreenState();
}

class _SampleTrackingScreenState extends State<SampleTrackingScreen> {
  String _selectedFilter = 'all';

  // Demo samples data
  final List<LabSample> _samples = [
    LabSample(
      id: '1',
      barcode: 'SOIL-0001',
      type: 'تربة',
      status: SampleStatus.inTransit,
      experimentName: 'تجربة القمح',
      plotCode: 'B-01',
      collectedAt: DateTime.now().subtract(const Duration(days: 2)),
      collectedBy: 'أحمد الراشد',
    ),
    LabSample(
      id: '2',
      barcode: 'SOIL-0002',
      type: 'تربة',
      status: SampleStatus.received,
      experimentName: 'تجربة القمح',
      plotCode: 'B-02',
      collectedAt: DateTime.now().subtract(const Duration(days: 3)),
      collectedBy: 'أحمد الراشد',
    ),
    LabSample(
      id: '3',
      barcode: 'LEAF-0001',
      type: 'أوراق',
      status: SampleStatus.processing,
      experimentName: 'تجربة الطماطم',
      plotCode: 'A-05',
      collectedAt: DateTime.now().subtract(const Duration(days: 5)),
      collectedBy: 'محمد علي',
    ),
    LabSample(
      id: '4',
      barcode: 'WATER-0001',
      type: 'ماء',
      status: SampleStatus.analyzed,
      experimentName: 'تجربة الري',
      plotCode: 'C-01',
      collectedAt: DateTime.now().subtract(const Duration(days: 7)),
      collectedBy: 'د. فاطمة حسن',
      results: {'pH': 7.2, 'EC': 1.5, 'TDS': 980},
    ),
    LabSample(
      id: '5',
      barcode: 'SOIL-0003',
      type: 'تربة',
      status: SampleStatus.pending,
      experimentName: 'تجربة القمح',
      plotCode: 'B-03',
      collectedAt: DateTime.now().subtract(const Duration(hours: 5)),
      collectedBy: 'أحمد الراشد',
    ),
  ];

  List<LabSample> get _filteredSamples {
    if (_selectedFilter == 'all') return _samples;
    return _samples.where((s) => s.status.name == _selectedFilter).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تتبع العينات 🧪'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.qr_code_scanner),
            onPressed: _scanBarcode,
          ),
        ],
      ),
      body: Column(
        children: [
          // Stats Summary
          _buildStatsSummary(),

          // Filter Chips
          _buildFilterChips(),

          // Samples List
          Expanded(
            child: _filteredSamples.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _filteredSamples.length,
                    itemBuilder: (context, index) {
                      return _SampleCard(
                        sample: _filteredSamples[index],
                        onTap: () => _showSampleDetails(_filteredSamples[index]),
                      );
                    },
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const NewSampleScreen(),
            ),
          );
        },
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text('عينة جديدة'),
      ),
    );
  }

  Widget _buildStatsSummary() {
    final stats = {
      'pending': _samples.where((s) => s.status == SampleStatus.pending).length,
      'inTransit': _samples.where((s) => s.status == SampleStatus.inTransit).length,
      'received': _samples.where((s) => s.status == SampleStatus.received).length,
      'processing': _samples.where((s) => s.status == SampleStatus.processing).length,
      'analyzed': _samples.where((s) => s.status == SampleStatus.analyzed).length,
    };

    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.teal.shade50,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _MiniStat(label: 'انتظار', value: stats['pending']!, color: Colors.grey),
          _MiniStat(label: 'بالطريق', value: stats['inTransit']!, color: Colors.blue),
          _MiniStat(label: 'وصلت', value: stats['received']!, color: Colors.orange),
          _MiniStat(label: 'تحليل', value: stats['processing']!, color: Colors.purple),
          _MiniStat(label: 'مكتمل', value: stats['analyzed']!, color: Colors.green),
        ],
      ),
    );
  }

  Widget _buildFilterChips() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          _FilterChip(
            label: 'الكل',
            value: 'all',
            selected: _selectedFilter == 'all',
            onSelected: () => setState(() => _selectedFilter = 'all'),
          ),
          _FilterChip(
            label: '⏳ انتظار',
            value: 'pending',
            selected: _selectedFilter == 'pending',
            onSelected: () => setState(() => _selectedFilter = 'pending'),
          ),
          _FilterChip(
            label: '🚚 بالطريق',
            value: 'inTransit',
            selected: _selectedFilter == 'inTransit',
            onSelected: () => setState(() => _selectedFilter = 'inTransit'),
          ),
          _FilterChip(
            label: '📥 وصلت',
            value: 'received',
            selected: _selectedFilter == 'received',
            onSelected: () => setState(() => _selectedFilter = 'received'),
          ),
          _FilterChip(
            label: '🔬 تحليل',
            value: 'processing',
            selected: _selectedFilter == 'processing',
            onSelected: () => setState(() => _selectedFilter = 'processing'),
          ),
          _FilterChip(
            label: '✅ مكتمل',
            value: 'analyzed',
            selected: _selectedFilter == 'analyzed',
            onSelected: () => setState(() => _selectedFilter = 'analyzed'),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.science_outlined, size: 64, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            'لا توجد عينات',
            style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
          ),
        ],
      ),
    );
  }

  void _scanBarcode() {
    // TODO: Implement barcode scanner
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('ماسح الباركود - قيد التطوير')),
    );
  }

  void _showSampleDetails(LabSample sample) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => _SampleDetailsSheet(sample: sample),
    );
  }
}

class _MiniStat extends StatelessWidget {
  final String label;
  final int value;
  final Color color;

  const _MiniStat({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              '$value',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
                fontSize: 16,
              ),
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey.shade700,
          ),
        ),
      ],
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final String value;
  final bool selected;
  final VoidCallback onSelected;

  const _FilterChip({
    required this.label,
    required this.value,
    required this.selected,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 8),
      child: FilterChip(
        label: Text(label),
        selected: selected,
        onSelected: (_) => onSelected(),
        selectedColor: Colors.teal.shade100,
        checkmarkColor: Colors.teal,
        labelStyle: TextStyle(
          color: selected ? Colors.teal.shade800 : Colors.grey.shade700,
          fontWeight: selected ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }
}

class _SampleCard extends StatelessWidget {
  final LabSample sample;
  final VoidCallback onTap;

  const _SampleCard({
    required this.sample,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final statusConfig = _getStatusConfig(sample.status);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      sample.barcode,
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.teal.shade50,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      sample.type,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.teal.shade700,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: statusConfig.color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(statusConfig.icon),
                        const SizedBox(width: 4),
                        Text(
                          statusConfig.label,
                          style: TextStyle(
                            fontSize: 12,
                            color: statusConfig.color,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Experiment & Plot
              Row(
                children: [
                  Icon(Icons.science, size: 16, color: Colors.grey.shade600),
                  const SizedBox(width: 4),
                  Text(
                    sample.experimentName,
                    style: TextStyle(color: Colors.grey.shade700),
                  ),
                  const SizedBox(width: 16),
                  Icon(Icons.grid_view, size: 16, color: Colors.grey.shade600),
                  const SizedBox(width: 4),
                  Text(
                    'القطعة ${sample.plotCode}',
                    style: TextStyle(color: Colors.grey.shade700),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              // Collection info
              Row(
                children: [
                  Icon(Icons.person_outline, size: 16, color: Colors.grey.shade500),
                  const SizedBox(width: 4),
                  Text(
                    sample.collectedBy,
                    style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                  ),
                  const Spacer(),
                  Icon(Icons.access_time, size: 16, color: Colors.grey.shade500),
                  const SizedBox(width: 4),
                  Text(
                    _formatTimeAgo(sample.collectedAt),
                    style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                  ),
                ],
              ),

              // Results preview if analyzed
              if (sample.status == SampleStatus.analyzed && sample.results != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.check_circle, color: Colors.green, size: 20),
                      const SizedBox(width: 8),
                      const Text('نتائج متاحة', style: TextStyle(color: Colors.green)),
                      const Spacer(),
                      Text(
                        'عرض النتائج ←',
                        style: TextStyle(
                          color: Colors.green.shade700,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  _StatusConfig _getStatusConfig(SampleStatus status) {
    switch (status) {
      case SampleStatus.pending:
        return _StatusConfig('انتظار', '⏳', Colors.grey);
      case SampleStatus.inTransit:
        return _StatusConfig('بالطريق', '🚚', Colors.blue);
      case SampleStatus.received:
        return _StatusConfig('وصلت', '📥', Colors.orange);
      case SampleStatus.processing:
        return _StatusConfig('تحليل', '🔬', Colors.purple);
      case SampleStatus.analyzed:
        return _StatusConfig('مكتمل', '✅', Colors.green);
    }
  }

  String _formatTimeAgo(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inDays > 0) return 'منذ ${diff.inDays} يوم';
    if (diff.inHours > 0) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inMinutes} دقيقة';
  }
}

class _StatusConfig {
  final String label;
  final String icon;
  final Color color;
  _StatusConfig(this.label, this.icon, this.color);
}

class _SampleDetailsSheet extends StatelessWidget {
  final LabSample sample;

  const _SampleDetailsSheet({required this.sample});

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      maxChildSize: 0.9,
      minChildSize: 0.5,
      expand: false,
      builder: (context, scrollController) {
        return SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Handle
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Barcode
              Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    sample.barcode,
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Timeline
              const Text(
                'رحلة العينة',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              _buildTimeline(),

              // Results
              if (sample.status == SampleStatus.analyzed && sample.results != null) ...[
                const SizedBox(height: 24),
                const Text(
                  'نتائج التحليل',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                _buildResultsTable(),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _buildTimeline() {
    final steps = [
      {'label': 'جمع العينة', 'icon': Icons.handshake, 'done': true},
      {'label': 'إرسال للمختبر', 'icon': Icons.local_shipping, 'done': sample.status.index >= 1},
      {'label': 'استلام المختبر', 'icon': Icons.inventory, 'done': sample.status.index >= 2},
      {'label': 'قيد التحليل', 'icon': Icons.science, 'done': sample.status.index >= 3},
      {'label': 'اكتمال التحليل', 'icon': Icons.check_circle, 'done': sample.status.index >= 4},
    ];

    return Column(
      children: steps.asMap().entries.map((entry) {
        final index = entry.key;
        final step = entry.value;
        final isLast = index == steps.length - 1;
        final isDone = step['done'] as bool;

        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Column(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: isDone ? Colors.green : Colors.grey.shade300,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    step['icon'] as IconData,
                    color: Colors.white,
                    size: 18,
                  ),
                ),
                if (!isLast)
                  Container(
                    width: 2,
                    height: 40,
                    color: isDone ? Colors.green : Colors.grey.shade300,
                  ),
              ],
            ),
            const SizedBox(width: 12),
            Padding(
              padding: const EdgeInsets.only(top: 6),
              child: Text(
                step['label'] as String,
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: isDone ? FontWeight.bold : FontWeight.normal,
                  color: isDone ? Colors.black : Colors.grey,
                ),
              ),
            ),
          ],
        );
      }).toList(),
    );
  }

  Widget _buildResultsTable() {
    if (sample.results == null) return const SizedBox();

    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Column(
        children: sample.results!.entries.map((entry) {
          return ListTile(
            title: Text(entry.key),
            trailing: Text(
              '${entry.value}',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

// ============ Models ============

enum SampleStatus {
  pending,
  inTransit,
  received,
  processing,
  analyzed,
}

class LabSample {
  final String id;
  final String barcode;
  final String type;
  final SampleStatus status;
  final String experimentName;
  final String plotCode;
  final DateTime collectedAt;
  final String collectedBy;
  final Map<String, dynamic>? results;

  LabSample({
    required this.id,
    required this.barcode,
    required this.type,
    required this.status,
    required this.experimentName,
    required this.plotCode,
    required this.collectedAt,
    required this.collectedBy,
    this.results,
  });
}

// ============ New Sample Screen ============

class NewSampleScreen extends StatefulWidget {
  const NewSampleScreen({super.key});

  @override
  State<NewSampleScreen> createState() => _NewSampleScreenState();
}

class _NewSampleScreenState extends State<NewSampleScreen> {
  final _formKey = GlobalKey<FormState>();
  String _selectedType = 'تربة';
  String _selectedExperiment = 'تجربة القمح';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('عينة جديدة 🧪'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Sample Type
              const Text('نوع العينة', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: ['تربة', 'أوراق', 'ماء', 'ثمار', 'بذور'].map((type) {
                  return ChoiceChip(
                    label: Text(type),
                    selected: _selectedType == type,
                    onSelected: (selected) {
                      if (selected) setState(() => _selectedType = type);
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),

              // Experiment Selection
              DropdownButtonFormField<String>(
                value: _selectedExperiment,
                decoration: const InputDecoration(
                  labelText: 'التجربة',
                  border: OutlineInputBorder(),
                ),
                items: ['تجربة القمح', 'تجربة الطماطم', 'تجربة الري']
                    .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                    .toList(),
                onChanged: (value) => setState(() => _selectedExperiment = value!),
              ),
              const SizedBox(height: 16),

              // Plot Selection
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: 'القطعة التجريبية',
                  border: OutlineInputBorder(),
                ),
                items: ['B-01', 'B-02', 'B-03', 'A-01', 'C-01']
                    .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                    .toList(),
                onChanged: (value) {},
              ),
              const SizedBox(height: 16),

              // Notes
              TextFormField(
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'ملاحظات',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 32),

              // Submit Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton.icon(
                  onPressed: () {
                    // Generate barcode and save
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('✅ تم إنشاء العينة وتوليد الباركود'),
                        backgroundColor: Colors.green,
                      ),
                    );
                    Navigator.pop(context);
                  },
                  icon: const Icon(Icons.qr_code),
                  label: const Text('إنشاء العينة'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.teal,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
