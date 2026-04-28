import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';

import '../../../../core/map/sahool_tile_provider.dart';
import '../../../../core/geo/geojson.dart';
import '../../../../core/services/integrations/ndvi_service.dart';
import '../../../ndvi/domain/spectral_index.dart';
import '../../../ndvi/ui/ndvi_tile_layer.dart';

/// شاشة خريطة الحقل مع طبقات NDVI
/// Field Map Screen with NDVI Layers
class FieldMapScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String? fieldName;
  final Map<String, dynamic>? initialCenter;

  const FieldMapScreen({
    super.key,
    required this.fieldId,
    this.fieldName,
    this.initialCenter,
  });

  @override
  ConsumerState<FieldMapScreen> createState() => _FieldMapScreenState();
}

class _FieldMapScreenState extends ConsumerState<FieldMapScreen> {
  // ── Layer toggles ─────────────────────────────────────────────────────────
  String _selectedLayer = 'satellite';
  bool _showZones = true;
  bool _showNdvi = false;
  bool _showNdwi = false;
  bool _showEvi = false;
  bool _showSavi = false;
  bool _showNdre = false;
  bool _showGpsTrack = false;
  bool _isTracking = false;
  String? _selectedZoneId;
  double _currentZoom = 15.0;

  // ── Spectral index API state ──────────────────────────────────────────────
  /// Live vegetation index values loaded from the backend API.
  /// Keys match [SpectralIndex.code] (e.g. 'NDVI', 'NDWI').
  final Map<String, double> _indexValues = {};
  bool _indexLoading = false;

  /// Error message: null = ok, non-null = shown in error banner.
  /// Distinguishes API failure (connectivity) from empty (no satellite coverage).
  String? _indexError;

  // ── Timeline state ────────────────────────────────────────────────────────
  /// Days back from today.  0 = live / most-recent data.
  int _daysBack = 0;

  /// Whether the timeline slider bar is visible on screen.
  bool _timelineVisible = false;

  /// Debounce timer so we don't fire an API call on every slider tick.
  Timer? _sliderDebounce;

  /// Actual satellite acquisition dates for this field, sorted newest-first.
  ///
  /// Loaded once from [NdviServiceConnector.getImagery] in [initState].
  /// The slider snaps to the nearest acquisition date on release so the user
  /// always navigates to real satellite passes instead of arbitrary day offsets.
  List<DateTime> _acquisitionDates = [];

  // ── Request generation counter ────────────────────────────────────────────
  /// Incremented on every new [_loadIndexValues] call.
  ///
  /// Each call captures the generation at start; before applying results it
  /// checks the counter hasn't advanced.  This discards stale responses that
  /// arrive after the slider has already moved to a newer position, preventing
  /// the "fast slider → wrong data applied" race condition.
  int _loadGeneration = 0;

  // ── In-memory index cache ─────────────────────────────────────────────────
  /// Live cache: "{fieldId}:live" → Map of all current spectral index values.
  ///
  /// Historical cache: "{fieldId}:NDVI:{YYYY-MM-DD}" → {"NDVI": value}.
  /// Historical entries store ONLY NDVI (the timeseries endpoint is NDVI-only);
  /// they are merged with the live multi-index map at display time to avoid
  /// serving stale NDWI/EVI/SAVI/NDRE values under a date-keyed cache entry.
  final Map<String, Map<String, double>> _indexCache = {};

  // ── Derived getters ───────────────────────────────────────────────────────

  /// Currently active spectral index for legend display
  SpectralIndex? get _activeIndex {
    if (_showNdvi) return SpectralIndex.ndvi;
    if (_showNdwi) return SpectralIndex.ndwi;
    if (_showEvi) return SpectralIndex.evi;
    if (_showSavi) return SpectralIndex.savi;
    if (_showNdre) return SpectralIndex.ndre;
    return null;
  }

  /// Effective date: null means "live / most recent".
  DateTime? get _effectiveDate =>
      _daysBack == 0 ? null : DateTime.now().subtract(Duration(days: _daysBack));

  /// Cache key for live (multi-index) entries: "{fieldId}:live"
  String get _liveCacheKey => '${widget.fieldId}:live';

