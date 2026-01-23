/// SAHOOL Super Home Screen v16
/// الشاشة الرئيسية المحسنة

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'state/home_controller.dart';

class HomeV16Screen extends ConsumerWidget {
  const HomeV16Screen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(homeControllerProvider);

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: () => ref.read(homeControllerProvider.notifier).refresh(),
        child: CustomScrollView(
          slivers: [
            // App Bar
            SliverAppBar(
              pinned: true,
              expandedHeight: 140,
              title: const Text("الموجز اليومي"),
              flexibleSpace: FlexibleSpaceBar(
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Theme.of(context).primaryColor,
                        Theme.of(context).primaryColor.withOpacity(0.8),
                      ],
                    ),
                  ),
                  child: SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.fromLTRB(16, 60, 16, 16),
                      child: Text(
                        state.error != null
                            ? "⚠️ ${state.error}"
                            : "مرحباً، جاهز للعمل اليوم",
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),

            // Content
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _KpiGrid(
                      ndvi: state.ndviAvg,
                      alerts: state.alertsOpen,
                      tasks: state.tasksDue,
                      weather: state.weatherSummary,
                      loading: state.loading,
                    ),
                    const SizedBox(height: 20),
                    const _QuickActions(),
                    const SizedBox(height: 20),
                    _AlertsPreview(
                      loading: state.loading,
                      alertsCount: state.alertsOpen,
                    ),
                    const SizedBox(height: 20),
                    _FieldsPreview(fieldsCount: state.fieldsCount),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// KPI Grid Widget
// ═══════════════════════════════════════════════════════════════

class _KpiGrid extends StatelessWidget {
  final double ndvi;
  final int alerts;
  final int tasks;
  final String weather;
  final bool loading;

  const _KpiGrid({
    required this.ndvi,
    required this.alerts,
    required this.tasks,
    required this.weather,
    required this.loading,
  });

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const SizedBox(
        height: 180,
        child: Center(child: CircularProgressIndicator()),
      );
    }

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.6,
      children: [
        _KpiCard(
          title: "NDVI متوسط",
          value: ndvi.toStringAsFixed(2),
          icon: Icons.eco,
          color: Colors.green,
        ),
        _KpiCard(
          title: "تنبيهات مفتوحة",
          value: "$alerts",
          icon: Icons.warning_amber,
          color: Colors.orange,
        ),
        _KpiCard(
          title: "مهام مستحقة",
          value: "$tasks",
          icon: Icons.checklist,
          color: Colors.blue,
        ),
        _KpiCard(
          title: "الطقس",
          value: weather,
          icon: Icons.wb_sunny,
          color: Colors.amber,
        ),
      ],
    );
  }
}

class _KpiCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _KpiCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Icon(icon, color: color, size: 24),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: color.withOpacity(0.9),
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              Text(
                title,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// Quick Actions Widget
// ═══════════════════════════════════════════════════════════════

class _QuickActions extends StatelessWidget {
  const _QuickActions();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "إجراءات سريعة",
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            _ActionButton(label: "حقولي", icon: Icons.map, onTap: () {}),
            const SizedBox(width: 12),
            _ActionButton(label: "NDVI", icon: Icons.show_chart, onTap: () {}),
            const SizedBox(width: 12),
            _ActionButton(label: "المهام", icon: Icons.checklist, onTap: () {}),
            const SizedBox(width: 12),
            _ActionButton(label: "الري", icon: Icons.water_drop, onTap: () {}),
          ],
        ),
      ],
    );
  }
}

class _ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final VoidCallback onTap;

  const _ActionButton({
    required this.label,
    required this.icon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Icon(icon, color: Theme.of(context).primaryColor),
              const SizedBox(height: 4),
              Text(label, style: const TextStyle(fontSize: 12)),
            ],
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// Alerts Preview Widget
// ═══════════════════════════════════════════════════════════════

class _AlertsPreview extends StatelessWidget {
  final bool loading;
  final int alertsCount;

  const _AlertsPreview({required this.loading, required this.alertsCount});

  @override
  Widget build(BuildContext context) {
    if (loading || alertsCount == 0) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.red[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber, color: Colors.red[700], size: 20),
              const SizedBox(width: 8),
              Text(
                "أهم التنبيهات",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.red[700],
                ),
              ),
              const Spacer(),
              Text(
                "$alertsCount تنبيهات",
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.red[600],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text("• انخفاض NDVI في الحقل 12"),
          const SizedBox(height: 4),
          const Text("• موعد ري مستحق لقطاع Zone A"),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// Fields Preview Widget
// ═══════════════════════════════════════════════════════════════

class _FieldsPreview extends StatelessWidget {
  final int fieldsCount;

  const _FieldsPreview({required this.fieldsCount});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              "حقولي ($fieldsCount)",
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            TextButton(onPressed: () {}, child: const Text("عرض الكل")),
          ],
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 120,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: fieldsCount > 5 ? 5 : fieldsCount,
            itemBuilder: (context, index) {
              return Container(
                width: 140,
                margin: const EdgeInsets.only(left: 12),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey[200]!),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.1),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text("حقل ${index + 1}",
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text(
                      "قمح",
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                    const Spacer(),
                    Row(
                      children: [
                        Icon(Icons.eco, size: 14, color: Colors.green[600]),
                        const SizedBox(width: 4),
                        Text(
                          "0.${60 + index}",
                          style: TextStyle(
                            color: Colors.green[700],
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
