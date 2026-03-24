import 'package:flutter/material.dart';
import '../theme/sahool_theme.dart';
import 'sahool_skeleton.dart';

/// SAHOOL Domain-Specific Skeleton Widgets
/// مكونات الهيكل العظمي المتخصصة بمجالات التطبيق
///
/// Provides skeleton loaders that match actual UI card layouts:
/// يوفر هياكل تحميل تطابق تخطيط البطاقات الفعلية:
///
/// - [FieldCardSkeleton] - Field card layout / بطاقة الحقل
/// - [WeatherCardSkeleton] - Weather card layout / بطاقة الطقس
/// - [TaskCardSkeleton] - Task card layout / بطاقة المهمة
/// - [StatsRowSkeleton] - Horizontal stats row / صف الإحصائيات
/// - [DashboardSkeleton] - Full dashboard loading / لوحة التحكم
/// - [MapSkeleton] - Map placeholder / خريطة نائبة

// =============================================================================
// FieldCardSkeleton - Matches Field Card Layout
// هيكل بطاقة الحقل - يطابق تخطيط بطاقة الحقل الفعلية
// =============================================================================

/// Skeleton that matches the [EnhancedFieldCard] layout.
/// هيكل يطابق تخطيط بطاقة الحقل المحسنة.
class FieldCardSkeleton extends StatelessWidget {
  /// Show compact variant for grid views.
  /// عرض الشكل المضغوط لعرض الشبكة.
  final bool isCompact;

  const FieldCardSkeleton({
    super.key,
    this.isCompact = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? SahoolColors.surfaceDark : Colors.white;
    final borderColor = isDark ? Colors.grey[700]! : Colors.grey[200]!;

    return Container(
      height: isCompact ? 160 : 140,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // الصف العلوي: أيقونة + عنوان + مؤشر الصحة
          Row(
            children: [
              // أيقونة الحقل النائبة
              SahoolSkeleton(
                width: 48,
                height: 48,
                borderRadius: 12,
              ),
              const SizedBox(width: 12),
              // العنوان والعنوان الفرعي
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SahoolSkeleton(width: 120, height: 16, borderRadius: 4),
                    const SizedBox(height: 8),
                    SahoolSkeleton(width: 80, height: 12, borderRadius: 4),
                  ],
                ),
              ),
              // مؤشر الصحة الدائري
              const SahoolSkeletonCircle(diameter: 48),
            ],
          ),
          const Spacer(),
          // الصف السفلي: إحصائيات الحقل
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: List.generate(
              3,
              (_) => Column(
                children: [
                  SahoolSkeleton(width: 40, height: 10, borderRadius: 3),
                  const SizedBox(height: 4),
                  SahoolSkeleton(width: 50, height: 14, borderRadius: 3),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// =============================================================================
// WeatherCardSkeleton - Matches Weather Card Layout
// هيكل بطاقة الطقس - يطابق تخطيط بطاقة الطقس الفعلية
// =============================================================================

/// Skeleton that matches the weather card in the dashboard.
/// هيكل يطابق بطاقة الطقس في لوحة التحكم.
class WeatherCardSkeleton extends StatelessWidget {
  const WeatherCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDark
              ? [Colors.grey[800]!, Colors.grey[700]!]
              : [Colors.grey[300]!, Colors.grey[200]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // الموقع والتاريخ
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              SahoolSkeleton(width: 120, height: 16, borderRadius: 4),
              SahoolSkeleton(width: 80, height: 16, borderRadius: 4),
            ],
          ),
          const SizedBox(height: 20),
          // درجة الحرارة ووصف الطقس
          Row(
            children: [
              // أيقونة الطقس النائبة
              SahoolSkeleton(width: 64, height: 64, borderRadius: 16),
              const SizedBox(width: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SahoolSkeleton(width: 80, height: 40, borderRadius: 6),
                  const SizedBox(height: 8),
                  SahoolSkeleton(width: 100, height: 14, borderRadius: 4),
                ],
              ),
            ],
          ),
          const SizedBox(height: 20),
          // تفاصيل الطقس (رطوبة، رياح، إلخ)
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: List.generate(
              3,
              (_) => Column(
                children: [
                  SahoolSkeleton(width: 24, height: 24, borderRadius: 6),
                  const SizedBox(height: 6),
                  SahoolSkeleton(width: 48, height: 12, borderRadius: 3),
                  const SizedBox(height: 4),
                  SahoolSkeleton(width: 36, height: 10, borderRadius: 3),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// =============================================================================
// TaskCardSkeleton - Matches Task Card Layout
// هيكل بطاقة المهمة - يطابق تخطيط بطاقة المهمة الفعلية
// =============================================================================

/// Skeleton that matches the [TaskCard] layout.
/// هيكل يطابق تخطيط بطاقة المهمة.
class TaskCardSkeleton extends StatelessWidget {
  const TaskCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? SahoolColors.surfaceDark : Colors.white;
    final borderColor = isDark ? Colors.grey[700]! : Colors.grey[200]!;

    return Container(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: borderColor),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withValues(alpha: isDark ? 0.0 : 0.08),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // مؤشر الحالة الدائري
          SahoolSkeleton(width: 40, height: 40, borderRadius: 10),
          const SizedBox(width: 12),
          // محتوى المهمة
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // عنوان المهمة
                SahoolSkeleton(width: 180, height: 16, borderRadius: 4),
                const SizedBox(height: 8),
                // وصف المهمة
                SahoolSkeleton(width: 140, height: 12, borderRadius: 4),
                const SizedBox(height: 8),
                // التاريخ والأولوية
                Row(
                  children: [
                    SahoolSkeleton(width: 70, height: 10, borderRadius: 3),
                    const SizedBox(width: 12),
                    SahoolSkeleton(width: 50, height: 18, borderRadius: 9),
                  ],
                ),
              ],
            ),
          ),
          // سهم التنقل
          SahoolSkeleton(width: 24, height: 24, borderRadius: 4),
        ],
      ),
    );
  }
}

