/// Form Validators - Flutter Form Integration
/// مدققات النماذج - تكامل مع نماذج Flutter
///
/// Provides form field validators that integrate with Flutter's Form widget.
/// Returns String? for use with TextFormField validator parameter.
///
/// Example usage:
/// ```dart
/// TextFormField(
///   validator: FormValidators.required(fieldName: 'Email'),
/// )
/// ```
library;

import 'validators.dart';
import 'coordinate_validator.dart';
import 'measurement_validator.dart';

/// Callback type for form field validation
typedef FormFieldValidator<T> = String? Function(T? value);

/// Form validators for Flutter Form integration
/// Returns String? for TextFormField validator parameter
class FormValidators {
  /// Private constructor to prevent instantiation
  const FormValidators._();

  /// Default locale for error messages (true = Arabic)
  static bool _useArabic = true;

  /// Set the default locale for error messages
  static void setLocale({required bool arabic}) {
    _useArabic = arabic;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Required Field Validators
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate required text field
  static FormFieldValidator<String> required({
    String fieldName = 'Field',
    String fieldNameAr = 'الحقل',
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.required(
        value,
        fieldName: fieldName,
        fieldNameAr: fieldNameAr,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate required selection (dropdown)
  static FormFieldValidator<T> requiredSelection<T>({
    String fieldName = 'Selection',
    String fieldNameAr = 'الاختيار',
    bool? arabic,
  }) {
    return (T? value) {
      final result = Validators.requiredValue(
        value,
        fieldName: fieldName,
        fieldNameAr: fieldNameAr,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Email Validators
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate email field
  static FormFieldValidator<String> email({
    bool isRequired = true,
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.email(value, isRequired: isRequired);
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Phone Validators
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate Saudi phone number
  static FormFieldValidator<String> saudiPhone({
    bool isRequired = true,
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.saudiPhone(value, isRequired: isRequired);
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate Yemen phone number
  static FormFieldValidator<String> yemenPhone({
    bool isRequired = true,
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.yemenPhone(value, isRequired: isRequired);
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate phone number for specified country
  static FormFieldValidator<String> phone({
    String countryCode = '+966',
    bool isRequired = true,
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.phone(
        value,
        countryCode: countryCode,
        isRequired: isRequired,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate international phone number
  static FormFieldValidator<String> internationalPhone({
    bool isRequired = true,
    int minDigits = 7,
    int maxDigits = 15,
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.internationalPhone(
        value,
        isRequired: isRequired,
        minDigits: minDigits,
        maxDigits: maxDigits,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Text Validators
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate text field with length constraints
  static FormFieldValidator<String> text({
    bool isRequired = true,
    int minLength = 1,
    int maxLength = 1000,
    bool allowSpecialChars = true,
    String fieldName = 'Text',
    String fieldNameAr = 'النص',
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.text(
        value,
        isRequired: isRequired,
        minLength: minLength,
        maxLength: maxLength,
        allowSpecialChars: allowSpecialChars,
        fieldName: fieldName,
        fieldNameAr: fieldNameAr,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate Arabic text field
  static FormFieldValidator<String> arabicText({
    bool isRequired = true,
    bool allowEnglish = true,
    int minLength = 1,
    int maxLength = 1000,
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.arabicText(
        value,
        isRequired: isRequired,
        allowEnglish: allowEnglish,
        minLength: minLength,
        maxLength: maxLength,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate field name
  static FormFieldValidator<String> fieldName({
    bool isRequired = true,
    int minLength = 2,
    int maxLength = 100,
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.fieldName(
        value,
        isRequired: isRequired,
        minLength: minLength,
        maxLength: maxLength,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate username
  static FormFieldValidator<String> username({
    bool isRequired = true,
    int minLength = 3,
    int maxLength = 30,
    bool allowArabic = true,
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.username(
        value,
        isRequired: isRequired,
        minLength: minLength,
        maxLength: maxLength,
        allowArabic: allowArabic,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Password Validators
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate password field
  static FormFieldValidator<String> password({
    bool isRequired = true,
    int minLength = 8,
    bool requireUppercase = true,
    bool requireLowercase = true,
    bool requireNumber = true,
    bool requireSpecialChar = false,
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.password(
        value,
        isRequired: isRequired,
        minLength: minLength,
        requireUppercase: requireUppercase,
        requireLowercase: requireLowercase,
        requireNumber: requireNumber,
        requireSpecialChar: requireSpecialChar,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Create password confirmation validator
  static FormFieldValidator<String> passwordConfirmation(
    String? Function() getPassword, {
    bool? arabic,
  }) {
    return (String? value) {
      final result = Validators.passwordMatch(
        getPassword(),
        value,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Coordinate Validators
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate latitude value
  static FormFieldValidator<String> latitude({
    bool isRequired = true,
    bool? arabic,
  }) {
    return (String? value) {
      if (value == null || value.trim().isEmpty) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? 'خط العرض مطلوب'
              : 'Latitude is required';
        }
        return null;
      }

      final parsed = double.tryParse(value.trim());
      if (parsed == null) {
        return (arabic ?? _useArabic)
            ? 'يجب أن يكون رقم صحيح'
            : 'Must be a valid number';
      }

      final result = CoordinateValidator.latitude(parsed);
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate longitude value
  static FormFieldValidator<String> longitude({
    bool isRequired = true,
    bool? arabic,
  }) {
    return (String? value) {
      if (value == null || value.trim().isEmpty) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? 'خط الطول مطلوب'
              : 'Longitude is required';
        }
        return null;
      }

      final parsed = double.tryParse(value.trim());
      if (parsed == null) {
        return (arabic ?? _useArabic)
            ? 'يجب أن يكون رقم صحيح'
            : 'Must be a valid number';
      }

      final result = CoordinateValidator.longitude(parsed);
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate coordinates for Saudi Arabia region
  static FormFieldValidator<String> saudiLatitude({
    bool isRequired = true,
    bool? arabic,
  }) {
    return (String? value) {
      if (value == null || value.trim().isEmpty) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? 'خط العرض مطلوب'
              : 'Latitude is required';
        }
        return null;
      }

      final parsed = double.tryParse(value.trim());
      if (parsed == null) {
        return (arabic ?? _useArabic)
            ? 'يجب أن يكون رقم صحيح'
            : 'Must be a valid number';
      }

      final result = CoordinateValidator.saudiLatitude(parsed);
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate coordinates for Saudi Arabia region
  static FormFieldValidator<String> saudiLongitude({
    bool isRequired = true,
    bool? arabic,
  }) {
    return (String? value) {
      if (value == null || value.trim().isEmpty) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? 'خط الطول مطلوب'
              : 'Longitude is required';
        }
        return null;
      }

      final parsed = double.tryParse(value.trim());
      if (parsed == null) {
        return (arabic ?? _useArabic)
            ? 'يجب أن يكون رقم صحيح'
            : 'Must be a valid number';
      }

      final result = CoordinateValidator.saudiLongitude(parsed);
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Measurement Validators
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate area in hectares (string input)
  static FormFieldValidator<String> areaHectares({
    bool isRequired = true,
    double minArea = 0.01,
    double maxArea = 10000,
    bool? arabic,
  }) {
    return (String? value) {
      if (value == null || value.trim().isEmpty) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? 'المساحة مطلوبة'
              : 'Area is required';
        }
        return null;
      }

      final parsed = double.tryParse(value.trim());
      if (parsed == null) {
        return (arabic ?? _useArabic)
            ? 'يجب أن تكون قيمة رقمية'
            : 'Must be a valid number';
      }

      final result = MeasurementValidator.areaHectares(
        parsed,
        minArea: minArea,
        maxArea: maxArea,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate temperature in Celsius (string input)
  static FormFieldValidator<String> temperatureCelsius({
    bool isRequired = true,
    double minTemp = -50,
    double maxTemp = 60,
    bool? arabic,
  }) {
    return (String? value) {
      if (value == null || value.trim().isEmpty) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? 'درجة الحرارة مطلوبة'
              : 'Temperature is required';
        }
        return null;
      }

      final parsed = double.tryParse(value.trim());
      if (parsed == null) {
        return (arabic ?? _useArabic)
            ? 'يجب أن تكون قيمة رقمية'
            : 'Must be a valid number';
      }

      final result = MeasurementValidator.temperatureCelsius(
        parsed,
        minTemp: minTemp,
        maxTemp: maxTemp,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate percentage value (string input)
  static FormFieldValidator<String> percentage({
    bool isRequired = true,
    double minValue = 0,
    double maxValue = 100,
    String fieldName = 'Value',
    String fieldNameAr = 'القيمة',
    bool? arabic,
  }) {
    return (String? value) {
      if (value == null || value.trim().isEmpty) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? '$fieldNameAr مطلوب'
              : '$fieldName is required';
        }
        return null;
      }

      final parsed = double.tryParse(value.trim().replaceAll('%', ''));
      if (parsed == null) {
        return (arabic ?? _useArabic)
            ? 'يجب أن تكون قيمة رقمية'
            : 'Must be a valid number';
      }

      final result = MeasurementValidator.percentage(
        parsed,
        minValue: minValue,
        maxValue: maxValue,
        fieldName: fieldName,
        fieldNameAr: fieldNameAr,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Date Validators
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate date is not in the future
  static FormFieldValidator<DateTime> dateNotFuture({
    bool isRequired = true,
    String fieldName = 'Date',
    String fieldNameAr = 'التاريخ',
    bool? arabic,
  }) {
    return (DateTime? value) {
      if (value == null) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? '$fieldNameAr مطلوب'
              : '$fieldName is required';
        }
        return null;
      }

      final result = MeasurementValidator.dateNotFuture(
        value,
        fieldName: fieldName,
        fieldNameAr: fieldNameAr,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate date is not in the past
  static FormFieldValidator<DateTime> dateNotPast({
    bool isRequired = true,
    String fieldName = 'Date',
    String fieldNameAr = 'التاريخ',
    bool? arabic,
  }) {
    return (DateTime? value) {
      if (value == null) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? '$fieldNameAr مطلوب'
              : '$fieldName is required';
        }
        return null;
      }

      final result = MeasurementValidator.dateNotPast(
        value,
        fieldName: fieldName,
        fieldNameAr: fieldNameAr,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate date is within a range
  static FormFieldValidator<DateTime> dateInRange({
    required DateTime minDate,
    required DateTime maxDate,
    bool isRequired = true,
    String fieldName = 'Date',
    String fieldNameAr = 'التاريخ',
    bool? arabic,
  }) {
    return (DateTime? value) {
      if (value == null) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? '$fieldNameAr مطلوب'
              : '$fieldName is required';
        }
        return null;
      }

      final result = MeasurementValidator.dateRange(
        value,
        minDate: minDate,
        maxDate: maxDate,
        fieldName: fieldName,
        fieldNameAr: fieldNameAr,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Numeric Validators
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate numeric value (string input) with min/max range
  static FormFieldValidator<String> numericRange({
    bool isRequired = true,
    double? minValue,
    double? maxValue,
    String fieldName = 'Value',
    String fieldNameAr = 'القيمة',
    String? unit,
    String? unitAr,
    bool? arabic,
  }) {
    return (String? value) {
      if (value == null || value.trim().isEmpty) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? '$fieldNameAr مطلوب'
              : '$fieldName is required';
        }
        return null;
      }

      final parsed = double.tryParse(value.trim());
      if (parsed == null) {
        return (arabic ?? _useArabic)
            ? 'يجب أن تكون قيمة رقمية'
            : 'Must be a valid number';
      }

      final result = MeasurementValidator.numericRange(
        parsed,
        minValue: minValue,
        maxValue: maxValue,
        fieldName: fieldName,
        fieldNameAr: fieldNameAr,
        unit: unit,
        unitAr: unitAr,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  /// Validate positive number (string input)
  static FormFieldValidator<String> positiveNumber({
    bool isRequired = true,
    bool allowZero = false,
    String fieldName = 'Value',
    String fieldNameAr = 'القيمة',
    bool? arabic,
  }) {
    return (String? value) {
      if (value == null || value.trim().isEmpty) {
        if (isRequired) {
          return (arabic ?? _useArabic)
              ? '$fieldNameAr مطلوب'
              : '$fieldName is required';
        }
        return null;
      }

      final parsed = double.tryParse(value.trim());
      if (parsed == null) {
        return (arabic ?? _useArabic)
            ? 'يجب أن تكون قيمة رقمية'
            : 'Must be a valid number';
      }

      final result = MeasurementValidator.positiveNumber(
        parsed,
        allowZero: allowZero,
        fieldName: fieldName,
        fieldNameAr: fieldNameAr,
      );
      return result.getMessage(arabic: arabic ?? _useArabic);
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Composite Validators
  // ─────────────────────────────────────────────────────────────────────────────

  /// Combine multiple validators (returns first error found)
  static FormFieldValidator<T> combine<T>(
    List<FormFieldValidator<T>> validators,
  ) {
    return (T? value) {
      for (final validator in validators) {
        final error = validator(value);
        if (error != null) {
          return error;
        }
      }
      return null;
    };
  }

  /// Validate only if condition is true
  static FormFieldValidator<T> conditional<T>(
    bool Function() condition,
    FormFieldValidator<T> validator,
  ) {
    return (T? value) {
      if (condition()) {
        return validator(value);
      }
      return null;
    };
  }
}
