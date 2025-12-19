// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Multi-Provider Configuration
// خدمات متعددة مع إعدادات الأولوية
// ═══════════════════════════════════════════════════════════════════════════

/// Provider priority levels
enum ProviderPriority {
  primary,   // الأساسي - يُستخدم أولاً
  secondary, // الثانوي - يُستخدم عند فشل الأساسي
  tertiary,  // الثالث - آخر خيار
  disabled,  // معطل
}

/// Provider status
enum ProviderStatus {
  available,    // متاح
  unavailable,  // غير متاح
  rateLimited,  // تجاوز الحد
  error,        // خطأ
  checking,     // جاري الفحص
}

// ─────────────────────────────────────────────────────────────────────────────
// MAP PROVIDERS - مزودي الخرائط
// ─────────────────────────────────────────────────────────────────────────────

enum MapProviderType {
  openStreetMap,
  googleMaps,
  mapbox,
  esri,
}

class MapProviderConfig {
  final MapProviderType type;
  final String name;
  final String nameAr;
  final String urlTemplate;
  final String? apiKey;
  final ProviderPriority priority;
  final bool requiresApiKey;
  final int maxZoom;
  final int minZoom;
  final String attribution;
  final bool supportsOffline;
  final double? costPerRequest; // Cost in USD per 1000 requests

  const MapProviderConfig({
    required this.type,
    required this.name,
    required this.nameAr,
    required this.urlTemplate,
    this.apiKey,
    required this.priority,
    this.requiresApiKey = false,
    this.maxZoom = 18,
    this.minZoom = 1,
    required this.attribution,
    this.supportsOffline = true,
    this.costPerRequest,
  });

  bool get isConfigured => !requiresApiKey || (apiKey != null && apiKey!.isNotEmpty);

  String get effectiveUrl {
    if (apiKey != null) {
      return urlTemplate.replaceAll('{apiKey}', apiKey!);
    }
    return urlTemplate;
  }
}

/// All available map providers
class MapProviders {
  // OpenStreetMap - مجاني، بدون مفتاح API
  static const openStreetMap = MapProviderConfig(
    type: MapProviderType.openStreetMap,
    name: 'OpenStreetMap',
    nameAr: 'خريطة الشارع المفتوحة',
    urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    priority: ProviderPriority.primary,
    requiresApiKey: false,
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors',
    supportsOffline: true,
    costPerRequest: 0,
  );

  // Google Maps - يحتاج مفتاح API
  static MapProviderConfig googleMaps({String? apiKey}) => MapProviderConfig(
    type: MapProviderType.googleMaps,
    name: 'Google Maps',
    nameAr: 'خرائط جوجل',
    urlTemplate: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&key={apiKey}',
    apiKey: apiKey,
    priority: ProviderPriority.secondary,
    requiresApiKey: true,
    maxZoom: 21,
    attribution: '© Google',
    supportsOffline: false,
    costPerRequest: 7.0, // $7 per 1000 requests
  );

  // Google Satellite
  static MapProviderConfig googleSatellite({String? apiKey}) => MapProviderConfig(
    type: MapProviderType.googleMaps,
    name: 'Google Satellite',
    nameAr: 'جوجل القمر الصناعي',
    urlTemplate: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&key={apiKey}',
    apiKey: apiKey,
    priority: ProviderPriority.secondary,
    requiresApiKey: true,
    maxZoom: 21,
    attribution: '© Google',
    supportsOffline: false,
    costPerRequest: 7.0,
  );

