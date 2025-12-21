import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';

/// SAHOOL Optimized List Widgets
/// قوائم محسّنة للأداء
///
/// Features:
/// - Lazy loading with pagination
/// - Efficient rebuilds with RepaintBoundary
/// - Scroll performance optimization
/// - Memory-efficient item recycling

/// قائمة محسّنة مع التحميل الكسول
class SahoolOptimizedListView<T> extends StatefulWidget {
  final List<T> items;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final Widget? separatorBuilder;
  final Widget? emptyWidget;
  final Widget? loadingWidget;
  final Widget? errorWidget;
  final EdgeInsets? padding;
  final ScrollController? controller;
  final bool shrinkWrap;
  final ScrollPhysics? physics;
  final bool isLoading;
  final bool hasError;
  final bool hasMore;
  final VoidCallback? onLoadMore;
  final double loadMoreThreshold;
  final bool addRepaintBoundaries;
  final bool addAutomaticKeepAlives;

  const SahoolOptimizedListView({
    super.key,
    required this.items,
    required this.itemBuilder,
    this.separatorBuilder,
    this.emptyWidget,
    this.loadingWidget,
    this.errorWidget,
    this.padding,
    this.controller,
    this.shrinkWrap = false,
    this.physics,
    this.isLoading = false,
    this.hasError = false,
    this.hasMore = false,
    this.onLoadMore,
    this.loadMoreThreshold = 200,
    this.addRepaintBoundaries = true,
    this.addAutomaticKeepAlives = false,
  });

  @override
  State<SahoolOptimizedListView<T>> createState() => _SahoolOptimizedListViewState<T>();
}

class _SahoolOptimizedListViewState<T> extends State<SahoolOptimizedListView<T>> {
  late ScrollController _controller;
  bool _isLoadingMore = false;

  @override
  void initState() {
    super.initState();
    _controller = widget.controller ?? ScrollController();
    _controller.addListener(_onScroll);
  }

  @override
  void dispose() {
    if (widget.controller == null) {
      _controller.dispose();
    } else {
      _controller.removeListener(_onScroll);
    }
    super.dispose();
  }

  void _onScroll() {
    if (!widget.hasMore || _isLoadingMore || widget.isLoading) return;

    final maxScroll = _controller.position.maxScrollExtent;
    final currentScroll = _controller.position.pixels;

    if (maxScroll - currentScroll <= widget.loadMoreThreshold) {
      _loadMore();
    }
  }

