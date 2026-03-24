import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// SAHOOL Gesture Animations - تحريكات الإيماءات
/// Interactive animations triggered by user gestures
///
/// Features:
/// - Swipe to delete animation
/// - Pull to refresh animation
/// - Long press scale
/// - Drag and drop animations

// =============================================================================
// SWIPE TO DELETE - التمرير للحذف
// =============================================================================

/// Swipe Action Direction
enum SwipeDirection {
  left,
  right,
  both,
}

/// Swipe Action Item - عنصر إجراء التمرير
class SwipeActionItem {
  final IconData icon;
  final Color backgroundColor;
  final Color iconColor;
  final String? label;
  final VoidCallback onTap;

  const SwipeActionItem({
    required this.icon,
    required this.backgroundColor,
    this.iconColor = Colors.white,
    this.label,
    required this.onTap,
  });
}

/// Swipe to Delete Widget - عنصر التمرير للحذف
class SwipeToDelete extends StatefulWidget {
  final Widget child;
  final List<SwipeActionItem> leftActions;
  final List<SwipeActionItem> rightActions;
  final double actionWidth;
  final Duration animationDuration;
  final Curve curve;
  final double threshold;
  final bool confirmDismiss;
  final Future<bool> Function()? onDismissConfirm;
  final VoidCallback? onDismiss;

  const SwipeToDelete({
    super.key,
    required this.child,
    this.leftActions = const [],
    this.rightActions = const [],
    this.actionWidth = 80,
    this.animationDuration = const Duration(milliseconds: 300),
    this.curve = Curves.easeOutCubic,
    this.threshold = 0.4,
    this.confirmDismiss = false,
    this.onDismissConfirm,
    this.onDismiss,
  });

  @override
  State<SwipeToDelete> createState() => _SwipeToDeleteState();
}

