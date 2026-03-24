'use client';

import { useState, useCallback, useMemo } from 'react';

/**
 * Validation rule types for form fields
 */
export type ValidationRule =
  | { type: 'required'; message?: string; messageAr?: string }
  | { type: 'email'; message?: string; messageAr?: string }
  | { type: 'minLength'; value: number; message?: string; messageAr?: string }
  | { type: 'maxLength'; value: number; message?: string; messageAr?: string }
  | { type: 'min'; value: number; message?: string; messageAr?: string }
  | { type: 'max'; value: number; message?: string; messageAr?: string }
  | { type: 'pattern'; value: RegExp; message?: string; messageAr?: string }
  | { type: 'match'; field: string; message?: string; messageAr?: string }
  | { type: 'phone'; message?: string; messageAr?: string }
  | { type: 'url'; message?: string; messageAr?: string }
  | {
      type: 'custom';
      validate: (value: string, values: Record<string, string>) => boolean;
      message?: string;
      messageAr?: string;
    };

/**
 * Field configuration with validation rules
 */
export interface FieldConfig {
  initialValue?: string;
  rules?: ValidationRule[];
}

/**
 * Form field state
 */
export interface FieldState {
  value: string;
  error: string | null;
  errorAr: string | null;
  touched: boolean;
  dirty: boolean;
}

/**
 * Form state
 */
export interface FormState {
  isValid: boolean;
  isSubmitting: boolean;
  isDirty: boolean;
  errors: Record<string, string | null>;
  errorsAr: Record<string, string | null>;
}

/**
 * Default validation messages (bilingual)
 */
const defaultMessages = {
  required: { en: 'This field is required', ar: 'هذا الحقل مطلوب' },
  email: { en: 'Please enter a valid email address', ar: 'يرجى إدخال بريد إلكتروني صحيح' },
  minLength: {
    en: (n: number) => `Minimum ${n} characters required`,
    ar: (n: number) => `الحد الأدنى ${n} حرف`,
  },
  maxLength: {
    en: (n: number) => `Maximum ${n} characters allowed`,
    ar: (n: number) => `الحد الأقصى ${n} حرف`,
  },
  min: {
    en: (n: number) => `Value must be at least ${n}`,
    ar: (n: number) => `القيمة يجب أن تكون ${n} على الأقل`,
  },
  max: {
    en: (n: number) => `Value must be at most ${n}`,
    ar: (n: number) => `القيمة يجب ألا تتجاوز ${n}`,
  },
  pattern: { en: 'Please enter a valid format', ar: 'يرجى إدخال صيغة صحيحة' },
  match: { en: 'Fields do not match', ar: 'الحقول غير متطابقة' },
  phone: { en: 'Please enter a valid phone number', ar: 'يرجى إدخال رقم هاتف صحيح' },
  url: { en: 'Please enter a valid URL', ar: 'يرجى إدخال رابط صحيح' },
  custom: { en: 'Invalid value', ar: 'قيمة غير صالحة' },
};

/**
 * Common validation patterns
 */
export const validationPatterns = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^[\d\s+()-]{8,}$/,
  phoneYemen: /^(009677|9677|\+9677|07|77|71|73|70)\d{7}$/,
  url: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
  strongPassword: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
  alphanumeric: /^[a-zA-Z0-9]+$/,
  arabic: /^[\u0600-\u06FF\s]+$/,
  numeric: /^\d+$/,
  decimal: /^\d+(\.\d+)?$/,
  date: /^\d{4}-\d{2}-\d{2}$/,
};

/**
 * Validate a single field value against rules
 */