  Future<void> _loadMore() async {
    if (_isLoadingMore) return;

    setState(() => _isLoadingMore = true);
    widget.onLoadMore?.call();

    // Reset after a short delay to prevent rapid calls
    await Future.delayed(const Duration(milliseconds: 500));
    if (mounted) {
      setState(() => _isLoadingMore = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    // Error state
    if (widget.hasError && widget.errorWidget != null) {
      return widget.errorWidget!;
    }

    // Empty state
    if (widget.items.isEmpty && !widget.isLoading) {
      return widget.emptyWidget ?? const SizedBox.shrink();
    }

    // Loading state (initial)
    if (widget.items.isEmpty && widget.isLoading) {
      return widget.loadingWidget ?? const Center(
        child: CircularProgressIndicator(),
      );
    }

    final itemCount = widget.items.length + (widget.hasMore ? 1 : 0);

    return ListView.builder(
      controller: _controller,
      padding: widget.padding,
      shrinkWrap: widget.shrinkWrap,
      physics: widget.physics,
      itemCount: widget.separatorBuilder != null ? itemCount * 2 - 1 : itemCount,
      addRepaintBoundaries: widget.addRepaintBoundaries,
      addAutomaticKeepAlives: widget.addAutomaticKeepAlives,
      itemBuilder: (context, index) {
        // Handle separator
        if (widget.separatorBuilder != null) {
          if (index.isOdd) {
            return widget.separatorBuilder!;
          }
          index = index ~/ 2;
        }

        // Loading more indicator
        if (index >= widget.items.length) {
          return Padding(
            padding: const EdgeInsets.all(16),
            child: Center(
              child: widget.loadingWidget ?? const CircularProgressIndicator(),
            ),
          );
        }

        // Build item with RepaintBoundary for optimization
        final item = widget.items[index];
        Widget child = widget.itemBuilder(context, item, index);

        if (widget.addRepaintBoundaries) {
          child = RepaintBoundary(child: child);
        }

        return child;
      },
    );
  }
}

/// Grid محسّن
class SahoolOptimizedGridView<T> extends StatelessWidget {
  final List<T> items;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final int crossAxisCount;
  final double mainAxisSpacing;
  final double crossAxisSpacing;
  final double childAspectRatio;
  final EdgeInsets? padding;
  final ScrollController? controller;
  final bool shrinkWrap;
  final ScrollPhysics? physics;
  final bool addRepaintBoundaries;

  const SahoolOptimizedGridView({
    super.key,
    required this.items,
    required this.itemBuilder,
    this.crossAxisCount = 2,
    this.mainAxisSpacing = 8,
    this.crossAxisSpacing = 8,
    this.childAspectRatio = 1,
    this.padding,
    this.controller,
    this.shrinkWrap = false,
    this.physics,
    this.addRepaintBoundaries = true,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      controller: controller,
      padding: padding,
      shrinkWrap: shrinkWrap,
      physics: physics,
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        mainAxisSpacing: mainAxisSpacing,
        crossAxisSpacing: crossAxisSpacing,
        childAspectRatio: childAspectRatio,
      ),
      itemCount: items.length,
      addRepaintBoundaries: addRepaintBoundaries,
      itemBuilder: (context, index) {
        Widget child = itemBuilder(context, items[index], index);

        if (addRepaintBoundaries) {
          child = RepaintBoundary(child: child);
        }

        return child;
      },
    );
  }
}

/// Sliver محسّن للقوائم المعقدة
class SahoolOptimizedSliverList<T> extends StatelessWidget {
  final List<T> items;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final bool addRepaintBoundaries;

  const SahoolOptimizedSliverList({
    super.key,
    required this.items,
    required this.itemBuilder,
    this.addRepaintBoundaries = true,
  });

  @override
  Widget build(BuildContext context) {
    return SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) {
          Widget child = itemBuilder(context, items[index], index);

          if (addRepaintBoundaries) {
            child = RepaintBoundary(child: child);
          }

          return child;
        },
        childCount: items.length,
        addRepaintBoundaries: addRepaintBoundaries,
      ),
    );
  }
}

/// Mixin لتحسين أداء التمرير
mixin ScrollOptimizationMixin<T extends StatefulWidget> on State<T> {
  bool _isScrolling = false;
  bool get isScrolling => _isScrolling;

  /// تحديث حالة التمرير
  bool handleScrollNotification(ScrollNotification notification) {
    if (notification is ScrollStartNotification) {
      if (!_isScrolling) {
        setState(() => _isScrolling = true);
      }
    } else if (notification is ScrollEndNotification) {
      if (_isScrolling) {
        setState(() => _isScrolling = false);
      }
    }
    return false;
  }

  /// الحصول على جودة الصورة بناءً على حالة التمرير
  FilterQuality get imageQuality =>
      _isScrolling ? FilterQuality.low : FilterQuality.medium;
}

/// Widget لتحسين أداء التمرير
class ScrollOptimizer extends StatelessWidget {
  final Widget child;
  final bool enableCaching;

  const ScrollOptimizer({
    super.key,
    required this.child,
    this.enableCaching = true,
  });

  @override
  Widget build(BuildContext context) {
    Widget optimized = child;

    if (enableCaching) {
      optimized = RepaintBoundary(child: optimized);
    }

    return optimized;
  }
}