class _SwipeToDeleteState extends State<SwipeToDelete>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  double _dragExtent = 0;
  bool _isDismissed = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _slideAnimation = Tween<Offset>(
      begin: Offset.zero,
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  double get _maxLeftDrag => widget.leftActions.length * widget.actionWidth;
  double get _maxRightDrag => widget.rightActions.length * widget.actionWidth;

  void _handleDragStart(DragStartDetails details) {
    if (_isDismissed) return;
    _controller.stop();
  }

  void _handleDragUpdate(DragUpdateDetails details) {
    if (_isDismissed) return;

    setState(() {
      _dragExtent += details.primaryDelta!;

      // Clamp drag extent
      if (_dragExtent > 0 && widget.leftActions.isEmpty) {
        _dragExtent = 0;
      } else if (_dragExtent < 0 && widget.rightActions.isEmpty) {
        _dragExtent = 0;
      }

      // Apply resistance at edges
      if (_dragExtent > _maxLeftDrag) {
        _dragExtent = _maxLeftDrag +
            (_dragExtent - _maxLeftDrag) * 0.2;
      } else if (_dragExtent < -_maxRightDrag) {
        _dragExtent = -_maxRightDrag +
            (_dragExtent + _maxRightDrag) * 0.2;
      }
    });
  }

  Future<void> _handleDragEnd(DragEndDetails details) async {
    if (_isDismissed) return;

    final velocity = details.primaryVelocity ?? 0;
    final screenWidth = MediaQuery.of(context).size.width;

    // Check for full swipe dismiss
    if (_dragExtent.abs() > screenWidth * widget.threshold || velocity.abs() > 1000) {
      if (widget.confirmDismiss && widget.onDismissConfirm != null) {
        final confirmed = await widget.onDismissConfirm!();
        if (!confirmed) {
          _animateToPosition(0);
          return;
        }
      }

      if (widget.onDismiss != null) {
        setState(() => _isDismissed = true);
        _animateToPosition(_dragExtent > 0 ? screenWidth : -screenWidth);
        widget.onDismiss!();
        return;
      }
    }

    // Snap to action position or back to center
    double targetPosition = 0;
    if (_dragExtent > _maxLeftDrag * 0.5 && widget.leftActions.isNotEmpty) {
      targetPosition = _maxLeftDrag;
    } else if (_dragExtent < -_maxRightDrag * 0.5 && widget.rightActions.isNotEmpty) {
      targetPosition = -_maxRightDrag;
    }

    _animateToPosition(targetPosition);
  }

  void _animateToPosition(double position) {
    _slideAnimation = Tween<Offset>(
      begin: Offset(_dragExtent / MediaQuery.of(context).size.width, 0),
      end: Offset(position / MediaQuery.of(context).size.width, 0),
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));

    _controller.addListener(_updateDragExtent);
    // ignore: unawaited_futures
    _controller.forward(from: 0).then((_) {
      _controller.removeListener(_updateDragExtent);
      if (!_isDismissed) {
        setState(() => _dragExtent = position);
      }
    });
  }

  void _updateDragExtent() {
    final screenWidth = MediaQuery.of(context).size.width;
    setState(() {
      _dragExtent = _slideAnimation.value.dx * screenWidth;
    });
  }

  void close() {
    _animateToPosition(0);
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Background actions
        Positioned.fill(
          child: Row(
            children: [
              // Left actions
              if (widget.leftActions.isNotEmpty)
                _buildActionRow(widget.leftActions, true),
              const Spacer(),
              // Right actions
              if (widget.rightActions.isNotEmpty)
                _buildActionRow(widget.rightActions, false),
            ],
          ),
        ),
        // Main content
        GestureDetector(
          onHorizontalDragStart: _handleDragStart,
          onHorizontalDragUpdate: _handleDragUpdate,
          onHorizontalDragEnd: _handleDragEnd,
          child: Transform.translate(
            offset: Offset(_dragExtent, 0),
            child: widget.child,
          ),
        ),
      ],
    );
  }

  Widget _buildActionRow(List<SwipeActionItem> actions, bool isLeft) {
    final progress = isLeft
        ? (_dragExtent / _maxLeftDrag).clamp(0.0, 1.0)
        : (-_dragExtent / _maxRightDrag).clamp(0.0, 1.0);

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: actions.asMap().entries.map((entry) {
        final index = entry.key;
        final action = entry.value;
        final delay = index / actions.length;
        final actionProgress = ((progress - delay) / (1 - delay)).clamp(0.0, 1.0);

        return GestureDetector(
          onTap: () {
            action.onTap();
            close();
          },
          child: Container(
            width: widget.actionWidth,
            color: action.backgroundColor,
            child: Center(
              child: Transform.scale(
                scale: 0.5 + (actionProgress * 0.5),
                child: Opacity(
                  opacity: actionProgress,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(action.icon, color: action.iconColor, size: 24),
                      if (action.label != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          action.label!,
                          style: TextStyle(
                            color: action.iconColor,
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}

// =============================================================================
// PULL TO REFRESH - السحب للتحديث
// =============================================================================

/// Custom Pull to Refresh - سحب للتحديث مخصص
class SahoolPullToRefresh extends StatefulWidget {
  final Widget child;
  final Future<void> Function() onRefresh;
  final Color indicatorColor;
  final Color backgroundColor;
  final double triggerDistance;
  final Widget? customIndicator;

  const SahoolPullToRefresh({
    super.key,
    required this.child,
    required this.onRefresh,
    this.indicatorColor = const Color(0xFF1B5E20),
    this.backgroundColor = Colors.white,
    this.triggerDistance = 100,
    this.customIndicator,
  });

  @override
  State<SahoolPullToRefresh> createState() => _SahoolPullToRefreshState();
}

class _SahoolPullToRefreshState extends State<SahoolPullToRefresh>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  double _dragOffset = 0;
  bool _isRefreshing = false;
  bool _triggered = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleDragUpdate(double delta) {
    if (_isRefreshing) return;

    setState(() {
      _dragOffset += delta;
      if (_dragOffset < 0) _dragOffset = 0;

      // Apply resistance after threshold
      if (_dragOffset > widget.triggerDistance) {
        final extra = _dragOffset - widget.triggerDistance;
        _dragOffset = widget.triggerDistance + (extra * 0.3);
      }

      if (_dragOffset >= widget.triggerDistance && !_triggered) {
        _triggered = true;
        HapticFeedback.mediumImpact();
      }
    });
  }

  Future<void> _handleDragEnd() async {
    if (_isRefreshing) return;

    if (_triggered) {
      setState(() {
        _isRefreshing = true;
        _dragOffset = widget.triggerDistance;
      });

      _controller.repeat();

      await widget.onRefresh();

      _controller.stop();
      setState(() {
        _isRefreshing = false;
        _triggered = false;
      });
    }

    // Animate back
    final startOffset = _dragOffset;
    final animation = Tween<double>(begin: startOffset, end: 0).animate(
      CurvedAnimation(
        parent: AnimationController(
          duration: const Duration(milliseconds: 300),
          vsync: this,
        )..forward(),
        curve: Curves.easeOutCubic,
      ),
    );

    animation.addListener(() {
      if (mounted) {
        setState(() {
          _dragOffset = animation.value;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return NotificationListener<ScrollNotification>(
      onNotification: (notification) {
        if (notification is ScrollUpdateNotification) {
          if (notification.metrics.pixels < 0) {
            _handleDragUpdate(-notification.scrollDelta!);
          }
        }
        if (notification is ScrollEndNotification) {
          _handleDragEnd();
        }
        return false;
      },
      child: Stack(
        children: [
          // Refresh indicator
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              height: _dragOffset,
              color: widget.backgroundColor,
              alignment: Alignment.center,
              child: _buildIndicator(),
            ),
          ),
          // Main content
          Transform.translate(
            offset: Offset(0, _dragOffset),
            child: widget.child,
          ),
        ],
      ),
    );
  }

  Widget _buildIndicator() {
    if (widget.customIndicator != null) {
      return widget.customIndicator!;
    }

    final progress = (_dragOffset / widget.triggerDistance).clamp(0.0, 1.0);

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final rotation = _isRefreshing
            ? _controller.value * 2 * math.pi
            : progress * math.pi;

        return Transform.rotate(
          angle: rotation,
          child: Opacity(
            opacity: progress,
            child: Icon(
              _triggered ? Icons.sync : Icons.arrow_downward,
              color: widget.indicatorColor,
              size: 32,
            ),
          ),
        );
      },
    );
  }
}

// =============================================================================
// LONG PRESS SCALE - الضغط المطول للتكبير
// =============================================================================

/// Long Press Scale Widget - عنصر الضغط المطول للتكبير
class LongPressScale extends StatefulWidget {
  final Widget child;
  final VoidCallback? onLongPress;
  final VoidCallback? onTap;
  final double scale;
  final Duration duration;
  final Duration delay;
  final bool enableHaptic;

  const LongPressScale({
    super.key,
    required this.child,
    this.onLongPress,
    this.onTap,
    this.scale = 0.95,
    this.duration = const Duration(milliseconds: 200),
    this.delay = const Duration(milliseconds: 300),
    this.enableHaptic = true,
  });

  @override
  State<LongPressScale> createState() => _LongPressScaleState();
}

class _LongPressScaleState extends State<LongPressScale>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: widget.scale,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    setState(() => _isPressed = true);
    _controller.forward();
  }

  void _onTapUp(TapUpDetails details) {
    setState(() => _isPressed = false);
    _controller.reverse();
  }

  void _onTapCancel() {
    setState(() => _isPressed = false);
    _controller.reverse();
  }

  void _onLongPress() {
    if (widget.enableHaptic) {
      HapticFeedback.mediumImpact();
    }
    widget.onLongPress?.call();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: _onTapDown,
      onTapUp: _onTapUp,
      onTapCancel: _onTapCancel,
      onTap: widget.onTap,
      onLongPress: widget.onLongPress != null ? _onLongPress : null,
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

/// Long Press Preview - معاينة الضغط المطول
/// Shows a preview popup on long press (like iOS 3D Touch)
class LongPressPreview extends StatefulWidget {
  final Widget child;
  final Widget preview;
  final List<PreviewAction>? actions;
  final Duration previewDelay;
  final bool enableHaptic;

  const LongPressPreview({
    super.key,
    required this.child,
    required this.preview,
    this.actions,
    this.previewDelay = const Duration(milliseconds: 300),
    this.enableHaptic = true,
  });

  @override
  State<LongPressPreview> createState() => _LongPressPreviewState();
}

class PreviewAction {
  final String title;
  final IconData icon;
  final Color? color;
  final VoidCallback onTap;
  final bool isDestructive;

  const PreviewAction({
    required this.title,
    required this.icon,
    required this.onTap,
    this.color,
    this.isDestructive = false,
  });
}

class _LongPressPreviewState extends State<LongPressPreview> {
  OverlayEntry? _overlayEntry;
  final LayerLink _layerLink = LayerLink();

  void _showPreview(BuildContext context) {
    if (widget.enableHaptic) {
      HapticFeedback.mediumImpact();
    }

    _overlayEntry = OverlayEntry(
      builder: (context) => _PreviewOverlay(
        link: _layerLink,
        preview: widget.preview,
        actions: widget.actions,
        onDismiss: _hidePreview,
      ),
    );

    Overlay.of(context).insert(_overlayEntry!);
  }

  void _hidePreview() {
    _overlayEntry?.remove();
    _overlayEntry = null;
  }

  @override
  void dispose() {
    _hidePreview();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return CompositedTransformTarget(
      link: _layerLink,
      child: GestureDetector(
        onLongPress: () => _showPreview(context),
        child: widget.child,
      ),
    );
  }
}

class _PreviewOverlay extends StatefulWidget {
  final LayerLink link;
  final Widget preview;
  final List<PreviewAction>? actions;
  final VoidCallback onDismiss;

  const _PreviewOverlay({
    required this.link,
    required this.preview,
    this.actions,
    required this.onDismiss,
  });

  @override
  State<_PreviewOverlay> createState() => _PreviewOverlayState();
}

class _PreviewOverlayState extends State<_PreviewOverlay>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutBack),
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _dismiss() async {
    await _controller.reverse();
    widget.onDismiss();
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      type: MaterialType.transparency,
      child: GestureDetector(
        onTap: _dismiss,
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return ColoredBox(
              color: Colors.black.withValues(alpha: _fadeAnimation.value * 0.5),
              child: Center(
                child: Transform.scale(
                  scale: _scaleAnimation.value,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Preview content
                      ClipRRect(
                        borderRadius: BorderRadius.circular(16),
                        child: SizedBox(
                          width: MediaQuery.of(context).size.width * 0.85,
                          child: widget.preview,
                        ),
                      ),
                      // Actions
                      if (widget.actions != null && widget.actions!.isNotEmpty) ...[
                        const SizedBox(height: 16),
                        Container(
                          width: MediaQuery.of(context).size.width * 0.85,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            children: widget.actions!.map((action) {
                              return ListTile(
                                leading: Icon(
                                  action.icon,
                                  color: action.isDestructive
                                      ? Colors.red
                                      : action.color,
                                ),
                                title: Text(
                                  action.title,
                                  style: TextStyle(
                                    color: action.isDestructive
                                        ? Colors.red
                                        : null,
                                  ),
                                ),
                                onTap: () {
                                  _dismiss();
                                  action.onTap();
                                },
                              );
                            }).toList(),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

// =============================================================================
// DRAG AND DROP ANIMATIONS - السحب والإفلات
// =============================================================================

/// Draggable Item with Animation - عنصر قابل للسحب مع تحريك
class AnimatedDraggable<T extends Object> extends StatefulWidget {
  final T data;
  final Widget child;
  final Widget? feedback;
  final Widget? childWhenDragging;
  final Axis? axis;
  final void Function(DraggableDetails)? onDragStarted;
  final void Function(DraggableDetails)? onDragEnd;
  final void Function(Velocity, Offset)? onDraggableCanceled;
  final double feedbackScale;
  final double feedbackOpacity;
  final Duration animationDuration;

  const AnimatedDraggable({
    super.key,
    required this.data,
    required this.child,
    this.feedback,
    this.childWhenDragging,
    this.axis,
    this.onDragStarted,
    this.onDragEnd,
    this.onDraggableCanceled,
    this.feedbackScale = 1.1,
    this.feedbackOpacity = 0.8,
    this.animationDuration = const Duration(milliseconds: 200),
  });

  @override
  State<AnimatedDraggable<T>> createState() => _AnimatedDraggableState<T>();
}

class _AnimatedDraggableState<T extends Object> extends State<AnimatedDraggable<T>>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  bool _isDragging = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: widget.feedbackScale,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutBack));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LongPressDraggable<T>(
      data: widget.data,
      axis: widget.axis,
      delay: const Duration(milliseconds: 150),
      onDragStarted: () {
        setState(() => _isDragging = true);
        _controller.forward();
        HapticFeedback.mediumImpact();
        widget.onDragStarted?.call(DraggableDetails(
          wasAccepted: false,
          velocity: Velocity.zero,
          offset: Offset.zero,
        ));
      },
      onDragEnd: (details) {
        setState(() => _isDragging = false);
        _controller.reverse();
        widget.onDragEnd?.call(details);
      },
      onDraggableCanceled: widget.onDraggableCanceled,
      feedback: Material(
        type: MaterialType.transparency,
        child: AnimatedBuilder(
          animation: _scaleAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Opacity(
                opacity: widget.feedbackOpacity,
                child: widget.feedback ?? widget.child,
              ),
            );
          },
        ),
      ),
      childWhenDragging: widget.childWhenDragging ??
          Opacity(
            opacity: 0.3,
            child: widget.child,
          ),
      child: AnimatedOpacity(
        duration: widget.animationDuration,
        opacity: _isDragging ? 0.5 : 1.0,
        child: widget.child,
      ),
    );
  }
}

/// Animated Drop Target - هدف إفلات متحرك
class AnimatedDropTarget<T extends Object> extends StatefulWidget {
  final Widget child;
  final Widget? hoverChild;
  final void Function(T data) onAccept;
  final bool Function(T? data)? onWillAccept;
  final void Function(T? data)? onLeave;
  final Duration animationDuration;
  final double hoverScale;
  final Color? hoverColor;

  const AnimatedDropTarget({
    super.key,
    required this.child,
    this.hoverChild,
    required this.onAccept,
    this.onWillAccept,
    this.onLeave,
    this.animationDuration = const Duration(milliseconds: 200),
    this.hoverScale = 1.05,
    this.hoverColor,
  });

  @override
  State<AnimatedDropTarget<T>> createState() => _AnimatedDropTargetState<T>();
}

class _AnimatedDropTargetState<T extends Object> extends State<AnimatedDropTarget<T>>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  bool _isHovering = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: widget.hoverScale,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutBack));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return DragTarget<T>(
      onWillAcceptWithDetails: (details) {
        final willAccept = widget.onWillAccept?.call(details.data) ?? true;
        if (willAccept) {
          setState(() => _isHovering = true);
          _controller.forward();
          HapticFeedback.selectionClick();
        }
        return willAccept;
      },
      onLeave: (data) {
        setState(() => _isHovering = false);
        _controller.reverse();
        widget.onLeave?.call(data);
      },
      onAcceptWithDetails: (details) {
        setState(() => _isHovering = false);
        _controller.reverse();
        HapticFeedback.heavyImpact();
        widget.onAccept(details.data);
      },
      builder: (context, candidateData, rejectedData) {
        return AnimatedBuilder(
          animation: _scaleAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: AnimatedContainer(
                duration: widget.animationDuration,
                decoration: BoxDecoration(
                  color: _isHovering ? widget.hoverColor?.withValues(alpha: 0.2) : null,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: _isHovering
                    ? (widget.hoverChild ?? widget.child)
                    : widget.child,
              ),
            );
          },
        );
      },
    );
  }
}

// =============================================================================
// REORDERABLE LIST ANIMATION - قائمة قابلة لإعادة الترتيب
// =============================================================================

/// Animated Reorderable List - قائمة قابلة لإعادة الترتيب متحركة
class AnimatedReorderableList<T> extends StatefulWidget {
  final List<T> items;
  final Widget Function(T item, int index, Animation<double> animation) itemBuilder;
  final void Function(int oldIndex, int newIndex) onReorder;
  final EdgeInsets? padding;
  final Duration animationDuration;
  final ScrollController? scrollController;

  const AnimatedReorderableList({
    super.key,
    required this.items,
    required this.itemBuilder,
    required this.onReorder,
    this.padding,
    this.animationDuration = const Duration(milliseconds: 300),
    this.scrollController,
  });

  @override
  State<AnimatedReorderableList<T>> createState() =>
      _AnimatedReorderableListState<T>();
}

class _AnimatedReorderableListState<T> extends State<AnimatedReorderableList<T>> {
  @override
  Widget build(BuildContext context) {
    return ReorderableListView.builder(
      scrollController: widget.scrollController,
      padding: widget.padding,
      itemCount: widget.items.length,
      onReorder: widget.onReorder,
      proxyDecorator: (child, index, animation) {
        return AnimatedBuilder(
          animation: animation,
          builder: (context, child) {
            final scale = Tween<double>(begin: 1.0, end: 1.05).animate(
              CurvedAnimation(
                parent: animation,
                curve: Curves.easeInOut,
              ),
            );

            final elevation = Tween<double>(begin: 0.0, end: 8.0).animate(
              CurvedAnimation(
                parent: animation,
                curve: Curves.easeInOut,
              ),
            );

            return Transform.scale(
              scale: scale.value,
              child: Material(
                elevation: elevation.value,
                borderRadius: BorderRadius.circular(12),
                child: child,
              ),
            );
          },
          child: child,
        );
      },
      itemBuilder: (context, index) {
        final item = widget.items[index];
        return ReorderableDragStartListener(
          key: ValueKey(item.hashCode),
          index: index,
          child: widget.itemBuilder(
            item,
            index,
            const AlwaysStoppedAnimation(1.0),
          ),
        );
      },
    );
  }
}

// =============================================================================
// PARALLAX GESTURE - إيماءة المنظور
// =============================================================================

/// Parallax Gesture Widget - عنصر إيماءة المنظور
/// Creates a parallax effect based on touch position
class ParallaxGesture extends StatefulWidget {
  final Widget child;
  final double maxOffset;
  final Duration animationDuration;
  final Curve curve;

  const ParallaxGesture({
    super.key,
    required this.child,
    this.maxOffset = 10,
    this.animationDuration = const Duration(milliseconds: 150),
    this.curve = Curves.easeOut,
  });

  @override
  State<ParallaxGesture> createState() => _ParallaxGestureState();
}

class _ParallaxGestureState extends State<ParallaxGesture>
    with SingleTickerProviderStateMixin {
  Offset _offset = Offset.zero;
  bool _isTouching = false;

  void _handlePanUpdate(DragUpdateDetails details) {
    setState(() {
      final size = context.size ?? Size.zero;
      final center = Offset(size.width / 2, size.height / 2);
      final position = details.localPosition - center;

      _offset = Offset(
        (position.dx / center.dx * widget.maxOffset).clamp(-widget.maxOffset, widget.maxOffset),
        (position.dy / center.dy * widget.maxOffset).clamp(-widget.maxOffset, widget.maxOffset),
      );
    });
  }

  void _handlePanStart(DragStartDetails details) {
    setState(() => _isTouching = true);
  }

  void _handlePanEnd(DragEndDetails details) {
    setState(() {
      _isTouching = false;
      _offset = Offset.zero;
    });
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanStart: _handlePanStart,
      onPanUpdate: _handlePanUpdate,
      onPanEnd: _handlePanEnd,
      child: AnimatedContainer(
        duration: widget.animationDuration,
        curve: widget.curve,
        transform: Matrix4.identity()
          ..translate(_offset.dx, _offset.dy),
        child: widget.child,
      ),
    );
  }
}
