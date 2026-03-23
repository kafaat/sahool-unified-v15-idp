/// Detection Screen - شاشة الكشف
///
/// Camera preview with real-time YOLO26 detection overlay.
/// Supports on-device and cloud inference with seamless switching.
library;

import 'dart:async';
import 'dart:io';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../data/yolo26_service.dart';
import '../domain/detection_model.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Providers - الموفرون
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for detection screen state
/// موفر حالة شاشة الكشف
final detectionScreenStateProvider =
    StateNotifierProvider<DetectionScreenNotifier, DetectionScreenState>((ref) {
  final yoloService = ref.watch(yolo26ServiceProvider);
  return DetectionScreenNotifier(yoloService);
});

/// Provider for inference mode (on-device vs cloud)
/// موفر وضع الاستدلال (على الجهاز أو سحابي)
final inferenceModeProvider = StateProvider<InferenceMode>((ref) {
  return InferenceMode.auto;
});

/// Inference mode enum
enum InferenceMode {
  auto,
  onDevice,
  cloud;

  String get displayName => switch (this) {
        auto => 'Auto',
        onDevice => 'On-Device',
        cloud => 'Cloud',
      };

  String get displayNameAr => switch (this) {
        auto => 'تلقائي',
        onDevice => 'على الجهاز',
        cloud => 'سحابي',
      };

  IconData get icon => switch (this) {
        auto => Icons.auto_mode,
        onDevice => Icons.phone_android,
        cloud => Icons.cloud,
      };
}

// ═══════════════════════════════════════════════════════════════════════════════
// State - الحالة
// ═══════════════════════════════════════════════════════════════════════════════

/// State for detection screen
/// حالة شاشة الكشف
class DetectionScreenState {
  final bool isLoading;
  final bool isDetecting;
  final bool isCameraInitialized;
  final Uint8List? capturedImage;
  final DetectionResult? result;
  final String? error;
  final String? errorAr;
  final List<Detection> liveDetections;
  final int processingTimeMs;
  final bool showBoundingBoxes;
  final bool showLabels;
  final DetectionType selectedType;

  const DetectionScreenState({
    this.isLoading = false,
    this.isDetecting = false,
    this.isCameraInitialized = false,
    this.capturedImage,
    this.result,
    this.error,
    this.errorAr,
    this.liveDetections = const [],
    this.processingTimeMs = 0,
    this.showBoundingBoxes = true,
    this.showLabels = true,
    this.selectedType = DetectionType.pest,
  });

  DetectionScreenState copyWith({
    bool? isLoading,
    bool? isDetecting,
    bool? isCameraInitialized,
    Uint8List? capturedImage,
    DetectionResult? result,
    String? error,
    String? errorAr,
    List<Detection>? liveDetections,
    int? processingTimeMs,
    bool? showBoundingBoxes,
    bool? showLabels,
    DetectionType? selectedType,
  }) {
    return DetectionScreenState(
      isLoading: isLoading ?? this.isLoading,
      isDetecting: isDetecting ?? this.isDetecting,
      isCameraInitialized: isCameraInitialized ?? this.isCameraInitialized,
      capturedImage: capturedImage ?? this.capturedImage,
      result: result ?? this.result,
      error: error,
      errorAr: errorAr,
      liveDetections: liveDetections ?? this.liveDetections,
      processingTimeMs: processingTimeMs ?? this.processingTimeMs,
      showBoundingBoxes: showBoundingBoxes ?? this.showBoundingBoxes,
      showLabels: showLabels ?? this.showLabels,
      selectedType: selectedType ?? this.selectedType,
    );
  }

  bool get hasResult => result != null;
  bool get hasError => error != null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Notifier - المُعلم
// ═══════════════════════════════════════════════════════════════════════════════

/// State notifier for detection screen
/// مُعلم الحالة لشاشة الكشف
class DetectionScreenNotifier extends StateNotifier<DetectionScreenState> {
  final Yolo26Service _yoloService;

  DetectionScreenNotifier(this._yoloService)
      : super(const DetectionScreenState());

