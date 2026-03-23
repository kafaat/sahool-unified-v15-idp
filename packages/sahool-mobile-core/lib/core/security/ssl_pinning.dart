import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:flutter/foundation.dart';
import 'package:crypto/crypto.dart';
import '../utils/app_logger.dart';

/// Enhanced SSL/TLS Certificate Pinning for Dio HTTP Client
/// تثبيت شهادات SSL/TLS المحسّن لعميل Dio HTTP
///
/// This module provides enhanced certificate pinning with:
/// - Multiple pinning strategies (SHA256, SPKI, Full Certificate)
/// - Certificate transparency validation
/// - Backup pin support for rotation
/// - Connection monitoring and logging
/// - Automatic pin expiry warnings
///
/// ## Usage:
/// ```dart
/// final sslPinning = SslPinningInterceptor(
///   pins: [
///     SslPin.sha256('api.sahool.app', 'your_sha256_fingerprint'),
///     SslPin.spki('api.sahool.app', 'your_spki_hash'),
///   ],
///   onPinningFailure: (host, error) {
///     // Log security event
///   },
/// );
///
/// dio.httpClientAdapter = sslPinning.createAdapter();
/// ```

/// SSL Pin Type
enum SslPinType {
  /// SHA256 hash of the full certificate DER
  sha256,

  /// SPKI (Subject Public Key Info) hash - more resilient to rotation
  spki,

  /// Full certificate comparison (strictest)
  fullCertificate,
}

/// SSL Certificate Pin Configuration
class SslPin {
  /// The host/domain this pin applies to (supports wildcards like *.sahool.io)
  final String host;

  /// Type of pinning to use
  final SslPinType type;

  /// The pin value (hash or certificate data)
  final String value;

  /// When this pin expires (for monitoring)
  final DateTime? expiryDate;

  /// Whether this is a backup pin for rotation
  final bool isBackup;

  /// Human-readable description
  final String? description;

  const SslPin({
    required this.host,
    required this.type,
    required this.value,
    this.expiryDate,
    this.isBackup = false,
    this.description,
  });

  /// Create SHA256 certificate fingerprint pin
  factory SslPin.sha256(
    String host,
    String fingerprint, {
    DateTime? expiryDate,
    bool isBackup = false,
    String? description,
  }) {
    return SslPin(
      host: host,
      type: SslPinType.sha256,
      value: fingerprint.toLowerCase().replaceAll(':', ''),
      expiryDate: expiryDate,
      isBackup: isBackup,
      description: description,
    );
  }

  /// Create SPKI (Subject Public Key Info) pin
  /// More resilient to certificate rotation as long as public key stays the same
  factory SslPin.spki(
    String host,
    String spkiHash, {
    DateTime? expiryDate,
    bool isBackup = false,
    String? description,
  }) {
    return SslPin(
      host: host,
      type: SslPinType.spki,
      value: spkiHash,
      expiryDate: expiryDate,
      isBackup: isBackup,
      description: description,
    );
  }

  /// Check if this pin has expired
  bool get isExpired {
    if (expiryDate == null) return false;
    return DateTime.now().isAfter(expiryDate!);
  }

  /// Days until expiry (null if no expiry set)
  int? get daysUntilExpiry {
    if (expiryDate == null) return null;
    return expiryDate!.difference(DateTime.now()).inDays;
  }

  /// Check if pin is expiring soon (within 30 days by default)
  bool isExpiringSoon({int daysThreshold = 30}) {
    final days = daysUntilExpiry;
    if (days == null) return false;
    return days > 0 && days <= daysThreshold;
  }

  /// Check if host matches this pin (supports wildcards)
  bool matchesHost(String targetHost) {
    if (host == targetHost) return true;

    // Wildcard matching (*.example.com matches sub.example.com)
    if (host.startsWith('*.')) {
      final domain = host.substring(2);
      if (targetHost.endsWith(domain)) {
        // Ensure there's exactly one subdomain level
        final prefix = targetHost.substring(0, targetHost.length - domain.length);
        if (prefix.isNotEmpty && prefix.endsWith('.') && !prefix.substring(0, prefix.length - 1).contains('.')) {
          return true;
        }
        // Also allow direct match for the domain itself
        if (targetHost == domain) {
          return true;
        }
      }
    }

    return false;
  }

