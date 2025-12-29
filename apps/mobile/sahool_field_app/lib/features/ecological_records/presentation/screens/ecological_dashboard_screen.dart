import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';

/// شاشة لوحة السجلات الإيكولوجية
/// Ecological Records Dashboard Screen
class EcologicalDashboardScreen extends StatefulWidget {
  const EcologicalDashboardScreen({super.key});

  @override
  State<EcologicalDashboardScreen> createState() => _EcologicalDashboardScreenState();
}

class _EcologicalDashboardScreenState extends State<EcologicalDashboardScreen> {
  // بيانات تجريبية - سيتم استبدالها ببيانات من API
  final int speciesCount = 24;
  final double soilHealthScore = 78.5;
  final double waterEfficiency = 82.0;
  final int practicesCount = 12;
  final double overallEcologicalScore = 76.0;

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: SahoolColors.background,
        appBar: _buildAppBar(),
        body: RefreshIndicator(
          onRefresh: _refreshData,
          color: SahoolColors.primary,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Section
                _buildHeaderSection(),

                const SizedBox(height: 20),

                // Summary Cards Row
                _buildSummaryCards(),

                const SizedBox(height: 24),

                // Ecological Score Card
                _buildEcologicalScoreCard(),

                const SizedBox(height: 24),

                // Quick Actions Section
                _buildQuickActionsSection(),

                const SizedBox(height: 24),

                // Recent Records Section
                _buildRecentRecordsSection(),

                const SizedBox(height: 100),
              ],
            ),
          ),
        ),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      title: const Text(
        'السجلات الإيكولوجية',
        style: TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 22,
        ),
      ),
      backgroundColor: SahoolColors.primary,
      foregroundColor: Colors.white,
      elevation: 0,
      actions: [
        IconButton(
          icon: const Icon(Icons.filter_list, size: 26),
          onPressed: _showFilterOptions,
        ),
        const SizedBox(width: 4),
      ],
    );
  }

  Widget _buildHeaderSection() {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            SahoolColors.primary,
            SahoolColors.forestGreen,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Icon(
                  Icons.eco,
                  color: Colors.white,
                  size: 32,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'السجلات الإيكولوجية',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'تتبع ممارسات الاستدامة',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCards() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: GridView.count(
        crossAxisCount: 2,
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 1.1,
        children: [
          _buildSummaryCard(
            title: 'التنوع البيولوجي',
            value: '$speciesCount',
            subtitle: 'نوع',
            icon: Icons.pets,
            color: SahoolColors.sageGreen,
            gradientColors: [
              SahoolColors.sageGreen,
              SahoolColors.forestGreen,
            ],
          ),
          _buildSummaryCard(
            title: 'صحة التربة',
            value: '${soilHealthScore.toStringAsFixed(0)}%',
            subtitle: 'النقاط',
            icon: Icons.grass,
            color: SahoolColors.earthBrown,
            gradientColors: [
              SahoolColors.earthBrown,
              const Color(0xFF6D5C47),
            ],
          ),
          _buildSummaryCard(
            title: 'كفاءة المياه',
            value: '${waterEfficiency.toStringAsFixed(0)}%',
            subtitle: 'الكفاءة',
            icon: Icons.water_drop,
            color: SahoolColors.info,
            gradientColors: [
              SahoolColors.info,
              const Color(0xFF1565C0),
            ],
          ),
          _buildSummaryCard(
            title: 'الممارسات',
            value: '$practicesCount',
            subtitle: 'مطبقة',
            icon: Icons.checklist,
            color: SahoolColors.success,
            gradientColors: [
              SahoolColors.success,
              SahoolColors.healthExcellent,
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCard({
    required String title,
    required String value,
    required String subtitle,
    required IconData icon,
    required Color color,
    required List<Color> gradientColors,
  }) {
    return GestureDetector(
      onTap: () => _navigateToDetail(title),
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: gradientColors,
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.3),
              blurRadius: 12,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    icon,
                    color: Colors.white,
                    size: 20,
                  ),
                ),
              ],
            ),
            const Spacer(),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEcologicalScoreCard() {
    final scoreColor = _getScoreColor(overallEcologicalScore);
    final scoreLabel = _getScoreLabel(overallEcologicalScore);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: OrganicCard(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'النقاط الإيكولوجية الإجمالية',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: SahoolColors.forestGreen,
                  ),
                ),
                StatusBadge(
                  label: scoreLabel,
                  color: scoreColor,
                ),
              ],
            ),
            const SizedBox(height: 24),
            Center(
              child: SizedBox(
                width: 180,
                height: 180,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    // Circular Progress
                    SizedBox(
                      width: 180,
                      height: 180,
                      child: CircularProgressIndicator(
                        value: overallEcologicalScore / 100,
                        strokeWidth: 16,
                        backgroundColor: Colors.grey[200],
                        valueColor: AlwaysStoppedAnimation<Color>(scoreColor),
                        strokeCap: StrokeCap.round,
                      ),
                    ),
                    // Score Text
                    Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          overallEcologicalScore.toStringAsFixed(0),
                          style: TextStyle(
                            fontSize: 48,
                            fontWeight: FontWeight.bold,
                            color: scoreColor,
                          ),
                        ),
                        Text(
                          'من 100',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            _buildScoreBreakdown(),
          ],
        ),
      ),
    );
  }

  Widget _buildScoreBreakdown() {
    return Column(
      children: [
        _buildBreakdownItem(
          'التنوع البيولوجي',
          72.0,
          Icons.pets,
          SahoolColors.sageGreen,
        ),
        const SizedBox(height: 12),
        _buildBreakdownItem(
          'صحة التربة',
          soilHealthScore,
          Icons.grass,
          SahoolColors.earthBrown,
        ),
        const SizedBox(height: 12),
        _buildBreakdownItem(
          'كفاءة المياه',
          waterEfficiency,
          Icons.water_drop,
          SahoolColors.info,
        ),
        const SizedBox(height: 12),
        _buildBreakdownItem(
          'الممارسات المستدامة',
          68.0,
          Icons.checklist,
          SahoolColors.success,
        ),
      ],
    );
  }

  Widget _buildBreakdownItem(
    String label,
    double score,
    IconData icon,
    Color color,
  ) {
    return Row(
      children: [
        Icon(icon, size: 20, color: color),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    label,
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: SahoolColors.textDark,
                    ),
                  ),
                  Text(
                    '${score.toStringAsFixed(0)}%',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: score / 100,
                  backgroundColor: Colors.grey[200],
                  valueColor: AlwaysStoppedAnimation<Color>(color),
                  minHeight: 6,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActionsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader('إجراءات سريعة'),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1.5,
            children: [
              _buildActionButton(
                'إضافة مسح تنوع بيولوجي',
                Icons.search,
                SahoolColors.sageGreen,
                () => _navigateToAddRecord('biodiversity'),
              ),
              _buildActionButton(
                'إضافة سجل تربة',
                Icons.terrain,
                SahoolColors.earthBrown,
                () => _navigateToAddRecord('soil'),
              ),
              _buildActionButton(
                'إضافة سجل مياه',
                Icons.water,
                SahoolColors.info,
                () => _navigateToAddRecord('water'),
              ),
              _buildActionButton(
                'إضافة ممارسة',
                Icons.add_task,
                SahoolColors.success,
                () => _navigateToAddRecord('practice'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildActionButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: color.withOpacity(0.3),
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                color: color,
                size: 24,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentRecordsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader('السجلات الأخيرة', onViewAll: _navigateToAllRecords),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Column(
            children: [
              _buildRecordItem(
                type: 'biodiversity',
                title: 'مسح التنوع البيولوجي - الحقل الشمالي',
                date: 'منذ يومين',
                score: 72,
                icon: Icons.pets,
                color: SahoolColors.sageGreen,
              ),
              const SizedBox(height: 12),
              _buildRecordItem(
                type: 'soil',
                title: 'تحليل التربة - الحقل الغربي',
                date: 'منذ 3 أيام',
                score: 85,
                icon: Icons.grass,
                color: SahoolColors.earthBrown,
              ),
              const SizedBox(height: 12),
              _buildRecordItem(
                type: 'water',
                title: 'كفاءة الري - المنطقة A',
                date: 'منذ 5 أيام',
                score: 78,
                icon: Icons.water_drop,
                color: SahoolColors.info,
              ),
              const SizedBox(height: 12),
              _buildRecordItem(
                type: 'practice',
                title: 'تطبيق السماد العضوي',
                date: 'منذ أسبوع',
                score: 90,
                icon: Icons.eco,
                color: SahoolColors.success,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRecordItem({
    required String type,
    required String title,
    required String date,
    required int score,
    required IconData icon,
    required Color color,
  }) {
    final scoreColor = _getScoreColor(score.toDouble());

    return GestureDetector(
      onTap: () => _navigateToRecordDetail(type),
      child: OrganicCard(
        padding: const EdgeInsets.all(16),
        borderRadius: 16,
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                color: color,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: SahoolColors.textDark,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        Icons.access_time,
                        size: 12,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        date,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: scoreColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: scoreColor.withOpacity(0.3),
                ),
              ),
              child: Text(
                '$score%',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: scoreColor,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, {VoidCallback? onViewAll}) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[800],
                ),
          ),
          if (onViewAll != null)
            TextButton(
              onPressed: onViewAll,
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('عرض الكل'),
                  SizedBox(width: 4),
                  Icon(Icons.arrow_back_ios, size: 14),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 70) {
      return SahoolColors.success;
    } else if (score >= 40) {
      return SahoolColors.warning;
    } else {
      return SahoolColors.danger;
    }
  }

  String _getScoreLabel(double score) {
    if (score >= 70) {
      return 'ممتاز';
    } else if (score >= 40) {
      return 'جيد';
    } else {
      return 'يحتاج تحسين';
    }
  }

  Future<void> _refreshData() async {
    // محاكاة تحديث البيانات
    await Future.delayed(const Duration(seconds: 1));
    setState(() {
      // تحديث البيانات من API
    });
  }

  void _showFilterOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: Container(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'تصفية السجلات',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              ListTile(
                leading: const Icon(Icons.pets),
                title: const Text('التنوع البيولوجي'),
                onTap: () => Navigator.pop(context),
              ),
              ListTile(
                leading: const Icon(Icons.grass),
                title: const Text('صحة التربة'),
                onTap: () => Navigator.pop(context),
              ),
              ListTile(
                leading: const Icon(Icons.water_drop),
                title: const Text('كفاءة المياه'),
                onTap: () => Navigator.pop(context),
              ),
              ListTile(
                leading: const Icon(Icons.eco),
                title: const Text('الممارسات المستدامة'),
                onTap: () => Navigator.pop(context),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _navigateToDetail(String category) {
    // التنقل إلى صفحة التفاصيل
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('فتح تفاصيل: $category')),
    );
  }

  void _navigateToAddRecord(String type) {
    // التنقل إلى نموذج إضافة سجل
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('إضافة سجل: $type')),
    );
  }

  void _navigateToAllRecords() {
    // التنقل إلى صفحة جميع السجلات
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('عرض جميع السجلات')),
    );
  }

  void _navigateToRecordDetail(String type) {
    // التنقل إلى تفاصيل السجل
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('فتح سجل: $type')),
    );
  }
}
