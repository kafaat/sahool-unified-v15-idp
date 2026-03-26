/// SAHOOL Haptic Feedback Widgets
/// أدوات الاهتزاز للتغذية اللمسية
///
/// Provides pre-built widgets with haptic feedback:
/// - HapticButton
/// - HapticListTile
/// - HapticSlider
/// - HapticIconButton
/// - HapticInkWell
/// - Extension methods for adding haptics to any widget
library;

import 'package:flutter/material.dart';

import 'haptic_config.dart';
import 'haptic_patterns.dart';
import 'haptic_service.dart';

// ═══════════════════════════════════════════════════════════════════════════
// HapticButton
// ═══════════════════════════════════════════════════════════════════════════

/// A button with built-in haptic feedback
/// زر مع اهتزاز مدمج
class HapticButton extends StatelessWidget {
  /// The callback that is called when the button is tapped
  final VoidCallback? onPressed;

  /// The callback that is called when the button is long-pressed
  final VoidCallback? onLongPress;

  /// The child widget
  final Widget child;

  /// The haptic pattern to use
  final HapticPattern hapticPattern;

  /// The haptic pattern to use on long press
  final HapticPattern? longPressPattern;

  /// Button style
  final ButtonStyle? style;

  /// Whether this is a destructive action
  final bool isDestructive;

  /// Whether to enable haptic feedback
  final bool enableHaptic;

  const HapticButton({
    super.key,
    required this.onPressed,
    required this.child,
    this.onLongPress,
    this.hapticPattern = HapticPattern.mediumTap,
    this.longPressPattern,
    this.style,
    this.isDestructive = false,
    this.enableHaptic = true,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  isDestructive ? HapticPattern.heavyTap : hapticPattern,
                  category: HapticCategory.button,
                );
              }
              onPressed!();
            }
          : null,
      onLongPress: onLongPress != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  longPressPattern ?? HapticPattern.heavyTap,
                  category: HapticCategory.button,
                );
              }
              onLongPress!();
            }
          : null,
      style: style,
      child: child,
    );
  }

  /// Create a text button variant
  static Widget text({
    Key? key,
    required VoidCallback? onPressed,
    required Widget child,
    VoidCallback? onLongPress,
    HapticPattern hapticPattern = HapticPattern.lightTap,
    ButtonStyle? style,
    bool enableHaptic = true,
  }) {
    return TextButton(
      key: key,
      onPressed: onPressed != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  hapticPattern,
                  category: HapticCategory.button,
                );
              }
              onPressed();
            }
          : null,
      onLongPress: onLongPress != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  HapticPattern.mediumTap,
                  category: HapticCategory.button,
                );
              }
              onLongPress();
            }
          : null,
      style: style,
      child: child,
    );
  }

  /// Create an outlined button variant
  static Widget outlined({
    Key? key,
    required VoidCallback? onPressed,
    required Widget child,
    VoidCallback? onLongPress,
    HapticPattern hapticPattern = HapticPattern.mediumTap,
    ButtonStyle? style,
    bool enableHaptic = true,
  }) {
    return OutlinedButton(
      key: key,
      onPressed: onPressed != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  hapticPattern,
                  category: HapticCategory.button,
                );
              }
              onPressed();
            }
          : null,
      onLongPress: onLongPress != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  HapticPattern.mediumTap,
                  category: HapticCategory.button,
                );
              }
              onLongPress();
            }
          : null,
      style: style,
      child: child,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// HapticIconButton
// ═══════════════════════════════════════════════════════════════════════════

/// An icon button with haptic feedback
/// زر أيقونة مع اهتزاز
class HapticIconButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final Widget icon;
  final HapticPattern hapticPattern;
  final double? iconSize;
  final EdgeInsetsGeometry? padding;
  final Color? color;
  final Color? disabledColor;
  final String? tooltip;
  final bool enableHaptic;

  const HapticIconButton({
    super.key,
    required this.onPressed,
    required this.icon,
    this.hapticPattern = HapticPattern.lightTap,
    this.iconSize,
    this.padding,
    this.color,
    this.disabledColor,
    this.tooltip,
    this.enableHaptic = true,
  });

  @override
  Widget build(BuildContext context) {
    return IconButton(
      onPressed: onPressed != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  hapticPattern,
                  category: HapticCategory.button,
                );
              }
              onPressed!();
            }
          : null,
      icon: icon,
      iconSize: iconSize,
      padding: padding,
      color: color,
      disabledColor: disabledColor,
      tooltip: tooltip,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// HapticListTile
