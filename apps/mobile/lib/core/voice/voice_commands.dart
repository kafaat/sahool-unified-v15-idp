import 'dart:math';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_logger.dart';

/// SAHOOL Voice Commands
/// تعريفات الأوامر الصوتية
///
/// Features:
/// - Bilingual commands (Arabic/English)
/// - Fuzzy matching for flexible recognition
/// - Command categorization
/// - Parameter extraction
/// - Context-aware suggestions

// ═══════════════════════════════════════════════════════════════════════════
// Command Types & Categories
// ═══════════════════════════════════════════════════════════════════════════

/// Voice command type
enum VoiceCommandType {
  // Navigation Commands
  openFields('open_fields', 'Navigation', 'الانتقال'),
  openWeather('open_weather', 'Navigation', 'الانتقال'),
  openNDVI('open_ndvi', 'Navigation', 'الانتقال'),
  openTasks('open_tasks', 'Navigation', 'الانتقال'),
  openAdvisor('open_advisor', 'Navigation', 'الانتقال'),
  openSettings('open_settings', 'Navigation', 'الانتقال'),
  openHome('open_home', 'Navigation', 'الانتقال'),
  goBack('go_back', 'Navigation', 'الانتقال'),

  // Field Operations
  selectField('select_field', 'Field', 'الحقل'),
  viewFieldDetails('view_field_details', 'Field', 'الحقل'),
  checkNDVI('check_ndvi', 'Field', 'الحقل'),
  viewCropHealth('view_crop_health', 'Field', 'الحقل'),

  // Irrigation Commands
  scheduleIrrigation('schedule_irrigation', 'Irrigation', 'الري'),
  recordIrrigation('record_irrigation', 'Irrigation', 'الري'),
  stopIrrigation('stop_irrigation', 'Irrigation', 'الري'),
  checkIrrigationStatus('check_irrigation_status', 'Irrigation', 'الري'),

  // Task Commands
  createTask('create_task', 'Task', 'المهام'),
  viewTodayTasks('view_today_tasks', 'Task', 'المهام'),
  completeTask('complete_task', 'Task', 'المهام'),
  showOverdueTasks('show_overdue_tasks', 'Task', 'المهام'),

  // Weather Commands
  showWeather('show_weather', 'Weather', 'الطقس'),
  showForecast('show_forecast', 'Weather', 'الطقس'),
  checkRainProbability('check_rain', 'Weather', 'الطقس'),

  // Scouting & Reports
  startScouting('start_scouting', 'Scouting', 'الفحص'),
  capturePhoto('capture_photo', 'Scouting', 'الفحص'),
  reportProblem('report_problem', 'Scouting', 'الفحص'),
  viewReports('view_reports', 'Scouting', 'الفحص'),

  // Advisory
  getAdvice('get_advice', 'Advisory', 'الاستشارة'),
  askQuestion('ask_question', 'Advisory', 'الاستشارة'),

  // Utility Commands
  help('help', 'Utility', 'المساعدة'),
  cancel('cancel', 'Utility', 'المساعدة'),
  repeat('repeat', 'Utility', 'المساعدة'),
  dailySummary('daily_summary', 'Utility', 'المساعدة'),

  // Unknown
  unknown('unknown', 'Unknown', 'غير معروف');

  final String id;
  final String categoryEn;
  final String categoryAr;

  const VoiceCommandType(this.id, this.categoryEn, this.categoryAr);
}

/// Command definition with patterns and metadata
class VoiceCommandDefinition {
  final VoiceCommandType type;
  final String nameEn;
  final String nameAr;
  final String descriptionEn;
  final String descriptionAr;
  final List<String> patternsEn;
  final List<String> patternsAr;
  final List<String> examplesEn;
  final List<String> examplesAr;
  final List<String> parameterHints;
  final bool requiresParameter;

  const VoiceCommandDefinition({
    required this.type,
    required this.nameEn,
    required this.nameAr,
    required this.descriptionEn,
    required this.descriptionAr,
    required this.patternsEn,
    required this.patternsAr,
    this.examplesEn = const [],
    this.examplesAr = const [],
    this.parameterHints = const [],
    this.requiresParameter = false,
  });
}

/// Parsed voice command with extracted parameters
class ParsedVoiceCommand {
  final VoiceCommandType type;
  final String rawText;
  final double confidence;
  final Map<String, dynamic> parameters;
  final bool isArabic;
  final DateTime timestamp;
  final String? matchedPattern;

