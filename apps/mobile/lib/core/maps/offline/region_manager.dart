import 'dart:async';

import 'tile_downloader.dart';
import 'tile_storage.dart';

/// Region Manager - مدير مناطق الخريطة
///
/// Features:
/// - Predefined Yemen governorates - محافظات اليمن المعرفة مسبقاً
/// - Custom region selection - اختيار منطقة مخصصة
/// - Region metadata management - إدارة بيانات المناطق
/// - Download coordination - تنسيق التحميل
class RegionManager {
  final TileStorage _storage;
  final TileDownloader _downloader;

  // Active downloads tracking
  final Map<String, StreamSubscription<DownloadProgress>> _activeDownloads = {};

  RegionManager({
    TileStorage? storage,
    TileDownloader? downloader,
  })  : _storage = storage ?? TileStorage(),
        _downloader = downloader ?? TileDownloader();

  /// Get all predefined regions - الحصول على كل المناطق المعرفة
  List<MapRegion> get predefinedRegions => YemenRegions.all;

  /// Get regions by category - الحصول على المناطق حسب الفئة
  List<MapRegion> getRegionsByCategory(RegionCategory category) {
    return YemenRegions.all.where((r) => r.category == category).toList();
  }

  /// Get region by ID - الحصول على منطقة بالمعرف
  MapRegion? getRegionById(String id) {
    try {
      return YemenRegions.all.firstWhere((r) => r.id == id);
    } catch (_) {
      return null;
    }
  }

  /// Get downloaded regions - الحصول على المناطق المحملة
  Future<List<DownloadedRegion>> getDownloadedRegions() async {
    return _storage.getAllRegionsMetadata();
  }

  /// Check if region is downloaded - التحقق من تحميل المنطقة
  Future<bool> isRegionDownloaded(String regionId) async {
    final regions = await _storage.getDownloadedRegionIds();
    return regions.contains(regionId);
  }

  /// Get download estimate for a region - تقدير تحميل منطقة
  DownloadEstimate getDownloadEstimate({
    required MapRegion region,
    int minZoom = 10,
    int maxZoom = 16,
  }) {
    return _downloader.estimateDownloadSize(
      bounds: region.bounds,
      minZoom: minZoom,
      maxZoom: maxZoom,
    );
  }

  /// Start downloading a region - بدء تحميل منطقة
  Future<DownloadResult> downloadRegion({
    required MapRegion region,
    int minZoom = 10,
    int maxZoom = 16,
    void Function(DownloadProgress)? onProgress,
  }) async {
    // Get storage path
    final storePath = await _storage.getRegionPath(region.id);

    // Save initial metadata
    await _storage.saveRegionMetadata(DownloadedRegion(
      id: region.id,
      nameAr: region.nameAr,
      nameEn: region.nameEn,
      bounds: region.bounds,
      minZoom: minZoom,
      maxZoom: maxZoom,
      downloadedAt: DateTime.now(),
      tileCount: 0,
      sizeBytes: 0,
      status: DownloadStatus.downloading,
    ));

    // Start download
    final result = await _downloader.downloadRegion(
      bounds: region.bounds,
      storePath: storePath,
      minZoom: minZoom,
      maxZoom: maxZoom,
      onProgress: onProgress,
    );

    // Update metadata with final stats
    final size = await _storage.getRegionSize(region.id);
    final tileCount = await _storage.getRegionTileCount(region.id);

    await _storage.saveRegionMetadata(DownloadedRegion(
      id: region.id,
      nameAr: region.nameAr,
      nameEn: region.nameEn,
      bounds: region.bounds,
      minZoom: minZoom,
      maxZoom: maxZoom,
      downloadedAt: DateTime.now(),
      tileCount: tileCount,
      sizeBytes: size,
      status: result.isSuccess ? DownloadStatus.completed : DownloadStatus.failed,
    ));

    return result;
  }

