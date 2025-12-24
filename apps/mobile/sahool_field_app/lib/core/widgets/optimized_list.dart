import 'package:flutter/material.dart';
import '../utils/app_logger.dart';

/// SAHOOL Optimized List Widgets
/// قوائم محسّنة للأداء مع التحميل الكسول والتمرير اللانهائي
///
/// Features:
/// - Lazy loading with const constructors
/// - Infinite scroll with pagination
/// - Efficient rebuilds with RepaintBoundary
/// - Memory-optimized item recycling
/// - Pull-to-refresh support
/// - Empty and error states

/// SahoolOptimizedList - قائمة محسّنة مع التحميل الكسول
///
/// A performance-optimized list view with lazy loading and efficient rendering
class SahoolOptimizedList<T> extends StatelessWidget {
  final List<T> items;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final Widget? separator;
  final Widget? emptyWidget;
  final EdgeInsets? padding;
  final ScrollController? controller;
  final ScrollPhysics? physics;
  final bool shrinkWrap;
  final bool addRepaintBoundaries;
  final bool addAutomaticKeepAlives;
  final String? semanticLabel;

  const SahoolOptimizedList({
    super.key,
    required this.items,
    required this.itemBuilder,
    this.separator,
    this.emptyWidget,
    this.padding,
    this.controller,
    this.physics,
    this.shrinkWrap = false,
    this.addRepaintBoundaries = true,
    this.addAutomaticKeepAlives = false,
    this.semanticLabel,
  });

  @override
  Widget build(BuildContext context) {
    // Empty state
    if (items.isEmpty) {
      return emptyWidget ??
          const Center(
            child: Text('No items'),
          );
    }

    // Build list with separator support
    if (separator != null) {
      return ListView.separated(
        key: key,
        controller: controller,
        padding: padding,
        physics: physics,
        shrinkWrap: shrinkWrap,
        addRepaintBoundaries: addRepaintBoundaries,
        addAutomaticKeepAlives: addAutomaticKeepAlives,
        itemCount: items.length,
        separatorBuilder: (_, __) => separator!,
        itemBuilder: (context, index) {
          final item = items[index];
          Widget child = itemBuilder(context, item, index);

          if (addRepaintBoundaries) {
            child = RepaintBoundary(
              key: ValueKey('item_$index'),
              child: child,
            );
          }

          return child;
        },
      );
    }

    // Build list without separator
    return ListView.builder(
      key: key,
      controller: controller,
      padding: padding,
      physics: physics,
      shrinkWrap: shrinkWrap,
      addRepaintBoundaries: addRepaintBoundaries,
      addAutomaticKeepAlives: addAutomaticKeepAlives,
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        Widget child = itemBuilder(context, item, index);

        if (addRepaintBoundaries) {
          child = RepaintBoundary(
            key: ValueKey('item_$index'),
            child: child,
          );
        }

        return child;
      },
    );
  }
}

/// SahoolPaginatedList - قائمة مع التمرير اللانهائي والتحميل الصفحي
///
/// A list view with infinite scroll support and pagination
class SahoolPaginatedList<T> extends StatefulWidget {
  final List<T> items;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final Widget? separator;
  final Widget? emptyWidget;
  final Widget? loadingWidget;
  final Widget? errorWidget;
  final EdgeInsets? padding;
  final ScrollController? controller;
  final ScrollPhysics? physics;
  final bool shrinkWrap;

  // Pagination
  final bool hasMore;
  final bool isLoading;
  final bool hasError;
  final Future<void> Function()? onLoadMore;
  final double loadMoreThreshold;

  // Pull to refresh
  final Future<void> Function()? onRefresh;

  // Performance
  final bool addRepaintBoundaries;
  final bool addAutomaticKeepAlives;

  const SahoolPaginatedList({
    super.key,
    required this.items,
    required this.itemBuilder,
    this.separator,
    this.emptyWidget,
    this.loadingWidget,
    this.errorWidget,
    this.padding,
    this.controller,
    this.physics,
    this.shrinkWrap = false,
    this.hasMore = false,
    this.isLoading = false,
    this.hasError = false,
    this.onLoadMore,
    this.loadMoreThreshold = 200.0,
    this.onRefresh,
    this.addRepaintBoundaries = true,
    this.addAutomaticKeepAlives = false,
  });

