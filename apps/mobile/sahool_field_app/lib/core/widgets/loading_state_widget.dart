import 'package:flutter/material.dart';

/// Reusable Loading State Widget
/// Provides consistent loading indicators across the app
///
/// واجهة حالة التحميل - توفر مؤشرات تحميل متسقة
class LoadingStateWidget extends StatelessWidget {
  final String? message;
  final String? messageAr;
  final bool showMessage;
  final double size;
  final Color? color;

  const LoadingStateWidget({
    super.key,
    this.message,
    this.messageAr,
    this.showMessage = false,
    this.size = 40.0,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayMessage = isRtl && messageAr != null ? messageAr : message;

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          SizedBox(
            width: size,
            height: size,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              valueColor: AlwaysStoppedAnimation<Color>(
                color ?? theme.colorScheme.primary,
              ),
            ),
          ),
          if (showMessage && displayMessage != null) ...[
            const SizedBox(height: 16),
            Text(
              displayMessage,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }
}

/// Skeleton Loader for List Items
/// Shows placeholder while data is loading
class SkeletonLoader extends StatelessWidget {
  final int itemCount;
  final double height;
  final double? width;
  final EdgeInsets padding;

  const SkeletonLoader({
    super.key,
    this.itemCount = 3,
    this.height = 80.0,
    this.width,
    this.padding = const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: itemCount,
      padding: padding,
      itemBuilder: (context, index) => _SkeletonItem(
        height: height,
        width: width,
      ),
    );
  }
}

class _SkeletonItem extends StatefulWidget {
  final double height;
  final double? width;

  const _SkeletonItem({
    required this.height,
    this.width,
  });

  @override
  State<_SkeletonItem> createState() => _SkeletonItemState();
}

class _SkeletonItemState extends State<_SkeletonItem>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();

    _animation = Tween<double>(begin: -1.0, end: 2.0).animate(
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
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final baseColor = isDark ? Colors.grey[800]! : Colors.grey[300]!;
    final highlightColor = isDark ? Colors.grey[700]! : Colors.grey[100]!;

    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          height: widget.height,
          width: widget.width,
          margin: const EdgeInsets.only(bottom: 12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            gradient: LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [baseColor, highlightColor, baseColor],
              stops: [
                _animation.value - 0.3,
                _animation.value,
                _animation.value + 0.3,
              ].map((e) => e.clamp(0.0, 1.0)).toList(),
            ),
          ),
        );
      },
    );
  }
}

/// Inline loading indicator for buttons
class InlineLoading extends StatelessWidget {
  final String? label;
  final String? labelAr;
  final double size;
  final Color? color;

  const InlineLoading({
    super.key,
    this.label,
    this.labelAr,
    this.size = 16.0,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayLabel = isRtl && labelAr != null ? labelAr : label;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(
              color ?? theme.colorScheme.onPrimary,
            ),
          ),
        ),
        if (displayLabel != null) ...[
          const SizedBox(width: 8),
          Text(displayLabel),
        ],
      ],
    );
  }
}

/// Full screen loading overlay
class LoadingOverlay extends StatelessWidget {
  final String? message;
  final String? messageAr;
  final bool isVisible;

  const LoadingOverlay({
    super.key,
    this.message,
    this.messageAr,
    this.isVisible = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!isVisible) return const SizedBox.shrink();

    return Container(
      color: Colors.black54,
      child: LoadingStateWidget(
        message: message,
        messageAr: messageAr,
        showMessage: true,
        size: 50,
        color: Colors.white,
      ),
    );
  }
}

/// Specialized loading states for specific screens
class LoadingFieldsState extends StatelessWidget {
  const LoadingFieldsState({super.key});

  @override
  Widget build(BuildContext context) {
    return const LoadingStateWidget(
      message: 'Loading fields...',
      messageAr: 'جارٍ تحميل الحقول...',
      showMessage: true,
    );
  }
}

class LoadingTasksState extends StatelessWidget {
  const LoadingTasksState({super.key});

  @override
  Widget build(BuildContext context) {
    return const LoadingStateWidget(
      message: 'Loading tasks...',
      messageAr: 'جارٍ تحميل المهام...',
      showMessage: true,
    );
  }
}

class LoadingWeatherState extends StatelessWidget {
  const LoadingWeatherState({super.key});

  @override
  Widget build(BuildContext context) {
    return const LoadingStateWidget(
      message: 'Loading weather data...',
      messageAr: 'جارٍ تحميل بيانات الطقس...',
      showMessage: true,
    );
  }
}
