/**
 * Custom Validation Decorators
 * مزخرفات التحقق المخصصة
 *
 * @module shared/validation
 * @description Custom validation decorators for SAHOOL platform-specific needs
 */

import {
  registerDecorator,
  ValidationOptions,
  ValidationArguments,
  ValidatorConstraint,
  ValidatorConstraintInterface,
  isLatitude,
  isLongitude,
} from "class-validator";

// ═══════════════════════════════════════════════════════════════════════════
// Yemen-Specific Validators
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Validates Yemen phone numbers
 * Formats: +967XXXXXXXX, 967XXXXXXXX, 00967XXXXXXXX, 7XXXXXXXX, 77XXXXXXXX, 78XXXXXXXX
 */
@ValidatorConstraint({ name: "isYemeniPhone", async: false })
export class IsYemeniPhoneConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "string") {
      return false;
    }

    // Yemen phone number patterns
    const patterns = [
      /^(\+967|967|00967)(7[0-9]{8})$/, // International format
      /^(7[0-9]{8})$/, // Local format (9 digits starting with 7)
      /^(77|78)[0-9]{7}$/, // Common mobile prefixes
    ];

    return patterns.some((pattern) => pattern.test(value.replace(/\s/g, "")));
  }

  defaultMessage(args: ValidationArguments) {
    return "Phone number must be a valid Yemeni phone number (e.g., +967712345678 or 712345678)";
  }
}

export function IsYemeniPhone(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsYemeniPhoneConstraint,
    });
  };
}

/**
 * Validates coordinates are within Yemen boundaries
 * Yemen bounds: 12-19°N, 42-54°E
 */
@ValidatorConstraint({ name: "isWithinYemen", async: false })
export class IsWithinYemenConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    const object = args.object as any;
    const [latField, lngField] = args.constraints;

    const lat = latField ? object[latField] : value.lat || value.latitude;
    const lng = lngField ? object[lngField] : value.lng || value.longitude;

    if (!isLatitude(lat) || !isLongitude(lng)) {
      return false;
    }

    // Yemen geographical bounds
    const YEMEN_BOUNDS = {
      minLat: 12.0,
      maxLat: 19.0,
      minLng: 42.0,
      maxLng: 54.0,
    };

    return (
      lat >= YEMEN_BOUNDS.minLat &&
      lat <= YEMEN_BOUNDS.maxLat &&
      lng >= YEMEN_BOUNDS.minLng &&
      lng <= YEMEN_BOUNDS.maxLng
    );
  }

  defaultMessage(args: ValidationArguments) {
    return "Coordinates must be within Yemen boundaries (12-19°N, 42-54°E)";
  }
}

export function IsWithinYemen(
  latField?: string,
  lngField?: string,
  validationOptions?: ValidationOptions,
) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [latField, lngField],
      validator: IsWithinYemenConstraint,
    });
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Arabic Text Validators
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Validates that text contains Arabic characters
 */
@ValidatorConstraint({ name: "containsArabic", async: false })
export class ContainsArabicConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "string") {
      return false;
    }

    // Arabic Unicode range: \u0600-\u06FF
    const arabicPattern = /[\u0600-\u06FF]/;
    return arabicPattern.test(value);
  }

  defaultMessage(args: ValidationArguments) {
    return "Text must contain Arabic characters";
  }
}

export function ContainsArabic(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: ContainsArabicConstraint,
    });
  };
}

/**
 * Validates that text is only Arabic characters (with spaces and common punctuation)
 */
@ValidatorConstraint({ name: "isArabicOnly", async: false })
export class IsArabicOnlyConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "string") {
      return false;
    }

    // Arabic characters, spaces, and common punctuation
    const arabicOnlyPattern = /^[\u0600-\u06FF\s.,،؛؟!]+$/;
    return arabicOnlyPattern.test(value);
  }

  defaultMessage(args: ValidationArguments) {
    return "Text must contain only Arabic characters";
  }
}

