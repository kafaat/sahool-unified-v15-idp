import 'package:flutter/material.dart';

/// SAHOOL Hero Animations - تحريكات البطل
/// Smooth hero transitions between screens
///
/// Features:
/// - Field card to detail hero
/// - Image zoom hero
/// - Custom hero controllers
/// - Flight shuttle builders

// =============================================================================
// HERO TAG CONSTANTS - ثوابت علامات البطل
// =============================================================================

/// Hero tags for consistent animations across the app
class HeroTags {
  /// Field card hero tag
  static String fieldCard(String fieldId) => 'field_card_$fieldId';

  /// Field image hero tag
  static String fieldImage(String fieldId) => 'field_image_$fieldId';

  /// Field title hero tag
  static String fieldTitle(String fieldId) => 'field_title_$fieldId';

  /// Crop image hero tag
  static String cropImage(String cropId) => 'crop_image_$cropId';

  /// Task card hero tag
  static String taskCard(String taskId) => 'task_card_$taskId';

  /// User avatar hero tag
  static String userAvatar(String userId) => 'user_avatar_$userId';

  /// Notification hero tag
  static String notification(String notificationId) => 'notification_$notificationId';

  /// Chart hero tag
  static String chart(String chartId) => 'chart_$chartId';

  /// FAB hero tag
  static const String fab = 'floating_action_button';

  /// App bar hero tag
  static const String appBar = 'app_bar_hero';

  /// Search bar hero tag
  static const String searchBar = 'search_bar_hero';
}

// =============================================================================
// FIELD CARD HERO - بطل بطاقة الحقل
// =============================================================================

/// Field Card Hero Widget - عنصر بطل بطاقة الحقل
/// Used on list screens for field cards
class FieldCardHero extends StatelessWidget {
  final String fieldId;
  final Widget child;
  final bool enabled;

  const FieldCardHero({
    super.key,
    required this.fieldId,
    required this.child,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!enabled) return child;

    return Hero(
      tag: HeroTags.fieldCard(fieldId),
      flightShuttleBuilder: _fieldCardFlightShuttle,
      child: Material(
        type: MaterialType.transparency,
        child: child,
      ),
    );
  }

  Widget _fieldCardFlightShuttle(
    BuildContext flightContext,
    Animation<double> animation,
    HeroFlightDirection flightDirection,
    BuildContext fromHeroContext,
    BuildContext toHeroContext,
  ) {
    final curvedAnimation = CurvedAnimation(
      parent: animation,
      curve: Curves.easeInOutCubic,
    );

    return AnimatedBuilder(
      animation: curvedAnimation,
      builder: (context, child) {
        // Interpolate border radius during flight
        final borderRadius = BorderRadiusTween(
          begin: BorderRadius.circular(16),
          end: BorderRadius.circular(0),
        ).evaluate(curvedAnimation);

        // Interpolate elevation
        final elevation = Tween<double>(
          begin: 4,
          end: 0,
        ).evaluate(curvedAnimation);

        return Material(
          elevation: elevation,
          borderRadius: borderRadius,
          clipBehavior: Clip.antiAlias,
          child: toHeroContext.widget,
        );
      },
    );
  }
}

/// Field Detail Hero Wrapper - غلاف بطل تفاصيل الحقل
/// Used on detail screens for receiving the hero animation
class FieldDetailHero extends StatelessWidget {
  final String fieldId;
  final Widget child;
  final bool enabled;

  const FieldDetailHero({
    super.key,
    required this.fieldId,
    required this.child,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!enabled) return child;

    return Hero(
      tag: HeroTags.fieldCard(fieldId),
      child: Material(
        type: MaterialType.transparency,
        child: child,
      ),
    );
  }
}

// =============================================================================
// IMAGE ZOOM HERO - بطل تكبير الصورة
// =============================================================================

/// Image Zoom Hero - بطل تكبير الصورة
/// Creates a smooth zoom transition for images
class ImageZoomHero extends StatelessWidget {
  final String imageTag;
  final Widget child;
  final bool enabled;
  final BorderRadius? borderRadius;
  final BoxFit fit;

  const ImageZoomHero({
    super.key,
    required this.imageTag,
    required this.child,
    this.enabled = true,
    this.borderRadius,
    this.fit = BoxFit.cover,
  });

  @override
  Widget build(BuildContext context) {
    if (!enabled) return child;

    return Hero(
      tag: imageTag,
      flightShuttleBuilder: _imageFlightShuttle,
      child: ClipRRect(
        borderRadius: borderRadius ?? BorderRadius.zero,
        child: child,
      ),
    );
  }

