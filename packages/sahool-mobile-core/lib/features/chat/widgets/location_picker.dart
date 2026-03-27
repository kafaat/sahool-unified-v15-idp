/// Location Picker Widget
/// أداة اختيار الموقع
///
/// Features:
/// - Get current location using geolocator
/// - Show location on map for confirmation
/// - Allow user to adjust pin position
/// - Return selected location coordinates
library;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/config/theme.dart';
import '../../../core/map/map_providers.dart';

/// Location data returned from picker
/// بيانات الموقع المُختار
class LocationData {
  final double latitude;
  final double longitude;
  final String? address;

  const LocationData({
    required this.latitude,
    required this.longitude,
    this.address,
  });

  Map<String, dynamic> toJson() => {
        'latitude': latitude,
        'longitude': longitude,
        'address': address,
      };
}

/// Location Picker Screen
/// شاشة اختيار الموقع
class LocationPickerScreen extends StatefulWidget {
  const LocationPickerScreen({super.key});

  @override
  State<LocationPickerScreen> createState() => _LocationPickerScreenState();
}

class _LocationPickerScreenState extends State<LocationPickerScreen> {
  final MapController _mapController = MapController();
  LatLng? _selectedLocation;
  bool _isLoading = true;
  String? _errorMessage;
  bool _showSatellite = false;

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  /// Get current location using geolocator
  /// الحصول على الموقع الحالي
  Future<void> _getCurrentLocation() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // Check if location services are enabled
      final serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() {
          _isLoading = false;
          _errorMessage = 'خدمات الموقع غير مفعلة';
        });
        // Use default location (Yemen center)
        _setDefaultLocation();
        return;
      }

      // Check permission
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          setState(() {
            _isLoading = false;
            _errorMessage = 'تم رفض إذن الموقع';
          });
          _setDefaultLocation();
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        setState(() {
          _isLoading = false;
          _errorMessage = 'إذن الموقع مرفوض بشكل دائم. يرجى تفعيله من الإعدادات';
        });
        _setDefaultLocation();
        return;
      }

      // Get current position
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 10),
        ),
      );

      if (mounted) {
        setState(() {
          _selectedLocation = LatLng(position.latitude, position.longitude);
          _isLoading = false;
        });
        _mapController.move(_selectedLocation!, 15);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = 'تعذر الحصول على الموقع';
        });
        _setDefaultLocation();
      }
    }
  }

  /// Set default location (Yemen center)
  /// تعيين الموقع الافتراضي
  void _setDefaultLocation() {
    setState(() {
      _selectedLocation = YemenMapBounds.center;
    });
  }

  /// Handle map tap to select location
  /// معالجة النقر على الخريطة لاختيار الموقع
  void _handleMapTap(TapPosition tapPosition, LatLng point) {
    setState(() {
      _selectedLocation = point;
    });
  }

  /// Toggle satellite view
  /// تبديل عرض القمر الصناعي
  void _toggleSatellite() {
    setState(() {
      _showSatellite = !_showSatellite;
    });
  }

  /// Confirm and return selected location
  /// تأكيد وإرجاع الموقع المختار
  void _confirmLocation() {
    if (_selectedLocation != null) {
      final locationData = LocationData(
        latitude: _selectedLocation!.latitude,
        longitude: _selectedLocation!.longitude,
      );
      Navigator.pop(context, locationData);
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = _showSatellite
        ? SahoolMapProviders.defaultSatellite
        : SahoolMapProviders.defaultProvider;

    return Scaffold(
      appBar: AppBar(
        title: const Text('اختر الموقع'),
        backgroundColor: SahoolTheme.primary,
        foregroundColor: Colors.white,
        actions: [
          // Satellite toggle
          IconButton(
            onPressed: _toggleSatellite,
            icon: Icon(_showSatellite ? Icons.map : Icons.satellite_alt),
            tooltip: _showSatellite ? 'خريطة' : 'قمر صناعي',
          ),
          // My location button
          IconButton(
            onPressed: _getCurrentLocation,
            icon: const Icon(Icons.my_location),
            tooltip: 'موقعي الحالي',
          ),
        ],
      ),
      body: Stack(
        children: [
          // Map
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: _selectedLocation ?? YemenMapBounds.center,
              initialZoom: 10,
              minZoom: YemenMapBounds.minZoom,
              maxZoom: YemenMapBounds.maxZoom,
              onTap: _handleMapTap,
            ),
            children: [
              // Tile layer
              TileLayer(
                urlTemplate: provider.tileUrl,
                userAgentPackageName: 'app.sahool.field',
                maxZoom: provider.maxZoom.toDouble(),
              ),

              // Selected location marker
              if (_selectedLocation != null)
                MarkerLayer(
                  markers: [
                    Marker(
                      point: _selectedLocation!,
                      width: 50,
                      height: 50,
                      child: const _LocationPin(),
                    ),
                  ],
                ),

              // Attribution
              RichAttributionWidget(
                attributions: [
                  TextSourceAttribution(provider.attribution),
                ],
              ),
            ],
          ),

          // Loading indicator
          if (_isLoading)
            const Center(
              child: Card(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text('جاري الحصول على الموقع...'),
                    ],
                  ),
                ),
              ),
            ),

          // Error message
          if (_errorMessage != null)
            Positioned(
              top: 16,
              left: 16,
              right: 16,
              child: Card(
                color: Colors.orange.shade100,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      const Icon(Icons.warning_amber, color: Colors.orange),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: const TextStyle(fontSize: 14),
                        ),
                      ),
                      IconButton(
                        onPressed: () {
                          setState(() {
                            _errorMessage = null;
                          });
                        },
                        icon: const Icon(Icons.close, size: 20),
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                    ],
                  ),
                ),
              ),
            ),

          // Coordinates display
          if (_selectedLocation != null)
            Positioned(
              bottom: 100,
              left: 16,
              right: 16,
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'الموقع المختار',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          const Icon(Icons.location_on,
                              size: 16, color: Colors.red),
                          const SizedBox(width: 8),
                          Text(
                            '${_selectedLocation!.latitude.toStringAsFixed(6)}, '
                            '${_selectedLocation!.longitude.toStringAsFixed(6)}',
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.grey[700],
                              fontFamily: 'monospace',
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'انقر على الخريطة لتغيير الموقع',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[500],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

          // Zoom controls
          Positioned(
            bottom: 200,
            right: 16,
            child: Column(
              children: [
                _buildControlButton(
                  icon: Icons.add,
                  onPressed: () {
                    final currentZoom = _mapController.camera.zoom;
                    _mapController.move(
                      _mapController.camera.center,
                      currentZoom + 1,
                    );
                  },
                ),
                const SizedBox(height: 8),
                _buildControlButton(
                  icon: Icons.remove,
                  onPressed: () {
                    final currentZoom = _mapController.camera.zoom;
                    _mapController.move(
                      _mapController.camera.center,
                      currentZoom - 1,
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton(
            onPressed: _selectedLocation != null ? _confirmLocation : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolTheme.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.send),
                SizedBox(width: 8),
                Text(
                  'إرسال الموقع',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required VoidCallback onPressed,
  }) {
    return Material(
      elevation: 2,
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: Colors.grey[700]),
        ),
      ),
    );
  }
}

/// Custom location pin widget
/// أيقونة دبوس الموقع
class _LocationPin extends StatelessWidget {
  const _LocationPin();

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.all(4),
          decoration: BoxDecoration(
            color: Colors.red,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.3),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: const Icon(
            Icons.location_on,
            color: Colors.white,
            size: 24,
          ),
        ),
        // Pin tail/shadow
        Container(
          width: 3,
          height: 10,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.red.shade700,
                Colors.transparent,
              ],
            ),
          ),
        ),
      ],
    );
  }
}
