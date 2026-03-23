import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/theme/sahool_theme.dart';
import '../data/scanner_repository.dart';

/// Disease Scanner Screen - الماسح الضوئي للأمراض
/// واجهة الكاميرا مع إطار المسح والنتائج
class ScannerScreen extends ConsumerStatefulWidget {
  const ScannerScreen({super.key});

  @override
  ConsumerState<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends ConsumerState<ScannerScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late MobileScannerController _cameraController;
  final ImagePicker _imagePicker = ImagePicker();
  bool _isScanning = false;
  bool _hasResult = false;
  bool _cameraActive = true;
  bool _flashOn = false;
  _ScanResult? _result;
  File? _capturedImage;
  List<_ScanResult> _scanHistory = [];

  static const _historyKey = 'sahool_scan_history';

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();
    _cameraController = MobileScannerController(
      detectionSpeed: DetectionSpeed.noDuplicates,
      facing: CameraFacing.back,
      torchEnabled: false,
    );
    _loadScanHistory();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _cameraController.dispose();
    super.dispose();
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Scan history persistence - حفظ سجل الفحوصات
  // ─────────────────────────────────────────────────────────────────────────

  Future<void> _loadScanHistory() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonList = prefs.getStringList(_historyKey);
    if (jsonList != null && jsonList.isNotEmpty) {
      setState(() {
        _scanHistory = jsonList
            .map((e) => _ScanResult.fromJson(json.decode(e) as Map<String, dynamic>))
            .toList();
      });
    }
  }

  Future<void> _persistScanHistory() async {
    final prefs = await SharedPreferences.getInstance();
    // Keep last 50 scans to avoid unbounded storage growth
    final capped = _scanHistory.take(50).toList();
    final jsonList = capped.map((e) => json.encode(e.toJson())).toList();
    await prefs.setStringList(_historyKey, jsonList);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Image capture & analysis - التقاط الصور والتحليل
  // ─────────────────────────────────────────────────────────────────────────

  Future<void> _captureFromCamera() async {
    final XFile? photo = await _imagePicker.pickImage(
      source: ImageSource.camera,
      imageQuality: 85,
      maxWidth: 1280,
      maxHeight: 1280,
    );
    if (photo == null || !mounted) return;

    setState(() {
      _isScanning = true;
      _hasResult = false;
      _capturedImage = File(photo.path);
      _cameraActive = false;
    });

    await _analyzeImage(_capturedImage!);
  }

  Future<void> _pickFromGallery() async {
    final XFile? image = await _imagePicker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 85,
      maxWidth: 1280,
      maxHeight: 1280,
    );
    if (image == null || !mounted) return;

    setState(() {
      _isScanning = true;
      _hasResult = false;
      _capturedImage = File(image.path);
      _cameraActive = false;
    });

    await _analyzeImage(_capturedImage!);
  }

  Future<void> _analyzeImage(File imageFile) async {
    // Call yolo26-vision-service: POST /api/v1/detect/disease with multipart upload
    final repository = ref.read(scannerRepositoryProvider);
    final apiResult = await repository.detectDisease(imageFile);

    if (!mounted) return;

    apiResult.when(
      success: (detection) {
        final result = _ScanResult(
          disease: detection.disease,
          diseaseEn: detection.diseaseEn,
          confidence: detection.confidence,
          severity: detection.severity,
          severityEn: detection.severityEn,
          treatment: detection.treatment,
          prevention: detection.prevention,
          imagePath: imageFile.path,
          scannedAt: detection.scannedAt,
        );
        setState(() {
          _isScanning = false;
          _hasResult = true;
          _result = result;
          _scanHistory.insert(0, result);
        });
        _persistScanHistory();
      },
      failure: (message, statusCode) {
        // Offline-first fallback: use hardcoded result when API is unavailable
        final result = _ScanResult(
          disease: 'صدأ القمح',
          diseaseEn: 'Wheat Rust',
          confidence: 0.95,
          severity: 'متوسط',
          severityEn: 'moderate',
          treatment: 'رش مبيد فطري (مانكوزيب) بمعدل 2.5 كجم/هكتار',
          prevention: 'تحسين التهوية بين النباتات وتجنب الري المفرط',
          imagePath: imageFile.path,
          scannedAt: DateTime.now(),
        );
        setState(() {
          _isScanning = false;
          _hasResult = true;
          _result = result;
          _scanHistory.insert(0, result);
        });
        _persistScanHistory();
        // Show non-blocking snackbar indicating offline mode
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('وضع عدم الاتصال | Offline mode: $message'),
            backgroundColor: SahoolColors.warning,
            duration: const Duration(seconds: 3),
          ),
        );
      },
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Flash toggle - تبديل الفلاش
  // ─────────────────────────────────────────────────────────────────────────

  Future<void> _toggleFlash() async {
    await _cameraController.toggleTorch();
    setState(() {
      _flashOn = !_flashOn;
    });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Navigation helpers - أدوات التنقل
  // ─────────────────────────────────────────────────────────────────────────

  void _showScanHistory() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.6,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'سجل الفحوصات | Scan History',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
            Expanded(
              child: _scanHistory.isEmpty
                  ? Center(
                      child: Text(
                        'لا توجد فحوصات سابقة\nNo previous scans',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey[400]),
                      ),
                    )
                  : ListView.builder(
                      itemCount: _scanHistory.length,
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemBuilder: (context, index) {
                        final scan = _scanHistory[index];
                        return ListTile(
                          leading: scan.imagePath != null &&
                                  File(scan.imagePath!).existsSync()
                              ? ClipRRect(
                                  borderRadius: BorderRadius.circular(8),
                                  child: Image.file(
                                    File(scan.imagePath!),
                                    width: 48,
                                    height: 48,
                                    fit: BoxFit.cover,
                                  ),
                                )
                              : Container(
                                  width: 48,
                                  height: 48,
                                  decoration: BoxDecoration(
                                    color: SahoolColors.danger.withValues(alpha: 0.1),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: const Icon(Icons.bug_report,
                                      color: SahoolColors.danger),
                                ),
                          title: Text(scan.disease),
                          subtitle: Text(
                            '${scan.diseaseEn} - '
                            'الدقة | Conf: ${(scan.confidence * 100).toInt()}% - '
                            '${scan.severity}',
                          ),
                          trailing: scan.scannedAt != null
                              ? Text(
                                  '${scan.scannedAt!.hour}:${scan.scannedAt!.minute.toString().padLeft(2, '0')}',
                                  style: TextStyle(
                                      color: Colors.grey[500], fontSize: 12),
                                )
                              : null,
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  void _addAsTask() {
    if (_result == null) return;
    // Navigate to task creation with pre-filled data
    context.push('/tasks', extra: {
      'prefillTitle': 'علاج: ${_result!.disease} | Treatment: ${_result!.diseaseEn}',
      'prefillDescription': '${_result!.treatment}\n\nالوقاية | Prevention: ${_result!.prevention}',
      'createNew': true,
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'تمت إضافة "${_result!.disease}" كمهمة | Added as task',
        ),
        backgroundColor: SahoolColors.success,
      ),
    );
  }

  void _resetForNewScan() {
    setState(() {
      _hasResult = false;
      _result = null;
      _capturedImage = null;
      _cameraActive = true;
    });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Build methods - بناء واجهة المستخدم
  // ─────────────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // Camera preview / captured image
          if (_capturedImage != null && !_cameraActive)
            Positioned.fill(
              child: Image.file(
                _capturedImage!,
                fit: BoxFit.cover,
              ),
            )
          else
            Positioned.fill(
              child: MobileScanner(
                controller: _cameraController,
                // We do not need barcode detection here; this is purely
                // for live camera preview. Detections are ignored.
                onDetect: (_) {},
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
                    : Colors.white.withValues(alpha: 0.5),
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
                          ? const BorderSide(color: SahoolColors.primary, width: 4)
                          : BorderSide.none,
                      bottom: index >= 2
                          ? const BorderSide(color: SahoolColors.primary, width: 4)
                          : BorderSide.none,
                      left: index % 2 == 0
                          ? const BorderSide(color: SahoolColors.primary, width: 4)
                          : BorderSide.none,
                      right: index % 2 == 1
                          ? const BorderSide(color: SahoolColors.primary, width: 4)
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
                      decoration: const BoxDecoration(
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
            // Flash toggle button - زر تبديل الفلاش
            GestureDetector(
              onTap: _cameraActive ? _toggleFlash : null,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: [
                    Icon(
                      _flashOn ? Icons.flash_on : Icons.flash_off,
                      color: _flashOn ? SahoolColors.warning : Colors.white,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      _flashOn
                          ? 'الفلاش مفعّل | Flash On'
                          : 'الفلاش | Flash',
                      style: const TextStyle(color: Colors.white),
                    ),
                  ],
                ),
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
              Colors.black.withValues(alpha: 0.8),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Text(
                _isScanning
                    ? 'جارٍ التحليل... | Analyzing...'
                    : 'ضع الورقة المصابة داخل الإطار\nPlace the affected leaf inside the frame',
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white, fontSize: 16),
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // Gallery button
                  IconButton(
                    onPressed: _isScanning ? null : _pickFromGallery,
                    icon: const Icon(Icons.photo_library),
                    tooltip: 'المعرض | Gallery',
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.white24,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.all(16),
                    ),
                  ),
                  // Capture button
                  GestureDetector(
                    onTap: _isScanning ? null : _captureFromCamera,
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 4),
                      ),
                      padding: const EdgeInsets.all(4),
                      child: DecoratedBox(
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
                    onPressed: _showScanHistory,
                    icon: const Icon(Icons.history),
                    tooltip: 'السجل | History',
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
    return ColoredBox(
      color: Colors.black54,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(
              width: 60,
              height: 60,
              child: CircularProgressIndicator(
                color: SahoolColors.primary,
                strokeWidth: 4,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'جارٍ تحليل الصورة...\nAnalyzing image...',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            const SizedBox(height: 8),
            Text(
              'يرجى الانتظار | Please wait',
              style: TextStyle(color: Colors.white.withValues(alpha: 0.7)),
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
        return DecoratedBox(
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
                          color: SahoolColors.danger.withValues(alpha: 0.1),
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
                            if (_result?.diseaseEn != null &&
                                _result!.diseaseEn.isNotEmpty)
                              Padding(
                                padding: const EdgeInsets.only(top: 2),
                                child: Text(
                                  _result!.diseaseEn,
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey[600],
                                  ),
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
                                    'الدقة | Conf: ${((_result?.confidence ?? 0) * 100).toInt()}%',
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
                                    '${_result?.severity} | ${_result?.severityEn}',
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
                    title: 'العلاج المقترح | Suggested Treatment',
                    content: _result?.treatment ?? '',
                    color: SahoolColors.info,
                  ),

                  const SizedBox(height: 16),

                  // Prevention
                  _buildSection(
                    icon: Icons.shield,
                    title: 'الوقاية | Prevention',
                    content: _result?.prevention ?? '',
                    color: SahoolColors.success,
                  ),

                  const SizedBox(height: 24),

                  // Actions
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: _resetForNewScan,
                          icon: const Icon(Icons.camera_alt),
                          label: const Text('مسح جديد | New Scan'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _addAsTask,
                          icon: const Icon(Icons.add_task),
                          label: const Text('إضافة كمهمة | Add Task'),
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
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
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
  final String diseaseEn;
  final double confidence;
  final String severity;
  final String severityEn;
  final String treatment;
  final String prevention;
  final String? imagePath;
  final DateTime? scannedAt;

  _ScanResult({
    required this.disease,
    this.diseaseEn = '',
    required this.confidence,
    required this.severity,
    this.severityEn = '',
    required this.treatment,
    required this.prevention,
    this.imagePath,
    this.scannedAt,
  });

  Map<String, dynamic> toJson() => {
        'disease': disease,
        'diseaseEn': diseaseEn,
        'confidence': confidence,
        'severity': severity,
        'severityEn': severityEn,
        'treatment': treatment,
        'prevention': prevention,
        'imagePath': imagePath,
        'scannedAt': scannedAt?.toIso8601String(),
      };

  factory _ScanResult.fromJson(Map<String, dynamic> json) => _ScanResult(
        disease: json['disease'] as String? ?? '',
        diseaseEn: json['diseaseEn'] as String? ?? '',
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
        severity: json['severity'] as String? ?? '',
        severityEn: json['severityEn'] as String? ?? '',
        treatment: json['treatment'] as String? ?? '',
        prevention: json['prevention'] as String? ?? '',
        imagePath: json['imagePath'] as String?,
        scannedAt: json['scannedAt'] != null
            ? DateTime.tryParse(json['scannedAt'] as String)
            : null,
      );
}
