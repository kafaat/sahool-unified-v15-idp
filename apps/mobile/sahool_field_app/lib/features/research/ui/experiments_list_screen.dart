import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/research_repository.dart';

/// شاشة قائمة التجارب البحثية - مربوطة بـ research-core API
/// Experiments List Screen - Connected to research-core service
class ExperimentsListScreen extends ConsumerStatefulWidget {
  const ExperimentsListScreen({super.key});

  @override
  ConsumerState<ExperimentsListScreen> createState() =>
      _ExperimentsListScreenState();
}

class _ExperimentsListScreenState extends ConsumerState<ExperimentsListScreen>
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

  List<Experiment> _getFilteredExperiments(
      List<Experiment> all, ExperimentStatus? status) {
    if (status == null) return all;
    return all.where((e) => e.status == status).toList();
  }

  @override
  Widget build(BuildContext context) {
    final experimentsAsync = ref.watch(experimentsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('التجارب البحثية'),
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
            onPressed: () {
              final experiments = experimentsAsync.valueOrNull ?? [];
              showSearch(
                context: context,
                delegate:
                    _ExperimentSearchDelegate(experiments: experiments),
              );
            },
          ),
        ],
      ),
      body: experimentsAsync.when(
        data: (experiments) => TabBarView(
          controller: _tabController,
          children: [
            _buildExperimentsList(experiments, null),
            _buildExperimentsList(experiments, ExperimentStatus.active),
            _buildExperimentsList(experiments, ExperimentStatus.completed),
          ],
        ),
        loading: () => const Center(
          child: CircularProgressIndicator(color: Colors.indigo),
        ),
        error: (error, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.cloud_off, size: 64, color: Colors.grey[400]),
              const SizedBox(height: 16),
              Text(
                error.toString(),
                style: TextStyle(color: Colors.grey[600]),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () => ref.invalidate(experimentsProvider),
                icon: const Icon(Icons.refresh),
                label: const Text('إعادة المحاولة'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.indigo,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _navigateToCreateExperiment(),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text('تجربة جديدة'),
      ),
    );
  }

  Widget _buildExperimentsList(
      List<Experiment> allExperiments, ExperimentStatus? status) {
    final experiments = _getFilteredExperiments(allExperiments, status);

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

    return RefreshIndicator(
      onRefresh: () => ref.refresh(experimentsProvider.future),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: experiments.length,
        itemBuilder: (context, index) {
          return _ExperimentCard(
            experiment: experiments[index],
            onTap: () => _navigateToExperiment(experiments[index]),
          );
        },
      ),
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

  Future<void> _navigateToCreateExperiment() async {
    final result = await Navigator.push<Experiment>(
      context,
      MaterialPageRoute(
        builder: (context) => const CreateExperimentScreen(),
      ),
    );

    // Refresh experiments list if a new experiment was created
    if (result != null && mounted) {
      ref.invalidate(experimentsProvider);
    }
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
        color: config.color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: config.color.withValues(alpha: 0.3)),
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
class ExperimentDetailsScreen extends StatelessWidget {
  final Experiment experiment;

  const ExperimentDetailsScreen({super.key, required this.experiment});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل التجربة'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        actions: [
          if (experiment.status == ExperimentStatus.active)
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () async {
                final result = await Navigator.push<Experiment>(
                  context,
                  MaterialPageRoute(
                    builder: (context) => EditExperimentScreen(experiment: experiment),
                  ),
                );
                // Handle result when returning - pop details screen if experiment was updated
                // to refresh the list with updated data
                if (result != null && context.mounted) {
                  Navigator.pop(context, result);
                }
              },
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
                    _StatusBadge(status: experiment.status),
                    const SizedBox(height: 16),
                    Text(
                      experiment.title,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      experiment.titleEn,
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
          value: '${experiment.plotsCount}',
          icon: Icons.grid_view,
          color: Colors.indigo,
        ),
        const _StatCard(
          title: 'الملاحظات',
          value: '48',
          icon: Icons.note,
          color: Colors.green,
        ),
        const _StatCard(
          title: 'العينات',
          value: '24',
          icon: Icons.science,
          color: Colors.blue,
        ),
        _StatCard(
          title: 'أيام التجربة',
          value: '${DateTime.now().difference(experiment.startDate).inDays}',
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
      color: color.withValues(alpha: 0.1),
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
            color: Colors.indigo.withValues(alpha: 0.1),
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

  factory Experiment.fromJson(Map<String, dynamic> json) {
    return Experiment(
      id: json['id'] as String,
      title: json['title'] as String? ?? '',
      titleEn: json['titleEn'] as String? ?? json['title'] as String? ?? '',
      status: _parseStatus(json['status'] as String?),
      plotsCount: json['plotsCount'] as int? ?? 0,
      startDate: json['startDate'] != null
          ? DateTime.parse(json['startDate'] as String)
          : DateTime.now(),
      principalResearcher: json['principalResearcher'] as String? ?? '',
      progress: (json['progress'] as num?)?.toDouble() ?? 0.0,
    );
  }

  static ExperimentStatus _parseStatus(String? status) {
    switch (status?.toLowerCase()) {
      case 'active':
        return ExperimentStatus.active;
      case 'paused':
        return ExperimentStatus.paused;
      case 'completed':
        return ExperimentStatus.completed;
      case 'locked':
        return ExperimentStatus.locked;
      default:
        return ExperimentStatus.draft;
    }
  }
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

/// مندوب البحث في التجارب
/// Experiment Search Delegate
class _ExperimentSearchDelegate extends SearchDelegate<Experiment?> {
  final List<Experiment> experiments;

  _ExperimentSearchDelegate({required this.experiments});

  @override
  String get searchFieldLabel => 'ابحث عن تجربة...';

  @override
  ThemeData appBarTheme(BuildContext context) {
    final theme = Theme.of(context);
    return theme.copyWith(
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
      ),
      inputDecorationTheme: const InputDecorationTheme(
        hintStyle: TextStyle(color: Colors.white70),
        border: InputBorder.none,
      ),
    );
  }

  @override
  List<Widget> buildActions(BuildContext context) {
    return [
      if (query.isNotEmpty)
        IconButton(
          icon: const Icon(Icons.clear),
          onPressed: () {
            query = '';
          },
        ),
    ];
  }

  @override
  Widget buildLeading(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.arrow_back),
      onPressed: () {
        close(context, null);
      },
    );
  }

  @override
  Widget buildResults(BuildContext context) {
    return _buildSearchResults(context);
  }

  @override
  Widget buildSuggestions(BuildContext context) {
    return _buildSearchResults(context);
  }

  Widget _buildSearchResults(BuildContext context) {
    final filteredExperiments = _filterExperiments(query);

    if (query.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              'ابحث بالاسم أو الوصف أو نوع المحصول',
              style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
            ),
          ],
        ),
      );
    }

    if (filteredExperiments.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              'لا توجد نتائج لـ "$query"',
              style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 8),
            Text(
              'جرّب كلمات بحث مختلفة',
              style: TextStyle(fontSize: 14, color: Colors.grey.shade500),
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
        return _SearchResultCard(
          experiment: experiment,
          query: query,
          onTap: () {
            close(context, experiment);
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) =>
                    ExperimentDetailsScreen(experiment: experiment),
              ),
            );
          },
        );
      },
    );
  }

  List<Experiment> _filterExperiments(String query) {
    if (query.isEmpty) return [];

    final lowerQuery = query.toLowerCase();
    return experiments.where((experiment) {
      // Search by Arabic title
      if (experiment.title.toLowerCase().contains(lowerQuery)) return true;
      // Search by English title
      if (experiment.titleEn.toLowerCase().contains(lowerQuery)) return true;
      // Search by principal researcher
      if (experiment.principalResearcher.toLowerCase().contains(lowerQuery)) {
        return true;
      }
      return false;
    }).toList();
  }
}

