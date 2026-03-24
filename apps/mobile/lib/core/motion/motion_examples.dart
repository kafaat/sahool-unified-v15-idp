// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Motion Effects Examples
// أمثلة تأثيرات الحركة - للتنفيذ المرجعي
// ═══════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';

import 'motion_effects.dart';
import 'motion_preferences.dart';
import 'parallax_controller.dart';
import 'parallax_layer.dart';
import 'tilt_effect.dart';

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX HOME SCREEN BACKGROUND
// ─────────────────────────────────────────────────────────────────────────────

/// Example: Parallax home screen with layered background
/// مثال: شاشة رئيسية مع خلفية منظور متعددة الطبقات
class ParallaxHomeScreen extends StatelessWidget {
  const ParallaxHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ParallaxContainer(
      config: const ParallaxConfig(
        maxDisplacement: 40.0,
        sensitivity: 1.0,
      ),
      screenId: 'home',
      child: Scaffold(
        body: Stack(
          fit: StackFit.expand,
          children: [
            // Far background - sky/gradient
            ParallaxLayer(
              depth: ParallaxDepthLayers.farBackground,
              offsetMultiplier: 1.5,
              child: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Color(0xFF87CEEB), // Sky blue
                      Color(0xFFE0F7FA), // Light cyan
                    ],
                  ),
                ),
              ),
            ),

            // Mid background - clouds/shapes
            ParallaxLayer(
              depth: ParallaxDepthLayers.midBackground,
              offsetMultiplier: 1.0,
              child: _buildCloudLayer(),
            ),

            // Near background - hills/elements
            ParallaxLayer(
              depth: ParallaxDepthLayers.nearBackground,
              offsetMultiplier: 0.7,
              child: _buildHillsLayer(),
            ),

            // Content layer
            ParallaxLayer(
              depth: ParallaxDepthLayers.content,
              offsetMultiplier: 0.3,
              child: _buildContent(context),
            ),

