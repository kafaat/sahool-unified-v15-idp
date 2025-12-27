/// Scanner Screen - شاشة الماسح الضوئي
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../providers/inventory_providers.dart';

/// شاشة مسح الباركود للبحث عن عناصر المخزون
class ScannerScreen extends ConsumerStatefulWidget {
  const ScannerScreen({super.key});

  @override
  ConsumerState<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends ConsumerState<ScannerScreen> {
  final MobileScannerController _cameraController = MobileScannerController();
  final TextEditingController _manualInputController = TextEditingController();
  bool _isProcessing = false;
  bool _showManualInput = false;

  @override
  void dispose() {
    _cameraController.dispose();
    _manualInputController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مسح الباركود'),
        actions: [
          IconButton(
            icon: Icon(_cameraController.torchEnabled ? Icons.flash_on : Icons.flash_off),
            onPressed: () => _cameraController.toggleTorch(),
          ),
          IconButton(
            icon: Icon(_showManualInput ? Icons.qr_code_scanner : Icons.keyboard),
            onPressed: () {
              setState(() {
                _showManualInput = !_showManualInput;
              });
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          // الماسح الضوئي
          if (!_showManualInput)
            MobileScanner(
              controller: _cameraController,
              onDetect: _onBarcodeDetected,
            ),

          // إدخال يدوي
          if (_showManualInput)
            Container(
              color: Colors.white,
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.qr_code,
                    size: 100,
                    color: Colors.grey,
                  ),
                  const SizedBox(height: 32),
                  TextField(
                    controller: _manualInputController,
                    decoration: const InputDecoration(
                      labelText: 'أدخل الباركود أو SKU',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.edit),
                    ),
                    autofocus: true,
                    onSubmitted: _onManualInput,
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () => _onManualInput(_manualInputController.text),
                      child: const Text('بحث'),
                    ),
                  ),
                ],
              ),
            ),

          // إطار المسح
          if (!_showManualInput)
            Center(
              child: Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.white, width: 2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Stack(
                  children: [
                    // زوايا الإطار
                    ..._buildCorners(Colors.green, 4),
                  ],
                ),
              ),
            ),

          // تعليمات
          if (!_showManualInput)
            Positioned(
              bottom: 32,
              left: 0,
              right: 0,
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.7),
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: const Text(
                    'وجّه الكاميرا نحو الباركود',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                    ),
                  ),
                ),
              ),
            ),

          // مؤشر التحميل
          if (_isProcessing)
            Container(
              color: Colors.black.withOpacity(0.5),
              child: const Center(
                child: CircularProgressIndicator(),
              ),
            ),
        ],
      ),
    );
  }

  List<Widget> _buildCorners(Color color, double thickness) {
    const length = 30.0;
    return [
      // أعلى يسار
      Positioned(
        top: 0,
        left: 0,
        child: Container(
          width: length,
          height: thickness,
          color: color,
        ),
      ),
      Positioned(
        top: 0,
        left: 0,
        child: Container(
          width: thickness,
          height: length,
          color: color,
        ),
      ),
      // أعلى يمين
      Positioned(
        top: 0,
        right: 0,
        child: Container(
          width: length,
          height: thickness,
          color: color,
        ),
      ),
      Positioned(
        top: 0,
        right: 0,
        child: Container(
          width: thickness,
          height: length,
          color: color,
        ),
      ),
      // أسفل يسار
      Positioned(
        bottom: 0,
        left: 0,
        child: Container(
          width: length,
          height: thickness,
          color: color,
        ),
      ),
      Positioned(
        bottom: 0,
        left: 0,
        child: Container(
          width: thickness,
          height: length,
          color: color,
        ),
      ),
      // أسفل يمين
      Positioned(
        bottom: 0,
        right: 0,
        child: Container(
          width: length,
          height: thickness,
          color: color,
        ),
      ),
      Positioned(
        bottom: 0,
        right: 0,
        child: Container(
          width: thickness,
          height: length,
          color: color,
        ),
      ),
    ];
  }

  Future<void> _onBarcodeDetected(BarcodeCapture capture) async {
    if (_isProcessing) return;

    final List<Barcode> barcodes = capture.barcodes;
    if (barcodes.isEmpty) return;

    final barcode = barcodes.first.rawValue;
    if (barcode == null || barcode.isEmpty) return;

    setState(() {
      _isProcessing = true;
    });

    await _searchItem(barcode);

    setState(() {
      _isProcessing = false;
    });
  }

  Future<void> _onManualInput(String code) async {
    if (code.isEmpty) return;

    setState(() {
      _isProcessing = true;
    });

    await _searchItem(code);

    setState(() {
      _isProcessing = false;
    });
  }

  Future<void> _searchItem(String code) async {
    try {
      // محاولة البحث بالباركود
      final itemAsync = ref.read(inventoryItemByBarcodeProvider(code));
      await itemAsync.when(
        data: (item) {
          if (mounted) {
            Navigator.pop(context);
            // Navigate to item detail
            // Navigator.push(
            //   context,
            //   MaterialPageRoute(
            //     builder: (_) => ItemDetailScreen(itemId: item.itemId),
            //   ),
            // );
          }
        },
        loading: () {},
        error: (error, stack) async {
          // إذا فشل البحث بالباركود، جرب SKU
          final itemBySku = ref.read(inventoryItemBySkuProvider(code));
          await itemBySku.when(
            data: (item) {
              if (mounted) {
                Navigator.pop(context);
                // Navigate to item detail
              }
            },
            loading: () {},
            error: (error, stack) {
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('لم يتم العثور على العنصر: $code'),
                    backgroundColor: Colors.red,
                  ),
                );
              }
            },
          );
        },
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خطأ في البحث: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
