library;

/// SAHOOL HTTP/Network Layer
/// طبقة الشبكة والاتصالات
///
/// This module provides a robust, secure network layer for the SAHOOL mobile app.
///
/// ## Features:
/// - Centralized network configuration
/// - Certificate pinning for security
/// - Request signing for API integrity
/// - Rate limiting to prevent abuse
/// - Automatic retry with exponential backoff
/// - Network connectivity monitoring
/// - PII-safe logging
/// - Security header validation
///
/// ## Usage:
/// ```dart
/// import 'package:sahool_field_app/core/http/http.dart';
///
/// // Create API client with default configuration
/// final client = ApiClient();
///
/// // Or with custom configuration
/// final client = ApiClient(
///   networkConfig: NetworkConfig.production(),
///   connectivityService: NetworkConnectivityService(),
/// );
///
/// // Make requests
/// final result = await client.get('/fields');
/// ```


// Core API Client
export 'api_client.dart';

// Network Configuration
export 'network_config.dart';

// Connectivity Monitoring
export 'connectivity_aware_client.dart';

// Interceptors
export 'auth_interceptor.dart';
export 'logging_interceptor.dart';
export 'rate_limiter.dart';
export 'request_signing_interceptor.dart';
export 'retry_interceptor.dart';
export 'security_headers_interceptor.dart';