  // Google Hybrid (Satellite + Roads)
  static MapProviderConfig googleHybrid({String? apiKey}) => MapProviderConfig(
    type: MapProviderType.googleMaps,
    name: 'Google Hybrid',
    nameAr: 'جوجل هجين',
    urlTemplate: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}&key={apiKey}',
    apiKey: apiKey,
    priority: ProviderPriority.tertiary,
    requiresApiKey: true,
    maxZoom: 21,
    attribution: '© Google',
    supportsOffline: false,
    costPerRequest: 7.0,
  );

  // Mapbox Streets
  static MapProviderConfig mapboxStreets({String? apiKey}) => MapProviderConfig(
    type: MapProviderType.mapbox,
    name: 'Mapbox Streets',
    nameAr: 'ماب بوكس شوارع',
    urlTemplate: 'https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token={apiKey}',
    apiKey: apiKey,
    priority: ProviderPriority.secondary,
    requiresApiKey: true,
    maxZoom: 22,
    attribution: '© Mapbox © OpenStreetMap',
    supportsOffline: true,
    costPerRequest: 0.5, // $0.50 per 1000 requests
  );

  // Mapbox Satellite
  static MapProviderConfig mapboxSatellite({String? apiKey}) => MapProviderConfig(
    type: MapProviderType.mapbox,
    name: 'Mapbox Satellite',
    nameAr: 'ماب بوكس قمر صناعي',
    urlTemplate: 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token={apiKey}',
    apiKey: apiKey,
    priority: ProviderPriority.secondary,
    requiresApiKey: true,
    maxZoom: 22,
    attribution: '© Mapbox © Maxar',
    supportsOffline: true,
    costPerRequest: 0.5,
  );

  // Mapbox Satellite Streets (Hybrid)
  static MapProviderConfig mapboxHybrid({String? apiKey}) => MapProviderConfig(
    type: MapProviderType.mapbox,
    name: 'Mapbox Hybrid',
    nameAr: 'ماب بوكس هجين',
    urlTemplate: 'https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/{z}/{x}/{y}?access_token={apiKey}',
    apiKey: apiKey,
    priority: ProviderPriority.tertiary,
    requiresApiKey: true,
    maxZoom: 22,
    attribution: '© Mapbox © Maxar © OpenStreetMap',
    supportsOffline: true,
    costPerRequest: 0.5,
  );

  // ESRI World Imagery
  static const esriSatellite = MapProviderConfig(
    type: MapProviderType.esri,
    name: 'ESRI Satellite',
    nameAr: 'ESRI قمر صناعي',
    urlTemplate: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    priority: ProviderPriority.tertiary,
    requiresApiKey: false,
    maxZoom: 19,
    attribution: '© Esri, Maxar, Earthstar Geographics',
    supportsOffline: true,
    costPerRequest: 0,
  );

  // ESRI World Street Map
  static const esriStreets = MapProviderConfig(
    type: MapProviderType.esri,
    name: 'ESRI Streets',
    nameAr: 'ESRI شوارع',
    urlTemplate: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
    priority: ProviderPriority.tertiary,
    requiresApiKey: false,
    maxZoom: 18,
    attribution: '© Esri, HERE, Garmin, OpenStreetMap',
    supportsOffline: true,
    costPerRequest: 0,
  );

  // OpenTopoMap - Terrain
  static const openTopoMap = MapProviderConfig(
    type: MapProviderType.openStreetMap,
    name: 'OpenTopoMap',
    nameAr: 'خريطة التضاريس',
    urlTemplate: 'https://tile.opentopomap.org/{z}/{x}/{y}.png',
    priority: ProviderPriority.tertiary,
    requiresApiKey: false,
    maxZoom: 17,
    attribution: '© OpenStreetMap, SRTM',
    supportsOffline: true,
    costPerRequest: 0,
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// WEATHER PROVIDERS - مزودي الطقس
// ─────────────────────────────────────────────────────────────────────────────

enum WeatherProviderType {
  openMeteo,
  openWeatherMap,
  weatherApi,
  visualCrossing,
}

class WeatherProviderConfig {
  final WeatherProviderType type;
  final String name;
  final String nameAr;
  final String baseUrl;
  final String? apiKey;
  final ProviderPriority priority;
  final bool requiresApiKey;
  final int forecastDays;
  final bool supportsHistorical;
  final bool supportsAlerts;
  final double? costPerRequest;
  final int rateLimit; // requests per minute

  const WeatherProviderConfig({
    required this.type,
    required this.name,
    required this.nameAr,
    required this.baseUrl,
    this.apiKey,
    required this.priority,
    this.requiresApiKey = false,
    this.forecastDays = 7,
    this.supportsHistorical = false,
    this.supportsAlerts = false,
    this.costPerRequest,
    this.rateLimit = 60,
  });

  bool get isConfigured => !requiresApiKey || (apiKey != null && apiKey!.isNotEmpty);
}

/// All available weather providers
class WeatherProviders {
  // Open-Meteo - مجاني، بدون مفتاح API
  static const openMeteo = WeatherProviderConfig(
    type: WeatherProviderType.openMeteo,
    name: 'Open-Meteo',
    nameAr: 'أوبن ميتيو',
    baseUrl: 'https://api.open-meteo.com/v1',
    priority: ProviderPriority.primary,
    requiresApiKey: false,
    forecastDays: 16,
    supportsHistorical: true,
    supportsAlerts: false,
    costPerRequest: 0,
    rateLimit: 10000,
  );

  // OpenWeatherMap - يحتاج مفتاح API (مجاني محدود)
  static WeatherProviderConfig openWeatherMap({String? apiKey}) => WeatherProviderConfig(
    type: WeatherProviderType.openWeatherMap,
    name: 'OpenWeatherMap',
    nameAr: 'أوبن ويذر ماب',
    baseUrl: 'https://api.openweathermap.org/data/2.5',
    apiKey: apiKey,
    priority: ProviderPriority.secondary,
    requiresApiKey: true,
    forecastDays: 8,
    supportsHistorical: false,
    supportsAlerts: true,
    costPerRequest: 0, // Free tier: 1000 calls/day
    rateLimit: 60,
  );

  // WeatherAPI - يحتاج مفتاح API
  static WeatherProviderConfig weatherApi({String? apiKey}) => WeatherProviderConfig(
    type: WeatherProviderType.weatherApi,
    name: 'WeatherAPI',
    nameAr: 'ويذر API',
    baseUrl: 'https://api.weatherapi.com/v1',
    apiKey: apiKey,
    priority: ProviderPriority.secondary,
    requiresApiKey: true,
    forecastDays: 14,
    supportsHistorical: true,
    supportsAlerts: true,
    costPerRequest: 0, // Free tier: 1M calls/month
    rateLimit: 100,
  );

  // Visual Crossing - يحتاج مفتاح API
  static WeatherProviderConfig visualCrossing({String? apiKey}) => WeatherProviderConfig(
    type: WeatherProviderType.visualCrossing,
    name: 'Visual Crossing',
    nameAr: 'فيجوال كروسينج',
    baseUrl: 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline',
    apiKey: apiKey,
    priority: ProviderPriority.tertiary,
    requiresApiKey: true,
    forecastDays: 15,
    supportsHistorical: true,
    supportsAlerts: true,
    costPerRequest: 0.0001, // $0.0001 per request
    rateLimit: 1000,
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// SATELLITE PROVIDERS - مزودي الأقمار الصناعية
// ─────────────────────────────────────────────────────────────────────────────

enum SatelliteProviderType {
  sentinelHub,
  planetLabs,
  maxar,
  landsat,
}

class SatelliteProviderConfig {
  final SatelliteProviderType type;
  final String name;
  final String nameAr;
  final String baseUrl;
  final String? apiKey;
  final ProviderPriority priority;
  final bool requiresApiKey;
  final int resolution; // meters
  final int revisitDays;
  final List<String> indices; // NDVI, NDWI, etc.
  final double? costPerKm2;

  const SatelliteProviderConfig({
    required this.type,
    required this.name,
    required this.nameAr,
    required this.baseUrl,
    this.apiKey,
    required this.priority,
    this.requiresApiKey = true,
    required this.resolution,
    required this.revisitDays,
    required this.indices,
    this.costPerKm2,
  });

  bool get isConfigured => !requiresApiKey || (apiKey != null && apiKey!.isNotEmpty);
}

/// All available satellite providers
class SatelliteProviders {
  // Sentinel Hub (Sentinel-2)
  static SatelliteProviderConfig sentinelHub({String? apiKey}) => SatelliteProviderConfig(
    type: SatelliteProviderType.sentinelHub,
    name: 'Sentinel Hub',
    nameAr: 'سنتينيل هب',
    baseUrl: 'https://services.sentinel-hub.com',
    apiKey: apiKey,
    priority: ProviderPriority.primary,
    requiresApiKey: true,
    resolution: 10,
    revisitDays: 5,
    indices: ['NDVI', 'NDWI', 'EVI', 'SAVI', 'NDMI', 'LAI'],
    costPerKm2: 0.001, // ~$0.001 per km²
  );

  // Planet Labs
  static SatelliteProviderConfig planetLabs({String? apiKey}) => SatelliteProviderConfig(
    type: SatelliteProviderType.planetLabs,
    name: 'Planet Labs',
    nameAr: 'بلانيت لابس',
    baseUrl: 'https://api.planet.com/data/v1',
    apiKey: apiKey,
    priority: ProviderPriority.secondary,
    requiresApiKey: true,
    resolution: 3,
    revisitDays: 1,
    indices: ['NDVI', 'NDWI', 'EVI', 'GNDVI'],
    costPerKm2: 0.10, // ~$0.10 per km²
  );

  // Maxar (DigitalGlobe)
  static SatelliteProviderConfig maxar({String? apiKey}) => SatelliteProviderConfig(
    type: SatelliteProviderType.maxar,
    name: 'Maxar',
    nameAr: 'ماكسار',
    baseUrl: 'https://api.maxar.com/streaming/v1',
    apiKey: apiKey,
    priority: ProviderPriority.tertiary,
    requiresApiKey: true,
    resolution: 0, // 30cm - 50cm
    revisitDays: 3,
    indices: ['NDVI'],
    costPerKm2: 15.0, // ~$15 per km²
  );

  // Landsat (Free via USGS)
  static const landsat = SatelliteProviderConfig(
    type: SatelliteProviderType.landsat,
    name: 'Landsat (USGS)',
    nameAr: 'لاندسات',
    baseUrl: 'https://earthexplorer.usgs.gov/inventory/json/v/1.4.1',
    priority: ProviderPriority.tertiary,
    requiresApiKey: false,
    resolution: 30,
    revisitDays: 16,
    indices: ['NDVI', 'NDWI', 'EVI', 'SAVI'],
    costPerKm2: 0,
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// PROVIDER MANAGER - إدارة المزودين
// ─────────────────────────────────────────────────────────────────────────────

class ProvidersConfig {
  // API Keys - يتم تحميلها من البيئة أو الإعدادات
  final String? googleMapsApiKey;
  final String? mapboxApiKey;
  final String? openWeatherMapApiKey;
  final String? weatherApiKey;
  final String? sentinelHubApiKey;
  final String? planetLabsApiKey;

  // Provider priorities (can be changed at runtime)
  final List<MapProviderType> mapProviderPriority;
  final List<WeatherProviderType> weatherProviderPriority;
  final List<SatelliteProviderType> satelliteProviderPriority;

  const ProvidersConfig({
    this.googleMapsApiKey,
    this.mapboxApiKey,
    this.openWeatherMapApiKey,
    this.weatherApiKey,
    this.sentinelHubApiKey,
    this.planetLabsApiKey,
    this.mapProviderPriority = const [
      MapProviderType.openStreetMap,
      MapProviderType.mapbox,
      MapProviderType.googleMaps,
      MapProviderType.esri,
    ],
    this.weatherProviderPriority = const [
      WeatherProviderType.openMeteo,
      WeatherProviderType.openWeatherMap,
      WeatherProviderType.weatherApi,
      WeatherProviderType.visualCrossing,
    ],
    this.satelliteProviderPriority = const [
      SatelliteProviderType.sentinelHub,
      SatelliteProviderType.landsat,
      SatelliteProviderType.planetLabs,
      SatelliteProviderType.maxar,
    ],
  });

  /// Get configured map providers sorted by priority
  List<MapProviderConfig> get mapProviders {
    final providers = <MapProviderConfig>[
      MapProviders.openStreetMap,
      if (googleMapsApiKey != null) MapProviders.googleMaps(apiKey: googleMapsApiKey),
      if (googleMapsApiKey != null) MapProviders.googleSatellite(apiKey: googleMapsApiKey),
      if (googleMapsApiKey != null) MapProviders.googleHybrid(apiKey: googleMapsApiKey),
      if (mapboxApiKey != null) MapProviders.mapboxStreets(apiKey: mapboxApiKey),
      if (mapboxApiKey != null) MapProviders.mapboxSatellite(apiKey: mapboxApiKey),
      if (mapboxApiKey != null) MapProviders.mapboxHybrid(apiKey: mapboxApiKey),
      MapProviders.esriSatellite,
      MapProviders.esriStreets,
      MapProviders.openTopoMap,
    ];

    // Sort by priority order
    providers.sort((a, b) {
      final aIndex = mapProviderPriority.indexOf(a.type);
      final bIndex = mapProviderPriority.indexOf(b.type);
      return (aIndex == -1 ? 999 : aIndex).compareTo(bIndex == -1 ? 999 : bIndex);
    });

    return providers;
  }

  /// Get configured weather providers sorted by priority
  List<WeatherProviderConfig> get weatherProviders {
    final providers = <WeatherProviderConfig>[
      WeatherProviders.openMeteo,
      if (openWeatherMapApiKey != null) WeatherProviders.openWeatherMap(apiKey: openWeatherMapApiKey),
      if (weatherApiKey != null) WeatherProviders.weatherApi(apiKey: weatherApiKey),
    ];

    providers.sort((a, b) {
      final aIndex = weatherProviderPriority.indexOf(a.type);
      final bIndex = weatherProviderPriority.indexOf(b.type);
      return (aIndex == -1 ? 999 : aIndex).compareTo(bIndex == -1 ? 999 : bIndex);
    });

    return providers;
  }

  /// Get primary map provider
  MapProviderConfig get primaryMapProvider => mapProviders.first;

  /// Get primary weather provider
  WeatherProviderConfig get primaryWeatherProvider => weatherProviders.first;

  /// Get satellite map provider (first available satellite/aerial)
  MapProviderConfig? get satelliteMapProvider {
    return mapProviders.firstWhere(
      (p) => p.name.toLowerCase().contains('satellite') ||
             p.name.toLowerCase().contains('hybrid'),
      orElse: () => MapProviders.esriSatellite,
    );
  }

  /// Check if premium features are available
  bool get hasPremiumMaps => googleMapsApiKey != null || mapboxApiKey != null;
  bool get hasPremiumWeather => openWeatherMapApiKey != null || weatherApiKey != null;
  bool get hasSatelliteImagery => sentinelHubApiKey != null || planetLabsApiKey != null;
}

// ─────────────────────────────────────────────────────────────────────────────
// DEFAULT CONFIGURATION - الإعدادات الافتراضية
// ─────────────────────────────────────────────────────────────────────────────

/// Default providers config (free tier only)
const defaultProvidersConfig = ProvidersConfig();

/// Development config with test keys
ProvidersConfig developmentProvidersConfig({
  String? googleMapsApiKey,
  String? mapboxApiKey,
  String? openWeatherMapApiKey,
}) {
  return ProvidersConfig(
    googleMapsApiKey: googleMapsApiKey,
    mapboxApiKey: mapboxApiKey,
    openWeatherMapApiKey: openWeatherMapApiKey,
  );
}
