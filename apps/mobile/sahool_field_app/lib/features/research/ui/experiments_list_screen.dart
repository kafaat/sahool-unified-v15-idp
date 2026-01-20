import 'package:flutter/material.dart';

/// شاشة قائمة التجارب البحثية
/// Experiments List Screen
class ExperimentsListScreen extends StatefulWidget {
  const ExperimentsListScreen({super.key});

  @override
  State<ExperimentsListScreen> createState() => _ExperimentsListScreenState();
}

class _ExperimentsListScreenState extends State<ExperimentsListScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _searchQuery = '';

  // Demo data
  final List<Experiment> _experiments = [
    Experiment(
      id: '1',
      title: 'تجربة أصناف القمح المقاومة للجفاف',
      titleEn: 'Drought-Resistant Wheat Varieties Trial',
      status: ExperimentStatus.active,
      plotsCount: 15,
      startDate: DateTime(2025, 1, 1),
      principalResearcher: 'د. فاطمة حسن',
      progress: 0.45,
    ),
    Experiment(
      id: '2',
      title: 'تجربة تقنيات الري الذكي',
      titleEn: 'Smart Irrigation Techniques Trial',
      status: ExperimentStatus.active,
      plotsCount: 8,
      startDate: DateTime(2025, 1, 15),
      principalResearcher: 'أحمد الراشد',
      progress: 0.30,
    ),
    Experiment(
      id: '3',
      title: 'تجربة الأسمدة العضوية',
      titleEn: 'Organic Fertilizers Trial',
      status: ExperimentStatus.draft,
      plotsCount: 12,
      startDate: DateTime(2025, 2, 1),
      principalResearcher: 'د. فاطمة حسن',
      progress: 0.0,
    ),
    Experiment(
      id: '4',
      title: 'تجربة مقاومة الآفات الطبيعية',
      titleEn: 'Natural Pest Resistance Trial',
      status: ExperimentStatus.completed,
      plotsCount: 10,
      startDate: DateTime(2024, 6, 1),
      principalResearcher: 'محمد علي',
      progress: 1.0,
    ),
  ];

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

  List<Experiment> _getFilteredExperiments(ExperimentStatus? status) {
    if (status == null) return _experiments;
    return _experiments.where((e) => e.status == status).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('التجارب البحثية 🔬'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          tabs: const [
            Tab(text: 'الكل'),
            Tab(text: 'نشطة'),
            Tab(text: 'مكتملة'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => _showSearch(context),
          ),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildExperimentsList(null),
          _buildExperimentsList(ExperimentStatus.active),
          _buildExperimentsList(ExperimentStatus.completed),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _navigateToCreateExperiment,
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text('تجربة جديدة'),
      ),
    );
  }

  Widget _buildExperimentsList(ExperimentStatus? status) {
    final experiments = _getFilteredExperiments(status);

    if (experiments.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.science_outlined, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              'لا توجد تجارب',
              style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: experiments.length,
      itemBuilder: (context, index) {
        return _ExperimentCard(
          experiment: experiments[index],
          onTap: () => _navigateToExperiment(experiments[index]),
        );
      },
    );
  }

  void _navigateToExperiment(Experiment experiment) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ExperimentDetailsScreen(experiment: experiment),
      ),
    );
  }

  void _showSearch(BuildContext context) {
    showSearch(
      context: context,
      delegate: _ExperimentsSearchDelegate(
        experiments: _experiments,
        onExperimentSelected: _navigateToExperiment,
      ),
    );
  }

  void _navigateToCreateExperiment() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const ExperimentFormScreen(),
      ),
    ).then((result) {
      if (result != null && result is Experiment) {
        setState(() {
          _experiments.add(result);
        });
      }
    });
  }
}

/// بطاقة التجربة
class _ExperimentCard extends StatelessWidget {
  final Experiment experiment;
  final VoidCallback onTap;