  /// Cache key for a historical NDVI entry: "{fieldId}:NDVI:{YYYY-MM-DD}".
  ///
  /// Historical entries store ONLY NDVI because the timeseries endpoint is
  /// NDVI-specific. Using a separate key from the live entry prevents stale
  /// NDWI / EVI / SAVI values being returned as a cache hit for a date.
  String _historicalCacheKey(DateTime date) {
    final d =
        '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
    return '${widget.fieldId}:NDVI:$d';
  }

  // ── Map ───────────────────────────────────────────────────────────────────

  /// Map controller for programmatic camera control
  late final MapController _mapController;

  /// Field boundary coordinates (loaded from field data)
  List<LatLng> _fieldBoundary = [];

  /// Base URL of the NDVI backend service, cached to avoid ref.read in build.
  String _ndviBaseUrl = '';

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _loadFieldBoundary();
    _loadIndexValues();
    _loadAcquisitionDates();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Cache baseUrl once the ProviderScope is available.
    _ndviBaseUrl = ref.read(ndviServiceProvider).baseUrl;
  }

  @override
  void dispose() {
    _sliderDebounce?.cancel();
    _mapController.dispose();
    super.dispose();
  }

  /// Load field boundary from initial center data or fetch from repository
  void _loadFieldBoundary() {
    // Try to extract boundary from initialCenter if provided as GeoJSON
    if (widget.initialCenter != null) {
      final geometry = widget.initialCenter!['geometry'] as Map<String, dynamic>?;
      if (geometry != null && geometry['type'] == 'Polygon') {
        try {
          _fieldBoundary = GeoJson.parsePolygon(geometry);
        } catch (e) {
          // Fallback: use center point to create a small bounding area
          _createBoundaryFromCenter();
        }
      } else if (widget.initialCenter!['lat'] != null &&
          widget.initialCenter!['lng'] != null) {
        _createBoundaryFromCenter();
      }
    }
  }

  /// Create a small bounding area from center point (fallback)
  void _createBoundaryFromCenter() {
    final lat = (widget.initialCenter!['lat'] as num?)?.toDouble();
    final lng = (widget.initialCenter!['lng'] as num?)?.toDouble();
    if (lat != null && lng != null) {
      // Create a small polygon around the center (approximately 100m x 100m)
      const offset = 0.001; // ~100m at equator
      _fieldBoundary = [
        LatLng(lat - offset, lng - offset),
        LatLng(lat - offset, lng + offset),
        LatLng(lat + offset, lng + offset),
        LatLng(lat + offset, lng - offset),
      ];
    }
  }

  /// Unified index loader — handles both live data and historical timeseries.
  ///
  /// Uses [_effectiveDate] to determine which data to fetch:
  ///   - `null` → calls `getIndices()` for the latest multi-index snapshot
  ///   - `DateTime` → calls `getTimeseries()` and picks the closest point
  ///
  /// Results are cached with separate key namespaces:
  ///   - Live: [_liveCacheKey] → all indices
  ///   - Historical: [_historicalCacheKey] → NDVI only, merged at display time
  ///
  /// A generation counter guards against stale responses: if the slider moves
  /// while a request is in-flight the old response is silently discarded.
  Future<void> _loadIndexValues() async {
    final date = _effectiveDate;

    // ── Increment generation — any in-flight call with an older gen is stale ──
    final gen = ++_loadGeneration;

    // ── Cache hit ─────────────────────────────────────────────────────────────
    if (date == null && _indexCache.containsKey(_liveCacheKey)) {
      setState(() {
        _indexValues
          ..clear()
          ..addAll(_indexCache[_liveCacheKey]!);
        _indexError = null;
      });
      return;
    }
    if (date != null) {
      final histKey = _historicalCacheKey(date);
      if (_indexCache.containsKey(histKey)) {
        setState(() {
          _indexValues['NDVI'] = _indexCache[histKey]!['NDVI']!;
          _indexError = null;
        });
        return;
      }
    }

    if (_indexLoading) return;
    setState(() {
      _indexLoading = true;
      _indexError = null;
    });

    try {
      final service = ref.read(ndviServiceProvider);

      if (date == null) {
        // ── Live: fetch all current indices ─────────────────────────────────
        final result = await service.getIndices(widget.fieldId);
        if (!mounted || gen != _loadGeneration) return; // stale — discard

        result.when(
          success: (indices) {
            if (indices.isEmpty) {
              _indexError = 'لا تتوفر بيانات قمر صناعي\nNo satellite data for this field';
              return;
            }
            final updated = {
              for (final i in indices) i.name.toUpperCase(): i.value,
            };
            _indexCache[_liveCacheKey] = Map.unmodifiable(updated);
            _indexValues
              ..clear()
              ..addAll(updated);
          },
          failure: (message, _) {
            _indexError = 'فشل تحميل البيانات: $message\nCheck connectivity';
          },
        );
      } else {
        // ── Historical: pick closest timeseries point ────────────────────────
        final result = await service.getTimeseries(
          widget.fieldId,
          startDate: date.subtract(const Duration(days: 15)),
          endDate: date.add(const Duration(days: 15)),
        );
        if (!mounted || gen != _loadGeneration) return; // stale — discard

        result.when(
          success: (points) {
            if (points.isEmpty) {
              _indexError =
                  'لا تتوفر بيانات قمر صناعي لهذا التاريخ\nNo satellite coverage for selected date';
              return;
            }
            points.sort((a, b) => a.date
                .difference(date)
                .inDays
                .abs()
                .compareTo(b.date.difference(date).inDays.abs()));
            final ndviValue = points.first.value;
            // Store NDVI-only under its own historical key (never mix with
            // NDWI/EVI/SAVI/NDRE, which are only available from live fetch).
            _indexCache[_historicalCacheKey(date)] =
                Map.unmodifiable({'NDVI': ndviValue});
            // Merge: preserve all live indices, update only NDVI for this date.
            _indexValues['NDVI'] = ndviValue;
          },
          failure: (message, _) {
            _indexError = 'فشل تحميل التاريخ: $message\nCheck connectivity';
          },
        );
      }
    } catch (e) {
      if (mounted && gen == _loadGeneration) _indexError = 'خطأ غير متوقع\n$e';
    } finally {
      if (mounted && gen == _loadGeneration) setState(() => _indexLoading = false);
    }
  }

  /// Load actual satellite acquisition dates for temporal snap.
  ///
  /// Calls [NdviServiceConnector.getImagery] to retrieve the list of available
  /// satellite passes for this field.  The result is stored in [_acquisitionDates]
  /// (sorted newest-first) and used by [_snapToBestAcquisition] to constrain
  /// the slider to real observation dates rather than arbitrary day offsets.
  Future<void> _loadAcquisitionDates() async {
    final service = ref.read(ndviServiceProvider);
    final result = await service.getImagery(widget.fieldId);
    if (!mounted) return;

    result.when(
      success: (imagery) {
        if (imagery.isEmpty) return;
        final dates = imagery.map((i) => i.captureDate).toList()
          ..sort((a, b) => b.compareTo(a)); // newest first
        setState(() => _acquisitionDates = dates);
      },
      failure: (_, __) {
        // Best-effort — failure is silent; slider falls back to arbitrary day offsets.
      },
    );
  }

  /// Snap [rawDays] to the closest actual satellite acquisition day offset.
  ///
  /// Returns [rawDays] unchanged when [_acquisitionDates] is empty (fallback).
  int _snapToBestAcquisition(int rawDays) {
    if (_acquisitionDates.isEmpty) return rawDays;
    final now = DateTime.now();
    // Initial sentinel: one beyond the slider's 90-day maximum so any real
    // acquisition will immediately be closer.
    const maxSliderDays = 90;
    var bestDiff = maxSliderDays + 1;
    var bestDays = rawDays;
    for (final acq in _acquisitionDates) {
      final daysBack = now.difference(acq).inDays.clamp(0, maxSliderDays);
      final diff = (daysBack - rawDays).abs();
      if (diff < bestDiff) {
        bestDiff = diff;
        bestDays = daysBack;
      }
    }
    return bestDays;
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.fieldName ?? 'خريطة الحقل'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            // Loading spinner
            if (_indexLoading)
              const Padding(
                padding: EdgeInsets.all(12),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                ),
              ),
            // Timeline toggle — opens/closes the slider bar
            IconButton(
              icon: Icon(
                Icons.timeline,
                color: _timelineVisible ? Colors.amber : Colors.white,
              ),
              onPressed: () => setState(() => _timelineVisible = !_timelineVisible),
              tooltip: 'الجدول الزمني',
            ),
            IconButton(
              icon: const Icon(Icons.layers),
              onPressed: _showLayersSheet,
              tooltip: 'الطبقات',
            ),
            IconButton(
              icon: const Icon(Icons.my_location),
              onPressed: _centerOnField,
              tooltip: 'توسيط',
            ),
          ],
        ),
        body: Stack(
          children: [
            _buildMapView(),

            // شريط الأدوات العائم
            Positioned(
              top: 16,
              right: 16,
              child: _buildToolbar(),
            ),

            // Error / no-coverage banner (above toolbar)
            if (_indexError != null && !_indexLoading)
              _buildErrorBanner(),

            // Historical date chip (shown when not in timeline mode)
            if (!_timelineVisible && _daysBack > 0)
              Positioned(
                top: 12,
                left: 0,
                right: 0,
                child: Center(child: _buildDateChip()),
              ),

            // Timeline slider bar
            if (_timelineVisible)
              _buildTimelineBar(),

            // معلومات المنطقة المحددة
            if (_selectedZoneId != null)
              Positioned(
                bottom: _timelineVisible ? 180 : 100,
                left: 16,
                right: 16,
                child: _buildZoneInfoCard(),
              ),

            // مفتاح الألوان
            Positioned(
              bottom: 16,
              left: 16,
              child: _buildLegend(),
            ),
          ],
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _openDiagnosis,
          backgroundColor: const Color(0xFF367C2B),
          icon: const Icon(Icons.medical_services),
          label: const Text('تشخيص'),
        ),
      ),
    );
  }

  /// Date chip shown at top when viewing historical data without the timeline bar.
  Widget _buildDateChip() {
    final date = _effectiveDate!;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.7),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.calendar_today, size: 14, color: Colors.amber),
          const SizedBox(width: 6),
          Text(
            '${date.day}/${date.month}/${date.year}  (منذ $_daysBack يوم)',
            style: const TextStyle(color: Colors.white, fontSize: 13),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: () {
              setState(() => _daysBack = 0);
              _loadIndexValues();
            },
            child: const Icon(Icons.close, size: 14, color: Colors.white70),
          ),
        ],
      ),
    );
  }

  /// Floating timeline slider (0 = today/live … 90 = 90 days ago).
  ///
  /// On drag-end the slider snaps to the nearest actual satellite acquisition
  /// date via [_snapToBestAcquisition].  The API call is debounced 400 ms.
  Widget _buildTimelineBar() {
    final date = _effectiveDate;
    final label = date == null
        ? 'اليوم (حي)'
        : '${date.day}/${date.month}/${date.year}';

    // Sub-label: show whether this date is a real acquisition
    final bool isRealAcquisition = _acquisitionDates.isNotEmpty &&
        date != null &&
        _acquisitionDates.any((d) => d.difference(date).inDays.abs() <= 1);

    return Positioned(
      bottom: 90,
      left: 16,
      right: 16,
      child: Card(
        elevation: 6,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  const Icon(Icons.timeline, size: 16, color: Color(0xFF367C2B)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'التاريخ: $label',
                          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                        ),
                        if (date != null)
                          Text(
                            isRealAcquisition
                                ? '🛰️ تاريخ مرور فعلي للقمر'
                                : (_acquisitionDates.isEmpty
                                    ? 'جارٍ تحميل مواعيد الاستشعار…'
                                    : 'تقريبي — سيُضبط لأقرب مرور'),
                            style: TextStyle(
                              fontSize: 10,
                              color: isRealAcquisition
                                  ? Colors.green.shade700
                                  : Colors.grey.shade600,
                            ),
                          ),
                      ],
                    ),
                  ),
                  if (_indexLoading)
                    const SizedBox(
                      width: 14,
                      height: 14,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                ],
              ),
              Row(
                children: [
                  const Text('−90', style: TextStyle(fontSize: 11, color: Colors.grey)),
                  Expanded(
                    child: Slider(
                      value: _daysBack.toDouble(),
                      min: 0,
                      max: 90,
                      divisions: 90,
                      activeColor: const Color(0xFF367C2B),
                      label: _daysBack == 0 ? 'اليوم' : '−$_daysBack يوم',
                      onChanged: (v) => setState(() => _daysBack = v.round()),
                      onChangeEnd: (v) {
                        // Snap to nearest real acquisition date, then debounce fetch
                        final snapped = _snapToBestAcquisition(v.round());
                        if (snapped != _daysBack) setState(() => _daysBack = snapped);
                        _sliderDebounce?.cancel();
                        _sliderDebounce = Timer(
                          const Duration(milliseconds: 400),
                          _loadIndexValues,
                        );
                      },
                    ),
                  ),
                  const Text('اليوم', style: TextStyle(fontSize: 11, color: Colors.grey)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }


  /// Error / no-coverage banner displayed below the AppBar.
  ///
  /// Tapping the refresh icon retries [_loadIndexValues].
  Widget _buildErrorBanner() {
    final isNoCoverage = _indexError!.contains('لا تتوفر');
    return Positioned(
      top: 8,
      left: 16,
      right: 16,
      child: Material(
        elevation: 4,
        borderRadius: BorderRadius.circular(12),
        color: isNoCoverage ? Colors.orange.shade700 : Colors.red.shade700,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          child: Row(
            children: [
              Icon(
                isNoCoverage ? Icons.cloud_off : Icons.wifi_off,
                color: Colors.white,
                size: 18,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  _indexError!,
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                ),
              ),
              GestureDetector(
                onTap: _loadIndexValues,
                child: const Icon(Icons.refresh, color: Colors.white, size: 18),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMapView() {
    // Determine center point
    final center = _fieldBoundary.isNotEmpty
        ? GeoJson.calculateCentroid(_fieldBoundary)
        : (widget.initialCenter != null
            ? LatLng(
                (widget.initialCenter!['lat'] as num?)?.toDouble() ?? 15.3694,
                (widget.initialCenter!['lng'] as num?)?.toDouble() ?? 44.1910,
              )
            : const LatLng(15.3694, 44.1910));

    // Determine tile URL based on selected layer
    final String tileUrl;
    switch (_selectedLayer) {
      case 'satellite':
        tileUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
        break;
      case 'terrain':
        tileUrl = 'https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png';
        break;
      default:
        tileUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
    }

    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: center,
        initialZoom: _currentZoom,
        onPositionChanged: (position, hasGesture) {
          if (hasGesture && mounted) {
            setState(() => _currentZoom = position.zoom ?? _currentZoom);
          }
        },
        onTap: (tapPosition, point) {
          if (_selectedZoneId != null) {
            setState(() => _selectedZoneId = null);
          }
        },
      ),
      children: [
        // Base tile layer
        TileLayer(
          urlTemplate: tileUrl,
          userAgentPackageName: 'com.sahool.field',
          maxZoom: 19,
          tileProvider: SahoolTileProvider(),
        ),

        // Field boundary — outline only (no fill) so raster tiles show through
        if (_fieldBoundary.isNotEmpty)
          PolygonLayer(
            polygons: [
              Polygon(
                points: _fieldBoundary,
                color: Colors.transparent,   // raster fills the field, not a solid colour
                borderColor: const Color(0xFF367C2B),
                borderStrokeWidth: 3,
              ),
            ],
          ),

        // Per-index field-scoped raster WMS tiles (raster-first, no polygon fill)
        ..._buildSpectralOverlays(),

        // Center marker
        MarkerLayer(
          markers: [
            Marker(
              point: center,
              width: 40,
              height: 40,
              child: Icon(
                _isTracking ? Icons.my_location : Icons.location_on,
                size: 36,
                color: _isTracking ? Colors.blue : const Color(0xFF367C2B),
              ),
            ),
          ],
        ),

        // Tracking indicator
        if (_isTracking)
          MarkerLayer(
            markers: [
              Marker(
                point: center,
                width: 100,
                height: 100,
                child: Container(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.blue.withValues(alpha: 0.15),
                    border: Border.all(color: Colors.blue.withValues(alpha: 0.4), width: 2),
                  ),
                ),
              ),
            ],
          ),
      ],
    );
  }

  /// Build per-index field-scoped WMS raster tile overlays.
  ///
  /// Each active spectral index gets its own [NdviTileLayerWidget] with a
  /// unique URL that includes `field_id`, `index`, and optionally `date`.
  /// The backend is responsible for clipping tiles to the field boundary
  /// (server-side masking) so only the field area is coloured.
  ///
  /// No polygon fill is applied — the raster provides per-pixel values.
  List<Widget> _buildSpectralOverlays() {
    final activeIndices = <SpectralIndex>[
      if (_showNdvi) SpectralIndex.ndvi,
      if (_showNdwi) SpectralIndex.ndwi,
      if (_showEvi) SpectralIndex.evi,
      if (_showSavi) SpectralIndex.savi,
      if (_showNdre) SpectralIndex.ndre,
    ];

    return [
      for (final idx in activeIndices)
        NdviTileLayerWidget(
          key: ValueKey('tile_${idx.code}_${_daysBack}'),
          config: NdviTileConfig.sahoolBackend(
            baseUrl: _ndviBaseUrl,
            fieldId: widget.fieldId,
            index: idx,
            date: _effectiveDate,
          ),
          visible: true,
        ),
    ];
  }

  Widget _buildToolbar() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildToolButton(
              icon: Icons.add,
              onPressed: () {
                final zoom = _mapController.camera.zoom;
                _mapController.move(_mapController.camera.center, zoom + 1);
              },
              tooltip: 'تكبير',
            ),
            _buildToolButton(
              icon: Icons.remove,
              onPressed: () {
                final zoom = _mapController.camera.zoom;
                _mapController.move(_mapController.camera.center, zoom - 1);
              },
              tooltip: 'تصغير',
            ),
            const Divider(height: 16),
            _buildToolButton(
              icon: Icons.crop_square,
              isActive: _showZones,
              onPressed: () => setState(() => _showZones = !_showZones),
              tooltip: 'المناطق',
            ),
            // Spectral index toggles
            _buildToolButton(
              icon: SpectralIndex.ndvi.icon,
              isActive: _showNdvi,
              activeColor: SpectralColormap.getColor(SpectralIndex.ndvi, 0.6),
              onPressed: () => setState(() => _showNdvi = !_showNdvi),
              tooltip: 'NDVI',
            ),
            _buildToolButton(
              icon: SpectralIndex.ndwi.icon,
              isActive: _showNdwi,
              activeColor: SpectralColormap.getColor(SpectralIndex.ndwi, 0.4),
              onPressed: () => setState(() => _showNdwi = !_showNdwi),
              tooltip: 'NDWI',
            ),
            _buildToolButton(
              icon: SpectralIndex.evi.icon,
              isActive: _showEvi,
              activeColor: SpectralColormap.getColor(SpectralIndex.evi, 0.5),
              onPressed: () => setState(() => _showEvi = !_showEvi),
              tooltip: 'EVI',
            ),
            _buildToolButton(
              icon: SpectralIndex.savi.icon,
              isActive: _showSavi,
              activeColor: SpectralColormap.getColor(SpectralIndex.savi, 0.5),
              onPressed: () => setState(() => _showSavi = !_showSavi),
              tooltip: 'SAVI',
            ),
            _buildToolButton(
              icon: SpectralIndex.ndre.icon,
              isActive: _showNdre,
              activeColor: SpectralColormap.getColor(SpectralIndex.ndre, 0.4),
              onPressed: () => setState(() => _showNdre = !_showNdre),
              tooltip: 'NDRE',
            ),
            const Divider(height: 16),
            _buildToolButton(
              icon: Icons.gps_fixed,
              isActive: _showGpsTrack,
              activeColor: Colors.orange,
              onPressed: () => setState(() => _showGpsTrack = !_showGpsTrack),
              tooltip: 'تتبع GPS',
            ),
            _buildToolButton(
              icon: _isTracking ? Icons.gps_off : Icons.my_location,
              isActive: _isTracking,
              activeColor: Colors.blue,
              onPressed: () => setState(() => _isTracking = !_isTracking),
              tooltip: _isTracking ? 'إيقاف التتبع' : 'بدء التتبع',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildToolButton({
    required IconData icon,
    required VoidCallback onPressed,
    required String tooltip,
    bool isActive = false,
    Color? activeColor,
  }) {
    final color = activeColor ?? const Color(0xFF367C2B);
    return Tooltip(
      message: tooltip,
      child: IconButton(
        icon: Icon(
          icon,
          color: isActive ? color : Colors.grey[600],
        ),
        onPressed: onPressed,
        style: IconButton.styleFrom(
          backgroundColor: isActive ? color.withValues(alpha: 0.1) : Colors.transparent,
        ),
      ),
    );
  }

  Widget _buildZoneInfoCard() {
    // Helper: render one index value from live API data (or '—' if not loaded)
    Widget liveIndicator(SpectralIndex idx) {
      final v = _indexValues[idx.code];
      return _buildIndicator(
        idx.code,
        v != null ? v.toStringAsFixed(2) : '—',
        v != null ? SpectralColormap.getColor(idx, v) : Colors.grey,
      );
    }

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF367C2B).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.location_on,
                    color: Color(0xFF367C2B),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'المنطقة $_selectedZoneId',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        _indexValues.isEmpty ? 'جارٍ التحميل…' : 'بيانات المؤشرات الحية',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => setState(() => _selectedZoneId = null),
                ),
              ],
            ),
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                liveIndicator(SpectralIndex.ndvi),
                liveIndicator(SpectralIndex.ndwi),
                liveIndicator(SpectralIndex.ndre),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                liveIndicator(SpectralIndex.evi),
                liveIndicator(SpectralIndex.savi),
                liveIndicator(SpectralIndex.lai),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      context.push('/satellite/${widget.fieldId}', extra: {
                        'fieldName': widget.fieldName,
                      });
                    },
                    icon: const Icon(Icons.timeline),
                    label: const Text('السلسلة الزمنية'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      context.push('/crop-health', extra: {
                        'fieldId': widget.fieldId,
                        'fieldName': widget.fieldName,
                      });
                    },
                    icon: const Icon(Icons.medical_services),
                    label: const Text('تشخيص'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF367C2B),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIndicator(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 12,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
      ],
    );
  }

  Widget _buildLegend() {
    final idx = _activeIndex;
    if (idx == null) return const SizedBox.shrink();

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(idx.icon, size: 16,
                    color: SpectralColormap.getColor(idx, 0.6)),
                const SizedBox(width: 6),
                Text(
                  idx.code,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              idx.nameAr,
              style: TextStyle(fontSize: 10, color: Colors.grey[600]),
            ),
            const SizedBox(height: 8),
            Container(
              width: 150,
              height: 16,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(4),
                gradient: LinearGradient(
                  colors: SpectralColormap.generateGradient(idx, steps: 20),
                ),
              ),
            ),
            const SizedBox(height: 4),
            SizedBox(
              width: 150,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    idx.minValue.toStringAsFixed(1),
                    style: const TextStyle(fontSize: 10),
                  ),
                  Text(
                    idx.maxValue.toStringAsFixed(1),
                    style: const TextStyle(fontSize: 10),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showLayersSheet() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                  'طبقات الخريطة',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const Divider(),
              ListTile(
                leading: const Icon(Icons.satellite_alt),
                title: const Text('القمر الصناعي'),
                trailing: _selectedLayer == 'satellite'
                    ? const Icon(Icons.check, color: Color(0xFF367C2B))
                    : null,
                onTap: () {
                  setState(() => _selectedLayer = 'satellite');
                  Navigator.pop(context);
                },
              ),
              ListTile(
                leading: const Icon(Icons.terrain),
                title: const Text('التضاريس'),
                trailing: _selectedLayer == 'terrain'
                    ? const Icon(Icons.check, color: Color(0xFF367C2B))
                    : null,
                onTap: () {
                  setState(() => _selectedLayer = 'terrain');
                  Navigator.pop(context);
                },
              ),
              ListTile(
                leading: const Icon(Icons.map),
                title: const Text('الشوارع'),
                trailing: _selectedLayer == 'streets'
                    ? const Icon(Icons.check, color: Color(0xFF367C2B))
                    : null,
                onTap: () {
                  setState(() => _selectedLayer = 'streets');
                  Navigator.pop(context);
                },
              ),
              const Divider(),
              SwitchListTile(
                secondary: const Icon(Icons.crop_square),
                title: const Text('عرض المناطق'),
                value: _showZones,
                onChanged: (v) {
                  setState(() => _showZones = v);
                },
                activeColor: const Color(0xFF367C2B),
              ),
              // Spectral index toggles
              SwitchListTile(
                secondary: Icon(SpectralIndex.ndvi.icon),
                title: const Text('طبقة NDVI - الغطاء النباتي'),
                value: _showNdvi,
                onChanged: (v) => setState(() => _showNdvi = v),
                activeColor: const Color(0xFF367C2B),
              ),
              SwitchListTile(
                secondary: Icon(SpectralIndex.ndwi.icon),
                title: const Text('طبقة NDWI - محتوى المياه'),
                value: _showNdwi,
                onChanged: (v) => setState(() => _showNdwi = v),
                activeColor: const Color(0xFF1E90FF),
              ),
              SwitchListTile(
                secondary: Icon(SpectralIndex.evi.icon),
                title: const Text('طبقة EVI - النبات المحسّن'),
                value: _showEvi,
                onChanged: (v) => setState(() => _showEvi = v),
                activeColor: const Color(0xFF2E8B57),
              ),
              SwitchListTile(
                secondary: Icon(SpectralIndex.savi.icon),
                title: const Text('طبقة SAVI - المعدّل للتربة'),
                value: _showSavi,
                onChanged: (v) => setState(() => _showSavi = v),
                activeColor: const Color(0xFF6B8E23),
              ),
              SwitchListTile(
                secondary: Icon(SpectralIndex.ndre.icon),
                title: const Text('طبقة NDRE - النيتروجين'),
                value: _showNdre,
                onChanged: (v) => setState(() => _showNdre = v),
                activeColor: const Color(0xFF32CD32),
              ),
              const Divider(),
              ListTile(
                leading: _indexLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.refresh, color: Color(0xFF367C2B)),
                title: Text(
                  _indexLoading ? 'جارٍ تحديث البيانات…' : 'تحديث بيانات المؤشرات',
                ),
                subtitle: _indexValues.isEmpty
                    ? const Text('لا توجد بيانات بعد')
                    : Text(
                        _indexValues.entries
                            .map((e) => '${e.key}: ${e.value.toStringAsFixed(2)}')
                            .join(' · '),
                        style: const TextStyle(fontSize: 11),
                      ),
                onTap: _indexLoading
                    ? null
                    : () {
                        Navigator.pop(context);
                        _loadIndexValues();
                      },
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  /// Center map on field bounds with padding and smooth animation
  ///
  /// Calculates the bounding box of the field geometry and uses
  /// the map controller to fit the bounds with appropriate padding.
  void _centerOnField() {
    // Check if we have field boundary data
    if (_fieldBoundary.isEmpty) {
      // Try to use initialCenter as fallback
      if (widget.initialCenter != null) {
        final lat = (widget.initialCenter!['lat'] as num?)?.toDouble();
        final lng = (widget.initialCenter!['lng'] as num?)?.toDouble();
        if (lat != null && lng != null) {
          // Animate to center point with default zoom
          _mapController.move(
            LatLng(lat, lng),
            16.0, // Default zoom for single point
          );
          setState(() => _currentZoom = 16.0);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('تم التوسيط على موقع الحقل'),
              duration: Duration(seconds: 2),
            ),
          );
          return;
        }
      }

      // No boundary or center data available
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('لا تتوفر بيانات حدود الحقل'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    // Calculate the bounding box of the field geometry
    final bounds = GeoJson.calculateBounds(_fieldBoundary);

    // Add padding around the field (in screen pixels)
    // This ensures the field boundary is not flush against the screen edges
    const EdgeInsets padding = EdgeInsets.all(50.0);

    // Use fitCamera to fit the bounds with padding and animation
    // CameraFit.bounds calculates the optimal center and zoom level
    _mapController.fitCamera(
      CameraFit.bounds(
        bounds: bounds,
        padding: padding,
        // Maximum zoom level to prevent over-zooming on small fields
        maxZoom: 18.0,
      ),
    );

    // Update the current zoom state to reflect the new camera position
    // Note: The actual zoom is calculated by fitCamera based on bounds
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        setState(() {
          _currentZoom = _mapController.camera.zoom;
        });
      }
    });

    // Show feedback to user
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم التوسيط على حدود الحقل'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _openDiagnosis() {
    context.push('/crop-health', extra: {
      'fieldId': widget.fieldId,
      'fieldName': widget.fieldName,
    });
  }
}
