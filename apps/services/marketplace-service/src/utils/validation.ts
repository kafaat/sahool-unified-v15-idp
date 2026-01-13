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

function sanitizePlainTextValue(input: string): string {
  if (typeof input !== "string") {
    return input;
  }

  let sanitized = input;

  // Remove null bytes
  sanitized = sanitized.replace(/\x00/g, "");

  // Remove control characters
  sanitized = sanitized.replace(/[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]/g, "");

  // Strip HTML tags
  sanitized = sanitized.replace(/<[^>]*>/g, "");

  // Decode common HTML entities
  sanitized = sanitized
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, " ");

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