function validateField(
  value: string,
  rules: ValidationRule[],
  allValues: Record<string, string>
): { error: string | null; errorAr: string | null } {
  for (const rule of rules) {
    switch (rule.type) {
      case 'required':
        if (!value || value.trim() === '') {
          return {
            error: rule.message || defaultMessages.required.en,
            errorAr: rule.messageAr || defaultMessages.required.ar,
          };
        }
        break;

      case 'email':
        if (value && !validationPatterns.email.test(value)) {
          return {
            error: rule.message || defaultMessages.email.en,
            errorAr: rule.messageAr || defaultMessages.email.ar,
          };
        }
        break;

      case 'minLength':
        if (value && value.length < rule.value) {
          return {
            error: rule.message || defaultMessages.minLength.en(rule.value),
            errorAr: rule.messageAr || defaultMessages.minLength.ar(rule.value),
          };
        }
        break;

      case 'maxLength':
        if (value && value.length > rule.value) {
          return {
            error: rule.message || defaultMessages.maxLength.en(rule.value),
            errorAr: rule.messageAr || defaultMessages.maxLength.ar(rule.value),
          };
        }
        break;

      case 'min':
        if (value && Number(value) < rule.value) {
          return {
            error: rule.message || defaultMessages.min.en(rule.value),
            errorAr: rule.messageAr || defaultMessages.min.ar(rule.value),
          };
        }
        break;

      case 'max':
        if (value && Number(value) > rule.value) {
          return {
            error: rule.message || defaultMessages.max.en(rule.value),
            errorAr: rule.messageAr || defaultMessages.max.ar(rule.value),
          };
        }
        break;

      case 'pattern':
        if (value && !rule.value.test(value)) {
          return {
            error: rule.message || defaultMessages.pattern.en,
            errorAr: rule.messageAr || defaultMessages.pattern.ar,
          };
        }
        break;

      case 'match':
        if (value !== allValues[rule.field]) {
          return {
            error: rule.message || defaultMessages.match.en,
            errorAr: rule.messageAr || defaultMessages.match.ar,
          };
        }
        break;

      case 'phone':
        if (value && !validationPatterns.phone.test(value)) {
          return {
            error: rule.message || defaultMessages.phone.en,
            errorAr: rule.messageAr || defaultMessages.phone.ar,
          };
        }
        break;

      case 'url':
        if (value && !validationPatterns.url.test(value)) {
          return {
            error: rule.message || defaultMessages.url.en,
            errorAr: rule.messageAr || defaultMessages.url.ar,
          };
        }
        break;

      case 'custom':
        if (!rule.validate(value, allValues)) {
          return {
            error: rule.message || defaultMessages.custom.en,
            errorAr: rule.messageAr || defaultMessages.custom.ar,
          };
        }
        break;
    }
  }

  return { error: null, errorAr: null };
}

/**
 * useFormValidation Hook
 *
 * A comprehensive form validation hook with bilingual support (Arabic/English)
 *
 * Features:
 * - Multiple validation rule types (required, email, pattern, etc.)
 * - Real-time validation on change/blur
 * - Bilingual error messages
 * - Form state management (dirty, touched, valid)
 * - Custom validation rules support
 *
 * @example
 * ```tsx
 * const { fields, formState, handleChange, handleBlur, validateForm, resetForm } = useFormValidation({
 *   email: {
 *     initialValue: '',
 *     rules: [
 *       { type: 'required', messageAr: 'البريد الإلكتروني مطلوب' },
 *       { type: 'email' }
 *     ]
 *   },
 *   password: {
 *     rules: [
 *       { type: 'required' },
 *       { type: 'minLength', value: 8 }
 *     ]
 *   }
 * });
 * ```
 */
