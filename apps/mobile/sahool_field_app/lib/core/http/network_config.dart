import 'dart:io';
import 'dart:math';

import 'package:flutter/foundation.dart';
import '../config/env_config.dart';

/// SAHOOL Network Configuration
/// تكوين الشبكة الموحد
///
/// Centralizes all network-related configuration settings for consistency
/// across ApiClient, KongGatewayClient, and other HTTP clients.
///
/// Features:
/// - Centralized timeout configuration
/// - TLS/SSL settings
/// - Retry configuration
/// - Environment-aware defaults
class NetworkConfig {
  /// Connection timeout - time to establish connection
  final Duration connectTimeout;

  /// Send timeout - time to send request data
  final Duration sendTimeout;

  /// Receive timeout - time to receive response data
  final Duration receiveTimeout;

  /// Maximum number of retry attempts
  final int maxRetries;

  /// Initial delay between retries (with exponential backoff)
  final Duration initialRetryDelay;

  /// Maximum delay between retries
  final Duration maxRetryDelay;

  /// Retry backoff multiplier
  final double retryBackoffMultiplier;

  /// Whether to enable keep-alive connections
  final bool enableKeepAlive;

  /// Keep-alive timeout for idle connections
  final Duration keepAliveTimeout;

  /// Maximum connections per host
  final int maxConnectionsPerHost;

  /// Minimum TLS version (1.2 or higher recommended)
  final TlsVersion minTlsVersion;

  /// Whether to validate server certificates
  final bool validateCertificates;

  /// Whether to follow redirects
  final bool followRedirects;

  /// Maximum number of redirects to follow
  final int maxRedirects;

  /// Request content type
  final String contentType;

  /// Accept header value
  final String acceptHeader;

  const NetworkConfig({
    this.connectTimeout = const Duration(seconds: 10),
    this.sendTimeout = const Duration(seconds: 30),
    this.receiveTimeout = const Duration(seconds: 30),
    this.maxRetries = 3,
    this.initialRetryDelay = const Duration(seconds: 1),
    this.maxRetryDelay = const Duration(seconds: 30),
    this.retryBackoffMultiplier = 2.0,
    this.enableKeepAlive = true,
    this.keepAliveTimeout = const Duration(seconds: 15),
    this.maxConnectionsPerHost = 6,
    this.minTlsVersion = TlsVersion.tls12,
    this.validateCertificates = true,
    this.followRedirects = true,
    this.maxRedirects = 5,
    this.contentType = 'application/json',
    this.acceptHeader = 'application/json',
  });

  /// Production network configuration
  /// Strict timeouts, TLS 1.2+, full validation
  static NetworkConfig production() {
    return NetworkConfig(
      connectTimeout: Duration(seconds: EnvConfig.connectTimeout.inSeconds),
      sendTimeout: const Duration(seconds: 20),
      receiveTimeout: Duration(seconds: EnvConfig.receiveTimeout.inSeconds),
      maxRetries: 3,
      initialRetryDelay: const Duration(seconds: 1),
      maxRetryDelay: const Duration(seconds: 30),
      retryBackoffMultiplier: 2.0,
      enableKeepAlive: true,
      keepAliveTimeout: const Duration(seconds: 15),
      maxConnectionsPerHost: 6,
      minTlsVersion: TlsVersion.tls12,
      validateCertificates: true,
      followRedirects: true,
      maxRedirects: 5,
    );
  }

  /// Staging network configuration
  /// More lenient timeouts for testing
  static NetworkConfig staging() {
    return NetworkConfig(
      connectTimeout: Duration(seconds: EnvConfig.connectTimeout.inSeconds),
      sendTimeout: const Duration(seconds: 30),
      receiveTimeout: Duration(seconds: EnvConfig.receiveTimeout.inSeconds),
      maxRetries: 3,
      initialRetryDelay: const Duration(seconds: 1),
      maxRetryDelay: const Duration(seconds: 60),
      retryBackoffMultiplier: 2.0,
      enableKeepAlive: true,
      keepAliveTimeout: const Duration(seconds: 15),
      maxConnectionsPerHost: 6,
      minTlsVersion: TlsVersion.tls12,
      validateCertificates: true,
      followRedirects: true,
      maxRedirects: 5,
    );
  }

  /// Development network configuration
  /// Relaxed settings for local development
  static NetworkConfig development() {
    return NetworkConfig(
      connectTimeout: Duration(seconds: EnvConfig.connectTimeout.inSeconds),
      sendTimeout: const Duration(seconds: 60),
      receiveTimeout: Duration(seconds: EnvConfig.receiveTimeout.inSeconds),
      maxRetries: 2,
      initialRetryDelay: const Duration(milliseconds: 500),
      maxRetryDelay: const Duration(seconds: 10),
      retryBackoffMultiplier: 1.5,
      enableKeepAlive: true,
      keepAliveTimeout: const Duration(seconds: 30),
      maxConnectionsPerHost: 10,
      minTlsVersion: TlsVersion.tls12,
      validateCertificates: !kDebugMode, // Allow self-signed in debug
      followRedirects: true,
      maxRedirects: 10,
    );
  }