// ═══════════════════════════════════════════════════════════════════════════

/// A list tile with haptic feedback
/// عنصر قائمة مع اهتزاز
class HapticListTile extends StatelessWidget {
  final Widget? leading;
  final Widget? title;
  final Widget? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final bool enabled;
  final bool selected;
  final HapticPattern tapPattern;
  final HapticPattern longPressPattern;
  final EdgeInsetsGeometry? contentPadding;
  final Color? tileColor;
  final Color? selectedTileColor;
  final ShapeBorder? shape;
  final bool enableHaptic;

  const HapticListTile({
    super.key,
    this.leading,
    this.title,
    this.subtitle,
    this.trailing,
    this.onTap,
    this.onLongPress,
    this.enabled = true,
    this.selected = false,
    this.tapPattern = HapticPattern.lightTap,
    this.longPressPattern = HapticPattern.mediumTap,
    this.contentPadding,
    this.tileColor,
    this.selectedTileColor,
    this.shape,
    this.enableHaptic = true,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: leading,
      title: title,
      subtitle: subtitle,
      trailing: trailing,
      enabled: enabled,
      selected: selected,
      contentPadding: contentPadding,
      tileColor: tileColor,
      selectedTileColor: selectedTileColor,
      shape: shape,
      onTap: onTap != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  tapPattern,
                  category: HapticCategory.list,
                );
              }
              onTap!();
            }
          : null,
      onLongPress: onLongPress != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  longPressPattern,
                  category: HapticCategory.list,
                );
              }
              onLongPress!();
            }
          : null,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// HapticSlider
// ═══════════════════════════════════════════════════════════════════════════

/// A slider with haptic feedback at discrete positions
/// منزلق مع اهتزاز عند المواضع المحددة
class HapticSlider extends StatefulWidget {
  final double value;
  final ValueChanged<double>? onChanged;
  final ValueChanged<double>? onChangeStart;
  final ValueChanged<double>? onChangeEnd;
  final double min;
  final double max;
  final int? divisions;
  final String? label;
  final Color? activeColor;
  final Color? inactiveColor;
  final Color? thumbColor;
  final HapticPattern tickPattern;
  final HapticPattern boundaryPattern;
  final bool enableHaptic;
  final bool hapticOnEveryTick;

  const HapticSlider({
    super.key,
    required this.value,
    required this.onChanged,
    this.onChangeStart,
    this.onChangeEnd,
    this.min = 0.0,
    this.max = 1.0,
    this.divisions,
    this.label,
    this.activeColor,
    this.inactiveColor,
    this.thumbColor,
    this.tickPattern = HapticPattern.tick,
    this.boundaryPattern = HapticPattern.impact,
    this.enableHaptic = true,
    this.hapticOnEveryTick = true,
  });

  @override
  State<HapticSlider> createState() => _HapticSliderState();
}

class _HapticSliderState extends State<HapticSlider> {
  double? _lastTickValue;
  bool _atMin = false;
  bool _atMax = false;

  @override
  Widget build(BuildContext context) {
    return Slider(
      value: widget.value,
      min: widget.min,
      max: widget.max,
      divisions: widget.divisions,
      label: widget.label,
      activeColor: widget.activeColor,
      inactiveColor: widget.inactiveColor,
      thumbColor: widget.thumbColor,
      onChangeStart: (value) {
        _lastTickValue = value;
        widget.onChangeStart?.call(value);
      },
      onChanged: widget.onChanged != null
          ? (value) {
              if (widget.enableHaptic) {
                _handleHapticFeedback(value);
              }
              widget.onChanged!(value);
            }
          : null,
      onChangeEnd: (value) {
        _lastTickValue = null;
        _atMin = false;
        _atMax = false;
        widget.onChangeEnd?.call(value);
      },
    );
  }

