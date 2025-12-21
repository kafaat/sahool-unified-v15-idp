// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Multi-Map Provider Service
// خدمة الخرائط متعددة المزودين مع التبديل التلقائي
// ═══════════════════════════════════════════════════════════════════════════

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../config/providers_config.dart';

/// Map provider status tracker
class MapProviderStatus {
  final MapProviderConfig provider;
  ProviderStatus status;
  int failureCount;
  DateTime? lastFailure;
  DateTime? lastSuccess;

  MapProviderStatus({
    required this.provider,
    this.status = ProviderStatus.available,
    this.failureCount = 0,
    this.lastFailure,
    this.lastSuccess,
  });

  bool get isHealthy => status == ProviderStatus.available && failureCount < 3;

  void recordFailure() {
    failureCount++;
    lastFailure = DateTime.now();
    if (failureCount >= 3) {
      status = ProviderStatus.unavailable;
    }
  }

  void recordSuccess() {
    failureCount = 0;
    status = ProviderStatus.available;
    lastSuccess = DateTime.now();
  }

  void reset() {
    failureCount = 0;
    status = ProviderStatus.available;
  }
}

/// Map layer type for user selection
enum MapLayerType {
  streets,    // الشوارع
  satellite,  // القمر الصناعي
  hybrid,     // هجين
  terrain,    // التضاريس
}

/// Current map state
class MapState {
  final MapProviderConfig activeProvider;
  final MapLayerType layerType;
  final List<MapProviderStatus> providerStatuses;

  const MapState({
    required this.activeProvider,
    required this.layerType,
    required this.providerStatuses,
  });

  MapState copyWith({
    MapProviderConfig? activeProvider,
    MapLayerType? layerType,
    List<MapProviderStatus>? providerStatuses,
  }) {
    return MapState(
      activeProvider: activeProvider ?? this.activeProvider,
      layerType: layerType ?? this.layerType,
      providerStatuses: providerStatuses ?? this.providerStatuses,
    );
  }
}

/// Multi-provider map service with automatic fallback
class MapProviderService extends ChangeNotifier {
  final ProvidersConfig config;

  late MapState _state;
  final Map<String, MapProviderStatus> _statusMap = {};
  Timer? _healthCheckTimer;

  MapProviderService({required this.config}) {
    _initializeProviders();
    _startHealthChecks();
  }

  MapState get state => _state;
  MapProviderConfig get activeProvider => _state.activeProvider;
  MapLayerType get currentLayerType => _state.layerType;
  List<MapProviderStatus> get providerStatuses => _state.providerStatuses;

  void _initializeProviders() {
    // Initialize status for all providers
    for (final provider in config.mapProviders) {
      _statusMap[provider.name] = MapProviderStatus(provider: provider);
    }

    // Set initial state with primary provider
    _state = MapState(
      activeProvider: config.primaryMapProvider,
      layerType: MapLayerType.streets,
      providerStatuses: _statusMap.values.toList(),
    );
  }

  void _startHealthChecks() {
    // Check provider health every 5 minutes
    _healthCheckTimer = Timer.periodic(
      const Duration(minutes: 5),
      (_) => _checkProvidersHealth(),
    );
  }

  /// Check health of all providers
  Future<void> _checkProvidersHealth() async {
    for (final entry in _statusMap.entries) {
      if (!entry.value.isHealthy) {
        // Try to recover failed providers
        final isAvailable = await _checkProviderAvailability(entry.value.provider);
        if (isAvailable) {
          entry.value.reset();
        }
      }
    }
    _updateState();
  }

