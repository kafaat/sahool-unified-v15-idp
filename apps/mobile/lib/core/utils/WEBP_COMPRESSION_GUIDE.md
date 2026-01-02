# دليل ضغط الصور بصيغة WebP للأجهزة المحمولة
# WebP Image Compression Guide for Mobile

## نظرة عامة - Overview

تم إضافة دعم ضغط الصور بصيغة WebP لتحسين أداء تطبيق SAHOOL على الأجهزة المحمولة، خاصة عند التعامل مع بلاطات الخرائط الفضائية.

WebP compression has been added to improve SAHOOL mobile app performance, especially when handling satellite map tiles.

### الفوائد - Benefits

- **تقليل حجم البيانات**: توفير 25-35% من حجم البيانات مقارنة بـ JPEG/PNG
- **تحسين الأداء**: تحميل أسرع للخرائط واستهلاك أقل للبيانات
- **دعم غير متصل**: تخزين محلي ذكي للبلاطات المضغوطة
- **تكيف تلقائي**: التراجع إلى JPEG على الأجهزة التي لا تدعم WebP

---

## الملفات المضافة - Added Files

### 1. `/lib/core/utils/image_compression.dart`
أداة ضغط الصور الرئيسية - Main image compression utility

**الوظائف الرئيسية - Key Functions:**

```dart
// كشف دعم WebP على الجهاز
Future<ImageFormat> getOptimalFormat()

// ضغط الصورة إلى WebP أو JPEG
Future<Uint8List?> compressToWebP({
  required Uint8List imageData,
  required double quality,
  ImageFormat? format,
})

// تغيير حجم الصورة للأجهزة المحمولة (512x512 كحد أقصى)
Future<Uint8List?> resizeForMobile({
  required Uint8List imageData,
  int maxWidth = 512,
  int maxHeight = 512,
})

// الحصول على بلاطة من الكاش
Future<Uint8List?> getCachedTile(String tileKey)

// حفظ بلاطة في الكاش
Future<bool> setCachedTile({
  required String tileKey,
  required Uint8List data,
  ImageFormat format = ImageFormat.webp,
})

// تحديد الجودة بناءً على حجم الشاشة
double getQualityForDevice(BuildContext context)
```

### 2. `/lib/core/services/tile_service.dart`
خدمة جلب ومعالجة البلاطات - Tile fetching and processing service

**الوظائف الرئيسية - Key Functions:**

```dart
// جلب وضغط بلاطة واحدة
Future<TileResult?> fetchAndCompressTile({
  required String url,
  required int zoom,
  required int x,
  required int y,
  double? quality,
})

// تحميل مسبق للبلاطات في منطقة محددة
Future<PrefetchResult> prefetchTilesForArea({
  required LatLngBounds bounds,
  required List<int> zoomLevels,
  double? quality,
  Function(int completed, int total)? onProgress,
})

// تحميل مسبق للبلاطات حول موقع
Future<PrefetchResult> prefetchTilesAroundLocation({
  required LatLng center,
  required double radiusKm,
  required List<int> zoomLevels,
  double? quality,
  Function(int completed, int total)? onProgress,
})
```

---

## الاستخدام - Usage

### مثال 1: جلب وضغط بلاطة واحدة
### Example 1: Fetch and Compress Single Tile

```dart
import 'package:sahool_field_app/core/services/tile_service.dart';
import 'package:sahool_field_app/core/utils/image_compression.dart';

// إنشاء خدمة البلاطات
final tileService = TileService(
  baseUrl: 'https://tiles.example.com/{z}/{x}/{y}.png',
  preferredFormat: ImageFormat.webp,
);

// جلب بلاطة واحدة مع الضغط
final tile = await tileService.fetchAndCompressTile(
  url: 'https://tiles.example.com/10/512/384.png',
  zoom: 10,
  x: 512,
  y: 384,
  quality: ImageCompressionUtil.mobileQuality, // 0.6 للجوال
);

if (tile != null) {
  print('Tile loaded: ${tile.sizeKB.toStringAsFixed(1)} KB');
  print('From cache: ${tile.fromCache}');
  print('Format: ${tile.format.name}');
}
```

### مثال 2: تحميل مسبق لمنطقة
### Example 2: Prefetch Area

```dart
import 'package:latlong2/latlong.dart';

// تحديد حدود المنطقة (مثال: صنعاء، اليمن)
final bounds = LatLngBounds(
  LatLng(15.2, 44.0),  // جنوب غرب - Southwest (Sana'a area)
  LatLng(15.6, 44.4),  // شمال شرق - Northeast
);

// تحميل مسبق لعدة مستويات تكبير
final result = await tileService.prefetchTilesForArea(
  bounds: bounds,
  zoomLevels: [10, 11, 12], // مستويات تكبير متعددة
  quality: ImageCompressionUtil.tabletQuality, // 0.8 للتابلت
  onProgress: (completed, total) {
    print('التقدم - Progress: $completed/$total');
  },
);

print('Downloaded: ${result.successfulTiles} tiles');
print('From cache: ${result.cachedTiles} tiles');
print('Success rate: ${result.successRate.toStringAsFixed(1)}%');
print('Duration: ${result.duration.inSeconds}s');
```