  void _handleHapticFeedback(double value) {
    // Check for boundary hit
    if (value == widget.min && !_atMin) {
      _atMin = true;
      HapticService.instance.trigger(
        widget.boundaryPattern,
        category: HapticCategory.slider,
      );
      return;
    } else if (value != widget.min) {
      _atMin = false;
    }

    if (value == widget.max && !_atMax) {
      _atMax = true;
      HapticService.instance.trigger(
        widget.boundaryPattern,
        category: HapticCategory.slider,
      );
      return;
    } else if (value != widget.max) {
      _atMax = false;
    }

    // Check for division tick
    if (widget.hapticOnEveryTick && widget.divisions != null) {
      final step = (widget.max - widget.min) / widget.divisions!;
      final currentTick = ((value - widget.min) / step).round();
      final lastTick = _lastTickValue != null
          ? ((_lastTickValue! - widget.min) / step).round()
          : currentTick;

      if (currentTick != lastTick) {
        HapticService.instance.trigger(
          widget.tickPattern,
          category: HapticCategory.slider,
        );
      }
      _lastTickValue = value;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// HapticInkWell
// ═══════════════════════════════════════════════════════════════════════════

/// An InkWell with haptic feedback
/// InkWell مع اهتزاز
class HapticInkWell extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final VoidCallback? onDoubleTap;
  final VoidCallback? onLongPress;
  final HapticPattern tapPattern;
  final HapticPattern doubleTapPattern;
  final HapticPattern longPressPattern;
  final HapticCategory category;
  final BorderRadius? borderRadius;
  final Color? splashColor;
  final Color? highlightColor;
  final bool enableHaptic;

  const HapticInkWell({
    super.key,
    required this.child,
    this.onTap,
    this.onDoubleTap,
    this.onLongPress,
    this.tapPattern = HapticPattern.lightTap,
    this.doubleTapPattern = HapticPattern.mediumTap,
    this.longPressPattern = HapticPattern.heavyTap,
    this.category = HapticCategory.other,
    this.borderRadius,
    this.splashColor,
    this.highlightColor,
    this.enableHaptic = true,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: borderRadius,
      splashColor: splashColor,
      highlightColor: highlightColor,
      onTap: onTap != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(tapPattern, category: category);
              }
              onTap!();
            }
          : null,
      onDoubleTap: onDoubleTap != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(doubleTapPattern, category: category);
              }
              onDoubleTap!();
            }
          : null,
      onLongPress: onLongPress != null
          ? () {
              if (enableHaptic) {
                HapticService.instance.trigger(longPressPattern, category: category);
              }
              onLongPress!();
            }
          : null,
      child: child,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// HapticSwitch
// ═══════════════════════════════════════════════════════════════════════════

/// A switch with haptic feedback
/// مفتاح مع اهتزاز
class HapticSwitch extends StatelessWidget {
  final bool value;
  final ValueChanged<bool>? onChanged;
  final Color? activeColor;
  final Color? activeTrackColor;
  final Color? inactiveThumbColor;
  final Color? inactiveTrackColor;
  final HapticPattern pattern;
  final bool enableHaptic;

  const HapticSwitch({
    super.key,
    required this.value,
    required this.onChanged,
    this.activeColor,
    this.activeTrackColor,
    this.inactiveThumbColor,
    this.inactiveTrackColor,
    this.pattern = HapticPattern.selectionChanged,
    this.enableHaptic = true,
  });

  @override
  Widget build(BuildContext context) {
    return Switch(
      value: value,
      activeColor: activeColor,
      activeTrackColor: activeTrackColor,
      inactiveThumbColor: inactiveThumbColor,
      inactiveTrackColor: inactiveTrackColor,
      onChanged: onChanged != null
          ? (newValue) {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  pattern,
                  category: HapticCategory.form,
                );
              }
              onChanged!(newValue);
            }
          : null,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// HapticCheckbox
// ═══════════════════════════════════════════════════════════════════════════

/// A checkbox with haptic feedback
/// مربع اختيار مع اهتزاز
class HapticCheckbox extends StatelessWidget {
  final bool? value;
  final ValueChanged<bool?>? onChanged;
  final Color? activeColor;
  final Color? checkColor;
  final HapticPattern pattern;
  final bool enableHaptic;
  final bool tristate;