  @override
  State<SahoolPaginatedList<T>> createState() => _SahoolPaginatedListState<T>();
}

class _SahoolPaginatedListState<T> extends State<SahoolPaginatedList<T>> {
  late ScrollController _scrollController;
  bool _isLoadingMore = false;

  @override
  void initState() {
    super.initState();
    _scrollController = widget.controller ?? ScrollController();
    _scrollController.addListener(_onScroll);
  }

  @override
  void didUpdateWidget(SahoolPaginatedList<T> oldWidget) {
    super.didUpdateWidget(oldWidget);

    // Update scroll controller if changed
    if (widget.controller != oldWidget.controller) {
      _scrollController.removeListener(_onScroll);
      _scrollController = widget.controller ?? ScrollController();
      _scrollController.addListener(_onScroll);
    }
  }

  @override
  void dispose() {
    if (widget.controller == null) {
      _scrollController.dispose();
    } else {
      _scrollController.removeListener(_onScroll);
    }
    super.dispose();
  }

  void _onScroll() {
    if (!widget.hasMore || _isLoadingMore || widget.isLoading) {
      return;
    }

    final maxScroll = _scrollController.position.maxScrollExtent;
    final currentScroll = _scrollController.position.pixels;

    if (maxScroll - currentScroll <= widget.loadMoreThreshold) {
      _loadMore();
    }
  }

  Future<void> _loadMore() async {
    if (_isLoadingMore || widget.onLoadMore == null) return;

    setState(() => _isLoadingMore = true);

    try {
      await widget.onLoadMore!();
      AppLogger.d('Loaded more items', tag: 'PAGINATED_LIST');
    } catch (e) {
      AppLogger.e('Failed to load more items', tag: 'PAGINATED_LIST', error: e);
    } finally {
      if (mounted) {
        setState(() => _isLoadingMore = false);
      }
    }
  }

  Widget _buildLoadingIndicator() {
    return widget.loadingWidget ??
        const Padding(
          padding: EdgeInsets.all(16.0),
          child: Center(
            child: CircularProgressIndicator(),
          ),
        );
  }

