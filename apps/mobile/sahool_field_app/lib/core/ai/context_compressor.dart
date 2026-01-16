import 'dart:convert';
import 'dart:math' as math;
import 'package:flutter/foundation.dart';
import 'package:crypto/crypto.dart';

/// Context Compressor - Client-side compression for AI skills
///
/// Reduces context payload size for offline-first scenarios:
/// - Removes redundant fields
/// - Compresses GIS coordinates
/// - Deduplicates entity references
/// - Implements selective field pruning
class ContextCompressor {
  /// Maximum context size in bytes (500KB)
  static const int maxContextSize = 500 * 1024;

  /// Compression threshold - compress if payload > 100KB
  static const int compressionThreshold = 100 * 1024;

  /// Coordinate precision for quantization (4 decimal places = ~11m accuracy)
  static const int coordinatePrecision = 4;

  /// Maximum history items to retain
  static const int maxHistoryItems = 50;

  /// Compress context to reduce payload size
  ///
  /// Strategy:
  /// 1. Remove null values
  /// 2. Quantize coordinates to reduce precision
  /// 3. Remove duplicate references
  /// 4. Truncate history
  /// 5. Calculate checksum
  ///
  /// Returns compressed context JSON and metadata
  static Map<String, dynamic> compress(
    Map<String, dynamic> context, {
    bool aggressive = false,
  }) {
    final startSize = jsonEncode(context).length;

    // Create working copy
    var compressed = _deepCopy(context);

    // Phase 1: Remove null values (safe)
    compressed = _removeNullValues(compressed);

    // Phase 2: Compress coordinates if GIS data present
    compressed = _compressCoordinates(compressed);

    // Phase 3: Deduplicate references
    compressed = _deduplicateReferences(compressed);

    // Phase 4: Truncate history
    compressed = _truncateHistory(compressed, aggressive);

    // Phase 5: Aggressive compression if needed
    if (aggressive) {
      compressed = _aggressiveCompress(compressed);
    }

    final endSize = jsonEncode(compressed).length;
    final compressionRatio = startSize > 0 ? (endSize / startSize * 100).round() : 0;

    if (kDebugMode) {
      debugPrint(
        '🗜️  Context compression: ${startSize}B → ${endSize}B (${compressionRatio}%)',
      );
    }

    return {
      'context': compressed,
      'metadata': {
        'original_size': startSize,
        'compressed_size': endSize,
        'compression_ratio': compressionRatio,
        'compressed_at': DateTime.now().toIso8601String(),
        'checksum': _calculateChecksum(compressed),
      },
    };
  }

  /// Decompress context (restore full structure)
  static Map<String, dynamic> decompress(Map<String, dynamic> payload) {
    final compressed = payload['context'] as Map<String, dynamic>?;
    final metadata = payload['metadata'] as Map<String, dynamic>?;

    if (compressed == null) {
      throw ArgumentError('Missing "context" in payload');
    }

    // Verify integrity
    if (metadata != null && metadata.containsKey('checksum')) {
      final expectedChecksum = metadata['checksum'] as String;
      final actualChecksum = _calculateChecksum(compressed);
      if (expectedChecksum != actualChecksum) {
        throw Exception('Checksum mismatch - context may be corrupted');
      }
    }

    return _deepCopy(compressed);
  }

  /// Check if context needs compression
  static bool needsCompression(Map<String, dynamic> context) {
    final size = jsonEncode(context).length;
    return size > compressionThreshold;
  }

  // ============================================================
  // Private Compression Strategies
  // ============================================================

  /// Remove all null values recursively
  static Map<String, dynamic> _removeNullValues(
    Map<String, dynamic> data,
  ) {
    final result = <String, dynamic>{};

    data.forEach((key, value) {
      if (value == null) {
        // Skip null values
      } else if (value is Map<String, dynamic>) {
        final compressed = _removeNullValues(value);
        if (compressed.isNotEmpty) {
          result[key] = compressed;
        }
      } else if (value is List) {
        final filtered = value.whereType<dynamic>().where((v) => v != null).toList();
        if (filtered.isNotEmpty) {
          result[key] = filtered;
        }
      } else {
        result[key] = value;
      }
    });

    return result;
  }

  /// Compress GIS coordinates with quantization
  ///
  /// Reduces precision from 15+ decimal places to configurable
  /// latitude: 4 decimals = ~11m accuracy
  /// longitude: 4 decimals = ~11m accuracy at equator
  static Map<String, dynamic> _compressCoordinates(
    Map<String, dynamic> data,
  ) {
    final result = <String, dynamic>{};

    data.forEach((key, value) {
      if (key.contains('lat') || key.contains('lng') || key.contains('coord')) {
        // Quantize numeric coordinates
        if (value is double) {
          result[key] = _quantizeCoordinate(value);
        } else if (value is num) {
          result[key] = _quantizeCoordinate(value.toDouble());
        } else if (value is Map<String, dynamic>) {
          result[key] = _compressCoordinates(value);
        } else {
          result[key] = value;
        }
      } else if (value is Map<String, dynamic>) {
        result[key] = _compressCoordinates(value);
      } else if (value is List && value.isNotEmpty) {
        // Check if it's a coordinate array [[lon, lat], ...]
        if (_isCoordinateArray(value)) {
          result[key] = (value as List).map((coord) {
            if (coord is List && coord.length >= 2) {
              return [
                _quantizeCoordinate((coord[0] as num).toDouble()),
                _quantizeCoordinate((coord[1] as num).toDouble()),
              ];
            }
            return coord;
          }).toList();
        } else {
          result[key] = value;
        }
      } else {
        result[key] = value;
      }
    });

    return result;
  }

