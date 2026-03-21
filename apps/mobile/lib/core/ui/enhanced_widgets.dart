/// SAHOOL Enhanced UI Widgets
/// مكونات واجهة المستخدم المحسّنة
///
/// Features:
/// - Pull to refresh with offline indicator
/// - Animated list items
/// - Enhanced cards with shimmer loading
/// - Connectivity-aware widgets
/// - Haptic feedback widgets

import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/theme.dart';
import '../offline/offline_ui_components.dart' show networkStatusProvider;
import '../sync/network_status.dart';

// =============================================================================
// Connectivity Banner - شريط حالة الاتصال
// =============================================================================

/// A banner that shows when the device is offline
/// شريط يظهر عندما يكون الجهاز غير متصل
class ConnectivityBanner extends ConsumerWidget {
  final Widget child;
  final bool showOnline;

  const ConnectivityBanner({
    super.key,
    required this.child,
    this.showOnline = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final networkStatus = ref.watch(networkStatusProvider);

    return Column(
      children: [
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          height: networkStatus.isConnected ? (showOnline ? 28 : 0) : 28,
          curve: Curves.easeInOut,
          child: Material(
            color: networkStatus.isConnected
                ? SahoolTheme.success
                : SahoolTheme.error,
            child: Center(
              child: Directionality(
                textDirection: TextDirection.rtl,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      networkStatus.isConnected
                          ? Icons.wifi
                          : Icons.wifi_off,
                      color: Colors.white,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      networkStatus.isConnected
                          ? 'متصل بالإنترنت'
                          : 'غير متصل - وضع عدم الاتصال',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        Expanded(child: child),
      ],
    );
  }
}

// =============================================================================
// Pull to Refresh Wrapper - غلاف السحب للتحديث
// =============================================================================

/// Enhanced pull to refresh with offline-aware behavior
/// سحب للتحديث محسّن مع إدراك حالة الاتصال
class SahoolRefreshIndicator extends ConsumerWidget {
  final Widget child;
  final Future<void> Function() onRefresh;
  final bool showOfflineMessage;
  final Color? color;

  const SahoolRefreshIndicator({
    super.key,
    required this.child,
    required this.onRefresh,
    this.showOfflineMessage = true,
    this.color,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final networkStatus = ref.watch(networkStatusProvider);

    return RefreshIndicator(
      onRefresh: () async {
        if (!networkStatus.isConnected && showOfflineMessage) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Directionality(
                textDirection: TextDirection.rtl,
                child: Row(
                  children: [
                    Icon(Icons.wifi_off, color: Colors.white, size: 18),
                    SizedBox(width: 8),
                    Text('غير متصل - يتم استخدام البيانات المخزنة'),
                  ],
                ),
              ),
              backgroundColor: SahoolTheme.warning,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          );
        }
        await onRefresh();
      },
      color: color ?? SahoolTheme.primary,
      backgroundColor: Colors.white,
      child: child,
    );
  }
}

// =============================================================================
// Animated List Item - عنصر قائمة متحرك
// =============================================================================

/// List item with entrance animation
/// عنصر قائمة مع تحريك الدخول
class AnimatedListItem extends StatefulWidget {
  final Widget child;
  final int index;
  final Duration delay;
  final Duration duration;
  final Curve curve;
  final Offset slideOffset;

  const AnimatedListItem({
    super.key,
    required this.child,
    required this.index,
    this.delay = const Duration(milliseconds: 50),
    this.duration = const Duration(milliseconds: 400),
    this.curve = Curves.easeOutCubic,
    this.slideOffset = const Offset(0, 30),
  });

  @override
  State<AnimatedListItem> createState() => _AnimatedListItemState();
}

class _AnimatedListItemState extends State<AnimatedListItem>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );

    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: widget.curve),
    );

    _slideAnimation = Tween<Offset>(
      begin: widget.slideOffset,
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));

    // Delay animation based on index
    Future.delayed(widget.delay * widget.index, () {
      if (mounted) _controller.forward();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Transform.translate(
          offset: _slideAnimation.value,
          child: Opacity(
            opacity: _fadeAnimation.value,
            child: widget.child,
          ),
        );
      },
    );
  }
}

// =============================================================================
// Staggered Animation Builder - بناء التحريك المتتابع
// =============================================================================

/// Creates staggered entrance animations for a list of widgets
/// ينشئ تحريكات دخول متتابعة لقائمة من المكونات
class StaggeredAnimationList extends StatelessWidget {
  final List<Widget> children;
  final Duration itemDelay;
  final Duration itemDuration;
  final ScrollController? scrollController;
  final EdgeInsets? padding;