  Widget _buildList() {
    // Calculate item count (add 1 for loading indicator if has more)
    final itemCount = widget.items.length + (widget.hasMore ? 1 : 0);

    // Build list with separator
    if (widget.separator != null) {
      return ListView.separated(
        controller: _scrollController,
        padding: widget.padding,
        physics: widget.physics,
        shrinkWrap: widget.shrinkWrap,
        addRepaintBoundaries: widget.addRepaintBoundaries,
        addAutomaticKeepAlives: widget.addAutomaticKeepAlives,
        itemCount: itemCount,
        separatorBuilder: (_, index) {
          // Don't show separator before loading indicator
          if (index >= widget.items.length - 1 && widget.hasMore) {
            return const SizedBox.shrink();
          }
          return widget.separator!;
        },
        itemBuilder: (context, index) {
          // Loading indicator at the end
          if (index >= widget.items.length) {
            return _buildLoadingIndicator();
          }

          // Build item
          final item = widget.items[index];
          Widget child = widget.itemBuilder(context, item, index);

          if (widget.addRepaintBoundaries) {
            child = RepaintBoundary(
              key: ValueKey('item_$index'),
              child: child,
            );
          }

          return child;
        },
      );
    }

    // Build list without separator
    return ListView.builder(
      controller: _scrollController,
      padding: widget.padding,
      physics: widget.physics,
      shrinkWrap: widget.shrinkWrap,
      addRepaintBoundaries: widget.addRepaintBoundaries,
      addAutomaticKeepAlives: widget.addAutomaticKeepAlives,
      itemCount: itemCount,
      itemBuilder: (context, index) {
        // Loading indicator at the end
        if (index >= widget.items.length) {
          return _buildLoadingIndicator();
        }

        // Build item
        final item = widget.items[index];
        Widget child = widget.itemBuilder(context, item, index);

        if (widget.addRepaintBoundaries) {
          child = RepaintBoundary(
            key: ValueKey('item_$index'),
            child: child,
          );
        }

        return child;
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    // Error state
    if (widget.hasError && widget.errorWidget != null) {
      return widget.errorWidget!;
    }

    // Empty state (no items and not loading)
    if (widget.items.isEmpty && !widget.isLoading) {
      return widget.emptyWidget ??
          const Center(
            child: Text('No items'),
          );
    }

    // Initial loading state
    if (widget.items.isEmpty && widget.isLoading) {
      return _buildLoadingIndicator();
    }

    // Build list with optional pull-to-refresh
    if (widget.onRefresh != null) {
      return RefreshIndicator(
        onRefresh: widget.onRefresh!,
        child: _buildList(),
      );
    }

    return _buildList();
  }
}

/// SahoolGridView - محسّن للعرض الشبكي
///
/// An optimized grid view with const constructor
class SahoolGridView<T> extends StatelessWidget {
  final List<T> items;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final int crossAxisCount;
  final double mainAxisSpacing;
  final double crossAxisSpacing;
  final double childAspectRatio;
  final EdgeInsets? padding;
  final ScrollController? controller;
  final ScrollPhysics? physics;
  final bool shrinkWrap;
  final bool addRepaintBoundaries;
  final Widget? emptyWidget;

  const SahoolGridView({
    super.key,
    required this.items,
    required this.itemBuilder,
    this.crossAxisCount = 2,
    this.mainAxisSpacing = 8.0,
    this.crossAxisSpacing = 8.0,
    this.childAspectRatio = 1.0,
    this.padding,
    this.controller,
    this.physics,
    this.shrinkWrap = false,
    this.addRepaintBoundaries = true,
    this.emptyWidget,
  });

  @override
  Widget build(BuildContext context) {
    // Empty state
    if (items.isEmpty) {
      return emptyWidget ??
          const Center(
            child: Text('No items'),
          );
    }

    return GridView.builder(
      controller: controller,
      padding: padding,
      physics: physics,
      shrinkWrap: shrinkWrap,
      addRepaintBoundaries: addRepaintBoundaries,
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        mainAxisSpacing: mainAxisSpacing,
        crossAxisSpacing: crossAxisSpacing,
        childAspectRatio: childAspectRatio,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        Widget child = itemBuilder(context, item, index);

        if (addRepaintBoundaries) {
          child = RepaintBoundary(
            key: ValueKey('grid_item_$index'),
            child: child,
          );
        }

        return child;
      },
    );
  }
}

/// SahoolSliverList - محسّن للقوائم المعقدة داخل CustomScrollView
///
/// Optimized sliver list for use in CustomScrollView
class SahoolSliverList<T> extends StatelessWidget {
  final List<T> items;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final bool addRepaintBoundaries;
  final bool addAutomaticKeepAlives;

  const SahoolSliverList({
    super.key,
    required this.items,
    required this.itemBuilder,
    this.addRepaintBoundaries = true,
    this.addAutomaticKeepAlives = false,
  });

  @override
  Widget build(BuildContext context) {
    return SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) {
          final item = items[index];
          Widget child = itemBuilder(context, item, index);

          if (addRepaintBoundaries) {
            child = RepaintBoundary(
              key: ValueKey('sliver_item_$index'),
              child: child,
            );
          }

          return child;
        },
        childCount: items.length,
        addRepaintBoundaries: addRepaintBoundaries,
        addAutomaticKeepAlives: addAutomaticKeepAlives,
      ),
    );
  }
}

/// Const helper widget for list items
///
/// Wraps list items with const constructor for better performance
class ConstListItem extends StatelessWidget {
  final Widget child;

  const ConstListItem({
    super.key,
    required this.child,
  });

  @override
  Widget build(BuildContext context) => child;
}

/// Performance-optimized list tile
///
/// A const-compatible list tile wrapper
class OptimizedListTile extends StatelessWidget {
  final Widget? leading;
  final Widget? title;
  final Widget? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;
  final EdgeInsets? contentPadding;

  const OptimizedListTile({
    super.key,
    this.leading,
    this.title,
    this.subtitle,
    this.trailing,
    this.onTap,
    this.contentPadding,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: leading,
      title: title,
      subtitle: subtitle,
      trailing: trailing,
      onTap: onTap,
      contentPadding: contentPadding,
    );
  }
}
