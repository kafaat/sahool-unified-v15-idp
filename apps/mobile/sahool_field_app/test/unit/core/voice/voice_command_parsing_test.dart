import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/voice/voice_command_service.dart';

void main() {
  late VoiceCommandService service;

  setUp(() {
    service = VoiceCommandService.instance;
  });

  group('Command Parsing - Open Field', () {
    test('should parse "افتح الحقل الأول"', () {
      final cmd = service.parseCommand('افتح الحقل الأول');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.openField);
      expect(cmd.parameters['fieldId'], '1');
    });

    test('should parse "اعرض حقل 3"', () {
      final cmd = service.parseCommand('اعرض حقل 3');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.openField);
      expect(cmd.parameters['fieldId'], '3');
    });

    test('should parse "شوف الحقل الثاني"', () {
      final cmd = service.parseCommand('شوف الحقل الثاني');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.openField);
      expect(cmd.parameters['fieldId'], '2');
    });

    test('should parse "فتح الحقل الخامس"', () {
      final cmd = service.parseCommand('فتح الحقل الخامس');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.openField);
      expect(cmd.parameters['fieldId'], '5');
    });
  });

  group('Command Parsing - Crop Status', () {
    test('should parse "حالة المحصول"', () {
      final cmd = service.parseCommand('حالة المحصول');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.cropStatus);
    });

    test('should parse "كيف المحصول"', () {
      final cmd = service.parseCommand('كيف المحصول');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.cropStatus);
    });

    test('should parse "ما حالة الزراعة"', () {
      final cmd = service.parseCommand('ما حالة الزراعة');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.cropStatus);
    });
  });

  group('Command Parsing - Record Irrigation', () {
    test('should parse "سجل ري"', () {
      final cmd = service.parseCommand('سجل ري للحقل');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.recordIrrigation);
    });

    test('should parse "ابدأ الري"', () {
      final cmd = service.parseCommand('ابدأ الري');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.recordIrrigation);
    });
  });

  group('Command Parsing - Show Tasks', () {
    test('should parse "عرض المهام"', () {
      final cmd = service.parseCommand('عرض المهام');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.showTasks);
    });

    test('should parse "شوف الأعمال"', () {
      final cmd = service.parseCommand('شوف الأعمال');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.showTasks);
    });
  });

  group('Command Parsing - Create Task', () {
    test('should parse "اضف مهمة"', () {
      final cmd = service.parseCommand('اضف مهمة جديدة');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.createTask);
    });
  });

  group('Command Parsing - Weather', () {
    test('should parse "كيف الطقس"', () {
      final cmd = service.parseCommand('كيف الطقس');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.weather);
    });

    test('should parse "ما الطقس"', () {
      final cmd = service.parseCommand('ما الطقس');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.weather);
    });

    test('should parse "شو الجو"', () {
      final cmd = service.parseCommand('شو الجو');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.weather);
    });
  });

  group('Command Parsing - Start Scout', () {
    test('should parse "ابدأ مسح"', () {
      final cmd = service.parseCommand('ابدأ مسح الحقل');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.startScout);
    });

    test('should parse "شغل المسح"', () {
      final cmd = service.parseCommand('شغل المسح');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.startScout);
    });
  });

  group('Command Parsing - Report Issue', () {
    test('should parse "سجل مشكلة"', () {
      final cmd = service.parseCommand('سجل مشكلة في الحقل');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.reportIssue);
    });

    test('should parse "في آفة"', () {
      final cmd = service.parseCommand('في آفة على النبات');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.reportIssue);
    });
  });

  group('Command Parsing - Capture Photo', () {
    test('should parse "التقط صورة"', () {
      final cmd = service.parseCommand('التقط صورة');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.capturePhoto);
    });

    test('should parse "خذ صورة"', () {
      final cmd = service.parseCommand('خذ صورة');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.capturePhoto);
    });
  });

  group('Command Parsing - Daily Summary', () {
    test('should parse "ملخص اليوم"', () {
      final cmd = service.parseCommand('ملخص اليوم');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.dailySummary);
    });

    test('should parse "تقرير اليوم"', () {
      final cmd = service.parseCommand('تقرير اليوم');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.dailySummary);
    });
  });

  group('Command Parsing - Unknown', () {
    test('should return unknown for unrecognized text', () {
      final cmd = service.parseCommand('مرحبا كيف حالك');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.unknown);
      expect(cmd.isRecognized, false);
    });

    test('should preserve raw text in unknown commands', () {
      final cmd = service.parseCommand('نص غير معروف');
      expect(cmd, isNotNull);
      expect(cmd!.rawText, 'نص غير معروف');
    });
  });

  group('Arabic Text Normalization', () {
    test('should handle different alif forms', () {
      // إعرض should normalize to اعرض
      final cmd = service.parseCommand('إعرض الحقل');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.openField);
    });

    test('should handle taa marbuta normalization', () {
      // مهمة → مهمه after normalization
      final cmd = service.parseCommand('اضف مهمة');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.createTask);
    });
  });

  group('Field ID Extraction', () {
    test('should extract numeric field IDs', () {
      final cmd = service.parseCommand('افتح حقل رقم 7');
      expect(cmd, isNotNull);
      expect(cmd!.type, VoiceCommandType.openField);
      expect(cmd.parameters['fieldId'], '7');
    });

    test('should extract الأول as 1', () {
      final cmd = service.parseCommand('افتح الحقل الأول');
      expect(cmd, isNotNull);
      expect(cmd!.parameters['fieldId'], '1');
    });

    test('should extract الثالث as 3', () {
      final cmd = service.parseCommand('افتح الحقل الثالث');
      expect(cmd, isNotNull);
      expect(cmd!.parameters['fieldId'], '3');
    });

    test('should extract الرابع as 4', () {
      final cmd = service.parseCommand('افتح الحقل الرابع');
      expect(cmd, isNotNull);
      expect(cmd!.parameters['fieldId'], '4');
    });
  });
}