  const StaggeredAnimationList({
    super.key,
    required this.children,
    this.itemDelay = const Duration(milliseconds: 50),
    this.itemDuration = const Duration(milliseconds: 400),
    this.scrollController,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: scrollController,
      padding: padding,
      itemCount: children.length,
      itemBuilder: (context, index) {
        return AnimatedListItem(
          index: index,
          delay: itemDelay,
          duration: itemDuration,
          child: children[index],
        );
      },
    );
  }
}

// =============================================================================
// Enhanced Card with Shimmer - بطاقة محسنة مع لمعان
// =============================================================================

/// Card with optional shimmer loading state
/// بطاقة مع حالة تحميل لمعان اختيارية
class SahoolCard extends StatelessWidget {
  final Widget child;
  final bool isLoading;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final EdgeInsets? margin;
  final EdgeInsets? padding;
  final Color? backgroundColor;
  final double elevation;
  final double borderRadius;
  final bool enableHaptic;

  const SahoolCard({
    super.key,
    required this.child,
    this.isLoading = false,
    this.onTap,
    this.onLongPress,
    this.margin,
    this.padding,
    this.backgroundColor,
    this.elevation = 2,
    this.borderRadius = 16,
    this.enableHaptic = true,
  });

  @override
  Widget build(BuildContext context) {
    final card = Card(
      margin: margin ?? const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: elevation,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(borderRadius),
      ),
      color: backgroundColor ?? Theme.of(context).cardColor,
      child: isLoading
          ? _ShimmerLoader(borderRadius: borderRadius, child: child)
          : Padding(
              padding: padding ?? const EdgeInsets.all(16),
              child: child,
            ),
    );

    if (onTap == null && onLongPress == null) return card;

    return GestureDetector(
      onTap: () {
        if (enableHaptic) HapticFeedback.lightImpact();
        onTap?.call();
      },
      onLongPress: () {
        if (enableHaptic) HapticFeedback.mediumImpact();
        onLongPress?.call();
      },
      child: card,
    );
  }
}

class _ShimmerLoader extends StatefulWidget {
  final double borderRadius;
  final Widget child;

  const _ShimmerLoader({
    required this.borderRadius,
    required this.child,
  });

  @override
  State<_ShimmerLoader> createState() => _ShimmerLoaderState();
}

class _ShimmerLoaderState extends State<_ShimmerLoader>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              colors: [
                Colors.grey.shade300,
                Colors.grey.shade100,
                Colors.grey.shade300,
              ],
              stops: [
                (_controller.value - 0.3).clamp(0.0, 1.0),
                _controller.value.clamp(0.0, 1.0),
                (_controller.value + 0.3).clamp(0.0, 1.0),
              ],
              begin: const Alignment(-1.0, -0.5),
              end: const Alignment(1.0, 0.5),
            ).createShader(bounds);
          },
          blendMode: BlendMode.srcATop,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(widget.borderRadius),
            child: widget.child,
          ),
        );
      },
    );
  }
}

// =============================================================================
// Haptic Feedback Button - زر مع ردود فعل لمسية
// =============================================================================

/// Button with haptic feedback and press animation
/// زر مع ردود فعل لمسية وتحريك الضغط
class HapticButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final VoidCallback? onLongPress;
  final HapticFeedbackType hapticType;
  final double pressScale;
  final Duration animationDuration;

  const HapticButton({
    super.key,
    required this.child,
    this.onPressed,
    this.onLongPress,
    this.hapticType = HapticFeedbackType.light,
    this.pressScale = 0.95,
    this.animationDuration = const Duration(milliseconds: 100),
  });

  @override
  State<HapticButton> createState() => _HapticButtonState();
}

enum HapticFeedbackType { light, medium, heavy, selection }

class _HapticButtonState extends State<HapticButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: widget.pressScale,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _triggerHaptic() {
    switch (widget.hapticType) {
      case HapticFeedbackType.light:
        HapticFeedback.lightImpact();
        break;
      case HapticFeedbackType.medium:
        HapticFeedback.mediumImpact();
        break;
      case HapticFeedbackType.heavy:
        HapticFeedback.heavyImpact();
        break;
      case HapticFeedbackType.selection:
        HapticFeedback.selectionClick();
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) {
        _controller.forward();
        _triggerHaptic();
      },
      onTapUp: (_) => _controller.reverse(),
      onTapCancel: () => _controller.reverse(),
      onTap: widget.onPressed,
      onLongPress: widget.onLongPress,
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: widget.child,
          );
        },
      ),
    );
  }
}

