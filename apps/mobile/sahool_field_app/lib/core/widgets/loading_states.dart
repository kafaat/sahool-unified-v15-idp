import 'package:flutter/material.dart';
import '../theme/sahool_theme.dart';

/// SAHOOL Loading States Widgets
/// مكونات حالات التحميل الموحدة

// ═══════════════════════════════════════════════════════════════════════════
// Shimmer Loading Effect
// ═══════════════════════════════════════════════════════════════════════════

/// Shimmer effect widget for loading placeholders
class SahoolShimmer extends StatefulWidget {
  final Widget child;
  final bool enabled;

  const SahoolShimmer({
    super.key,
    required this.child,
    this.enabled = true,
  });

  @override
  State<SahoolShimmer> createState() => _SahoolShimmerState();
}

class _SahoolShimmerState extends State<SahoolShimmer>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();

    _animation = Tween<double>(begin: -1, end: 2).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOutSine),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.enabled) return widget.child;

    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: const [
                Color(0xFFE0E0E0),
                Color(0xFFF5F5F5),
                Color(0xFFE0E0E0),
              ],
              stops: [
                _animation.value - 0.3,
                _animation.value,
                _animation.value + 0.3,
              ].map((s) => s.clamp(0.0, 1.0)).toList(),
            ).createShader(bounds);
          },
          blendMode: BlendMode.srcATop,
          child: widget.child,
        );
      },
      child: widget.child,
    );
  }
}

/// Shimmer Card placeholder
class SahoolShimmerCard extends StatelessWidget {
  final double height;
  final double? width;
  final double borderRadius;