  /// Download custom region - تحميل منطقة مخصصة
  Future<DownloadResult> downloadCustomRegion({
    required String id,
    required String nameAr,
    required String nameEn,
    required RegionBounds bounds,
    int minZoom = 10,
    int maxZoom = 16,
    void Function(DownloadProgress)? onProgress,
  }) async {
    final region = MapRegion(
      id: id,
      nameAr: nameAr,
      nameEn: nameEn,
      bounds: bounds,
      category: RegionCategory.custom,
      iconName: 'location_on',
    );

    return downloadRegion(
      region: region,
      minZoom: minZoom,
      maxZoom: maxZoom,
      onProgress: onProgress,
    );
  }

  /// Pause download - إيقاف التحميل مؤقتاً
  void pauseDownload() {
    _downloader.pause();
  }

  /// Resume download - استمرار التحميل
  void resumeDownload() {
    _downloader.resume();
  }

  /// Cancel download - إلغاء التحميل
  void cancelDownload() {
    _downloader.cancel();
  }

  /// Delete a downloaded region - حذف منطقة محملة
  Future<bool> deleteRegion(String regionId) async {
    final success = await _storage.deleteRegion(regionId);
    if (success) {
      await _storage.deleteRegionMetadata(regionId);
    }
    return success;
  }

  /// Get storage statistics - إحصائيات التخزين
  Future<StorageStats> getStorageStats() async {
    return _storage.getStorageStats();
  }

  /// Cleanup expired tiles - تنظيف البلاطات المنتهية
  Future<CleanupResult> cleanupExpiredTiles({int expirationDays = 30}) async {
    return _storage.cleanupExpiredTiles(expirationDays: expirationDays);
  }

  /// Get download progress stream - الحصول على مجرى تقدم التحميل
  Stream<DownloadProgress> get downloadProgressStream =>
      _downloader.progressStream;

  /// Dispose resources - تحرير الموارد
  void dispose() {
    for (final subscription in _activeDownloads.values) {
      subscription.cancel();
    }
    _activeDownloads.clear();
    _downloader.dispose();
  }
}

/// Map region definition - تعريف منطقة الخريطة
class MapRegion {
  final String id;
  final String nameAr;
  final String nameEn;
  final RegionBounds bounds;
  final RegionCategory category;
  final String iconName;
  final String? description;
  final String? descriptionAr;

  const MapRegion({
    required this.id,
    required this.nameAr,
    required this.nameEn,
    required this.bounds,
    required this.category,
    required this.iconName,
    this.description,
    this.descriptionAr,
  });

  /// Get name based on locale - الاسم حسب اللغة
  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  /// Get description based on locale - الوصف حسب اللغة
  String? getDescription(String locale) =>
      locale == 'ar' ? descriptionAr : description;

  /// Center point - النقطة المركزية
  ({double lat, double lng}) get center => (
        lat: bounds.centerLat,
        lng: bounds.centerLng,
      );

  @override
  String toString() => 'MapRegion($id: $nameEn)';
}

/// Region category - فئة المنطقة
enum RegionCategory {
  highland('highland', 'المرتفعات', 'Highland'),
  coastal('coastal', 'الساحل', 'Coastal'),
  desert('desert', 'الصحراء', 'Desert'),
  island('island', 'الجزر', 'Islands'),
  custom('custom', 'مخصصة', 'Custom');

  final String id;
  final String nameAr;
  final String nameEn;

  const RegionCategory(this.id, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;
}

/// Yemen Regions - مناطق اليمن
///
/// All 22 governorates with accurate geographic bounds
class YemenRegions {
  YemenRegions._();

  // ═══════════════════════════════════════════════════════════════════════════
  // المنطقة الشمالية - Northern Region (Highland)
  // ═══════════════════════════════════════════════════════════════════════════

  /// صنعاء - Sana'a (Capital Governorate)
  static const sanaa = MapRegion(
    id: 'sanaa',
    nameAr: 'صنعاء',
    nameEn: "Sana'a",
    bounds: RegionBounds(
      south: 15.20,
      west: 43.90,
      north: 15.60,
      east: 44.40,
    ),
    category: RegionCategory.highland,
    iconName: 'location_city',
    description: 'Capital region with central highlands',
    descriptionAr: 'منطقة العاصمة في المرتفعات الوسطى',
  );

