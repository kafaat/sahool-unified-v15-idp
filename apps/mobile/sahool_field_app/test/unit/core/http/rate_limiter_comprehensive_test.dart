import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/http/rate_limiter.dart';

/// Comprehensive rate limiter tests
/// اختبارات شاملة لمحدد معدل الطلبات
void main() {
  group('RateLimiter', () {
    late RateLimiter rateLimiter;

    setUp(() {
      rateLimiter = RateLimiter();
    });

    group('tryAcquire', () {
      test('succeeds on first request', () async {
        final result = await rateLimiter.tryAcquire('/api/v1/fields');
        expect(result, isTrue);
      });

      test('succeeds for multiple requests within limit', () async {
        for (int i = 0; i < 10; i++) {
          final result = await rateLimiter.tryAcquire('/api/v1/fields');
          expect(result, isTrue);
        }
      });

      test('auth endpoint has lower limit than default', () async {
        // Auth has 5 requests/minute limit
        int consumed = 0;
        for (int i = 0; i < 10; i++) {
          if (await rateLimiter.tryAcquire('/api/v1/auth/login')) {
            consumed++;
          }
        }
        // Should consume exactly 5 (the auth bucket capacity)
        expect(consumed, 5);
      });
    });

    group('getStatus', () {
      test('returns full capacity for fresh limiter', () {
        final status = rateLimiter.getStatus('default');
        expect(status.endpointType, 'default');
        expect(status.maxTokens, 60);
        expect(status.queuedRequests, 0);
      });

      test('returns reduced tokens after consumption', () async {
        await rateLimiter.tryAcquire('/api/v1/fields');
        final status = rateLimiter.getStatus('default');
        expect(status.availableTokens, lessThan(60));
      });
    });

    group('getConfig', () {
      test('returns auth config', () {
        final config = rateLimiter.getConfig('auth');
        expect(config.maxRequests, 5);
        expect(config.maxRetries, 3);
      });

      test('returns sync config', () {
        final config = rateLimiter.getConfig('sync');
        expect(config.maxRequests, 30);
        expect(config.maxRetries, 5);
      });

      test('returns upload config', () {
        final config = rateLimiter.getConfig('upload');
        expect(config.maxRequests, 10);
      });

      test('returns default config for unknown endpoint', () {
        final config = rateLimiter.getConfig('unknown');
        expect(config.maxRequests, 60);
      });
    });

    group('reset', () {
      test('clears all buckets', () async {
        // Consume some tokens
        for (int i = 0; i < 5; i++) {
          await rateLimiter.tryAcquire('/api/v1/auth/login');
        }
        // Auth bucket should be empty
        expect(await rateLimiter.tryAcquire('/api/v1/auth/login'), isFalse);

        // Reset
        rateLimiter.reset();

        // Should have tokens again
        expect(await rateLimiter.tryAcquire('/api/v1/auth/login'), isTrue);
      });
    });
  });

  group('TokenBucket', () {
    test('starts with full capacity', () {
      final bucket = TokenBucket(capacity: 10, refillRate: 1.0);
      expect(bucket.availableTokens, 10);
    });

    test('tryConsume reduces tokens', () {
      final bucket = TokenBucket(capacity: 10, refillRate: 1.0);
      expect(bucket.tryConsume(), isTrue);
      expect(bucket.availableTokens, 9);
    });

    test('tryConsume fails when empty', () {
      final bucket = TokenBucket(capacity: 2, refillRate: 0.01);
      expect(bucket.tryConsume(), isTrue);
      expect(bucket.tryConsume(), isTrue);
      expect(bucket.tryConsume(), isFalse);
    });

    test('tryConsume with multiple tokens', () {
      final bucket = TokenBucket(capacity: 5, refillRate: 1.0);
      expect(bucket.tryConsume(tokens: 3), isTrue);
      expect(bucket.availableTokens, 2);
      expect(bucket.tryConsume(tokens: 3), isFalse);
    });

    test('getWaitTime returns zero when tokens available', () {
      final bucket = TokenBucket(capacity: 10, refillRate: 1.0);
      expect(bucket.getWaitTime(), Duration.zero);
    });

    test('getWaitTime returns positive duration when empty', () {
      final bucket = TokenBucket(capacity: 1, refillRate: 1.0);
      bucket.tryConsume();
      final waitTime = bucket.getWaitTime();
      expect(waitTime.inMilliseconds, greaterThan(0));
    });
  });

  group('EndpointConfig', () {
    test('construction with required fields', () {
      const config = EndpointConfig(
        maxRequests: 10,
        windowDuration: Duration(minutes: 1),
      );
      expect(config.maxRequests, 10);
      expect(config.windowDuration, const Duration(minutes: 1));
      expect(config.maxRetries, 3); // default
      expect(config.backoffMultiplier, 2.0); // default
    });

    test('defaultConfig factory', () {
      final config = EndpointConfig.defaultConfig();
      expect(config.maxRequests, 60);
      expect(config.windowDuration, const Duration(minutes: 1));
      expect(config.maxRetries, 3);
      expect(config.initialBackoff, const Duration(seconds: 1));
      expect(config.maxBackoff, const Duration(seconds: 30));
    });

    test('getBackoffDuration increases with retry count', () {
      final config = EndpointConfig.defaultConfig();

      final d0 = config.getBackoffDuration(0);
      final d1 = config.getBackoffDuration(1);
      final d2 = config.getBackoffDuration(2);
      final d3 = config.getBackoffDuration(3);

      // Each retry should produce a longer (or equal) duration
      expect(d1.inMilliseconds, greaterThanOrEqualTo(d0.inMilliseconds));
      expect(d2.inMilliseconds, greaterThanOrEqualTo(d1.inMilliseconds));
      expect(d3.inMilliseconds, greaterThanOrEqualTo(d2.inMilliseconds));

      // First retry should be at least initialBackoff
      expect(d0.inMilliseconds, greaterThanOrEqualTo(config.initialBackoff.inMilliseconds));
    });

    test('getBackoffDuration respects maxBackoff', () {
      final config = EndpointConfig.defaultConfig();

      // retry 10: should be capped at maxBackoff
      final backoff = config.getBackoffDuration(10);
      expect(backoff.inMilliseconds, lessThanOrEqualTo(config.maxBackoff.inMilliseconds));
    });

    test('getBackoffDuration respects minimum', () {
      const config = EndpointConfig(
        maxRequests: 10,
        windowDuration: Duration(minutes: 1),
        initialBackoff: Duration(seconds: 5),
      );

      // retry 0: 5s * 2^0 = 5s (not less than initialBackoff)
      expect(config.getBackoffDuration(0).inSeconds, 5);
    });
  });

  group('RateLimitStatus', () {
    test('construction with all fields', () {
      final status = RateLimitStatus(
        endpointType: 'auth',
        availableTokens: 3,
        maxTokens: 5,
        refillRate: 0.083,
        queuedRequests: 0,
      );
      expect(status.endpointType, 'auth');
      expect(status.availableTokens, 3);
      expect(status.maxTokens, 5);
      expect(status.queuedRequests, 0);
    });
  });

  group('RateLimitException', () {
    test('stores message and endpointType', () {
      final exception = RateLimitException(
        'Rate limit exceeded',
        endpointType: 'auth',
      );
      expect(exception.message, 'Rate limit exceeded');
      expect(exception.endpointType, 'auth');
    });

    test('toString includes message', () {
      final exception = RateLimitException(
        'Rate limit exceeded',
        endpointType: 'auth',
      );
      expect(exception.toString(), contains('Rate limit exceeded'));
    });
  });
}
