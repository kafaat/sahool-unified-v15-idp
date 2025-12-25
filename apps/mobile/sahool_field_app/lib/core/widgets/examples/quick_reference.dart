/// SAHOOL Widget Quick Reference Guide
/// دليل مرجعي سريع لمكونات ساهول
///
/// This file provides quick reference examples for all SAHOOL UI components.
/// All components support RTL (Right-to-Left) and Arabic text by default.

// ══════════════════════════════════════════════════════════════════════════════
// 1. ERROR HANDLING COMPONENTS - مكونات معالجة الأخطاء
// ══════════════════════════════════════════════════════════════════════════════

/*
┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolErrorBoundary - Error boundary for catching widget errors             │
│ حد الأخطاء لالتقاط أخطاء الـ widgets                                       │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolErrorBoundary(
  child: MyWidget(),
  onError: (error, stack) => logError(error),
  errorBuilder: (error, retry) => SahoolErrorView(
    error: error,
    onRetry: retry,
  ),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolErrorView - Standard error display with retry button                  │
│ عرض خطأ قياسي مع زر إعادة المحاولة                                         │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolErrorView(
  error: Exception('Network error'),
  onRetry: () => reload(),
  customMessage: 'رسالة خاصة',
  showDetails: false,
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolTypedErrorView - Auto-categorizes errors (network, auth, etc.)       │
│ عرض خطأ بتصنيف تلقائي (شبكة، مصادقة، إلخ)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolTypedErrorView(
  error: error,
  onRetry: () => retry(),
  showDetails: false,
)

Error Types (SahoolErrorType):
  - network: Network/connection errors
  - timeout: Request timeout
  - authentication: 401 errors
  - permission: 403 errors
  - notFound: 404 errors
  - server: 500+ errors
  - validation: Invalid data
  - unknown: General errors

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolInlineError - Compact error for inline display                       │
│ خطأ مضغوط للعرض المضمن                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolInlineError(
  message: 'فشل التحميل',
  onRetry: () => reload(),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolNetworkError - Dedicated network error display                       │
│ عرض مخصص لأخطاء الشبكة                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolNetworkError(
  onRetry: () => reconnect(),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolErrorUtil - Utility for error classification                         │
│ أداة مساعدة لتصنيف الأخطاء                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

final type = SahoolErrorUtil.getErrorType(error);
final message = SahoolErrorUtil.getLocalizedMessage(type);
final icon = SahoolErrorUtil.getErrorIcon(type);
*/

// ══════════════════════════════════════════════════════════════════════════════
// 2. LOADING STATE COMPONENTS - مكونات حالات التحميل
// ══════════════════════════════════════════════════════════════════════════════

