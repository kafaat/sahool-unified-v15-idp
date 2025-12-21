/// جميع محافظات اليمن الـ 22
/// All 22 Yemen Governorates with geographic data
library;

/// Yemen Governorate data model
class YemenGovernorate {
  final String id;
  final String nameAr;
  final String nameEn;
  final double latitude;
  final double longitude;
  final int elevation; // meters
  final String region; // highland, coastal, desert, island

  const YemenGovernorate({
    required this.id,
    required this.nameAr,
    required this.nameEn,
    required this.latitude,
    required this.longitude,
    required this.elevation,
    required this.region,
  });

  /// Get display name based on locale
  String getName(String locale) {
    return locale == 'ar' ? nameAr : nameEn;
  }
}

/// Region types for climate-based grouping
enum YemenRegion {
  highland('highland', 'المرتفعات', 'Highland'),
  coastal('coastal', 'الساحل', 'Coastal'),
  desert('desert', 'الصحراء', 'Desert'),
  island('island', 'الجزر', 'Island');

  final String id;
  final String nameAr;
  final String nameEn;

  const YemenRegion(this.id, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;
}

/// All 22 Yemen Governorates - جميع محافظات اليمن الـ 22
class YemenGovernorates {
  YemenGovernorates._();

  // المنطقة الشمالية - Northern Region
  static const sanaa = YemenGovernorate(
    id: 'sanaa',
    nameAr: 'صنعاء',
    nameEn: "Sana'a",
    latitude: 15.3694,
    longitude: 44.1910,
    elevation: 2250,
    region: 'highland',
  );

  static const amanatAlAsimah = YemenGovernorate(
    id: 'amanat_al_asimah',
    nameAr: 'أمانة العاصمة',
    nameEn: 'Amanat Al Asimah',
    latitude: 15.3556,
    longitude: 44.2067,
    elevation: 2200,
    region: 'highland',
  );

  static const amran = YemenGovernorate(
    id: 'amran',
    nameAr: 'عمران',
    nameEn: 'Amran',
    latitude: 15.6594,
    longitude: 43.9439,
    elevation: 2300,
    region: 'highland',
  );

  static const saadah = YemenGovernorate(
    id: 'saadah',
    nameAr: 'صعدة',
    nameEn: "Sa'dah",
    latitude: 16.9400,
    longitude: 43.7614,
    elevation: 1850,
    region: 'highland',
  );

  static const alJawf = YemenGovernorate(
    id: 'al_jawf',
    nameAr: 'الجوف',
    nameEn: 'Al Jawf',
    latitude: 16.5833,
    longitude: 45.5000,
    elevation: 1200,
    region: 'desert',
  );

  static const hajjah = YemenGovernorate(
    id: 'hajjah',
    nameAr: 'حجة',
    nameEn: 'Hajjah',
    latitude: 15.6917,
    longitude: 43.6028,
    elevation: 1800,
    region: 'highland',
  );

  static const alMahwit = YemenGovernorate(
    id: 'al_mahwit',
    nameAr: 'المحويت',
    nameEn: 'Al Mahwit',
    latitude: 15.4700,
    longitude: 43.5447,
    elevation: 2100,
    region: 'highland',
  );

  // المنطقة الوسطى - Central Region
  static const dhamar = YemenGovernorate(
    id: 'dhamar',
    nameAr: 'ذمار',
    nameEn: 'Dhamar',
    latitude: 14.5500,
    longitude: 44.4000,
    elevation: 2400,
    region: 'highland',
  );

  static const ibb = YemenGovernorate(
    id: 'ibb',
    nameAr: 'إب',
    nameEn: 'Ibb',
    latitude: 13.9667,
    longitude: 44.1667,
    elevation: 2050,
    region: 'highland',
  );

  static const taiz = YemenGovernorate(
    id: 'taiz',
    nameAr: 'تعز',
    nameEn: 'Taiz',
    latitude: 13.5789,
    longitude: 44.0219,
    elevation: 1400,
    region: 'highland',
  );

  static const alBayda = YemenGovernorate(
    id: 'al_bayda',
    nameAr: 'البيضاء',
    nameEn: 'Al Bayda',
    latitude: 13.9833,
    longitude: 45.5667,
    elevation: 2250,
    region: 'highland',
  );

  static const raymah = YemenGovernorate(
    id: 'raymah',
    nameAr: 'ريمة',
    nameEn: 'Raymah',
    latitude: 14.6333,
    longitude: 43.7167,
    elevation: 2600,
    region: 'highland',
  );

  static const marib = YemenGovernorate(
    id: 'marib',
    nameAr: 'مأرب',
    nameEn: 'Marib',
    latitude: 15.4667,
    longitude: 45.3333,
    elevation: 1100,
    region: 'desert',
  );

  // المنطقة الساحلية الغربية - Western Coastal Region
  static const hodeidah = YemenGovernorate(
    id: 'hodeidah',
    nameAr: 'الحديدة',
    nameEn: 'Hodeidah',
    latitude: 14.7979,
    longitude: 42.9540,
    elevation: 12,
    region: 'coastal',
  );

