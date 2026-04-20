/// DateIntervalChips — pick the cadence (every 3 / 7 / 14 / 30 days)
/// for the multi-date mobile views.
/// شريحات اختيار الفاصل الزمني
///
/// Mirrors the web `IntervalStepSelector`. Writes to
/// [intervalStepProvider] so the filmstrip sheet + composite chart +
/// multi-date compare all refetch together when the cadence changes.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../presentation/providers/filmstrip_provider.dart';

class DateIntervalChips extends ConsumerWidget {
  /// When `true`, shows both English and Arabic labels on each chip.
  /// Defaults to true — the web equivalent does the same because the
  /// farmer-facing UX is intentionally bilingual.
  final bool bilingual;

  /// Disables all chips (e.g. while a filmstrip fetch is in flight).
  final bool disabled;

  /// Override the Riverpod-backed state with explicit callbacks. Used
  /// by widget tests (no provider scope needed) and by callers that
  /// want to drive the chip selection from outside the satellite
  /// feature (e.g. the field-detail screen that keeps its own tab
  /// state).
  final IntervalStep? value;
  final ValueChanged<IntervalStep>? onChanged;

  const DateIntervalChips({
    super.key,
    this.bilingual = true,
    this.disabled = false,
    this.value,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Explicit controlled mode wins when both are supplied; otherwise
    // fall back to the shared interval provider.
    final active = value ?? ref.watch(intervalStepProvider);
    final theme = Theme.of(context);

    void select(IntervalStep step) {
      if (disabled || step == active) return;
      if (onChanged != null) {
        onChanged!(step);
      } else {
        ref.read(intervalStepProvider.notifier).state = step;
      }
    }

    return Semantics(
      container: true,
      label: 'Interval step',
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        key: const Key('date-interval-chips'),
        children: IntervalStep.values.map((step) {
          final isActive = step == active;
          return ChoiceChip(
            key: Key('interval-step-${step.days}'),
            label: Text(
              bilingual ? '${step.labelEn} · ${step.labelAr}' : step.labelEn,
              style: TextStyle(
                color: isActive ? Colors.white : theme.textTheme.bodyMedium?.color,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
            selected: isActive,
            onSelected: disabled ? null : (_) => select(step),
            selectedColor: Colors.green.shade700,
            backgroundColor: theme.colorScheme.surface,
            side: BorderSide(
              color: isActive ? Colors.green.shade700 : Colors.grey.shade300,
            ),
            showCheckmark: false,
          );
        }).toList(),
      ),
    );
  }
}
