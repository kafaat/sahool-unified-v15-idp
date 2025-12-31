import 'dart:io';
import 'package:crypto/crypto.dart';
import 'package:flutter/foundation.dart';

/// Certificate Tools
/// أدوات إدارة الشهادات
///
/// Development tools for extracting and managing SSL certificate fingerprints.
/// These tools should only be used in debug/development mode.
///
/// USAGE:
/// This file contains utility functions to help developers extract
/// certificate fingerprints from servers for configuration purposes.

/// Extract certificate fingerprint from a URL
///
/// Example:
/// ```dart
/// final info = await getCertificateInfo('https://api.sahool.app');
/// print(info);
/// ```
Future<CertificateInfo?> getCertificateInfo(String url) async {
  if (!kDebugMode) {
    print('⚠️ Certificate tools should only be used in debug mode');
    return null;
  }

  try {
    final uri = Uri.parse(url);
    final host = uri.host;
    final port = uri.port == 0 ? 443 : uri.port;

    print('Connecting to $host:$port...');

    final socket = await SecureSocket.connect(
      host,
      port,
      timeout: const Duration(seconds: 10),
      onBadCertificate: (_) => true, // Allow any certificate for inspection
    );

    final cert = socket.peerCertificate;
    if (cert == null) {
      socket.close();
      print('❌ No certificate found');
      return null;
    }

    final certInfo = CertificateInfo.fromX509(cert, host);

    socket.close();
    return certInfo;
  } catch (e) {
    print('❌ Error getting certificate info: $e');
    return null;
  }
}

/// Batch extract certificate info from multiple URLs
///
/// Example:
/// ```dart
/// final urls = [
///   'https://api.sahool.app',
///   'https://api-staging.sahool.app',
///   'https://ws.sahool.app',
/// ];
/// final results = await getCertificateInfoBatch(urls);
/// for (final result in results) {
///   print(result);
/// }
/// ```
Future<List<CertificateInfo>> getCertificateInfoBatch(
  List<String> urls,
) async {
  final results = <CertificateInfo>[];

  for (final url in urls) {
    print('\n--- Fetching certificate for $url ---');
    final info = await getCertificateInfo(url);
    if (info != null) {
      results.add(info);
    }
  }

  return results;
}

/// Print certificate configuration code
///
/// This generates Dart code that can be copied into certificate_config.dart
///
/// Example:
/// ```dart
/// final info = await getCertificateInfo('https://api.sahool.app');
/// printCertificateConfigCode(info);
/// ```
void printCertificateConfigCode(CertificateInfo info) {
  print('\n=== Certificate Configuration Code ===');
  print("'${info.host}': [");
  print('  CertificatePin(');
  print('    type: PinType.sha256,');
  print("    value: '${info.sha256Fingerprint}',");
  print('    expiryDate: DateTime(${info.validUntil.year}, ${info.validUntil.month}, ${info.validUntil.day}),');
  print("    description: 'Certificate for ${info.host}',");
  print('  ),');
  print('],');
  print('=====================================\n');
}

/// Generate configuration for multiple certificates
void generateBulkConfiguration(List<CertificateInfo> certificates) {
  print('\n╔════════════════════════════════════════════════════╗');
  print('║  Certificate Pin Configuration - Copy This Code   ║');
  print('╚════════════════════════════════════════════════════╝\n');

  for (final cert in certificates) {
    print("  '${cert.host}': [");
    print('    CertificatePin(');
    print('      type: PinType.sha256,');
    print("      value: '${cert.sha256Fingerprint}',");
    print('      expiryDate: DateTime(${cert.validUntil.year}, ${cert.validUntil.month}, ${cert.validUntil.day}),');
    print("      description: 'Certificate for ${cert.host}',");
    print('    ),');
    print('  ],');
    print('');
  }
}

/// Verify certificate against expected fingerprint
Future<bool> verifyCertificateFingerprint({
  required String url,
  required String expectedFingerprint,
}) async {
  final info = await getCertificateInfo(url);
  if (info == null) return false;

  final matches = info.sha256Fingerprint.toLowerCase() ==
      expectedFingerprint.toLowerCase();

  if (matches) {
    print('✅ Certificate fingerprint matches!');
  } else {
    print('❌ Certificate fingerprint does NOT match!');
    print('   Expected: $expectedFingerprint');
    print('   Actual:   ${info.sha256Fingerprint}');
  }

  return matches;
}

