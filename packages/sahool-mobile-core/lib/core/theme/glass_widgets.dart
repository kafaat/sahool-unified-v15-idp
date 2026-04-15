import 'dart:ui';
import 'package:flutter/material.dart';
import 'glassmorphism.dart';
import 'glass_colors.dart';
import 'theme_animations.dart';

/// SAHOOL Glass Widgets - Example Components
/// ودجات زجاجية لسهول - مكونات نموذجية
///
/// Premium glassmorphism widgets for:
/// - Weather display | عرض الطقس
/// - Field cards | بطاقات الحقول
/// - Statistics panels | لوحات الإحصائيات

// ═══════════════════════════════════════════════════════════════════════════
// Glass Weather Card - بطاقة الطقس الزجاجية
// ═══════════════════════════════════════════════════════════════════════════

/// Premium glass weather card with animated effects
/// بطاقة طقس زجاجية متميزة مع تأثيرات متحركة
class GlassWeatherCard extends StatelessWidget {
  final double temperature;
  final String condition;
  final String? conditionAr;
  final IconData weatherIcon;
  final String location;
  final String? locationAr;
  final double? humidity;
  final double? windSpeed;
  final String? uvIndex;
  final VoidCallback? onTap;
  final bool showAnimation;
  final double blurIntensity;
  final Gradient? backgroundGradient;

