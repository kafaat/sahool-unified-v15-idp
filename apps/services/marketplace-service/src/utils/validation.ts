/**
 * Custom Validation Decorators for Marketplace Service
 * مزخرفات التحقق المخصصة
 */

import {
  registerDecorator,
  ValidationOptions,
  ValidationArguments,
  ValidatorConstraint,
  ValidatorConstraintInterface,
} from "class-validator";
import { Transform, TransformFnParams } from "class-transformer";

// ═══════════════════════════════════════════════════════════════════════════
// Money Value Validator
// ═══════════════════════════════════════════════════════════════════════════

@ValidatorConstraint({ name: "isMoneyValue", async: false })
export class IsMoneyValueConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "number") {
      return false;
    }

    if (value < 0) {
      return false;
    }

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

// ═══════════════════════════════════════════════════════════════════════════
// Yemen Phone Validator
// ═══════════════════════════════════════════════════════════════════════════

@ValidatorConstraint({ name: "isYemeniPhone", async: false })
export class IsYemeniPhoneConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "string") {
      return false;
    }

    const patterns = [
      /^(\+967|967|00967)(7[0-9]{8})$/,
      /^(7[0-9]{8})$/,
      /^(77|78)[0-9]{7}$/,
    ];

    return patterns.some((pattern) => pattern.test(value.replace(/\s/g, "")));
  }

  defaultMessage(args: ValidationArguments) {
    return "Phone number must be a valid Yemeni phone number";
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

// ═══════════════════════════════════════════════════════════════════════════
// Date Validators
// ═══════════════════════════════════════════════════════════════════════════

@ValidatorConstraint({ name: "isAfterDate", async: false })
export class IsAfterDateConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    const [relatedPropertyName] = args.constraints;
    const relatedValue = (args.object as any)[relatedPropertyName];

    if (!value || !relatedValue) {
      return true;
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

@ValidatorConstraint({ name: "isFutureDate", async: false })
export class IsFutureDateConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (!value) {
      return true;
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

// ═══════════════════════════════════════════════════════════════════════════
// Sanitization Decorator
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Sanitize plain text - removes all HTML and normalizes whitespace.
 * Security: Uses iterative approach to handle nested/encoded HTML.
 */
function sanitizePlainTextValue(input: string): string {
  if (typeof input !== "string") {
    return input;
  }

  let sanitized = input;

  // Remove null bytes
  sanitized = sanitized.replace(/\x00/g, "");

  // Remove control characters
  sanitized = sanitized.replace(/[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]/g, "");

  // Security: Iteratively decode and strip to handle nested/encoded HTML
  // Limit iterations to prevent infinite loops
  const MAX_ITERATIONS = 5;
  for (let i = 0; i < MAX_ITERATIONS; i++) {
    const before = sanitized;

    // Decode HTML entities (order matters: decode &amp; last to avoid double-decode)
    sanitized = sanitized
      .replace(/&lt;/gi, "<")
      .replace(/&gt;/gi, ">")
      .replace(/&quot;/gi, '"')
      .replace(/&#0*39;/gi, "'")
      .replace(/&#x0*27;/gi, "'")
      .replace(/&apos;/gi, "'")
      .replace(/&nbsp;/gi, " ")
      .replace(/&#0*60;/gi, "<")
      .replace(/&#0*62;/gi, ">")
      .replace(/&#x0*3c;/gi, "<")
      .replace(/&#x0*3e;/gi, ">")
      .replace(/&amp;/gi, "&");

    // Strip HTML tags
    sanitized = sanitized.replace(/<[^>]*>/g, "");

    // If no changes, we're done
    if (sanitized === before) {
      break;
    }
  }

  // Final safety: remove any remaining angle brackets
  sanitized = sanitized.replace(/[<>]/g, "");

  // Normalize whitespace
  sanitized = sanitized.replace(/\s+/g, " ");

  // Trim
  sanitized = sanitized.trim();

  return sanitized;
}

export function SanitizePlainText() {
  return Transform((params: TransformFnParams) => {
    if (typeof params.value !== "string") {
      return params.value;
    }
    return sanitizePlainTextValue(params.value);
  });
}