  /// Get configuration based on current environment
  factory NetworkConfig.fromEnvironment() {
    if (EnvConfig.isProduction) {
      return NetworkConfig.production();
    } else if (EnvConfig.isStaging) {
      return NetworkConfig.staging();
    } else {
      return NetworkConfig.development();
    }
  }

  /// Mobile sync configuration with extended timeouts
  /// تكوين المزامنة المحمولة مع مهل ممتدة
  ///
  /// Optimized for mobile sync operations in low-connectivity areas:
  /// - Extended timeouts for slow/unstable connections
  /// - More aggressive retries for reliability
  /// - Larger batch processing support
  static NetworkConfig forMobileSync() {
    final base = NetworkConfig.fromEnvironment();
    return base.copyWith(
      connectTimeout: const Duration(seconds: 60), // Increased from 10-30s
      sendTimeout: const Duration(seconds: 90), // For large sync batches
      receiveTimeout: const Duration(seconds: 90), // For large server responses
      maxRetries: 5, // More retries for reliability
      initialRetryDelay: const Duration(seconds: 1),
      maxRetryDelay: const Duration(minutes: 5), // Up to 5 minutes backoff
      retryBackoffMultiplier: 2.0,
    );
  }

  /// Create copy with updated values
  NetworkConfig copyWith({
    Duration? connectTimeout,
    Duration? sendTimeout,
    Duration? receiveTimeout,
    int? maxRetries,
    Duration? initialRetryDelay,
    Duration? maxRetryDelay,
    double? retryBackoffMultiplier,
    bool? enableKeepAlive,
    Duration? keepAliveTimeout,
    int? maxConnectionsPerHost,
    TlsVersion? minTlsVersion,
    bool? validateCertificates,
    bool? followRedirects,
    int? maxRedirects,
    String? contentType,
    String? acceptHeader,
  }) {
    return NetworkConfig(
      connectTimeout: connectTimeout ?? this.connectTimeout,
      sendTimeout: sendTimeout ?? this.sendTimeout,
      receiveTimeout: receiveTimeout ?? this.receiveTimeout,
      maxRetries: maxRetries ?? this.maxRetries,
      initialRetryDelay: initialRetryDelay ?? this.initialRetryDelay,
      maxRetryDelay: maxRetryDelay ?? this.maxRetryDelay,
      retryBackoffMultiplier:
          retryBackoffMultiplier ?? this.retryBackoffMultiplier,
      enableKeepAlive: enableKeepAlive ?? this.enableKeepAlive,
      keepAliveTimeout: keepAliveTimeout ?? this.keepAliveTimeout,
      maxConnectionsPerHost:
          maxConnectionsPerHost ?? this.maxConnectionsPerHost,
      minTlsVersion: minTlsVersion ?? this.minTlsVersion,
      validateCertificates: validateCertificates ?? this.validateCertificates,
      followRedirects: followRedirects ?? this.followRedirects,
      maxRedirects: maxRedirects ?? this.maxRedirects,
      contentType: contentType ?? this.contentType,
      acceptHeader: acceptHeader ?? this.acceptHeader,
    );
  }

  /// Calculate retry delay with exponential backoff
  Duration getRetryDelay(int retryAttempt) {
    final multiplier = pow(retryBackoffMultiplier, retryAttempt);
    final delay = initialRetryDelay * multiplier;
    return Duration(
      milliseconds: delay.inMilliseconds.clamp(
        initialRetryDelay.inMilliseconds,
        maxRetryDelay.inMilliseconds,
      ),
    );
  }

  /// Get default headers for requests
  Map<String, String> getDefaultHeaders() {
    return {
      'Content-Type': contentType,
      'Accept': acceptHeader,
      'X-Client-Platform':
          Platform.isAndroid ? 'android' : (Platform.isIOS ? 'ios' : 'unknown'),
      'X-Client-Version': EnvConfig.appVersion,
      'Accept-Language': 'ar,en',
    };
  }

  @override
  String toString() {
    return 'NetworkConfig('
        'connect: ${connectTimeout.inSeconds}s, '
        'send: ${sendTimeout.inSeconds}s, '
        'receive: ${receiveTimeout.inSeconds}s, '
        'retries: $maxRetries, '
        'tls: ${minTlsVersion.name}'
        ')';
  }
}

/// TLS Version enumeration
enum TlsVersion {
  /// TLS 1.0 (deprecated, avoid using)
  tls10,

  /// TLS 1.1 (deprecated, avoid using)
  tls11,

  /// TLS 1.2 (minimum recommended)
  tls12,

  /// TLS 1.3 (recommended for best security)
  tls13,
}

/// Extension to convert TlsVersion to SecurityContext settings
extension TlsVersionExtension on TlsVersion {
  /// Check if this TLS version is secure (1.2+)
  bool get isSecure => index >= TlsVersion.tls12.index;

  /// Get the minimum protocol version string for HttpClient
  String get protocolName {
    switch (this) {
      case TlsVersion.tls10:
        return 'TLSv1';
      case TlsVersion.tls11:
        return 'TLSv1.1';
      case TlsVersion.tls12:
        return 'TLSv1.2';
      case TlsVersion.tls13:
        return 'TLSv1.3';
    }
  }
}
