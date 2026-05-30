import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/network/backend_connectivity_provider.dart';
import '../../../core/auth/auth_service.dart';

/// SAHOOL Splash Screen - شاشة البداية
/// Checks backend connectivity while showing the animated logo.
/// Navigates to login/home on success, or shows a retry screen on failure.
class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen>
    with TickerProviderStateMixin {
  late AnimationController _breathingController;
  late AnimationController _loadingController;
  late Animation<double> _breathingAnimation;
  late Animation<double> _loadingAnimation;

  bool _animationDone = false;
  bool _navigated = false;

  @override
  void initState() {
    super.initState();

    _breathingController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat(reverse: true);

    _loadingController = AnimationController(
      duration: const Duration(milliseconds: 2500),
      vsync: this,
    )..forward();

    _loadingAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _loadingController, curve: Curves.easeOut),
    );

    _breathingAnimation = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: _breathingController, curve: Curves.easeInOut),
    );

    _loadingController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        setState(() => _animationDone = true);
        _tryNavigate();
      }
    });
  }

  /// Navigate once animation is done — proceed regardless of connectivity (offline-first).
  void _tryNavigate() {
    if (_navigated || !_animationDone) return;

    final connectivity = ref.read(backendConnectivityProvider);
    connectivity.when(
      data: (_) => _navigate(), // Navigate whether online or offline
      loading: () {
        // Animation finished but check still running — will be triggered from ref.listen
      },
      error: (_, __) => _navigate(),
    );
  }

  void _navigate() {
    if (_navigated || !mounted) return;
    _navigated = true;

    final authState = ref.read(authStateProvider);
    if (authState.isAuthenticated) {
      context.go('/home');
    } else {
      context.go('/login');
    }
  }

  @override
  void dispose() {
    _breathingController.dispose();
    _loadingController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // React to connectivity check completing after animation finishes — navigate regardless
    ref.listen(backendConnectivityProvider, (_, next) {
      next.whenData((_) {
        if (_animationDone) _navigate();
      });
    });

    // Watch provider to trigger rebuilds when connectivity check completes
    ref.watch(backendConnectivityProvider);
    const bool showError = false;

    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF1B5E20),
              Color(0xFF2E7D32),
              Color(0xFF388E3C),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              const Spacer(flex: 2),

              // Logo
              AnimatedBuilder(
                animation: _breathingAnimation,
                builder: (context, child) => Transform.scale(
                  scale: _breathingAnimation.value,
                  child: child,
                ),
                child: Column(
                  children: [
                    Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.2),
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
                        color: Colors.white.withValues(alpha: 0.9),
                        fontSize: 18,
                        fontWeight: FontWeight.w300,
                      ),
                    ),
                  ],
                ),
              ),

              const Spacer(flex: 2),

              // Loading / error section
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 60),
                child: showError ? _buildErrorSection() : _buildLoadingSection(),
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
                        color: Colors.white.withValues(alpha: 0.6),
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

  Widget _buildLoadingSection() {
    return AnimatedBuilder(
      animation: _loadingAnimation,
      builder: (context, child) {
        return Column(
          children: [
            SizedBox(
              height: 60,
              child: CustomPaint(
                size: const Size(double.infinity, 60),
                painter: _PlantGrowthPainter(progress: _loadingAnimation.value),
              ),
            ),
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: LinearProgressIndicator(
                value: _animationDone ? null : _loadingAnimation.value,
                backgroundColor: Colors.white.withValues(alpha: 0.3),
                valueColor: const AlwaysStoppedAnimation(Colors.white),
                minHeight: 6,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              _animationDone ? 'جاري الاتصال بالخادم...' : 'جاري التحميل...',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.8),
                fontSize: 14,
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildErrorSection() {
    return Column(
      children: [
        const Icon(Icons.wifi_off_rounded, color: Colors.white70, size: 48),
        const SizedBox(height: 16),
        Text(
          'تعذّر الاتصال بالخادم',
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.95),
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        Text(
          'تأكد من تشغيل الخادم والاتصال بالشبكة',
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.7),
            fontSize: 13,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 24),
        ElevatedButton.icon(
          onPressed: _retry,
          icon: const Icon(Icons.refresh_rounded),
          label: const Text('إعادة المحاولة'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.white,
            foregroundColor: SahoolColors.primary,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(30),
            ),
          ),
        ),
      ],
    );
  }

  void _retry() {
    setState(() {
      _navigated = false;
      _animationDone = false;
    });
    // Invalidate provider to re-run the connectivity check
    ref.invalidate(backendConnectivityProvider);
    // Restart the loading animation
    _loadingController
      ..reset()
      ..forward();
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
    final stemHeight = size.height * progress;
    canvas.drawLine(
      Offset(centerX, bottomY),
      Offset(centerX, bottomY - stemHeight),
      paint,
    );

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
  bool shouldRepaint(covariant _PlantGrowthPainter oldDelegate) =>
      oldDelegate.progress != progress;
}