// =============================================================================
// Fade In Widget - مكون الظهور التدريجي
// =============================================================================

/// Widget that fades in when built
/// مكون يظهر تدريجياً عند بنائه
class FadeIn extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final Duration delay;
  final Curve curve;

  const FadeIn({
    super.key,
    required this.child,
    this.duration = const Duration(milliseconds: 400),
    this.delay = Duration.zero,
    this.curve = Curves.easeOut,
  });

  @override
  State<FadeIn> createState() => _FadeInState();
}

class _FadeInState extends State<FadeIn> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
    _animation = CurvedAnimation(parent: _controller, curve: widget.curve);

    if (widget.delay == Duration.zero) {
      _controller.forward();
    } else {
      Future.delayed(widget.delay, () {
        if (mounted) _controller.forward();
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _animation,
      child: widget.child,
    );
  }
}

// =============================================================================
// Slide In Widget - مكون الانزلاق للداخل
// =============================================================================

/// Widget that slides in when built
/// مكون ينزلق للداخل عند بنائه
class SlideIn extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final Duration delay;
  final Curve curve;
  final SlideDirection direction;

  const SlideIn({
    super.key,
    required this.child,
    this.duration = const Duration(milliseconds: 400),
    this.delay = Duration.zero,
    this.curve = Curves.easeOutCubic,
    this.direction = SlideDirection.fromBottom,
  });

  @override
  State<SlideIn> createState() => _SlideInState();
}

enum SlideDirection { fromTop, fromBottom, fromLeft, fromRight }

class _SlideInState extends State<SlideIn> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );

    final curve = CurvedAnimation(parent: _controller, curve: widget.curve);

    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(curve);
    _slideAnimation = Tween<Offset>(
      begin: _getBeginOffset(),
      end: Offset.zero,
    ).animate(curve);

    if (widget.delay == Duration.zero) {
      _controller.forward();
    } else {
      Future.delayed(widget.delay, () {
        if (mounted) _controller.forward();
      });
    }
  }

  Offset _getBeginOffset() {
    switch (widget.direction) {
      case SlideDirection.fromTop:
        return const Offset(0, -0.3);
      case SlideDirection.fromBottom:
        return const Offset(0, 0.3);
      case SlideDirection.fromLeft:
        return const Offset(-0.3, 0);
      case SlideDirection.fromRight:
        return const Offset(0.3, 0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: widget.child,
      ),
    );
  }
}

// =============================================================================
// Scale In Widget - مكون التكبير للداخل
// =============================================================================

/// Widget that scales in when built
/// مكون يتكبر للداخل عند بنائه
class ScaleIn extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final Duration delay;
  final Curve curve;
  final double beginScale;

  const ScaleIn({
    super.key,
    required this.child,
    this.duration = const Duration(milliseconds: 400),
    this.delay = Duration.zero,
    this.curve = Curves.easeOutBack,
    this.beginScale = 0.0,
  });

  @override
  State<ScaleIn> createState() => _ScaleInState();
}

class _ScaleInState extends State<ScaleIn> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );

    final curve = CurvedAnimation(parent: _controller, curve: widget.curve);

    _scaleAnimation = Tween<double>(
      begin: widget.beginScale,
      end: 1.0,
    ).animate(curve);

    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );

    if (widget.delay == Duration.zero) {
      _controller.forward();
    } else {
      Future.delayed(widget.delay, () {
        if (mounted) _controller.forward();
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _scaleAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: widget.child,
      ),
    );
  }
}

// =============================================================================
// Rotating Widget - مكون دوار
// =============================================================================

/// Widget that continuously rotates
/// مكون يدور باستمرار
class RotatingWidget extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final bool reverse;

  const RotatingWidget({
    super.key,
    required this.child,
    this.duration = const Duration(seconds: 2),
    this.reverse = false,
  });

  @override
  State<RotatingWidget> createState() => _RotatingWidgetState();
}

class _RotatingWidgetState extends State<RotatingWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    )..repeat(reverse: widget.reverse);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return RotationTransition(
      turns: _controller,
      child: widget.child,
    );
  }
}

// =============================================================================
// Typing Animation Text - نص متحرك بالكتابة
// =============================================================================

/// Text that appears character by character
/// نص يظهر حرفاً تلو الآخر
class TypingText extends StatefulWidget {
  final String text;
  final TextStyle? style;
  final Duration charDuration;
  final Duration startDelay;
  final VoidCallback? onComplete;