  const _ExperimentCard({
    required this.experiment,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 2,
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
                  _StatusBadge(status: experiment.status),
                  const Spacer(),
                  Text(
                    '${experiment.plotsCount} قطعة',
                    style: TextStyle(
                      color: Colors.grey.shade600,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Title
              Text(
                experiment.title,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                experiment.titleEn,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 12),

              // Info Row
              Row(
                children: [
                  Icon(Icons.person_outline, size: 16, color: Colors.grey.shade600),
                  const SizedBox(width: 4),
                  Text(
                    experiment.principalResearcher,
                    style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                  ),
                  const SizedBox(width: 16),
                  Icon(Icons.calendar_today, size: 16, color: Colors.grey.shade600),
                  const SizedBox(width: 4),
                  Text(
                    _formatDate(experiment.startDate),
                    style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Progress
              if (experiment.status == ExperimentStatus.active) ...[
                Row(
                  children: [
                    Expanded(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: experiment.progress,
                          backgroundColor: Colors.grey.shade200,
                          valueColor: const AlwaysStoppedAnimation<Color>(Colors.indigo),
                          minHeight: 6,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '${(experiment.progress * 100).toInt()}%',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.indigo,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year}/${date.month}/${date.day}';
  }
}

/// شارة الحالة
class _StatusBadge extends StatelessWidget {
  final ExperimentStatus status;

  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    final config = _getStatusConfig();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: config.color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: config.color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(config.icon),
          const SizedBox(width: 4),
          Text(
            config.label,
            style: TextStyle(
              color: config.color,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  _StatusConfig _getStatusConfig() {
    switch (status) {
      case ExperimentStatus.draft:
        return _StatusConfig('مسودة', '📝', Colors.grey);
      case ExperimentStatus.active:
        return _StatusConfig('نشطة', '🔬', Colors.green);
      case ExperimentStatus.paused:
        return _StatusConfig('متوقفة', '⏸️', Colors.orange);
      case ExperimentStatus.completed:
        return _StatusConfig('مكتملة', '✅', Colors.blue);
      case ExperimentStatus.locked:
        return _StatusConfig('مقفلة', '🔒', Colors.red);
    }
  }
}

class _StatusConfig {
  final String label;
  final String icon;
  final Color color;

  _StatusConfig(this.label, this.icon, this.color);
}

/// شاشة تفاصيل التجربة
class ExperimentDetailsScreen extends StatefulWidget {
  final Experiment experiment;

  const ExperimentDetailsScreen({super.key, required this.experiment});

  @override
  State<ExperimentDetailsScreen> createState() => _ExperimentDetailsScreenState();
}

class _ExperimentDetailsScreenState extends State<ExperimentDetailsScreen> {
  late Experiment _experiment;

  @override
  void initState() {
    super.initState();
    _experiment = widget.experiment;
  }

  void _navigateToEditExperiment() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ExperimentFormScreen(experiment: _experiment),
      ),
    ).then((result) {
      if (result != null && result is Experiment) {
        setState(() {
          _experiment = result;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل التجربة'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        actions: [
          if (_experiment.status == ExperimentStatus.active ||
              _experiment.status == ExperimentStatus.draft)
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: _navigateToEditExperiment,
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title Card
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _StatusBadge(status: _experiment.status),
                    const SizedBox(height: 16),
                    Text(
                      _experiment.title,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _experiment.titleEn,
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Quick Actions
            _buildQuickActions(context),
            const SizedBox(height: 16),

            // Stats Grid
            _buildStatsGrid(),
            const SizedBox(height: 16),

            // Plots Section
            _buildPlotsSection(context),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _ActionButton(
            icon: Icons.note_add,
            label: 'تسجيل ملاحظة',
            color: Colors.green,
            onTap: () {
              // Navigate to researcher task screen
            },
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _ActionButton(
            icon: Icons.science,
            label: 'أخذ عينة',
            color: Colors.blue,
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const SampleCollectionScreen(),
                ),
              );
            },
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _ActionButton(
            icon: Icons.bar_chart,
            label: 'التقارير',
            color: Colors.purple,
            onTap: () {},
          ),
        ),
      ],
    );
  }

  Widget _buildStatsGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: [
        _StatCard(
          title: 'القطع التجريبية',
          value: '${_experiment.plotsCount}',
          icon: Icons.grid_view,
          color: Colors.indigo,
        ),
        _StatCard(
          title: 'الملاحظات',
          value: '48',
          icon: Icons.note,
          color: Colors.green,
        ),
        _StatCard(
          title: 'العينات',
          value: '24',
          icon: Icons.science,
          color: Colors.blue,
        ),
        _StatCard(
          title: 'أيام التجربة',
          value: '${DateTime.now().difference(_experiment.startDate).inDays}',
          icon: Icons.calendar_today,
          color: Colors.orange,
        ),
      ],
    );
  }

  Widget _buildPlotsSection(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'القطع التجريبية',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            TextButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const PlotsMapScreen(),
                  ),
                );
              },
              child: const Text('عرض الخريطة'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Demo plots list
        ...List.generate(3, (index) => _PlotListItem(
          plotCode: 'B-${(index + 1).toString().padLeft(2, '0')}',
          treatmentCode: 'T${index + 1}',
          lastObservation: DateTime.now().subtract(Duration(days: index)),
        )),
      ],
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: color.withOpacity(0.1),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const Spacer(),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PlotListItem extends StatelessWidget {
  final String plotCode;
  final String treatmentCode;
  final DateTime lastObservation;

  const _PlotListItem({
    required this.plotCode,
    required this.treatmentCode,
    required this.lastObservation,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        leading: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: Colors.indigo.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(Icons.grid_view, color: Colors.indigo),
        ),
        title: Text(
          'القطعة $plotCode',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text('المعاملة: $treatmentCode'),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            const Text('آخر رصد', style: TextStyle(fontSize: 11)),
            Text(
              'منذ ${DateTime.now().difference(lastObservation).inDays} يوم',
              style: const TextStyle(
                color: Colors.indigo,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
          ],
        ),
        onTap: () {
          // Navigate to plot details
        },
      ),
    );
  }
}

// ============ Search Delegate ============

class _ExperimentsSearchDelegate extends SearchDelegate<String> {
  final List<Experiment> experiments;
  final Function(Experiment) onExperimentSelected;

  _ExperimentsSearchDelegate({
    required this.experiments,
    required this.onExperimentSelected,
  });

  @override
  String get searchFieldLabel => 'البحث في التجارب...';

  @override
  List<Widget> buildActions(BuildContext context) {
    return [
      IconButton(
        icon: const Icon(Icons.clear),
        onPressed: () => query = '',
      ),
    ];
  }

  @override
  Widget buildLeading(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.arrow_back),
      onPressed: () => close(context, ''),
    );
  }

  List<Experiment> _getFilteredExperiments() {
    if (query.isEmpty) return experiments;
    final queryLower = query.toLowerCase();
    return experiments.where((e) {
      return e.title.toLowerCase().contains(queryLower) ||
          e.titleEn.toLowerCase().contains(queryLower) ||
          e.principalResearcher.toLowerCase().contains(queryLower);
    }).toList();
  }

  @override
  Widget buildResults(BuildContext context) {
    final filteredExperiments = _getFilteredExperiments();
    return _buildExperimentsList(filteredExperiments, context);
  }

  @override
  Widget buildSuggestions(BuildContext context) {
    final filteredExperiments = _getFilteredExperiments();
    return _buildExperimentsList(filteredExperiments, context);
  }

  Widget _buildExperimentsList(List<Experiment> filteredExperiments, BuildContext context) {
    if (filteredExperiments.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              query.isEmpty ? 'ابدأ البحث' : 'لا توجد نتائج',
              style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: filteredExperiments.length,
      itemBuilder: (context, index) {
        final experiment = filteredExperiments[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: ListTile(
            contentPadding: const EdgeInsets.all(12),
            leading: Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: Colors.indigo.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.science, color: Colors.indigo),
            ),
            title: Text(
              experiment.title,
              style: const TextStyle(fontWeight: FontWeight.bold),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  experiment.titleEn,
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  experiment.principalResearcher,
                  style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                ),
              ],
            ),
            trailing: _buildStatusChip(experiment.status),
            onTap: () {
              close(context, '');
              onExperimentSelected(experiment);
            },
          ),
        );
      },
    );
  }

