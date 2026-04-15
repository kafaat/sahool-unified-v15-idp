/// Offline Maps Module - وحدة الخرائط المحلية
///
/// Provides offline map functionality for the SAHOOL mobile app:
/// - Download map tiles for regions
/// - Store and manage cached tiles
/// - Serve tiles from local storage with network fallback
/// - Yemen governorates predefined regions
///
/// Usage:
/// ```dart
/// import 'package:sahool_field_app/core/maps/offline/offline_maps.dart';
///
/// // Initialize region manager
/// final regionManager = RegionManager();
///
/// // Download a region
/// final result = await regionManager.downloadRegion(
///   region: YemenRegions.sanaa,
///   minZoom: 10,
///   maxZoom: 16,
///   onProgress: (progress) => print('${progress.progressPercent}%'),
/// );
///
/// // Use offline tile provider in FlutterMap
/// FlutterMap(
///   children: [
///     OfflineTileLayerOptions.create(
///       priorityMode: TilePriority.offlineFirst,
///     ),
///   ],
/// );
/// ```
library;

// Core components
export 'tile_downloader.dart';
export 'tile_storage.dart';
export 'region_manager.dart';
export 'offline_tile_provider.dart';