  Widget _imageFlightShuttle(
    BuildContext flightContext,
    Animation<double> animation,
    HeroFlightDirection flightDirection,
    BuildContext fromHeroContext,
    BuildContext toHeroContext,
  ) {
    final isForward = flightDirection == HeroFlightDirection.push;

    return AnimatedBuilder(
      animation: animation,
      builder: (context, child) {
        final fromBorderRadius = borderRadius ?? BorderRadius.zero;
        const toBorderRadius = BorderRadius.zero;

        final borderRadiusTween = BorderRadiusTween(
          begin: isForward ? fromBorderRadius : toBorderRadius,
          end: isForward ? toBorderRadius : fromBorderRadius,
        );

        return ClipRRect(
          borderRadius: borderRadiusTween.evaluate(
            CurvedAnimation(parent: animation, curve: Curves.easeInOutCubic),
          )!,
          child: isForward ? toHeroContext.widget : fromHeroContext.widget,
        );
      },
    );
  }
}

/// Zoomable Image View - عرض صورة قابل للتكبير
/// Full screen image view with pinch to zoom
class ZoomableImageView extends StatefulWidget {
  final String imageTag;
  final ImageProvider imageProvider;
  final Color backgroundColor;
  final double minScale;
  final double maxScale;
  final VoidCallback? onTap;

  const ZoomableImageView({
    super.key,
    required this.imageTag,
    required this.imageProvider,
    this.backgroundColor = Colors.black,
    this.minScale = 1.0,
    this.maxScale = 4.0,
    this.onTap,
  });

  @override
  State<ZoomableImageView> createState() => _ZoomableImageViewState();
}