  /// Set detection type
  void setDetectionType(DetectionType type) {
    state = state.copyWith(selectedType: type);
  }

  /// Toggle bounding boxes visibility
  void toggleBoundingBoxes() {
    state = state.copyWith(showBoundingBoxes: !state.showBoundingBoxes);
  }

  /// Toggle labels visibility
  void toggleLabels() {
    state = state.copyWith(showLabels: !state.showLabels);
  }

  /// Run detection on captured image
  Future<DetectionResult?> runDetection(
    Uint8List imageBytes, {
    String? fieldId,
    InferenceMode mode = InferenceMode.auto,
  }) async {
    state = state.copyWith(
      isDetecting: true,
      error: null,
      capturedImage: imageBytes,
    );

    try {
      final stopwatch = Stopwatch()..start();

      List<Detection> detections;

      switch (mode) {
        case InferenceMode.auto:
          detections = await _yoloService.detectWithFallback(
            imageBytes,
            type: state.selectedType,
            fieldId: fieldId,
          );
        case InferenceMode.onDevice:
          detections = switch (state.selectedType) {
            DetectionType.pest => await _yoloService.detectPests(
                imageBytes,
                fieldId: fieldId,
              ),
            DetectionType.disease => await _yoloService.detectDiseases(
                imageBytes,
                fieldId: fieldId,
              ),
            _ => await _yoloService.detectPests(
                imageBytes,
                fieldId: fieldId,
              ),
          };
        case InferenceMode.cloud:
          // Force cloud by using fallback when on-device fails
          detections = await _yoloService.detectWithFallback(
            imageBytes,
            type: state.selectedType,
            fieldId: fieldId,
          );
      }

      stopwatch.stop();

      final result = DetectionResult(
        resultId: DateTime.now().millisecondsSinceEpoch.toString(),
        detections: detections,
        processingTimeMs: stopwatch.elapsedMilliseconds,
        imageWidth: 0, // Will be updated with actual dimensions
        imageHeight: 0,
        source: detections.isEmpty
            ? DetectionSource.onDevice
            : detections.first.source,
        modelVersion: Yolo26Service.modelVersion,
        fieldId: fieldId,
        timestamp: DateTime.now(),
      );

      state = state.copyWith(
        isDetecting: false,
        result: result,
        liveDetections: detections,
        processingTimeMs: stopwatch.elapsedMilliseconds,
      );

      return result;
    } catch (e) {
      final error = e is Yolo26Exception ? e : Yolo26Exception('$e', 'خطأ');
      state = state.copyWith(
        isDetecting: false,
        error: error.message,
        errorAr: error.messageAr,
      );
      return null;
    }
  }

  /// Clear current detection
  void clearDetection() {
    state = state.copyWith(
      result: null,
      capturedImage: null,
      liveDetections: [],
      error: null,
    );
  }

  /// Update live detections for real-time preview
  void updateLiveDetections(List<Detection> detections, int processingTimeMs) {
    state = state.copyWith(
      liveDetections: detections,
      processingTimeMs: processingTimeMs,
    );
  }

