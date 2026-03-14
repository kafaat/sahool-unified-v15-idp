/// Comprehensive Rate Limiter Tests - SAHOOL Mobile
/// اختبارات شاملة لمحدد السرعة - تطبيق سهول للجوال
///
/// Tests cover:
/// - TokenBucket consumption and refill
/// - EndpointConfig backoff calculations
/// - RateLimiter endpoint type detection
/// - RateLimitStatus utilization
/// - RateLimitException

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/http/rate_limiter.dart';

void main() {
  group('TokenBucket', () {
    test('should start with full capacity', () {
      final bucket = TokenBucket(capacity: 10, refillRate: 1.0);
      expect(bucket.availableTokens, 10);
    });

    test('should consume tokens', () {
      final bucket = TokenBucket(capacity: 10, refillRate: 1.0);
      expect(bucket.tryConsume(), true);
      expect(bucket.availableTokens, 9);
    });

    test('should consume multiple tokens', () {
      final bucket = TokenBucket(capacity: 10, refillRate: 1.0);
      expect(bucket.tryConsume(tokens: 5), true);
      expect(bucket.availableTokens, 5);
    });

    test('should fail when not enough tokens', () {
      final bucket = TokenBucket(capacity: 2, refillRate: 0.1);
      expect(bucket.tryConsume(), true);
      expect(bucket.tryConsume(), true);
      expect(bucket.tryConsume(), false);
    });

    test('should fail for more tokens than available', () {
      final bucket = TokenBucket(capacity: 5, refillRate: 1.0);
      expect(bucket.tryConsume(tokens: 10), false);
    });

    test('getWaitTime returns zero when tokens available', () {
      final bucket = TokenBucket(capacity: 10, refillRate: 1.0);
      expect(bucket.getWaitTime(), Duration.zero);
    });

    test('getWaitTime returns positive duration when no tokens', () {
      final bucket = TokenBucket(capacity: 1, refillRate: 1.0);
      bucket.tryConsume(); // Exhaust tokens
      final waitTime = bucket.getWaitTime();
      expect(waitTime.inMilliseconds, greaterThan(0));
    });

    test('should not exceed capacity after refill', () {
      final bucket = TokenBucket(capacity: 5, refillRate: 100.0);
      // Even with high refill rate, should not exceed capacity
      expect(bucket.availableTokens, lessThanOrEqualTo(5));
    });
  });

  group('EndpointConfig', () {
    test('default config values', () {
      final config = EndpointConfig.defaultConfig();
      expect(config.maxRequests, 60);
      expect(config.windowDuration, const Duration(minutes: 1));
      expect(config.maxRetries, 3);
      expect(config.initialBackoff, const Duration(seconds: 1));
      expect(config.maxBackoff, const Duration(seconds: 30));
    });

    test('custom config values', () {
      const config = EndpointConfig(
        maxRequests: 10,
        windowDuration: Duration(minutes: 5),
        maxRetries: 5,
        initialBackoff: Duration(seconds: 2),
        maxBackoff: Duration(seconds: 120),
        backoffMultiplier: 3.0,
      );
      expect(config.maxRequests, 10);
      expect(config.maxRetries, 5);
      expect(config.backoffMultiplier, 3.0);
    });

    test('getBackoffDuration increases with retry count', () {
      final config = EndpointConfig.defaultConfig();
      final d0 = config.getBackoffDuration(0);
      final d1 = config.getBackoffDuration(1);
      final d2 = config.getBackoffDuration(2);
      // Backoff should increase
      expect(d1.inMilliseconds, greaterThanOrEqualTo(d0.inMilliseconds));
      expect(d2.inMilliseconds, greaterThanOrEqualTo(d1.inMilliseconds));
    });

    test('getBackoffDuration respects maxBackoff', () {
      final config = EndpointConfig.defaultConfig();
      final duration = config.getBackoffDuration(100); // Very high retry count
      expect(
        duration.inMilliseconds,
        lessThanOrEqualTo(config.maxBackoff.inMilliseconds),
      );
    });

    test('getBackoffDuration respects initialBackoff as minimum', () {
      final config = EndpointConfig.defaultConfig();
      final duration = config.getBackoffDuration(0);
      expect(
        duration.inMilliseconds,
        greaterThanOrEqualTo(config.initialBackoff.inMilliseconds),
      );
    });
  });

  group('RateLimiter', () {
    late RateLimiter limiter;

    setUp(() {
      limiter = RateLimiter();
    });

    test('should allow requests within limit', () async {
      final result = await limiter.tryAcquire('/api/v1/fields');
      expect(result, true);
    });

    test('should detect auth endpoint type', () async {
      // Auth endpoints have strict 5 req/min limit
      for (var i = 0; i < 5; i++) {
        final result = await limiter.tryAcquire('/api/v1/auth/login');
        expect(result, true, reason: 'Request $i should succeed');
      }
      // 6th should fail
      final result = await limiter.tryAcquire('/api/v1/auth/login');
      expect(result, false, reason: '6th auth request should be rate limited');
    });

    test('should detect sync endpoint type', () async {
      final status = limiter.getStatus('sync');
      expect(status.maxTokens, 30);
    });

    test('should detect upload endpoint type', () async {
      final status = limiter.getStatus('upload');
      expect(status.maxTokens, 10);
    });

    test('should detect default endpoint type', () async {
      final status = limiter.getStatus('default');
      expect(status.maxTokens, 60);
    });

    test('should classify auth paths correctly', () async {
      await limiter.tryAcquire('/auth/login');
      await limiter.tryAcquire('/api/v1/register');
      await limiter.tryAcquire('/api/v1/refresh-token');
      // All should use auth bucket
      final status = limiter.getStatus('auth');
      expect(status.availableTokens, 2); // 5 - 3 = 2
    });

    test('should classify sync paths correctly', () async {
      await limiter.tryAcquire('/api/v1/sync/fields');
      await limiter.tryAcquire('/api/v1/tasks/list');
      await limiter.tryAcquire('/api/v1/outbox/process');
      final status = limiter.getStatus('sync');
      expect(status.availableTokens, 27); // 30 - 3 = 27
    });

    test('should classify upload paths correctly', () async {
      await limiter.tryAcquire('/api/v1/upload/image');
      await limiter.tryAcquire('/api/v1/file/download');
      await limiter.tryAcquire('/api/v1/attachment/list');
      final status = limiter.getStatus('upload');
      expect(status.availableTokens, 7); // 10 - 3 = 7
    });

    test('reset clears all state', () async {
      await limiter.tryAcquire('/api/v1/auth/login');
      await limiter.tryAcquire('/api/v1/fields');
      limiter.reset();
      final authStatus = limiter.getStatus('auth');
      expect(authStatus.availableTokens, 5); // Fresh bucket
    });

    test('getConfig returns correct config for endpoint type', () {
      final authConfig = limiter.getConfig('auth');
      expect(authConfig.maxRequests, 5);

      final syncConfig = limiter.getConfig('sync');
      expect(syncConfig.maxRequests, 30);

      final uploadConfig = limiter.getConfig('upload');
      expect(uploadConfig.maxRequests, 10);
    });

    test('getConfig returns default for unknown endpoint', () {
      final config = limiter.getConfig('unknown_endpoint');
      expect(config.maxRequests, 60);
    });

    test('custom endpoint configs', () {
      final customLimiter = RateLimiter(
        endpointConfigs: {
          'custom': const EndpointConfig(
            maxRequests: 100,
            windowDuration: Duration(minutes: 5),
          ),
        },
      );
      final config = customLimiter.getConfig('custom');
      expect(config.maxRequests, 100);
    });
  });

  group('RateLimitStatus', () {
    test('utilization percentage calculation', () {
      final status = RateLimitStatus(
        endpointType: 'test',
        availableTokens: 3,
        maxTokens: 10,
        refillRate: 1.0,
        queuedRequests: 0,
      );
      expect(status.utilizationPercent, 70.0);
    });

    test('zero utilization when full', () {
      final status = RateLimitStatus(
        endpointType: 'test',
        availableTokens: 10,
        maxTokens: 10,
        refillRate: 1.0,
        queuedRequests: 0,
      );
      expect(status.utilizationPercent, 0.0);
    });

    test('100% utilization when empty', () {
      final status = RateLimitStatus(
        endpointType: 'test',
        availableTokens: 0,
        maxTokens: 10,
        refillRate: 1.0,
        queuedRequests: 0,
      );
      expect(status.utilizationPercent, 100.0);
    });

    test('toString format', () {
      final status = RateLimitStatus(
        endpointType: 'auth',
        availableTokens: 3,
        maxTokens: 5,
        refillRate: 0.083,
        queuedRequests: 2,
      );
      final str = status.toString();
      expect(str, contains('auth'));
      expect(str, contains('3/5'));
      expect(str, contains('2 queued'));
    });
  });

  group('RateLimitException (rate_limiter)', () {
    test('should store message and endpoint type', () {
      final exc = RateLimitException(
        'Too many requests',
        endpointType: 'auth',
      );
      expect(exc.message, 'Too many requests');
      expect(exc.endpointType, 'auth');
    });

    test('toString format', () {
      final exc = RateLimitException(
        'Rate limit exceeded',
        endpointType: 'upload',
      );
      expect(exc.toString(), contains('RateLimitException'));
      expect(exc.toString(), contains('Rate limit exceeded'));
    });

    test('implements Exception', () {
      final exc = RateLimitException('test', endpointType: 'default');
      expect(exc, isA<Exception>());
    });
  });
}
