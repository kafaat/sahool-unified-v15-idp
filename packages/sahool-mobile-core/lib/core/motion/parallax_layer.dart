// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Parallax Layer Widgets
// ودجات طبقة المنظور - للتأثيرات البصرية متعددة العمق
// ═══════════════════════════════════════════════════════════════════════════

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

import 'motion_service.dart';
import 'parallax_controller.dart';

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX CONTAINER
// ─────────────────────────────────────────────────────────────────────────────

/// Container that provides parallax context to its children
/// حاوية توفر سياق المنظور لعناصرها الفرعية
class ParallaxContainer extends StatefulWidget {
  /// Child widget
  final Widget child;

  /// Custom parallax controller (optional, creates one if not provided)
  final ParallaxController? controller;

  /// Configuration for parallax effect
  final ParallaxConfig config;

  /// Whether to auto-start the parallax effect
  final bool autoStart;

  /// Screen identifier for per-screen enable/disable
  final String? screenId;

  const ParallaxContainer({
    super.key,
    required this.child,
    this.controller,
    this.config = ParallaxConfig.defaultConfig,
    this.autoStart = true,
    this.screenId,
  });

  @override
  State<ParallaxContainer> createState() => _ParallaxContainerState();

  /// Access the parallax controller from context
  static ParallaxController? of(BuildContext context) {
    return context
        .dependOnInheritedWidgetOfExactType<_ParallaxInheritedWidget>()
        ?.controller;
  }
}

class _ParallaxContainerState extends State<ParallaxContainer>
    with WidgetsBindingObserver {
  late ParallaxController _controller;
  bool _ownsController = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    // Use provided controller or create new one
    if (widget.controller != null) {
      _controller = widget.controller!;
    } else {
      _controller = ParallaxController(
        motionService: MotionService.instance,
        config: widget.config,
      );
      _ownsController = true;
    }

    // Set screen ID
    if (widget.screenId != null) {
      _controller.setCurrentScreen(widget.screenId);
    }

    // Auto-start if enabled
    if (widget.autoStart) {
      SchedulerBinding.instance.addPostFrameCallback((_) {
        _controller.start();
      });
    }
  }

  @override
  void didUpdateWidget(ParallaxContainer oldWidget) {
    super.didUpdateWidget(oldWidget);

    // Update config if changed
    if (oldWidget.config != widget.config) {
      _controller.updateConfig(widget.config);
    }

    // Update screen ID
    if (oldWidget.screenId != widget.screenId) {
      _controller.setCurrentScreen(widget.screenId);
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    // Pause/resume based on app lifecycle
    switch (state) {
      case AppLifecycleState.paused:
      case AppLifecycleState.inactive:
        MotionService.instance.pause();
        break;
      case AppLifecycleState.resumed:
        MotionService.instance.resume();
        break;
      default:
        break;
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);

    if (_ownsController) {
      _controller.dispose();
    }

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return _ParallaxInheritedWidget(
      controller: _controller,
      child: widget.child,
    );
  }
}

/// Inherited widget to provide parallax controller
class _ParallaxInheritedWidget extends InheritedWidget {
  final ParallaxController controller;

  const _ParallaxInheritedWidget({
    required this.controller,
    required super.child,
  });

