import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';

/// شاشة الترحيب والتعريف - Onboarding
/// تقديم التطبيق للمستخدم الجديد بطريقة جذابة
class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<OnboardingPage> _pages = [
    OnboardingPage(
      title: "أهلاً بك في سهول",
      subtitle: "منصتك الذكية لإدارة مزرعتك",
      description:
          "سهول يساعدك في مراقبة حقولك، تتبع صحة المحاصيل، وإدارة العمليات الزراعية بكفاءة عالية.",
      icon: Icons.agriculture,
      color: SahoolColors.forestGreen,
      illustration: _IllustrationType.farm,
    ),
    OnboardingPage(
      title: "راقب حقولك بذكاء",
      subtitle: "صور الأقمار الصناعية ومؤشرات NDVI",
      description:
          "احصل على صور حية لحقولك من الأقمار الصناعية مع تحليل صحة المحاصيل باستخدام مؤشرات الغطاء النباتي.",
      icon: Icons.satellite_alt,
      color: SahoolColors.sageGreen,
      illustration: _IllustrationType.satellite,
    ),
    OnboardingPage(
      title: "توقعات الطقس الدقيقة",
      subtitle: "تنبؤات محلية لحقلك",
      description:
          "توقعات طقس مخصصة لموقع مزرعتك مع تنبيهات الصقيع والأمطار وتوصيات زراعية يومية.",
      icon: Icons.wb_sunny,
      color: SahoolColors.harvestGold,
      illustration: _IllustrationType.weather,
    ),
    OnboardingPage(
      title: "مجتمع المزارعين",
      subtitle: "تعلم من خبراء الزراعة",
      description:
          "تواصل مع مزارعين آخرين، اطرح أسئلتك، واحصل على إجابات من خبراء معتمدين في مختلف المجالات الزراعية.",
      icon: Icons.people,
      color: SahoolColors.earthBrown,
      illustration: _IllustrationType.community,
    ),
  ];

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _onNextPage() {
    if (_currentPage < _pages.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
      );
    } else {
      _completeOnboarding();
    }
  }

  void _completeOnboarding() {
    // Navigate to login/home screen
    Navigator.of(context).pushReplacementNamed('/login');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            // Skip Button
            Align(
              alignment: Alignment.topRight,
              child: TextButton(
                onPressed: _completeOnboarding,
                child: Text(
                  "تخطي",
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 16,
                  ),
                ),
              ),
            ),

            // Page View
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                onPageChanged: (index) {
                  setState(() => _currentPage = index);
                },
                itemCount: _pages.length,
                itemBuilder: (context, index) {
                  return _buildPage(_pages[index]);
                },
              ),
            ),

            // Bottom Section
            Padding(
              padding: const EdgeInsets.all(32),
              child: Column(
                children: [
                  // Page Indicators
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(
                      _pages.length,
                      (index) => _buildDot(index),
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Next/Start Button
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: _onNextPage,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _pages[_currentPage].color,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                        elevation: 0,
                      ),
                      child: Text(
                        _currentPage == _pages.length - 1 ? "ابدأ الآن" : "التالي",
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPage(OnboardingPage page) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Illustration
          _buildIllustration(page.illustration, page.color),
          const SizedBox(height: 48),

          // Title
          Text(
            page.title,
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: page.color,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),

          // Subtitle
          Text(
            page.subtitle,
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[700],
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),

          // Description
          Text(
            page.description,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
              height: 1.6,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildIllustration(_IllustrationType type, Color color) {
    switch (type) {
      case _IllustrationType.farm:
        return _FarmIllustration(color: color);
      case _IllustrationType.satellite:
        return _SatelliteIllustration(color: color);
      case _IllustrationType.weather:
        return _WeatherIllustration(color: color);
      case _IllustrationType.community:
        return _CommunityIllustration(color: color);
    }
  }

  Widget _buildDot(int index) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      margin: const EdgeInsets.symmetric(horizontal: 4),
      width: _currentPage == index ? 24 : 8,
      height: 8,
      decoration: BoxDecoration(
        color: _currentPage == index
            ? _pages[_currentPage].color
            : Colors.grey[300],
        borderRadius: BorderRadius.circular(4),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Data Classes
// ═══════════════════════════════════════════════════════════════════════════

class OnboardingPage {
  final String title;
  final String subtitle;
  final String description;
  final IconData icon;
  final Color color;
  final _IllustrationType illustration;

  OnboardingPage({
    required this.title,
    required this.subtitle,
    required this.description,
    required this.icon,
    required this.color,
    required this.illustration,
  });
}

enum _IllustrationType { farm, satellite, weather, community }

// ═══════════════════════════════════════════════════════════════════════════
// Custom Illustrations
// ═══════════════════════════════════════════════════════════════════════════

class _FarmIllustration extends StatelessWidget {
  final Color color;

  const _FarmIllustration({required this.color});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 280,
      height: 200,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background circle
          Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
          ),
          // Field representation
          Positioned(
            bottom: 20,
            child: Container(
              width: 240,
              height: 60,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    color.withOpacity(0.3),
                    color.withOpacity(0.5),
                  ],
                ),
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(120),
                ),
              ),
            ),
          ),
          // Tractor icon
          Positioned(
            bottom: 50,
            left: 60,
            child: Icon(Icons.agriculture, size: 48, color: color),
          ),
          // Plant icons
          Positioned(
            bottom: 60,
            right: 50,
            child: Icon(Icons.grass, size: 36, color: color.withOpacity(0.7)),
          ),
          Positioned(
            bottom: 70,
            right: 90,
            child: Icon(Icons.grass, size: 28, color: color.withOpacity(0.5)),
          ),
          // Sun
          Positioned(
            top: 20,
            right: 40,
            child: Icon(Icons.wb_sunny, size: 40, color: SahoolColors.harvestGold),
          ),
        ],
      ),
    );
  }
}