  /// Set camera initialized status
  void setCameraInitialized(bool initialized) {
    state = state.copyWith(isCameraInitialized: initialized);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Detection Screen Widget - شاشة الكشف
// ═══════════════════════════════════════════════════════════════════════════════

/// Detection screen with camera preview and overlay
/// شاشة الكشف مع معاينة الكاميرا والتراكب
class DetectionScreen extends ConsumerStatefulWidget {
  final String? fieldId;
  final String? fieldName;
  final DetectionType? initialType;

  const DetectionScreen({
    super.key,
    this.fieldId,
    this.fieldName,
    this.initialType,
  });

  @override
  ConsumerState<DetectionScreen> createState() => _DetectionScreenState();
}

class _DetectionScreenState extends ConsumerState<DetectionScreen>
    with WidgetsBindingObserver {
  CameraController? _cameraController;
  List<CameraDescription>? _cameras;
  bool _isProcessingFrame = false;
  Timer? _processingTimer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeCamera();

    // Set initial detection type if provided
    if (widget.initialType != null) {
      Future.microtask(() {
        ref
            .read(detectionScreenStateProvider.notifier)
            .setDetectionType(widget.initialType!);
      });
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _cameraController?.dispose();
    _processingTimer?.cancel();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return;
    }

    if (state == AppLifecycleState.inactive) {
      _cameraController?.dispose();
    } else if (state == AppLifecycleState.resumed) {
      _initializeCamera();
    }
  }

  Future<void> _initializeCamera() async {
    try {
      _cameras = await availableCameras();
      if (_cameras == null || _cameras!.isEmpty) {
        throw Exception('No cameras available');
      }

      // Use back camera
      final camera = _cameras!.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.back,
        orElse: () => _cameras!.first,
      );

      _cameraController = CameraController(
        camera,
        ResolutionPreset.high,
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid
            ? ImageFormatGroup.yuv420
            : ImageFormatGroup.bgra8888,
      );

      await _cameraController!.initialize();

      if (mounted) {
        ref
            .read(detectionScreenStateProvider.notifier)
            .setCameraInitialized(true);
        setState(() {});
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل تهيئة الكاميرا: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _captureAndDetect() async {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return;
    }

    try {
      final image = await _cameraController!.takePicture();
      final bytes = await image.readAsBytes();

      await ref.read(detectionScreenStateProvider.notifier).runDetection(
            bytes,
            fieldId: widget.fieldId,
            mode: ref.read(inferenceModeProvider),
          );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل التقاط الصورة: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _pickFromGallery() async {
    try {
      final picker = ImagePicker();
      final image = await picker.pickImage(source: ImageSource.gallery);

      if (image != null) {
        final bytes = await image.readAsBytes();
        await ref.read(detectionScreenStateProvider.notifier).runDetection(
              bytes,
              fieldId: widget.fieldId,
              mode: ref.read(inferenceModeProvider),
            );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل اختيار الصورة: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(detectionScreenStateProvider);
    final inferenceMode = ref.watch(inferenceModeProvider);
    final onDeviceAvailable = ref.watch(onDeviceModelAvailableProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: Colors.black,
        appBar: AppBar(
          title: Text(widget.fieldName ?? 'كشف الآفات والأمراض'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            // Inference mode selector
            PopupMenuButton<InferenceMode>(
              icon: Icon(inferenceMode.icon),
              tooltip: 'وضع الاستدلال',
              onSelected: (mode) {
                ref.read(inferenceModeProvider.notifier).state = mode;
              },
              itemBuilder: (context) => InferenceMode.values.map((mode) {
                return PopupMenuItem(
                  value: mode,
                  child: Row(
                    children: [
                      Icon(mode.icon, size: 20),
                      const SizedBox(width: 8),
                      Text(mode.displayNameAr),
                      if (mode == inferenceMode)
                        const Padding(
                          padding: EdgeInsets.only(right: 8),
                          child: Icon(Icons.check, size: 16),
                        ),
                    ],
                  ),
                );
              }).toList(),
            ),

            // Detection type selector
            PopupMenuButton<DetectionType>(
              icon: Text(state.selectedType.icon,
                  style: const TextStyle(fontSize: 20)),
              tooltip: 'نوع الكشف',
              onSelected: (type) {
                ref
                    .read(detectionScreenStateProvider.notifier)
                    .setDetectionType(type);
              },
              itemBuilder: (context) => [
                DetectionType.pest,
                DetectionType.disease,
                DetectionType.plant,
              ].map((type) {
                return PopupMenuItem(
                  value: type,
                  child: Row(
                    children: [
                      Text(type.icon),
                      const SizedBox(width: 8),
                      Text(type.displayNameAr),
                    ],
                  ),
                );
              }).toList(),
            ),

            // Settings
            IconButton(
              icon: const Icon(Icons.settings),
              onPressed: () => _showSettings(context),
            ),
          ],
        ),
        body: Stack(
          children: [
            // Camera preview or captured image
            if (state.capturedImage != null)
              _buildCapturedImageView(state)
            else if (_cameraController != null &&
                _cameraController!.value.isInitialized)
              _buildCameraPreview(state)
            else
              const Center(
                child: CircularProgressIndicator(color: Colors.white),
              ),

            // Detection overlay
            if (state.showBoundingBoxes && state.liveDetections.isNotEmpty)
              _buildDetectionOverlay(state),

            // Status bar
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: _buildStatusBar(state, onDeviceAvailable, inferenceMode),
            ),

            // Results panel
            if (state.hasResult)
              Positioned(
                bottom: 100,
                left: 16,
                right: 16,
                child: _buildResultsPanel(state),
              ),

            // Loading indicator
            if (state.isDetecting)
              Container(
                color: Colors.black54,
                child: const Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      CircularProgressIndicator(color: Colors.white),
                      SizedBox(height: 16),
                      Text(
                        'جاري الكشف...',
                        style: TextStyle(color: Colors.white, fontSize: 16),
                      ),
                    ],
                  ),
                ),
              ),

            // Error message
            if (state.hasError)
              Positioned(
                bottom: 180,
                left: 16,
                right: 16,
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.withValues(alpha: 0.9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error, color: Colors.white),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          state.errorAr ?? state.error ?? 'خطأ غير معروف',
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white),
                        onPressed: () {
                          ref
                              .read(detectionScreenStateProvider.notifier)
                              .clearDetection();
                        },
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
        bottomNavigationBar: _buildBottomBar(state),
      ),
    );
  }

  Widget _buildCameraPreview(DetectionScreenState state) {
    return ClipRect(
      child: OverflowBox(
        alignment: Alignment.center,
        child: FittedBox(
          fit: BoxFit.cover,
          child: SizedBox(
            width: _cameraController!.value.previewSize?.height ?? 0,
            height: _cameraController!.value.previewSize?.width ?? 0,
            child: CameraPreview(_cameraController!),
          ),
        ),
      ),
    );
  }

  Widget _buildCapturedImageView(DetectionScreenState state) {
    return Image.memory(
      state.capturedImage!,
      fit: BoxFit.contain,
      width: double.infinity,
      height: double.infinity,
    );
  }

  Widget _buildDetectionOverlay(DetectionScreenState state) {
    return CustomPaint(
      size: Size.infinite,
      painter: DetectionOverlayPainter(
        detections: state.liveDetections,
        showLabels: state.showLabels,
      ),
    );
  }

  Widget _buildStatusBar(
    DetectionScreenState state,
    AsyncValue<bool> onDeviceAvailable,
    InferenceMode mode,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Colors.black87, Colors.transparent],
        ),
      ),
      child: SafeArea(
        bottom: false,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Detection type
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.white24,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(state.selectedType.icon),
                  const SizedBox(width: 4),
                  Text(
                    state.selectedType.displayNameAr,
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                  ),
                ],
              ),
            ),

