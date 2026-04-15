import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/crops/data/crop_helper.dart';
import 'package:sahool_field_app/features/crops/data/models/crop_model.dart';

void main() {
  group('CropHelper.getCropNameAr', () {
    test('returns غير محدد for null code', () {
      expect(CropHelper.getCropNameAr(null), 'غير محدد');
    });

    test('returns غير محدد for empty code', () {
      expect(CropHelper.getCropNameAr(''), 'غير محدد');
    });

    test('returns Arabic name from fallback mapping (lowercase)', () {
      expect(CropHelper.getCropNameAr('wheat'), 'قمح');
      expect(CropHelper.getCropNameAr('tomato'), 'طماطم');
      expect(CropHelper.getCropNameAr('coffee'), 'بن');
      expect(CropHelper.getCropNameAr('onion'), 'بصل');
    });

    test('returns Arabic name from fallback mapping (uppercase)', () {
      expect(CropHelper.getCropNameAr('WHEAT'), 'قمح');
      expect(CropHelper.getCropNameAr('TOMATO'), 'طماطم');
      expect(CropHelper.getCropNameAr('COFFEE'), 'بن يمني');
    });

    test('returns crop.nameAr when crop object is provided', () {
      const crop = Crop(
        code: 'CUSTOM', nameEn: 'Custom', nameAr: 'مخصص',
        scientificName: 'Test sp.', category: CropCategory.vegetables,
        growthHabit: GrowthHabit.annual, growingSeasonDays: 60,
        optimalTempMin: 15, optimalTempMax: 30,
        waterRequirement: WaterRequirement.medium, baseYieldTonHa: 2,
      );
      expect(CropHelper.getCropNameAr('CUSTOM', crop: crop), 'مخصص');
    });

    test('returns code itself for unknown crop', () {
      expect(CropHelper.getCropNameAr('UNKNOWN_CROP'), 'UNKNOWN_CROP');
    });

    test('covers cereals mapping', () {
      expect(CropHelper.getCropNameAr('barley'), 'شعير');
      expect(CropHelper.getCropNameAr('sorghum'), 'ذرة رفيعة');
      expect(CropHelper.getCropNameAr('rice'), 'أرز');
      expect(CropHelper.getCropNameAr('millet'), 'دخن');
    });

    test('covers legumes mapping', () {
      expect(CropHelper.getCropNameAr('faba_bean'), 'فول');
      expect(CropHelper.getCropNameAr('lentil'), 'عدس');
      expect(CropHelper.getCropNameAr('chickpea'), 'حمص');
    });

    test('covers fruits mapping', () {
      expect(CropHelper.getCropNameAr('date_palm'), 'نخيل');
      expect(CropHelper.getCropNameAr('mango'), 'مانجو');
      expect(CropHelper.getCropNameAr('banana'), 'موز');
      expect(CropHelper.getCropNameAr('grape'), 'عنب');
    });

    test('covers vegetables mapping', () {
      expect(CropHelper.getCropNameAr('potato'), 'بطاطس');
      expect(CropHelper.getCropNameAr('garlic'), 'ثوم');
      expect(CropHelper.getCropNameAr('cucumber'), 'خيار');
      expect(CropHelper.getCropNameAr('eggplant'), 'باذنجان');
      expect(CropHelper.getCropNameAr('okra'), 'بامية');
    });
  });

  group('CropHelper.getCropEmoji', () {
    test('returns default emoji for null/empty', () {
      expect(CropHelper.getCropEmoji(null), '🌱');
      expect(CropHelper.getCropEmoji(''), '🌱');
    });

    test('returns correct emojis for cereals', () {
      expect(CropHelper.getCropEmoji('WHEAT'), '🌾');
      expect(CropHelper.getCropEmoji('BARLEY'), '🌾');
      expect(CropHelper.getCropEmoji('CORN'), '🌽');
      expect(CropHelper.getCropEmoji('RICE'), '🍚');
    });

    test('returns correct emojis for vegetables', () {
      expect(CropHelper.getCropEmoji('TOMATO'), '🍅');
      expect(CropHelper.getCropEmoji('POTATO'), '🥔');
      expect(CropHelper.getCropEmoji('ONION'), '🧅');
      expect(CropHelper.getCropEmoji('GARLIC'), '🧄');
      expect(CropHelper.getCropEmoji('EGGPLANT'), '🍆');
      expect(CropHelper.getCropEmoji('CUCUMBER'), '🥒');
      expect(CropHelper.getCropEmoji('CARROT'), '🥕');
      expect(CropHelper.getCropEmoji('WATERMELON'), '🍉');
    });

    test('returns correct emojis for fruits', () {
      expect(CropHelper.getCropEmoji('DATE_PALM'), '🌴');
      expect(CropHelper.getCropEmoji('MANGO'), '🥭');
      expect(CropHelper.getCropEmoji('BANANA'), '🍌');
      expect(CropHelper.getCropEmoji('GRAPE'), '🍇');
      expect(CropHelper.getCropEmoji('CITRUS_ORANGE'), '🍊');
      expect(CropHelper.getCropEmoji('CITRUS_LEMON'), '🍋');
    });

    test('returns correct emojis for stimulants', () {
      expect(CropHelper.getCropEmoji('COFFEE'), '☕');
      expect(CropHelper.getCropEmoji('QAT'), '🌿');
    });

    test('is case insensitive (uppercases internally)', () {
      expect(CropHelper.getCropEmoji('wheat'), '🌾');
      expect(CropHelper.getCropEmoji('Tomato'), '🍅');
    });

    test('returns default for unknown crops', () {
      expect(CropHelper.getCropEmoji('ALIEN_PLANT'), '🌱');
    });
  });

  group('CropHelper.getCategoryColor', () {
    test('returns color for all categories', () {
      for (final category in CropCategory.values) {
        final color = CropHelper.getCategoryColor(category);
        expect(color, startsWith('#'), reason: '${category.name} should return hex color');
        expect(color.length, 7, reason: '${category.name} color should be #RRGGBB');
      }
    });

    test('returns distinct colors for major categories', () {
      final cereals = CropHelper.getCategoryColor(CropCategory.cereals);
      final vegetables = CropHelper.getCategoryColor(CropCategory.vegetables);
      final fruits = CropHelper.getCategoryColor(CropCategory.fruits);
      expect(cereals, isNot(vegetables));
      expect(vegetables, isNot(fruits));
    });

    test('specific color values', () {
      expect(CropHelper.getCategoryColor(CropCategory.cereals), '#F4A460');
      expect(CropHelper.getCategoryColor(CropCategory.vegetables), '#228B22');
      expect(CropHelper.getCategoryColor(CropCategory.fruits), '#FF6347');
    });
  });
}
