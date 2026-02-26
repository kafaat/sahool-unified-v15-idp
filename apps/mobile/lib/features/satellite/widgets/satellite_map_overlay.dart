/// Satellite Map Overlay Widget - ودجت تراكب خريطة الأقمار الصناعية
/// Map overlay showing NDVI visualization on field polygon
library;

import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

class SatelliteMapOverlay extends StatefulWidget {
  final String? imageUrl;
  final double ndviValue;
  final VoidCallback? onRefresh;
  final DateTime? captureDate;
  final ValueChanged<double>? onOpacityChanged;
  final VoidCallback? onTap;

  const SatelliteMapOverlay({
    super.key,
    this.imageUrl,
    required this.ndviValue,
    this.onRefresh,
    this.captureDate,
    this.onOpacityChanged,
    this.onTap,
  });

  @override
  State<SatelliteMapOverlay> createState() => _SatelliteMapOverlayState();
}

class _SatelliteMapOverlayState extends State<SatelliteMapOverlay>
    with SingleTickerProviderStateMixin {
  double _opacity = 0.85;
  bool _showControls = false;
  late final AnimationController _pulseController;
  late final Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.15).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
    // Pulse the NDVI badge briefly to draw attention
    _pulseController.forward().then((_) => _pulseController.reverse());
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return GestureDetector(
      onTap: () {
        setState(() => _showControls = !_showControls);
        widget.onTap?.call();
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        height: _showControls ? 260 : 200,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Stack(
          children: [
            // Satellite image with opacity control
            if (widget.imageUrl != null && widget.imageUrl!.isNotEmpty)
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: AnimatedOpacity(
                  opacity: _opacity,
                  duration: const Duration(milliseconds: 200),
                  child: CachedNetworkImage(
                    imageUrl: widget.imageUrl!,
                    fit: BoxFit.cover,
                    width: double.infinity,
                    height: double.infinity,
                    progressIndicatorBuilder: (context, url, downloadProgress) {
                      return Center(
                        child: CircularProgressIndicator(
                          value: downloadProgress.progress,
                          valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF367C2B)),
                        ),
                      );
                    },
                    errorWidget: (context, _, __) => _buildPlaceholder(isArabic),
                  ),
                ),
              )
            else
              _buildPlaceholder(isArabic),

            // NDVI badge with pulse animation
            Positioned(
              top: 12,
              right: 12,
              child: ScaleTransition(
                scale: _pulseAnimation,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: _getNdviColor(widget.ndviValue),
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: _getNdviColor(widget.ndviValue).withOpacity(0.4),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      const Text(
                        'NDVI',
                        style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        widget.ndviValue.toStringAsFixed(2),
                        style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        _getHealthLabel(widget.ndviValue, isArabic),
                        style: const TextStyle(color: Colors.white70, fontSize: 10),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // Capture date badge
            if (widget.captureDate != null)
              Positioned(
                top: 12,
                left: 60,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.black54,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.calendar_today, size: 12, color: Colors.white70),
                      const SizedBox(width: 4),
                      Text(
                        '${widget.captureDate!.day}/${widget.captureDate!.month}/${widget.captureDate!.year}',
                        style: const TextStyle(color: Colors.white, fontSize: 11),
                      ),
                    ],
                  ),
                ),
              ),

            // Refresh button
            if (widget.onRefresh != null)
              Positioned(
                top: 12,
                left: 12,
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.2),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: IconButton(
                    icon: const Icon(Icons.refresh, color: Color(0xFF367C2B)),
                    onPressed: widget.onRefresh,
                    iconSize: 20,
                    tooltip: isArabic ? 'تحديث' : 'Refresh',
                  ),
                ),
              ),

            // Gradient legend (replaces discrete dots)
            Positioned(
              bottom: _showControls ? 60 : 12,
              left: 12,
              right: 12,
              child: AnimatedSlide(
                duration: const Duration(milliseconds: 200),
                offset: Offset.zero,
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.75),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: [
                      // Gradient bar
                      Container(
                        height: 12,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(6),
                          gradient: const LinearGradient(
                            colors: [
                              Color(0xFFF44336), // Critical
                              Color(0xFFFF9800), // Poor
                              Color(0xFFFFC107), // Fair
                              Color(0xFF8BC34A), // Good
                              Color(0xFF4CAF50), // Excellent
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      // Labels
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(isArabic ? 'حرج' : 'Critical', style: const TextStyle(color: Colors.white70, fontSize: 9)),
                          Text(isArabic ? 'ضعيف' : 'Poor', style: const TextStyle(color: Colors.white70, fontSize: 9)),
                          Text(isArabic ? 'متوسط' : 'Fair', style: const TextStyle(color: Colors.white70, fontSize: 9)),
                          Text(isArabic ? 'جيد' : 'Good', style: const TextStyle(color: Colors.white70, fontSize: 9)),
                          Text(isArabic ? 'ممتاز' : 'Excellent', style: const TextStyle(color: Colors.white70, fontSize: 9)),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // Opacity slider (shown on tap)
            if (_showControls)
              Positioned(
                bottom: 12,
                left: 12,
                right: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.75),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.opacity, size: 16, color: Colors.white70),
                      Expanded(
                        child: Slider(
                          value: _opacity,
                          min: 0.1,
                          max: 1.0,
                          activeColor: const Color(0xFF4CAF50),
                          inactiveColor: Colors.white24,
                          onChanged: (value) {
                            setState(() => _opacity = value);
                            widget.onOpacityChanged?.call(value);
                          },
                        ),
                      ),
                      Text(
                        '${(_opacity * 100).toInt()}%',
                        style: const TextStyle(color: Colors.white, fontSize: 11),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  String _getHealthLabel(double ndvi, bool isArabic) {
    if (ndvi >= 0.8) return isArabic ? 'ممتاز' : 'Excellent';
    if (ndvi >= 0.6) return isArabic ? 'جيد' : 'Good';
    if (ndvi >= 0.4) return isArabic ? 'متوسط' : 'Fair';
    if (ndvi >= 0.2) return isArabic ? 'ضعيف' : 'Poor';
    return isArabic ? 'حرج' : 'Critical';
  }

  Widget _buildPlaceholder(bool isArabic) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.satellite_alt,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 12),
          Text(
            isArabic ? 'لا توجد صورة قمر صناعي' : 'No satellite image',
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Color _getNdviColor(double ndvi) {
    if (ndvi >= 0.8) return const Color(0xFF4CAF50); // Excellent - Dark Green
    if (ndvi >= 0.6) return const Color(0xFF8BC34A); // Good - Light Green
    if (ndvi >= 0.4) return const Color(0xFFFFC107); // Fair - Yellow
    if (ndvi >= 0.2) return const Color(0xFFFF9800); // Poor - Orange
    return const Color(0xFFF44336); // Critical - Red
  }
}
