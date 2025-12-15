// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - External Providers State Management
// إدارة حالة المزودين الخارجيين مع Riverpod
// ═══════════════════════════════════════════════════════════════════════════

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/providers_config.dart';
import '../services/map_provider_service.dart';
import '../services/weather_provider_service.dart';

// ─────────────────────────────────────────────────────────────────────────────
// PROVIDERS CONFIGURATION
// ─────────────────────────────────────────────────────────────────────────────

/// Main providers configuration
/// Can be overridden with API keys from environment or settings
final providersConfigProvider = StateProvider<ProvidersConfig>((ref) {
  // Default config (free providers only)
  // In production, load API keys from secure storage
  return const ProvidersConfig(
    // API Keys - uncomment and add your keys
    // googleMapsApiKey: 'YOUR_GOOGLE_MAPS_API_KEY',
    // mapboxApiKey: 'YOUR_MAPBOX_ACCESS_TOKEN',
    // openWeatherMapApiKey: 'YOUR_OPENWEATHERMAP_API_KEY',
    // sentinelHubApiKey: 'YOUR_SENTINEL_HUB_API_KEY',

    // Provider priority (most preferred first)
    mapProviderPriority: [
      MapProviderType.openStreetMap,  // Free, no API key
      MapProviderType.esri,           // Free, no API key
      MapProviderType.mapbox,         // Paid, needs API key
      MapProviderType.googleMaps,     // Paid, needs API key
    ],
    weatherProviderPriority: [
      WeatherProviderType.openMeteo,       // Free, no API key
      WeatherProviderType.openWeatherMap,  // Free tier available
      WeatherProviderType.weatherApi,      // Free tier available
    ],
  );
});

// ─────────────────────────────────────────────────────────────────────────────
// MAP PROVIDER SERVICE
// ─────────────────────────────────────────────────────────────────────────────

/// Map provider service with fallback support
final mapProviderServiceProvider = ChangeNotifierProvider<MapProviderService>((ref) {
  final config = ref.watch(providersConfigProvider);
  return MapProviderService(config: config);
});

/// Current active map provider
final activeMapProviderProvider = Provider<MapProviderConfig>((ref) {
  final service = ref.watch(mapProviderServiceProvider);
  return service.activeProvider;
});

/// Current map layer type
final mapLayerTypeProvider = Provider<MapLayerType>((ref) {
  final service = ref.watch(mapProviderServiceProvider);
  return service.currentLayerType;
});

/// Map tile URL template
final mapTileUrlProvider = Provider<String>((ref) {
  final service = ref.watch(mapProviderServiceProvider);
  return service.getTileUrl();
});

/// Available map providers list
final availableMapProvidersProvider = Provider<List<MapProviderConfig>>((ref) {
  final config = ref.watch(providersConfigProvider);
  return config.mapProviders;
});

// ─────────────────────────────────────────────────────────────────────────────
// WEATHER PROVIDER SERVICE
// ─────────────────────────────────────────────────────────────────────────────

/// Weather provider service with fallback support
final weatherProviderServiceProvider = Provider<WeatherProviderService>((ref) {
  final config = ref.watch(providersConfigProvider);
  return WeatherProviderService(config: config);
});

/// Current weather for location
final currentWeatherProvider = FutureProvider.family<WeatherResult<WeatherData>, LatLng>((ref, location) async {
  final service = ref.watch(weatherProviderServiceProvider);
  return service.getCurrentWeather(location.lat, location.lng);
});

/// Weather forecast for location
final weatherForecastProvider = FutureProvider.family<WeatherResult<List<ForecastDay>>, WeatherForecastParams>((ref, params) async {
  final service = ref.watch(weatherProviderServiceProvider);
  return service.getForecast(params.lat, params.lng, days: params.days);
});

// ─────────────────────────────────────────────────────────────────────────────
// PROVIDER STATUS & HEALTH
// ─────────────────────────────────────────────────────────────────────────────

