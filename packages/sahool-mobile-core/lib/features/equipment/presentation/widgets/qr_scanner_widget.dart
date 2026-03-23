/// QR Scanner Widget - ماسح رمز QR للمعدات
/// Equipment-specific QR code scanner
library;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/widgets/barcode_scanner_widget.dart';
import '../../state/equipment_providers.dart';

/// Equipment QR Scanner Button
class EquipmentQRScannerButton extends ConsumerWidget {
  final void Function(Equipment equipment)? onEquipmentFound;
  final VoidCallback? onError;
  final bool showLabel;

  const EquipmentQRScannerButton({
    super.key,
    this.onEquipmentFound,
    this.onError,
    this.showLabel = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ElevatedButton.icon(
      onPressed: () => _scanQRCode(context, ref),
      icon: const Icon(Icons.qr_code_scanner),
      label: showLabel ? const Text('مسح QR') : const SizedBox.shrink(),
      style: ElevatedButton.styleFrom(
        backgroundColor: SahoolColors.forestGreen,
        foregroundColor: Colors.white,
        padding: EdgeInsets.symmetric(
          horizontal: showLabel ? 20 : 16,
          vertical: 12,
        ),
      ),
    );
  }

  Future<void> _scanQRCode(BuildContext context, WidgetRef ref) async {
    final result = await BarcodeScannerScreen.scan(
      context,
      title: 'مسح رمز المعدة',
      subtitle: 'وجّه الكاميرا نحو رمز QR الموجود على المعدة',
    );

    if (result != null && context.mounted) {
      final qrCode = result.value;

      // Show loading indicator
      _showLoadingDialog(context);

      // Try to find equipment by QR code
      final repo = ref.read(equipmentRepositoryProvider);
      final apiResult = await repo.getEquipmentByQrCode(qrCode);

      if (context.mounted) {
        Navigator.pop(context); // Close loading dialog

        if (apiResult.isSuccess && apiResult.data != null) {
          onEquipmentFound?.call(apiResult.data!);
        } else {
          // Try local database
          final localDb = ref.read(equipmentLocalDbProvider);
          final localEquipment = await localDb.getEquipmentByQrCode(qrCode);

          if (localEquipment != null) {
            onEquipmentFound?.call(localEquipment);
          } else {
            _showNotFoundDialog(context, qrCode);
            onError?.call();
          }
        }
      }
    }
  }

  void _showLoadingDialog(BuildContext context) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: Card(
          child: Padding(
            padding: EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircularProgressIndicator(
                  color: SahoolColors.forestGreen,
                ),
                SizedBox(height: 16),
                Text('جاري البحث عن المعدة...'),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showNotFoundDialog(BuildContext context, String qrCode) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.error_outline, color: SahoolColors.danger),
            SizedBox(width: 8),
            Text('المعدة غير موجودة'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('لم يتم العثور على معدة مرتبطة بهذا الرمز.'),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.qr_code, size: 16, color: Colors.grey),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      qrCode,
                      style: TextStyle(
                        fontFamily: 'monospace',
                        color: Colors.grey[700],
                        fontSize: 12,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('حسنا'),
          ),
        ],
      ),
    );
  }
}

/// Floating QR Scanner FAB
class EquipmentQRFAB extends ConsumerWidget {
  final void Function(Equipment equipment)? onEquipmentFound;

  const EquipmentQRFAB({
    super.key,
    this.onEquipmentFound,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FloatingActionButton(
      onPressed: () => _scanQRCode(context, ref),
      backgroundColor: SahoolColors.forestGreen,
      child: const Icon(Icons.qr_code_scanner),
    );
  }

  Future<void> _scanQRCode(BuildContext context, WidgetRef ref) async {
    final result = await BarcodeScannerScreen.scan(
      context,
      title: 'مسح رمز المعدة',
      subtitle: 'وجّه الكاميرا نحو رمز QR الموجود على المعدة',
    );

    if (result != null && context.mounted) {
      final qrCode = result.value;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Row(
            children: [
              SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              ),
              SizedBox(width: 12),
              Text('جاري البحث عن المعدة...'),
            ],
          ),
          duration: Duration(seconds: 2),
        ),
      );

      final repo = ref.read(equipmentRepositoryProvider);
      final apiResult = await repo.getEquipmentByQrCode(qrCode);

      if (context.mounted) {
        if (apiResult.isSuccess && apiResult.data != null) {
          ScaffoldMessenger.of(context).hideCurrentSnackBar();
          onEquipmentFound?.call(apiResult.data!);
        } else {
          // Try local
          final localDb = ref.read(equipmentLocalDbProvider);
          final localEquipment = await localDb.getEquipmentByQrCode(qrCode);

          if (localEquipment != null) {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
            onEquipmentFound?.call(localEquipment);
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('المعدة غير موجودة'),
                backgroundColor: SahoolColors.danger,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
        }
      }
    }
  }
}

/// QR Code Display Widget
class EquipmentQRDisplay extends StatelessWidget {
  final String qrCode;
  final String? equipmentName;
  final VoidCallback? onShare;
  final VoidCallback? onPrint;

  const EquipmentQRDisplay({
    super.key,
    required this.qrCode,
    this.equipmentName,
    this.onShare,
    this.onPrint,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // QR Code placeholder (would use qr_flutter in production)
          Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey[300]!),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.qr_code_2,
                  size: 120,
                  color: SahoolColors.forestGreen,
                ),
                const SizedBox(height: 8),
                Text(
                  'QR Code',
                  style: TextStyle(
                    color: Colors.grey[500],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Equipment name
          if (equipmentName != null) ...[
            Text(
              equipmentName!,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 4),
          ],

          // QR code value
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              qrCode,
              style: TextStyle(
                fontFamily: 'monospace',
                color: Colors.grey[700],
                fontSize: 12,
              ),
            ),
          ),

          // Action buttons
          if (onShare != null || onPrint != null) ...[
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (onShare != null)
                  IconButton(
                    onPressed: onShare,
                    icon: const Icon(Icons.share),
                    tooltip: 'مشاركة',
                  ),
                if (onPrint != null)
                  IconButton(
                    onPressed: onPrint,
                    icon: const Icon(Icons.print),
                    tooltip: 'طباعة',
                  ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
