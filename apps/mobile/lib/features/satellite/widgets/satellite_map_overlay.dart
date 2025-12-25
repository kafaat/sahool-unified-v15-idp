/// Satellite Map Overlay Widget - ودجت تراكب خريطة الأقمار الصناعية
/// Map overlay showing NDVI visualization on field polygon
library;

import 'package:flutter/material.dart';

class SatelliteMapOverlay extends StatelessWidget {
  final String? imageUrl;
  final double ndviValue;
  final VoidCallback? onRefresh;

  const SatelliteMapOverlay({
    super.key,
    this.imageUrl,
    required this.ndviValue,
    this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Container(
      height: 200,
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Stack(
        children: [
          // Satellite image or placeholder
          if (imageUrl != null && imageUrl!.isNotEmpty)
            ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.network(
                imageUrl!,
                fit: BoxFit.cover,
                width: double.infinity,
                height: double.infinity,
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  return Center(
                    child: CircularProgressIndicator(
                      value: loadingProgress.expectedTotalBytes != null
                          ? loadingProgress.cumulativeBytesLoaded /
                              loadingProgress.expectedTotalBytes!
                          : null,
                      valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF367C2B)),
                    ),
                  );
                },
                errorBuilder: (context, error, stackTrace) {
                  return _buildPlaceholder(isArabic);
                },
              ),
            )
          else
            _buildPlaceholder(isArabic),

          // NDVI value overlay
          Positioned(
            top: 12,
            right: 12,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: _getNdviColor(ndviValue),
                borderRadius: BorderRadius.circular(8),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.2),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    'NDVI',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    ndviValue.toStringAsFixed(2),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Refresh button
          if (onRefresh != null)
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
                  onPressed: onRefresh,
                  tooltip: isArabic ? 'تحديث' : 'Refresh',
                ),
              ),
            ),

          // Legend
          Positioned(
            bottom: 12,
            left: 12,
            right: 12,
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.7),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildLegendItem(
                    isArabic ? 'منخفض' : 'Low',
                    const Color(0xFFF44336),
                  ),
                  _buildLegendItem(
                    isArabic ? 'متوسط' : 'Medium',
                    const Color(0xFFFFC107),
                  ),
                  _buildLegendItem(
                    isArabic ? 'جيد' : 'Good',
                    const Color(0xFF8BC34A),
                  ),
                  _buildLegendItem(
                    isArabic ? 'ممتاز' : 'Excellent',
                    const Color(0xFF4CAF50),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
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

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 10,
          ),
        ),
      ],
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
