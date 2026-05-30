/// Yemen governorates and districts data for farm location selection
class YemenLocations {
  YemenLocations._();

  static const List<Map<String, dynamic>> governorates = [
    {
      'name': 'صنعاء',
      'nameEn': 'Sanaa',
      'lat': 15.3694,
      'lng': 44.1910,
      'districts': ['صنعاء المدينة', 'بني حشيش', 'خولان', 'سنحان', 'حمدان', 'بيت بوس'],
    },
    {
      'name': 'عدن',
      'nameEn': 'Aden',
      'lat': 12.8297,
      'lng': 45.0365,
      'districts': ['المعلا', 'خور مكسر', 'كريتر', 'التواهي', 'دار سعد', 'المنصورة'],
    },
    {
      'name': 'تعز',
      'nameEn': 'Taiz',
      'lat': 13.5785,
      'lng': 44.0177,
      'districts': ['تعز المدينة', 'التربة', 'الشمايتين', 'الجبل', 'موزع', 'الحوبان'],
    },
    {
      'name': 'حضرموت',
      'nameEn': 'Hadramawt',
      'lat': 15.9310,
      'lng': 48.5186,
      'districts': ['المكلا', 'الشحر', 'سيئون', 'تريم', 'قسم', 'الديس'],
    },
    {
      'name': 'الحديدة',
      'nameEn': 'Hudaydah',
      'lat': 14.7978,
      'lng': 42.9545,
      'districts': ['الحديدة', 'الدريهمي', 'باجل', 'زبيد', 'المراوعة', 'بيت الفقيه'],
    },
    {
      'name': 'إب',
      'nameEn': 'Ibb',
      'lat': 13.9813,
      'lng': 44.1776,
      'districts': ['إب المدينة', 'السبرة', 'يريم', 'ضوران آنس', 'المقاطرة'],
    },
    {
      'name': 'ذمار',
      'nameEn': 'Dhamar',
      'lat': 14.5434,
      'lng': 44.4022,
      'districts': ['ذمار المدينة', 'مغرب عنس', 'حبابة', 'الحداء', 'وصاب'],
    },
    {
      'name': 'المحويت',
      'nameEn': 'Mahwit',
      'lat': 15.4616,
      'lng': 43.5465,
      'districts': ['المحويت', 'ملحان', 'رجال ألمع', 'بني سعد', 'الطفة'],
    },
    {
      'name': 'ريمة',
      'nameEn': 'Raymah',
      'lat': 14.6597,
      'lng': 43.7101,
      'districts': ['كسمة', 'الجبين', 'الجعفرية', 'بلاد الطعام'],
    },
    {
      'name': 'البيضاء',
      'nameEn': 'Al Bayda',
      'lat': 14.0022,
      'lng': 45.5723,
      'districts': ['البيضاء', 'القريشية', 'رداع', 'الصومعة', 'السومة', 'ناطع'],
    },
    {
      'name': 'مأرب',
      'nameEn': 'Marib',
      'lat': 15.4706,
      'lng': 45.3243,
      'districts': ['مأرب المدينة', 'مأرب', 'حريب', 'الجوبة', 'رغوان'],
    },
    {
      'name': 'الجوف',
      'nameEn': 'Al Jawf',
      'lat': 16.3390,
      'lng': 45.5045,
      'districts': ['الحزم', 'الغيل', 'المتون', 'خب والشعف', 'المسلوب'],
    },
  ];

  /// Get districts for a given governorate name
  static List<String> getDistricts(String governorateName) {
    final gov = governorates.firstWhere(
      (g) => g['name'] == governorateName,
      orElse: () => <String, dynamic>{},
    );
    final districts = gov['districts'];
    if (districts is List) {
      return List<String>.from(districts);
    }
    return [];
  }

  /// Get center coordinates for a governorate
  static Map<String, double>? getCenter(String governorateName) {
    final gov = governorates.firstWhere(
      (g) => g['name'] == governorateName,
      orElse: () => <String, dynamic>{},
    );
    if (gov.isEmpty) return null;
    return {
      'lat': (gov['lat'] as num).toDouble(),
      'lng': (gov['lng'] as num).toDouble(),
    };
  }
}
