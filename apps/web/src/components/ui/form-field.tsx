'use client';

import * as React from 'react';
import { clsx } from 'clsx';
import { Input, type InputProps } from './input';
import { validationPatterns, type ValidationRule } from '@/hooks/useFormValidation';

export interface FormFieldProps extends Omit<InputProps, 'error'> {
  /** Field name for form identification */
  name: string;
  /** Validation rules */
  rules?: ValidationRule[];
  /** Current error message */
  error?: string | null;
  /** Arabic error message */
  errorAr?: string | null;
  /** Show validation status icon */
  showValidationIcon?: boolean;
  /** Character counter */
  showCharCount?: boolean;
  /** Maximum characters for counter */
  maxChars?: number;
  /** Validate on change vs blur */
  validateOn?: 'change' | 'blur';
  /** Custom validation function */
  onValidate?: (value: string) => { valid: boolean; error?: string; errorAr?: string };
  /** Success message when valid */
  successMessage?: string;
  /** Arabic success message */
  successMessageAr?: string;
}

/**
 * FormField Component
 *
 * Enhanced form input with built-in validation, accessibility, and bilingual support.
 *
 * Features:
 * - Real-time validation
 * - Character counter
 * - Validation icons
 * - Bilingual error messages
 * - Accessible error announcements
 *
 * @example
 * ```tsx
 * <FormField
 *   name="email"
 *   label="Email"
 *   labelAr="البريد الإلكتروني"
 *   type="email"
 *   rules={[
 *     { type: 'required', messageAr: 'البريد الإلكتروني مطلوب' },
 *     { type: 'email' }
 *   ]}
 *   showValidationIcon
 * />
 * ```
 */
