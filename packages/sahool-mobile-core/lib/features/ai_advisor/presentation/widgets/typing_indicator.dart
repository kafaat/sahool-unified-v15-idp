/// Typing Indicator Widget
/// مؤشر الكتابة
///
/// Shows animated typing indicator when AI is processing
library;

import 'package:flutter/material.dart';
import '../../../../core/config/theme.dart';

class TypingIndicator extends StatefulWidget {
  final Color? color;
  final double dotSize;
  final double spacing;

  const TypingIndicator({
    super.key,
    this.color,
    this.dotSize = 8,
    this.spacing = 4,
  });

  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late List<Animation<double>> _animations;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();

    _animations = List.generate(3, (index) {
      final start = index * 0.2;
      final end = start + 0.4;
      return Tween<double>(begin: 0, end: 1).animate(
        CurvedAnimation(
          parent: _controller,
          curve: Interval(start, end.clamp(0.0, 1.0), curve: Curves.easeInOut),
        ),
      );
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = widget.color ?? SahoolTheme.primary;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // AI icon
          Container(
            width: 24,
            height: 24,
            margin: const EdgeInsets.only(left: 8),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.psychology,
              size: 14,
              color: color,
            ),
          ),

          // Animated dots
          ...List.generate(3, (index) {
            return AnimatedBuilder(
              animation: _animations[index],
              builder: (context, child) {
                return Container(
                  margin: EdgeInsets.only(left: index == 0 ? 0 : widget.spacing),
                  child: Transform.translate(
                    offset: Offset(0, -4 * _animations[index].value),
                    child: Container(
                      width: widget.dotSize,
                      height: widget.dotSize,
                      decoration: BoxDecoration(
                        color: color.withValues(alpha: 0.4 + _animations[index].value * 0.6),
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                );
              },
            );
          }),
        ],
      ),
    );
  }
}

/// Inline typing indicator for chat
class InlineTypingIndicator extends StatefulWidget {
  final String? text;

  const InlineTypingIndicator({
    super.key,
    this.text,
  });

  @override
  State<InlineTypingIndicator> createState() => _InlineTypingIndicatorState();
}

class _InlineTypingIndicatorState extends State<InlineTypingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<int> _dotsAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat();

    _dotsAnimation = IntTween(begin: 0, end: 3).animate(_controller);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _dotsAnimation,
      builder: (context, child) {
        final dots = '.' * (_dotsAnimation.value + 1);
        return Text(
          widget.text != null ? '${widget.text}$dots' : 'جاري الكتابة$dots',
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey[600],
            fontStyle: FontStyle.italic,
          ),
        );
      },
    );
  }
}

/// Processing indicator with message
class ProcessingIndicator extends StatelessWidget {
  final String? message;
  final bool showSpinner;

  const ProcessingIndicator({
    super.key,
    this.message,
    this.showSpinner = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: SahoolTheme.primary.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: SahoolTheme.primary.withValues(alpha: 0.1),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (showSpinner)
            const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(SahoolTheme.primary),
              ),
            ),
          if (showSpinner) const SizedBox(width: 12),
          Text(
            message ?? 'جاري المعالجة...',
            style: const TextStyle(
              fontSize: 14,
              color: SahoolTheme.primary,
            ),
          ),
        ],
      ),
    );
  }
}

/// AI thinking indicator with pulse animation
class AiThinkingIndicator extends StatefulWidget {
  final String? status;

  const AiThinkingIndicator({
    super.key,
    this.status,
  });

  @override
  State<AiThinkingIndicator> createState() => _AiThinkingIndicatorState();
}

class _AiThinkingIndicatorState extends State<AiThinkingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 0.8, end: 1.2).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
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
      children: [
        AnimatedBuilder(
          animation: _pulseAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: _pulseAnimation.value,
              child: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: SahoolTheme.primary.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.psychology,
                  color: SahoolTheme.primary,
                  size: 24,
                ),
              ),
            );
          },
        ),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'المستشار الذكي يفكر...',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            if (widget.status != null)
              Text(
                widget.status!,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
          ],
        ),
      ],
    );
  }
}

/// Wave typing indicator
class WaveTypingIndicator extends StatefulWidget {
  final Color? color;

  const WaveTypingIndicator({
    super.key,
    this.color,
  });

  @override
  State<WaveTypingIndicator> createState() => _WaveTypingIndicatorState();
}

class _WaveTypingIndicatorState extends State<WaveTypingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = widget.color ?? SahoolTheme.primary;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: List.generate(5, (index) {
          return AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              final delay = index * 0.15;
              final value = ((_controller.value + delay) % 1.0);
              final height = 4 + 8 * _sinValue(value);

              return Container(
                margin: EdgeInsets.only(left: index == 0 ? 0 : 3),
                width: 3,
                height: height,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.3 + 0.7 * _sinValue(value)),
                  borderRadius: BorderRadius.circular(2),
                ),
              );
            },
          );
        }),
      ),
    );
  }

  double _sinValue(double value) {
    return (1 + (value * 2 * 3.14159).sin()) / 2;
  }
}

extension on double {
  double sin() {
    return _sin(this);
  }
}

double _sin(double x) {
  // Simple sine approximation
  x = x % (2 * 3.14159);
  double result = x;
  double term = x;
  for (int i = 1; i <= 7; i++) {
    term *= -x * x / ((2 * i) * (2 * i + 1));
    result += term;
  }
  return result;
}
