import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../performance/image_cache_manager.dart';

/// SAHOOL Cached Image Widget
/// مكون الصور المخزنة مؤقتاً
///
/// Features:
/// - Caching with CachedNetworkImage
/// - Memory optimization with memCacheWidth/Height
/// - Placeholder and error handling
/// - Fade-in animation
/// - Retry on error

/// SahoolCachedImage - صورة محسّنة مع كاش
///
/// A performance-optimized cached network image widget
class SahoolCachedImage extends StatelessWidget {
  final String imageUrl;
  final double? width;
  final double? height;
  final BoxFit fit;
  final Widget? placeholder;
  final Widget? errorWidget;
  final int? memCacheWidth;
  final int? memCacheHeight;
  final Duration fadeInDuration;
  final Duration fadeOutDuration;
  final Curve fadeInCurve;
  final Curve fadeOutCurve;
  final Map<String, String>? httpHeaders;
  final bool useOldImageOnUrlChange;
  final Color? color;
  final BlendMode? colorBlendMode;
  final FilterQuality filterQuality;
  final Alignment alignment;
  final ImageRepeat repeat;

  const SahoolCachedImage({
    super.key,
    required this.imageUrl,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
    this.placeholder,
    this.errorWidget,
    this.memCacheWidth,
    this.memCacheHeight,
    this.fadeInDuration = const Duration(milliseconds: 300),
    this.fadeOutDuration = const Duration(milliseconds: 200),
    this.fadeInCurve = Curves.easeIn,
    this.fadeOutCurve = Curves.easeOut,
    this.httpHeaders,
    this.useOldImageOnUrlChange = false,
    this.color,
    this.colorBlendMode,
    this.filterQuality = FilterQuality.low,
    this.alignment = Alignment.center,
    this.repeat = ImageRepeat.noRepeat,
  });

  /// Calculate optimal memory cache dimensions based on widget size
  int? get _optimalMemCacheWidth {
    if (memCacheWidth != null) return memCacheWidth;
    if (width != null) {
      // Cache at 2x widget size for better quality on high-DPI screens
      return (width! * 2).toInt();
    }
    return null;
  }

  int? get _optimalMemCacheHeight {
    if (memCacheHeight != null) return memCacheHeight;
    if (height != null) {
      // Cache at 2x widget size for better quality on high-DPI screens
      return (height! * 2).toInt();
    }
    return null;
  }

  Widget _buildPlaceholder(BuildContext context, String url) {
    return placeholder ??
        Container(
          width: width,
          height: height,
          color: Colors.grey[200],
          child: const Center(
            child: CircularProgressIndicator(
              strokeWidth: 2,
            ),
          ),
        );
  }

  Widget _buildError(BuildContext context, String url, dynamic error) {
    return errorWidget ??
        Container(
          width: width,
          height: height,
          color: Colors.grey[300],
          child: const Icon(
            Icons.broken_image_outlined,
            color: Colors.grey,
            size: 48,
          ),
        );
  }

  @override
  Widget build(BuildContext context) {
    // Handle empty or invalid URLs
    if (imageUrl.isEmpty) {
      return _buildError(context, imageUrl, 'Empty URL');
    }

    return CachedNetworkImage(
      imageUrl: imageUrl,
      cacheManager: SahoolImageCacheManager.instance,
      width: width,
      height: height,
      fit: fit,
      placeholder: _buildPlaceholder,
      errorWidget: _buildError,
      memCacheWidth: _optimalMemCacheWidth,
      memCacheHeight: _optimalMemCacheHeight,
      fadeInDuration: fadeInDuration,
      fadeOutDuration: fadeOutDuration,
      fadeInCurve: fadeInCurve,
      fadeOutCurve: fadeOutCurve,
      httpHeaders: httpHeaders,
      useOldImageOnUrlChange: useOldImageOnUrlChange,
      color: color,
      colorBlendMode: colorBlendMode,
      filterQuality: filterQuality,
      alignment: alignment,
      repeat: repeat,
    );
  }
}

/// SahoolCachedAvatar - صورة شخصية دائرية مع كاش
///
/// Circular avatar with cached network image
class SahoolCachedAvatar extends StatelessWidget {
  final String imageUrl;
  final double radius;
  final Widget? placeholder;
  final Widget? errorWidget;
  final Color? backgroundColor;
  final Widget? fallbackChild;

  const SahoolCachedAvatar({
    super.key,
    required this.imageUrl,
    this.radius = 20,
    this.placeholder,
    this.errorWidget,
    this.backgroundColor,
    this.fallbackChild,
  });

  @override
  Widget build(BuildContext context) {
    if (imageUrl.isEmpty) {
      return CircleAvatar(
        radius: radius,
        backgroundColor: backgroundColor ?? Colors.grey[300],
        child: fallbackChild ??
            Icon(
              Icons.person,
              size: radius,
              color: Colors.grey[600],
            ),
      );
    }

    return CircleAvatar(
      radius: radius,
      backgroundColor: backgroundColor ?? Colors.grey[200],
      child: ClipOval(
        child: SahoolCachedImage(
          imageUrl: imageUrl,
          width: radius * 2,
          height: radius * 2,
          fit: BoxFit.cover,
          placeholder: placeholder,
          errorWidget: errorWidget ??
              (context, url, error) => Icon(
                    Icons.person,
                    size: radius,
                    color: Colors.grey[600],
                  ),
          memCacheWidth: (radius * 4).toInt(), // 2x for retina
          memCacheHeight: (radius * 4).toInt(),
        ),
      ),
    );
  }
}