  const ParsedVoiceCommand({
    required this.type,
    required this.rawText,
    required this.confidence,
    this.parameters = const {},
    required this.isArabic,
    required this.timestamp,
    this.matchedPattern,
  });

  bool get isRecognized => type != VoiceCommandType.unknown;
  bool get isHighConfidence => confidence >= 0.7;
  bool get hasParameters => parameters.isNotEmpty;

  @override
  String toString() =>
      'ParsedVoiceCommand(type: ${type.id}, confidence: ${(confidence * 100).toStringAsFixed(1)}%, params: $parameters)';
}

// ═══════════════════════════════════════════════════════════════════════════
// Command Definitions Registry
// ═══════════════════════════════════════════════════════════════════════════

class VoiceCommandRegistry {
  static const List<VoiceCommandDefinition> commands = [
    // ─────────────────────────────────────────────────────────────────────────
    // Navigation Commands
    // ─────────────────────────────────────────────────────────────────────────
    VoiceCommandDefinition(
      type: VoiceCommandType.openFields,
      nameEn: 'Open Fields',
      nameAr: 'افتح الحقول',
      descriptionEn: 'Navigate to the fields list',
      descriptionAr: 'الانتقال إلى قائمة الحقول',
      patternsEn: ['open fields', 'show fields', 'go to fields', 'fields list', 'view fields', 'my fields'],
      patternsAr: ['افتح الحقول', 'اعرض الحقول', 'شوف الحقول', 'الحقول', 'قائمة الحقول', 'حقولي'],
      examplesEn: ['Open fields', 'Show my fields'],
      examplesAr: ['افتح الحقول', 'اعرض حقولي'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.openWeather,
      nameEn: 'Show Weather',
      nameAr: 'أظهر الطقس',
      descriptionEn: 'View current weather and forecast',
      descriptionAr: 'عرض الطقس الحالي والتوقعات',
      patternsEn: ['show weather', 'open weather', 'weather', 'whats the weather', 'weather forecast', 'how is the weather'],
      patternsAr: ['اظهر الطقس', 'افتح الطقس', 'الطقس', 'كيف الطقس', 'شو الجو', 'احوال الطقس', 'الجو'],
      examplesEn: ['Show weather', "What's the weather today"],
      examplesAr: ['أظهر الطقس', 'كيف الجو اليوم'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.openNDVI,
      nameEn: 'Check NDVI',
      nameAr: 'فحص NDVI',
      descriptionEn: 'View vegetation health indices',
      descriptionAr: 'عرض مؤشرات صحة النبات',
      patternsEn: ['check ndvi', 'open ndvi', 'ndvi', 'vegetation index', 'plant health', 'crop health map'],
      patternsAr: ['فحص ndvi', 'افتح ndvi', 'مؤشر الغطاء النباتي', 'صحة النبات', 'خريطة صحة المحصول'],
      examplesEn: ['Check NDVI', 'Show vegetation health'],
      examplesAr: ['فحص NDVI', 'صحة النباتات'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.openTasks,
      nameEn: 'Open Tasks',
      nameAr: 'افتح المهام',
      descriptionEn: 'View task list',
      descriptionAr: 'عرض قائمة المهام',
      patternsEn: ['open tasks', 'show tasks', 'my tasks', 'task list', 'todo', 'what to do'],
      patternsAr: ['افتح المهام', 'اعرض المهام', 'مهامي', 'قائمة المهام', 'الأعمال', 'ايش اسوي'],
      examplesEn: ['Open tasks', 'Show my tasks'],
      examplesAr: ['افتح المهام', 'ما المهام اليوم'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.openAdvisor,
      nameEn: 'Open Advisor',
      nameAr: 'افتح المستشار',
      descriptionEn: 'Open the agricultural advisor',
      descriptionAr: 'فتح المستشار الزراعي',
      patternsEn: ['open advisor', 'agricultural advisor', 'get advice', 'ask advisor', 'farming tips'],
      patternsAr: ['افتح المستشار', 'المستشار الزراعي', 'نصيحة', 'استشارة', 'اسأل المستشار'],
      examplesEn: ['Open advisor', 'I need farming advice'],
      examplesAr: ['افتح المستشار', 'أحتاج نصيحة زراعية'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.openSettings,
      nameEn: 'Open Settings',
      nameAr: 'افتح الإعدادات',
      descriptionEn: 'Open app settings',
      descriptionAr: 'فتح إعدادات التطبيق',
      patternsEn: ['open settings', 'settings', 'preferences', 'app settings'],
      patternsAr: ['افتح الإعدادات', 'الإعدادات', 'التفضيلات', 'اعدادات التطبيق'],
      examplesEn: ['Open settings'],
      examplesAr: ['افتح الإعدادات'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.openHome,
      nameEn: 'Go Home',
      nameAr: 'الصفحة الرئيسية',
      descriptionEn: 'Go to home screen',
      descriptionAr: 'الانتقال للصفحة الرئيسية',
      patternsEn: ['go home', 'home', 'main screen', 'dashboard', 'home page'],
      patternsAr: ['الرئيسية', 'الصفحة الرئيسية', 'البداية', 'الشاشة الرئيسية'],
      examplesEn: ['Go home', 'Back to home'],
      examplesAr: ['الرئيسية', 'رجوع للبداية'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.goBack,
      nameEn: 'Go Back',
      nameAr: 'رجوع',
      descriptionEn: 'Go to previous screen',
      descriptionAr: 'الرجوع للشاشة السابقة',
      patternsEn: ['go back', 'back', 'previous', 'return'],
      patternsAr: ['رجوع', 'ارجع', 'السابق', 'للخلف'],
      examplesEn: ['Go back', 'Back'],
      examplesAr: ['رجوع', 'ارجع'],
    ),

    // ─────────────────────────────────────────────────────────────────────────
    // Field Operations
    // ─────────────────────────────────────────────────────────────────────────
    VoiceCommandDefinition(
      type: VoiceCommandType.selectField,
      nameEn: 'Select Field',
      nameAr: 'اختر حقل',
      descriptionEn: 'Select a specific field by name or number',
      descriptionAr: 'اختيار حقل معين بالاسم أو الرقم',
      patternsEn: ['open field', 'select field', 'go to field', 'field number', 'show field'],
      patternsAr: ['افتح حقل', 'اختر حقل', 'الحقل رقم', 'حقل', 'اعرض حقل'],
      examplesEn: ['Open field 1', 'Select field number 3'],
      examplesAr: ['افتح حقل 1', 'الحقل رقم 3', 'افتح الحقل الأول'],
      parameterHints: ['fieldId', 'fieldNumber', 'fieldName'],
      requiresParameter: true,
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.viewFieldDetails,
      nameEn: 'View Field Details',
      nameAr: 'تفاصيل الحقل',
      descriptionEn: 'View detailed information about a field',
      descriptionAr: 'عرض معلومات تفصيلية عن الحقل',
      patternsEn: ['field details', 'field info', 'field information', 'tell me about field'],
      patternsAr: ['تفاصيل الحقل', 'معلومات الحقل', 'عن الحقل', 'اخبرني عن حقل'],
      examplesEn: ['Show field details', 'Field information'],
      examplesAr: ['تفاصيل الحقل', 'معلومات الحقل 2'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.checkNDVI,
      nameEn: 'Check Field NDVI',
      nameAr: 'فحص NDVI للحقل',
      descriptionEn: 'Check NDVI for specific field',
      descriptionAr: 'فحص مؤشر الغطاء النباتي لحقل معين',
      patternsEn: ['check ndvi for field', 'field ndvi', 'ndvi of field', 'vegetation health of'],
      patternsAr: ['فحص ndvi للحقل', 'ndvi الحقل', 'صحة النباتات في حقل'],
      examplesEn: ['Check NDVI for field 1'],
      examplesAr: ['فحص NDVI للحقل 1'],
      parameterHints: ['fieldId'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.viewCropHealth,
      nameEn: 'View Crop Health',
      nameAr: 'صحة المحصول',
      descriptionEn: 'View crop health status',
      descriptionAr: 'عرض حالة صحة المحصول',
      patternsEn: ['crop health', 'how is the crop', 'crop status', 'plant condition'],
      patternsAr: ['صحة المحصول', 'كيف المحصول', 'حالة المحصول', 'حالة الزراعة', 'كيف الزرع'],
      examplesEn: ['How is the crop health'],
      examplesAr: ['كيف صحة المحصول', 'حالة المحصول'],
    ),

    // ─────────────────────────────────────────────────────────────────────────
    // Irrigation Commands
    // ─────────────────────────────────────────────────────────────────────────
    VoiceCommandDefinition(
      type: VoiceCommandType.scheduleIrrigation,
      nameEn: 'Schedule Irrigation',
      nameAr: 'جدول الري',
      descriptionEn: 'Schedule irrigation for a field',
      descriptionAr: 'جدولة الري لحقل معين',
      patternsEn: ['schedule irrigation', 'plan irrigation', 'irrigation schedule', 'set irrigation', 'water schedule'],
      patternsAr: ['جدول الري', 'جدولة الري', 'خطة الري', 'ترتيب الري', 'موعد الري'],
      examplesEn: ['Schedule irrigation for field 1', 'Set irrigation schedule'],
      examplesAr: ['جدول الري للحقل 1', 'حدد موعد الري'],
      parameterHints: ['fieldId', 'date', 'duration'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.recordIrrigation,
      nameEn: 'Record Irrigation',
      nameAr: 'سجل ري',
      descriptionEn: 'Record an irrigation activity',
      descriptionAr: 'تسجيل عملية ري',
      patternsEn: ['record irrigation', 'log irrigation', 'add irrigation', 'irrigated', 'watered'],
      patternsAr: ['سجل ري', 'اضف ري', 'تسجيل ري', 'سقيت', 'رويت الحقل'],
      examplesEn: ['Record irrigation for field 1', 'I watered field 2'],
      examplesAr: ['سجل ري للحقل 1', 'سقيت الحقل 2'],
      parameterHints: ['fieldId', 'amount', 'duration'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.stopIrrigation,
      nameEn: 'Stop Irrigation',
      nameAr: 'أوقف الري',
      descriptionEn: 'Stop ongoing irrigation',
      descriptionAr: 'إيقاف الري الجاري',
      patternsEn: ['stop irrigation', 'end irrigation', 'turn off water', 'stop watering'],
      patternsAr: ['اوقف الري', 'انهي الري', 'اقفل الماء', 'وقف الري'],
      examplesEn: ['Stop irrigation'],
      examplesAr: ['أوقف الري'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.checkIrrigationStatus,
      nameEn: 'Irrigation Status',
      nameAr: 'حالة الري',
      descriptionEn: 'Check irrigation status',
      descriptionAr: 'التحقق من حالة الري',
      patternsEn: ['irrigation status', 'is irrigation on', 'watering status', 'when was last irrigation'],
      patternsAr: ['حالة الري', 'هل الري شغال', 'متى آخر ري', 'وضع الري'],
      examplesEn: ['What is the irrigation status'],
      examplesAr: ['حالة الري', 'متى آخر مرة سقيت'],
    ),

    // ─────────────────────────────────────────────────────────────────────────
    // Task Commands
    // ─────────────────────────────────────────────────────────────────────────
    VoiceCommandDefinition(
      type: VoiceCommandType.createTask,
      nameEn: 'Create Task',
      nameAr: 'إنشاء مهمة',
      descriptionEn: 'Create a new task',
      descriptionAr: 'إنشاء مهمة جديدة',
      patternsEn: ['create task', 'new task', 'add task', 'make task', 'add todo'],
      patternsAr: ['انشئ مهمة', 'مهمة جديدة', 'اضف مهمة', 'سجل مهمة', 'اضف عمل'],
      examplesEn: ['Create task', 'Add new task'],
      examplesAr: ['إنشاء مهمة', 'أضف مهمة جديدة'],
      parameterHints: ['title', 'description', 'dueDate'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.viewTodayTasks,
      nameEn: "Today's Tasks",
      nameAr: 'مهام اليوم',
      descriptionEn: "View today's tasks",
      descriptionAr: 'عرض مهام اليوم',
      patternsEn: ['today tasks', 'todays tasks', 'what to do today', 'tasks for today', 'daily tasks'],
      patternsAr: ['مهام اليوم', 'ايش المهام اليوم', 'شو اعمل اليوم', 'اعمال اليوم'],
      examplesEn: ["What are today's tasks"],
      examplesAr: ['ما مهام اليوم', 'إيش أعمل اليوم'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.completeTask,
      nameEn: 'Complete Task',
      nameAr: 'أكمل المهمة',
      descriptionEn: 'Mark a task as complete',
      descriptionAr: 'تحديد مهمة كمكتملة',
      patternsEn: ['complete task', 'finish task', 'done with task', 'task completed', 'mark done'],
      patternsAr: ['اكمل المهمة', 'انهي المهمة', 'خلصت المهمة', 'تم انجاز', 'انجزت'],
      examplesEn: ['Complete task 1', 'Mark task as done'],
      examplesAr: ['أكمل المهمة 1', 'خلصت المهمة'],
      parameterHints: ['taskId'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.showOverdueTasks,
      nameEn: 'Overdue Tasks',
      nameAr: 'المهام المتأخرة',
      descriptionEn: 'Show overdue tasks',
      descriptionAr: 'عرض المهام المتأخرة',
      patternsEn: ['overdue tasks', 'late tasks', 'missed tasks', 'pending tasks'],
      patternsAr: ['المهام المتأخرة', 'المهام المتأجلة', 'مهام فاتت', 'مهام معلقة'],
      examplesEn: ['Show overdue tasks'],
      examplesAr: ['اعرض المهام المتأخرة'],
    ),

    // ─────────────────────────────────────────────────────────────────────────
    // Weather Commands
    // ─────────────────────────────────────────────────────────────────────────
    VoiceCommandDefinition(
      type: VoiceCommandType.showWeather,
      nameEn: 'Current Weather',
      nameAr: 'الطقس الحالي',
      descriptionEn: 'Show current weather conditions',
      descriptionAr: 'عرض أحوال الطقس الحالية',
      patternsEn: ['current weather', 'weather now', 'how is weather', 'weather today'],
      patternsAr: ['الطقس الحالي', 'الطقس الان', 'كيف الجو', 'الجو اليوم'],
      examplesEn: ['How is the weather now'],
      examplesAr: ['كيف الطقس الآن'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.showForecast,
      nameEn: 'Weather Forecast',
      nameAr: 'توقعات الطقس',
      descriptionEn: 'Show weather forecast',
      descriptionAr: 'عرض توقعات الطقس',
      patternsEn: ['weather forecast', 'forecast', 'weather tomorrow', 'next week weather', 'week forecast'],
      patternsAr: ['توقعات الطقس', 'الطقس بكرة', 'طقس الاسبوع', 'توقعات الجو'],
      examplesEn: ['Show weather forecast', 'Weather for this week'],
      examplesAr: ['توقعات الطقس', 'الجو بكرة'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.checkRainProbability,
      nameEn: 'Rain Probability',
      nameAr: 'احتمال المطر',
      descriptionEn: 'Check probability of rain',
      descriptionAr: 'التحقق من احتمال هطول المطر',
      patternsEn: ['will it rain', 'rain probability', 'chance of rain', 'is it going to rain', 'rain forecast'],
      patternsAr: ['هل ستمطر', 'احتمال المطر', 'فرصة المطر', 'بتمطر', 'توقعات المطر'],
      examplesEn: ['Will it rain today', 'Rain probability'],
      examplesAr: ['هل بتمطر اليوم', 'احتمال المطر'],
    ),

    // ─────────────────────────────────────────────────────────────────────────
    // Scouting & Reports
    // ─────────────────────────────────────────────────────────────────────────
    VoiceCommandDefinition(
      type: VoiceCommandType.startScouting,
      nameEn: 'Start Scouting',
      nameAr: 'ابدأ الفحص',
      descriptionEn: 'Start a field scouting session',
      descriptionAr: 'بدء جلسة فحص ميداني',
      patternsEn: ['start scouting', 'begin scouting', 'field inspection', 'scout field', 'start inspection'],
      patternsAr: ['ابدأ الفحص', 'ابدا جولة', 'فحص الحقل', 'تفقد الحقل', 'جولة ميدانية'],
      examplesEn: ['Start scouting', 'Begin field inspection'],
      examplesAr: ['ابدأ الفحص', 'جولة فحص الحقل'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.capturePhoto,
      nameEn: 'Take Photo',
      nameAr: 'التقط صورة',
      descriptionEn: 'Capture a photo for documentation',
      descriptionAr: 'التقاط صورة للتوثيق',
      patternsEn: ['take photo', 'capture photo', 'take picture', 'photograph', 'snap'],
      patternsAr: ['التقط صورة', 'صور', 'خذ صورة', 'تصوير'],
      examplesEn: ['Take a photo', 'Capture'],
      examplesAr: ['التقط صورة', 'صور'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.reportProblem,
      nameEn: 'Report Problem',
      nameAr: 'بلاغ مشكلة',
      descriptionEn: 'Report an issue or problem',
      descriptionAr: 'الإبلاغ عن مشكلة',
      patternsEn: ['report problem', 'report issue', 'found problem', 'there is a problem', 'pest detected', 'disease found'],
      patternsAr: ['بلغ عن مشكلة', 'سجل مشكلة', 'في مشكلة', 'وجدت آفة', 'في مرض', 'حشرات'],
      examplesEn: ['Report a problem', 'Found pest damage'],
      examplesAr: ['بلغ عن مشكلة', 'في آفات بالحقل'],
      parameterHints: ['problemType', 'severity', 'location'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.viewReports,
      nameEn: 'View Reports',
      nameAr: 'عرض التقارير',
      descriptionEn: 'View scouting reports',
      descriptionAr: 'عرض تقارير الفحص',
      patternsEn: ['view reports', 'show reports', 'scouting reports', 'inspection history'],
      patternsAr: ['عرض التقارير', 'اعرض التقارير', 'تقارير الفحص', 'سجل الفحوصات'],
      examplesEn: ['View reports', 'Show scouting history'],
      examplesAr: ['عرض التقارير', 'سجل الفحوصات'],
    ),

    // ─────────────────────────────────────────────────────────────────────────
    // Advisory
    // ─────────────────────────────────────────────────────────────────────────
    VoiceCommandDefinition(
      type: VoiceCommandType.getAdvice,
      nameEn: 'Get Advice',
      nameAr: 'احصل على نصيحة',
      descriptionEn: 'Get farming advice',
      descriptionAr: 'الحصول على نصيحة زراعية',
      patternsEn: ['get advice', 'need advice', 'farming tip', 'what should i do', 'recommend'],
      patternsAr: ['اعطني نصيحة', 'احتاج نصيحة', 'ايش اسوي', 'شو توصي', 'نصيحة'],
      examplesEn: ['I need farming advice', 'What should I do'],
      examplesAr: ['أحتاج نصيحة', 'إيش أسوي'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.askQuestion,
      nameEn: 'Ask Question',
      nameAr: 'اسأل سؤال',
      descriptionEn: 'Ask a question to the advisor',
      descriptionAr: 'طرح سؤال على المستشار',
      patternsEn: ['ask question', 'i have a question', 'can you help', 'help me with'],
      patternsAr: ['عندي سؤال', 'اسأل', 'ساعدني', 'محتاج مساعدة'],
      examplesEn: ['I have a question', 'Can you help me'],
      examplesAr: ['عندي سؤال', 'ساعدني'],
    ),

    // ─────────────────────────────────────────────────────────────────────────
    // Utility Commands
    // ─────────────────────────────────────────────────────────────────────────
    VoiceCommandDefinition(
      type: VoiceCommandType.help,
      nameEn: 'Help',
      nameAr: 'مساعدة',
      descriptionEn: 'Show voice command help',
      descriptionAr: 'عرض مساعدة الأوامر الصوتية',
      patternsEn: ['help', 'help me', 'what can you do', 'voice commands', 'what can i say'],
      patternsAr: ['مساعدة', 'ساعدني', 'شو اقدر اقول', 'الأوامر الصوتية', 'كيف استخدم'],
      examplesEn: ['Help', 'What can I say'],
      examplesAr: ['مساعدة', 'شو أقدر أقول'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.cancel,
      nameEn: 'Cancel',
      nameAr: 'إلغاء',
      descriptionEn: 'Cancel current operation',
      descriptionAr: 'إلغاء العملية الحالية',
      patternsEn: ['cancel', 'stop', 'never mind', 'forget it', 'abort'],
      patternsAr: ['الغاء', 'الغي', 'توقف', 'خلاص', 'بلا'],
      examplesEn: ['Cancel', 'Stop'],
      examplesAr: ['إلغاء', 'توقف'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.repeat,
      nameEn: 'Repeat',
      nameAr: 'كرر',
      descriptionEn: 'Repeat last response',
      descriptionAr: 'تكرار الرد الأخير',
      patternsEn: ['repeat', 'say again', 'what did you say', 'come again'],
      patternsAr: ['كرر', 'اعد', 'شو قلت', 'مرة ثانية'],
      examplesEn: ['Repeat that', 'Say again'],
      examplesAr: ['كرر', 'أعد مرة ثانية'],
    ),

    VoiceCommandDefinition(
      type: VoiceCommandType.dailySummary,
      nameEn: 'Daily Summary',
      nameAr: 'ملخص اليوم',
      descriptionEn: 'Get daily farm summary',
      descriptionAr: 'الحصول على ملخص المزرعة اليومي',
      patternsEn: ['daily summary', 'today summary', 'whats happening', 'farm status', 'morning briefing'],
      patternsAr: ['ملخص اليوم', 'تقرير اليوم', 'شو صار', 'حالة المزرعة', 'احداث اليوم'],
      examplesEn: ['Give me daily summary', 'Farm status'],
      examplesAr: ['ملخص اليوم', 'شو صار اليوم'],
    ),
  ];

  /// Get command by type
  static VoiceCommandDefinition? getCommand(VoiceCommandType type) {
    try {
      return commands.firstWhere((c) => c.type == type);
    } catch (_) {
      return null;
    }
  }

  /// Get commands by category
  static List<VoiceCommandDefinition> getCommandsByCategory(String category) {
    return commands.where((c) => c.type.categoryEn == category).toList();
  }

  /// Get all categories
  static List<String> getCategories() {
    return commands.map((c) => c.type.categoryEn).toSet().toList();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Command Parser with Fuzzy Matching
// ═══════════════════════════════════════════════════════════════════════════

class VoiceCommandParser {
  static const double _matchThreshold = 0.6;

  /// Parse raw text into a command
  static ParsedVoiceCommand parse(String text) {
    if (text.isEmpty) {
      return ParsedVoiceCommand(
        type: VoiceCommandType.unknown,
        rawText: text,
        confidence: 0,
        isArabic: false,
        timestamp: DateTime.now(),
      );
    }

    final isArabic = _containsArabic(text);
    final normalizedText = isArabic ? _normalizeArabic(text) : text.toLowerCase();

    AppLogger.d('Parsing voice command', tag: 'VOICE_CMD', data: {
      'text': text,
      'isArabic': isArabic,
      'normalized': normalizedText,
    });

    // Try to find best matching command
    VoiceCommandType? bestMatch;
    double bestConfidence = 0;
    String? matchedPattern;

    for (final command in VoiceCommandRegistry.commands) {
      final patterns = isArabic ? command.patternsAr : command.patternsEn;

      for (final pattern in patterns) {
        final normalizedPattern = isArabic ? _normalizeArabic(pattern) : pattern.toLowerCase();
        final similarity = _calculateSimilarity(normalizedText, normalizedPattern);

        if (similarity > bestConfidence) {
          bestConfidence = similarity;
          bestMatch = command.type;
          matchedPattern = pattern;
        }

        // Exact or near-exact match - no need to continue
        if (similarity >= 0.95) break;
      }

      if (bestConfidence >= 0.95) break;
    }

    // Apply threshold
    if (bestConfidence < _matchThreshold) {
      bestMatch = VoiceCommandType.unknown;
      bestConfidence = 0;
      matchedPattern = null;
    }

    // Extract parameters
    final parameters = bestMatch != null && bestMatch != VoiceCommandType.unknown
        ? _extractParameters(text, bestMatch, isArabic)
        : <String, dynamic>{};

    final result = ParsedVoiceCommand(
      type: bestMatch ?? VoiceCommandType.unknown,
      rawText: text,
      confidence: bestConfidence,
      parameters: parameters,
      isArabic: isArabic,
      timestamp: DateTime.now(),
      matchedPattern: matchedPattern,
    );

    AppLogger.i('Voice command parsed', tag: 'VOICE_CMD', data: {
      'type': result.type.id,
      'confidence': '${(result.confidence * 100).toStringAsFixed(1)}%',
      'params': result.parameters,
    });

    return result;
  }

  /// Check if text contains Arabic characters
  static bool _containsArabic(String text) {
    return RegExp(r'[\u0600-\u06FF]').hasMatch(text);
  }

  /// Normalize Arabic text
  static String _normalizeArabic(String text) {
    return text
        .replaceAll('أ', 'ا')
        .replaceAll('إ', 'ا')
        .replaceAll('آ', 'ا')
        .replaceAll('ة', 'ه')
        .replaceAll('ى', 'ي')
        .replaceAll(RegExp(r'[\u064B-\u065F]'), '') // Remove diacritics
        .trim();
  }

  /// Calculate similarity between two strings using fuzzy matching
  static double _calculateSimilarity(String s1, String s2) {
    // Check for exact match
    if (s1 == s2) return 1.0;

    // Check for containment
    if (s1.contains(s2)) return 0.9 + (s2.length / s1.length) * 0.1;
    if (s2.contains(s1)) return 0.85 + (s1.length / s2.length) * 0.1;

    // Word-based matching
    final words1 = s1.split(RegExp(r'\s+'));
    final words2 = s2.split(RegExp(r'\s+'));
    final matchingWords = words1.where((w) => words2.contains(w)).length;

    if (matchingWords > 0) {
      final wordMatchRatio = matchingWords / max(words1.length, words2.length);
      if (wordMatchRatio >= 0.5) return 0.6 + wordMatchRatio * 0.3;
    }

    // Levenshtein distance-based similarity
    final distance = _levenshteinDistance(s1, s2);
    final maxLen = max(s1.length, s2.length);
    if (maxLen == 0) return 1.0;

    return 1.0 - (distance / maxLen);
  }

  /// Levenshtein distance between two strings
  static int _levenshteinDistance(String s1, String s2) {
    if (s1.isEmpty) return s2.length;
    if (s2.isEmpty) return s1.length;

    final m = s1.length;
    final n = s2.length;
    final dp = List.generate(m + 1, (i) => List.filled(n + 1, 0));

    for (var i = 0; i <= m; i++) {
      dp[i][0] = i;
    }
    for (var j = 0; j <= n; j++) {
      dp[0][j] = j;
    }

    for (var i = 1; i <= m; i++) {
      for (var j = 1; j <= n; j++) {
        if (s1[i - 1] == s2[j - 1]) {
          dp[i][j] = dp[i - 1][j - 1];
        } else {
          dp[i][j] = 1 + [dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]].reduce(min);
        }
      }
    }

    return dp[m][n];
  }

  /// Extract parameters from command text
  static Map<String, dynamic> _extractParameters(
    String text,
    VoiceCommandType type,
    bool isArabic,
  ) {
    final params = <String, dynamic>{};

    // Extract field identifier
    if (_fieldCommands.contains(type)) {
      final fieldId = _extractFieldId(text, isArabic);
      if (fieldId != null) {
        params['fieldId'] = fieldId;
      }
    }

    // Extract task identifier
    if (_taskCommands.contains(type)) {
      final taskId = _extractTaskId(text, isArabic);
      if (taskId != null) {
        params['taskId'] = taskId;
      }
    }

    // Extract numeric values
    final numbers = _extractNumbers(text);
    if (numbers.isNotEmpty) {
      params['numbers'] = numbers;
    }

    return params;
  }

  static const _fieldCommands = {
    VoiceCommandType.selectField,
    VoiceCommandType.viewFieldDetails,
    VoiceCommandType.checkNDVI,
    VoiceCommandType.scheduleIrrigation,
    VoiceCommandType.recordIrrigation,
  };

  static const _taskCommands = {
    VoiceCommandType.completeTask,
  };

  /// Extract field ID from text
  static String? _extractFieldId(String text, bool isArabic) {
    // Arabic number words
    if (isArabic) {
      final arabicNumbers = {
        'الأول': '1', 'الاول': '1',
        'الثاني': '2',
        'الثالث': '3',
        'الرابع': '4',
        'الخامس': '5',
        'السادس': '6',
        'السابع': '7',
        'الثامن': '8',
        'التاسع': '9',
        'العاشر': '10',
      };

      for (final entry in arabicNumbers.entries) {
        if (text.contains(entry.key)) {
          return entry.value;
        }
      }
    }

    // Numeric extraction
    final patterns = [
      RegExp(r'(?:field|حقل)\s*(?:number|رقم)?\s*(\d+)', caseSensitive: false),
      RegExp(r'(\d+)(?:\s*(?:field|حقل))?', caseSensitive: false),
    ];

    for (final pattern in patterns) {
      final match = pattern.firstMatch(text);
      if (match != null) {
        return match.group(1);
      }
    }

    return null;
  }

  /// Extract task ID from text
  static String? _extractTaskId(String text, bool isArabic) {
    final patterns = [
      RegExp(r'(?:task|مهمة)\s*(?:number|رقم)?\s*(\d+)', caseSensitive: false),
      RegExp(r'(\d+)(?:\s*(?:task|مهمة))?', caseSensitive: false),
    ];

    for (final pattern in patterns) {
      final match = pattern.firstMatch(text);
      if (match != null) {
        return match.group(1);
      }
    }

    return null;
  }

  /// Extract all numbers from text
  static List<int> _extractNumbers(String text) {
    final matches = RegExp(r'\d+').allMatches(text);
    return matches.map((m) => int.parse(m.group(0)!)).toList();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for voice command definitions
final voiceCommandDefinitionsProvider = Provider<List<VoiceCommandDefinition>>((ref) {
  return VoiceCommandRegistry.commands;
});

/// Provider for voice command categories
final voiceCommandCategoriesProvider = Provider<List<String>>((ref) {
  return VoiceCommandRegistry.getCategories();
});

/// Provider to get commands by category
final voiceCommandsByCategoryProvider = Provider.family<List<VoiceCommandDefinition>, String>((ref, category) {
  return VoiceCommandRegistry.getCommandsByCategory(category);
});
