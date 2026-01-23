import 'models/crop_model.dart';

/// Crop Helper Utilities
/// أدوات مساعدة للمحاصيل
///
/// Provides helper functions to display crop information
class CropHelper {
  /// Static mapping of common crop codes to Arabic names (fallback)
  /// Used when crops haven't been loaded from API yet
  static const Map<String, String> _fallbackCropNamesAr = {
    // Cereals
    'WHEAT': 'قمح',
    'wheat': 'قمح',
    'BARLEY': 'شعير',
    'barley': 'شعير',
    'CORN': 'ذرة شامية',
    'corn': 'ذرة',
    'SORGHUM': 'ذرة رفيعة',
    'sorghum': 'ذرة رفيعة',
    'MILLET': 'دخن',
    'millet': 'دخن',
    'RICE': 'أرز',
    'rice': 'أرز',

    // Legumes
    'FABA_BEAN': 'فول',
    'faba_bean': 'فول',
    'LENTIL': 'عدس',
    'lentil': 'عدس',
    'CHICKPEA': 'حمص',
    'chickpea': 'حمص',
    'COWPEA': 'لوبيا',
    'cowpea': 'لوبيا',
    'GREEN_BEAN': 'فاصوليا خضراء',
    'green_bean': 'فاصوليا',
    'PEANUT': 'فول سوداني',
    'peanut': 'فول سوداني',
    'FENUGREEK': 'حلبة',
    'fenugreek': 'حلبة',

    // Vegetables
    'TOMATO': 'طماطم',
    'tomato': 'طماطم',
    'POTATO': 'بطاطس',
    'potato': 'بطاطس',
    'ONION': 'بصل',
    'onion': 'بصل',
    'GARLIC': 'ثوم',
    'garlic': 'ثوم',
    'PEPPER': 'فلفل حلو',
    'pepper': 'فلفل',
    'CHILI': 'فلفل حار',
    'chili': 'فلفل حار',
    'EGGPLANT': 'باذنجان',
    'eggplant': 'باذنجان',
    'CUCUMBER': 'خيار',
    'cucumber': 'خيار',
    'ZUCCHINI': 'كوسا',
    'zucchini': 'كوسا',
    'WATERMELON': 'بطيخ',
    'watermelon': 'بطيخ',
    'CARROT': 'جزر',
    'carrot': 'جزر',
    'CABBAGE': 'ملفوف',
    'cabbage': 'ملفوف',
    'LETTUCE': 'خس',
    'lettuce': 'خس',
    'OKRA': 'بامية',
    'okra': 'بامية',

    // Fruits
    'DATE_PALM': 'نخيل تمر',
    'date_palm': 'نخيل',
    'MANGO': 'مانجو',
    'mango': 'مانجو',
    'BANANA': 'موز',
    'banana': 'موز',
    'GRAPE': 'عنب',
    'grape': 'عنب',
    'PAPAYA': 'باباي',
    'papaya': 'باباي',
    'CITRUS_ORANGE': 'برتقال',
    'orange': 'برتقال',
    'CITRUS_LEMON': 'ليمون',
    'lemon': 'ليمون',
    'POMEGRANATE': 'رمان',
    'pomegranate': 'رمان',
    'FIG': 'تين',
    'fig': 'تين',
    'GUAVA': 'جوافة',
    'guava': 'جوافة',

    // Stimulants
    'COFFEE': 'بن يمني',
    'coffee': 'بن',
    'QAT': 'قات',
    'qat': 'قات',

    // Oilseeds
    'SESAME': 'سمسم',
    'sesame': 'سمسم',
    'SUNFLOWER': 'دوار الشمس',
    'sunflower': 'دوار الشمس',
    'SOYBEAN': 'فول الصويا',
    'soybean': 'فول الصويا',

    // Fodder
    'ALFALFA': 'برسيم حجازي',
    'alfalfa': 'برسيم',
    'CLOVER': 'برسيم مصري',
    'clover': 'برسيم',
    'RHODES_GRASS': 'جت',
    'rhodes_grass': 'جت',

    // Spices
    'CORIANDER': 'كزبرة',
    'coriander': 'كزبرة',
    'CUMIN': 'كمون',
    'cumin': 'كمون',
    'HENNA': 'حناء',
    'henna': 'حناء',
    'BASIL': 'ريحان',
    'basil': 'ريحان',

    // Fiber
    'COTTON': 'قطن',
    'cotton': 'قطن',

    // Sugar
    'SUGARCANE': 'قصب السكر',
    'sugarcane': 'قصب',

    // Generic
    'other': 'أخرى',
    'unknown': 'غير محدد',
  };