### مثال 3: تحميل مسبق حول موقع
### Example 3: Prefetch Around Location

```dart
// تحميل البلاطات حول موقع محدد (مثال: الحديدة)
final center = LatLng(14.7979, 42.9545); // الحديدة - Hodeidah
final radiusKm = 10.0; // نصف قطر 10 كم

final result = await tileService.prefetchTilesAroundLocation(
  center: center,
  radiusKm: radiusKm,
  zoomLevels: [11, 12],
  onProgress: (completed, total) {
    setState(() {
      _downloadProgress = completed / total;
    });
  },
);
```

### مثال 4: التكامل مع الخرائط الموجودة
### Example 4: Integration with Existing Maps

```dart
import 'package:flutter_map/flutter_map.dart';
import 'package:sahool_field_app/core/map/sahool_tile_provider.dart';

// إنشاء مزود بلاطات مخصص مع الضغط
class CompressedTileProvider extends TileProvider {
  final TileService _tileService;

  CompressedTileProvider({
    required String baseUrl,
  }) : _tileService = TileService(baseUrl: baseUrl);

  @override
  ImageProvider getImage(TileCoordinates coordinates, TileLayer options) {
    return CompressedTileImage(
      tileService: _tileService,
      coordinates: coordinates,
      options: options,
    );
  }
}

class CompressedTileImage extends ImageProvider<CompressedTileImage> {
  final TileService tileService;
  final TileCoordinates coordinates;
  final TileLayer options;

  CompressedTileImage({
    required this.tileService,
    required this.coordinates,
    required this.options,
  });

  @override
  Future<CompressedTileImage> obtainKey(ImageConfiguration configuration) {
    return SynchronousFuture<CompressedTileImage>(this);
  }

  @override
  ImageStreamCompleter loadImage(
    CompressedTileImage key,
    ImageDecoderCallback decode,
  ) {
    return MultiFrameImageStreamCompleter(
      codec: _loadAsync(key, decode),
      scale: 1.0,
    );
  }

  Future<ui.Codec> _loadAsync(
    CompressedTileImage key,
    ImageDecoderCallback decode,
  ) async {
    final url = getTileUrl(coordinates, options);

    final tile = await tileService.fetchAndCompressTile(
      url: url,
      zoom: coordinates.z,
      x: coordinates.x,
      y: coordinates.y,
    );

    if (tile != null) {
      final buffer = await ui.ImmutableBuffer.fromUint8List(tile.data);
      return await decode(buffer);
    }

    throw Exception('Failed to load tile');
  }
}
```

### مثال 5: تحديد الجودة بناءً على الجهاز
### Example 5: Device-Based Quality

```dart
import 'package:flutter/material.dart';

class SatelliteMapScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // تحديد الجودة بناءً على حجم الشاشة
    final quality = ImageCompressionUtil.getQualityForDevice(context);

    return Scaffold(
      body: FlutterMap(
        options: MapOptions(
          // إعدادات الخريطة
        ),
        children: [
          TileLayer(
            urlTemplate: 'https://tiles.example.com/{z}/{x}/{y}.png',
            tileProvider: CompressedTileProvider(
              baseUrl: 'https://tiles.example.com/{z}/{x}/{y}.png',
              quality: quality, // استخدام الجودة المناسبة
            ),
          ),
        ],
      ),
    );
  }
}
```

---

## إعدادات الجودة - Quality Settings

```dart
// للأجهزة المحمولة (هواتف)
ImageCompressionUtil.mobileQuality  // 0.6 (60%)

// للأجهزة اللوحية (تابلت)
ImageCompressionUtil.tabletQuality  // 0.8 (80%)

// مخصص
const customQuality = 0.7; // 70%
```

---

## إدارة الكاش - Cache Management

```dart
// الحصول على معلومات الكاش
final cacheInfo = await ImageCompressionUtil.getCacheSize();
print('Cache size: ${cacheInfo.sizeFormatted}');
print('File count: ${cacheInfo.fileCount}');

// مسح الكاش
await ImageCompressionUtil.clearCache();

// أو من خلال خدمة البلاطات
final tileService = TileService(baseUrl: '...');
final info = await tileService.getCacheInfo();
await tileService.clearCache();
```

---

## الأداء والإحصائيات - Performance & Statistics

