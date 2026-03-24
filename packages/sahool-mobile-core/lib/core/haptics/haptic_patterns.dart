/// SAHOOL Haptic Feedback Patterns
/// أنماط الاهتزاز للتغذية اللمسية
///
/// Defines various haptic feedback patterns for different interactions.
/// يحدد أنماط اهتزاز مختلفة للتفاعلات المتنوعة
library;


/// Haptic feedback pattern types
/// أنواع أنماط الاهتزاز
enum HapticPattern {
  /// Light tap for selection/toggle
  /// نقرة خفيفة للاختيار/التبديل
  lightTap,

  /// Medium tap for button press
  /// نقرة متوسطة لضغط الأزرار
  mediumTap,

  /// Heavy tap for important actions
  /// نقرة قوية للإجراءات المهمة
  heavyTap,

  /// Success feedback for completed tasks
  /// اهتزاز النجاح للمهام المكتملة
  success,

  /// Warning feedback for alerts
  /// اهتزاز التحذير للتنبيهات
  warning,

  /// Error feedback for validation failures
  /// اهتزاز الخطأ لفشل التحقق
  error,

  /// Notification feedback for new alerts
  /// اهتزاز الإشعار للتنبيهات الجديدة
  notification,

  /// Scroll feedback for list boundaries
  /// اهتزاز التمرير لحدود القوائم
  scroll,

  /// Drag feedback for drag & drop interactions
  /// اهتزاز السحب لتفاعلات السحب والإفلات
  drag,

  /// Selection changed feedback
  /// اهتزاز تغيير التحديد
  selectionChanged,

  /// Impact feedback for collisions
  /// اهتزاز الاصطدام للتصادمات
  impact,

  /// Tick feedback for slider increments
  /// اهتزاز التكة لزيادات المنزلق
  tick,

  /// Soft feedback for subtle interactions
  /// اهتزاز ناعم للتفاعلات الخفيفة
  soft,

  /// Rigid feedback for rigid interactions
  /// اهتزاز صلب للتفاعلات الصلبة
  rigid,
}

/// Pattern definition with duration and intensity
/// تعريف النمط مع المدة والشدة
class HapticPatternDefinition {
  /// Pattern type
  final HapticPattern pattern;

  /// Human-readable name in English
  final String name;

  /// Human-readable name in Arabic
  final String nameAr;

  /// Description of when to use this pattern
  final String description;

  /// Description in Arabic
  final String descriptionAr;

  /// Vibration duration in milliseconds
  final int durationMs;

  /// Vibration intensity (0.0 to 1.0)
  final double intensity;

  /// Vibration pattern for custom patterns [delay, vibrate, delay, vibrate, ...]
  final List<int>? vibrationPattern;

  /// Whether this pattern uses system haptic feedback
  final bool useSystemFeedback;

  /// The system haptic type to use if applicable
  final HapticFeedbackType? systemFeedbackType;

  const HapticPatternDefinition({
    required this.pattern,
    required this.name,
    required this.nameAr,
    required this.description,
    required this.descriptionAr,
    required this.durationMs,
    required this.intensity,
    this.vibrationPattern,
    this.useSystemFeedback = true,
    this.systemFeedbackType,
  });
}

/// System haptic feedback type enumeration
/// نوع الاهتزاز النظامي
enum HapticFeedbackType {
  /// Light impact
  lightImpact,

  /// Medium impact
  mediumImpact,

  /// Heavy impact
  heavyImpact,

  /// Selection click
  selectionClick,

  /// Vibrate
  vibrate,
}

/// Predefined haptic pattern definitions
/// تعريفات أنماط الاهتزاز المحددة مسبقا
class HapticPatterns {
  HapticPatterns._();

  /// Get pattern definition for a given pattern type
  static HapticPatternDefinition getDefinition(HapticPattern pattern) {
    return definitions[pattern] ?? _defaultDefinition;
  }