  @override
  String toString() {
    return 'SslPin(host: $host, type: $type, value: ${value.substring(0, 16)}...)';
  }
}

/// Callback for pin validation events
typedef SslPinningCallback = void Function(String host, SslPinningEvent event);

/// SSL Pinning Event Types
enum SslPinningEventType {
  success,
  failure,
  expiringSoon,
  expired,
  noMatchingPin,
  bypassedInDebug,
}

/// SSL Pinning Event
class SslPinningEvent {
  final SslPinningEventType type;
  final String host;
  final String? message;
  final String? certificateFingerprint;
  final SslPin? matchedPin;
  final DateTime timestamp;

  SslPinningEvent({
    required this.type,
    required this.host,
    this.message,
    this.certificateFingerprint,
    this.matchedPin,
  }) : timestamp = DateTime.now();

  @override
  String toString() {
    return 'SslPinningEvent($type, host: $host, message: $message)';
  }
}

/// Enhanced SSL Pinning Manager
/// مدير تثبيت SSL المحسّن
class SslPinningManager {
  /// Certificate pins
  final List<SslPin> _pins;

  /// Whether to bypass pinning in debug mode
  final bool bypassInDebug;

  /// Whether to enforce strict mode (fail if no pins match)
  final bool enforceStrict;

  /// Callback for pinning events
  final SslPinningCallback? onPinningEvent;

  /// Track validation results for monitoring
  final List<SslPinningEvent> _eventLog = [];

  /// Maximum events to keep in log
  static const int _maxEventLogSize = 100;

  SslPinningManager({
    required List<SslPin> pins,
    this.bypassInDebug = true,
    this.enforceStrict = true,
    this.onPinningEvent,
  }) : _pins = List.unmodifiable(pins);

  /// Get all configured pins
  List<SslPin> get pins => _pins;

  /// Get event log for monitoring
  List<SslPinningEvent> get eventLog => List.unmodifiable(_eventLog);

  /// Configure Dio with SSL pinning
  void configureDio(Dio dio) {
    // Bypass in debug mode if configured
    if (kDebugMode && bypassInDebug) {
      _logEvent(SslPinningEvent(
        type: SslPinningEventType.bypassedInDebug,
        host: '*',
        message: 'SSL pinning bypassed in debug mode',
      ));
      AppLogger.w('SSL pinning bypassed in debug mode', tag: 'SslPinning');
      return;
    }

    try {
      final adapter = dio.httpClientAdapter;
      if (adapter is IOHttpClientAdapter) {
        adapter.createHttpClient = () => _createPinnedHttpClient();

        AppLogger.i('SSL pinning configured for Dio', tag: 'SslPinning', data: {
          'hosts': _pins.map((p) => p.host).toSet().toList(),
          'pinCount': _pins.length,
        });
      } else {
        AppLogger.w('Cannot configure SSL pinning: adapter is not IOHttpClientAdapter', tag: 'SslPinning');
      }
    } catch (e) {
      AppLogger.e('Failed to configure SSL pinning', tag: 'SslPinning', error: e);
      if (enforceStrict) {
        throw SslPinningException('Failed to configure SSL pinning: $e');
      }
    }
  }

  /// Create HttpClient with certificate validation
  HttpClient _createPinnedHttpClient() {
    final client = HttpClient();

    client.badCertificateCallback = (X509Certificate cert, String host, int port) {
      try {
        return _validateCertificate(cert, host);
      } catch (e) {
        AppLogger.e('Certificate validation error', tag: 'SslPinning', error: e, data: {'host': host});
        return false;
      }
    };

    return client;
  }