// =============================================================================
// StatsRowSkeleton - Horizontal Stats Row
// صف إحصائيات أفقي هيكلي
// =============================================================================

/// Skeleton for a horizontal row of stat cards (e.g., dashboard stats).
/// هيكل صف إحصائيات أفقي (مثل إحصائيات لوحة التحكم).
class StatsRowSkeleton extends StatelessWidget {
  /// Number of stat items in the row.
  /// عدد عناصر الإحصائيات في الصف.
  final int itemCount;

  const StatsRowSkeleton({
    super.key,
    this.itemCount = 3,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? SahoolColors.surfaceDark : Colors.white;

    return Row(
      children: List.generate(itemCount, (index) {
        return Expanded(
          child: Container(
            margin: EdgeInsets.only(
              left: index > 0 ? 6 : 0,
              right: index < itemCount - 1 ? 6 : 0,
            ),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withValues(alpha: isDark ? 0.0 : 0.08),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              children: [
                SahoolSkeleton(width: 24, height: 24, borderRadius: 6),
                const SizedBox(height: 8),
                SahoolSkeleton(width: 40, height: 20, borderRadius: 4),
                const SizedBox(height: 4),
                SahoolSkeleton(width: 56, height: 10, borderRadius: 3),
              ],
            ),
          ),
        );
      }),
    );
  }
}

// =============================================================================
// DashboardSkeleton - Full Dashboard Loading State
// هيكل لوحة التحكم الكاملة
// =============================================================================

/// Full dashboard skeleton matching the [HomeDashboardScreen] layout.
/// هيكل لوحة التحكم الكاملة يطابق تخطيط الشاشة الرئيسية.
class DashboardSkeleton extends StatelessWidget {
  const DashboardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // عنوان قسم الطقس
          _buildSectionTitleSkeleton(),
          const SizedBox(height: 12),

          // بطاقة الطقس
          const WeatherCardSkeleton(),
          const SizedBox(height: 24),

          // عنوان قسم المحفظة
          _buildSectionTitleSkeleton(),
          const SizedBox(height: 12),

          // بطاقة المحفظة
          _buildWalletSkeleton(context),
          const SizedBox(height: 24),

          // عنوان قسم الوصول السريع
          _buildSectionTitleSkeleton(),
          const SizedBox(height: 12),

          // أزرار الوصول السريع
          _buildQuickActionsSkeleton(),
          const SizedBox(height: 24),

          // عنوان قسم التنبيهات
          _buildSectionTitleSkeleton(),
          const SizedBox(height: 12),

          // التنبيهات
          _buildAlertsSkeleton(context),
          const SizedBox(height: 24),

          // عنوان قسم الإحصائيات
          _buildSectionTitleSkeleton(),
          const SizedBox(height: 12),

