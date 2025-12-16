import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../weather/presentation/providers/weather_provider.dart';
import '../../market/data/market_repository.dart';
import '../../../core/network/api_result.dart';

/// SAHOOL Home Dashboard Screen - الشاشة الرئيسية المذهلة
/// تجمع ملخص الطقس، التنبيهات، والإجراءات السريعة
class HomeDashboardScreen extends ConsumerStatefulWidget {
  const HomeDashboardScreen({super.key});

  @override
  ConsumerState<HomeDashboardScreen> createState() => _HomeDashboardScreenState();
}

class _HomeDashboardScreenState extends ConsumerState<HomeDashboardScreen> {
  @override
  void initState() {
    super.initState();
    // تحميل بيانات الطقس عند بدء الشاشة
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(weatherProvider.notifier).loadWeatherByLocation(15.3694, 44.1910);
    });
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'صباح الخير';
    if (hour < 17) return 'مساء الخير';
    return 'مساء النور';
  }

  @override
  Widget build(BuildContext context) {
    final weatherState = ref.watch(weatherProvider);
    final walletAsync = ref.watch(walletFutureProvider);

    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: RefreshIndicator(
        onRefresh: () async {
          ref.read(weatherProvider.notifier).loadWeatherByLocation(15.3694, 44.1910);
          ref.invalidate(walletFutureProvider);
        },
        color: SahoolColors.primary,
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            // 1. الرأس المتحرك (Sliver App Bar)
            SliverAppBar(
              expandedHeight: 200.0,
              floating: false,
              pinned: true,
              backgroundColor: SahoolColors.forestGreen,
              flexibleSpace: FlexibleSpaceBar(
                title: Text(
                  '${_getGreeting()}، يا مزارع',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                background: _buildHeaderBackground(),
              ),
              actions: [
                IconButton(
                  icon: const Icon(Icons.notifications_outlined, color: Colors.white),
                  onPressed: () {
                    // فتح صفحة الإشعارات
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.settings_outlined, color: Colors.white),
                  onPressed: () {
                    // فتح الإعدادات
                  },
                ),
              ],
            ),

            // 2. المحتوى
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // بطاقة الطقس الحية
                    _buildSectionTitle('حالة الجو اليوم', Icons.wb_sunny_outlined),
                    const SizedBox(height: 12),
                    _buildWeatherSection(weatherState),

                    const SizedBox(height: 24),

                    // ملخص مالي
                    _buildSectionTitle('ملخص المحفظة', Icons.account_balance_wallet_outlined),
                    const SizedBox(height: 12),
                    _buildWalletSection(walletAsync),

                    const SizedBox(height: 24),

                    // الإجراءات السريعة
                    _buildSectionTitle('وصول سريع', Icons.bolt_outlined),
                    const SizedBox(height: 12),
                    _buildQuickActionsGrid(),

                    const SizedBox(height: 24),

                    // التنبيهات الحية (IoT)
                    _buildSectionTitle('تنبيهات الحقول', Icons.warning_amber_outlined),
                    const SizedBox(height: 12),
                    _buildAlertsSection(),

                    const SizedBox(height: 24),

                    // إحصائيات سريعة
                    _buildSectionTitle('إحصائيات اليوم', Icons.insights_outlined),
                    const SizedBox(height: 12),
                    _buildStatsRow(),

                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Widgets المساعدة
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildHeaderBackground() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [Color(0xFF1B5E20), Color(0xFF43A047)],
          begin: Alignment.bottomLeft,
          end: Alignment.topRight,
        ),
      ),
      child: Stack(
        children: [
          // نمط خلفي
          Positioned(
            right: -50,
            top: -30,
            child: Icon(
              Icons.agriculture,
              size: 200,
              color: Colors.white.withOpacity(0.1),
            ),
          ),
          Positioned(
            left: 20,
            bottom: 60,
            child: Icon(
              Icons.wb_sunny,
              size: 60,
              color: Colors.yellow.withOpacity(0.3),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 20, color: SahoolColors.forestGreen),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
      ],
    );
  }

  Widget _buildWeatherSection(WeatherState weatherState) {
    if (weatherState.isLoading) {
      return _buildLoadingCard();
    }

    if (weatherState.error != null) {
      return _buildWeatherCardFallback();
    }

    final data = weatherState.data;
    if (data == null) {
      return _buildWeatherCardFallback();
    }

    return _buildWeatherCard(
      temp: data.current.temperature.round(),
      description: data.current.description,
      humidity: data.current.humidity.round(),
      windSpeed: data.current.windSpeed,
      city: 'صنعاء',
    );
  }

  Widget _buildWeatherCard({
    required int temp,
    required String description,
    required int humidity,
    required double windSpeed,
    required String city,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E88E5), Color(0xFF42A5F5)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.blue.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    description,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(Icons.location_on, color: Colors.white70, size: 16),
                      const SizedBox(width: 4),
                      Text(
                        city,
                        style: const TextStyle(color: Colors.white70, fontSize: 14),
                      ),
                    ],
                  ),
                ],
              ),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '$temp',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 56,
                      fontWeight: FontWeight.w300,
                    ),
                  ),
                  const Padding(
                    padding: EdgeInsets.only(top: 8),
                    child: Text(
                      '°C',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 20,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(color: Colors.white24),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildWeatherDetail(Icons.water_drop, '$humidity%', 'رطوبة'),
              _buildWeatherDetail(Icons.air, '${windSpeed.toStringAsFixed(1)} م/ث', 'رياح'),
              _buildWeatherDetail(Icons.wb_sunny, 'مثالي', 'للزراعة'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildWeatherCardFallback() {
    return _buildWeatherCard(
      temp: 28,
      description: 'مشمس وصحو',
      humidity: 45,
      windSpeed: 3.5,
      city: 'صنعاء',
    );
  }

  Widget _buildWeatherDetail(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 22),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 14,
          ),
        ),
        Text(
          label,
          style: const TextStyle(color: Colors.white60, fontSize: 11),
        ),
      ],
    );
  }

  Widget _buildWalletSection(AsyncValue<ApiResult<WalletModel>> walletAsync) {
    return walletAsync.when(
      loading: () => _buildLoadingCard(height: 100),
      error: (_, __) => _buildWalletCardFallback(),
      data: (result) {
        if (result is Success<WalletModel>) {
          final wallet = result.data;
          return _buildWalletCard(
            balance: wallet.balance,
            creditScore: wallet.creditScore,
          );
        }
        return _buildWalletCardFallback();
      },
    );
  }

  Widget _buildWalletCard({required double balance, required int creditScore}) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'الرصيد المتاح',
                  style: TextStyle(color: Colors.grey, fontSize: 13),
                ),
                const SizedBox(height: 4),
                Text(
                  '\$${balance.toStringAsFixed(2)}',
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: _getCreditScoreColor(creditScore).withOpacity(0.1),
              borderRadius: BorderRadius.circular(30),
              border: Border.all(
                color: _getCreditScoreColor(creditScore).withOpacity(0.3),
              ),
            ),
            child: Column(
              children: [
                Text(
                  '$creditScore',
                  style: TextStyle(
                    color: _getCreditScoreColor(creditScore),
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                  ),
                ),
                Text(
                  'نقاط ائتمان',
                  style: TextStyle(
                    color: _getCreditScoreColor(creditScore),
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWalletCardFallback() {
    return _buildWalletCard(balance: 1250.00, creditScore: 720);
  }

  Color _getCreditScoreColor(int score) {
    if (score >= 700) return Colors.green;
    if (score >= 600) return Colors.orange;
    return Colors.red;
  }

  Widget _buildQuickActionsGrid() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _ActionItem(
          icon: Icons.qr_code_scanner,
          label: 'فحص آفة',
          color: Colors.purple,
          onTap: () {
            // Navigator.push to crop health screen
          },
        ),
        _ActionItem(
          icon: Icons.water_drop,
          label: 'الري الذكي',
          color: Colors.blue,
          onTap: () {
            // Navigator.push to irrigation screen
          },
        ),
        _ActionItem(
          icon: Icons.store,
          label: 'السوق',
          color: Colors.orange,
          onTap: () {
            // Navigator.push to market screen
          },
        ),
        _ActionItem(
          icon: Icons.chat_bubble,
          label: 'الخبراء',
          color: SahoolColors.forestGreen,
          onTap: () {
            // Navigator.push to community chat
          },
        ),
      ],
    );
  }

  Widget _buildAlertsSection() {
    // في التطبيق الحقيقي، هذه البيانات تأتي من خدمة IoT
    return Column(
      children: [
        _AlertCard(
          title: 'حقل الشمال',
          message: 'رطوبة التربة ممتازة (65%)',
          icon: Icons.check_circle,
          color: Colors.green,
          time: 'منذ 5 دقائق',
        ),
        const SizedBox(height: 10),
        _AlertCard(
          title: 'بيت محمي 1',
          message: 'درجة الحرارة مرتفعة قليلاً (32°)',
          icon: Icons.warning_amber_rounded,
          color: Colors.orange,
          time: 'منذ 15 دقيقة',
        ),
      ],
    );
  }

  Widget _buildStatsRow() {
    return Row(
      children: [
        Expanded(
          child: _StatMiniCard(
            icon: Icons.grass,
            value: '5',
            label: 'حقول نشطة',
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _StatMiniCard(
            icon: Icons.task_alt,
            value: '3',
            label: 'مهام اليوم',
            color: Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _StatMiniCard(
            icon: Icons.trending_up,
            value: '85%',
            label: 'صحة المحاصيل',
            color: Colors.green,
          ),
        ),
      ],
    );
  }

  Widget _buildLoadingCard({double height = 150}) {
    return Container(
      height: height,
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(16),
      ),
      child: const Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Widgets المكونة
// ═══════════════════════════════════════════════════════════════════════════

class _ActionItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionItem({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
              border: Border.all(color: color.withOpacity(0.2)),
            ),
            child: Icon(icon, color: color, size: 28),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Colors.black87,
            ),
          ),
        ],
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final String title;
  final String message;
  final IconData icon;
  final Color color;
  final String time;

  const _AlertCard({
    required this.title,
    required this.message,
    required this.icon,
    required this.color,
    required this.time,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border(right: BorderSide(color: color, width: 4)),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  message,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Text(
            time,
            style: TextStyle(
              color: Colors.grey[400],
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }
}

class _StatMiniCard extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color color;

  const _StatMiniCard({
    required this.icon,
    required this.value,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: const TextStyle(
              fontSize: 10,
              color: Colors.grey,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