  const SahoolShimmerCard({
    super.key,
    this.height = 120,
    this.width,
    this.borderRadius = 16,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolShimmer(
      child: Container(
        height: height,
        width: width,
        decoration: BoxDecoration(
          color: Colors.grey[300],
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
    );
  }
}

/// Shimmer List placeholder
class SahoolShimmerList extends StatelessWidget {
  final int itemCount;
  final double itemHeight;
  final double spacing;

  const SahoolShimmerList({
    super.key,
    this.itemCount = 5,
    this.itemHeight = 80,
    this.spacing = 12,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      itemCount: itemCount,
      separatorBuilder: (_, __) => SizedBox(height: spacing),
      itemBuilder: (_, __) => SahoolShimmerCard(height: itemHeight),
    );
  }
}

/// Shimmer Grid placeholder
class SahoolShimmerGrid extends StatelessWidget {
  final int itemCount;
  final int crossAxisCount;
  final double childAspectRatio;

  const SahoolShimmerGrid({
    super.key,
    this.itemCount = 6,
    this.crossAxisCount = 2,
    this.childAspectRatio = 1.0,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        childAspectRatio: childAspectRatio,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: itemCount,
      itemBuilder: (_, __) => const SahoolShimmerCard(),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Loading Indicators
// ═══════════════════════════════════════════════════════════════════════════

/// Full screen loading indicator
class SahoolLoadingScreen extends StatelessWidget {
  final String? message;

  const SahoolLoadingScreen({
    super.key,
    this.message,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const SahoolLoadingSpinner(size: 48),
            if (message != null) ...[
              const SizedBox(height: 24),
              Text(
                message!,
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 16,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Custom loading spinner with SAHOOL branding
class SahoolLoadingSpinner extends StatefulWidget {
  final double size;
  final Color? color;

  const SahoolLoadingSpinner({
    super.key,
    this.size = 32,
    this.color,
  });

  @override
  State<SahoolLoadingSpinner> createState() => _SahoolLoadingSpinnerState();
}

class _SahoolLoadingSpinnerState extends State<SahoolLoadingSpinner>
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
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: CircularProgressIndicator(
        strokeWidth: 3,
        valueColor: AlwaysStoppedAnimation<Color>(
          widget.color ?? SahoolColors.primary,
        ),
      ),
    );
  }
}

/// Loading overlay for async operations
class SahoolLoadingOverlay extends StatelessWidget {
  final bool isLoading;
  final Widget child;
  final String? message;

  const SahoolLoadingOverlay({
    super.key,
    required this.isLoading,
    required this.child,
    this.message,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (isLoading)
          Container(
            color: Colors.black.withOpacity(0.3),
            child: Center(
              child: Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 20,
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const SahoolLoadingSpinner(size: 40),
                    if (message != null) ...[
                      const SizedBox(height: 16),
                      Text(
                        message!,
                        style: const TextStyle(
                          fontSize: 14,
                          color: SahoolColors.textSecondary,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}

/// Inline loading indicator
class SahoolInlineLoading extends StatelessWidget {
  final String? message;

  const SahoolInlineLoading({
    super.key,
    this.message,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SahoolLoadingSpinner(size: 20),
          if (message != null) ...[
            const SizedBox(width: 12),
            Text(
              message!,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 14,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Button Loading States
// ═══════════════════════════════════════════════════════════════════════════

/// Button with loading state
class SahoolLoadingButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final bool isLoading;
  final Widget child;
  final Color? backgroundColor;
  final Color? foregroundColor;

  const SahoolLoadingButton({
    super.key,
    required this.onPressed,
    required this.isLoading,
    required this.child,
    this.backgroundColor,
    this.foregroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: backgroundColor ?? SahoolColors.primary,
        foregroundColor: foregroundColor ?? Colors.white,
        disabledBackgroundColor:
            (backgroundColor ?? SahoolColors.primary).withOpacity(0.7),
      ),
      child: isLoading
          ? SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(
                  foregroundColor ?? Colors.white,
                ),
              ),
            )
          : child,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Pull to Refresh
// ═══════════════════════════════════════════════════════════════════════════

/// Custom refresh indicator with SAHOOL styling
class SahoolRefreshIndicator extends StatelessWidget {
  final Widget child;
  final Future<void> Function() onRefresh;

  const SahoolRefreshIndicator({
    super.key,
    required this.child,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: onRefresh,
      color: SahoolColors.primary,
      backgroundColor: Colors.white,
      strokeWidth: 3,
      displacement: 60,
      child: child,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Additional Loading Components
// ═══════════════════════════════════════════════════════════════════════════

/// Linear progress indicator with SAHOOL styling
class SahoolProgressBar extends StatelessWidget {
  final double? value;
  final Color? backgroundColor;
  final Color? progressColor;
  final double height;

  const SahoolProgressBar({
    super.key,
    this.value,
    this.backgroundColor,
    this.progressColor,
    this.height = 4,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: height,
      child: LinearProgressIndicator(
        value: value,
        backgroundColor: backgroundColor ?? Colors.grey[200],
        valueColor: AlwaysStoppedAnimation<Color>(
          progressColor ?? SahoolColors.primary,
        ),
        borderRadius: BorderRadius.circular(height / 2),
      ),
    );
  }
}

/// Text shimmer effect for loading text
class SahoolTextShimmer extends StatelessWidget {
  final double width;
  final double height;
  final double borderRadius;

  const SahoolTextShimmer({
    super.key,
    this.width = 100,
    this.height = 16,
    this.borderRadius = 4,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolShimmer(
      child: Container(
        width: width,
        height: height,
        decoration: BoxDecoration(
          color: Colors.grey[300],
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
    );
  }
}

/// Circle shimmer for avatars
class SahoolCircleShimmer extends StatelessWidget {
  final double size;

  const SahoolCircleShimmer({
    super.key,
    this.size = 48,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolShimmer(
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: Colors.grey[300],
          shape: BoxShape.circle,
        ),
      ),
    );
  }
}

/// Skeleton loading for list items
class SahoolListItemSkeleton extends StatelessWidget {
  final bool hasAvatar;
  final int textLines;

  const SahoolListItemSkeleton({
    super.key,
    this.hasAvatar = true,
    this.textLines = 2,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          if (hasAvatar) ...[
            const SahoolCircleShimmer(size: 48),
            const SizedBox(width: 16),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (int i = 0; i < textLines; i++) ...[
                  SahoolTextShimmer(
                    width: i == 0 ? double.infinity : 120,
                    height: i == 0 ? 16 : 14,
                  ),
                  if (i < textLines - 1) const SizedBox(height: 8),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Skeleton loading for profile header
class SahoolProfileHeaderSkeleton extends StatelessWidget {
  const SahoolProfileHeaderSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SahoolCircleShimmer(size: 100),
          const SizedBox(height: 16),
          const SahoolTextShimmer(width: 150, height: 20),
          const SizedBox(height: 8),
          const SahoolTextShimmer(width: 200, height: 14),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              for (int i = 0; i < 3; i++)
                const Column(
                  children: [
                    SahoolTextShimmer(width: 60, height: 20),
                    SizedBox(height: 4),
                    SahoolTextShimmer(width: 80, height: 14),
                  ],
                ),
            ],
          ),
        ],
      ),
    );
  }
}

/// Loading state wrapper for async data
class SahoolAsyncBuilder<T> extends StatelessWidget {
  final Future<T>? future;
  final T? data;
  final Widget Function(T data) builder;
  final Widget? loadingWidget;
  final Widget Function(Object error)? errorBuilder;

  const SahoolAsyncBuilder({
    super.key,
    this.future,
    this.data,
    required this.builder,
    this.loadingWidget,
    this.errorBuilder,
  });

  @override
  Widget build(BuildContext context) {
    if (data != null) {
      return builder(data as T);
    }

    if (future == null) {
      return loadingWidget ?? const SahoolLoadingScreen();
    }

    return FutureBuilder<T>(
      future: future,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          return builder(snapshot.data as T);
        }

        if (snapshot.hasError) {
          return errorBuilder?.call(snapshot.error!) ??
              Center(
                child: Text(
                  'خطأ: ${snapshot.error}',
                  style: const TextStyle(color: SahoolColors.danger),
                ),
              );
        }

        return loadingWidget ?? const SahoolLoadingScreen();
      },
    );
  }
}

/// Skeleton for field card
class SahoolFieldCardSkeleton extends StatelessWidget {
  const SahoolFieldCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const SahoolCircleShimmer(size: 40),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SahoolTextShimmer(width: 150, height: 16),
                      SizedBox(height: 6),
                      SahoolTextShimmer(width: 100, height: 14),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const SahoolShimmerCard(height: 100),
            const SizedBox(height: 12),
            Row(
              children: [
                for (int i = 0; i < 3; i++) ...[
                  const Expanded(
                    child: SahoolTextShimmer(width: double.infinity, height: 14),
                  ),
                  if (i < 2) const SizedBox(width: 12),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }
}