  const TypingText({
    super.key,
    required this.text,
    this.style,
    this.charDuration = const Duration(milliseconds: 50),
    this.startDelay = Duration.zero,
    this.onComplete,
  });

  @override
  State<TypingText> createState() => _TypingTextState();
}

class _TypingTextState extends State<TypingText> {
  String _displayText = '';
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    Future.delayed(widget.startDelay, _startTyping);
  }

  void _startTyping() {
    if (!mounted) return;

    if (_currentIndex < widget.text.length) {
      setState(() {
        _displayText = widget.text.substring(0, _currentIndex + 1);
        _currentIndex++;
      });
      Future.delayed(widget.charDuration, _startTyping);
    } else {
      widget.onComplete?.call();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Text(
      _displayText,
      style: widget.style,
    );
  }
}

// =============================================================================
// Counting Animation - تحريك العد
// =============================================================================

/// Animated number counter
/// عداد أرقام متحرك
class AnimatedCounter extends StatefulWidget {
  final int value;
  final Duration duration;
  final TextStyle? style;
  final String? prefix;
  final String? suffix;
  final int fractionDigits;

  const AnimatedCounter({
    super.key,
    required this.value,
    this.duration = const Duration(milliseconds: 800),
    this.style,
    this.prefix,
    this.suffix,
    this.fractionDigits = 0,
  });

  @override
  State<AnimatedCounter> createState() => _AnimatedCounterState();
}

class _AnimatedCounterState extends State<AnimatedCounter>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  int _previousValue = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
    _updateAnimation();
    _controller.forward();
  }

  @override
  void didUpdateWidget(AnimatedCounter oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.value != widget.value) {
      _previousValue = oldWidget.value;
      _updateAnimation();
      _controller.forward(from: 0);
    }
  }

  void _updateAnimation() {
    _animation = Tween<double>(
      begin: _previousValue.toDouble(),
      end: widget.value.toDouble(),
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        final value = _animation.value.toStringAsFixed(widget.fractionDigits);
        return Text(
          '${widget.prefix ?? ''}$value${widget.suffix ?? ''}',
          style: widget.style,
        );
      },
    );
  }
}

// =============================================================================
// Shake Animation - تحريك الاهتزاز
// =============================================================================

/// Widget that shakes (useful for error states)
/// مكون يهتز (مفيد لحالات الخطأ)
class ShakeWidget extends StatefulWidget {
  final Widget child;
  final bool shake;
  final Duration duration;
  final double magnitude;

  const ShakeWidget({
    super.key,
    required this.child,
    this.shake = false,
    this.duration = const Duration(milliseconds: 500),
    this.magnitude = 10,
  });

  @override
  State<ShakeWidget> createState() => ShakeWidgetState();
}

class ShakeWidgetState extends State<ShakeWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
  }

  @override
  void didUpdateWidget(ShakeWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.shake && !oldWidget.shake) {
      shake();
    }
  }

  void shake() {
    _controller.forward(from: 0);
    HapticFeedback.mediumImpact();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final sineValue = math.sin(4 * math.pi * _controller.value);
        final offset = sineValue * widget.magnitude * (1 - _controller.value);
        return Transform.translate(
          offset: Offset(offset, 0),
          child: widget.child,
        );
      },
    );
  }
}

// =============================================================================
// Bouncing Dots Loader - نقاط متحركة للتحميل
// =============================================================================

/// Bouncing dots loading indicator
/// مؤشر تحميل بنقاط متقافزة
class BouncingDotsLoader extends StatefulWidget {
  final Color color;
  final double size;
  final Duration duration;

  const BouncingDotsLoader({
    super.key,
    this.color = SahoolTheme.primary,
    this.size = 10,
    this.duration = const Duration(milliseconds: 1000),
  });

  @override
  State<BouncingDotsLoader> createState() => _BouncingDotsLoaderState();
}

class _BouncingDotsLoaderState extends State<BouncingDotsLoader>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(3, (index) {
        return AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            final delay = index * 0.2;
            final progress = (_controller.value - delay) % 1.0;
            final bounce = math.sin(progress * math.pi) * widget.size;

            return Container(
              margin: EdgeInsets.symmetric(horizontal: widget.size / 4),
              child: Transform.translate(
                offset: Offset(0, -bounce.abs()),
                child: Container(
                  width: widget.size,
                  height: widget.size,
                  decoration: BoxDecoration(
                    color: widget.color,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            );
          },
        );
      }),
    );
  }
}