/// Provider health status
final providerHealthProvider = Provider<ProviderHealth>((ref) {
  final config = ref.watch(providersConfigProvider);

  return ProviderHealth(
    hasPremiumMaps: config.hasPremiumMaps,
    hasPremiumWeather: config.hasPremiumWeather,
    hasSatelliteImagery: config.hasSatelliteImagery,
    configuredMapProviders: config.mapProviders.length,
    configuredWeatherProviders: config.weatherProviders.length,
  );
});

/// Premium features availability
final hasPremiumFeaturesProvider = Provider<bool>((ref) {
  final health = ref.watch(providerHealthProvider);
  return health.hasPremiumMaps || health.hasPremiumWeather || health.hasSatelliteImagery;
});

// ─────────────────────────────────────────────────────────────────────────────
// HELPER CLASSES
// ─────────────────────────────────────────────────────────────────────────────

/// Simple lat/lng class
class LatLng {
  final double lat;
  final double lng;

  const LatLng(this.lat, this.lng);

  @override
  bool operator ==(Object other) =>
      other is LatLng && other.lat == lat && other.lng == lng;

  @override
  int get hashCode => lat.hashCode ^ lng.hashCode;
}

/// Weather forecast parameters
class WeatherForecastParams {
  final double lat;
  final double lng;
  final int days;

  const WeatherForecastParams({
    required this.lat,
    required this.lng,
    this.days = 7,
  });

  @override
  bool operator ==(Object other) =>
      other is WeatherForecastParams &&
      other.lat == lat &&
      other.lng == lng &&
      other.days == days;

  @override
  int get hashCode => lat.hashCode ^ lng.hashCode ^ days.hashCode;
}

/// Provider health summary
class ProviderHealth {
  final bool hasPremiumMaps;
  final bool hasPremiumWeather;
  final bool hasSatelliteImagery;
  final int configuredMapProviders;
  final int configuredWeatherProviders;

  const ProviderHealth({
    required this.hasPremiumMaps,
    required this.hasPremiumWeather,
    required this.hasSatelliteImagery,
    required this.configuredMapProviders,
    required this.configuredWeatherProviders,
  });

  bool get allFree => !hasPremiumMaps && !hasPremiumWeather && !hasSatelliteImagery;
}

// ─────────────────────────────────────────────────────────────────────────────
// API KEY MANAGEMENT
// ─────────────────────────────────────────────────────────────────────────────

/// Update providers configuration with new API keys
void updateProvidersConfig(WidgetRef ref, {
  String? googleMapsApiKey,
  String? mapboxApiKey,
  String? openWeatherMapApiKey,
  String? sentinelHubApiKey,
}) {
  final current = ref.read(providersConfigProvider);

  ref.read(providersConfigProvider.notifier).state = ProvidersConfig(
    googleMapsApiKey: googleMapsApiKey ?? current.googleMapsApiKey,
    mapboxApiKey: mapboxApiKey ?? current.mapboxApiKey,
    openWeatherMapApiKey: openWeatherMapApiKey ?? current.openWeatherMapApiKey,
    sentinelHubApiKey: sentinelHubApiKey ?? current.sentinelHubApiKey,
    mapProviderPriority: current.mapProviderPriority,
    weatherProviderPriority: current.weatherProviderPriority,
  );
}

/// Update provider priority order
void updateProviderPriority(WidgetRef ref, {
  List<MapProviderType>? mapPriority,
  List<WeatherProviderType>? weatherPriority,
}) {
  final current = ref.read(providersConfigProvider);

  ref.read(providersConfigProvider.notifier).state = ProvidersConfig(
    googleMapsApiKey: current.googleMapsApiKey,
    mapboxApiKey: current.mapboxApiKey,
    openWeatherMapApiKey: current.openWeatherMapApiKey,
    sentinelHubApiKey: current.sentinelHubApiKey,
    mapProviderPriority: mapPriority ?? current.mapProviderPriority,
    weatherProviderPriority: weatherPriority ?? current.weatherProviderPriority,
  );
}