  @override
  bool updateShouldNotify(_ParallaxInheritedWidget oldWidget) {
    return controller != oldWidget.controller;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX LAYER
// ─────────────────────────────────────────────────────────────────────────────

/// A single parallax layer with depth-based movement
/// طبقة منظور واحدة مع حركة قائمة على العمق
class ParallaxLayer extends StatelessWidget {
  /// Child widget
  final Widget child;

  /// Depth of this layer (0.0 = far background, 1.0 = foreground)
  final double depth;

  /// Additional offset multiplier
  final double offsetMultiplier;

  /// Whether to use inverse depth (foreground moves more)
  final bool inverseDepth;

  /// Whether to enable rotation based on tilt
  final bool enableRotation;

  /// Maximum rotation angle in degrees
  final double maxRotation;

  /// Whether to enable scale based on tilt
  final bool enableScale;

  /// Maximum scale factor
  final double maxScale;

  /// Animation duration for smooth transitions
  final Duration animationDuration;

  /// Animation curve
  final Curve animationCurve;

  const ParallaxLayer({
    super.key,
    required this.child,
    this.depth = ParallaxDepthLayers.content,
    this.offsetMultiplier = 1.0,
    this.inverseDepth = false,
    this.enableRotation = false,
    this.maxRotation = 5.0,
    this.enableScale = false,
    this.maxScale = 1.05,
    this.animationDuration = const Duration(milliseconds: 100),
    this.animationCurve = Curves.easeOutCubic,
  });

  @override
  Widget build(BuildContext context) {
    final controller = ParallaxContainer.of(context);

    if (controller == null) {
      return child;
    }

    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        // Get offset for this depth
        final offset = inverseDepth
            ? controller.getOffsetForDepthInverse(depth)
            : controller.getOffsetForDepth(depth);

        // Calculate transform values
        final dx = offset.x * offsetMultiplier;
        final dy = offset.y * offsetMultiplier;

        // Calculate rotation
        double rotation = 0.0;
        if (enableRotation) {
          rotation = offset.normalizedX * maxRotation * (math.pi / 180);
        }

        // Calculate scale
        double scale = 1.0;
        if (enableScale) {
          final tiltMagnitude = math.sqrt(
            offset.normalizedX * offset.normalizedX +
                offset.normalizedY * offset.normalizedY,
          );
          scale = 1.0 + (tiltMagnitude * (maxScale - 1.0));
        }

        return TweenAnimationBuilder<Offset>(
          tween: Tween(begin: Offset.zero, end: Offset(dx, dy)),
          duration: animationDuration,
          curve: animationCurve,
          builder: (context, animatedOffset, child) {
            return Transform(
              transform: Matrix4.identity()
                ..translate(animatedOffset.dx, animatedOffset.dy)
                ..rotateZ(rotation)
                ..scale(scale),
              alignment: Alignment.center,
              child: child,
            );
          },
          child: child,
        );
      },
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX IMAGE
// ─────────────────────────────────────────────────────────────────────────────

/// Image with parallax effect
/// صورة مع تأثير المنظور
class ParallaxImage extends StatelessWidget {
  /// Image provider
  final ImageProvider image;

  /// Depth of this layer
  final double depth;

  /// How to fit the image
  final BoxFit fit;

  /// Image width
  final double? width;

  /// Image height
  final double? height;

  /// Border radius
  final BorderRadius? borderRadius;

  /// Additional offset multiplier
  final double offsetMultiplier;

  /// Whether to zoom slightly larger for parallax headroom
  final bool enableOverscale;

  /// Overscale factor (how much larger to make the image)
  final double overscaleFactor;

  const ParallaxImage({
    super.key,
    required this.image,
    this.depth = ParallaxDepthLayers.farBackground,
    this.fit = BoxFit.cover,
    this.width,
    this.height,
    this.borderRadius,
    this.offsetMultiplier = 1.0,
    this.enableOverscale = true,
    this.overscaleFactor = 1.15,
  });

  /// Create from asset path
  factory ParallaxImage.asset(
    String assetPath, {
    Key? key,
    double depth = ParallaxDepthLayers.farBackground,
    BoxFit fit = BoxFit.cover,
    double? width,
    double? height,
    BorderRadius? borderRadius,
    double offsetMultiplier = 1.0,
    bool enableOverscale = true,
    double overscaleFactor = 1.15,
  }) {
    return ParallaxImage(
      key: key,
      image: AssetImage(assetPath),
      depth: depth,
      fit: fit,
      width: width,
      height: height,
      borderRadius: borderRadius,
      offsetMultiplier: offsetMultiplier,
      enableOverscale: enableOverscale,
      overscaleFactor: overscaleFactor,
    );
  }

  /// Create from network URL
  factory ParallaxImage.network(
    String url, {
    Key? key,
    double depth = ParallaxDepthLayers.farBackground,
    BoxFit fit = BoxFit.cover,
    double? width,
    double? height,
    BorderRadius? borderRadius,
    double offsetMultiplier = 1.0,
    bool enableOverscale = true,
    double overscaleFactor = 1.15,
  }) {
    return ParallaxImage(
      key: key,
      image: NetworkImage(url),
      depth: depth,
      fit: fit,
      width: width,
      height: height,
      borderRadius: borderRadius,
      offsetMultiplier: offsetMultiplier,
      enableOverscale: enableOverscale,
      overscaleFactor: overscaleFactor,
    );
  }

  @override
  Widget build(BuildContext context) {
    Widget imageWidget = Image(
      image: image,
      fit: fit,
      width: enableOverscale && width != null ? width! * overscaleFactor : width,
      height:
          enableOverscale && height != null ? height! * overscaleFactor : height,
    );

    if (borderRadius != null) {
      imageWidget = ClipRRect(
        borderRadius: borderRadius!,
        child: imageWidget,
      );
    }

    // Wrap in overscale container if needed
    if (enableOverscale) {
      imageWidget = Transform.scale(
        scale: overscaleFactor,
        child: imageWidget,
      );
    }

    return ClipRect(
      child: SizedBox(
        width: width,
        height: height,
        child: ParallaxLayer(
          depth: depth,
          offsetMultiplier: offsetMultiplier,
          child: imageWidget,
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX CARD
// ─────────────────────────────────────────────────────────────────────────────

/// Card with parallax effect
/// بطاقة مع تأثير المنظور
class ParallaxCard extends StatelessWidget {
  /// Card content
  final Widget child;

  /// Depth of this layer
  final double depth;

  /// Card elevation
  final double elevation;

  /// Card color
  final Color? color;

  /// Card border radius
  final BorderRadius borderRadius;

  /// Card margin
  final EdgeInsets? margin;

  /// Card padding
  final EdgeInsets? padding;

  /// Additional offset multiplier
  final double offsetMultiplier;

  /// Whether to enable dynamic shadow based on tilt
  final bool dynamicShadow;

  /// Maximum shadow offset
  final double maxShadowOffset;

  /// Whether to enable subtle rotation
  final bool enableRotation;

  /// Maximum rotation angle
  final double maxRotation;

  /// On tap callback
  final VoidCallback? onTap;

  const ParallaxCard({
    super.key,
    required this.child,
    this.depth = ParallaxDepthLayers.content,
    this.elevation = 4.0,
    this.color,
    this.borderRadius = const BorderRadius.all(Radius.circular(16)),
    this.margin,
    this.padding,
    this.offsetMultiplier = 1.0,
    this.dynamicShadow = true,
    this.maxShadowOffset = 8.0,
    this.enableRotation = false,
    this.maxRotation = 3.0,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final controller = ParallaxContainer.of(context);

    if (controller == null) {
      return _buildCard(context, ParallaxOffset.zero);
    }

    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        final offset = controller.currentOffset;
        return _buildCard(context, offset);
      },
    );
  }

  Widget _buildCard(BuildContext context, ParallaxOffset offset) {
    // Calculate dynamic shadow
    List<BoxShadow> shadows = [];
    if (dynamicShadow) {
      final shadowX = -offset.normalizedX * maxShadowOffset;
      final shadowY = -offset.normalizedY * maxShadowOffset;

      shadows = [
        BoxShadow(
          color: Colors.black.withValues(alpha: 0.1),
          blurRadius: elevation * 2,
          offset: Offset(shadowX, shadowY + elevation),
        ),
        BoxShadow(
          color: Colors.black.withValues(alpha: 0.05),
          blurRadius: elevation,
          offset: Offset(shadowX / 2, shadowY / 2 + elevation / 2),
        ),
      ];
    } else {
      shadows = [
        BoxShadow(
          color: Colors.black.withValues(alpha: 0.1),
          blurRadius: elevation * 2,
          offset: Offset(0, elevation),
        ),
      ];
    }

    Widget card = Container(
      margin: margin,
      padding: padding,
      decoration: BoxDecoration(
        color: color ?? Theme.of(context).cardColor,
        borderRadius: borderRadius,
        boxShadow: shadows,
      ),
      child: child,
    );

    if (onTap != null) {
      card = GestureDetector(
        onTap: onTap,
        child: card,
      );
    }

    return ParallaxLayer(
      depth: depth,
      offsetMultiplier: offsetMultiplier,
      enableRotation: enableRotation,
      maxRotation: maxRotation,
      child: card,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX STACK
// ─────────────────────────────────────────────────────────────────────────────

/// Stack with automatic depth assignment to children
/// مكدس مع تعيين تلقائي للعمق للعناصر الفرعية
class ParallaxStack extends StatelessWidget {
  /// Children widgets (first = background, last = foreground)
  final List<Widget> children;

  /// Base depth for first child
  final double baseDepth;

  /// Depth increment per child
  final double depthIncrement;

  /// Alignment of children
  final AlignmentGeometry alignment;

  /// Fit for children
  final StackFit fit;

  /// Clip behavior
  final Clip clipBehavior;

  const ParallaxStack({
    super.key,
    required this.children,
    this.baseDepth = 0.0,
    this.depthIncrement = 0.15,
    this.alignment = AlignmentDirectional.topStart,
    this.fit = StackFit.loose,
    this.clipBehavior = Clip.hardEdge,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      alignment: alignment,
      fit: fit,
      clipBehavior: clipBehavior,
      children: List.generate(children.length, (index) {
        final depth = (baseDepth + (index * depthIncrement)).clamp(0.0, 1.0);
        return ParallaxLayer(
          depth: depth,
          child: children[index],
        );
      }),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX BACKGROUND
// ─────────────────────────────────────────────────────────────────────────────

/// Full-screen parallax background
/// خلفية منظور بملء الشاشة
class ParallaxBackground extends StatelessWidget {
  /// Background image or widget
  final Widget background;

  /// Foreground content
  final Widget child;

  /// Background depth
  final double backgroundDepth;

  /// Background offset multiplier
  final double backgroundOffsetMultiplier;

  /// Whether to add gradient overlay
  final bool addGradientOverlay;

  /// Gradient colors (top to bottom)
  final List<Color>? gradientColors;

  const ParallaxBackground({
    super.key,
    required this.background,
    required this.child,
    this.backgroundDepth = ParallaxDepthLayers.farBackground,
    this.backgroundOffsetMultiplier = 1.5,
    this.addGradientOverlay = true,
    this.gradientColors,
  });

  /// Create with image asset
  factory ParallaxBackground.asset(
    String assetPath, {
    Key? key,
    required Widget child,
    double backgroundDepth = ParallaxDepthLayers.farBackground,
    double backgroundOffsetMultiplier = 1.5,
    bool addGradientOverlay = true,
    List<Color>? gradientColors,
  }) {
    return ParallaxBackground(
      key: key,
      background: Image.asset(
        assetPath,
        fit: BoxFit.cover,
        width: double.infinity,
        height: double.infinity,
      ),
      backgroundDepth: backgroundDepth,
      backgroundOffsetMultiplier: backgroundOffsetMultiplier,
      addGradientOverlay: addGradientOverlay,
      gradientColors: gradientColors,
      child: child,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // Parallax background
        ParallaxLayer(
          depth: backgroundDepth,
          offsetMultiplier: backgroundOffsetMultiplier,
          child: Transform.scale(
            scale: 1.2, // Slightly larger for parallax headroom
            child: background,
          ),
        ),

        // Optional gradient overlay
        if (addGradientOverlay)
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: gradientColors ??
                    [
                      Colors.black.withValues(alpha: 0.3),
                      Colors.transparent,
                      Colors.black.withValues(alpha: 0.5),
                    ],
              ),
            ),
          ),

        // Foreground content
        child,
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX ICON
// ─────────────────────────────────────────────────────────────────────────────

/// Icon with parallax effect
/// أيقونة مع تأثير المنظور
class ParallaxIcon extends StatelessWidget {
  /// Icon data
  final IconData icon;

  /// Icon size
  final double size;

  /// Icon color
  final Color? color;

  /// Depth layer
  final double depth;

  /// Offset multiplier
  final double offsetMultiplier;

  /// Enable rotation
  final bool enableRotation;

  const ParallaxIcon({
    super.key,
    required this.icon,
    this.size = 24.0,
    this.color,
    this.depth = ParallaxDepthLayers.content,
    this.offsetMultiplier = 1.0,
    this.enableRotation = false,
  });

  @override
  Widget build(BuildContext context) {
    return ParallaxLayer(
      depth: depth,
      offsetMultiplier: offsetMultiplier,
      enableRotation: enableRotation,
      maxRotation: 10.0,
      child: Icon(
        icon,
        size: size,
        color: color,
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX TEXT
// ─────────────────────────────────────────────────────────────────────────────

/// Text with parallax effect
/// نص مع تأثير المنظور
class ParallaxText extends StatelessWidget {
  /// Text content
  final String text;

  /// Text style
  final TextStyle? style;

  /// Text alignment
  final TextAlign? textAlign;

  /// Depth layer
  final double depth;

  /// Offset multiplier
  final double offsetMultiplier;

  const ParallaxText({
    super.key,
    required this.text,
    this.style,
    this.textAlign,
    this.depth = ParallaxDepthLayers.content,
    this.offsetMultiplier = 1.0,
  });

  @override
  Widget build(BuildContext context) {
    return ParallaxLayer(
      depth: depth,
      offsetMultiplier: offsetMultiplier,
      child: Text(
        text,
        style: style,
        textAlign: textAlign,
      ),
    );
  }
}