export function IsArabicOnly(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsArabicOnlyConstraint,
    });
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Business Logic Validators
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Validates that end date is after start date
 */
@ValidatorConstraint({ name: "isAfterDate", async: false })
export class IsAfterDateConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    const [relatedPropertyName] = args.constraints;
    const relatedValue = (args.object as any)[relatedPropertyName];

    if (!value || !relatedValue) {
      return true; // Skip validation if either date is missing
    }

    const endDate = new Date(value);
    const startDate = new Date(relatedValue);

    return endDate > startDate;
  }

  defaultMessage(args: ValidationArguments) {
    const [relatedPropertyName] = args.constraints;
    return `${args.property} must be after ${relatedPropertyName}`;
  }
}

export function IsAfterDate(
  property: string,
  validationOptions?: ValidationOptions,
) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [property],
      validator: IsAfterDateConstraint,
    });
  };
}

/**
 * Validates that a date is in the future
 */
@ValidatorConstraint({ name: "isFutureDate", async: false })
export class IsFutureDateConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (!value) {
      return true; // Skip validation if date is missing
    }

    const date = new Date(value);
    const now = new Date();

    return date > now;
  }

  defaultMessage(args: ValidationArguments) {
    return `${args.property} must be a future date`;
  }
}

export function IsFutureDate(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsFutureDateConstraint,
    });
  };
}

/**
 * Validates password complexity
 * Requirements: min length, uppercase, lowercase, number, special character
 */
@ValidatorConstraint({ name: "isStrongPassword", async: false })
export class IsStrongPasswordConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "string") {
      return false;
    }

    const minLength = args.constraints[0] || 8;

    // Check minimum length
    if (value.length < minLength) {
      return false;
    }

    // Check for uppercase letter
    if (!/[A-Z]/.test(value)) {
      return false;
    }

    // Check for lowercase letter
    if (!/[a-z]/.test(value)) {
      return false;
    }

    // Check for number
    if (!/[0-9]/.test(value)) {
      return false;
    }

    // Check for special character
    if (!/[@$!%*?&#^()_+\-=[\]{};:'",.<>/?\\|`~]/.test(value)) {
      return false;
    }

    return true;
  }

  defaultMessage(args: ValidationArguments) {
    const minLength = args.constraints[0] || 8;
    return `Password must be at least ${minLength} characters and contain uppercase, lowercase, number, and special character`;
  }
}

export function IsStrongPassword(
  minLength: number = 8,
  validationOptions?: ValidationOptions,
) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [minLength],
      validator: IsStrongPasswordConstraint,
    });
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Geospatial Validators
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Validates GeoJSON Polygon
 */
@ValidatorConstraint({ name: "isGeoJSONPolygon", async: false })
export class IsGeoJSONPolygonConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (!value || typeof value !== "object") {
      return false;
    }

    // Check basic GeoJSON structure
    if (value.type !== "Polygon") {
      return false;
    }

    if (!Array.isArray(value.coordinates) || value.coordinates.length === 0) {
      return false;
    }

    // Check outer ring
    const outerRing = value.coordinates[0];
    if (!Array.isArray(outerRing) || outerRing.length < 4) {
      return false;
    }

    // Check that polygon is closed (first point equals last point)
    const firstPoint = outerRing[0];
    const lastPoint = outerRing[outerRing.length - 1];
    if (
      !Array.isArray(firstPoint) ||
      !Array.isArray(lastPoint) ||
      firstPoint[0] !== lastPoint[0] ||
      firstPoint[1] !== lastPoint[1]
    ) {
      return false;
    }

    // Validate all coordinates are valid longitude/latitude pairs
    for (const ring of value.coordinates) {
      for (const [lng, lat] of ring) {
        if (!isLongitude(lng) || !isLatitude(lat)) {
          return false;
        }
      }
    }

    return true;
  }

  defaultMessage(args: ValidationArguments) {
    return "Must be a valid GeoJSON Polygon with at least 4 points and closed ring";
  }
}