class _SatelliteIllustration extends StatelessWidget {
  final Color color;

  const _SatelliteIllustration({required this.color});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 280,
      height: 200,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background circle
          Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
          ),
          // Satellite
          Positioned(
            top: 20,
            child: Icon(Icons.satellite_alt, size: 56, color: color),
          ),
          // Signal lines
          Positioned(
            top: 80,
            child: CustomPaint(
              size: const Size(100, 80),
              painter: _SignalPainter(color: color),
            ),
          ),
          // Field grid
          Positioned(
            bottom: 20,
            child: Container(
              width: 120,
              height: 80,
              decoration: BoxDecoration(
                border: Border.all(color: color.withOpacity(0.5), width: 2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: GridView.count(
                crossAxisCount: 3,
                physics: const NeverScrollableScrollPhysics(),
                children: List.generate(
                  9,
                  (index) => Container(
                    margin: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      color: [
                        SahoolColors.healthExcellent,
                        SahoolColors.healthGood,
                        SahoolColors.healthModerate,
                        SahoolColors.healthGood,
                        SahoolColors.healthExcellent,
                        SahoolColors.healthGood,
                        SahoolColors.healthModerate,
                        SahoolColors.healthGood,
                        SahoolColors.healthExcellent,
                      ][index]
                          .withOpacity(0.6),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SignalPainter extends CustomPainter {
  final Color color;

  _SignalPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    for (var i = 0; i < 3; i++) {
      final radius = 20.0 + (i * 20);
      canvas.drawArc(
        Rect.fromCenter(
          center: Offset(size.width / 2, 0),
          width: radius * 2,
          height: radius * 2,
        ),
        0.3,
        2.5,
        false,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _WeatherIllustration extends StatelessWidget {
  final Color color;

  const _WeatherIllustration({required this.color});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 280,
      height: 200,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background circle
          Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              gradient: RadialGradient(
                colors: [
                  color.withOpacity(0.2),
                  color.withOpacity(0.05),
                ],
              ),
              shape: BoxShape.circle,
            ),
          ),
          // Sun
          Positioned(
            top: 30,
            left: 60,
            child: Icon(Icons.wb_sunny, size: 64, color: color),
          ),
          // Cloud
          Positioned(
            top: 50,
            right: 50,
            child: Icon(Icons.cloud, size: 48, color: Colors.grey[400]),
          ),
          // Temperature display
          Positioned(
            bottom: 40,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.thermostat, color: color, size: 28),
                  const SizedBox(width: 8),
                  Text(
                    "32°C",
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                ],
              ),
            ),
          ),
          // Rain drops
          Positioned(
            top: 90,
            right: 70,
            child: Icon(Icons.water_drop, size: 16, color: Colors.blue[300]),
          ),
          Positioned(
            top: 100,
            right: 55,
            child: Icon(Icons.water_drop, size: 12, color: Colors.blue[200]),
          ),
        ],
      ),
    );
  }
}

class _CommunityIllustration extends StatelessWidget {
  final Color color;

  const _CommunityIllustration({required this.color});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 280,
      height: 200,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background circle
          Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
          ),
          // Center person (expert)
          Positioned(
            child: CircleAvatar(
              radius: 36,
              backgroundColor: color,
              child: const Icon(Icons.person, size: 40, color: Colors.white),
            ),
          ),
          // Surrounding people
          Positioned(
            top: 20,
            left: 40,
            child: CircleAvatar(
              radius: 24,
              backgroundColor: SahoolColors.sageGreen.withOpacity(0.5),
              child: Icon(Icons.person, size: 28, color: SahoolColors.forestGreen),
            ),
          ),
          Positioned(
            top: 30,
            right: 40,
            child: CircleAvatar(
              radius: 20,
              backgroundColor: SahoolColors.harvestGold.withOpacity(0.5),
              child: Icon(Icons.person, size: 24, color: SahoolColors.earthBrown),
            ),
          ),
          Positioned(
            bottom: 30,
            left: 50,
            child: CircleAvatar(
              radius: 22,
              backgroundColor: SahoolColors.paleOlive,
              child: Icon(Icons.person, size: 26, color: SahoolColors.forestGreen),
            ),
          ),
          Positioned(
            bottom: 20,
            right: 50,
            child: CircleAvatar(
              radius: 26,
              backgroundColor: SahoolColors.sageGreen.withOpacity(0.5),
              child: Icon(Icons.person, size: 30, color: SahoolColors.forestGreen),
            ),
          ),
          // Connection lines
          Positioned.fill(
            child: CustomPaint(
              painter: _ConnectionPainter(color: color),
            ),
          ),
          // Chat bubble
          Positioned(
            top: 60,
            right: 80,
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                  ),
                ],
              ),
              child: const Icon(Icons.chat_bubble, size: 20, color: SahoolColors.forestGreen),
            ),
          ),
        ],
      ),
    );
  }
}

class _ConnectionPainter extends CustomPainter {
  final Color color;

  _ConnectionPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(0.2)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    final center = Offset(size.width / 2, size.height / 2);

    // Draw connection lines from center to surrounding positions
    final points = [
      Offset(size.width * 0.25, size.height * 0.2),
      Offset(size.width * 0.75, size.height * 0.25),
      Offset(size.width * 0.3, size.height * 0.75),
      Offset(size.width * 0.75, size.height * 0.8),
    ];

    for (final point in points) {
      canvas.drawLine(center, point, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