  // المنطقة الجنوبية - Southern Region
  static const aden = YemenGovernorate(
    id: 'aden',
    nameAr: 'عدن',
    nameEn: 'Aden',
    latitude: 12.7855,
    longitude: 45.0187,
    elevation: 6,
    region: 'coastal',
  );

  static const lahij = YemenGovernorate(
    id: 'lahij',
    nameAr: 'لحج',
    nameEn: 'Lahij',
    latitude: 13.0500,
    longitude: 44.8833,
    elevation: 150,
    region: 'highland',
  );

  static const adDali = YemenGovernorate(
    id: 'ad_dali',
    nameAr: 'الضالع',
    nameEn: "Ad Dali'",
    latitude: 13.7000,
    longitude: 44.7333,
    elevation: 1500,
    region: 'highland',
  );

  static const abyan = YemenGovernorate(
    id: 'abyan',
    nameAr: 'أبين',
    nameEn: 'Abyan',
    latitude: 13.0167,
    longitude: 45.3667,
    elevation: 50,
    region: 'coastal',
  );

  // المنطقة الشرقية - Eastern Region
  static const hadramaut = YemenGovernorate(
    id: 'hadramaut',
    nameAr: 'حضرموت',
    nameEn: 'Hadramaut',
    latitude: 15.9500,
    longitude: 48.7833,
    elevation: 650,
    region: 'desert',
  );

  static const shabwah = YemenGovernorate(
    id: 'shabwah',
    nameAr: 'شبوة',
    nameEn: 'Shabwah',
    latitude: 14.5333,
    longitude: 46.8333,
    elevation: 900,
    region: 'desert',
  );

  static const alMahrah = YemenGovernorate(
    id: 'al_mahrah',
    nameAr: 'المهرة',
    nameEn: 'Al Mahrah',
    latitude: 16.0667,
    longitude: 52.2333,
    elevation: 200,
    region: 'coastal',
  );

  // الجزر - Islands
  static const socotra = YemenGovernorate(
    id: 'socotra',
    nameAr: 'سقطرى',
    nameEn: 'Socotra',
    latitude: 12.4634,
    longitude: 53.8237,
    elevation: 250,
    region: 'island',
  );

  /// All 22 governorates list
  static const List<YemenGovernorate> all = [
    // Northern
    sanaa,
    amanatAlAsimah,
    amran,
    saadah,
    alJawf,
    hajjah,
    alMahwit,
    // Central
    dhamar,
    ibb,
    taiz,
    alBayda,
    raymah,
    marib,
    // Western Coastal
    hodeidah,
    // Southern
    aden,
    lahij,
    adDali,
    abyan,
    // Eastern
    hadramaut,
    shabwah,
    alMahrah,
    // Islands
    socotra,
  ];

  /// Get governorates by region
  static List<YemenGovernorate> byRegion(String region) {
    return all.where((g) => g.region == region).toList();
  }

  /// Highland governorates (المرتفعات)
  static List<YemenGovernorate> get highland => byRegion('highland');

  /// Coastal governorates (الساحل)
  static List<YemenGovernorate> get coastal => byRegion('coastal');

  /// Desert governorates (الصحراء)
  static List<YemenGovernorate> get desert => byRegion('desert');

  /// Island governorates (الجزر)
  static List<YemenGovernorate> get island => byRegion('island');

  /// Get governorate by ID
  static YemenGovernorate? getById(String id) {
    try {
      return all.firstWhere((g) => g.id == id);
    } catch (_) {
      return null;
    }
  }

  /// Get governorate names for dropdown (Arabic)
  static List<String> get namesAr => all.map((g) => g.nameAr).toList();

  /// Get governorate names for dropdown (English)
  static List<String> get namesEn => all.map((g) => g.nameEn).toList();

  /// Get Map of id -> nameAr for forms
  static Map<String, String> get mapIdToNameAr {
    return {for (var g in all) g.id: g.nameAr};
  }

  /// Get Map of id -> nameEn for forms
  static Map<String, String> get mapIdToNameEn {
    return {for (var g in all) g.id: g.nameEn};
  }

  /// Find nearest governorate to a given coordinate
  static YemenGovernorate findNearest(double lat, double lon) {
    YemenGovernorate nearest = all.first;
    double minDistance = double.infinity;

    for (final gov in all) {
      final distance = _calculateDistance(lat, lon, gov.latitude, gov.longitude);
      if (distance < minDistance) {
        minDistance = distance;
        nearest = gov;
      }
    }

    return nearest;
  }

  /// Calculate distance between two points (Haversine formula simplified)
  static double _calculateDistance(
    double lat1,
    double lon1,
    double lat2,
    double lon2,
  ) {
    final dLat = lat2 - lat1;
    final dLon = lon2 - lon1;
    return dLat * dLat + dLon * dLon; // Simplified for comparison only
  }
}
