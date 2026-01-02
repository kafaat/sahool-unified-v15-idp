import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'app_logger.dart';

/// أداة ضغط الصور للأجهزة المحمولة
/// Mobile Image Compression Utility
///
/// يوفر ضغط صور البلاطات الفضائية بصيغة WebP للأجهزة المحمولة
/// Provides WebP compression for satellite tiles optimized for mobile devices
///
/// Features:
/// - تحويل البلاطات إلى صيغة WebP - Convert tiles to WebP format
/// - دعم إعدادات الجودة للجوال والتابلت - Quality settings for mobile/tablet
/// - تغيير حجم الصور الكبيرة - Resize large images
/// - تخزين البلاطات المضغوطة محلياً - Cache compressed tiles locally
/// - التراجع إلى JPEG عند عدم دعم WebP - Fallback to JPEG if WebP not supported
class ImageCompressionUtil {
  static const String _cacheDir = 'compressed_tiles';
  static const String _formatKey = 'image_format_support';

  // إعدادات الجودة - Quality settings
  static const double mobileQuality = 0.6; // للجوال - Mobile
  static const double tabletQuality = 0.8; // للتابلت - Tablet

  // الحد الأقصى لحجم البلاطة - Maximum tile size
  static const int maxTileWidth = 512;
  static const int maxTileHeight = 512;

  /// كشف دعم صيغة WebP على الجهاز
  /// Detect WebP support on device
  static Future<ImageFormat> getOptimalFormat() async {
    try {
      final prefs = await SharedPreferences.getInstance();

      // تحقق من الكاش أولاً - Check cache first
      final cachedFormat = prefs.getString(_formatKey);
      if (cachedFormat != null) {
        return ImageFormat.values.firstWhere(
          (f) => f.toString() == cachedFormat,
          orElse: () => ImageFormat.jpeg,
        );
      }

      // اختبر دعم WebP - Test WebP support
      final supportsWebP = await _testWebPSupport();
      final format = supportsWebP ? ImageFormat.webp : ImageFormat.jpeg;

      // احفظ النتيجة - Cache result
      await prefs.setString(_formatKey, format.toString());

      AppLogger.i(
        'Image format detected: ${format.name}',
        tag: 'IMAGE_COMPRESSION',
      );

      return format;
    } catch (e) {
      AppLogger.e(
        'Failed to detect image format',
        tag: 'IMAGE_COMPRESSION',
        error: e,
      );
      return ImageFormat.jpeg; // التراجع إلى JPEG - Fallback to JPEG
    }
  }

  /// اختبار دعم WebP - Test WebP support
  static Future<bool> _testWebPSupport() async {
    try {
      // إنشاء صورة WebP بسيطة 1x1 - Create simple 1x1 WebP image
      final webpBytes = Uint8List.fromList([
        0x52, 0x49, 0x46, 0x46, 0x26, 0x00, 0x00, 0x00, // RIFF header
        0x57, 0x45, 0x42, 0x50, 0x56, 0x50, 0x38, 0x4C, // WEBP VP8L
        0x1A, 0x00, 0x00, 0x00, 0x2F, 0x00, 0x00, 0x00,
        0x10, 0x07, 0x10, 0x11, 0x11, 0x88, 0x88, 0xFE,
        0x07, 0x00,
      ]);

      // حاول فك تشفير الصورة - Try to decode
      final codec = await ui.instantiateImageCodec(webpBytes);
      final frame = await codec.getNextFrame();
      frame.image.dispose();
      codec.dispose();

      return true;
    } catch (e) {
      return false;
    }
  }

  /// ضغط الصورة إلى صيغة WebP أو JPEG
  /// Compress image to WebP or JPEG format
  ///
  /// [imageData] البيانات الأصلية للصورة - Original image data
  /// [quality] جودة الضغط (0.0 - 1.0) - Compression quality
  /// [format] الصيغة المستهدفة - Target format
  static Future<Uint8List?> compressToWebP({
    required Uint8List imageData,
    required double quality,
    ImageFormat? format,
  }) async {
    try {
      // حدد الصيغة المثلى إذا لم تُحدد - Determine optimal format if not specified
      format ??= await getOptimalFormat();

      // فك تشفير الصورة - Decode image
      final image = img.decodeImage(imageData);
      if (image == null) {
        AppLogger.e('Failed to decode image', tag: 'IMAGE_COMPRESSION');
        return null;
      }

      // ضغط حسب الصيغة - Compress based on format
      Uint8List? compressed;

      if (format == ImageFormat.webp) {
        // ضغط WebP - WebP compression
        compressed = img.encodeWebP(
          image,
          quality: (quality * 100).toInt(),
        );
      } else {
        // ضغط JPEG كبديل - JPEG compression as fallback
        compressed = img.encodeJpg(
          image,
          quality: (quality * 100).toInt(),
        );
      }

      if (compressed != null) {
        final originalSize = imageData.length / 1024; // KB
        final compressedSize = compressed.length / 1024; // KB
        final ratio = ((1 - (compressedSize / originalSize)) * 100);

        AppLogger.d(
          'Compressed: ${originalSize.toStringAsFixed(1)} KB → '
          '${compressedSize.toStringAsFixed(1)} KB '
          '(${ratio.toStringAsFixed(1)}% reduction)',
          tag: 'IMAGE_COMPRESSION',
        );
      }

      return compressed;
    } catch (e) {
      AppLogger.e(
        'Failed to compress image',
        tag: 'IMAGE_COMPRESSION',
        error: e,
      );
      return null;
    }
  }