  /// Check if a specific provider is available
  Future<bool> _checkProviderAvailability(MapProviderConfig provider) async {
    try {
      // Try to fetch a sample tile
      final testUrl = provider.effectiveUrl
          .replaceAll('{z}', '10')
          .replaceAll('{x}', '512')
          .replaceAll('{y}', '512');

      final response = await http.head(Uri.parse(testUrl))
          .timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Get tile URL with automatic fallback
  String getTileUrl({int? z, int? x, int? y}) {
    return _state.activeProvider.effectiveUrl;
  }

  /// Handle tile load error - switch to fallback provider
  Future<MapProviderConfig?> handleTileError(String failedUrl) async {
    final currentStatus = _statusMap[_state.activeProvider.name];
    currentStatus?.recordFailure();

    // Find next healthy provider
    final healthyProviders = _statusMap.values
        .where((s) => s.isHealthy && s.provider.name != _state.activeProvider.name)
        .toList();

    if (healthyProviders.isNotEmpty) {
      // Sort by provider priority
      healthyProviders.sort((a, b) {
        final aIndex = config.mapProviderPriority.indexOf(a.provider.type);
        final bIndex = config.mapProviderPriority.indexOf(b.provider.type);
        return aIndex.compareTo(bIndex);
      });

      final newProvider = healthyProviders.first.provider;
      _state = _state.copyWith(activeProvider: newProvider);
      notifyListeners();
      return newProvider;
    }

    return null;
  }

  /// Manually switch provider
  void switchProvider(MapProviderConfig provider) {
    if (_statusMap[provider.name]?.isHealthy ?? false) {
      _state = _state.copyWith(activeProvider: provider);
      notifyListeners();
    }
  }

  /// Switch map layer type
  void switchLayerType(MapLayerType type) {
    MapProviderConfig? newProvider;

    switch (type) {
      case MapLayerType.streets:
        newProvider = _findProviderByKeyword(['street', 'osm', 'openstreetmap']);
        break;
      case MapLayerType.satellite:
        newProvider = _findProviderByKeyword(['satellite', 'imagery']);
        break;
      case MapLayerType.hybrid:
        newProvider = _findProviderByKeyword(['hybrid']);
        break;
      case MapLayerType.terrain:
        newProvider = _findProviderByKeyword(['topo', 'terrain']);
        break;
    }

    if (newProvider != null) {
      _state = _state.copyWith(
        activeProvider: newProvider,
        layerType: type,
      );
      notifyListeners();
    }
  }

  MapProviderConfig? _findProviderByKeyword(List<String> keywords) {
    for (final status in _statusMap.values) {
      if (!status.isHealthy) continue;

      final nameLower = status.provider.name.toLowerCase();
      for (final keyword in keywords) {
        if (nameLower.contains(keyword)) {
          return status.provider;
        }
      }
    }
    return null;
  }

  /// Get all available providers for current layer type
  List<MapProviderConfig> getAvailableProviders({MapLayerType? forLayerType}) {
    return _statusMap.values
        .where((s) => s.isHealthy)
        .map((s) => s.provider)
        .where((p) {
          if (forLayerType == null) return true;

          final name = p.name.toLowerCase();
          switch (forLayerType) {
            case MapLayerType.streets:
              return name.contains('street') || name.contains('osm') ||
                     (!name.contains('satellite') && !name.contains('hybrid'));
            case MapLayerType.satellite:
              return name.contains('satellite') || name.contains('imagery');
            case MapLayerType.hybrid:
              return name.contains('hybrid');
            case MapLayerType.terrain:
              return name.contains('topo') || name.contains('terrain');
          }
        })
        .toList();
  }

  /// Get provider statistics
  Map<String, dynamic> getProviderStats() {
    return {
      'active_provider': _state.activeProvider.name,
      'layer_type': _state.layerType.name,
      'healthy_count': _statusMap.values.where((s) => s.isHealthy).length,
      'total_count': _statusMap.length,
      'providers': _statusMap.map((key, value) => MapEntry(key, {
        'status': value.status.name,
        'failure_count': value.failureCount,
        'last_failure': value.lastFailure?.toIso8601String(),
        'last_success': value.lastSuccess?.toIso8601String(),
      })),
    };
  }

  /// Force refresh provider status
  Future<void> refreshProviderStatus() async {
    for (final status in _statusMap.values) {
      status.status = ProviderStatus.checking;
    }
    notifyListeners();

    await _checkProvidersHealth();
  }

  void _updateState() {
    _state = _state.copyWith(
      providerStatuses: _statusMap.values.toList(),
    );
    notifyListeners();
  }

  @override
  void dispose() {
    _healthCheckTimer?.cancel();
    super.dispose();
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// FLUTTER MAP INTEGRATION HELPERS
// ─────────────────────────────────────────────────────────────────────────────

/// Extension for easy flutter_map integration
extension MapProviderServiceX on MapProviderService {
  /// Get TileLayer options for flutter_map
  Map<String, dynamic> getTileLayerOptions() {
    return {
      'urlTemplate': getTileUrl(),
      'maxZoom': activeProvider.maxZoom.toDouble(),
      'minZoom': activeProvider.minZoom.toDouble(),
      'userAgentPackageName': 'app.sahool.field',
      'tileSize': 256,
      'additionalOptions': activeProvider.apiKey != null
          ? {'access_token': activeProvider.apiKey}
          : null,
    };
  }

  /// Attribution text
  String get attribution => activeProvider.attribution;

  /// Whether offline caching is supported
  bool get supportsOffline => activeProvider.supportsOffline;
}

// ─────────────────────────────────────────────────────────────────────────────
// LAYER SWITCHER WIDGET
// ─────────────────────────────────────────────────────────────────────────────

/// Map layer switcher button widget
class MapLayerSwitcher extends StatelessWidget {
  final MapProviderService service;
  final void Function(MapLayerType)? onLayerChanged;

  const MapLayerSwitcher({
    super.key,
    required this.service,
    this.onLayerChanged,
  });

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: service,
      builder: (context, _) {
        return PopupMenuButton<MapLayerType>(
          icon: _getLayerIcon(service.currentLayerType),
          tooltip: 'تبديل نوع الخريطة',
          onSelected: (type) {
            service.switchLayerType(type);
            onLayerChanged?.call(type);
          },
          itemBuilder: (context) => [
            _buildMenuItem(
              MapLayerType.streets,
              'الشوارع',
              'Streets',
              Icons.map_outlined,
            ),
            _buildMenuItem(
              MapLayerType.satellite,
              'القمر الصناعي',
              'Satellite',
              Icons.satellite_alt,
            ),
            _buildMenuItem(
              MapLayerType.hybrid,
              'هجين',
              'Hybrid',
              Icons.layers,
            ),
            _buildMenuItem(
              MapLayerType.terrain,
              'التضاريس',
              'Terrain',
              Icons.terrain,
            ),
          ],
        );
      },
    );
  }

  PopupMenuItem<MapLayerType> _buildMenuItem(
    MapLayerType type,
    String labelAr,
    String labelEn,
    IconData icon,
  ) {
    final isSelected = service.currentLayerType == type;

    return PopupMenuItem(
      value: type,
      child: Row(
        children: [
          Icon(
            icon,
            color: isSelected ? Colors.green : Colors.grey,
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                labelAr,
                style: TextStyle(
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
              Text(
                labelEn,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
          if (isSelected) ...[
            const Spacer(),
            const Icon(Icons.check, color: Colors.green, size: 18),
          ],
        ],
      ),
    );
  }

  Widget _getLayerIcon(MapLayerType type) {
    IconData icon;
    switch (type) {
      case MapLayerType.streets:
        icon = Icons.map_outlined;
        break;
      case MapLayerType.satellite:
        icon = Icons.satellite_alt;
        break;
      case MapLayerType.hybrid:
        icon = Icons.layers;
        break;
      case MapLayerType.terrain:
        icon = Icons.terrain;
        break;
    }
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Icon(icon, color: Colors.grey[700]),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PROVIDER STATUS INDICATOR
// ─────────────────────────────────────────────────────────────────────────────

/// Shows current provider status
class MapProviderIndicator extends StatelessWidget {
  final MapProviderService service;
  final bool showDetails;

  const MapProviderIndicator({
    super.key,
    required this.service,
    this.showDetails = false,
  });

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: service,
      builder: (context, _) {
        final provider = service.activeProvider;

        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.black54,
            borderRadius: BorderRadius.circular(4),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _getProviderIcon(provider.type),
              const SizedBox(width: 4),
              Text(
                provider.name,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                ),
              ),
              if (showDetails) ...[
                const SizedBox(width: 8),
                Icon(
                  provider.supportsOffline ? Icons.offline_bolt : Icons.cloud,
                  color: Colors.white70,
                  size: 12,
                ),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _getProviderIcon(MapProviderType type) {
    String emoji;
    switch (type) {
      case MapProviderType.openStreetMap:
        emoji = '🗺️';
        break;
      case MapProviderType.googleMaps:
        emoji = '📍';
        break;
      case MapProviderType.mapbox:
        emoji = '🎨';
        break;
      case MapProviderType.esri:
        emoji = '🌍';
        break;
    }
    return Text(emoji, style: const TextStyle(fontSize: 12));
  }
}