  /// All pattern definitions
  static const Map<HapticPattern, HapticPatternDefinition> definitions = {
    HapticPattern.lightTap: HapticPatternDefinition(
      pattern: HapticPattern.lightTap,
      name: 'Light Tap',
      nameAr: 'نقرة خفيفة',
      description: 'Selection, toggle, list item tap',
      descriptionAr: 'الاختيار، التبديل، نقر عنصر القائمة',
      durationMs: 10,
      intensity: 0.3,
      useSystemFeedback: true,
      systemFeedbackType: HapticFeedbackType.lightImpact,
    ),
    HapticPattern.mediumTap: HapticPatternDefinition(
      pattern: HapticPattern.mediumTap,
      name: 'Medium Tap',
      nameAr: 'نقرة متوسطة',
      description: 'Button press, action confirmation',
      descriptionAr: 'ضغط الزر، تأكيد الإجراء',
      durationMs: 20,
      intensity: 0.5,
      useSystemFeedback: true,
      systemFeedbackType: HapticFeedbackType.mediumImpact,
    ),
    HapticPattern.heavyTap: HapticPatternDefinition(
      pattern: HapticPattern.heavyTap,
      name: 'Heavy Tap',
      nameAr: 'نقرة قوية',
      description: 'Important action, destructive action',
      descriptionAr: 'إجراء مهم، إجراء حذف',
      durationMs: 30,
      intensity: 0.8,
      useSystemFeedback: true,
      systemFeedbackType: HapticFeedbackType.heavyImpact,
    ),
    HapticPattern.success: HapticPatternDefinition(
      pattern: HapticPattern.success,
      name: 'Success',
      nameAr: 'نجاح',
      description: 'Task completed, operation successful',
      descriptionAr: 'اكتملت المهمة، نجحت العملية',
      durationMs: 100,
      intensity: 0.6,
      useSystemFeedback: false,
      vibrationPattern: [0, 30, 50, 30], // Short-pause-short pattern
    ),
    HapticPattern.warning: HapticPatternDefinition(
      pattern: HapticPattern.warning,
      name: 'Warning',
      nameAr: 'تحذير',
      description: 'Alert, requires attention',
      descriptionAr: 'تنبيه، يتطلب الانتباه',
      durationMs: 150,
      intensity: 0.7,
      useSystemFeedback: false,
      vibrationPattern: [0, 50, 30, 50], // Two pulses
    ),
    HapticPattern.error: HapticPatternDefinition(
      pattern: HapticPattern.error,
      name: 'Error',
      nameAr: 'خطأ',
      description: 'Validation failure, operation failed',
      descriptionAr: 'فشل التحقق، فشلت العملية',
      durationMs: 200,
      intensity: 0.9,
      useSystemFeedback: false,
      vibrationPattern: [0, 70, 30, 70, 30, 70], // Three strong pulses
    ),
    HapticPattern.notification: HapticPatternDefinition(
      pattern: HapticPattern.notification,
      name: 'Notification',
      nameAr: 'إشعار',
      description: 'New notification, incoming message',
      descriptionAr: 'إشعار جديد، رسالة واردة',
      durationMs: 120,
      intensity: 0.5,
      useSystemFeedback: false,
      vibrationPattern: [0, 20, 40, 40, 40, 20], // Notification pattern
    ),
    HapticPattern.scroll: HapticPatternDefinition(
      pattern: HapticPattern.scroll,
      name: 'Scroll',
      nameAr: 'تمرير',
      description: 'Reached list boundary, overscroll',
      descriptionAr: 'وصل لحد القائمة، تجاوز التمرير',
      durationMs: 5,
      intensity: 0.2,
      useSystemFeedback: true,
      systemFeedbackType: HapticFeedbackType.selectionClick,
    ),
    HapticPattern.drag: HapticPatternDefinition(
      pattern: HapticPattern.drag,
      name: 'Drag',
      nameAr: 'سحب',
      description: 'Drag started, drag over target',
      descriptionAr: 'بدء السحب، السحب فوق الهدف',
      durationMs: 15,
      intensity: 0.4,
      useSystemFeedback: true,
      systemFeedbackType: HapticFeedbackType.mediumImpact,
    ),
    HapticPattern.selectionChanged: HapticPatternDefinition(
      pattern: HapticPattern.selectionChanged,
      name: 'Selection Changed',
      nameAr: 'تغير التحديد',
      description: 'Selection state changed',
      descriptionAr: 'تغيرت حالة التحديد',
      durationMs: 10,
      intensity: 0.25,
      useSystemFeedback: true,
      systemFeedbackType: HapticFeedbackType.selectionClick,
    ),
    HapticPattern.impact: HapticPatternDefinition(
      pattern: HapticPattern.impact,
      name: 'Impact',
      nameAr: 'اصطدام',
      description: 'Collision, snap to grid',
      descriptionAr: 'تصادم، محاذاة للشبكة',
      durationMs: 25,
      intensity: 0.6,
      useSystemFeedback: true,
      systemFeedbackType: HapticFeedbackType.heavyImpact,
    ),
    HapticPattern.tick: HapticPatternDefinition(
      pattern: HapticPattern.tick,
      name: 'Tick',
      nameAr: 'تكة',
      description: 'Slider step, picker rotation',
      descriptionAr: 'خطوة المنزلق، دوران المختار',
      durationMs: 5,
      intensity: 0.15,
      useSystemFeedback: true,
      systemFeedbackType: HapticFeedbackType.selectionClick,
    ),
    HapticPattern.soft: HapticPatternDefinition(
      pattern: HapticPattern.soft,
      name: 'Soft',
      nameAr: 'ناعم',
      description: 'Subtle feedback, background completion',
      descriptionAr: 'تغذية راجعة خفيفة، اكتمال الخلفية',
      durationMs: 8,
      intensity: 0.1,
      useSystemFeedback: true,
      systemFeedbackType: HapticFeedbackType.lightImpact,
    ),
    HapticPattern.rigid: HapticPatternDefinition(
      pattern: HapticPattern.rigid,
      name: 'Rigid',
      nameAr: 'صلب',
      description: 'Rigid interaction, lock',
      descriptionAr: 'تفاعل صلب، قفل',
      durationMs: 20,
      intensity: 0.7,
      useSystemFeedback: true,
      systemFeedbackType: HapticFeedbackType.heavyImpact,
    ),
  };

  /// Default pattern definition as fallback
  static const HapticPatternDefinition _defaultDefinition =
      HapticPatternDefinition(
    pattern: HapticPattern.lightTap,
    name: 'Default',
    nameAr: 'افتراضي',
    description: 'Default haptic feedback',
    descriptionAr: 'الاهتزاز الافتراضي',
    durationMs: 10,
    intensity: 0.3,
    useSystemFeedback: true,
    systemFeedbackType: HapticFeedbackType.lightImpact,
  );

  /// Get patterns suitable for buttons
  static List<HapticPattern> get buttonPatterns => [
        HapticPattern.lightTap,
        HapticPattern.mediumTap,
        HapticPattern.heavyTap,
      ];

  /// Get patterns suitable for notifications
  static List<HapticPattern> get notificationPatterns => [
        HapticPattern.notification,
        HapticPattern.warning,
        HapticPattern.error,
        HapticPattern.success,
      ];

  /// Get patterns suitable for gestures
  static List<HapticPattern> get gesturePatterns => [
        HapticPattern.scroll,
        HapticPattern.drag,
        HapticPattern.selectionChanged,
      ];

  /// Get all patterns
  static List<HapticPattern> get allPatterns => HapticPattern.values;
}