  /// تغيير حجم الصورة للأجهزة المحمولة
  /// Resize image for mobile devices
  ///
  /// [imageData] البيانات الأصلية للصورة - Original image data
  /// [maxWidth] العرض الأقصى - Maximum width
  /// [maxHeight] الارتفاع الأقصى - Maximum height
  static Future<Uint8List?> resizeForMobile({
    required Uint8List imageData,
    int maxWidth = maxTileWidth,
    int maxHeight = maxTileHeight,
  }) async {
    try {
      // فك تشفير الصورة - Decode image
      final image = img.decodeImage(imageData);
      if (image == null) {
        AppLogger.e('Failed to decode image for resizing', tag: 'IMAGE_COMPRESSION');
        return null;
      }

      // تحقق من الحاجة لتغيير الحجم - Check if resizing needed
      if (image.width <= maxWidth && image.height <= maxHeight) {
        AppLogger.d(
          'Image already within limits (${image.width}x${image.height})',
          tag: 'IMAGE_COMPRESSION',
        );
        return imageData; // لا حاجة لتغيير الحجم - No need to resize
      }

      // احسب النسبة للحفاظ على الأبعاد - Calculate aspect ratio
      final aspectRatio = image.width / image.height;
      int newWidth = maxWidth;
      int newHeight = maxHeight;

      if (aspectRatio > 1) {
        // عرض أكبر من الارتفاع - Width > height
        newHeight = (newWidth / aspectRatio).round();
      } else {
        // ارتفاع أكبر من العرض - Height > width
        newWidth = (newHeight * aspectRatio).round();
      }

      // تغيير الحجم - Resize
      final resized = img.copyResize(
        image,
        width: newWidth,
        height: newHeight,
        interpolation: img.Interpolation.linear,
      );

      AppLogger.d(
        'Resized: ${image.width}x${image.height} → ${newWidth}x${newHeight}',
        tag: 'IMAGE_COMPRESSION',
      );

      // ترميز الصورة - Encode image
      return Uint8List.fromList(img.encodePng(resized));
    } catch (e) {
      AppLogger.e(
        'Failed to resize image',
        tag: 'IMAGE_COMPRESSION',
        error: e,
      );
      return null;
    }
  }

  /// الحصول على بلاطة من الكاش
  /// Get cached tile
  ///
  /// [tileKey] مفتاح البلاطة (مثال: "z/x/y") - Tile key (e.g., "z/x/y")
  static Future<Uint8List?> getCachedTile(String tileKey) async {
    try {
      final dir = await _getCacheDirectory();
      final file = File('${dir.path}/$tileKey.webp');

      if (await file.exists()) {
        final bytes = await file.readAsBytes();
        AppLogger.d('Cache HIT: $tileKey', tag: 'IMAGE_COMPRESSION');
        return bytes;
      }

      // حاول الحصول على JPEG إذا لم يوجد WebP - Try JPEG if WebP not found
      final jpegFile = File('${dir.path}/$tileKey.jpg');
      if (await jpegFile.exists()) {
        final bytes = await jpegFile.readAsBytes();
        AppLogger.d('Cache HIT (JPEG): $tileKey', tag: 'IMAGE_COMPRESSION');
        return bytes;
      }

      AppLogger.d('Cache MISS: $tileKey', tag: 'IMAGE_COMPRESSION');
      return null;
    } catch (e) {
      AppLogger.e(
        'Failed to get cached tile: $tileKey',
        tag: 'IMAGE_COMPRESSION',
        error: e,
      );
      return null;
    }
  }