  Widget _buildStatusChip(ExperimentStatus status) {
    Color color;
    String label;
    switch (status) {
      case ExperimentStatus.draft:
        color = Colors.grey;
        label = 'مسودة';
        break;
      case ExperimentStatus.active:
        color = Colors.green;
        label = 'نشطة';
        break;
      case ExperimentStatus.paused:
        color = Colors.orange;
        label = 'متوقفة';
        break;
      case ExperimentStatus.completed:
        color = Colors.blue;
        label = 'مكتملة';
        break;
      case ExperimentStatus.locked:
        color = Colors.red;
        label = 'مقفلة';
        break;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

// ============ Experiment Form Screen ============

/// شاشة إنشاء/تعديل التجربة
class ExperimentFormScreen extends StatefulWidget {
  final Experiment? experiment;

  const ExperimentFormScreen({super.key, this.experiment});

  @override
  State<ExperimentFormScreen> createState() => _ExperimentFormScreenState();
}

class _ExperimentFormScreenState extends State<ExperimentFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _titleEnController = TextEditingController();
  final _principalResearcherController = TextEditingController();
  final _plotsCountController = TextEditingController();

  ExperimentStatus _selectedStatus = ExperimentStatus.draft;
  DateTime _startDate = DateTime.now();
  bool _isSubmitting = false;

  bool get isEditing => widget.experiment != null;

  @override
  void initState() {
    super.initState();
    if (widget.experiment != null) {
      _titleController.text = widget.experiment!.title;
      _titleEnController.text = widget.experiment!.titleEn;
      _principalResearcherController.text = widget.experiment!.principalResearcher;
      _plotsCountController.text = widget.experiment!.plotsCount.toString();
      _selectedStatus = widget.experiment!.status;
      _startDate = widget.experiment!.startDate;
    }
  }

  @override
  void dispose() {
    _titleController.dispose();
    _titleEnController.dispose();
    _principalResearcherController.dispose();
    _plotsCountController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(isEditing ? 'تعديل التجربة' : 'تجربة جديدة'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        actions: [
          if (isEditing)
            IconButton(
              icon: const Icon(Icons.delete_outline),
              onPressed: _showDeleteConfirmation,
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // عنوان التجربة بالعربية
              _buildSectionTitle('عنوان التجربة'),
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(
                  hintText: 'أدخل عنوان التجربة بالعربية',
                  prefixIcon: Icon(Icons.title),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'الرجاء إدخال عنوان التجربة';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // عنوان التجربة بالإنجليزية
              _buildSectionTitle('العنوان بالإنجليزية'),
              TextFormField(
                controller: _titleEnController,
                decoration: const InputDecoration(
                  hintText: 'Enter experiment title in English',
                  prefixIcon: Icon(Icons.translate),
                ),
                textDirection: TextDirection.ltr,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'الرجاء إدخال العنوان بالإنجليزية';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // الباحث الرئيسي
              _buildSectionTitle('الباحث الرئيسي'),
              TextFormField(
                controller: _principalResearcherController,
                decoration: const InputDecoration(
                  hintText: 'اسم الباحث الرئيسي',
                  prefixIcon: Icon(Icons.person),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'الرجاء إدخال اسم الباحث';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // عدد القطع التجريبية
              _buildSectionTitle('عدد القطع التجريبية'),
              TextFormField(
                controller: _plotsCountController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  hintText: 'عدد القطع',
                  prefixIcon: Icon(Icons.grid_view),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'الرجاء إدخال عدد القطع';
                  }
                  if (int.tryParse(value) == null || int.parse(value) <= 0) {
                    return 'الرجاء إدخال رقم صحيح';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // حالة التجربة
              _buildSectionTitle('حالة التجربة'),
              DropdownButtonFormField<ExperimentStatus>(
                value: _selectedStatus,
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.flag),
                ),
                items: ExperimentStatus.values.map((status) {
                  return DropdownMenuItem<ExperimentStatus>(
                    value: status,
                    child: Row(
                      children: [
                        Text(_getStatusEmoji(status)),
                        const SizedBox(width: 8),
                        Text(_getStatusLabel(status)),
                      ],
                    ),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() => _selectedStatus = value);
                  }
                },
              ),
              const SizedBox(height: 16),

              // تاريخ البدء
              _buildSectionTitle('تاريخ البدء'),
              InkWell(
                onTap: _selectStartDate,
                child: InputDecorator(
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.calendar_today),
                    suffixIcon: Icon(Icons.arrow_drop_down),
                  ),
                  child: Text(
                    '${_startDate.year}/${_startDate.month}/${_startDate.day}',
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // زر الحفظ
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isSubmitting ? null : _saveExperiment,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.indigo,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  icon: _isSubmitting
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : Icon(isEditing ? Icons.save : Icons.add),
                  label: Text(
                    _isSubmitting
                        ? 'جاري الحفظ...'
                        : (isEditing ? 'حفظ التغييرات' : 'إنشاء التجربة'),
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // زر الإلغاء
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: () => Navigator.pop(context),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text('إلغاء'),
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 16,
          color: Colors.indigo,
        ),
      ),
    );
  }

  Future<void> _selectStartDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _startDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(primary: Colors.indigo),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() => _startDate = picked);
    }
  }

  String _getStatusEmoji(ExperimentStatus status) {
    switch (status) {
      case ExperimentStatus.draft:
        return '📝';
      case ExperimentStatus.active:
        return '🔬';
      case ExperimentStatus.paused:
        return '⏸️';
      case ExperimentStatus.completed:
        return '✅';
      case ExperimentStatus.locked:
        return '🔒';
    }
  }

  String _getStatusLabel(ExperimentStatus status) {
    switch (status) {
      case ExperimentStatus.draft:
        return 'مسودة';
      case ExperimentStatus.active:
        return 'نشطة';
      case ExperimentStatus.paused:
        return 'متوقفة';
      case ExperimentStatus.completed:
        return 'مكتملة';
      case ExperimentStatus.locked:
        return 'مقفلة';
    }
  }

  void _saveExperiment() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isSubmitting = true);

    // Calculate progress based on status
    double progress;
    switch (_selectedStatus) {
      case ExperimentStatus.draft:
        progress = 0.0;
        break;
      case ExperimentStatus.completed:
        progress = 1.0;
        break;
      case ExperimentStatus.locked:
        progress = widget.experiment?.progress ?? 0.0;
        break;
      default:
        progress = widget.experiment?.progress ?? 0.1;
    }

    final experiment = Experiment(
      id: widget.experiment?.id ?? DateTime.now().millisecondsSinceEpoch.toString(),
      title: _titleController.text,
      titleEn: _titleEnController.text,
      status: _selectedStatus,
      plotsCount: int.parse(_plotsCountController.text),
      startDate: _startDate,
      principalResearcher: _principalResearcherController.text,
      progress: progress,
    );

    // Simulate saving delay
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(isEditing ? 'تم تحديث التجربة بنجاح' : 'تم إنشاء التجربة بنجاح'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, experiment);
      }
    });
  }

  void _showDeleteConfirmation() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف التجربة'),
        content: const Text('هل أنت متأكد من حذف هذه التجربة؟ لا يمكن التراجع عن هذا الإجراء.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context, 'deleted'); // Return to previous screen
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('حذف', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }
}

// ============ Models ============

enum ExperimentStatus {
  draft,
  active,
  paused,
  completed,
  locked,
}

class Experiment {
  final String id;
  final String title;
  final String titleEn;
  final ExperimentStatus status;
  final int plotsCount;
  final DateTime startDate;
  final String principalResearcher;
  final double progress;

  Experiment({
    required this.id,
    required this.title,
    required this.titleEn,
    required this.status,
    required this.plotsCount,
    required this.startDate,
    required this.principalResearcher,
    required this.progress,
  });
}

// ============ Placeholder Screens ============

class SampleCollectionScreen extends StatelessWidget {
  const SampleCollectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('جمع العينات 🧪'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: const Center(
        child: Text('شاشة جمع العينات - قيد التطوير'),
      ),
    );
  }
}

class PlotsMapScreen extends StatelessWidget {
  const PlotsMapScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('خريطة القطع 🗺️'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
      ),
      body: const Center(
        child: Text('خريطة القطع التجريبية - قيد التطوير'),
      ),
    );
  }
}