/*
┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolShimmer - Base shimmer effect for loading                            │
│ تأثير التحميل الأساسي                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolShimmer(
  enabled: true,
  child: Container(...),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolShimmerCard - Shimmer placeholder card                               │
│ بطاقة تحميل وهمية                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolShimmerCard(
  height: 120,
  width: double.infinity,
  borderRadius: 16,
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolShimmerList - Shimmer list placeholder                               │
│ قائمة تحميل وهمية                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolShimmerList(
  itemCount: 5,
  itemHeight: 80,
  spacing: 12,
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolShimmerGrid - Shimmer grid placeholder                               │
│ شبكة تحميل وهمية                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolShimmerGrid(
  itemCount: 6,
  crossAxisCount: 2,
  childAspectRatio: 1.0,
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolLoadingScreen - Full screen loading                                  │
│ شاشة تحميل كاملة                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolLoadingScreen(
  message: 'جاري التحميل...',
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolLoadingOverlay - Loading overlay for content                         │
│ غطاء تحميل للمحتوى                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolLoadingOverlay(
  isLoading: _isLoading,
  message: 'جاري الحفظ...',
  child: MyContent(),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolLoadingButton - Button with loading state                            │
│ زر مع حالة تحميل                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolLoadingButton(
  onPressed: _submit,
  isLoading: _isLoading,
  child: Text('حفظ'),
  backgroundColor: SahoolColors.primary,
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolLoadingSpinner - Custom loading spinner                              │
│ دائرة تحميل مخصصة                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolLoadingSpinner(
  size: 32,
  color: SahoolColors.primary,
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolInlineLoading - Inline loading indicator                             │
│ مؤشر تحميل مضمن                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolInlineLoading(
  message: 'جاري التحميل...',
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolRefreshIndicator - Pull to refresh                                   │
│ اسحب للتحديث                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolRefreshIndicator(
  onRefresh: () async => await reload(),
  child: ListView(...),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolProgressBar - Linear progress bar                                    │
│ شريط التقدم الخطي                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolProgressBar(
  value: 0.7, // null for indeterminate
  height: 4,
  progressColor: SahoolColors.primary,
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolTextShimmer - Text loading shimmer                                   │
│ تحميل نص وهمي                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolTextShimmer(
  width: 100,
  height: 16,
  borderRadius: 4,
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolCircleShimmer - Avatar loading shimmer                               │
│ تحميل صورة رمزية وهمية                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolCircleShimmer(size: 48)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolListItemSkeleton - List item skeleton                                │
│ هيكل عنصر قائمة                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolListItemSkeleton(
  hasAvatar: true,
  textLines: 2,
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolProfileHeaderSkeleton - Profile header skeleton                      │
│ هيكل رأس الملف الشخصي                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolProfileHeaderSkeleton()

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolFieldCardSkeleton - Field card skeleton                              │
│ هيكل بطاقة الحقل                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolFieldCardSkeleton()

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolAsyncBuilder - Async data loader with loading/error states           │
│ محمل بيانات غير متزامن مع حالات التحميل/الخطأ                             │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolAsyncBuilder<String>(
  future: fetchData(),
  builder: (data) => Text(data),
  loadingWidget: SahoolLoadingScreen(),
  errorBuilder: (error) => SahoolErrorView(error: error),
)
*/

// ══════════════════════════════════════════════════════════════════════════════
// 3. EMPTY STATE COMPONENTS - مكونات الحالات الفارغة
// ══════════════════════════════════════════════════════════════════════════════

/*
┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolEmptyState - Base customizable empty state                           │
│ حالة فارغة قابلة للتخصيص                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolEmptyState(
  icon: Icons.inbox,
  title: 'لا توجد عناصر',
  message: 'رسالة توضيحية',
  actionLabel: 'إضافة',
  onAction: () => add(),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ PREDEFINED EMPTY STATES - الحالات الفارغة المحددة مسبقاً                   │
└─────────────────────────────────────────────────────────────────────────────┘

NoFieldsEmptyState(onAddField: () => addField())
NoTasksEmptyState(onAddTask: () => addTask())
NoDataEmptyState(onRefresh: () => refresh())
NoConnectionEmptyState(onRetry: () => retry())
NoAlertsEmptyState()
NoNotificationsEmptyState()
NoSearchResultsEmptyState(searchQuery: 'query', onClear: () {})
OfflineEmptyState(onRetry: () => reconnect())
NoEquipmentEmptyState(onAddEquipment: () => add())
NoTransactionsEmptyState()
NoMessagesEmptyState(onStartChat: () => chat())
ComingSoonEmptyState(featureName: 'اسم الميزة')
NoCropsEmptyState(onAddCrop: () => addCrop())
NoReportsEmptyState(onCreateReport: () => create())
NoWeatherDataEmptyState(onRefresh: () => refresh())
NoImagesEmptyState(onAddImage: () => addImage())
PermissionDeniedEmptyState(
  permissionName: 'الكاميرا',
  onRequestPermission: () => request(),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolCompactEmptyState - Compact empty state for small spaces             │
│ حالة فارغة مضغوطة للمساحات الصغيرة                                         │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolCompactEmptyState(
  icon: Icons.description_outlined,
  message: 'لا توجد مستندات',
  actionLabel: 'إضافة',
  onAction: () => add(),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ SahoolRTLEmptyState - RTL wrapper for Arabic support                       │
│ غلاف RTL لدعم اللغة العربية                                                │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolRTLEmptyState(
  child: NoFieldsEmptyState(),
)
*/

