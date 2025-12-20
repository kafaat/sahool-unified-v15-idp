import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/utils/app_logger.dart';

void main() {
  group('AppLogger', () {
    setUp(() {
      // Clear log buffer before each test
      AppLogger.clearBuffer();
    });

    group('Logging Methods', () {
      test('debug log should add entry to buffer', () {
        AppLogger.d('Test debug message');

        final logs = AppLogger.getRecentLogs();
        expect(logs, isNotEmpty);
        expect(logs.last.level, equals(LogLevel.debug));
        expect(logs.last.message, equals('Test debug message'));
      });

      test('info log should add entry to buffer', () {
        AppLogger.i('Test info message');

        final logs = AppLogger.getRecentLogs();
        expect(logs, isNotEmpty);
        expect(logs.last.level, equals(LogLevel.info));
      });

      test('warning log should add entry to buffer', () {
        AppLogger.w('Test warning message');

        final logs = AppLogger.getRecentLogs();
        expect(logs, isNotEmpty);
        expect(logs.last.level, equals(LogLevel.warning));
      });

      test('error log should add entry to buffer', () {
        AppLogger.e('Test error message', error: Exception('Test exception'));

        final logs = AppLogger.getRecentLogs();
        expect(logs, isNotEmpty);
        expect(logs.last.level, equals(LogLevel.error));
        expect(logs.last.error, isNotNull);
      });

      test('critical log should add entry to buffer', () {
        AppLogger.critical('Test critical message');

        final logs = AppLogger.getRecentLogs();
        expect(logs, isNotEmpty);
        expect(logs.last.level, equals(LogLevel.critical));
      });
    });

    group('Specialized Logging', () {
      test('network log should include method and URL', () {
        AppLogger.network('GET', '/api/users', statusCode: 200);

        final logs = AppLogger.getRecentLogs();
        expect(logs, isNotEmpty);
        expect(logs.last.message, contains('GET'));
        expect(logs.last.message, contains('/api/users'));
        expect(logs.last.message, contains('200'));
      });

      test('network log with error status should be error level', () {
        AppLogger.network('POST', '/api/data', statusCode: 500);

        final logs = AppLogger.getRecentLogs();
        expect(logs.last.level, equals(LogLevel.error));
      });

      test('sync log should have correct format', () {
        AppLogger.sync('pull', success: true, details: '10 items');

        final logs = AppLogger.getRecentLogs();
        expect(logs, isNotEmpty);
        expect(logs.last.message, contains('Sync'));
        expect(logs.last.message, contains('pull'));
      });

      test('user action log should include action', () {
        AppLogger.userAction('button_click', params: {'button': 'submit'});

        final logs = AppLogger.getRecentLogs();
        expect(logs, isNotEmpty);
        expect(logs.last.message, contains('User'));
        expect(logs.last.message, contains('button_click'));
      });

      test('performance log should include duration', () {
        AppLogger.performance('database_query', const Duration(milliseconds: 150));

        final logs = AppLogger.getRecentLogs();
        expect(logs, isNotEmpty);
        expect(logs.last.message, contains('150ms'));
      });
    });

    group('Log Buffer', () {
      test('getRecentLogs should return specified count', () {
        // Add multiple logs
        for (int i = 0; i < 10; i++) {
          AppLogger.d('Message $i');
        }

        final logs = AppLogger.getRecentLogs(count: 5);
        expect(logs.length, equals(5));
      });

      test('clearBuffer should remove all logs', () {
        AppLogger.d('Test message');
        expect(AppLogger.getRecentLogs(), isNotEmpty);

        AppLogger.clearBuffer();
        expect(AppLogger.getRecentLogs(), isEmpty);
      });

      test('exportLogs should return string representation', () {
        AppLogger.d('Test message 1');
        AppLogger.i('Test message 2');

        final exported = AppLogger.exportLogs();
        expect(exported, isNotEmpty);
        expect(exported, contains('Test message 1'));
        expect(exported, contains('Test message 2'));
      });
    });

    group('Log Tags', () {
      test('logs should include tag when provided', () {
        AppLogger.d('Tagged message', tag: 'CustomTag');

        final logs = AppLogger.getRecentLogs();
        expect(logs.last.tag, equals('CustomTag'));
      });

      test('logs should include data when provided', () {
        AppLogger.d('Data message', data: {'key': 'value'});

        final logs = AppLogger.getRecentLogs();
        expect(logs.last.data, isNotNull);
        expect(logs.last.data!['key'], equals('value'));
      });
    });

    group('LogEntry', () {
      test('formattedMessage should include message', () {
        AppLogger.d('Test message');

        final log = AppLogger.getRecentLogs().last;
        expect(log.formattedMessage, contains('Test message'));
      });

      test('toJson should return valid map', () {
        AppLogger.d('Test message', tag: 'TestTag');

        final log = AppLogger.getRecentLogs().last;
        final json = log.toJson();

        expect(json, isA<Map<String, dynamic>>());
        expect(json['level'], equals('debug'));
        expect(json['message'], equals('Test message'));
        expect(json['tag'], equals('TestTag'));
        expect(json['timestamp'], isNotNull);
      });

      test('toString should include all components', () {
        AppLogger.e('Error occurred', tag: 'ErrorTag', error: Exception('Test'));

        final log = AppLogger.getRecentLogs().last;
        final str = log.toString();

        expect(str, contains('ERROR'));
        expect(str, contains('ErrorTag'));
        expect(str, contains('Error occurred'));
      });
    });

    group('Configuration', () {
      test('configure should update settings', () {
        AppLogger.configure(minLevel: LogLevel.warning);

        // Debug logs should be filtered
        AppLogger.d('Debug message');
        AppLogger.w('Warning message');

        final logs = AppLogger.getRecentLogs();
        // Should only have warning
        expect(logs.where((l) => l.level == LogLevel.debug), isEmpty);
        expect(logs.where((l) => l.level == LogLevel.warning), isNotEmpty);

        // Reset
        AppLogger.configure(minLevel: LogLevel.debug);
      });
    });
  });

  group('LoggerMixin', () {
    test('mixin should provide logging methods', () {
      final testClass = _TestClassWithLogger();
      testClass.testLog();

      final logs = AppLogger.getRecentLogs();
      expect(logs, isNotEmpty);
      expect(logs.last.tag, equals('_TestClassWithLogger'));
    });
  });
}

// Test class using LoggerMixin
class _TestClassWithLogger with LoggerMixin {
  void testLog() {
    logDebug('Test debug from mixin');
  }
}
