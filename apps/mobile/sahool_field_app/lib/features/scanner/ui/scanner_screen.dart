import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/sahool_theme.dart';

/// Disease Scanner Screen - الماسح الضوئي للأمراض
/// واجهة الكاميرا مع إطار المسح والنتائج
class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  bool _isScanning = false;
  bool _hasResult = false;
  _ScanResult? _result;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _startScan() async {
    setState(() {
      _isScanning = true;
      _hasResult = false;
    });

    // Simulate scanning
    await Future.delayed(const Duration(seconds: 3));

    if (mounted) {
      setState(() {
        _isScanning = false;
        _hasResult = true;
        _result = _ScanResult(
          disease: 'صدأ القمح',
          confidence: 0.95,
          severity: 'متوسط',
          treatment: 'رش مبيد فطري (مانكوزيب) بمعدل 2.5 كجم/هكتار',
          prevention: 'تحسين التهوية بين النباتات وتجنب الري المفرط',
        );
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // Camera placeholder (black background)
          Container(color: Colors.black),

          // Simulated camera view with gradient
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.green.withOpacity(0.3),
                  Colors.black.withOpacity(0.5),
                ],
              ),
            ),
          ),

          // Scan frame overlay
          _buildScanFrame(),

          // Top controls
          _buildTopControls(),

          // Bottom controls
          _buildBottomControls(),

          // Result sheet
          if (_hasResult) _buildResultSheet(),

          // Scanning overlay
          if (_isScanning) _buildScanningOverlay(),
        ],
      ),
    );
  }

  Widget _buildScanFrame() {
    return Center(
      child: Container(
        width: 280,
        height: 280,
        decoration: BoxDecoration(
          border: Border.all(
            color: _isScanning
                ? SahoolColors.warning
                : _hasResult
                    ? SahoolColors.success
                    : Colors.white.withOpacity(0.5),
            width: 3,
          ),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Stack(
          children: [
            // Corner decorations
            ...List.generate(4, (index) {
              return Positioned(
                top: index < 2 ? 0 : null,
                bottom: index >= 2 ? 0 : null,
                left: index % 2 == 0 ? 0 : null,
                right: index % 2 == 1 ? 0 : null,
                child: Container(
                  width: 30,
                  height: 30,
                  decoration: BoxDecoration(
                    border: Border(
                      top: index < 2
                          ? BorderSide(color: SahoolColors.primary, width: 4)
                          : BorderSide.none,
                      bottom: index >= 2
                          ? BorderSide(color: SahoolColors.primary, width: 4)
                          : BorderSide.none,
                      left: index % 2 == 0
                          ? BorderSide(color: SahoolColors.primary, width: 4)
                          : BorderSide.none,
                      right: index % 2 == 1
                          ? BorderSide(color: SahoolColors.primary, width: 4)
                          : BorderSide.none,
                    ),
                  ),
                ),
              );
            }),
            // Scanning line
            if (_isScanning)
              AnimatedBuilder(
                animation: _animationController,
                builder: (context, child) {
                  return Positioned(
                    top: 260 * _animationController.value,
                    left: 0,
                    right: 0,
                    child: Container(
                      height: 3,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Colors.transparent,
                            SahoolColors.primary,
                            Colors.transparent,
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopControls() {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            IconButton(
              onPressed: () => context.pop(),
              icon: const Icon(Icons.close),
              style: IconButton.styleFrom(
                backgroundColor: Colors.black54,
                foregroundColor: Colors.white,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.black54,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Row(
                children: [
                  Icon(Icons.flash_off, color: Colors.white, size: 20),
                  SizedBox(width: 8),
                  Text('الفلاش', style: TextStyle(color: Colors.white)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomControls() {
    return Positioned(
      bottom: 0,
      left: 0,
      right: 0,
      child: Container(
        padding: const EdgeInsets.all(32),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.transparent,
              Colors.black.withOpacity(0.8),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Text(
                _isScanning
                    ? 'جارٍ التحليل...'
                    : 'ضع الورقة المصابة داخل الإطار',
                style: const TextStyle(color: Colors.white, fontSize: 16),
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // Gallery button
                  IconButton(
                    onPressed: () {},
                    icon: const Icon(Icons.photo_library),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.white24,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.all(16),
                    ),
                  ),
                  // Capture button
                  GestureDetector(
                    onTap: _isScanning ? null : _startScan,
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 4),
                      ),
                      padding: const EdgeInsets.all(4),
                      child: Container(
                        decoration: BoxDecoration(
                          color: _isScanning ? SahoolColors.warning : Colors.white,
                          shape: BoxShape.circle,
                        ),
                        child: _isScanning
                            ? const Padding(
                                padding: EdgeInsets.all(20),
                                child: CircularProgressIndicator(
                                  color: Colors.white,
                                  strokeWidth: 3,
                                ),
                              )
                            : null,
                      ),
                    ),
                  ),
                  // History button
                  IconButton(
                    onPressed: () {},
                    icon: const Icon(Icons.history),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.white24,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.all(16),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildScanningOverlay() {
    return Container(
      color: Colors.black54,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 60,
              height: 60,
              child: CircularProgressIndicator(
                color: SahoolColors.primary,
                strokeWidth: 4,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'جارٍ تحليل الصورة...',
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            const SizedBox(height: 8),
            Text(
              'يرجى الانتظار',
              style: TextStyle(color: Colors.white.withOpacity(0.7)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultSheet() {
    return DraggableScrollableSheet(
      initialChildSize: 0.5,
      minChildSize: 0.3,
      maxChildSize: 0.85,
      builder: (context, scrollController) {
        return Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: SingleChildScrollView(
            controller: scrollController,
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Handle
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: Colors.grey[300],
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Result header
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: SahoolColors.danger.withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.bug_report,
                          color: SahoolColors.danger,
                          size: 28,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _result?.disease ?? '',
                              style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: SahoolColors.success,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    'الدقة: ${((_result?.confidence ?? 0) * 100).toInt()}%',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: SahoolColors.warning,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    'الشدة: ${_result?.severity}',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),
                  const Divider(),
                  const SizedBox(height: 16),

                  // Treatment
                  _buildSection(
                    icon: Icons.medical_services,
                    title: 'العلاج المقترح',
                    content: _result?.treatment ?? '',
                    color: SahoolColors.info,
                  ),

                  const SizedBox(height: 16),

                  // Prevention
                  _buildSection(
                    icon: Icons.shield,
                    title: 'الوقاية',
                    content: _result?.prevention ?? '',
                    color: SahoolColors.success,
                  ),

                  const SizedBox(height: 24),

                  // Actions
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () {
                            setState(() {
                              _hasResult = false;
                              _result = null;
                            });
                          },
                          icon: const Icon(Icons.camera_alt),
                          label: const Text('مسح جديد'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {},
                          icon: const Icon(Icons.add_task),
                          label: const Text('إضافة كمهمة'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSection({
    required IconData icon,
    required String title,
    required String content,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(content, style: const TextStyle(fontSize: 14)),
        ],
      ),
    );
  }
}

class _ScanResult {
  final String disease;
  final double confidence;
  final String severity;
  final String treatment;
  final String prevention;

  _ScanResult({
    required this.disease,
    required this.confidence,
    required this.severity,
    required this.treatment,
    required this.prevention,
  });
}