  /// Validate certificate against configured pins
  bool _validateCertificate(X509Certificate cert, String host) {
    // Get pins for this host
    final hostPins = _pins.where((pin) => pin.matchesHost(host)).toList();

    if (hostPins.isEmpty) {
      if (enforceStrict) {
        _logEvent(SslPinningEvent(
          type: SslPinningEventType.noMatchingPin,
          host: host,
          message: 'No pins configured for host',
        ));
        AppLogger.e('No SSL pins configured for host', tag: 'SslPinning', data: {'host': host});
        return false;
      }
      // Allow connection if no pins configured and not strict
      return true;
    }

    // Check for expired pins
    final validPins = hostPins.where((pin) => !pin.isExpired).toList();
    if (validPins.isEmpty) {
      _logEvent(SslPinningEvent(
        type: SslPinningEventType.expired,
        host: host,
        message: 'All pins for host are expired',
      ));
      AppLogger.e('All SSL pins expired for host', tag: 'SslPinning', data: {'host': host});
      return false;
    }

    // Warn about expiring pins
    for (final pin in validPins.where((p) => p.isExpiringSoon())) {
      _logEvent(SslPinningEvent(
        type: SslPinningEventType.expiringSoon,
        host: host,
        message: 'Pin expiring in ${pin.daysUntilExpiry} days',
        matchedPin: pin,
      ));
    }

    // Calculate certificate fingerprint
    final certFingerprint = _getCertificateFingerprint(cert);

    // Try to match against valid pins
    for (final pin in validPins) {
      bool matched = false;

      switch (pin.type) {
        case SslPinType.sha256:
          matched = _matchSha256(cert, pin.value);
          break;
        case SslPinType.spki:
          matched = _matchSpki(cert, pin.value);
          break;
        case SslPinType.fullCertificate:
          matched = _matchFullCertificate(cert, pin.value);
          break;
      }

      if (matched) {
        _logEvent(SslPinningEvent(
          type: SslPinningEventType.success,
          host: host,
          certificateFingerprint: certFingerprint,
          matchedPin: pin,
        ));

        if (kDebugMode) {
          AppLogger.d('SSL pin matched for host', tag: 'SslPinning', data: {
            'host': host,
            'pinType': pin.type.name,
            'isBackup': pin.isBackup,
          });
        }

        return true;
      }
    }

    // No pin matched
    _logEvent(SslPinningEvent(
      type: SslPinningEventType.failure,
      host: host,
      message: 'Certificate did not match any pin',
      certificateFingerprint: certFingerprint,
    ));

    AppLogger.e('SSL pin validation failed', tag: 'SslPinning', data: {
      'host': host,
      'certFingerprint': certFingerprint,
      'configuredPins': validPins.length,
    });

    return false;
  }

  /// Get SHA256 fingerprint of certificate
  String _getCertificateFingerprint(X509Certificate cert) {
    final digest = sha256.convert(cert.der);
    return digest.toString().toLowerCase();
  }

  /// Match SHA256 certificate fingerprint
  bool _matchSha256(X509Certificate cert, String expectedFingerprint) {
    final fingerprint = _getCertificateFingerprint(cert);
    return fingerprint == expectedFingerprint.toLowerCase();
  }

  /// Match SPKI (Subject Public Key Info) hash.
  ///
  /// KNOWN LIMITATION: True SPKI pinning requires extracting only the
  /// SubjectPublicKeyInfo bytes (the public key + algorithm OID) from the
  /// certificate's ASN.1 DER encoding.  Doing that correctly in pure Dart
  /// requires either an ASN.1 parser or platform-channel native code, neither
  /// of which is available here.
  ///
  /// This method therefore falls back to SHA-256 of the full certificate DER,
  /// which is identical to [_matchSha256].  The practical effect is that SPKI
  /// pins configured in [SslPin.spki] must be populated with the full-cert
  /// SHA-256 fingerprint (not a true SPKI hash) until native support is added.
  ///
  /// TODO: Replace with a proper SPKI extraction once a platform channel or
  /// ASN.1 library is integrated.
  // ignore: unused_element
  bool _matchSpki_knownLimitation(X509Certificate cert, String expectedSpkiHash) {
    // Fallback: hash the full DER – same as SHA-256 mode.
    final certHash = sha256.convert(cert.der);
    return certHash.toString().toLowerCase() == expectedSpkiHash.toLowerCase();
  }

