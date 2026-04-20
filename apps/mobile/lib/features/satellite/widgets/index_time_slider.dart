/// IndexTimeSlider — mobile-equivalent of the web `IndexTimeSlider`.
/// Native-Slider scrubber with prev/next chevrons that drives a
/// single `DateTime` selection across the map layer, legend, and
/// inspector — EOSDA's "time scrubber" pattern.
/// الشريط الزمني للمؤشر — منزلق لتنقّل التواريخ
///
/// Display-only — parent supplies the list of available ISO dates.
/// Writes the chosen date through [onChanged] (controlled mode) or
/// [selectedDateProvider] when [onChanged] is null.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../presentation/providers/filmstrip_provider.dart';

class IndexTimeSlider extends ConsumerWidget {
  /// Available acquisition dates. The widget sorts internally so the
  /// caller doesn't need to hand-sort them.
  final List<DateTime> dates;

  /// Currently selected date. When null, defaults to the last (most
  /// recent) entry of [dates].
  final DateTime? value;

  /// Emit the newly selected date. When null, the widget falls back
  /// to writing [selectedDateProvider] directly.
  final ValueChanged<DateTime>? onChanged;

  /// Disables all controls while tiles are loading.
  final bool disabled;

  const IndexTimeSlider({
    super.key,
    required this.dates,
    this.value,
    this.onChanged,
    this.disabled = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (dates.isEmpty) {
      return Padding(
        padding: const EdgeInsets.all(8),
        child: Center(
          key: const Key('index-time-slider-empty'),
          child: Text(
            'No acquisitions · لا توجد بيانات',
            style: TextStyle(color: Colors.grey.shade500, fontSize: 12),
          ),
        ),
      );
    }

    final sorted = [...dates]..sort();
    final current = value ?? sorted.last;
    final currentIdx = () {
      for (var i = 0; i < sorted.length; i++) {
        if (_sameDay(sorted[i], current)) return i;
      }
      return sorted.length - 1;
    }();

    void go(int nextIdx) {
      if (disabled) return;
      final bounded = nextIdx.clamp(0, sorted.length - 1);
      final chosen = sorted[bounded];
      if (_sameDay(chosen, current)) return;
      if (onChanged != null) {
        onChanged!(chosen);
      } else {
        ref.read(selectedDateProvider.notifier).state = chosen;
      }
    }

    final canPrev = !disabled && currentIdx > 0;
    final canNext = !disabled && currentIdx < sorted.length - 1;

    return Container(
      key: const Key('index-time-slider'),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface.withOpacity(0.95),
        borderRadius: BorderRadius.circular(10),
        boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4)],
      ),
      child: Row(
        children: [
          IconButton(
            key: const Key('index-time-prev'),
            icon: const Icon(Icons.chevron_left),
            tooltip: 'Previous · السابق',
            onPressed: canPrev ? () => go(currentIdx - 1) : null,
          ),
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Slider(
                  key: const Key('index-time-range'),
                  value: currentIdx.toDouble(),
                  min: 0,
                  max: (sorted.length - 1).toDouble(),
                  divisions: sorted.length > 1 ? sorted.length - 1 : null,
                  label: _formatCompact(sorted[currentIdx]),
                  onChanged: disabled
                      ? null
                      : (v) => go(v.round()),
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      _formatCompact(sorted.first),
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey.shade600,
                      ),
                    ),
                    Text(
                      _formatCompact(sorted[currentIdx]),
                      key: const Key('index-time-current'),
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      _formatCompact(sorted.last),
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          IconButton(
            key: const Key('index-time-next'),
            icon: const Icon(Icons.chevron_right),
            tooltip: 'Next · التالي',
            onPressed: canNext ? () => go(currentIdx + 1) : null,
          ),
        ],
      ),
    );
  }

  static String _formatCompact(DateTime d) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    return '${d.day.toString().padLeft(2, '0')} ${months[d.month - 1]}';
  }

  static bool _sameDay(DateTime a, DateTime b) =>
      a.year == b.year && a.month == b.month && a.day == b.day;
}
