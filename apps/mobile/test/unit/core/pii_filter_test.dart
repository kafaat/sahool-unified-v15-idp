import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile/core/utils/pii_filter.dart';

void main() {
  group('PiiFilter - Phone Number Masking', () {
    test('Should mask Saudi phone numbers with +966', () {
      final result = PiiFilter.sanitize('+966501234567');
      expect(result, '+966****4567');
    });

    test('Should mask Saudi phone numbers with 966', () {
      final result = PiiFilter.sanitize('966501234567');
      expect(result, '966****4567');
    });

    test('Should mask Saudi phone numbers with leading 0', () {
      final result = PiiFilter.sanitize('0501234567');
      expect(result, '0****4567');
    });

    test('Should mask phone numbers in text', () {
      final result = PiiFilter.sanitize('User phone: +966501234567');
      expect(result, 'User phone: +966****4567');
    });

    test('Should mask multiple phone numbers', () {
      final result = PiiFilter.sanitize(
        'Contact: +966501234567 or 0557778888',
      );
      expect(result, contains('****4567'));
      expect(result, contains('****8888'));
    });

    test('Should mask international phone numbers', () {
      final result = PiiFilter.sanitize('+1-555-123-4567');
      expect(result, contains('****4567'));
    });
  });

  group('PiiFilter - Email Masking', () {
    test('Should mask email addresses', () {
      final result = PiiFilter.sanitize('ahmed@example.com');
      expect(result, 'ah****@example.com');
    });

    test('Should mask emails with short usernames', () {
      final result = PiiFilter.sanitize('ab@example.com');
      expect(result, 'ab****@example.com');
    });

    test('Should mask single character username', () {
      final result = PiiFilter.sanitize('a@example.com');
      expect(result, 'a*@example.com');
    });

    test('Should mask email in text', () {
      final result = PiiFilter.sanitize('Contact: ahmed@example.com');
      expect(result, 'Contact: ah****@example.com');
    });

    test('Should mask multiple emails', () {
      final result = PiiFilter.sanitize(
        'From: user1@test.com To: user2@test.com',
      );
      expect(result, contains('us****@test.com'));
    });

    test('Should preserve domain name', () {
      final result = PiiFilter.sanitize('test@sahool.sa');
      expect(result, contains('@sahool.sa'));
    });
  });

  group('PiiFilter - National ID Masking', () {
    test('Should mask 10-digit national ID starting with 1', () {
      final result = PiiFilter.sanitize('1234567890');
      expect(result, '12******90');
    });

    test('Should mask 10-digit national ID starting with 2', () {
      final result = PiiFilter.sanitize('2987654321');
      expect(result, '29******21');
    });

    test('Should mask national ID in text', () {
      final result = PiiFilter.sanitize('ID: 1234567890');
      expect(result, 'ID: 12******90');
    });

    test('Should not mask other 10-digit numbers', () {
      final result = PiiFilter.sanitize('Phone: 0501234567');
      // Should be treated as phone, not national ID
      expect(result, contains('****4567'));
    });
  });

  group('PiiFilter - Credit Card Masking', () {
    test('Should mask credit card with dashes', () {
      final result = PiiFilter.sanitize('4532-1234-5678-9010');
      expect(result, '****-****-****-9010');
    });

    test('Should mask credit card with spaces', () {
      final result = PiiFilter.sanitize('4532 1234 5678 9010');
      expect(result, '****-****-****-9010');
    });

    test('Should mask credit card without separators', () {
      final result = PiiFilter.sanitize('4532123456789010');
      expect(result, '****-****-****-9010');
    });

    test('Should mask credit card in text', () {
      final result = PiiFilter.sanitize('Card: 4532-1234-5678-9010');
      expect(result, 'Card: ****-****-****-9010');
    });
  });

  group('PiiFilter - Token and Password Removal', () {
    test('Should remove JWT tokens', () {
      final token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
          'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.'
          'SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';

      final result = PiiFilter.sanitize(token);
      expect(result, '[TOKEN_REDACTED]');
    });

    test('Should remove Bearer tokens', () {
      final result = PiiFilter.sanitize('Bearer abc123xyz456');
      expect(result, 'Bearer [REDACTED]');
    });

    test('Should remove tokens in Authorization header', () {
      final result = PiiFilter.sanitize('Authorization: Bearer token123');
      expect(result, contains('[REDACTED]'));
    });

    test('Should redact long API keys', () {
      final apiKey = 'api_key_test_abcdef1234567890xyz';
      final result = PiiFilter.sanitize('API Key: $apiKey');
      expect(result, contains('[KEY_REDACTED]'));
    });
  });

  group('PiiFilter - GPS Coordinate Rounding', () {
    test('Should round GPS coordinates to 3 decimal places', () {
      final result = PiiFilter.sanitize('24.7135517, 46.6752957');
      expect(result, '24.714, 46.675');
    });

    test('Should round coordinates in text', () {
      final result = PiiFilter.sanitize('Location: 24.7135517, 46.6752957');
      expect(result, 'Location: 24.714, 46.675');
    });

    test('Should handle negative coordinates', () {
      final result = PiiFilter.sanitize('-33.8688197, 151.2092955');
      expect(result, '-33.869, 151.209');
    });
  });

  group('PiiFilter - Arabic Name Masking', () {
    test('Should mask Arabic names', () {
      final result = PiiFilter.sanitize('محمد بن سلمان');
      expect(result, contains('م****د'));
      expect(result, contains('ب*ن'));
      expect(result, contains('س****ن'));
    });

    test('Should mask long Arabic names', () {
      final result = PiiFilter.sanitize('عبدالرحمن');
      expect(result, 'ع*******ن');
    });

    test('Should not mask short Arabic words', () {
      final result = PiiFilter.sanitize('من هو');
      // Too short, should not be masked
      expect(result, 'من هو');
    });
  });

  group('PiiFilter - Map Sanitization', () {
    test('Should sanitize sensitive fields in map', () {
      final data = {
        'username': 'ahmed',
        'password': 'secret123',
        'token': 'abc123',
      };

      final result = PiiFilter.sanitize(data);
      expect(result['username'], 'ahmed');
      expect(result['password'], '[REDACTED]');
      expect(result['token'], '[REDACTED]');
    });

    test('Should sanitize nested maps', () {
      final data = {
        'user': {
          'name': 'Ahmed',
          'email': 'ahmed@example.com',
          'password': 'secret',
        },
      };

      final result = PiiFilter.sanitize(data);
      expect(result['user']['name'], 'Ahmed');
      expect(result['user']['email'], 'ah****@example.com');
      expect(result['user']['password'], '[REDACTED]');
    });

    test('Should sanitize PII in map values', () {
      final data = {
        'phone': '+966501234567',
        'email': 'user@example.com',
        'note': 'Contact at +966557778888',
      };

      final result = PiiFilter.sanitize(data);
      expect(result['phone'], '+966****4567');
      expect(result['email'], 'us****@example.com');
      expect(result['note'], contains('****8888'));
    });
  });

  group('PiiFilter - List Sanitization', () {
    test('Should sanitize list of strings', () {
      final list = [
        '+966501234567',
        'ahmed@example.com',
        'Bearer token123',
      ];

      final result = PiiFilter.sanitize(list);
      expect(result[0], '+966****4567');
      expect(result[1], 'ah****@example.com');
      expect(result[2], contains('[REDACTED]'));
    });

    test('Should sanitize list of maps', () {
      final list = [
        {'phone': '+966501234567'},
        {'email': 'user@example.com'},
      ];

      final result = PiiFilter.sanitize(list);
      expect(result[0]['phone'], '+966****4567');
      expect(result[1]['email'], 'us****@example.com');
    });
  });

  group('PiiFilter - Header Sanitization', () {
    test('Should sanitize authorization headers', () {
      final headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer token123',
      };

      final result = PiiFilter.sanitizeHeaders(headers);
      expect(result['Content-Type'], 'application/json');
      expect(result['Authorization'], '[REDACTED]');
    });

    test('Should sanitize API key headers', () {
      final headers = {
        'X-API-Key': 'secret_key_123',
      };

      final result = PiiFilter.sanitizeHeaders(headers);
      expect(result['X-API-Key'], '[REDACTED]');
    });

    test('Should sanitize cookie headers', () {
      final headers = {
        'Cookie': 'session=abc123; user=xyz',
      };

      final result = PiiFilter.sanitizeHeaders(headers);
      expect(result['Cookie'], '[REDACTED]');
    });
  });

  group('PiiFilter - Request/Response Body Sanitization', () {
    test('Should sanitize request body as map', () {
      final body = {
        'username': 'ahmed',
        'password': 'secret123',
        'phone': '+966501234567',
      };

      final result = PiiFilter.sanitizeRequestBody(body);
      expect(result['username'], 'ahmed');
      expect(result['password'], '[REDACTED]');
      expect(result['phone'], '+966****4567');
    });

    test('Should sanitize JSON string body', () {
      final body = '{"password":"secret123","email":"test@example.com"}';
      final result = PiiFilter.sanitizeRequestBody(body);

      expect(result, contains('[REDACTED]'));
      expect(result, contains('****@example.com'));
    });

    test('Should handle null body', () {
      final result = PiiFilter.sanitizeRequestBody(null);
      expect(result, null);
    });
  });

  group('PiiFilter - Error Sanitization', () {
    test('Should sanitize error messages', () {
      final error = Exception('Token expired: Bearer abc123');
      final result = PiiFilter.sanitizeError(error);

      expect(result, contains('[REDACTED]'));
    });

    test('Should sanitize error with phone number', () {
      final error = Exception('Failed to send SMS to +966501234567');
      final result = PiiFilter.sanitizeError(error);

      expect(result, contains('****4567'));
    });
  });

  group('PiiFilter - PII Detection', () {
    test('Should detect phone numbers', () {
      expect(PiiFilter.containsPii('+966501234567'), true);
    });

    test('Should detect emails', () {
      expect(PiiFilter.containsPii('ahmed@example.com'), true);
    });

    test('Should detect tokens', () {
      expect(PiiFilter.containsPii('Bearer abc123'), true);
    });

    test('Should detect national IDs', () {
      expect(PiiFilter.containsPii('1234567890'), true);
    });

    test('Should not detect normal text', () {
      expect(PiiFilter.containsPii('Hello world'), false);
    });
  });

  group('PiiFilter - PII Summary', () {
    test('Should count PII types in text', () {
      final text = '''
        Contact: +966501234567
        Email: ahmed@example.com
        Another phone: 0557778888
        Token: Bearer abc123
      ''';

      final summary = PiiFilter.getPiiSummary(text);
      expect(summary['phones']! >= 2, true);
      expect(summary['emails'], 1);
      expect(summary['tokens']! >= 1, true);
    });

    test('Should return zero counts for clean text', () {
      final summary = PiiFilter.getPiiSummary('Hello world');
      expect(summary['phones'], 0);
      expect(summary['emails'], 0);
      expect(summary['tokens'], 0);
    });
  });

  group('PiiFilter - String Extension', () {
    test('Should sanitize using extension', () {
      final result = '+966501234567'.sanitizePii();
      expect(result, '+966****4567');
    });

    test('Should detect PII using extension', () {
      expect('+966501234567'.containsPii(), true);
      expect('Hello world'.containsPii(), false);
    });
  });

  group('PiiFilter - Map Extension', () {
    test('Should sanitize map using extension', () {
      final data = {
        'phone': '+966501234567',
        'password': 'secret',
      }.sanitizePii();

      expect(data['phone'], '+966****4567');
      expect(data['password'], '[REDACTED]');
    });
  });

  group('PiiFilter - Edge Cases', () {
    test('Should handle null input', () {
      final result = PiiFilter.sanitize(null);
      expect(result, null);
    });

    test('Should handle empty string', () {
      final result = PiiFilter.sanitize('');
      expect(result, '');
    });

    test('Should handle empty map', () {
      final result = PiiFilter.sanitize({});
      expect(result, {});
    });

    test('Should handle empty list', () {
      final result = PiiFilter.sanitize([]);
      expect(result, []);
    });

    test('Should handle mixed content types', () {
      final data = {
        'string': '+966501234567',
        'number': 12345,
        'bool': true,
        'null': null,
        'list': ['test@example.com'],
      };

      final result = PiiFilter.sanitize(data);
      expect(result['string'], '+966****4567');
      expect(result['number'], 12345);
      expect(result['bool'], true);
      expect(result['null'], null);
      expect(result['list'][0], 'te****@example.com');
    });

    test('Should handle very long strings efficiently', () {
      final longText = '+966501234567 ' * 1000;
      final result = PiiFilter.sanitize(longText);

      expect(result, contains('****4567'));
      expect(result, isNot(contains('+966501234567')));
    });

    test('Should handle special characters in text', () {
      final text = 'Email: ahmed@example.com\nPhone: +966501234567\tID: 1234567890';
      final result = PiiFilter.sanitize(text);

      expect(result, contains('****@example.com'));
      expect(result, contains('****4567'));
      expect(result, contains('******90'));
    });

    test('Should preserve non-PII data exactly', () {
      final data = {
        'username': 'ahmed',
        'age': 30,
        'active': true,
        'settings': {'theme': 'dark'},
      };

      final result = PiiFilter.sanitize(data);
      expect(result['username'], 'ahmed');
      expect(result['age'], 30);
      expect(result['active'], true);
      expect(result['settings']['theme'], 'dark');
    });
  });

  group('PiiFilter - Case Sensitivity', () {
    test('Should handle case variations in field names', () {
      final data = {
        'Password': 'secret1',
        'PASSWORD': 'secret2',
        'password': 'secret3',
        'Token': 'token1',
        'AccessToken': 'token2',
      };

      final result = PiiFilter.sanitize(data);
      expect(result['Password'], '[REDACTED]');
      expect(result['PASSWORD'], '[REDACTED]');
      expect(result['password'], '[REDACTED]');
      expect(result['Token'], '[REDACTED]');
      expect(result['AccessToken'], '[REDACTED]');
    });
  });

  group('PiiFilter - Real-world Scenarios', () {
    test('Should sanitize login request', () {
      final request = {
        'email': 'user@example.com',
        'password': 'P@ssw0rd123',
        'deviceId': 'device-abc-123',
      };

      final result = PiiFilter.sanitize(request);
      expect(result['email'], 'us****@example.com');
      expect(result['password'], '[REDACTED]');
      expect(result['deviceId'], 'device-abc-123');
    });

    test('Should sanitize user profile response', () {
      final response = {
        'user': {
          'id': '123',
          'name': 'Ahmed',
          'email': 'ahmed@example.com',
          'phone': '+966501234567',
          'nationalId': '1234567890',
        },
      };

      final result = PiiFilter.sanitize(response);
      expect(result['user']['id'], '123');
      expect(result['user']['name'], 'Ahmed');
      expect(result['user']['email'], 'ah****@example.com');
      expect(result['user']['phone'], '+966****4567');
      expect(result['user']['nationalId'], '12******90');
    });

    test('Should sanitize error messages', () {
      final error = '''
        Authentication failed for user ahmed@example.com
        Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature
        Please contact support at +966501234567
      ''';

      final result = PiiFilter.sanitize(error);
      expect(result, contains('****@example.com'));
      expect(result, contains('[TOKEN_REDACTED]'));
      expect(result, contains('****4567'));
    });
  });
}