class _ZoomableImageViewState extends State<ZoomableImageView>
    with SingleTickerProviderStateMixin {
  late TransformationController _transformationController;
  late AnimationController _animationController;
  Animation<Matrix4>? _animation;

  @override
  void initState() {
    super.initState();
    _transformationController = TransformationController();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _transformationController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  void _onDoubleTap() {
    final Matrix4 endMatrix;
    final currentScale = _transformationController.value.getMaxScaleOnAxis();

    if (currentScale > 1.5) {
      endMatrix = Matrix4.identity();
    } else {
      endMatrix = Matrix4.identity()..scale(2.5, 2.5);
    }

    _animation = Matrix4Tween(
      begin: _transformationController.value,
      end: endMatrix,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOutCubic,
    ));

    _animationController.forward(from: 0);
    _animationController.addListener(() {
      if (_animation != null) {
        _transformationController.value = _animation!.value;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onDoubleTap: _onDoubleTap,
      onTap: widget.onTap ?? () => Navigator.of(context).pop(),
      child: ColoredBox(
        color: widget.backgroundColor,
        child: Center(
          child: Hero(
            tag: widget.imageTag,
            child: InteractiveViewer(
              transformationController: _transformationController,
              minScale: widget.minScale,
              maxScale: widget.maxScale,
              child: Image(
                image: widget.imageProvider,
                fit: BoxFit.contain,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// =============================================================================
// CUSTOM HERO CONTROLLERS - متحكمات بطل مخصصة
// =============================================================================

/// Hero Controller with Custom Animations
/// متحكم بطل مع تحريكات مخصصة
class SahoolHeroController extends HeroController {
  SahoolHeroController({
    HeroFlightShuttleBuilder? createRectTween,
  }) : super(
          createRectTween: (begin, end) {
            return MaterialRectArcTween(begin: begin, end: end);
          },
        );
}

/// Custom Rect Tween for smoother hero animations
/// منحنى مستطيل مخصص لتحريكات بطل أكثر سلاسة
class SahoolRectTween extends RectTween {
  final Curve curve;

  SahoolRectTween({
    super.begin,
    super.end,
    this.curve = Curves.easeInOutCubic,
  });

  @override
  Rect? lerp(double t) {
    final curvedT = curve.transform(t);
    return Rect.lerp(begin, end, curvedT);
  }
}

/// Hero Flight Shuttle Builders
/// بناة رحلة البطل
class HeroShuttleBuilders {
  /// Default fade and scale shuttle
  static Widget fadeScaleShuttle(
    BuildContext flightContext,
    Animation<double> animation,
    HeroFlightDirection flightDirection,
    BuildContext fromHeroContext,
    BuildContext toHeroContext,
  ) {
    final curvedAnimation = CurvedAnimation(
      parent: animation,
      curve: Curves.easeInOutCubic,
    );

    return FadeTransition(
      opacity: curvedAnimation,
      child: ScaleTransition(
        scale: Tween<double>(begin: 0.9, end: 1.0).animate(curvedAnimation),
        child: toHeroContext.widget,
      ),
    );
  }

  /// Card to full screen shuttle
  static Widget cardToFullScreenShuttle(
    BuildContext flightContext,
    Animation<double> animation,
    HeroFlightDirection flightDirection,
    BuildContext fromHeroContext,
    BuildContext toHeroContext,
  ) {
    final isForward = flightDirection == HeroFlightDirection.push;
    final curvedAnimation = CurvedAnimation(
      parent: animation,
      curve: Curves.easeInOutCubic,
    );

    return AnimatedBuilder(
      animation: curvedAnimation,
      builder: (context, child) {
        final borderRadius = BorderRadiusTween(
          begin: const BorderRadius.all(Radius.circular(16)),
          end: BorderRadius.zero,
        ).evaluate(curvedAnimation);

        final elevation = Tween<double>(
          begin: isForward ? 4 : 0,
          end: isForward ? 0 : 4,
        ).evaluate(curvedAnimation);

        return Material(
          elevation: elevation,
          borderRadius: borderRadius,
          clipBehavior: Clip.antiAlias,
          child: isForward ? toHeroContext.widget : fromHeroContext.widget,
        );
      },
    );
  }

  /// Circular reveal shuttle
  static Widget circularRevealShuttle(
    BuildContext flightContext,
    Animation<double> animation,
    HeroFlightDirection flightDirection,
    BuildContext fromHeroContext,
    BuildContext toHeroContext,
  ) {
    return AnimatedBuilder(
      animation: animation,
      builder: (context, child) {
        return ClipOval(
          clipper: _CircularRevealClipper(animation.value),
          child: toHeroContext.widget,
        );
      },
    );
  }
}

class _CircularRevealClipper extends CustomClipper<Rect> {
  final double fraction;

  _CircularRevealClipper(this.fraction);

  @override
  Rect getClip(Size size) {
    final radius = (size.width > size.height ? size.width : size.height) * fraction;
    final center = Offset(size.width / 2, size.height / 2);
    return Rect.fromCircle(center: center, radius: radius);
  }

  @override
  bool shouldReclip(_CircularRevealClipper oldClipper) {
    return oldClipper.fraction != fraction;
  }
}

// =============================================================================
// HERO AWARE WIDGETS - عناصر واعية للبطل
// =============================================================================

/// Hero Aware Card - بطاقة واعية للبطل
/// Card that automatically handles hero animations
class HeroAwareCard extends StatelessWidget {
  final String heroTag;
  final Widget child;
  final VoidCallback? onTap;
  final double elevation;
  final BorderRadius borderRadius;
  final Color? color;
  final EdgeInsets padding;
  final bool heroEnabled;

  const HeroAwareCard({
    super.key,
    required this.heroTag,
    required this.child,
    this.onTap,
    this.elevation = 4,
    this.borderRadius = const BorderRadius.all(Radius.circular(16)),
    this.color,
    this.padding = const EdgeInsets.all(16),
    this.heroEnabled = true,
  });

  @override
  Widget build(BuildContext context) {
    final card = Material(
      elevation: elevation,
      borderRadius: borderRadius,
      color: color ?? Theme.of(context).cardColor,
      child: InkWell(
        onTap: onTap,
        borderRadius: borderRadius,
        child: Padding(
          padding: padding,
          child: child,
        ),
      ),
    );

    if (!heroEnabled) return card;

    return Hero(
      tag: heroTag,
      flightShuttleBuilder: HeroShuttleBuilders.cardToFullScreenShuttle,
      child: card,
    );
  }
}

/// Hero Aware Image - صورة واعية للبطل
/// Image that automatically handles hero animations with zoom capability
class HeroAwareImage extends StatelessWidget {
  final String heroTag;
  final ImageProvider imageProvider;
  final double? width;
  final double? height;
  final BoxFit fit;
  final BorderRadius borderRadius;
  final VoidCallback? onTap;
  final Widget? placeholder;
  final Widget? errorWidget;
  final bool heroEnabled;

  const HeroAwareImage({
    super.key,
    required this.heroTag,
    required this.imageProvider,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
    this.borderRadius = const BorderRadius.all(Radius.circular(12)),
    this.onTap,
    this.placeholder,
    this.errorWidget,
    this.heroEnabled = true,
  });

  @override
  Widget build(BuildContext context) {
    final imageWidget = ClipRRect(
      borderRadius: borderRadius,
      child: Image(
        image: imageProvider,
        width: width,
        height: height,
        fit: fit,
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) return child;
          return placeholder ??
              Container(
                width: width,
                height: height,
                color: Colors.grey[200],
                child: const Center(
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              );
        },
        errorBuilder: (context, error, stackTrace) {
          return errorWidget ??
              Container(
                width: width,
                height: height,
                color: Colors.grey[200],
                child: Icon(
                  Icons.image_not_supported,
                  color: Colors.grey[400],
                  size: 32,
                ),
              );
        },
      ),
    );

    final tappableImage = onTap != null
        ? GestureDetector(
            onTap: onTap,
            child: imageWidget,
          )
        : imageWidget;

    if (!heroEnabled) return tappableImage;

    return Hero(
      tag: heroTag,
      flightShuttleBuilder: (
        flightContext,
        animation,
        flightDirection,
        fromHeroContext,
        toHeroContext,
      ) {
        return AnimatedBuilder(
          animation: animation,
          builder: (context, child) {
            final fromRadius = borderRadius;
            final toRadius = flightDirection == HeroFlightDirection.push
                ? BorderRadius.zero
                : borderRadius;

            final currentRadius = BorderRadiusTween(
              begin: fromRadius,
              end: toRadius,
            ).evaluate(CurvedAnimation(
              parent: animation,
              curve: Curves.easeInOutCubic,
            ));

            return ClipRRect(
              borderRadius: currentRadius!,
              child: flightDirection == HeroFlightDirection.push
                  ? toHeroContext.widget
                  : fromHeroContext.widget,
            );
          },
        );
      },
      child: tappableImage,
    );
  }
}

// =============================================================================
// HERO TRANSITIONS PAGE - صفحة انتقالات البطل
// =============================================================================

/// Hero Page Route with custom animations
class HeroPageRoute<T> extends PageRoute<T> {
  final WidgetBuilder builder;
  final Duration transitionDuration_;
  final Duration reverseTransitionDuration_;
  final Curve curve;

  HeroPageRoute({
    required this.builder,
    super.settings,
    this.transitionDuration_ = const Duration(milliseconds: 500),
    this.reverseTransitionDuration_ = const Duration(milliseconds: 350),
    this.curve = Curves.easeInOutCubic,
  });

  @override
  Color? get barrierColor => null;

  @override
  String? get barrierLabel => null;

  @override
  bool get maintainState => true;

  @override
  Duration get transitionDuration => transitionDuration_;

  @override
  Duration get reverseTransitionDuration => reverseTransitionDuration_;

  @override
  Widget buildPage(
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
  ) {
    return builder(context);
  }

  @override
  Widget buildTransitions(
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    final curvedAnimation = CurvedAnimation(
      parent: animation,
      curve: curve,
      reverseCurve: curve.flipped,
    );

    return FadeTransition(
      opacity: Tween<double>(begin: 0.0, end: 1.0).animate(
        CurvedAnimation(
          parent: curvedAnimation,
          curve: const Interval(0.0, 0.5),
        ),
      ),
      child: child,
    );
  }
}

// =============================================================================
// CROSS-FADE HERO ANIMATION - تحريك بطل التلاشي المتقاطع
// =============================================================================

/// Cross Fade Hero - بطل التلاشي المتقاطع
/// Hero animation that cross-fades between source and destination
class CrossFadeHero extends StatelessWidget {
  final String heroTag;
  final Widget child;
  final bool enabled;

  const CrossFadeHero({
    super.key,
    required this.heroTag,
    required this.child,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!enabled) return child;

    return Hero(
      tag: heroTag,
      flightShuttleBuilder: _crossFadeFlightShuttle,
      child: child,
    );
  }

  Widget _crossFadeFlightShuttle(
    BuildContext flightContext,
    Animation<double> animation,
    HeroFlightDirection flightDirection,
    BuildContext fromHeroContext,
    BuildContext toHeroContext,
  ) {
    final isForward = flightDirection == HeroFlightDirection.push;
    final curvedAnimation = CurvedAnimation(
      parent: animation,
      curve: Curves.easeInOutCubic,
    );

    return AnimatedBuilder(
      animation: curvedAnimation,
      builder: (context, child) {
        return Stack(
          children: [
            // From widget fading out
            Opacity(
              opacity: isForward ? 1 - curvedAnimation.value : curvedAnimation.value,
              child: fromHeroContext.widget,
            ),
            // To widget fading in
            Opacity(
              opacity: isForward ? curvedAnimation.value : 1 - curvedAnimation.value,
              child: toHeroContext.widget,
            ),
          ],
        );
      },
    );
  }
}

// =============================================================================
// HERO ANIMATION MIXIN - خليط تحريك البطل
// =============================================================================

/// Mixin for widgets that need hero animation support
/// خليط للعناصر التي تحتاج دعم تحريك البطل
mixin HeroAnimationMixin<T extends StatefulWidget> on State<T> {
  /// Generate unique hero tag
  String generateHeroTag(String prefix, String id) => '${prefix}_$id';

  /// Navigate with hero animation
  Future<void> navigateWithHero(
    BuildContext context,
    Widget destination, {
    Duration duration = const Duration(milliseconds: 500),
    Curve curve = Curves.easeInOutCubic,
  }) {
    return Navigator.of(context).push(
      HeroPageRoute(
        builder: (context) => destination,
        transitionDuration_: duration,
        curve: curve,
      ),
    );
  }

  /// Pop with hero animation
  void popWithHero(BuildContext context, [dynamic result]) {
    Navigator.of(context).pop(result);
  }
}
