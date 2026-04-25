/// PixelInspectorSheet — mobile-equivalent of the web
/// `PixelInspectorPopup`. Bottom sheet showing every computed index
/// at the tapped pixel, grouped by category and with mappable
/// indices flagged so the farmer knows which can also be rendered
/// as an overlay.
/// نافذة فحص البكسل — تعرض كل المؤشرات عند النقطة المنقور عليها
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/models/index_filmstrip.dart';
import '../presentation/providers/filmstrip_provider.dart';

/// Same category groupings as the web popup — kept in sync so farmers
/// see identical organisation across surfaces.
class _Category {
  final String key;
  final String titleEn;
  final String titleAr;
  final List<String> indices;

  const _Category(this.key, this.titleEn, this.titleAr, this.indices);
}

const List<_Category> _kCategories = [
  _Category(
    'core',
    'Core',
    'الأساسية',
    ['ndvi', 'ndre', 'evi', 'savi', 'lai', 'gndvi'],
  ),
  _Category(
    'water',
    'Water',
    'المياه',
    ['ndwi', 'ndmi', 'msi', 'mndwi'],
  ),
  _Category(
    'chlorophyll',
    'Chlorophyll & Nitrogen',
    'الكلوروفيل والنيتروجين',
    ['mcari', 'tcari', 'sipi', 'cvi', 'ci_green', 'ci_rededge', 'mtci', 'ireci', 'rendvi'],
  ),
  _Category(
    'stress',
    'Stress & Senescence',
    'الإجهاد والشيخوخة',
    ['pri', 'psri', 'cri', 'ari', 'rep'],
  ),
  _Category(
    'productivity',
    'Productivity',
    'الإنتاجية',
    ['fpar', 'fapar', 'ccci', 'wdrvi'],
  ),
  _Category(
    'soil_burn',
    'Soil & Burn',
    'التربة والحرائق',
    ['bsi', 'nbr', 'nbr2', 'ndbi', 'soc'],
  ),
];

String _formatValue(double? v) {
  if (v == null || v.isNaN) return '—';
  final abs = v.abs();
  final digits = abs >= 100 ? 0 : abs >= 10 ? 1 : 3;
  return v.toStringAsFixed(digits);
}

class PixelInspectorSheet extends ConsumerWidget {
  const PixelInspectorSheet({super.key});

  /// Opens the sheet for the pixel set in [activePixelProbeProvider].
  /// Use `ref.read(activePixelProbeProvider.notifier).state = PixelProbe(...)`
  /// first, then call `show(context)`.
  static Future<void> show(BuildContext context) {
    return showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (_) => const FractionallySizedBox(
        heightFactor: 0.75,
        child: PixelInspectorSheet(),
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final probe = ref.watch(activePixelProbeProvider);
    if (probe == null) {
      return const Padding(
        padding: EdgeInsets.all(24),
        child: Center(
          key: Key('pixel-inspector-no-probe'),
          child: Text('اضغط على أي نقطة للفحص · Tap any pixel to inspect'),
        ),
      );
    }
    final result = ref.watch(pixelInspectionProvider(probe));
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _Header(probe: probe),
          const SizedBox(height: 8),
          Expanded(
            child: result.when(
              loading: () => const Center(
                key: Key('pixel-inspector-loading'),
                child: CircularProgressIndicator(),
              ),
              error: (err, _) => Center(
                key: const Key('pixel-inspector-error'),
                child: Text(
                  'فشل الفحص | $err',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.red),
                ),
              ),
              data: (data) => _InspectionBody(data: data),
            ),
          ),
        ],
      ),
    );
  }
}

class _Header extends ConsumerWidget {
  final PixelProbe probe;
  const _Header({required this.probe});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Pixel Inspector · فحص البكسل',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              Text(
                '${probe.lat.toStringAsFixed(5)}, ${probe.lon.toStringAsFixed(5)}',
                style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
              ),
            ],
          ),
        ),
        IconButton(
          icon: const Icon(Icons.close),
          tooltip: 'Close | إغلاق',
          onPressed: () {
            ref.read(activePixelProbeProvider.notifier).state = null;
            Navigator.of(context).maybePop();
          },
        ),
      ],
    );
  }
}

class _InspectionBody extends StatelessWidget {
  final PixelInspection data;
  const _InspectionBody({required this.data});

  @override
  Widget build(BuildContext context) {
    final mappable = data.mappable.toSet();
    return ListView(
      key: const Key('pixel-inspector-body'),
      children: [
        Text(
          '${data.date.toIso8601String().substring(0, 10)} · ${data.satellite.toUpperCase()}',
          style: TextStyle(color: Colors.grey.shade700, fontSize: 12),
        ),
        const SizedBox(height: 12),
        for (final cat in _kCategories) _buildCategory(cat, mappable),
        const SizedBox(height: 4),
        Text(
          '● = قابل للعرض كطبقة · mappable as a raster overlay',
          style: TextStyle(color: Colors.grey.shade600, fontSize: 10),
        ),
      ],
    );
  }

  Widget _buildCategory(_Category cat, Set<String> mappable) {
    final rows = <Widget>[];
    for (final name in cat.indices) {
      if (!data.indices.containsKey(name)) continue;
      final value = data.indices[name];
      final isMap = mappable.contains(name);
      rows.add(_row(name, value, isMap));
    }
    if (rows.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                cat.titleEn,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
              Text(
                cat.titleAr,
                style: TextStyle(
                  color: Colors.grey.shade700,
                  fontSize: 13,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ...rows,
        ],
      ),
    );
  }

  Widget _row(String name, double? value, bool isMap) {
    return Padding(
      key: Key('pixel-index-$name'),
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '${name.toUpperCase()}${isMap ? ' ●' : ''}',
            style: TextStyle(
              fontSize: 12,
              fontWeight: isMap ? FontWeight.w600 : FontWeight.w400,
              color: isMap ? Colors.green.shade800 : Colors.grey.shade800,
              letterSpacing: 0.5,
            ),
          ),
          Text(
            _formatValue(value),
            style: TextStyle(
              fontSize: 12,
              fontFamily: 'monospace',
              color: value == null ? Colors.grey.shade400 : Colors.black87,
            ),
          ),
        ],
      ),
    );
  }
}