/// SahoolCachedThumbnail - صورة مصغرة محسّنة
///
/// Optimized thumbnail image with aggressive memory caching
class SahoolCachedThumbnail extends StatelessWidget {
  final String imageUrl;
  final double size;
  final BoxFit fit;
  final Widget? placeholder;
  final Widget? errorWidget;
  final BorderRadius? borderRadius;

  const SahoolCachedThumbnail({
    super.key,
    required this.imageUrl,
    this.size = 80,
    this.fit = BoxFit.cover,
    this.placeholder,
    this.errorWidget,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    Widget image = SahoolCachedImage(
      imageUrl: imageUrl,
      width: size,
      height: size,
      fit: fit,
      placeholder: placeholder,
      errorWidget: errorWidget,
      // Aggressive memory optimization for thumbnails
      memCacheWidth: (size * 1.5).toInt(),
      memCacheHeight: (size * 1.5).toInt(),
      filterQuality: FilterQuality.low,
    );

    if (borderRadius != null) {
      image = ClipRRect(
        borderRadius: borderRadius!,
        child: image,
      );
    }

    return SizedBox(
      width: size,
      height: size,
      child: image,
    );
  }
}

/// SahoolCachedHeroImage - صورة بطل مع كاش للتحولات
///
/// Hero image with caching for smooth transitions
class SahoolCachedHeroImage extends StatelessWidget {
  final String imageUrl;
  final String heroTag;
  final double? width;
  final double? height;
  final BoxFit fit;
  final Widget? placeholder;
  final Widget? errorWidget;

  const SahoolCachedHeroImage({
    super.key,
    required this.imageUrl,
    required this.heroTag,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
    this.placeholder,
    this.errorWidget,
  });

  @override
  Widget build(BuildContext context) {
    return Hero(
      tag: heroTag,
      child: SahoolCachedImage(
        imageUrl: imageUrl,
        width: width,
        height: height,
        fit: fit,
        placeholder: placeholder,
        errorWidget: errorWidget,
        useOldImageOnUrlChange: true,
      ),
    );
  }
}

/// SahoolImageGallery - معرض صور محسّن
///
/// Optimized image gallery with PageView
class SahoolImageGallery extends StatefulWidget {
  final List<String> imageUrls;
  final int initialPage;
  final void Function(int index)? onPageChanged;
  final Widget? placeholder;
  final Widget? errorWidget;
  final bool showIndicator;

  const SahoolImageGallery({
    super.key,
    required this.imageUrls,
    this.initialPage = 0,
    this.onPageChanged,
    this.placeholder,
    this.errorWidget,
    this.showIndicator = true,
  });

  @override
  State<SahoolImageGallery> createState() => _SahoolImageGalleryState();
}

class _SahoolImageGalleryState extends State<SahoolImageGallery> {
  late PageController _pageController;
  late int _currentPage;

  @override
  void initState() {
    super.initState();
    _currentPage = widget.initialPage;
    _pageController = PageController(initialPage: widget.initialPage);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _onPageChanged(int index) {
    setState(() {
      _currentPage = index;
    });
    widget.onPageChanged?.call(index);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.imageUrls.isEmpty) {
      return const Center(
        child: Text('No images'),
      );
    }

    return Stack(
      children: [
        // PageView with images
        PageView.builder(
          controller: _pageController,
          onPageChanged: _onPageChanged,
          itemCount: widget.imageUrls.length,
          itemBuilder: (context, index) {
            return SahoolCachedImage(
              imageUrl: widget.imageUrls[index],
              fit: BoxFit.contain,
              placeholder: widget.placeholder,
              errorWidget: widget.errorWidget,
            );
          },
        ),

        // Page indicator
        if (widget.showIndicator && widget.imageUrls.length > 1)
          Positioned(
            bottom: 16,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  '${_currentPage + 1} / ${widget.imageUrls.length}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

/// SahoolNetworkImageBuilder - باني صور مخصص
///
/// Custom network image builder with more control
class SahoolNetworkImageBuilder extends StatelessWidget {
  final String imageUrl;
  final Widget Function(BuildContext context, ImageProvider imageProvider)
      imageBuilder;
  final Widget Function(BuildContext context, String url)? placeholder;
  final Widget Function(BuildContext context, String url, dynamic error)?
      errorWidget;
  final int? memCacheWidth;
  final int? memCacheHeight;

  const SahoolNetworkImageBuilder({
    super.key,
    required this.imageUrl,
    required this.imageBuilder,
    this.placeholder,
    this.errorWidget,
    this.memCacheWidth,
    this.memCacheHeight,
  });

  @override
  Widget build(BuildContext context) {
    return CachedNetworkImage(
      imageUrl: imageUrl,
      cacheManager: SahoolImageCacheManager.instance,
      imageBuilder: imageBuilder,
      placeholder: placeholder,
      errorWidget: errorWidget,
      memCacheWidth: memCacheWidth,
      memCacheHeight: memCacheHeight,
    );
  }
}