  /// حفظ بلاطة في الكاش
  /// Set cached tile
  ///
  /// [tileKey] مفتاح البلاطة - Tile key
  /// [data] بيانات البلاطة - Tile data
  /// [format] صيغة الملف - File format
  static Future<bool> setCachedTile({
    required String tileKey,
    required Uint8List data,
    ImageFormat format = ImageFormat.webp,
  }) async {
    try {
      final dir = await _getCacheDirectory();

      // إنشاء المجلدات الفرعية - Create subdirectories
      final parts = tileKey.split('/');
      if (parts.length > 1) {
        final subDir = Directory('${dir.path}/${parts[0]}');
        if (!await subDir.exists()) {
          await subDir.create(recursive: true);
        }
      }

      // حدد امتداد الملف - Determine file extension
      final extension = format == ImageFormat.webp ? 'webp' : 'jpg';
      final file = File('${dir.path}/$tileKey.$extension');

      // احفظ الملف - Save file
      await file.writeAsBytes(data);

      AppLogger.d('Cached: $tileKey ($extension)', tag: 'IMAGE_COMPRESSION');
      return true;
    } catch (e) {
      AppLogger.e(
        'Failed to cache tile: $tileKey',
        tag: 'IMAGE_COMPRESSION',
        error: e,
      );
      return false;
    }
  }

  /// مسح الكاش
  /// Clear cache
  static Future<void> clearCache() async {
    try {
      final dir = await _getCacheDirectory();
      if (await dir.exists()) {
        await dir.delete(recursive: true);
        AppLogger.i('Tile cache cleared', tag: 'IMAGE_COMPRESSION');
      }
    } catch (e) {
      AppLogger.e(
        'Failed to clear cache',
        tag: 'IMAGE_COMPRESSION',
        error: e,
      );
    }
  }

  /// الحصول على حجم الكاش
  /// Get cache size
  static Future<CacheSizeInfo> getCacheSize() async {
    try {
      final dir = await _getCacheDirectory();
      if (!await dir.exists()) {
        return const CacheSizeInfo(sizeBytes: 0, fileCount: 0);
      }

      int totalSize = 0;
      int fileCount = 0;

      await for (final entity in dir.list(recursive: true)) {
        if (entity is File) {
          totalSize += await entity.length();
          fileCount++;
        }
      }

      return CacheSizeInfo(sizeBytes: totalSize, fileCount: fileCount);
    } catch (e) {
      AppLogger.e(
        'Failed to get cache size',
        tag: 'IMAGE_COMPRESSION',
        error: e,
      );
      return const CacheSizeInfo(sizeBytes: 0, fileCount: 0);
    }
  }

  /// الحصول على مسار مجلد الكاش
  /// Get cache directory path
  static Future<Directory> _getCacheDirectory() async {
    final appDir = await getApplicationDocumentsDirectory();
    final cacheDir = Directory('${appDir.path}/$_cacheDir');

    if (!await cacheDir.exists()) {
      await cacheDir.create(recursive: true);
    }

    return cacheDir;
  }

  /// تحديد جودة الضغط بناءً على حجم الشاشة
  /// Determine compression quality based on screen size
  static double getQualityForDevice(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;

    // تعتبر الأجهزة التي عرضها أكبر من 600 بكسل تابلت
    // Devices with width > 600px are considered tablets
    if (screenWidth > 600) {
      return tabletQuality;
    }

    return mobileQuality;
  }
}

/// صيغ الصور المدعومة
/// Supported image formats
enum ImageFormat {
  webp,
  jpeg,
}

extension ImageFormatExtension on ImageFormat {
  String get name {
    switch (this) {
      case ImageFormat.webp:
        return 'WebP';
      case ImageFormat.jpeg:
        return 'JPEG';
    }
  }

  String get extension {
    switch (this) {
      case ImageFormat.webp:
        return 'webp';
      case ImageFormat.jpeg:
        return 'jpg';
    }
  }
}

/// معلومات حجم الكاش
/// Cache size information
class CacheSizeInfo {
  final int sizeBytes;
  final int fileCount;

  const CacheSizeInfo({
    required this.sizeBytes,
    required this.fileCount,
  });

  double get sizeMB => sizeBytes / (1024 * 1024);
  double get sizeKB => sizeBytes / 1024;

  String get sizeFormatted {
    if (sizeBytes < 1024) {
      return '$sizeBytes B';
    } else if (sizeBytes < 1024 * 1024) {
      return '${sizeKB.toStringAsFixed(1)} KB';
    } else {
      return '${sizeMB.toStringAsFixed(1)} MB';
    }
  }

  @override
  String toString() => '$fileCount files, $sizeFormatted';
}