  /// Quantize coordinate to reduce precision
  static double _quantizeCoordinate(double value) {
    final factor = math.pow(10, coordinatePrecision).toDouble();
    return (value * factor).round() / factor;
  }

  /// Check if value is a coordinate array
  static bool _isCoordinateArray(dynamic value) {
    if (value is! List || value.isEmpty) return false;
    if (value.length > 100) return false; // Sanity check

    // Check first element
    final first = value.first;
    return first is List && first.length >= 2 &&
        first.every((v) => v is num);
  }

  /// Remove duplicate entity references
  ///
  /// Tracks seen IDs and replaces duplicates with references
  static Map<String, dynamic> _deduplicateReferences(
    Map<String, dynamic> data,
  ) {
    final seen = <String, String>{}; // id -> first occurrence key
    final result = <String, dynamic>{};

    void processValue(String key, dynamic value) {
      if (value is Map<String, dynamic>) {
        final id = value['id'] as String?;
        if (id != null && seen.containsKey(id)) {
          // Replace with reference
          result[key] = {'\$ref': id};
        } else {
          if (id != null) {
            seen[id] = key;
          }
          result[key] = _deduplicateReferences(value);
        }
      } else if (value is List) {
        result[key] = value.asMap().entries.map((entry) {
          if (entry.value is Map<String, dynamic>) {
            final map = entry.value as Map<String, dynamic>;
            final id = map['id'] as String?;
            if (id != null && seen.containsKey(id)) {
              return {'\$ref': id};
            } else {
              if (id != null) {
                seen[id] = '$key[$entry.key]';
              }
              return _deduplicateReferences(map);
            }
          }
          return entry.value;
        }).toList();
      } else {
        result[key] = value;
      }
    }

    data.forEach(processValue);
    return result;
  }

  /// Truncate history to reduce size
  static Map<String, dynamic> _truncateHistory(
    Map<String, dynamic> data,
    bool aggressive,
  ) {
    final result = <String, dynamic>{};
    final limit = aggressive ? 10 : maxHistoryItems;

    data.forEach((key, value) {
      if ((key.contains('history') || key.contains('events')) && value is List) {
        // Keep only recent items
        result[key] = value.length > limit
            ? value.sublist(value.length - limit)
            : value;
      } else if (value is Map<String, dynamic>) {
        result[key] = _truncateHistory(value, aggressive);
      } else {
        result[key] = value;
      }
    });

    return result;
  }

  /// Aggressive compression - remove non-essential fields
  static Map<String, dynamic> _aggressiveCompress(
    Map<String, dynamic> data,
  ) {
    final essential = {
      'id', 'name', 'tenant_id', 'field_id',
      'status', 'geometry', 'boundary',
      'coordinates', 'lat', 'lng',
      'created_at', 'updated_at',
    };

    final result = <String, dynamic>{};

    data.forEach((key, value) {
      final isEssential = essential.contains(key) ||
          key.startsWith('_') ||
          key.contains('error');

      if (isEssential) {
        if (value is Map<String, dynamic>) {
          result[key] = _aggressiveCompress(value);
        } else if (value is List) {
          result[key] = value.map((item) {
            if (item is Map<String, dynamic>) {
              return _aggressiveCompress(item);
            }
            return item;
          }).toList();
        } else {
          result[key] = value;
        }
      }
    });

    return result;
  }

  /// Calculate checksum for integrity verification
  static String _calculateChecksum(Map<String, dynamic> data) {
    final json = jsonEncode(data);
    return sha256.convert(utf8.encode(json)).toString().substring(0, 16);
  }

  /// Deep copy to avoid mutations
  static Map<String, dynamic> _deepCopy(Map<String, dynamic> data) {
    return jsonDecode(jsonEncode(data)) as Map<String, dynamic>;
  }
}

/// Compression metrics for monitoring
class CompressionMetrics {
  final int originalSize;
  final int compressedSize;
  final int compressionRatio; // percentage
  final String checksum;
  final DateTime timestamp;

  CompressionMetrics({
    required this.originalSize,
    required this.compressedSize,
    required this.compressionRatio,
    required this.checksum,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  /// Get human-readable compression ratio
  String get humanReadableRatio =>
      '${originalSize}B → ${compressedSize}B (${compressionRatio}%)';

  /// Check if compression was effective
  bool get isEffective => compressionRatio < 90;

  @override
  String toString() => 'CompressionMetrics($humanReadableRatio)';
}