  const HapticCheckbox({
    super.key,
    required this.value,
    required this.onChanged,
    this.activeColor,
    this.checkColor,
    this.pattern = HapticPattern.selectionChanged,
    this.enableHaptic = true,
    this.tristate = false,
  });

  @override
  Widget build(BuildContext context) {
    return Checkbox(
      value: value,
      activeColor: activeColor,
      checkColor: checkColor,
      tristate: tristate,
      onChanged: onChanged != null
          ? (newValue) {
              if (enableHaptic) {
                HapticService.instance.trigger(
                  pattern,
                  category: HapticCategory.form,
                );
              }
              onChanged!(newValue);
            }
          : null,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// HapticRefreshIndicator
// ═══════════════════════════════════════════════════════════════════════════

/// A refresh indicator with haptic feedback when activated
/// مؤشر تحديث مع اهتزاز عند التفعيل
class HapticRefreshIndicator extends StatelessWidget {
  final Widget child;
  final Future<void> Function() onRefresh;
  final Color? color;
  final Color? backgroundColor;
  final double displacement;
  final HapticPattern pattern;
  final bool enableHaptic;

  const HapticRefreshIndicator({
    super.key,
    required this.child,
    required this.onRefresh,
    this.color,
    this.backgroundColor,
    this.displacement = 40.0,
    this.pattern = HapticPattern.mediumTap,
    this.enableHaptic = true,
  });

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      color: color,
      backgroundColor: backgroundColor,
      displacement: displacement,
      onRefresh: () async {
        if (enableHaptic) {
          HapticService.instance.trigger(pattern, category: HapticCategory.gesture);
        }
        await onRefresh();
      },
      child: child,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Extension Methods
// ═══════════════════════════════════════════════════════════════════════════

/// Extension to add haptic feedback to any widget
/// إضافة لإضافة الاهتزاز لأي أداة
extension HapticWidgetExtension on Widget {
  /// Wrap widget with haptic feedback on tap
  Widget withHaptics({
    VoidCallback? onTap,
    HapticPattern pattern = HapticPattern.lightTap,
    HapticCategory category = HapticCategory.other,
    BorderRadius? borderRadius,
  }) {
    return HapticInkWell(
      onTap: onTap,
      tapPattern: pattern,
      category: category,
      borderRadius: borderRadius,
      child: this,
    );
  }

  /// Wrap widget with gesture detector and haptic feedback
  Widget withHapticGestures({
    VoidCallback? onTap,
    VoidCallback? onDoubleTap,
    VoidCallback? onLongPress,
    HapticPattern tapPattern = HapticPattern.lightTap,
    HapticPattern doubleTapPattern = HapticPattern.mediumTap,
    HapticPattern longPressPattern = HapticPattern.heavyTap,
    HapticCategory category = HapticCategory.gesture,
  }) {
    return GestureDetector(
      onTap: onTap != null
          ? () {
              HapticService.instance.trigger(tapPattern, category: category);
              onTap();
            }
          : null,
      onDoubleTap: onDoubleTap != null
          ? () {
              HapticService.instance.trigger(doubleTapPattern, category: category);
              onDoubleTap();
            }
          : null,
      onLongPress: onLongPress != null
          ? () {
              HapticService.instance.trigger(longPressPattern, category: category);
              onLongPress();
            }
          : null,
      child: this,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Haptic Callback Helpers
// ═══════════════════════════════════════════════════════════════════════════

/// Create a callback that triggers haptic feedback before executing
/// إنشاء استدعاء يُفعّل الاهتزاز قبل التنفيذ
VoidCallback? withHaptic(
  VoidCallback? callback, {
  HapticPattern pattern = HapticPattern.mediumTap,
  HapticCategory category = HapticCategory.other,
}) {
  if (callback == null) return null;
  return () {
    HapticService.instance.trigger(pattern, category: category);
    callback();
  };
}

/// Create a value changed callback that triggers haptic feedback
/// إنشاء استدعاء تغيير القيمة يُفعّل الاهتزاز
ValueChanged<T>? withHapticValue<T>(
  ValueChanged<T>? callback, {
  HapticPattern pattern = HapticPattern.selectionChanged,
  HapticCategory category = HapticCategory.form,
}) {
  if (callback == null) return null;
  return (value) {
    HapticService.instance.trigger(pattern, category: category);
    callback(value);
  };
}