/// بطاقة نتيجة البحث
class _SearchResultCard extends StatelessWidget {
  final Experiment experiment;
  final String query;
  final VoidCallback onTap;

  const _SearchResultCard({
    required this.experiment,
    required this.query,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: Colors.indigo.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(Icons.science, color: Colors.indigo),
        ),
        title: Text(
          experiment.title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              experiment.titleEn,
              style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(Icons.person_outline, size: 14, color: Colors.grey.shade500),
                const SizedBox(width: 4),
                Text(
                  experiment.principalResearcher,
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
                ),
              ],
            ),
          ],
        ),
        trailing: _StatusBadge(status: experiment.status),
        onTap: onTap,
      ),
    );
  }
}

/// شاشة إنشاء تجربة جديدة
/// Create Experiment Screen
class CreateExperimentScreen extends StatelessWidget {
  const CreateExperimentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تجربة جديدة'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
      ),
      body: const Center(
        child: Text('شاشة إنشاء تجربة جديدة - قيد التطوير'),
      ),
    );
  }
}

/// شاشة تعديل التجربة
/// Edit Experiment Screen
class EditExperimentScreen extends StatelessWidget {
  final Experiment experiment;

  const EditExperimentScreen({super.key, required this.experiment});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تعديل التجربة'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            onPressed: () {
              // Return the updated experiment when saving
              // For now, return the original experiment as placeholder
              Navigator.pop(context, experiment);
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title field
            TextFormField(
              initialValue: experiment.title,
              decoration: const InputDecoration(
                labelText: 'عنوان التجربة (عربي)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: experiment.titleEn,
              decoration: const InputDecoration(
                labelText: 'Experiment Title (English)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: experiment.principalResearcher,
              decoration: const InputDecoration(
                labelText: 'الباحث الرئيسي',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: experiment.plotsCount.toString(),
              decoration: const InputDecoration(
                labelText: 'عدد القطع التجريبية',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  // Return the updated experiment
                  Navigator.pop(context, experiment);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.indigo,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('حفظ التغييرات'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
