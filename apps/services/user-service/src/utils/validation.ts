/**
 * Custom Validation Decorators for User Service
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

// ═══════════════════════════════════════════════════════════════════════════
// Strong Password Validator
// ═══════════════════════════════════════════════════════════════════════════

@ValidatorConstraint({ name: "isStrongPassword", async: false })
export class IsStrongPasswordConstraint implements ValidatorConstraintInterface {
  validate(value: any, args: ValidationArguments) {
    if (typeof value !== "string") {
      return false;
    }

    const minLength = args.constraints[0] || 8;

    if (value.length < minLength) {
      return false;
    }

    if (!/[A-Z]/.test(value)) {
      return false;
    }

    if (!/[a-z]/.test(value)) {
      return false;
    }

    if (!/[0-9]/.test(value)) {
      return false;
    }

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
// Sanitization Decorators
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Simple HTML sanitization without external dependencies
 * Security: Decodes entities BEFORE stripping tags to prevent bypass attacks
 */
function sanitizePlainTextValue(input: string): string {
  if (typeof input !== "string") {
    return input;
  }

  let sanitized = input;

  // Remove null bytes
  sanitized = sanitized.replace(/\x00/g, "");

  // Remove control characters (except newline and tab)
  sanitized = sanitized.replace(
    // eslint-disable-next-line no-control-regex
    /[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]/g,
    "",
  );

  // Security: Decode HTML entities FIRST, then strip tags
  // This prevents bypass attacks like &lt;script&gt; -> <script>
  sanitized = sanitized
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, " ");

  // Strip HTML tags AFTER decoding entities
  sanitized = sanitized.replace(/<[^>]*>/g, "");

  // Second pass: decode any remaining entities that might have been nested
  sanitized = sanitized
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&");

  // Final pass: strip any tags that appeared after second decode
  sanitized = sanitized.replace(/<[^>]*>/g, "");

  // Normalize whitespace
  sanitized = sanitized.replace(/\s+/g, " ");

  // Trim
  sanitized = sanitized.trim();

  return sanitized;
}

/**
 * Decorator to sanitize plain text in DTO properties
 */
export function SanitizePlainText() {
  return Transform((params: TransformFnParams) => {
    if (typeof params.value !== "string") {
      return params.value;
    }
    return sanitizePlainTextValue(params.value);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// User Role and Status Enums (must match Prisma schema)
// ═══════════════════════════════════════════════════════════════════════════

export enum UserRole {
  ADMIN = "ADMIN",
  MANAGER = "MANAGER",
  FARMER = "FARMER",
  WORKER = "WORKER",
  VIEWER = "VIEWER",
}

export enum UserStatus {
  ACTIVE = "ACTIVE",
  INACTIVE = "INACTIVE",
  PENDING = "PENDING",
  SUSPENDED = "SUSPENDED",
}
