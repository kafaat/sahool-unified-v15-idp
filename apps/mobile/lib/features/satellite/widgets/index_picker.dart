/// IndexPicker — mobile-equivalent of the web `IndexPicker`. Lets the
/// farmer switch the active raster overlay between the 6 mappable
/// indices (NDVI / NDRE / NDWI / EVI / SAVI / LAI).
/// مُنتقي المؤشر — للتبديل بين المؤشرات الستة القابلة للعرض
///
/// Writes through to [selectedIndexProvider] so observers (map overlay,
/// legend, filmstrip sheet, pixel inspector) all react together.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../presentation/providers/filmstrip_provider.dart';

class IndexPicker extends ConsumerWidget {
  /// Show both English and Arabic labels on each chip. Defaults to true —
  /// the web surface does the same so farmer-facing UX stays bilingual.
  final bool bilingual;

  /// Disable the whole picker (e.g. while a tile fetch is in flight).
  final bool disabled;

  /// Controlled-mode overrides. Used by widget tests and by callers
  /// that want to drive the selection outside the satellite feature.
  final MappableIndex? value;
  final ValueChanged<MappableIndex>? onChanged;

  const IndexPicker({
    super.key,
    this.bilingual = true,
    this.disabled = false,
    this.value,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final active = value ?? ref.watch(selectedIndexProvider);

    void select(MappableIndex idx) {
      if (disabled || idx == active) return;
      if (onChanged != null) {
        onChanged!(idx);
      } else {
        ref.read(selectedIndexProvider.notifier).state = idx;
      }
    }

    return Semantics(
      container: true,
      label: 'Vegetation index selector',
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        key: const Key('index-picker'),
        child: Row(
          children: [
            for (final idx in MappableIndex.values)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: ChoiceChip(
                  key: Key('index-picker-${idx.apiName}'),
                  selected: idx == active,
                  onSelected: disabled ? null : (_) => select(idx),
                  selectedColor: Colors.green.shade700,
                  backgroundColor: Theme.of(context).colorScheme.surface,
                  showCheckmark: false,
                  side: BorderSide(
                    color: idx == active
                        ? Colors.green.shade700
                        : Colors.grey.shade300,
                  ),
                  label: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 10,
                        height: 10,
                        margin: const EdgeInsets.only(right: 6),
                        decoration: BoxDecoration(
                          color: Color(idx.swatchArgb),
                          shape: BoxShape.circle,
                        ),
                      ),
                      Text(
                        idx.labelEn,
                        style: TextStyle(
                          color: idx == active
                              ? Colors.white
                              : Theme.of(context).textTheme.bodyMedium?.color,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      if (bilingual) ...[
                        const SizedBox(width: 4),
                        Text(
                          '· ${idx.labelAr}',
                          style: TextStyle(
                            color: idx == active
                                ? Colors.white70
                                : Colors.grey.shade600,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
