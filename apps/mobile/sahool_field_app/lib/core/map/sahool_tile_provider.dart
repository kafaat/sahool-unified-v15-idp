import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';

/// SAHOOL Tile Provider - مزود بلاطات الخريطة مع التخزين المحلي
///
/// يعمل بنظام:
/// 1. تحقق من وجود البلاطة محلياً (Cache Hit)
/// 2. إذا لم توجد، حملها من الشبكة (Cache Miss)
/// 3. احفظها محلياً للاستخدام لاحقاً (Offline Ready)
class SahoolTileProvider extends TileProvider {
  final Dio _dio;
  final String storeName;

  /// إنشاء مزود بلاطات جديد
  /// [storeName] اسم مجلد التخزين (افتراضي: sahool_map_cache)
  SahoolTileProvider({
    this.storeName = 'sahool_map_cache',
    Dio? dio,
  }) : _dio = dio ?? Dio();

  @override
  ImageProvider getImage(TileCoordinates coordinates, TileLayer options) {
    final url = getTileUrl(coordinates, options);

    return SahoolCachedTileImage(
      url: url,
      x: coordinates.x,
      y: coordinates.y,
      z: coordinates.z,
      storeName: storeName,
      dio: _dio,
    );
  }
}

/// ImageProvider مخصص للبلاطات مع دعم التخزين المحلي
class SahoolCachedTileImage extends ImageProvider<SahoolCachedTileImage> {
  final String url;
  final int x, y, z;
  final String storeName;
  final Dio dio;

  SahoolCachedTileImage({
    required this.url,
    required this.x,
    required this.y,
    required this.z,
    required this.storeName,
    required this.dio,
  });

  @override
  Future<SahoolCachedTileImage> obtainKey(ImageConfiguration configuration) {
    return SynchronousFuture<SahoolCachedTileImage>(this);
  }

  @override
  ImageStreamCompleter loadImage(
    SahoolCachedTileImage key,
    ImageDecoderCallback decode,
  ) {
    return MultiFrameImageStreamCompleter(
      codec: _loadAsync(key, decode),
      scale: 1.0,
      debugLabel: 'SahoolTile($z/$x/$y)',
      informationCollector: () => <DiagnosticsNode>[
        DiagnosticsProperty<String>('URL', url),
        DiagnosticsProperty<String>('Tile', '$z/$x/$y'),
      ],
    );
  }

  Future<ui.Codec> _loadAsync(
    SahoolCachedTileImage key,
    ImageDecoderCallback decode,
  ) async {
    try {
      // 1. تحديد مسار الملف في الهاتف
      final dir = await getApplicationDocumentsDirectory();
      final cacheDir = Directory('${dir.path}/${key.storeName}/$z');

      // إنشاء المجلد إذا لم يكن موجوداً
      if (!await cacheDir.exists()) {
        await cacheDir.create(recursive: true);
      }

      final File file = File('${cacheDir.path}/${key.x}_${key.y}.png');

      // 2. هل الملف موجود محلياً؟ (Offline Hit)
      if (await file.exists()) {
        final Uint8List bytes = await file.readAsBytes();
        if (bytes.isNotEmpty) {
          final buffer = await ui.ImmutableBuffer.fromUint8List(bytes);
          return await decode(buffer);
        }
      }

      // 3. غير موجود -> تحميل من الشبكة (Online Miss)
      final Response<List<int>> response = await key.dio.get<List<int>>(
        key.url,
        options: Options(
          responseType: ResponseType.bytes,
          receiveTimeout: const Duration(seconds: 10),
          sendTimeout: const Duration(seconds: 5),
        ),
      );

      if (response.data == null || response.data!.isEmpty) {
        throw Exception('Empty response');
      }

      final bytes = Uint8List.fromList(response.data!);

      // 4. حفظ الملف للمستقبل (Caching)
      // نحفظ بشكل غير متزامن لتجنب التأخير
      file.writeAsBytes(bytes).catchError((e) {
        debugPrint('Failed to cache tile: $e');
      });

      final buffer = await ui.ImmutableBuffer.fromUint8List(bytes);
      return await decode(buffer);
    } catch (e) {
      // في حالة الخطأ (لا نت ولا كاش)، نرجع صورة شفافة
      debugPrint('Tile load failed ($z/$x/$y): $e');
      return _transparentTile(decode);
    }
  }

  /// صورة شفافة 1x1 بكسل (للحالات التي لا يوجد فيها نت ولا كاش)
  Future<ui.Codec> _transparentTile(ImageDecoderCallback decode) async {
    // PNG شفاف 1x1 بكسل
    final Uint8List transparent = Uint8List.fromList([
      0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, // PNG signature
      0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52, // IHDR chunk
      0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
      0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, // IDAT chunk
      0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
      0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
      0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, // IEND chunk
      0x42, 0x60, 0x82,
    ]);
    final buffer = await ui.ImmutableBuffer.fromUint8List(transparent);
    return await decode(buffer);
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is SahoolCachedTileImage &&
        other.url == url &&
        other.z == z &&
        other.x == x &&
        other.y == y;
  }

  @override
  int get hashCode => Object.hash(url, z, x, y);

  @override
  String toString() => 'SahoolCachedTileImage($z/$x/$y)';
}
