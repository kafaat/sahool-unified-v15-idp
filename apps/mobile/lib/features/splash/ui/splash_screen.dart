import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/sahool_theme.dart';

/// SAHOOL Splash Screen - شاشة البداية
/// شعار SAHOOL مع حركة النبض وشريط تحميل على شكل ساق نبات
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  late AnimationController _breathingController;
  late AnimationController _loadingController;
  late Animation<double> _breathingAnimation;
  late Animation<double> _loadingAnimation;

  @override
  void initState() {
    super.initState();

    // Breathing animation for logo
    _breathingController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat(reverse: true);

    _breathingAnimation = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: _breathingController, curve: Curves.easeInOut),
    );

    // Loading progress animation
    _loadingController = AnimationController(
      duration: const Duration(milliseconds: 2500),
      vsync: this,
    )..forward();

    _loadingAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _loadingController, curve: Curves.easeOut),
    );

    // Navigate after loading
    _loadingController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        context.go('/role-selection');
      }
    });
  }

  @override
  void dispose() {
    _breathingController.dispose();
    _loadingController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF1B5E20), // Dark Green
              Color(0xFF2E7D32), // Medium Green
              Color(0xFF388E3C), // Light Green
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              const Spacer(flex: 2),

              // Logo with breathing animation
              AnimatedBuilder(
                animation: _breathingAnimation,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _breathingAnimation.value,
                    child: child,
                  );
                },
                child: Column(
                  children: [
                    // Logo Icon
                    Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.2),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.eco,
                        size: 60,
                        color: SahoolColors.primary,
                      ),
                    ),
                    const SizedBox(height: 24),
                    // Logo Text
                    const Text(
                      'SAHOOL',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 42,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 8,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'منصة الزراعة الذكية',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 18,
                        fontWeight: FontWeight.w300,
                      ),
                    ),
                  ],
                ),
              ),

              const Spacer(flex: 2),

              // Plant stem loading indicator
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 60),
                child: AnimatedBuilder(
                  animation: _loadingAnimation,
                  builder: (context, child) {
                    return Column(
                      children: [
                        // Plant growth indicator
                        SizedBox(
                          height: 60,
                          child: CustomPaint(
                            size: const Size(double.infinity, 60),
                            painter: _PlantGrowthPainter(
                              progress: _loadingAnimation.value,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                        // Progress bar
                        ClipRRect(
                          borderRadius: BorderRadius.circular(10),
                          child: LinearProgressIndicator(
                            value: _loadingAnimation.value,
                            backgroundColor: Colors.white.withOpacity(0.3),
                            valueColor: const AlwaysStoppedAnimation(Colors.white),
                            minHeight: 6,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'جاري التحميل...',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.8),
                            fontSize: 14,
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ),

              const Spacer(),

              // Bottom branding
              Padding(
                padding: const EdgeInsets.only(bottom: 32),
                child: Column(
                  children: [
                    Text(
                      'Power of',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.6),
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'KAFAAT',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 4,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Plant growth painter for loading indicator
class _PlantGrowthPainter extends CustomPainter {
  final double progress;

  _PlantGrowthPainter({required this.progress});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final centerX = size.width / 2;
    final bottomY = size.height;

    // Draw stem
    final stemHeight = size.height * progress;
    canvas.drawLine(
      Offset(centerX, bottomY),
      Offset(centerX, bottomY - stemHeight),
      paint,
    );

    // Draw leaves based on progress
    if (progress > 0.3) {
      _drawLeaf(canvas, paint, centerX, bottomY - stemHeight * 0.3, -1, (progress - 0.3) / 0.7);
    }
    if (progress > 0.5) {
      _drawLeaf(canvas, paint, centerX, bottomY - stemHeight * 0.5, 1, (progress - 0.5) / 0.5);
    }
    if (progress > 0.7) {
      _drawLeaf(canvas, paint, centerX, bottomY - stemHeight * 0.7, -1, (progress - 0.7) / 0.3);
    }
    if (progress > 0.9) {
      // Draw flower/top
      paint.style = PaintingStyle.fill;
      canvas.drawCircle(
        Offset(centerX, bottomY - stemHeight),
        6 * ((progress - 0.9) / 0.1),
        paint,
      );
    }
  }

  void _drawLeaf(Canvas canvas, Paint paint, double x, double y, int direction, double leafProgress) {
    final path = Path();
    final leafLength = 15 * leafProgress;
    path.moveTo(x, y);
    path.quadraticBezierTo(
      x + (20 * direction * leafProgress),
      y - 5,
      x + (leafLength * direction),
      y - 10,
    );
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _PlantGrowthPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}