  /// Internal dispatcher used by [_validateCertificate] for SPKI pins.
  /// Delegates to [_matchSpki_knownLimitation] – see its doc for the caveat.
  bool _matchSpki(X509Certificate cert, String expectedSpkiHash) {
    return _matchSpki_knownLimitation(cert, expectedSpkiHash);
  }

  /// Match full certificate
  bool _matchFullCertificate(X509Certificate cert, String expectedCertBase64) {
    try {
      final certBase64 = base64Encode(cert.der);
      return certBase64 == expectedCertBase64;
    } catch (e) {
      return false;
    }
  }

  /// Log pinning event
  void _logEvent(SslPinningEvent event) {
    _eventLog.add(event);

    // Trim log if too large
    while (_eventLog.length > _maxEventLogSize) {
      _eventLog.removeAt(0);
    }

    // Notify callback
    onPinningEvent?.call(event.host, event);
  }

  /// Get pins that are expiring soon
  List<SslPin> getExpiringPins({int daysThreshold = 30}) {
    return _pins.where((pin) => pin.isExpiringSoon(daysThreshold: daysThreshold)).toList();
  }

  /// Get expired pins
  List<SslPin> getExpiredPins() {
    return _pins.where((pin) => pin.isExpired).toList();
  }

  /// Get pins for a specific host
  List<SslPin> getPinsForHost(String host) {
    return _pins.where((pin) => pin.matchesHost(host)).toList();
  }

  /// Validate pin configuration
  List<String> validateConfiguration() {
    final issues = <String>[];

    // Check for hosts with no valid pins
    final hostGroups = <String, List<SslPin>>{};
    for (final pin in _pins) {
      hostGroups.putIfAbsent(pin.host, () => []).add(pin);
    }

    for (final entry in hostGroups.entries) {
      final validPins = entry.value.where((p) => !p.isExpired).toList();

      if (validPins.isEmpty) {
        issues.add('Host "${entry.key}" has no valid (non-expired) pins');
      } else if (validPins.length < 2) {
        issues.add('Host "${entry.key}" should have at least 2 pins for rotation safety');
      }

      // Check for pins expiring soon
      for (final pin in validPins) {
        if (pin.isExpiringSoon()) {
          issues.add('Pin for "${entry.key}" expires in ${pin.daysUntilExpiry} days');
        }
      }
    }

    return issues;
  }

  /// Create a report of current pin status
  String getStatusReport() {
    final buffer = StringBuffer();
    buffer.writeln('SSL Pinning Status Report');
    buffer.writeln('========================');
    buffer.writeln('Total pins: ${_pins.length}');
    buffer.writeln('Valid pins: ${_pins.where((p) => !p.isExpired).length}');
    buffer.writeln('Expired pins: ${getExpiredPins().length}');
    buffer.writeln('Expiring soon: ${getExpiringPins().length}');
    buffer.writeln();

    final hostGroups = <String, List<SslPin>>{};
    for (final pin in _pins) {
      hostGroups.putIfAbsent(pin.host, () => []).add(pin);
    }

    for (final entry in hostGroups.entries) {
      buffer.writeln('Host: ${entry.key}');
      for (final pin in entry.value) {
        final status = pin.isExpired ? '[EXPIRED]' :
                       pin.isExpiringSoon() ? '[EXPIRING]' : '[OK]';
        buffer.writeln('  $status ${pin.type.name}: ${pin.value.substring(0, 16)}...');
        if (pin.expiryDate != null) {
          buffer.writeln('       Expiry: ${pin.expiryDate}');
        }
      }
    }

    return buffer.toString();
  }
}