export function IsGeoJSONPolygon(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsGeoJSONPolygonConstraint,
    });
  };
}

/**
 * Validates minimum field area in hectares
 */
@ValidatorConstraint({ name: "isValidFieldArea", async: false })
export class IsValidFieldAreaConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "number") {
      return false;
    }

    const minArea = args.constraints[0] || 0.01; // Minimum 100 sq meters (0.01 hectares)
    const maxArea = args.constraints[1] || 10000; // Maximum 10,000 hectares

    return value >= minArea && value <= maxArea;
  }

  defaultMessage(args: ValidationArguments) {
    const minArea = args.constraints[0] || 0.01;
    const maxArea = args.constraints[1] || 10000;
    return `Field area must be between ${minArea} and ${maxArea} hectares`;
  }
}

export function IsValidFieldArea(
  minArea: number = 0.01,
  maxArea: number = 10000,
  validationOptions?: ValidationOptions,
) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [minArea, maxArea],
      validator: IsValidFieldAreaConstraint,
    });
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Financial Validators
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Validates decimal precision for monetary values
 */
@ValidatorConstraint({ name: "isMoneyValue", async: false })
export class IsMoneyValueConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "number") {
      return false;
    }

    // Check if value is negative
    if (value < 0) {
      return false;
    }

    // Check decimal precision (max 2 decimal places)
    const decimalPlaces = (value.toString().split(".")[1] || "").length;
    if (decimalPlaces > 2) {
      return false;
    }

    return true;
  }

  defaultMessage(args: ValidationArguments) {
    return "Amount must be a positive number with maximum 2 decimal places";
  }
}

export function IsMoneyValue(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsMoneyValueConstraint,
    });
  };
}

/**
 * Validates credit card number using Luhn algorithm
 */
@ValidatorConstraint({ name: "isCreditCard", async: false })
export class IsCreditCardConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "string") {
      return false;
    }

    // Remove spaces and dashes
    const cardNumber = value.replace(/[\s-]/g, "");

    // Check if it's all digits
    if (!/^\d+$/.test(cardNumber)) {
      return false;
    }

    // Check length (13-19 digits)
    if (cardNumber.length < 13 || cardNumber.length > 19) {
      return false;
    }

    // Luhn algorithm
    let sum = 0;
    let isEven = false;

    for (let i = cardNumber.length - 1; i >= 0; i--) {
      let digit = parseInt(cardNumber[i]);

      if (isEven) {
        digit *= 2;
        if (digit > 9) {
          digit -= 9;
        }
      }

      sum += digit;
      isEven = !isEven;
    }

    return sum % 10 === 0;
  }

  defaultMessage(args: ValidationArguments) {
    return "Invalid credit card number";
  }
}

export function IsCreditCard(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsCreditCardConstraint,
    });
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Barcode Validators
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Validates EAN-13 barcode
 */
@ValidatorConstraint({ name: "isEAN13", async: false })
export class IsEAN13Constraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "string") {
      return false;
    }

    // Check length and numeric
    if (!/^\d{13}$/.test(value)) {
      return false;
    }

    // Calculate checksum
    let sum = 0;
    for (let i = 0; i < 12; i++) {
      const digit = parseInt(value[i]);
      sum += i % 2 === 0 ? digit : digit * 3;
    }

    const checksum = (10 - (sum % 10)) % 10;
    return checksum === parseInt(value[12]);
  }

  defaultMessage(args: ValidationArguments) {
    return "Invalid EAN-13 barcode";
  }
}

export function IsEAN13(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsEAN13Constraint,
    });
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Export all validators
// ═══════════════════════════════════════════════════════════════════════════

export const CUSTOM_VALIDATORS = {
  IsYemeniPhone,
  IsWithinYemen,
  ContainsArabic,
  IsArabicOnly,
  IsAfterDate,
  IsFutureDate,
  IsStrongPassword,
  IsGeoJSONPolygon,
  IsValidFieldArea,
  IsMoneyValue,
  IsCreditCard,
  IsEAN13,
};