            // On-device status
            onDeviceAvailable.when(
              data: (available) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: available
                      ? Colors.green.withValues(alpha: 0.3)
                      : Colors.orange.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      available ? Icons.phone_android : Icons.cloud,
                      color: Colors.white,
                      size: 16,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      available ? 'على الجهاز' : 'سحابي',
                      style: const TextStyle(color: Colors.white, fontSize: 12),
                    ),
                  ],
                ),
              ),
              loading: () => const SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              ),
              error: (_, __) => const Icon(
                Icons.error_outline,
                color: Colors.red,
                size: 16,
              ),
            ),

            // Processing time
            if (state.processingTimeMs > 0)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white24,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  '${state.processingTimeMs}ms',
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultsPanel(DetectionScreenState state) {
    final result = state.result!;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black26,
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'نتائج الكشف',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              Row(
                children: [
                  Icon(
                    result.source == DetectionSource.onDevice
                        ? Icons.phone_android
                        : Icons.cloud,
                    size: 16,
                    color: Colors.grey,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${result.processingTimeMs}ms',
                    style: const TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Detections count
          Row(
            children: [
              _buildCountChip('الكل', result.totalDetections, Colors.blue),
              if (result.pests.isNotEmpty)
                _buildCountChip('آفات', result.pests.length, Colors.orange),
              if (result.diseases.isNotEmpty)
                _buildCountChip('أمراض', result.diseases.length, Colors.red),
              if (result.plants.isNotEmpty)
                _buildCountChip('نباتات', result.plants.length, Colors.green),
            ],
          ),

          // Detection list (first 3)
          if (result.detections.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Divider(height: 1),
            const SizedBox(height: 8),
            ...result.detections.take(3).map((d) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      Text(d.detectionType.icon),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          d.classNameAr,
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: _getConfidenceColor(d.confidence)
                              .withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          d.confidencePercent,
                          style: TextStyle(
                            fontSize: 12,
                            color: _getConfidenceColor(d.confidence),
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                )),
            if (result.detections.length > 3)
              TextButton(
                onPressed: () => _showAllDetections(context, result),
                child: Text('عرض الكل (${result.totalDetections})'),
              ),
          ],
        ],
      ),
    );
  }

  Widget _buildCountChip(String label, int count, Color color) {
    return Padding(
      padding: const EdgeInsets.only(left: 8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Text(
          '$label: $count',
          style: TextStyle(
            fontSize: 12,
            color: color,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) return Colors.green;
    if (confidence >= 0.6) return Colors.orange;
    return Colors.red;
  }

  Widget _buildBottomBar(DetectionScreenState state) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
      decoration: const BoxDecoration(
        color: Colors.black,
      ),
      child: SafeArea(
        top: false,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            // Gallery button
            IconButton(
              onPressed: state.isDetecting ? null : _pickFromGallery,
              icon: const Icon(Icons.photo_library, size: 28),
              color: Colors.white,
              tooltip: 'اختيار من المعرض',
            ),

            // Capture button
            GestureDetector(
              onTap: state.isDetecting
                  ? null
                  : (state.capturedImage != null
                      ? () => ref
                          .read(detectionScreenStateProvider.notifier)
                          .clearDetection()
                      : _captureAndDetect),
              child: Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 4),
                  color: state.capturedImage != null
                      ? Colors.red
                      : Colors.transparent,
                ),
                child: state.capturedImage != null
                    ? const Icon(Icons.close, color: Colors.white, size: 32)
                    : Container(
                        margin: const EdgeInsets.all(4),
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.white,
                        ),
                      ),
              ),
            ),

            // Toggle overlay button
            IconButton(
              onPressed: () {
                ref
                    .read(detectionScreenStateProvider.notifier)
                    .toggleBoundingBoxes();
              },
              icon: Icon(
                state.showBoundingBoxes
                    ? Icons.visibility
                    : Icons.visibility_off,
                size: 28,
              ),
              color: Colors.white,
              tooltip: 'إظهار/إخفاء الإطارات',
            ),
          ],
        ),
      ),
    );
  }

  void _showSettings(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Consumer(
        builder: (context, ref, _) {
          final state = ref.watch(detectionScreenStateProvider);
          final settings = ref.watch(detectionSettingsProvider);

          return Directionality(
            textDirection: TextDirection.rtl,
            child: SafeArea(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text(
                      'إعدادات الكشف',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  SwitchListTile(
                    title: const Text('إظهار الإطارات'),
                    value: state.showBoundingBoxes,
                    onChanged: (_) {
                      ref
                          .read(detectionScreenStateProvider.notifier)
                          .toggleBoundingBoxes();
                    },
                  ),
                  SwitchListTile(
                    title: const Text('إظهار التسميات'),
                    value: state.showLabels,
                    onChanged: (_) {
                      ref
                          .read(detectionScreenStateProvider.notifier)
                          .toggleLabels();
                    },
                  ),
                  SwitchListTile(
                    title: const Text('تفضيل الاستدلال على الجهاز'),
                    subtitle: const Text('أسرع ويعمل بدون اتصال'),
                    value: settings.preferOnDevice,
                    onChanged: (value) {
                      ref.read(detectionSettingsProvider.notifier).state =
                          settings.copyWith(preferOnDevice: value);
                    },
                  ),
                  SwitchListTile(
                    title: const Text('تفعيل الاحتياط السحابي'),
                    subtitle: const Text(
                        'استخدام السحابة عند فشل الاستدلال على الجهاز'),
                    value: settings.enableFallback,
                    onChanged: (value) {
                      ref.read(detectionSettingsProvider.notifier).state =
                          settings.copyWith(enableFallback: value);
                    },
                  ),
                  ListTile(
                    title: const Text('عتبة الثقة'),
                    subtitle: Slider(
                      value: settings.confidenceThreshold,
                      min: 0.1,
                      max: 0.9,
                      divisions: 8,
                      label: '${(settings.confidenceThreshold * 100).toInt()}%',
                      onChanged: (value) {
                        ref.read(detectionSettingsProvider.notifier).state =
                            settings.copyWith(confidenceThreshold: value);
                      },
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  void _showAllDetections(BuildContext context, DetectionResult result) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: DraggableScrollableSheet(
          initialChildSize: 0.6,
          maxChildSize: 0.9,
          minChildSize: 0.3,
          expand: false,
          builder: (context, scrollController) => Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  'جميع الكشوفات (${result.totalDetections})',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Expanded(
                child: ListView.builder(
                  controller: scrollController,
                  itemCount: result.detections.length,
                  itemBuilder: (context, index) {
                    final detection = result.detections[index];
                    return ListTile(
                      leading: Text(
                        detection.detectionType.icon,
                        style: const TextStyle(fontSize: 24),
                      ),
                      title: Text(detection.classNameAr),
                      subtitle: Text(detection.className),
                      trailing: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: _getConfidenceColor(detection.confidence)
                              .withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          detection.confidencePercent,
                          style: TextStyle(
                            color: _getConfidenceColor(detection.confidence),
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Detection Overlay Painter - رسام تراكب الكشف
// ═══════════════════════════════════════════════════════════════════════════════

/// Custom painter for detection bounding boxes
/// رسام مخصص لإطارات حدود الكشف
class DetectionOverlayPainter extends CustomPainter {
  final List<Detection> detections;
  final bool showLabels;

  DetectionOverlayPainter({
    required this.detections,
    this.showLabels = true,
  });

  @override
  void paint(Canvas canvas, Size size) {
    for (final detection in detections) {
      final color = _getColorForType(detection.detectionType);

      // Draw bounding box
      final rect = Rect.fromLTWH(
        detection.bbox.x * size.width,
        detection.bbox.y * size.height,
        detection.bbox.width * size.width,
        detection.bbox.height * size.height,
      );

      final boxPaint = Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2;

      canvas.drawRect(rect, boxPaint);

      // Draw label background
      if (showLabels) {
        final label = '${detection.classNameAr} ${detection.confidencePercent}';

        final textSpan = TextSpan(
          text: label,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        );

        final textPainter = TextPainter(
          text: textSpan,
          textDirection: TextDirection.rtl,
        )..layout();

        final labelRect = Rect.fromLTWH(
          rect.left,
          rect.top - textPainter.height - 4,
          textPainter.width + 8,
          textPainter.height + 4,
        );

        final labelBgPaint = Paint()..color = color;
        canvas.drawRect(labelRect, labelBgPaint);

        textPainter.paint(
          canvas,
          Offset(rect.left + 4, rect.top - textPainter.height - 2),
        );
      }
    }
  }

  Color _getColorForType(DetectionType type) {
    return switch (type) {
      DetectionType.pest => Colors.orange,
      DetectionType.disease => Colors.red,
      DetectionType.weed => Colors.purple,
      DetectionType.plant => Colors.green,
      DetectionType.fruit => Colors.yellow,
      DetectionType.deficiency => Colors.cyan,
    };
  }

  @override
  bool shouldRepaint(covariant DetectionOverlayPainter oldDelegate) {
    return detections != oldDelegate.detections ||
        showLabels != oldDelegate.showLabels;
  }
}
