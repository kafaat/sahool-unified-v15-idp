/// SAHOOL Map Providers - Multiple Map Library Support
/// دعم متعدد لمكتبات الخرائط
///
/// Supported Providers:
/// - MapLibre GL (Open Source - No API key required)
/// - OpenStreetMap (Free)
/// - Mapbox (Requires API key)
/// - Google Maps (Requires API key)
/// - Custom Tile Server

import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';

/// Map Provider Types
/// أنواع مزودي الخرائط
enum MapProvider {
  /// MapLibre GL - Open Source fork of Mapbox GL
  /// مفتوح المصدر - لا يحتاج مفتاح API
  maplibre,

  /// OpenStreetMap - Free community maps
  /// خرائط مجانية من المجتمع
  openStreetMap,

  /// Mapbox - Premium maps (requires API key)
  /// خرائط متميزة (يحتاج مفتاح API)
  mapbox,

  /// Google Maps (requires API key)
  /// خرائط جوجل (يحتاج مفتاح API)
  google,

  /// SAHOOL Custom Tile Server
  /// خادم البلاطات المخصص لسهول
  sahoolTiles,

  /// Satellite imagery
  /// صور الأقمار الصناعية
  satellite,
}

/// Map Style Types
/// أنماط الخرائط
enum MapStyle {
  streets,
  satellite,
  satelliteStreets,
  outdoors,
  light,
  dark,
  terrain,
  agricultural, // Custom SAHOOL agricultural style
}

/// Map Provider Configuration
/// تكوين مزود الخرائط
class MapProviderConfig {
  final MapProvider provider;
  final String name;
  final String nameAr;
  final String? apiKey;
  final String tileUrl;
  final String? styleUrl;
  final String attribution;
  final int minZoom;
  final int maxZoom;
  final bool requiresApiKey;
  final bool supportsOffline;
  final bool supportsVector;

  const MapProviderConfig({
    required this.provider,
    required this.name,
    required this.nameAr,
    this.apiKey,
    required this.tileUrl,
    this.styleUrl,
    required this.attribution,
    this.minZoom = 1,
    this.maxZoom = 19,
    this.requiresApiKey = false,
    this.supportsOffline = true,
    this.supportsVector = false,
  });
}

/// SAHOOL Map Providers Registry
/// سجل مزودي الخرائط في سهول
class SahoolMapProviders {

  /// MapLibre OpenStreetMap Style (Free, No API Key)
  /// نمط MapLibre مع OpenStreetMap (مجاني)
  static MapProviderConfig get maplibreOsm => const MapProviderConfig(
    provider: MapProvider.maplibre,
    name: 'MapLibre OSM',
    nameAr: 'MapLibre - خرائط مفتوحة',
    tileUrl: 'https://tiles.openfreemap.org/styles/liberty/{z}/{x}/{y}.png',
    styleUrl: 'https://tiles.openfreemap.org/styles/liberty.json',
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
    requiresApiKey: false,
    supportsOffline: true,
    supportsVector: true,
  );

  /// MapLibre with Protomaps (Free Vector Tiles)
  static MapProviderConfig get maplibreProtomaps => const MapProviderConfig(
    provider: MapProvider.maplibre,
    name: 'MapLibre Protomaps',
    nameAr: 'MapLibre - بروتومابس',
    tileUrl: 'https://api.protomaps.com/tiles/v3/{z}/{x}/{y}.mvt',
    styleUrl: 'https://api.protomaps.com/styles/v2/light.json',
    attribution: '© Protomaps © OpenStreetMap',
    maxZoom: 15,
    requiresApiKey: false,
    supportsOffline: true,
    supportsVector: true,
  );

  /// OpenStreetMap Standard (Free)
  /// خرائط OpenStreetMap القياسية (مجانية)
  static MapProviderConfig get openStreetMap => const MapProviderConfig(
    provider: MapProvider.openStreetMap,
    name: 'OpenStreetMap',
    nameAr: 'خرائط الشوارع المفتوحة',
    tileUrl: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
    requiresApiKey: false,
    supportsOffline: true,
    supportsVector: false,
  );

  /// OpenStreetMap HOT (Humanitarian)
  static MapProviderConfig get osmHot => const MapProviderConfig(
    provider: MapProvider.openStreetMap,
    name: 'OSM Humanitarian',
    nameAr: 'خرائط إنسانية',
    tileUrl: 'https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
    attribution: '© OpenStreetMap contributors, HOT',
    maxZoom: 19,
    requiresApiKey: false,
    supportsOffline: true,
    supportsVector: false,
  );