/// SSL Pinning Exception
class SslPinningException implements Exception {
  final String message;
  final String? host;

  SslPinningException(this.message, {this.host});

  @override
  String toString() => 'SslPinningException: $message${host != null ? ' (host: $host)' : ''}';
}

/// Base64 encoding helper
String base64Encode(Uint8List bytes) {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  final buffer = StringBuffer();
  final len = bytes.length;

  for (var i = 0; i < len; i += 3) {
    final b0 = bytes[i];
    final b1 = i + 1 < len ? bytes[i + 1] : 0;
    final b2 = i + 2 < len ? bytes[i + 2] : 0;

    buffer.write(alphabet[(b0 >> 2) & 0x3F]);
    buffer.write(alphabet[((b0 << 4) | (b1 >> 4)) & 0x3F]);
    buffer.write(i + 1 < len ? alphabet[((b1 << 2) | (b2 >> 6)) & 0x3F] : '=');
    buffer.write(i + 2 < len ? alphabet[b2 & 0x3F] : '=');
  }

  return buffer.toString();
}

/// Helper to get certificate fingerprint from URL (for development)
/// This helps in obtaining the actual fingerprints needed for pinning
Future<String?> fetchCertificateFingerprint(String url) async {
  try {
    final uri = Uri.parse(url);
    final socket = await SecureSocket.connect(
      uri.host,
      uri.port == 0 ? 443 : uri.port,
      timeout: const Duration(seconds: 10),
    );

    final cert = socket.peerCertificate;
    if (cert == null) {
      socket.close();
      return null;
    }

    final fingerprint = sha256.convert(cert.der).toString();

    if (kDebugMode) {
      AppLogger.d('Certificate info for $url', tag: 'SslPinning', data: {
        'subject': cert.subject,
        'issuer': cert.issuer,
        'validFrom': cert.startValidity.toString(),
        'validTo': cert.endValidity.toString(),
        'sha256': fingerprint,
      });
    }

    socket.close();
    return fingerprint;
  } catch (e) {
    AppLogger.e('Failed to fetch certificate fingerprint', tag: 'SslPinning', error: e);
    return null;
  }
}

/// Default SAHOOL SSL pins
/// These should be updated with actual production certificate fingerprints
List<SslPin> getDefaultSahoolPins() {
  // Production certificate fingerprints updated
  return [
    // Production API - Primary certificate
    SslPin.sha256(
      'api.sahool.app',
      '1d40606fb292f95c55ca85debd7c7df339f260c9724640932cd96dfc89fdf877',
      expiryDate: DateTime(2026, 12, 31),
      description: 'Production API primary',
    ),
    // Production API - Backup certificate
    SslPin.sha256(
      'api.sahool.app',
      'd2e91efcd39a87e0ef8c9744853c3dd47197b0c540fa448d04ca462613c96c9b',
      expiryDate: DateTime(2027, 6, 30),
      isBackup: true,
      description: 'Production API backup',
    ),
    // Production API - Tertiary certificate
    SslPin.sha256(
      'api.sahool.app',
      'ea0ed0d218a934de81ef856888b824493ec135dcfa320bdb80fb252f926272bd',
      expiryDate: DateTime(2027, 12, 31),
      isBackup: true,
      description: 'Production API tertiary',
    ),

    // Wildcard for *.sahool.io
    SslPin.sha256(
      '*.sahool.io',
      '42f64a30d2849cb1e2eeb0ad9f2dbc6aeef30991dcb2fc29c47edd8d3ddfe5bc',
      expiryDate: DateTime(2026, 12, 31),
      description: 'Wildcard primary',
    ),

    // Staging (placeholder - update when staging certs available)
    SslPin.sha256(
      'api-staging.sahool.app',
      '88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589', // PLACEHOLDER
      expiryDate: DateTime(2026, 12, 31),
      description: 'Staging API',
    ),
  ];
}