// ══════════════════════════════════════════════════════════════════════════════
// 4. COMPLETE USAGE PATTERNS - أنماط الاستخدام الكاملة
// ══════════════════════════════════════════════════════════════════════════════

/*
┌─────────────────────────────────────────────────────────────────────────────┐
│ PATTERN 1: List Screen with Loading, Error, and Empty States               │
│ النمط 1: شاشة قائمة مع حالات التحميل والخطأ والفراغ                        │
└─────────────────────────────────────────────────────────────────────────────┘

Widget build(BuildContext context) {
  if (_isLoading) {
    return SahoolShimmerList(itemCount: 5);
  }

  if (_hasError) {
    return SahoolNetworkError(onRetry: _reload);
  }

  if (_items.isEmpty) {
    return NoDataEmptyState(onRefresh: _reload);
  }

  return SahoolRefreshIndicator(
    onRefresh: _reload,
    child: ListView.builder(...),
  );
}

┌─────────────────────────────────────────────────────────────────────────────┐
│ PATTERN 2: Form with Loading Button                                        │
│ النمط 2: نموذج مع زر تحميل                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolLoadingButton(
  onPressed: _isValid ? _submit : null,
  isLoading: _isSubmitting,
  child: Text('حفظ'),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ PATTERN 3: Async Data Loading                                              │
│ النمط 3: تحميل البيانات غير المتزامنة                                      │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolAsyncBuilder<List<Field>>(
  future: _apiService.getFields(),
  builder: (fields) {
    if (fields.isEmpty) {
      return NoFieldsEmptyState(onAddField: _addField);
    }
    return FieldsList(fields: fields);
  },
  loadingWidget: SahoolShimmerList(itemCount: 5),
  errorBuilder: (error) => SahoolTypedErrorView(
    error: error,
    onRetry: () => setState(() {}),
  ),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ PATTERN 4: Global Error Boundary                                           │
│ النمط 4: حدود الخطأ العامة                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

MaterialApp(
  builder: (context, child) {
    return SahoolErrorBoundary(
      onError: (error, stack) {
        // Log to analytics
        FirebaseCrashlytics.instance.recordError(error, stack);
      },
      child: child ?? SizedBox(),
    );
  },
  home: MyHomePage(),
)

┌─────────────────────────────────────────────────────────────────────────────┐
│ PATTERN 5: Loading Overlay for Actions                                     │
│ النمط 5: غطاء تحميل للإجراءات                                              │
└─────────────────────────────────────────────────────────────────────────────┘

SahoolLoadingOverlay(
  isLoading: _isSaving,
  message: 'جاري الحفظ...',
  child: FormContent(),
)
*/

// ══════════════════════════════════════════════════════════════════════════════
// 5. RTL AND ARABIC SUPPORT - دعم RTL واللغة العربية
// ══════════════════════════════════════════════════════════════════════════════

/*
All widgets automatically support RTL and Arabic text. To enable RTL in your app:

MaterialApp(
  locale: Locale('ar', 'SA'),
  supportedLocales: [Locale('ar', 'SA'), Locale('en', 'US')],
  builder: (context, child) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: child ?? SizedBox(),
    );
  },
  home: MyHomePage(),
)

All error messages and empty state text are in Arabic by default.
All icons and layouts support RTL automatically.
*/

// ══════════════════════════════════════════════════════════════════════════════
// 6. COLOR USAGE - استخدام الألوان
// ══════════════════════════════════════════════════════════════════════════════

/*
All widgets use colors from SahoolColors (lib/core/theme/sahool_theme.dart):

- SahoolColors.primary - Primary green
- SahoolColors.secondary - Light green
- SahoolColors.danger - Error red
- SahoolColors.success - Success green
- SahoolColors.warning - Warning yellow
- SahoolColors.info - Info blue
- SahoolColors.textDark - Dark text
- SahoolColors.textSecondary - Secondary text
- SahoolColors.background - Background color

These colors are optimized for outdoor visibility and glove usage.
*/