  /// ESRI World Imagery (Satellite - Free for limited use)
  static MapProviderConfig get esriSatellite => const MapProviderConfig(
    provider: MapProvider.satellite,
    name: 'ESRI Satellite',
    nameAr: 'صور الأقمار الصناعية - ESRI',
    tileUrl: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '© Esri, Maxar, Earthstar Geographics',
    maxZoom: 18,
    requiresApiKey: false,
    supportsOffline: true,
    supportsVector: false,
  );

  /// Stadia Maps (Free tier available)
  static MapProviderConfig get stadiaMaps => const MapProviderConfig(
    provider: MapProvider.maplibre,
    name: 'Stadia Maps',
    nameAr: 'خرائط ستاديا',
    tileUrl: 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}.png',
    attribution: '© Stadia Maps © OpenStreetMap',
    maxZoom: 20,
    requiresApiKey: false, // Free tier available
    supportsOffline: true,
    supportsVector: false,
  );

  /// SAHOOL Custom Tile Server
  /// خادم البلاطات المخصص لسهول
  static MapProviderConfig sahoolTiles(String baseUrl) => MapProviderConfig(
    provider: MapProvider.sahoolTiles,
    name: 'SAHOOL Maps',
    nameAr: 'خرائط سهول',
    tileUrl: '$baseUrl/tiles/{z}/{x}/{y}.png',
    attribution: '© SAHOOL Platform',
    maxZoom: 20,
    requiresApiKey: false,
    supportsOffline: true,
    supportsVector: true,
  );

  /// Mapbox Streets (Requires API Key)
  static MapProviderConfig mapbox(String apiKey) => MapProviderConfig(
    provider: MapProvider.mapbox,
    name: 'Mapbox Streets',
    nameAr: 'خرائط ماب بوكس',
    apiKey: apiKey,
    tileUrl: 'https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token=$apiKey',
    styleUrl: 'mapbox://styles/mapbox/streets-v12',
    attribution: '© Mapbox © OpenStreetMap',
    maxZoom: 22,
    requiresApiKey: true,
    supportsOffline: true,
    supportsVector: true,
  );

  /// Mapbox Satellite (Requires API Key)
  static MapProviderConfig mapboxSatellite(String apiKey) => MapProviderConfig(
    provider: MapProvider.mapbox,
    name: 'Mapbox Satellite',
    nameAr: 'صور الأقمار - ماب بوكس',
    apiKey: apiKey,
    tileUrl: 'https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/{z}/{x}/{y}?access_token=$apiKey',
    styleUrl: 'mapbox://styles/mapbox/satellite-streets-v12',
    attribution: '© Mapbox © OpenStreetMap © Maxar',
    maxZoom: 22,
    requiresApiKey: true,
    supportsOffline: true,
    supportsVector: true,
  );

  /// Get all free providers (no API key required)
  /// الحصول على جميع المزودين المجانيين
  static List<MapProviderConfig> get freeProviders => [
    maplibreOsm,
    maplibreProtomaps,
    openStreetMap,
    osmHot,
    esriSatellite,
    stadiaMaps,
  ];

  /// Get default provider (MapLibre OSM - Free)
  /// المزود الافتراضي (مجاني)
  static MapProviderConfig get defaultProvider => maplibreOsm;

  /// Get satellite provider (ESRI - Free)
  static MapProviderConfig get defaultSatellite => esriSatellite;
}

/// Yemen-specific map bounds
/// حدود الخريطة الخاصة باليمن
class YemenMapBounds {
  static const LatLng center = LatLng(15.5527, 48.5164);
  static const LatLng southWest = LatLng(12.1, 42.5);
  static const LatLng northEast = LatLng(19.0, 54.5);
  static const double defaultZoom = 6.0;
  static const double minZoom = 5.0;
  static const double maxZoom = 18.0;

  /// Major cities in Yemen
  /// المدن الرئيسية في اليمن
  static const Map<String, LatLng> cities = {
    'sanaa': LatLng(15.3694, 44.1910),
    'aden': LatLng(12.7855, 45.0187),
    'taiz': LatLng(13.5789, 44.0219),
    'hodeidah': LatLng(14.7979, 42.9540),
    'mukalla': LatLng(14.5425, 49.1242),
    'ibb': LatLng(13.9667, 44.1667),
    'dhamar': LatLng(14.5500, 44.4000),
    'sayun': LatLng(15.9433, 48.7863),
    'marib': LatLng(15.4667, 45.3333),
    'hajjah': LatLng(15.6917, 43.6028),
  };
}