/// Certificate information class
class CertificateInfo {
  final String host;
  final String subject;
  final String issuer;
  final DateTime validFrom;
  final DateTime validUntil;
  final String sha256Fingerprint;
  final String sha1Fingerprint;
  final List<int> derBytes;

  CertificateInfo({
    required this.host,
    required this.subject,
    required this.issuer,
    required this.validFrom,
    required this.validUntil,
    required this.sha256Fingerprint,
    required this.sha1Fingerprint,
    required this.derBytes,
  });

  factory CertificateInfo.fromX509(X509Certificate cert, String host) {
    final derBytes = cert.der;
    final sha256Hash = sha256.convert(derBytes);
    final sha1Hash = sha1.convert(derBytes);

    return CertificateInfo(
      host: host,
      subject: cert.subject,
      issuer: cert.issuer,
      validFrom: cert.startValidity,
      validUntil: cert.endValidity,
      sha256Fingerprint: sha256Hash.toString(),
      sha1Fingerprint: sha1Hash.toString(),
      derBytes: derBytes,
    );
  }

  /// Check if certificate is currently valid
  bool get isValid {
    final now = DateTime.now();
    return now.isAfter(validFrom) && now.isBefore(validUntil);
  }

  /// Days until expiry
  int get daysUntilExpiry {
    return validUntil.difference(DateTime.now()).inDays;
  }

  /// Format fingerprint with colons (standard format)
  String get formattedSha256 {
    return _formatFingerprint(sha256Fingerprint);
  }

  String get formattedSha1 {
    return _formatFingerprint(sha1Fingerprint);
  }

  String _formatFingerprint(String fingerprint) {
    final formatted = fingerprint
        .toUpperCase()
        .replaceAllMapped(RegExp(r'.{2}'), (match) => '${match.group(0)}:');
    return formatted.substring(0, formatted.length - 1);
  }

  @override
  String toString() {
    final buffer = StringBuffer();
    buffer.writeln('╔════════════════════════════════════════════════════╗');
    buffer.writeln('║  Certificate Information                          ║');
    buffer.writeln('╚════════════════════════════════════════════════════╝');
    buffer.writeln('Host:           $host');
    buffer.writeln('Subject:        $subject');
    buffer.writeln('Issuer:         $issuer');
    buffer.writeln('Valid From:     $validFrom');
    buffer.writeln('Valid Until:    $validUntil');
    buffer.writeln('Days to Expire: $daysUntilExpiry');
    buffer.writeln('Is Valid:       ${isValid ? "✅ Yes" : "❌ No"}');
    buffer.writeln('');
    buffer.writeln('SHA-256 Fingerprint (raw):');
    buffer.writeln('  $sha256Fingerprint');
    buffer.writeln('');
    buffer.writeln('SHA-256 Fingerprint (formatted):');
    buffer.writeln('  $formattedSha256');
    buffer.writeln('');
    buffer.writeln('SHA-1 Fingerprint:');
    buffer.writeln('  $formattedSha1');
    buffer.writeln('════════════════════════════════════════════════════');
    return buffer.toString();
  }

  /// Export as JSON-like map
  Map<String, dynamic> toMap() {
    return {
      'host': host,
      'subject': subject,
      'issuer': issuer,
      'validFrom': validFrom.toIso8601String(),
      'validUntil': validUntil.toIso8601String(),
      'daysUntilExpiry': daysUntilExpiry,
      'isValid': isValid,
      'sha256Fingerprint': sha256Fingerprint,
      'sha1Fingerprint': sha1Fingerprint,
    };
  }
}

/// Example usage in debug mode:
///
/// ```dart
/// // In your debug/development code:
/// void _debugCertificates() async {
///   if (!kDebugMode) return;
///
///   // Single certificate
///   final info = await getCertificateInfo('https://api.sahool.app');
///   if (info != null) {
///     print(info);
///     printCertificateConfigCode(info);
///   }
///
///   // Multiple certificates
///   final urls = [
///     'https://api.sahool.app',
///     'https://api-staging.sahool.app',
///     'https://ws.sahool.app',
///   ];
///   final results = await getCertificateInfoBatch(urls);
///   generateBulkConfiguration(results);
///
///   // Verify against expected fingerprint
///   await verifyCertificateFingerprint(
///     url: 'https://api.sahool.app',
///     expectedFingerprint: 'your_expected_fingerprint_here',
///   );
/// }
/// ```