export function FormField({
  name,
  rules = [],
  error,
  errorAr,
  showValidationIcon = false,
  showCharCount = false,
  maxChars,
  validateOn = 'blur',
  onValidate,
  successMessage,
  successMessageAr,
  value,
  onChange,
  onBlur,
  className,
  ...inputProps
}: FormFieldProps) {
  const [localError, setLocalError] = React.useState<string | null>(null);
  const [localErrorAr, setLocalErrorAr] = React.useState<string | null>(null);
  const [touched, setTouched] = React.useState(false);
  const [isValid, setIsValid] = React.useState(false);

  const inputRef = React.useRef<HTMLInputElement>(null);
  const errorId = `${name}-error`;
  const successId = `${name}-success`;
  const countId = `${name}-count`;

  // Get the current value
  const currentValue = typeof value === 'string' ? value : '';
  const charCount = currentValue.length;

  // Validate the field
  const validate = React.useCallback(
    (val: string) => {
      // Custom validation
      if (onValidate) {
        const result = onValidate(val);
        setLocalError(result.valid ? null : result.error || 'Invalid value');
        setLocalErrorAr(result.valid ? null : result.errorAr || 'قيمة غير صالحة');
        setIsValid(result.valid);
        return result.valid;
      }

      // Rule-based validation
      for (const rule of rules) {
        switch (rule.type) {
          case 'required':
            if (!val || val.trim() === '') {
              setLocalError(rule.message || 'This field is required');
              setLocalErrorAr(rule.messageAr || 'هذا الحقل مطلوب');
              setIsValid(false);
              return false;
            }
            break;

          case 'email':
            if (val && !validationPatterns.email.test(val)) {
              setLocalError(rule.message || 'Please enter a valid email');
              setLocalErrorAr(rule.messageAr || 'يرجى إدخال بريد إلكتروني صحيح');
              setIsValid(false);
              return false;
            }
            break;

          case 'minLength':
            if (val && val.length < rule.value) {
              setLocalError(rule.message || `Minimum ${rule.value} characters`);
              setLocalErrorAr(rule.messageAr || `الحد الأدنى ${rule.value} حرف`);
              setIsValid(false);
              return false;
            }
            break;

          case 'maxLength':
            if (val && val.length > rule.value) {
              setLocalError(rule.message || `Maximum ${rule.value} characters`);
              setLocalErrorAr(rule.messageAr || `الحد الأقصى ${rule.value} حرف`);
              setIsValid(false);
              return false;
            }
            break;

          case 'pattern':
            if (val && !rule.value.test(val)) {
              setLocalError(rule.message || 'Invalid format');
              setLocalErrorAr(rule.messageAr || 'صيغة غير صحيحة');
              setIsValid(false);
              return false;
            }
            break;

          case 'phone':
            if (val && !validationPatterns.phone.test(val)) {
              setLocalError(rule.message || 'Invalid phone number');
              setLocalErrorAr(rule.messageAr || 'رقم الهاتف غير صحيح');
              setIsValid(false);
              return false;
            }
            break;

          case 'url':
            if (val && !validationPatterns.url.test(val)) {
              setLocalError(rule.message || 'Invalid URL');
              setLocalErrorAr(rule.messageAr || 'الرابط غير صحيح');
              setIsValid(false);
              return false;
            }
            break;
        }
      }

      setLocalError(null);
      setLocalErrorAr(null);
      setIsValid(rules.length > 0 && val.length > 0);
      return true;
    },
    [rules, onValidate]
  );

  // Handle change with validation
  const handleChange = React.useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e);

      if (validateOn === 'change' || touched) {
        validate(e.target.value);
      }
    },
    [onChange, validateOn, touched, validate]
  );

  // Handle blur with validation
  const handleBlur = React.useCallback(
    (e: React.FocusEvent<HTMLInputElement>) => {
      onBlur?.(e);
      setTouched(true);

      if (validateOn === 'blur') {
        validate(e.target.value);
      }
    },
    [onBlur, validateOn, validate]
  );

  // Compute final error state
  const finalError = error ?? localError;
  const finalErrorAr = errorAr ?? localErrorAr;
  const hasError = touched && finalError;
  const showSuccess = touched && isValid && !hasError && (successMessage || successMessageAr);

  // Build aria-describedby
  const describedBy =
    [
      hasError ? errorId : null,
      showSuccess ? successId : null,
      showCharCount ? countId : null,
      inputProps.helperText ? `${name}-helper` : null,
    ]
      .filter(Boolean)
      .join(' ') || undefined;

  // Validation icon
  const ValidationIcon = () => {
    if (!showValidationIcon || !touched) return null;

    if (hasError) {
      return (
        <svg
          className="w-5 h-5 text-red-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      );
    }

    if (isValid) {
      return (
        <svg
          className="w-5 h-5 text-green-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      );
    }

    return null;
  };

  return (
    <div className={clsx('w-full', className)}>
      <Input
        ref={inputRef}
        name={name}
        value={value}
        onChange={handleChange}
        onBlur={handleBlur}
        error={hasError ? `${finalErrorAr || ''} ${finalError || ''}`.trim() : undefined}
        aria-describedby={describedBy}
        rightIcon={showValidationIcon ? <ValidationIcon /> : inputProps.rightIcon}
        {...inputProps}
      />

      {/* Success message */}
      {showSuccess && (
        <p
          id={successId}
          className="mt-1.5 text-sm text-green-600 flex items-center gap-1"
          role="status"
          aria-live="polite"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>{successMessageAr}</span>
          {successMessageAr && successMessage && <span className="mx-1">-</span>}
          <span className="text-xs">{successMessage}</span>
        </p>
      )}

      {/* Character counter */}
      {showCharCount && (
        <p
          id={countId}
          className={clsx(
            'mt-1 text-xs text-end',
            maxChars && charCount > maxChars ? 'text-red-500' : 'text-gray-400'
          )}
          aria-live="polite"
        >
          {maxChars ? `${charCount}/${maxChars}` : charCount}
          <span className="sr-only">
            {maxChars ? ` characters out of ${maxChars} maximum` : ` characters entered`}
          </span>
        </p>
      )}
    </div>
  );
}

FormField.displayName = 'FormField';

/**
 * Pre-configured form field components for common use cases
 */

export function EmailField(props: Omit<FormFieldProps, 'type' | 'rules'>) {
  return (
    <FormField
      type="email"
      autoComplete="email"
      rules={[
        { type: 'required', messageAr: 'البريد الإلكتروني مطلوب' },
        { type: 'email', messageAr: 'يرجى إدخال بريد إلكتروني صحيح' },
      ]}
      showValidationIcon
      {...props}
    />
  );
}

export function PasswordField(props: Omit<FormFieldProps, 'type' | 'rules'>) {
  return (
    <FormField
      type="password"
      autoComplete="current-password"
      rules={[
        { type: 'required', messageAr: 'كلمة المرور مطلوبة' },
        { type: 'minLength', value: 8, messageAr: 'كلمة المرور يجب أن تكون 8 أحرف على الأقل' },
      ]}
      showValidationIcon
      {...props}
    />
  );
}

export function PhoneField(props: Omit<FormFieldProps, 'type' | 'rules'>) {
  return (
    <FormField
      type="tel"
      autoComplete="tel"
      rules={[
        { type: 'required', messageAr: 'رقم الهاتف مطلوب' },
        { type: 'phone', messageAr: 'يرجى إدخال رقم هاتف صحيح' },
      ]}
      showValidationIcon
      {...props}
    />
  );
}

export function NameField(props: Omit<FormFieldProps, 'type' | 'rules'>) {
  return (
    <FormField
      type="text"
      autoComplete="name"
      rules={[
        { type: 'required', messageAr: 'الاسم مطلوب' },
        { type: 'minLength', value: 2, messageAr: 'الاسم يجب أن يكون حرفين على الأقل' },
      ]}
      showValidationIcon
      {...props}
    />
  );
}

export default FormField;