  /// أمانة العاصمة - Amanat Al Asimah (Sana'a City)
  static const amanatAlAsimah = MapRegion(
    id: 'amanat_al_asimah',
    nameAr: 'أمانة العاصمة',
    nameEn: 'Amanat Al Asimah',
    bounds: RegionBounds(
      south: 15.30,
      west: 44.10,
      north: 15.45,
      east: 44.30,
    ),
    category: RegionCategory.highland,
    iconName: 'apartment',
    description: 'Sana\'a city metropolitan area',
    descriptionAr: 'منطقة مدينة صنعاء الحضرية',
  );

  /// عمران - Amran
  static const amran = MapRegion(
    id: 'amran',
    nameAr: 'عمران',
    nameEn: 'Amran',
    bounds: RegionBounds(
      south: 15.50,
      west: 43.70,
      north: 15.90,
      east: 44.20,
    ),
    category: RegionCategory.highland,
    iconName: 'terrain',
    description: 'Highland governorate north of Sana\'a',
    descriptionAr: 'محافظة جبلية شمال صنعاء',
  );

  /// صعدة - Sa'dah
  static const saadah = MapRegion(
    id: 'saadah',
    nameAr: 'صعدة',
    nameEn: "Sa'dah",
    bounds: RegionBounds(
      south: 16.70,
      west: 43.50,
      north: 17.20,
      east: 44.10,
    ),
    category: RegionCategory.highland,
    iconName: 'landscape',
    description: 'Northern highland region',
    descriptionAr: 'المنطقة الشمالية الجبلية',
  );

  /// الجوف - Al Jawf
  static const alJawf = MapRegion(
    id: 'al_jawf',
    nameAr: 'الجوف',
    nameEn: 'Al Jawf',
    bounds: RegionBounds(
      south: 16.20,
      west: 45.00,
      north: 16.90,
      east: 46.00,
    ),
    category: RegionCategory.desert,
    iconName: 'wb_sunny',
    description: 'Desert region in the northeast',
    descriptionAr: 'منطقة صحراوية في الشمال الشرقي',
  );

  /// حجة - Hajjah
  static const hajjah = MapRegion(
    id: 'hajjah',
    nameAr: 'حجة',
    nameEn: 'Hajjah',
    bounds: RegionBounds(
      south: 15.45,
      west: 43.30,
      north: 15.95,
      east: 43.85,
    ),
    category: RegionCategory.highland,
    iconName: 'terrain',
    description: 'Western highland governorate',
    descriptionAr: 'محافظة المرتفعات الغربية',
  );