  const GlassWeatherCard({
    super.key,
    required this.temperature,
    required this.condition,
    this.conditionAr,
    required this.weatherIcon,
    required this.location,
    this.locationAr,
    this.humidity,
    this.windSpeed,
    this.uvIndex,
    this.onTap,
    this.showAnimation = true,
    this.blurIntensity = 15.0,
    this.backgroundGradient,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayCondition = isRtl ? (conditionAr ?? condition) : condition;
    final displayLocation = isRtl ? (locationAr ?? location) : location;
    final theme = Theme.of(context);

    Widget content = GestureDetector(
      onTap: onTap,
      child: GlassContainer(
        blurIntensity: blurIntensity,
        opacity: isDark ? 0.15 : 0.2,
        borderRadius: 24,
        padding: const EdgeInsets.all(20),
        gradient: backgroundGradient,
        borderGradient: showAnimation ? GlassGradients.borderSahool : null,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Location Row
            Row(
              children: [
                Icon(
                  Icons.location_on_outlined,
                  size: 16,
                  color: isDark ? Colors.white70 : Colors.black54,
                ),
                const SizedBox(width: 4),
                Text(
                  displayLocation,
                  style: TextStyle(
                    fontSize: 14,
                    color: isDark ? Colors.white70 : Colors.black54,
                  ),
                ),
                const Spacer(),
                _buildSyncIndicator(context),
              ],
            ),
            const SizedBox(height: 20),

            // Main Temperature Display
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Temperature
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${temperature.round()}',
                            style: theme.textTheme.displayMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              height: 1,
                            ),
                          ),
                          Text(
                            '°C',
                            style: theme.textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.w300,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        displayCondition,
                        style: theme.textTheme.titleMedium?.copyWith(
                          color: isDark ? Colors.white70 : Colors.black54,
                        ),
                      ),
                    ],
                  ),
                ),

                // Weather Icon
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _getWeatherColor(condition).withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(
                    weatherIcon,
                    size: 48,
                    color: _getWeatherColor(condition),
                  ),
                ),
              ],
            ),

            // Details Row
            if (humidity != null || windSpeed != null || uvIndex != null) ...[
              const SizedBox(height: 20),
              Container(
                height: 1,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Colors.transparent,
                      (isDark ? Colors.white : Colors.black).withValues(alpha: 0.1),
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  if (humidity != null)
                    _WeatherDetail(
                      icon: Icons.water_drop_outlined,
                      value: '${humidity!.round()}%',
                      label: isRtl ? 'الرطوبة' : 'Humidity',
                    ),
                  if (windSpeed != null)
                    _WeatherDetail(
                      icon: Icons.air,
                      value: '${windSpeed!.round()} km/h',
                      label: isRtl ? 'الرياح' : 'Wind',
                    ),
                  if (uvIndex != null)
                    _WeatherDetail(
                      icon: Icons.wb_sunny_outlined,
                      value: uvIndex!,
                      label: isRtl ? 'الأشعة' : 'UV',
                    ),
                ],
              ),
            ],
          ],
        ),
      ),
    );

    // Add shimmer animation if enabled
    if (showAnimation) {
      content = GlassShimmer(
        duration: const Duration(seconds: 3),
        intensity: 0.15,
        enabled: showAnimation,
        child: content,
      );
    }

    return content;
  }

  Widget _buildSyncIndicator(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.green.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: const BoxDecoration(
              color: Colors.green,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            'Live',
            style: TextStyle(
              fontSize: 10,
              color: isDark ? Colors.white70 : Colors.black54,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Color _getWeatherColor(String condition) {
    final lower = condition.toLowerCase();
    if (lower.contains('sun') || lower.contains('clear')) {
      return const Color(0xFFFFB300);
    } else if (lower.contains('cloud')) {
      return const Color(0xFF78909C);
    } else if (lower.contains('rain')) {
      return const Color(0xFF42A5F5);
    } else if (lower.contains('snow')) {
      return const Color(0xFF90CAF9);
    } else if (lower.contains('storm') || lower.contains('thunder')) {
      return const Color(0xFF7E57C2);
    }
    return const Color(0xFF4CAF50);
  }
}

class _WeatherDetail extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;

  const _WeatherDetail({
    required this.icon,
    required this.value,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Column(
      children: [
        Icon(
          icon,
          size: 20,
          color: isDark ? Colors.white54 : Colors.black45,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: isDark ? Colors.white : Colors.black87,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: isDark ? Colors.white54 : Colors.black45,
          ),
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Field Card - بطاقة الحقل الزجاجية
// ═══════════════════════════════════════════════════════════════════════════

/// Premium glass field card with NDVI indicator
/// بطاقة حقل زجاجية متميزة مع مؤشر NDVI
class GlassFieldCard extends StatelessWidget {
  final String fieldName;
  final String? fieldNameAr;
  final double area;
  final String areaUnit;
  final String cropType;
  final String? cropTypeAr;
  final double? ndviValue;
  final String status;
  final String? statusAr;
  final Color? statusColor;
  final String? lastUpdated;
  final VoidCallback? onTap;
  final Widget? thumbnail;
  final bool showHealthIndicator;
  final double blurIntensity;

  const GlassFieldCard({
    super.key,
    required this.fieldName,
    this.fieldNameAr,
    required this.area,
    this.areaUnit = 'ha',
    required this.cropType,
    this.cropTypeAr,
    this.ndviValue,
    required this.status,
    this.statusAr,
    this.statusColor,
    this.lastUpdated,
    this.onTap,
    this.thumbnail,
    this.showHealthIndicator = true,
    this.blurIntensity = 10.0,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final theme = Theme.of(context);

    final displayName = isRtl ? (fieldNameAr ?? fieldName) : fieldName;
    final displayCrop = isRtl ? (cropTypeAr ?? cropType) : cropType;
    final displayStatus = isRtl ? (statusAr ?? status) : status;

    final healthColor = _getHealthColor(ndviValue);
    final effectiveStatusColor = statusColor ?? healthColor;

    return GestureDetector(
      onTap: onTap,
      child: GlassContainer(
        blurIntensity: blurIntensity,
        opacity: isDark ? 0.12 : 0.15,
        borderRadius: 20,
        padding: EdgeInsets.zero,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Thumbnail / Map Preview
            if (thumbnail != null)
              ClipRRect(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                child: SizedBox(
                  height: 120,
                  width: double.infinity,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      thumbnail!,
                      // Gradient overlay
                      Positioned.fill(
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              begin: Alignment.topCenter,
                              end: Alignment.bottomCenter,
                              colors: [
                                Colors.transparent,
                                Colors.black.withValues(alpha: 0.3),
                              ],
                            ),
                          ),
                        ),
                      ),
                      // NDVI badge
                      if (ndviValue != null && showHealthIndicator)
                        Positioned(
                          top: 12,
                          right: isRtl ? null : 12,
                          left: isRtl ? 12 : null,
                          child: _buildNdviBadge(context, ndviValue!),
                        ),
                    ],
                  ),
                ),
              ),

            // Content
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Field Name & Status
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          displayName,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      _buildStatusChip(context, displayStatus, effectiveStatusColor),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Details Row
                  Row(
                    children: [
                      // Area
                      _FieldDetail(
                        icon: Icons.square_foot,
                        value: '${area.toStringAsFixed(1)} $areaUnit',
                        iconColor: isDark ? Colors.white54 : Colors.black45,
                      ),
                      const SizedBox(width: 16),
                      // Crop
                      _FieldDetail(
                        icon: Icons.grass,
                        value: displayCrop,
                        iconColor: const Color(0xFF4CAF50),
                      ),
                    ],
                  ),

                  // Health Indicator Bar
                  if (ndviValue != null && showHealthIndicator && thumbnail == null) ...[
                    const SizedBox(height: 16),
                    _buildHealthBar(context, ndviValue!),
                  ],

                  // Last Updated
                  if (lastUpdated != null) ...[
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Icon(
                          Icons.access_time,
                          size: 12,
                          color: isDark ? Colors.white38 : Colors.black38,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          lastUpdated!,
                          style: TextStyle(
                            fontSize: 11,
                            color: isDark ? Colors.white38 : Colors.black38,
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNdviBadge(BuildContext context, double ndvi) {
    final healthColor = _getHealthColor(ndvi);
    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.black.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: healthColor.withValues(alpha: 0.5)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: healthColor,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                'NDVI ${ndvi.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(BuildContext context, String status, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Text(
        status,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: color,
        ),
      ),
    );
  }

  Widget _buildHealthBar(BuildContext context, double ndvi) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final healthColor = _getHealthColor(ndvi);
    final percentage = (ndvi.clamp(0, 1) * 100).round();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Health',
              style: TextStyle(
                fontSize: 11,
                color: isDark ? Colors.white54 : Colors.black45,
              ),
            ),
            Text(
              '$percentage%',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: healthColor,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        GlassProgressIndicator(
          value: ndvi,
          height: 6,
          borderRadius: 3,
          valueColor: healthColor,
          blurIntensity: 5,
          opacity: 0.1,
        ),
      ],
    );
  }

  Color _getHealthColor(double? ndvi) {
    if (ndvi == null) return Colors.grey;
    if (ndvi >= 0.7) return const Color(0xFF2E7D32);
    if (ndvi >= 0.5) return const Color(0xFF4CAF50);
    if (ndvi >= 0.3) return const Color(0xFFFF9800);
    return const Color(0xFFF44336);
  }
}

class _FieldDetail extends StatelessWidget {
  final IconData icon;
  final String value;
  final Color iconColor;

  const _FieldDetail({
    required this.icon,
    required this.value,
    required this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: iconColor),
        const SizedBox(width: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 13,
            color: isDark ? Colors.white70 : Colors.black54,
          ),
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Stats Panel - لوحة الإحصائيات الزجاجية
// ═══════════════════════════════════════════════════════════════════════════

/// Premium glass statistics panel
/// لوحة إحصائيات زجاجية متميزة
class GlassStatsPanel extends StatelessWidget {
  final List<GlassStatItem> stats;
  final String? title;
  final String? titleAr;
  final int crossAxisCount;
  final double spacing;
  final double blurIntensity;
  final bool showAnimations;
  final VoidCallback? onViewAll;

  const GlassStatsPanel({
    super.key,
    required this.stats,
    this.title,
    this.titleAr,
    this.crossAxisCount = 2,
    this.spacing = 12,
    this.blurIntensity = 10.0,
    this.showAnimations = true,
    this.onViewAll,
  });

  @override
  Widget build(BuildContext context) {
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayTitle = isRtl ? (titleAr ?? title) : title;
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        if (displayTitle != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  displayTitle,
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (onViewAll != null)
                  GlassButton(
                    onPressed: onViewAll,
                    style: GlassButtonStyle.text,
                    opacity: 0,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          isRtl ? 'عرض الكل' : 'View All',
                          style: TextStyle(
                            color: theme.colorScheme.primary,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Icon(
                          isRtl ? Icons.arrow_back_ios : Icons.arrow_forward_ios,
                          size: 14,
                          color: theme.colorScheme.primary,
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),

        // Stats Grid
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: crossAxisCount,
            crossAxisSpacing: spacing,
            mainAxisSpacing: spacing,
            childAspectRatio: 1.3,
          ),
          itemCount: stats.length,
          itemBuilder: (context, index) {
            final stat = stats[index];
            Widget statWidget = _GlassStatCard(
              stat: stat,
              blurIntensity: blurIntensity,
            );

            if (showAnimations && stat.showTrend) {
              statWidget = PulsingGlow(
                glowColor: stat.trendPositive ? Colors.green : Colors.red,
                enabled: stat.showTrend,
                minOpacity: 0.1,
                maxOpacity: 0.3,
                blurRadius: 15,
                child: statWidget,
              );
            }

            return statWidget;
          },
        ),
      ],
    );
  }
}

/// Individual stat item data
class GlassStatItem {
  final String label;
  final String? labelAr;
  final String value;
  final String? unit;
  final IconData icon;
  final Color? iconColor;
  final Color? valueColor;
  final String? trend;
  final bool trendPositive;
  final bool showTrend;
  final VoidCallback? onTap;

  const GlassStatItem({
    required this.label,
    this.labelAr,
    required this.value,
    this.unit,
    required this.icon,
    this.iconColor,
    this.valueColor,
    this.trend,
    this.trendPositive = true,
    this.showTrend = false,
    this.onTap,
  });
}

class _GlassStatCard extends StatelessWidget {
  final GlassStatItem stat;
  final double blurIntensity;

  const _GlassStatCard({
    required this.stat,
    required this.blurIntensity,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayLabel = isRtl ? (stat.labelAr ?? stat.label) : stat.label;
    final theme = Theme.of(context);

    final iconColor = stat.iconColor ?? theme.colorScheme.primary;
    final valueColor = stat.valueColor ?? (isDark ? Colors.white : Colors.black87);

    return GestureDetector(
      onTap: stat.onTap,
      child: GlassContainer(
        blurIntensity: blurIntensity,
        opacity: isDark ? 0.12 : 0.15,
        borderRadius: 16,
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Header Row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: iconColor.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(stat.icon, size: 20, color: iconColor),
                ),
                if (stat.trend != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: (stat.trendPositive ? Colors.green : Colors.red)
                          .withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          stat.trendPositive
                              ? Icons.arrow_upward
                              : Icons.arrow_downward,
                          size: 10,
                          color: stat.trendPositive ? Colors.green : Colors.red,
                        ),
                        const SizedBox(width: 2),
                        Text(
                          stat.trend!,
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: stat.trendPositive ? Colors.green : Colors.red,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),

            // Value
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Flexible(
                      child: Text(
                        stat.value,
                        style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: valueColor,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    if (stat.unit != null) ...[
                      const SizedBox(width: 4),
                      Text(
                        stat.unit!,
                        style: TextStyle(
                          fontSize: 12,
                          color: isDark ? Colors.white54 : Colors.black45,
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  displayLabel,
                  style: TextStyle(
                    fontSize: 12,
                    color: isDark ? Colors.white54 : Colors.black45,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Alert Card - بطاقة التنبيه الزجاجية
// ═══════════════════════════════════════════════════════════════════════════

/// Glass alert card for notifications and warnings
/// بطاقة تنبيه زجاجية للإشعارات والتحذيرات
class GlassAlertCard extends StatelessWidget {
  final String message;
  final String? messageAr;
  final GlassAlertType type;
  final IconData? icon;
  final String? actionLabel;
  final String? actionLabelAr;
  final VoidCallback? onAction;
  final VoidCallback? onDismiss;
  final bool showIcon;
  final double blurIntensity;

  const GlassAlertCard({
    super.key,
    required this.message,
    this.messageAr,
    this.type = GlassAlertType.info,
    this.icon,
    this.actionLabel,
    this.actionLabelAr,
    this.onAction,
    this.onDismiss,
    this.showIcon = true,
    this.blurIntensity = 10.0,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayMessage = isRtl ? (messageAr ?? message) : message;
    final displayAction = isRtl ? (actionLabelAr ?? actionLabel) : actionLabel;

    final alertColor = _getAlertColor(type);
    final effectiveIcon = icon ?? _getAlertIcon(type);

    return GlassContainer(
      blurIntensity: blurIntensity,
      opacity: isDark ? 0.15 : 0.2,
      borderRadius: 16,
      padding: const EdgeInsets.all(16),
      borderColor: alertColor.withValues(alpha: 0.3),
      child: Row(
        children: [
          // Icon
          if (showIcon)
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: alertColor.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(effectiveIcon, size: 24, color: alertColor),
            ),
          if (showIcon) const SizedBox(width: 16),

          // Message
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  displayMessage,
                  style: TextStyle(
                    fontSize: 14,
                    color: isDark ? Colors.white : Colors.black87,
                  ),
                ),
                if (displayAction != null && onAction != null) ...[
                  const SizedBox(height: 8),
                  GestureDetector(
                    onTap: onAction,
                    child: Text(
                      displayAction,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: alertColor,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),

          // Dismiss button
          if (onDismiss != null)
            IconButton(
              onPressed: onDismiss,
              icon: Icon(
                Icons.close,
                size: 20,
                color: isDark ? Colors.white54 : Colors.black45,
              ),
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
            ),
        ],
      ),
    );
  }

  Color _getAlertColor(GlassAlertType type) {
    switch (type) {
      case GlassAlertType.success:
        return const Color(0xFF4CAF50);
      case GlassAlertType.warning:
        return const Color(0xFFFF9800);
      case GlassAlertType.error:
        return const Color(0xFFF44336);
      case GlassAlertType.info:
        return const Color(0xFF2196F3);
    }
  }

  IconData _getAlertIcon(GlassAlertType type) {
    switch (type) {
      case GlassAlertType.success:
        return Icons.check_circle_outline;
      case GlassAlertType.warning:
        return Icons.warning_amber_outlined;
      case GlassAlertType.error:
        return Icons.error_outline;
      case GlassAlertType.info:
        return Icons.info_outline;
    }
  }
}

enum GlassAlertType { success, warning, error, info }

// ═══════════════════════════════════════════════════════════════════════════
// Glass Quick Action Button - زر الإجراء السريع الزجاجي
// ═══════════════════════════════════════════════════════════════════════════

/// Glass quick action button for dashboard
/// زر إجراء سريع زجاجي للوحة التحكم
class GlassQuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final String? labelAr;
  final VoidCallback? onTap;
  final Color? color;
  final double blurIntensity;
  final bool showBadge;
  final int? badgeCount;

  const GlassQuickAction({
    super.key,
    required this.icon,
    required this.label,
    this.labelAr,
    this.onTap,
    this.color,
    this.blurIntensity = 10.0,
    this.showBadge = false,
    this.badgeCount,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayLabel = isRtl ? (labelAr ?? label) : label;
    final theme = Theme.of(context);

    final effectiveColor = color ?? theme.colorScheme.primary;

    return GestureDetector(
      onTap: onTap,
      child: GlassContainer(
        blurIntensity: blurIntensity,
        opacity: isDark ? 0.12 : 0.15,
        borderRadius: 16,
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Icon with badge
            Stack(
              clipBehavior: Clip.none,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: effectiveColor.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Icon(icon, size: 28, color: effectiveColor),
                ),
                if (showBadge && badgeCount != null && badgeCount! > 0)
                  Positioned(
                    right: -6,
                    top: -6,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: const BoxDecoration(
                        color: Colors.red,
                        shape: BoxShape.circle,
                      ),
                      constraints: const BoxConstraints(
                        minWidth: 18,
                        minHeight: 18,
                      ),
                      child: Center(
                        child: Text(
                          badgeCount! > 99 ? '99+' : '$badgeCount',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            // Label
            Text(
              displayLabel,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: isDark ? Colors.white70 : Colors.black54,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}