export function useFormValidation(config: Record<string, FieldConfig>) {
  // Initialize field states
  const initialFields = useMemo(() => {
    const result: Record<string, FieldState> = {};
    for (const [name, fieldConfig] of Object.entries(config)) {
      result[name] = {
        value: fieldConfig.initialValue || '',
        error: null,
        errorAr: null,
        touched: false,
        dirty: false,
      };
    }
    return result;
  }, [config]);

  const [fields, setFields] = useState<Record<string, FieldState>>(initialFields);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Get all current values
  const getAllValues = useCallback(() => {
    const values: Record<string, string> = {};
    for (const [name, state] of Object.entries(fields)) {
      values[name] = state.value;
    }
    return values;
  }, [fields]);

  // Handle field change
  const handleChange = useCallback(
    (name: string) =>
      (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const value = e.target.value;
        setFields((prev) => {
          const prevField = prev[name];
          if (!prevField) return prev;
          return {
            ...prev,
            [name]: {
              value,
              error: prevField.error,
              errorAr: prevField.errorAr,
              touched: prevField.touched,
              dirty: value !== (config[name]?.initialValue || ''),
            },
          };
        });
      },
    [config]
  );

  // Set field value directly
  const setValue = useCallback(
    (name: string, value: string) => {
      setFields((prev) => {
        const prevField = prev[name];
        if (!prevField) return prev;
        return {
          ...prev,
          [name]: {
            value,
            error: prevField.error,
            errorAr: prevField.errorAr,
            touched: prevField.touched,
            dirty: value !== (config[name]?.initialValue || ''),
          },
        };
      });
    },
    [config]
  );

  // Handle field blur (validate on blur)
  const handleBlur = useCallback(
    (name: string) => () => {
      const fieldConfig = config[name];
      if (!fieldConfig) return;

      const currentField = fields[name];
      if (!currentField) return;

      const allValues = getAllValues();
      const { error, errorAr } = validateField(
        currentField.value,
        fieldConfig.rules || [],
        allValues
      );

      setFields((prev) => {
        const prevField = prev[name];
        if (!prevField) return prev;
        return {
          ...prev,
          [name]: {
            value: prevField.value,
            dirty: prevField.dirty,
            touched: true,
            error,
            errorAr,
          },
        };
      });
    },
    [config, fields, getAllValues]
  );

  // Validate single field
  const validateFieldByName = useCallback(
    (name: string): boolean => {
      const fieldConfig = config[name];
      if (!fieldConfig) return true;

      const currentField = fields[name];
      if (!currentField) return true;

      const allValues = getAllValues();
      const { error, errorAr } = validateField(
        currentField.value,
        fieldConfig.rules || [],
        allValues
      );

      setFields((prev) => {
        const prevField = prev[name];
        if (!prevField) return prev;
        return {
          ...prev,
          [name]: {
            value: prevField.value,
            dirty: prevField.dirty,
            touched: true,
            error,
            errorAr,
          },
        };
      });

      return error === null;
    },
    [config, fields, getAllValues]
  );

  // Validate all fields
  const validateForm = useCallback((): boolean => {
    const allValues = getAllValues();
    let isValid = true;
    const newFields: Record<string, FieldState> = {};

    for (const [name, fieldConfig] of Object.entries(config)) {
      const currentField = fields[name];
      if (!currentField) continue;

      const { error, errorAr } = validateField(
        currentField.value,
        fieldConfig.rules || [],
        allValues
      );

      newFields[name] = {
        value: currentField.value,
        dirty: currentField.dirty,
        touched: true,
        error,
        errorAr,
      };

      if (error !== null) {
        isValid = false;
      }
    }

    setFields((prev) => ({ ...prev, ...newFields }));
    return isValid;
  }, [config, fields, getAllValues]);

  // Reset form to initial values
  const resetForm = useCallback(() => {
    setFields(initialFields);
    setIsSubmitting(false);
  }, [initialFields]);

  // Clear all errors
  const clearErrors = useCallback(() => {
    setFields((prev) => {
      const newFields: Record<string, FieldState> = {};
      for (const [name, field] of Object.entries(prev)) {
        newFields[name] = {
          value: field.value,
          touched: field.touched,
          dirty: field.dirty,
          error: null,
          errorAr: null,
        };
      }
      return newFields;
    });
  }, []);

  // Set field error manually
  const setFieldError = useCallback((name: string, error: string, errorAr?: string) => {
    setFields((prev) => {
      const prevField = prev[name];
      if (!prevField) return prev;
      return {
        ...prev,
        [name]: {
          value: prevField.value,
          touched: prevField.touched,
          dirty: prevField.dirty,
          error,
          errorAr: errorAr || error,
        },
      };
    });
  }, []);

  // Compute form state
  const formState: FormState = useMemo(() => {
    const errors: Record<string, string | null> = {};
    const errorsAr: Record<string, string | null> = {};
    let hasErrors = false;
    let isDirty = false;

    for (const [name, state] of Object.entries(fields)) {
      errors[name] = state.error;
      errorsAr[name] = state.errorAr;
      if (state.error !== null) hasErrors = true;
      if (state.dirty) isDirty = true;
    }

    return {
      isValid: !hasErrors,
      isSubmitting,
      isDirty,
      errors,
      errorsAr,
    };
  }, [fields, isSubmitting]);

  // Get values for submission
  const getValues = useCallback(() => {
    return getAllValues();
  }, [getAllValues]);

  // Handle form submission
  const handleSubmit = useCallback(
    (onSubmit: (values: Record<string, string>) => Promise<void> | void) =>
      async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
          return;
        }

        setIsSubmitting(true);

        try {
          await onSubmit(getValues());
        } finally {
          setIsSubmitting(false);
        }
      },
    [validateForm, getValues]
  );

  return {
    fields,
    formState,
    handleChange,
    handleBlur,
    setValue,
    validateForm,
    validateFieldByName,
    resetForm,
    clearErrors,
    setFieldError,
    getValues,
    handleSubmit,
    setIsSubmitting,
  };
}

export default useFormValidation;