  /// المحويت - Al Mahwit
  static const alMahwit = MapRegion(
    id: 'al_mahwit',
    nameAr: 'المحويت',
    nameEn: 'Al Mahwit',
    bounds: RegionBounds(
      south: 15.25,
      west: 43.30,
      north: 15.65,
      east: 43.75,
    ),
    category: RegionCategory.highland,
    iconName: 'terrain',
    description: 'Highland coffee-growing region',
    descriptionAr: 'منطقة جبلية لزراعة البن',
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // المنطقة الوسطى - Central Region
  // ═══════════════════════════════════════════════════════════════════════════

  /// ذمار - Dhamar
  static const dhamar = MapRegion(
    id: 'dhamar',
    nameAr: 'ذمار',
    nameEn: 'Dhamar',
    bounds: RegionBounds(
      south: 14.35,
      west: 44.15,
      north: 14.75,
      east: 44.65,
    ),
    category: RegionCategory.highland,
    iconName: 'agriculture',
    description: 'Major agricultural highland region',
    descriptionAr: 'منطقة زراعية جبلية رئيسية',
  );

  /// إب - Ibb
  static const ibb = MapRegion(
    id: 'ibb',
    nameAr: 'إب',
    nameEn: 'Ibb',
    bounds: RegionBounds(
      south: 13.75,
      west: 43.90,
      north: 14.20,
      east: 44.40,
    ),
    category: RegionCategory.highland,
    iconName: 'park',
    description: 'Green highlands - most fertile region',
    descriptionAr: 'المرتفعات الخضراء - أخصب منطقة',
  );

  /// تعز - Taiz
  static const taiz = MapRegion(
    id: 'taiz',
    nameAr: 'تعز',
    nameEn: 'Taiz',
    bounds: RegionBounds(
      south: 13.35,
      west: 43.75,
      north: 13.85,
      east: 44.25,
    ),
    category: RegionCategory.highland,
    iconName: 'location_city',
    description: 'Third largest city, highland region',
    descriptionAr: 'ثالث أكبر مدينة، منطقة جبلية',
  );

  /// البيضاء - Al Bayda
  static const alBayda = MapRegion(
    id: 'al_bayda',
    nameAr: 'البيضاء',
    nameEn: 'Al Bayda',
    bounds: RegionBounds(
      south: 13.75,
      west: 45.30,
      north: 14.25,
      east: 45.85,
    ),
    category: RegionCategory.highland,
    iconName: 'terrain',
    description: 'Central highland governorate',
    descriptionAr: 'محافظة المرتفعات الوسطى',
  );

  /// ريمة - Raymah
  static const raymah = MapRegion(
    id: 'raymah',
    nameAr: 'ريمة',
    nameEn: 'Raymah',
    bounds: RegionBounds(
      south: 14.40,
      west: 43.45,
      north: 14.85,
      east: 43.95,
    ),
    category: RegionCategory.highland,
    iconName: 'forest',
    description: 'Highest rainfall region in Yemen',
    descriptionAr: 'أعلى نسبة هطول أمطار في اليمن',
  );

  /// مأرب - Marib
  static const marib = MapRegion(
    id: 'marib',
    nameAr: 'مأرب',
    nameEn: 'Marib',
    bounds: RegionBounds(
      south: 15.20,
      west: 45.00,
      north: 15.70,
      east: 45.65,
    ),
    category: RegionCategory.desert,
    iconName: 'wb_sunny',
    description: 'Historic region with ancient dam',
    descriptionAr: 'منطقة تاريخية مع السد القديم',
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // المنطقة الساحلية الغربية - Western Coastal Region
  // ═══════════════════════════════════════════════════════════════════════════

  /// الحديدة - Hodeidah
  static const hodeidah = MapRegion(
    id: 'hodeidah',
    nameAr: 'الحديدة',
    nameEn: 'Hodeidah',
    bounds: RegionBounds(
      south: 14.55,
      west: 42.70,
      north: 15.05,
      east: 43.20,
    ),
    category: RegionCategory.coastal,
    iconName: 'waves',
    description: 'Major Red Sea port city',
    descriptionAr: 'ميناء البحر الأحمر الرئيسي',
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // المنطقة الجنوبية - Southern Region
  // ═══════════════════════════════════════════════════════════════════════════

  /// عدن - Aden
  static const aden = MapRegion(
    id: 'aden',
    nameAr: 'عدن',
    nameEn: 'Aden',
    bounds: RegionBounds(
      south: 12.70,
      west: 44.85,
      north: 12.90,
      east: 45.15,
    ),
    category: RegionCategory.coastal,
    iconName: 'anchor',
    description: 'Major southern port city',
    descriptionAr: 'ميناء الجنوب الرئيسي',
  );

  /// لحج - Lahij
  static const lahij = MapRegion(
    id: 'lahij',
    nameAr: 'لحج',
    nameEn: 'Lahij',
    bounds: RegionBounds(
      south: 12.85,
      west: 44.60,
      north: 13.25,
      east: 45.10,
    ),
    category: RegionCategory.highland,
    iconName: 'agriculture',
    description: 'Agricultural region near Aden',
    descriptionAr: 'منطقة زراعية قرب عدن',
  );

  /// الضالع - Ad Dali'
  static const adDali = MapRegion(
    id: 'ad_dali',
    nameAr: 'الضالع',
    nameEn: "Ad Dali'",
    bounds: RegionBounds(
      south: 13.45,
      west: 44.50,
      north: 13.95,
      east: 44.95,
    ),
    category: RegionCategory.highland,
    iconName: 'terrain',
    description: 'Southern highland governorate',
    descriptionAr: 'محافظة المرتفعات الجنوبية',
  );

  /// أبين - Abyan
  static const abyan = MapRegion(
    id: 'abyan',
    nameAr: 'أبين',
    nameEn: 'Abyan',
    bounds: RegionBounds(
      south: 12.80,
      west: 45.15,
      north: 13.35,
      east: 45.65,
    ),
    category: RegionCategory.coastal,
    iconName: 'beach_access',
    description: 'Southern coastal governorate',
    descriptionAr: 'محافظة الساحل الجنوبي',
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // المنطقة الشرقية - Eastern Region
  // ═══════════════════════════════════════════════════════════════════════════

  /// حضرموت - Hadramaut
  static const hadramaut = MapRegion(
    id: 'hadramaut',
    nameAr: 'حضرموت',
    nameEn: 'Hadramaut',
    bounds: RegionBounds(
      south: 15.65,
      west: 48.40,
      north: 16.25,
      east: 49.10,
    ),
    category: RegionCategory.desert,
    iconName: 'wb_sunny',
    description: 'Largest governorate - historic valley',
    descriptionAr: 'أكبر محافظة - الوادي التاريخي',
  );

  /// شبوة - Shabwah
  static const shabwah = MapRegion(
    id: 'shabwah',
    nameAr: 'شبوة',
    nameEn: 'Shabwah',
    bounds: RegionBounds(
      south: 14.25,
      west: 46.55,
      north: 14.80,
      east: 47.10,
    ),
    category: RegionCategory.desert,
    iconName: 'terrain',
    description: 'Desert region with oil production',
    descriptionAr: 'منطقة صحراوية مع إنتاج النفط',
  );

  /// المهرة - Al Mahrah
  static const alMahrah = MapRegion(
    id: 'al_mahrah',
    nameAr: 'المهرة',
    nameEn: 'Al Mahrah',
    bounds: RegionBounds(
      south: 15.80,
      west: 51.90,
      north: 16.35,
      east: 52.55,
    ),
    category: RegionCategory.coastal,
    iconName: 'water',
    description: 'Easternmost governorate on Arabian Sea',
    descriptionAr: 'المحافظة الشرقية على بحر العرب',
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // الجزر - Islands
  // ═══════════════════════════════════════════════════════════════════════════

  /// سقطرى - Socotra
  static const socotra = MapRegion(
    id: 'socotra',
    nameAr: 'سقطرى',
    nameEn: 'Socotra',
    bounds: RegionBounds(
      south: 12.35,
      west: 53.50,
      north: 12.65,
      east: 54.15,
    ),
    category: RegionCategory.island,
    iconName: 'island',
    description: 'UNESCO World Heritage island',
    descriptionAr: 'جزيرة تراث عالمي لليونسكو',
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // All Regions - كل المناطق
  // ═══════════════════════════════════════════════════════════════════════════

  /// All 22 governorates - كل المحافظات الـ 22
  static const List<MapRegion> all = [
    // Northern Highland
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

  /// Highland regions - المناطق الجبلية
  static List<MapRegion> get highland =>
      all.where((r) => r.category == RegionCategory.highland).toList();

  /// Coastal regions - المناطق الساحلية
  static List<MapRegion> get coastal =>
      all.where((r) => r.category == RegionCategory.coastal).toList();

  /// Desert regions - المناطق الصحراوية
  static List<MapRegion> get desert =>
      all.where((r) => r.category == RegionCategory.desert).toList();

  /// Island regions - الجزر
  static List<MapRegion> get islands =>
      all.where((r) => r.category == RegionCategory.island).toList();

  /// Get region by ID - الحصول على منطقة بالمعرف
  static MapRegion? getById(String id) {
    try {
      return all.firstWhere((r) => r.id == id);
    } catch (_) {
      return null;
    }
  }

  /// Get names for dropdown (Arabic) - الأسماء بالعربية
  static List<String> get namesAr => all.map((r) => r.nameAr).toList();

  /// Get names for dropdown (English) - الأسماء بالإنجليزية
  static List<String> get namesEn => all.map((r) => r.nameEn).toList();

  /// Recommended regions for download - المناطق المُوصى بتحميلها
  static const List<String> recommendedRegionIds = [
    'sanaa',
    'dhamar',
    'ibb',
    'taiz',
    'aden',
    'hodeidah',
  ];

  /// Get recommended regions - الحصول على المناطق المُوصى بها
  static List<MapRegion> get recommended =>
      recommendedRegionIds.map((id) => getById(id)!).toList();
}