            // Foreground elements
            ParallaxLayer(
              depth: ParallaxDepthLayers.farForeground,
              offsetMultiplier: 0.1,
              inverseDepth: true,
              child: _buildForegroundElements(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCloudLayer() {
    return const Align(
      alignment: Alignment(0.3, -0.6),
      child: Icon(
        Icons.cloud,
        size: 120,
        color: Colors.white70,
      ),
    );
  }

  Widget _buildHillsLayer() {
    return Align(
      alignment: Alignment.bottomCenter,
      child: Container(
        height: 200,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.green.shade200.withValues(alpha: 0.5),
              Colors.green.shade400.withValues(alpha: 0.8),
            ],
          ),
          borderRadius: const BorderRadius.only(
            topLeft: Radius.elliptical(200, 100),
            topRight: Radius.elliptical(200, 100),
          ),
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'مرحباً بك',
              style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    shadows: [
                      const Shadow(
                        color: Colors.black26,
                        blurRadius: 8,
                        offset: Offset(0, 2),
                      ),
                    ],
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'منصة ساهول الزراعية',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.white.withValues(alpha: 0.9),
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildForegroundElements() {
    return Positioned(
      bottom: 100,
      left: 20,
      child: FloatEffect(
        config: FloatConfig.gentle,
        child: Container(
          width: 50,
          height: 50,
          decoration: BoxDecoration(
            color: Colors.green.shade400,
            shape: BoxShape.circle,
          ),
          child: const Icon(Icons.grass, color: Colors.white),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TILTING FIELD CARDS
// ─────────────────────────────────────────────────────────────────────────────

/// Example: Field cards with 3D tilt effect
/// مثال: بطاقات الحقول مع تأثير ميلان ثلاثي الأبعاد
class TiltingFieldCard extends StatelessWidget {
  final String fieldName;
  final String fieldNameAr;
  final double area;
  final String cropType;
  final double healthScore;
  final String? imageUrl;
  final VoidCallback? onTap;

  const TiltingFieldCard({
    super.key,
    required this.fieldName,
    required this.fieldNameAr,
    required this.area,
    required this.cropType,
    required this.healthScore,
    this.imageUrl,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return TiltCard(
      config: TiltConfig.card,
      width: double.infinity,
      borderRadius: const BorderRadius.all(Radius.circular(20)),
      padding: const EdgeInsets.all(16),
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with image
          if (imageUrl != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.network(
                imageUrl!,
                height: 120,
                width: double.infinity,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => _buildPlaceholderImage(),
              ),
            )
          else
            _buildPlaceholderImage(),

          const SizedBox(height: 12),

          // Field name
          Text(
            fieldNameAr,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            fieldName,
            style: theme.textTheme.bodySmall?.copyWith(
              color: Colors.grey,
            ),
          ),

          const SizedBox(height: 12),

          // Stats row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildStat(
                icon: Icons.straighten,
                value: '${area.toStringAsFixed(1)} هـ',
                label: 'المساحة',
              ),
              _buildStat(
                icon: Icons.grass,
                value: cropType,
                label: 'المحصول',
              ),
              _buildHealthIndicator(),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPlaceholderImage() {
    return Container(
      height: 120,
      decoration: BoxDecoration(
        color: Colors.green.shade100,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Center(
        child: Icon(
          Icons.landscape,
          size: 48,
          color: Colors.green.shade300,
        ),
      ),
    );
  }

  Widget _buildStat({
    required IconData icon,
    required String value,
    required String label,
  }) {
    return Column(
      children: [
        Icon(icon, size: 20, color: Colors.grey),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: const TextStyle(fontSize: 10, color: Colors.grey),
        ),
      ],
    );
  }

  Widget _buildHealthIndicator() {
    Color healthColor;
    String healthLabel;

    if (healthScore >= 80) {
      healthColor = Colors.green;
      healthLabel = 'ممتاز';
    } else if (healthScore >= 60) {
      healthColor = Colors.orange;
      healthLabel = 'جيد';
    } else {
      healthColor = Colors.red;
      healthLabel = 'ضعيف';
    }

    return Column(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(color: healthColor, width: 3),
          ),
          child: Center(
            child: Text(
              '${healthScore.round()}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: healthColor,
                fontSize: 12,
              ),
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          healthLabel,
          style: TextStyle(fontSize: 10, color: healthColor),
        ),
      ],
    );
  }
}

/// Example: Grid of tilting field cards
/// مثال: شبكة بطاقات الحقول المائلة
class TiltingFieldCardsGrid extends StatelessWidget {
  const TiltingFieldCardsGrid({super.key});

  @override
  Widget build(BuildContext context) {
    return ParallaxContainer(
      screenId: 'fields_grid',
      child: Scaffold(
        appBar: AppBar(
          title: const Text('حقولي'),
        ),
        body: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: 5,
          itemBuilder: (context, index) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: WaveEffect(
                config: WaveConfig.gentle,
                index: index,
                child: TiltingFieldCard(
                  fieldName: 'Field ${index + 1}',
                  fieldNameAr: 'الحقل ${index + 1}',
                  area: 5.0 + index * 2.5,
                  cropType: ['قمح', 'شعير', 'ذرة', 'طماطم', 'خيار'][index % 5],
                  healthScore: 60.0 + (index * 8.0) % 40,
                  onTap: () {
                    // Navigate to field details
                  },
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 3D WEATHER WIDGET
// ─────────────────────────────────────────────────────────────────────────────

/// Example: 3D weather widget with tilt and parallax
/// مثال: ودجة الطقس ثلاثية الأبعاد مع ميلان ومنظور
class Weather3DWidget extends StatelessWidget {
  final double temperature;
  final String condition;
  final String conditionAr;
  final IconData weatherIcon;
  final double humidity;
  final double windSpeed;

  const Weather3DWidget({
    super.key,
    required this.temperature,
    required this.condition,
    required this.conditionAr,
    required this.weatherIcon,
    required this.humidity,
    required this.windSpeed,
  });

  @override
  Widget build(BuildContext context) {
    return TiltCard(
      config: TiltConfig.dramatic.copyWith(
        maxTiltX: 20.0,
        maxTiltY: 20.0,
      ),
      width: double.infinity,
      height: 200,
      gradient: const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Color(0xFF4A90D9),
          Color(0xFF67B8E3),
        ],
      ),
      borderRadius: const BorderRadius.all(Radius.circular(24)),
      child: Stack(
        children: [
          // Background weather icon (parallax)
          ParallaxLayer(
            depth: ParallaxDepthLayers.midBackground,
            offsetMultiplier: 2.0,
            child: Positioned(
              right: -30,
              top: -20,
              child: Icon(
                weatherIcon,
                size: 180,
                color: Colors.white.withValues(alpha: 0.1),
              ),
            ),
          ),

          // Content
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Temperature
                    ParallaxLayer(
                      depth: ParallaxDepthLayers.nearForeground,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${temperature.round()}°',
                            style: const TextStyle(
                              fontSize: 56,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          Text(
                            conditionAr,
                            style: const TextStyle(
                              fontSize: 18,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Weather icon with float
                    FloatEffect(
                      config: FloatConfig.gentle.copyWith(
                        enableAutoFloat: true,
                        autoFloatAmplitude: 8.0,
                      ),
                      child: Icon(
                        weatherIcon,
                        size: 72,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),

                const Spacer(),

                // Stats row
                ParallaxLayer(
                  depth: ParallaxDepthLayers.content,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildWeatherStat(
                        Icons.water_drop,
                        '${humidity.round()}%',
                        'الرطوبة',
                      ),
                      _buildWeatherStat(
                        Icons.air,
                        '${windSpeed.round()} كم/س',
                        'الرياح',
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWeatherStat(IconData icon, String value, String label) {
    return Row(
      children: [
        Icon(icon, color: Colors.white70, size: 20),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.7),
                fontSize: 12,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// FLOATING ACTION BUTTONS
// ─────────────────────────────────────────────────────────────────────────────

/// Example: Floating action buttons with motion effects
/// مثال: أزرار الإجراء العائمة مع تأثيرات الحركة
class MotionFABExample extends StatelessWidget {
  const MotionFABExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('أزرار عائمة')),
      body: const Center(child: Text('جرّب تحريك الجهاز لرؤية تأثير الأزرار')),
      floatingActionButton: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Simple floating FAB
          FloatEffect(
            config: FloatConfig.gentle,
            child: FloatingActionButton.small(
              heroTag: 'fab_small',
              onPressed: () {},
              child: const Icon(Icons.camera_alt),
            ),
          ),
          const SizedBox(height: 16),

          // Motion FAB with rotation
          MotionFloatingActionButton(
            icon: Icons.add,
            onPressed: () {},
            heroTag: 'fab_motion',
          ),
          const SizedBox(height: 16),

          // Extended motion FAB
          MotionFloatingActionButton(
            icon: Icons.add_a_photo,
            label: 'إضافة صورة',
            onPressed: () {},
            isExtended: true,
            heroTag: 'fab_extended',
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SHAKE TO REFRESH EXAMPLE
// ─────────────────────────────────────────────────────────────────────────────

/// Example: Shake to refresh list
/// مثال: هز الجهاز لتحديث القائمة
class ShakeToRefreshExample extends StatefulWidget {
  const ShakeToRefreshExample({super.key});

  @override
  State<ShakeToRefreshExample> createState() => _ShakeToRefreshExampleState();
}

class _ShakeToRefreshExampleState extends State<ShakeToRefreshExample> {
  List<String> _items = List.generate(10, (i) => 'العنصر ${i + 1}');
  bool _isRefreshing = false;

  Future<void> _refresh() async {
    if (_isRefreshing) return;

    setState(() => _isRefreshing = true);

    // Simulate network request
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      _items = List.generate(10, (i) => 'العنصر ${i + 1} (محدّث)');
      _isRefreshing = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return ParallaxContainer(
      screenId: 'shake_refresh',
      child: Scaffold(
        appBar: AppBar(
          title: const Text('هز للتحديث'),
        ),
        body: ShakeToRefresh(
          onRefresh: _refresh,
          showIndicator: true,
          child: RefreshIndicator(
            onRefresh: _refresh,
            child: ListView.builder(
              itemCount: _items.length,
              itemBuilder: (context, index) {
                return WaveEffect(
                  index: index,
                  config: WaveConfig.gentle,
                  child: ListTile(
                    leading: const Icon(Icons.eco),
                    title: Text(_items[index]),
                    subtitle: Text('محصول رقم ${index + 1}'),
                  ),
                );
              },
            ),
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPREHENSIVE DEMO SCREEN
// ─────────────────────────────────────────────────────────────────────────────

/// Comprehensive motion effects demo screen
/// شاشة عرض شاملة لتأثيرات الحركة
class MotionEffectsDemoScreen extends StatelessWidget {
  const MotionEffectsDemoScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ParallaxContainer(
      config: const ParallaxConfig(
        maxDisplacement: 35.0,
        sensitivity: 1.0,
      ),
      screenId: 'motion_demo',
      child: Scaffold(
        appBar: AppBar(
          title: const Text('تأثيرات الحركة'),
          actions: [
            IconButton(
              icon: const Icon(Icons.settings),
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => const MotionPreferencesScreen(),
                  ),
                );
              },
            ),
          ],
        ),
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Weather widget
            const Weather3DWidget(
              temperature: 28,
              condition: 'Sunny',
              conditionAr: 'مشمس',
              weatherIcon: Icons.wb_sunny,
              humidity: 45,
              windSpeed: 12,
            ),

            const SizedBox(height: 24),

            // Section: Tilt cards
            _buildSectionTitle(context, 'بطاقات مع تأثير الميلان'),
            const SizedBox(height: 12),

            const TiltCard(
              config: TiltConfig.card,
              padding: EdgeInsets.all(16),
              child: ListTile(
                leading: Icon(Icons.agriculture, size: 40),
                title: Text('القمح'),
                subtitle: Text('12.5 هكتار - صحة ممتازة'),
              ),
            ),

            const SizedBox(height: 16),

            // Section: Float effect
            _buildSectionTitle(context, 'تأثير الطفو'),
            const SizedBox(height: 12),

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                FloatEffect(
                  config: FloatConfig.gentle.copyWith(enableAutoFloat: true),
                  child: _buildIconCard(Icons.water_drop, 'ري'),
                ),
                FloatEffect(
                  config: FloatConfig.dramatic.copyWith(enableAutoFloat: true),
                  child: _buildIconCard(Icons.bug_report, 'آفات'),
                ),
                BobbingEffect(
                  amplitude: 8.0,
                  child: _buildIconCard(Icons.eco, 'محصول'),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Section: Pulse effect
            _buildSectionTitle(context, 'تأثير النبض'),
            const SizedBox(height: 12),

            Center(
              child: PulseEffect(
                minScale: 0.95,
                maxScale: 1.05,
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: Colors.red.shade400,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.warning, color: Colors.white, size: 40),
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Section: Parallax layers
            _buildSectionTitle(context, 'طبقات المنظور'),
            const SizedBox(height: 12),

            SizedBox(
              height: 200,
              child: ParallaxStack(
                baseDepth: 0.0,
                depthIncrement: 0.2,
                children: [
                  // Background
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.green.shade100,
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  // Mid layer
                  Center(
                    child: Icon(
                      Icons.landscape,
                      size: 100,
                      color: Colors.green.shade300,
                    ),
                  ),
                  // Foreground
                  Align(
                    alignment: Alignment.bottomRight,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Text(
                        'حقل 1',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.green.shade800,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Interactive hint
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Row(
                children: [
                  Icon(Icons.info, color: Colors.blue.shade700),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'حرّك جهازك لرؤية تأثيرات الحركة. يمكنك ضبط الإعدادات من أيقونة الترس.',
                      style: TextStyle(fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(BuildContext context, String title) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: Colors.grey.shade700,
          ),
    );
  }

  Widget _buildIconCard(IconData icon, String label) {
    return Container(
      width: 80,
      height: 80,
      decoration: BoxDecoration(
        color: Colors.green.shade100,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.green.shade200.withValues(alpha: 0.5),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: Colors.green.shade700, size: 32),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.green.shade800,
            ),
          ),
        ],
      ),
    );
  }
}
