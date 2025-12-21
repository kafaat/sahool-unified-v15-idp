/// SAHOOL Barcode/QR Scanner Widget
/// ماسح الباركود والـ QR

import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

/// نتيجة المسح
class ScanResult {
  final String value;
  final BarcodeFormat format;
  final DateTime scannedAt;

  ScanResult({
    required this.value,
    required this.format,
    DateTime? scannedAt,
  }) : scannedAt = scannedAt ?? DateTime.now();

  bool get isQrCode => format == BarcodeFormat.qrCode;
  bool get isBarcode => !isQrCode;
}

/// شاشة ماسح الباركود
class BarcodeScannerScreen extends StatefulWidget {
  final String title;
  final String? subtitle;
  final bool allowMultipleScan;
  final List<BarcodeFormat>? formats;

  const BarcodeScannerScreen({
    super.key,
    this.title = 'مسح الباركود',
    this.subtitle,
    this.allowMultipleScan = false,
    this.formats,
  });

  /// فتح الماسح وإرجاع النتيجة
  static Future<ScanResult?> scan(
    BuildContext context, {
    String title = 'مسح الباركود',
    String? subtitle,
    List<BarcodeFormat>? formats,
  }) async {
    return Navigator.of(context).push<ScanResult>(
      MaterialPageRoute(
        builder: (_) => BarcodeScannerScreen(
          title: title,
          subtitle: subtitle,
          formats: formats,
        ),
      ),
    );
  }

  @override
  State<BarcodeScannerScreen> createState() => _BarcodeScannerScreenState();
}

class _BarcodeScannerScreenState extends State<BarcodeScannerScreen> {
  late MobileScannerController _controller;
  bool _isFlashOn = false;
  bool _isFrontCamera = false;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _controller = MobileScannerController(
      detectionSpeed: DetectionSpeed.normal,
      facing: CameraFacing.back,
      torchEnabled: false,
      formats: widget.formats,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_isProcessing) return;

    final barcodes = capture.barcodes;
    if (barcodes.isEmpty) return;

    final barcode = barcodes.first;
    if (barcode.rawValue == null) return;

    _isProcessing = true;

    final result = ScanResult(
      value: barcode.rawValue!,
      format: barcode.format,
    );

    if (widget.allowMultipleScan) {
      _showScanResult(result);
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          setState(() => _isProcessing = false);
        }
      });
    } else {
      Navigator.of(context).pop(result);
    }
  }

  void _showScanResult(ScanResult result) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('تم المسح: ${result.value}'),
        backgroundColor: Colors.green,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _toggleFlash() async {
    await _controller.toggleTorch();
    setState(() => _isFlashOn = !_isFlashOn);
  }

  void _switchCamera() async {
    await _controller.switchCamera();
    setState(() => _isFrontCamera = !_isFrontCamera);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
        title: Text(
          widget.title,
          style: const TextStyle(color: Colors.white),
        ),
        actions: [
          IconButton(
            icon: Icon(_isFlashOn ? Icons.flash_on : Icons.flash_off),
            color: _isFlashOn ? Colors.yellow : Colors.white,
            onPressed: _toggleFlash,
          ),
          IconButton(
            icon: Icon(_isFrontCamera ? Icons.camera_front : Icons.camera_rear),
            color: Colors.white,
            onPressed: _switchCamera,
          ),
        ],
      ),
      body: Stack(
        children: [
          // Scanner
          MobileScanner(
            controller: _controller,
            onDetect: _onDetect,
          ),

          // Overlay
          _buildScannerOverlay(),

          // Instructions
          if (widget.subtitle != null)
            Positioned(
              bottom: 100,
              left: 24,
              right: 24,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  widget.subtitle!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                  ),
                ),
              ),
            ),

          // Processing indicator
          if (_isProcessing)
            Container(
              color: Colors.black54,
              child: const Center(
                child: CircularProgressIndicator(color: Colors.white),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildScannerOverlay() {
    return CustomPaint(
      painter: _ScannerOverlayPainter(),
      child: const SizedBox.expand(),
    );
  }
}

/// رسم إطار الماسح
class _ScannerOverlayPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final scanAreaSize = size.width * 0.7;
    final left = (size.width - scanAreaSize) / 2;
    final top = (size.height - scanAreaSize) / 2;
    final scanRect = Rect.fromLTWH(left, top, scanAreaSize, scanAreaSize);

    // Dark overlay
    final backgroundPath = Path()
      ..addRect(Rect.fromLTWH(0, 0, size.width, size.height));
    final scanPath = Path()..addRRect(RRect.fromRectAndRadius(scanRect, const Radius.circular(16)));
    final overlayPath = Path.combine(PathOperation.difference, backgroundPath, scanPath);

    canvas.drawPath(
      overlayPath,
      Paint()..color = Colors.black54,
    );

    // Corner lines
    final cornerPaint = Paint()
      ..color = Colors.green
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    const cornerLength = 30.0;
    const cornerRadius = 16.0;

    // Top-left corner
    canvas.drawPath(
      Path()
        ..moveTo(left, top + cornerLength)
        ..lineTo(left, top + cornerRadius)
        ..arcToPoint(Offset(left + cornerRadius, top), radius: const Radius.circular(cornerRadius))
        ..lineTo(left + cornerLength, top),
      cornerPaint,
    );

    // Top-right corner
    canvas.drawPath(
      Path()
        ..moveTo(left + scanAreaSize - cornerLength, top)
        ..lineTo(left + scanAreaSize - cornerRadius, top)
        ..arcToPoint(Offset(left + scanAreaSize, top + cornerRadius), radius: const Radius.circular(cornerRadius))
        ..lineTo(left + scanAreaSize, top + cornerLength),
      cornerPaint,
    );

    // Bottom-left corner
    canvas.drawPath(
      Path()
        ..moveTo(left, top + scanAreaSize - cornerLength)
        ..lineTo(left, top + scanAreaSize - cornerRadius)
        ..arcToPoint(Offset(left + cornerRadius, top + scanAreaSize), radius: const Radius.circular(cornerRadius))
        ..lineTo(left + cornerLength, top + scanAreaSize),
      cornerPaint,
    );

    // Bottom-right corner
    canvas.drawPath(
      Path()
        ..moveTo(left + scanAreaSize - cornerLength, top + scanAreaSize)
        ..lineTo(left + scanAreaSize - cornerRadius, top + scanAreaSize)
        ..arcToPoint(Offset(left + scanAreaSize, top + scanAreaSize - cornerRadius), radius: const Radius.circular(cornerRadius))
        ..lineTo(left + scanAreaSize, top + scanAreaSize - cornerLength),
      cornerPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// Widget صغير لزر المسح
class ScanButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final String label;
  final IconData icon;

  const ScanButton({
    super.key,
    this.onPressed,
    this.label = 'مسح',
    this.icon = Icons.qr_code_scanner,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon),
      label: Text(label),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }
}