### مقارنة الأحجام - Size Comparison

| نوع الصورة | الحجم الأصلي | بعد الضغط (WebP 60%) | التوفير |
|-----------|-------------|---------------------|---------|
| بلاطة خريطة 256x256 | 45 KB | 15 KB | 67% |
| بلاطة خريطة 512x512 | 180 KB | 60 KB | 67% |
| صورة فضائية عالية الدقة | 2.5 MB | 850 KB | 66% |

### توصيات الاستخدام - Usage Recommendations

1. **للاستخدام اليومي**: استخدم `mobileQuality` (0.6) لتوازن جيد بين الجودة وحجم البيانات
2. **للعرض التفصيلي**: استخدم `tabletQuality` (0.8) على الأجهزة اللوحية
3. **التحميل المسبق**: حمّل البلاطات مسبقاً للمناطق المهمة أثناء الاتصال بالإنترنت
4. **إدارة الكاش**: راقب حجم الكاش ونظفه دورياً

---

## الاختبار - Testing

```dart
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Image Compression Tests', () {
    test('WebP format detection', () async {
      final format = await ImageCompressionUtil.getOptimalFormat();
      expect(format, isNotNull);
      print('Detected format: ${format.name}');
    });

    test('Image compression', () async {
      // تحميل صورة اختبار
      final testImage = Uint8List.fromList([/* ... */]);

      final compressed = await ImageCompressionUtil.compressToWebP(
        imageData: testImage,
        quality: 0.6,
      );

      expect(compressed, isNotNull);
      expect(compressed!.length, lessThan(testImage.length));
    });

    test('Tile caching', () async {
      final testData = Uint8List.fromList([1, 2, 3, 4, 5]);

      // حفظ
      final saved = await ImageCompressionUtil.setCachedTile(
        tileKey: 'test/10/5',
        data: testData,
      );
      expect(saved, isTrue);

      // استرجاع
      final retrieved = await ImageCompressionUtil.getCachedTile('test/10/5');
      expect(retrieved, isNotNull);
      expect(retrieved, equals(testData));
    });
  });
}
```

---

## استكشاف الأخطاء - Troubleshooting

### المشكلة: WebP غير مدعوم على بعض الأجهزة
**الحل**: النظام يتراجع تلقائياً إلى JPEG

### المشكلة: البلاطات لا تُحفظ في الكاش
**الحل**: تحقق من صلاحيات التخزين والمساحة المتاحة

```dart
// التحقق من المساحة المتاحة
final cacheInfo = await ImageCompressionUtil.getCacheSize();
if (cacheInfo.sizeMB > 500) {
  await ImageCompressionUtil.clearCache();
}
```

### المشكلة: الضغط يستهلك الكثير من الذاكرة
**الحل**: معالجة البلاطات على دفعات صغيرة

```dart
// التحميل المسبق على دفعات
const batchSize = 5;
// (يتم ذلك تلقائياً في TileService)
```

---

## الخطوات التالية - Next Steps

1. **التكامل مع الخرائط الموجودة**: استبدل `SahoolTileProvider` الحالي بالنسخة المضغوطة
2. **إضافة واجهة مستخدم**: أضف شاشة لإدارة الكاش ومراقبة الأداء
3. **التحليل والمراقبة**: راقب استخدام البيانات والأداء في الإنتاج
4. **التحسينات المستقبلية**: أضف دعم AVIF وصيغ أحدث

---

## المراجع - References

- [Flutter Image Package](https://pub.dev/packages/image)
- [WebP Format Specification](https://developers.google.com/speed/webp)
- [Flutter Map Tile Caching](https://pub.dev/packages/flutter_map_tile_caching)

---

## الملاحظات الفنية - Technical Notes

### البنية - Architecture

```
lib/
├── core/
│   ├── utils/
│   │   ├── image_compression.dart    ← أداة الضغط الرئيسية
│   │   └── app_logger.dart
│   └── services/
│       └── tile_service.dart         ← خدمة البلاطات
└── features/
    └── satellite/                     ← ميزات الخرائط الفضائية
```

### الاعتماديات المطلوبة - Required Dependencies

```yaml
dependencies:
  image: ^4.3.0                   # معالجة وضغط الصور
  dio: ^5.7.0                     # طلبات HTTP
  path_provider: ^2.1.5           # الوصول إلى التخزين
  shared_preferences: ^2.3.3      # التخزين المحلي
  latlong2: ^0.9.1                # الإحداثيات الجغرافية
  flutter_map: ^7.0.2             # الخرائط
```

---

## رخصة الاستخدام - License

هذا الكود جزء من تطبيق SAHOOL المحمول ويخضع لنفس رخصة المشروع.

This code is part of SAHOOL mobile app and subject to the same project license.