  /// Get Arabic name for a crop code
  /// If crop object is provided, use it; otherwise use fallback mapping
  static String getCropNameAr(String? cropCode, {Crop? crop}) {
    if (cropCode == null || cropCode.isEmpty) {
      return 'غير محدد';
    }

    // If crop object is provided, use its Arabic name
    if (crop != null) {
      return crop.nameAr;
    }

    // Use fallback mapping
    return _fallbackCropNamesAr[cropCode] ??
        _fallbackCropNamesAr[cropCode.toUpperCase()] ??
        cropCode;
  }

  /// Get emoji icon for crop
  static String getCropEmoji(String? cropCode) {
    if (cropCode == null || cropCode.isEmpty) return '🌱';

    final code = cropCode.toUpperCase();
    switch (code) {
      // Cereals
      case 'WHEAT':
      case 'BARLEY':
        return '🌾';
      case 'CORN':
      case 'SORGHUM':
        return '🌽';
      case 'RICE':
        return '🍚';
      case 'MILLET':
        return '🌾';

      // Legumes
      case 'FABA_BEAN':
      case 'CHICKPEA':
      case 'LENTIL':
      case 'PEANUT':
        return '🫘';
      case 'GREEN_BEAN':
      case 'COWPEA':
        return '🫛';

      // Vegetables
      case 'TOMATO':
        return '🍅';
      case 'POTATO':
        return '🥔';
      case 'ONION':
        return '🧅';
      case 'GARLIC':
        return '🧄';
      case 'PEPPER':
      case 'CHILI':
        return '🌶️';
      case 'EGGPLANT':
        return '🍆';
      case 'CUCUMBER':
        return '🥒';
      case 'ZUCCHINI':
        return '🥬';
      case 'WATERMELON':
        return '🍉';
      case 'CARROT':
        return '🥕';
      case 'CABBAGE':
      case 'LETTUCE':
        return '🥬';
      case 'OKRA':
        return '🫑';

      // Fruits
      case 'DATE_PALM':
        return '🌴';
      case 'MANGO':
        return '🥭';
      case 'BANANA':
        return '🍌';
      case 'GRAPE':
        return '🍇';
      case 'PAPAYA':
        return '🍈';
      case 'CITRUS_ORANGE':
        return '🍊';
      case 'CITRUS_LEMON':
        return '🍋';
      case 'POMEGRANATE':
        return '🍎';
      case 'FIG':
        return '🫐';
      case 'GUAVA':
        return '🍑';

      // Stimulants
      case 'COFFEE':
        return '☕';
      case 'QAT':
        return '🌿';

      // Oilseeds
      case 'SESAME':
      case 'SUNFLOWER':
      case 'SOYBEAN':
        return '🌻';

      // Fodder
      case 'ALFALFA':
      case 'CLOVER':
      case 'RHODES_GRASS':
        return '🌿';

      // Spices
      case 'CORIANDER':
      case 'CUMIN':
      case 'BASIL':
        return '🌿';
      case 'HENNA':
        return '🍃';

      // Fiber
      case 'COTTON':
        return '🌸';

      // Sugar
      case 'SUGARCANE':
        return '🎋';

      default:
        return '🌱';
    }
  }

  /// Get color for crop category
  static String getCategoryColor(CropCategory category) {
    switch (category) {
      case CropCategory.cereals:
        return '#F4A460'; // Sandy brown
      case CropCategory.legumes:
        return '#8B4513'; // Saddle brown
      case CropCategory.vegetables:
        return '#228B22'; // Forest green
      case CropCategory.fruits:
        return '#FF6347'; // Tomato
      case CropCategory.oilseeds:
        return '#FFD700'; // Gold
      case CropCategory.fiber:
        return '#E0E0E0'; // Light gray
      case CropCategory.sugar:
        return '#DEB887'; // Burlywood
      case CropCategory.stimulants:
        return '#8B4513'; // Saddle brown
      case CropCategory.spices:
        return '#2E8B57'; // Sea green
      case CropCategory.fodder:
        return '#90EE90'; // Light green
      case CropCategory.tubers:
        return '#CD853F'; // Peru
    }
  }
}
