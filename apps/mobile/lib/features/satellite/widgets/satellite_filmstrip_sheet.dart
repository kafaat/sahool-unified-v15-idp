/// SatelliteFilmstripSheet — bottom sheet with a horizontal PageView
/// of per-date thumbnails. Mirrors the web `IndexFilmstrip` carousel
/// so mobile + web users see the same "scroll through acquisitions"
/// UX (EOSDA / OneSoil parity).
/// نافذة سفلية بـcarousel لعدة تواريخ
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/models/index_filmstrip.dart';
import '../presentation/providers/filmstrip_provider.dart';
import 'date_interval_chips.dart';

/// Static helper to open the sheet. Keeps call sites terse:
///
///     SatelliteFilmstripSheet.show(context, fieldId: 'F123', indexName: 'ndvi');
class SatelliteFilmstripSheet extends ConsumerWidget {
  final String fieldId;
  final String indexName;

  const SatelliteFilmstripSheet({
    super.key,
    required this.fieldId,
    required this.indexName,
  });

  /// Opens the sheet at ~75% height. Returns the date the user tapped
  /// when the sheet is dismissed (or null if they swiped away without
  /// selecting). The sheet also writes the tapped date to
  /// [selectedDateProvider] so observers don't need to await the
  /// future.
  static Future<DateTime?> show(
    BuildContext context, {
    required String fieldId,
    required String indexName,
  }) {
    return showModalBottomSheet<DateTime?>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) => FractionallySizedBox(
        heightFactor: 0.75,
        child: SatelliteFilmstripSheet(fieldId: fieldId, indexName: indexName),
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final step = ref.watch(intervalStepProvider);
    final args = FilmstripArgs(
      fieldId: fieldId,
      indexName: indexName,
      stepDays: step.days,
    );
    final filmstrip = ref.watch(filmstripProvider(args));
    final selected = ref.watch(selectedDateProvider);

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _Header(indexName: indexName),
          const SizedBox(height: 8),
          const DateIntervalChips(),
          const SizedBox(height: 12),
          Expanded(
            child: filmstrip.when(
              loading: () => const Center(
                key: Key('filmstrip-loading'),
                child: CircularProgressIndicator(),
              ),
              error: (err, _) => Center(
                key: const Key('filmstrip-error'),
                child: Text(
                  'فشل تحميل الشريط | $err',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.red),
                ),
              ),
              data: (data) => _FilmstripCarousel(
                key: const Key('filmstrip-carousel'),
                data: data,
                selectedDate: selected,
                onSelect: (date) {
                  ref.read(selectedDateProvider.notifier).state = date;
                  Navigator.of(context).pop(date);
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final String indexName;
  const _Header({required this.indexName});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          indexName.toUpperCase(),
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(width: 8),
        const Text('· شريط الصور', style: TextStyle(color: Colors.grey)),
        const Spacer(),
        IconButton(
          icon: const Icon(Icons.close),
          tooltip: 'Close | إغلاق',
          onPressed: () => Navigator.of(context).maybePop(),
        ),
      ],
    );
  }
}

class _FilmstripCarousel extends StatefulWidget {
  final IndexFilmstrip data;
  final DateTime? selectedDate;
  final void Function(DateTime date) onSelect;

  const _FilmstripCarousel({
    super.key,
    required this.data,
    required this.onSelect,
    this.selectedDate,
  });

  @override
  State<_FilmstripCarousel> createState() => _FilmstripCarouselState();
}

class _FilmstripCarouselState extends State<_FilmstripCarousel> {
  late final PageController _controller;

  @override
  void initState() {
    super.initState();
    // Start on the selected page if any, else on the last frame (latest
    // acquisition) — the most common user intent.
    final initialPage = _resolveInitialPage();
    _controller = PageController(viewportFraction: 0.75, initialPage: initialPage);
  }

  int _resolveInitialPage() {
    if (widget.data.frames.isEmpty) return 0;
    if (widget.selectedDate != null) {
      final target = widget.selectedDate!;
      for (var i = 0; i < widget.data.frames.length; i++) {
        if (_sameDay(widget.data.frames[i].date, target)) return i;
      }
    }
    return widget.data.frames.length - 1;
  }

  bool _sameDay(DateTime a, DateTime b) =>
      a.year == b.year && a.month == b.month && a.day == b.day;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final frames = widget.data.frames;
    if (frames.isEmpty) {
      return const Center(
        key: Key('filmstrip-empty'),
        child: Text('لا توجد بيانات · No acquisitions'),
      );
    }

    return Column(
      children: [
        Text(
          '${frames.length} frame${frames.length == 1 ? '' : 's'} · '
          'كل ${widget.data.stepDays} يوم',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey.shade700,
              ),
        ),
        const SizedBox(height: 8),
        Expanded(
          child: PageView.builder(
            key: const Key('filmstrip-pageview'),
            controller: _controller,
            itemCount: frames.length,
            itemBuilder: (_, idx) {
              final frame = frames[idx];
              final active = widget.selectedDate != null &&
                  _sameDay(frame.date, widget.selectedDate!);
              return _FilmstripPage(
                frame: frame,
                colorScale: widget.data.colorScale,
                active: active,
                onTap: () => widget.onSelect(frame.date),
              );
            },
          ),
        ),
      ],
    );
  }
}

class _FilmstripPage extends StatelessWidget {
  final FilmstripFrame frame;
  final IndexColorScale colorScale;
  final bool active;
  final VoidCallback onTap;

  const _FilmstripPage({
    required this.frame,
    required this.colorScale,
    required this.active,
    required this.onTap,
  });

  Color _tile() {
    final hex = colorScale.sample(frame.value);
    if (hex == null) return Colors.grey.shade300;
    return _parseHex(hex);
  }

  static Color _parseHex(String hex) {
    final cleaned = hex.replaceAll('#', '');
    final value = int.tryParse(cleaned, radix: 16) ?? 0xFF888888;
    return Color(0xFF000000 | value);
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 6),
      child: InkWell(
        key: Key('filmstrip-frame-${frame.date.toIso8601String().substring(0, 10)}'),
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: active ? Colors.green.shade600 : Colors.grey.shade300,
              width: active ? 2 : 1,
            ),
          ),
          child: Column(
            children: [
              Expanded(
                child: Container(
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: _tile(),
                    borderRadius: const BorderRadius.vertical(
                      top: Radius.circular(12),
                    ),
                  ),
                  child: Center(
                    child: Text(
                      frame.value == null ? '—' : frame.value!.toStringAsFixed(2),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 36,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      frame.date.toIso8601String().substring(0, 10),
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(frame.status.en,
                            style: const TextStyle(fontSize: 12)),
                        Text(frame.status.ar,
                            style: const TextStyle(fontSize: 12)),
                      ],
                    ),
                    if (frame.cloudCover != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(
                          '☁ ${frame.cloudCover!.toStringAsFixed(0)}%',
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.grey.shade600,
                          ),
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