          // صف الإحصائيات
          const StatsRowSkeleton(),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  /// عنوان قسم هيكلي مع أيقونة
  Widget _buildSectionTitleSkeleton() {
    return Row(
      children: [
        SahoolSkeleton(width: 20, height: 20, borderRadius: 4),
        const SizedBox(width: 8),
        SahoolSkeleton(width: 100, height: 18, borderRadius: 4),
      ],
    );
  }

  /// هيكل بطاقة المحفظة
  Widget _buildWalletSkeleton(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? SahoolColors.surfaceDark : Colors.white;
    final borderColor = isDark ? Colors.grey[700]! : Colors.grey[200]!;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SahoolSkeleton(width: 80, height: 12, borderRadius: 3),
                const SizedBox(height: 8),
                SahoolSkeleton(width: 120, height: 28, borderRadius: 4),
              ],
            ),
          ),
          SahoolSkeleton(width: 60, height: 60, borderRadius: 30),
        ],
      ),
    );
  }

  /// هيكل أزرار الوصول السريع
  Widget _buildQuickActionsSkeleton() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: List.generate(4, (_) {
        return Column(
          children: [
            SahoolSkeleton(width: 56, height: 56, borderRadius: 28),
            const SizedBox(height: 8),
            SahoolSkeleton(width: 48, height: 10, borderRadius: 3),
          ],
        );
      }),
    );
  }

  /// هيكل قسم التنبيهات
  Widget _buildAlertsSkeleton(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? SahoolColors.surfaceDark : Colors.white;

    return Column(
      children: List.generate(2, (index) {
        return Container(
          margin: const EdgeInsets.only(bottom: 10),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: cardColor,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            children: [
              SahoolSkeleton(width: 36, height: 36, borderRadius: 18),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SahoolSkeleton(width: 140, height: 14, borderRadius: 3),
                    const SizedBox(height: 6),
                    SahoolSkeleton(width: 200, height: 11, borderRadius: 3),
                  ],
                ),
              ),
              SahoolSkeleton(width: 50, height: 10, borderRadius: 3),
            ],
          ),
        );
      }),
    );
  }
}

// =============================================================================
// MapSkeleton - Map Placeholder with Shimmer
// هيكل خريطة نائبة مع تأثير اللمعان
// =============================================================================

/// Map placeholder skeleton with grid pattern and loading message.
/// هيكل خريطة نائبة مع نمط شبكي ورسالة تحميل.
class MapSkeleton extends StatelessWidget {
  /// English loading message displayed below the spinner.
  /// رسالة التحميل بالإنجليزية.
  final String? message;

  /// Arabic loading message displayed above the English one.
  /// رسالة التحميل بالعربية.
  final String? messageAr;

  /// Height of the map placeholder. Expands to fill if null.
  /// ارتفاع الخريطة النائبة. تمتد لتملأ المساحة إذا كان فارغاً.
  final double? height;

  const MapSkeleton({
    super.key,
    this.message,
    this.messageAr,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? Colors.grey[900] : Colors.grey[200];
    final gridColor = isDark ? Colors.grey[800]! : Colors.grey[300]!;

    return Container(
      height: height,
      color: bgColor,
      child: Stack(
        children: [
          // نمط الشبكة لمحاكاة الخريطة
          CustomPaint(
            painter: _MapGridPainter(color: gridColor),
            size: Size.infinite,
          ),
          // طبقة التحميل
          Center(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              decoration: BoxDecoration(
                color: isDark
                    ? Colors.grey[850]?.withValues(alpha: 0.95)
                    : Colors.white.withValues(alpha: 0.95),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.1),
                    blurRadius: 20,
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 40,
                    height: 40,
                    child: CircularProgressIndicator(
                      strokeWidth: 3,
                      valueColor: const AlwaysStoppedAnimation<Color>(
                        SahoolColors.primary,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    messageAr ?? 'جاري تحميل الخريطة...',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 16,
                      color: SahoolColors.textDark,
                    ),
                  ),
                  if (message != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      message!,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Grid painter for map skeleton background.
/// رسام الشبكة لخلفية هيكل الخريطة.
class _MapGridPainter extends CustomPainter {
  final Color color;

  _MapGridPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 0.5;

    const spacing = 40.0;

    // خطوط عمودية
    for (double x = 0; x < size.width; x += spacing) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }

    // خطوط أفقية
    for (double y = 0; y < size.height; y += spacing) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant _MapGridPainter oldDelegate) =>
      color != oldDelegate.color;
}
