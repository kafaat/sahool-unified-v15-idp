/// Validators Unit Tests - اختبارات وحدة التحقق
///
/// Comprehensive tests for all validation utilities in the SAHOOL platform.
/// Tests cover: required fields, email, phone (Saudi/Yemen/international),
/// Arabic text, field name, password strength, username, and field-specific
/// validators (area, NDVI, crop type).
///
/// Run with: flutter test test/core/validation/validators_test.dart
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile_core/core/validation/validators.dart';

void main() {
  // ===========================================================================
  // ValidationResult
  // ===========================================================================

  group('ValidationResult', () {
    test('success is valid with no error messages', () {
      const result = ValidationResult.success;
      expect(result.isValid, isTrue);
      expect(result.errorMessage, isNull);
      expect(result.errorMessageAr, isNull);
    });

    test('error factory creates invalid result with bilingual messages', () {
      final result = ValidationResult.error('Email is required', 'البريد مطلوب');
      expect(result.isValid, isFalse);
      expect(result.errorMessage, 'Email is required');
      expect(result.errorMessageAr, 'البريد مطلوب');
    });

    test('getMessage returns Arabic by default', () {
      final result = ValidationResult.error('Required', 'مطلوب');
      expect(result.getMessage(), 'مطلوب');
    });

    test('getMessage returns English when arabic is false', () {
      final result = ValidationResult.error('Required', 'مطلوب');
      expect(result.getMessage(arabic: false), 'Required');
    });

    test('getMessage returns null for success', () {
      expect(ValidationResult.success.getMessage(), isNull);
      expect(ValidationResult.success.getMessage(arabic: false), isNull);
    });

    test('toString shows success or error', () {
      expect(ValidationResult.success.toString(), 'ValidationResult.success');
      final err = ValidationResult.error('Bad', 'سيء');
      expect(err.toString(), contains('ValidationResult.error'));
      expect(err.toString(), contains('Bad'));
    });
  });

  // ===========================================================================
  // Required Field Validators
  // ===========================================================================

  group('Validators.required', () {
    test('returns error for null value', () {
      final result = Validators.required(null);
      expect(result.isValid, isFalse);
      expect(result.errorMessage, contains('required'));
    });

    test('returns error for empty string', () {
      expect(Validators.required('').isValid, isFalse);
    });

    test('returns error for whitespace-only string', () {
      expect(Validators.required('   ').isValid, isFalse);
    });

    test('returns success for non-empty string', () {
      expect(Validators.required('hello').isValid, isTrue);
    });

    test('includes custom field name in error message', () {
      final result = Validators.required(null, fieldName: 'Name', fieldNameAr: 'الاسم');
      expect(result.errorMessage, contains('Name'));
      expect(result.errorMessageAr, contains('الاسم'));
    });
  });

  group('Validators.requiredValue', () {
    test('returns error for null', () {
      final result = Validators.requiredValue<int>(null);
      expect(result.isValid, isFalse);
    });

    test('returns success for non-null value', () {
      expect(Validators.requiredValue<int>(42).isValid, isTrue);
    });

    test('returns success for zero', () {
      expect(Validators.requiredValue<int>(0).isValid, isTrue);
    });

    test('returns success for false boolean', () {
      expect(Validators.requiredValue<bool>(false).isValid, isTrue);
    });
  });

  group('Validators.requiredList', () {
    test('returns error for null list', () {
      expect(Validators.requiredList<int>(null).isValid, isFalse);
    });

    test('returns error for empty list', () {
      expect(Validators.requiredList<int>([]).isValid, isFalse);
    });

    test('returns success for list with items', () {
      expect(Validators.requiredList<int>([1, 2]).isValid, isTrue);
    });

    test('enforces minItems parameter', () {
      expect(Validators.requiredList<int>([1], minItems: 2).isValid, isFalse);
      expect(Validators.requiredList<int>([1, 2], minItems: 2).isValid, isTrue);
    });

    test('includes custom field name in error', () {
      final result = Validators.requiredList<String>(
        null,
        fieldName: 'Tags',
        fieldNameAr: 'العلامات',
      );
      expect(result.errorMessage, contains('Tags'));
      expect(result.errorMessageAr, contains('العلامات'));
    });
  });

  // ===========================================================================
  // Email Validation
  // ===========================================================================

  group('Validators.email', () {
    test('valid email addresses', () {
      final validEmails = [
        'user@example.com',
        'test.user@domain.org',
        'a@b.co',
        'user+tag@example.com',
        'user@sub.domain.com',
      ];
      for (final email in validEmails) {
        expect(Validators.email(email).isValid, isTrue, reason: 'Expected $email to be valid');
      }
    });

    test('invalid email addresses', () {
      final invalidEmails = [
        'not-an-email',
        '@domain.com',
        'user@',
        'user@.com',
        'user@domain',
      ];
      for (final email in invalidEmails) {
        expect(Validators.email(email).isValid, isFalse, reason: 'Expected $email to be invalid');
      }
    });

    test('rejects email with consecutive dots', () {
      expect(Validators.email('user..name@domain.com').isValid, isFalse);
    });

    test('rejects email longer than 254 characters', () {
      final longLocal = 'a' * 240;
      final longEmail = '$longLocal@example.com';
      expect(Validators.email(longEmail).isValid, isFalse);
    });

    test('rejects email with single-char TLD', () {
      expect(Validators.email('user@domain.a').isValid, isFalse);
    });

    test('required email returns error for null', () {
      final result = Validators.email(null);
      expect(result.isValid, isFalse);
      expect(result.errorMessageAr, isNotNull);
    });

    test('required email returns error for empty string', () {
      expect(Validators.email('').isValid, isFalse);
    });

    test('optional email allows null', () {
      expect(Validators.email(null, isRequired: false).isValid, isTrue);
    });

    test('optional email allows empty string', () {
      expect(Validators.email('', isRequired: false).isValid, isTrue);
    });

    test('optional email still validates format if provided', () {
      expect(Validators.email('bad-email', isRequired: false).isValid, isFalse);
    });
  });

  // ===========================================================================
  // Phone Validation - Saudi
  // ===========================================================================

  group('Validators.saudiPhone', () {
    test('valid Saudi phone numbers', () {
      final validNumbers = [
        '0512345678',
        '0551234567',
        '0591234567',
        '+966512345678',
        '966512345678',
        '00966512345678',
      ];
      for (final number in validNumbers) {
        expect(
          Validators.saudiPhone(number).isValid,
          isTrue,
          reason: 'Expected $number to be valid',
        );
      }
    });

    test('accepts numbers with spaces and dashes', () {
      expect(Validators.saudiPhone('05 1234 5678').isValid, isTrue);
      expect(Validators.saudiPhone('05-1234-5678').isValid, isTrue);
      expect(Validators.saudiPhone('+966 51 234 5678').isValid, isTrue);
    });

    test('rejects non-05 prefix', () {
      expect(Validators.saudiPhone('0612345678').isValid, isFalse);
      expect(Validators.saudiPhone('0412345678').isValid, isFalse);
    });

    test('rejects wrong digit count', () {
      expect(Validators.saudiPhone('051234567').isValid, isFalse); // 9 digits
      expect(Validators.saudiPhone('05123456789').isValid, isFalse); // 11 digits
    });

    test('rejects letters in number', () {
      expect(Validators.saudiPhone('05abc12345').isValid, isFalse);
    });

    test('required returns error for null', () {
      expect(Validators.saudiPhone(null).isValid, isFalse);
    });

    test('optional allows null', () {
      expect(Validators.saudiPhone(null, isRequired: false).isValid, isTrue);
    });
  });

  // ===========================================================================
  // Phone Validation - Yemen
  // ===========================================================================

  group('Validators.yemenPhone', () {
    test('valid Yemen phone numbers', () {
      final validNumbers = [
        '712345678',
        '771234567',
        '733123456',
        '+967712345678',
        '967712345678',
        '00967712345678',
      ];
      for (final number in validNumbers) {
        expect(
          Validators.yemenPhone(number).isValid,
          isTrue,
          reason: 'Expected $number to be valid',
        );
      }
    });

    test('accepts numbers with spaces and dashes', () {
      expect(Validators.yemenPhone('7 1234 5678').isValid, isTrue);
      expect(Validators.yemenPhone('+967 71 234 5678').isValid, isTrue);
    });

    test('rejects non-7 prefix', () {
      expect(Validators.yemenPhone('612345678').isValid, isFalse);
      expect(Validators.yemenPhone('812345678').isValid, isFalse);
    });

    test('rejects wrong digit count', () {
      expect(Validators.yemenPhone('71234567').isValid, isFalse); // 8 digits
      expect(Validators.yemenPhone('7123456789').isValid, isFalse); // 10 digits
    });

    test('required returns error for null', () {
      expect(Validators.yemenPhone(null).isValid, isFalse);
    });

    test('optional allows null', () {
      expect(Validators.yemenPhone(null, isRequired: false).isValid, isTrue);
    });
  });

  // ===========================================================================
  // Phone Validation - International & Dispatch
  // ===========================================================================

  group('Validators.internationalPhone', () {
    test('valid international numbers', () {
      expect(Validators.internationalPhone('+14155552671').isValid, isTrue);
      expect(Validators.internationalPhone('442071234567').isValid, isTrue);
      expect(Validators.internationalPhone('1234567').isValid, isTrue);
    });

    test('rejects too few digits', () {
      expect(Validators.internationalPhone('123456').isValid, isFalse);
    });

    test('rejects too many digits', () {
      final tooLong = '1' * 16;
      expect(Validators.internationalPhone(tooLong).isValid, isFalse);
    });

    test('rejects alphabetic characters', () {
      expect(Validators.internationalPhone('+1abc4567890').isValid, isFalse);
    });

    test('optional allows empty', () {
      expect(Validators.internationalPhone(null, isRequired: false).isValid, isTrue);
      expect(Validators.internationalPhone('', isRequired: false).isValid, isTrue);
    });
  });

  group('Validators.phone (dispatch)', () {
    test('dispatches to saudiPhone for +966', () {
      final result = Validators.phone('0512345678', countryCode: '+966');
      expect(result.isValid, isTrue);
    });

    test('dispatches to yemenPhone for +967', () {
      final result = Validators.phone('712345678', countryCode: '+967');
      expect(result.isValid, isTrue);
    });

    test('dispatches to internationalPhone for other codes', () {
      final result = Validators.phone('+14155552671', countryCode: '+1');
      expect(result.isValid, isTrue);
    });

    test('defaults to Saudi validation', () {
      final result = Validators.phone('0512345678');
      expect(result.isValid, isTrue);
    });
  });

  // ===========================================================================
  // Arabic Text Validation
  // ===========================================================================

  group('Validators.arabicText', () {
    test('accepts Arabic text', () {
      expect(Validators.arabicText('مرحبا بالعالم').isValid, isTrue);
    });

    test('accepts mixed Arabic and English when allowEnglish is true', () {
      expect(Validators.arabicText('حقل Field-1', allowEnglish: true).isValid, isTrue);
    });

    test('rejects pure English when allowEnglish is false', () {
      expect(Validators.arabicText('Hello', allowEnglish: false).isValid, isFalse);
    });

    test('enforces minLength', () {
      expect(Validators.arabicText('ا', minLength: 5).isValid, isFalse);
    });

    test('enforces maxLength', () {
      final longText = 'ا' * 1001;
      expect(Validators.arabicText(longText, maxLength: 1000).isValid, isFalse);
    });

    test('required returns error for null', () {
      expect(Validators.arabicText(null).isValid, isFalse);
    });

    test('optional allows null', () {
      expect(Validators.arabicText(null, isRequired: false).isValid, isTrue);
    });

    test('rejects dangerous content (script injection)', () {
      expect(Validators.arabicText('<script>alert("xss")</script>').isValid, isFalse);
    });

    test('rejects javascript: protocol', () {
      expect(Validators.arabicText('javascript:alert(1)').isValid, isFalse);
    });
  });

  // ===========================================================================
  // General Text Validation
  // ===========================================================================

  group('Validators.text', () {
    test('accepts normal text', () {
      expect(Validators.text('Hello world').isValid, isTrue);
    });

    test('enforces minLength', () {
      expect(Validators.text('Hi', minLength: 5).isValid, isFalse);
    });

    test('enforces maxLength', () {
      final longText = 'a' * 1001;
      expect(Validators.text(longText, maxLength: 1000).isValid, isFalse);
    });

    test('required returns error for empty', () {
      expect(Validators.text('').isValid, isFalse);
    });

    test('optional allows empty', () {
      expect(Validators.text('', isRequired: false).isValid, isTrue);
    });

    test('uses custom field name in errors', () {
      final result = Validators.text(null, fieldName: 'Description', fieldNameAr: 'الوصف');
      expect(result.errorMessage, contains('Description'));
      expect(result.errorMessageAr, contains('الوصف'));
    });

    test('rejects dangerous HTML content', () {
      expect(Validators.text('<iframe src="evil">').isValid, isFalse);
      expect(Validators.text('eval(code)').isValid, isFalse);
      expect(Validators.text('document.cookie').isValid, isFalse);
    });
  });

  // ===========================================================================
  // Field Name Validation
  // ===========================================================================

  group('Validators.fieldName', () {
    test('accepts valid field names', () {
      expect(Validators.fieldName('Field 1').isValid, isTrue);
      expect(Validators.fieldName('حقل-القمح').isValid, isTrue);
      expect(Validators.fieldName('North_Field_A').isValid, isTrue);
    });

    test('rejects names shorter than minLength', () {
      expect(Validators.fieldName('A').isValid, isFalse);
    });

    test('rejects names longer than maxLength', () {
      final longName = 'a' * 101;
      expect(Validators.fieldName(longName, maxLength: 100).isValid, isFalse);
    });

    test('rejects special characters', () {
      expect(Validators.fieldName('Field@#!').isValid, isFalse);
      expect(Validators.fieldName('Field<script>').isValid, isFalse);
    });

    test('required returns error for null', () {
      final result = Validators.fieldName(null);
      expect(result.isValid, isFalse);
      expect(result.errorMessageAr, isNotNull);
    });

    test('optional allows null', () {
      expect(Validators.fieldName(null, isRequired: false).isValid, isTrue);
    });
  });

  // ===========================================================================
  // Password Validation
  // ===========================================================================

  group('Validators.password', () {
    test('accepts strong password', () {
      expect(Validators.password('SecureP4ss').isValid, isTrue);
    });

    test('rejects too short password', () {
      expect(Validators.password('Ab1').isValid, isFalse);
    });

    test('rejects too long password', () {
      final longPass = 'Aa1${'a' * 130}';
      expect(Validators.password(longPass).isValid, isFalse);
    });

    test('rejects password without uppercase when required', () {
      expect(
        Validators.password('nouppercase1', requireUppercase: true).isValid,
        isFalse,
      );
    });

    test('rejects password without lowercase when required', () {
      expect(
        Validators.password('NOLOWERCASE1', requireLowercase: true).isValid,
        isFalse,
      );
    });

    test('rejects password without number when required', () {
      expect(
        Validators.password('NoNumberHere', requireNumber: true).isValid,
        isFalse,
      );
    });

    test('rejects password without special char when required', () {
      expect(
        Validators.password('NoSpecial1', requireSpecialChar: true).isValid,
        isFalse,
      );
    });

    test('accepts password with special char when required', () {
      expect(
        Validators.password('Secure1!', requireSpecialChar: true).isValid,
        isTrue,
      );
    });

    test('required returns error for null', () {
      expect(Validators.password(null).isValid, isFalse);
    });

    test('optional allows null', () {
      expect(Validators.password(null, isRequired: false).isValid, isTrue);
    });

    test('respects custom minLength', () {
      expect(Validators.password('Ab1', minLength: 3).isValid, isTrue);
      expect(Validators.password('Ab', minLength: 3).isValid, isFalse);
    });
  });

  group('Validators.passwordMatch', () {
    test('matching passwords succeed', () {
      expect(Validators.passwordMatch('abc123', 'abc123').isValid, isTrue);
    });

    test('mismatched passwords fail', () {
      expect(Validators.passwordMatch('abc123', 'xyz789').isValid, isFalse);
    });

    test('null confirm password fails', () {
      expect(Validators.passwordMatch('abc123', null).isValid, isFalse);
    });

    test('empty confirm password fails', () {
      expect(Validators.passwordMatch('abc123', '').isValid, isFalse);
    });

    test('null password when required fails', () {
      expect(Validators.passwordMatch(null, 'abc123').isValid, isFalse);
    });

    test('null password when optional succeeds', () {
      expect(Validators.passwordMatch(null, null, isRequired: false).isValid, isTrue);
    });
  });

  // ===========================================================================
  // Username Validation
  // ===========================================================================

  group('Validators.username', () {
    test('accepts valid usernames', () {
      expect(Validators.username('farmer_ali').isValid, isTrue);
      expect(Validators.username('admin').isValid, isTrue);
    });

    test('accepts Arabic usernames when allowed', () {
      expect(Validators.username('مزارع_علي', allowArabic: true).isValid, isTrue);
    });

    test('rejects Arabic usernames when disallowed', () {
      expect(Validators.username('مزارع', allowArabic: false).isValid, isFalse);
    });

    test('rejects too short username', () {
      expect(Validators.username('ab').isValid, isFalse);
    });

    test('rejects too long username', () {
      final long = 'a' * 31;
      expect(Validators.username(long).isValid, isFalse);
    });

    test('rejects username starting with number', () {
      expect(Validators.username('1farmer').isValid, isFalse);
    });

    test('rejects special characters other than underscore', () {
      expect(Validators.username('user@name').isValid, isFalse);
      expect(Validators.username('user-name').isValid, isFalse);
      expect(Validators.username('user name').isValid, isFalse);
    });

    test('required returns error for null', () {
      expect(Validators.username(null).isValid, isFalse);
    });

    test('optional allows null', () {
      expect(Validators.username(null, isRequired: false).isValid, isTrue);
    });
  });

  // ===========================================================================
  // FieldValidators (agricultural-specific)
  // ===========================================================================

  group('FieldValidators', () {
    late FieldValidators fv;

    setUp(() {
      fv = FieldValidators();
    });

    group('validateArea', () {
      test('accepts valid area', () {
        expect(fv.validateArea(5.0).isValid, isTrue);
        expect(fv.validateArea(0.1).isValid, isTrue);
        expect(fv.validateArea(10000).isValid, isTrue);
      });

      test('rejects null', () {
        expect(fv.validateArea(null).isValid, isFalse);
      });

      test('rejects zero', () {
        expect(fv.validateArea(0).isValid, isFalse);
      });

      test('rejects negative', () {
        expect(fv.validateArea(-1).isValid, isFalse);
      });

      test('rejects area exceeding 10000 hectares', () {
        expect(fv.validateArea(10001).isValid, isFalse);
      });
    });

    group('validateNdvi', () {
      test('accepts valid NDVI values', () {
        expect(fv.validateNdvi(0.0).isValid, isTrue);
        expect(fv.validateNdvi(0.5).isValid, isTrue);
        expect(fv.validateNdvi(1.0).isValid, isTrue);
      });

      test('null is optional (returns success)', () {
        expect(fv.validateNdvi(null).isValid, isTrue);
      });

      test('rejects values below 0', () {
        expect(fv.validateNdvi(-0.1).isValid, isFalse);
      });

      test('rejects values above 1', () {
        expect(fv.validateNdvi(1.1).isValid, isFalse);
      });
    });

    group('validateName', () {
      test('delegates to Validators.fieldName', () {
        expect(fv.validateName('North Field').isValid, isTrue);
        expect(fv.validateName(null).isValid, isFalse);
        expect(fv.validateName('A').isValid, isFalse);
      });
    });

    group('validateCropType', () {
      test('accepts non-empty crop type', () {
        expect(fv.validateCropType('wheat').isValid, isTrue);
        expect(fv.validateCropType('قمح').isValid, isTrue);
      });

      test('rejects null', () {
        expect(fv.validateCropType(null).isValid, isFalse);
      });

      test('rejects empty string', () {
        expect(fv.validateCropType('').isValid, isFalse);
      });

      test('rejects whitespace only', () {
        expect(fv.validateCropType('   ').isValid, isFalse);
      });
    });
  });

  // ===========================================================================
  // XSS / Security
  // ===========================================================================

  group('XSS prevention', () {
    test('rejects script tags in text fields', () {
      expect(Validators.text('<script>alert(1)</script>').isValid, isFalse);
      expect(Validators.fieldName('<script>x</script>').isValid, isFalse);
    });

    test('rejects iframe injection', () {
      expect(Validators.text('<iframe src="evil.com">').isValid, isFalse);
    });

    test('rejects event handler injection', () {
      expect(Validators.text('onload=alert(1)').isValid, isFalse);
    });

    test('rejects eval calls', () {
      expect(Validators.text('eval(code)').isValid, isFalse);
    });

    test('rejects document access', () {
      expect(Validators.text('document.cookie').isValid, isFalse);
    });

    test('rejects window access', () {
      expect(Validators.text('window.location').isValid, isFalse);
    });
  });
}
