/**
 * useFormValidation Hook Tests
 * اختبارات خطاف التحقق من النماذج
 */
import { describe, it, expect, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useFormValidation, validationPatterns } from "../useFormValidation";

describe("useFormValidation", () => {
  // ═══════════════════════════════════════════════════════════════════════════
  // INITIALIZATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("initialization", () => {
    it("should initialize fields with default empty values", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { rules: [{ type: "required" }] },
          name: { rules: [] },
        }),
      );

      expect(result.current.fields.email.value).toBe("");
      expect(result.current.fields.name.value).toBe("");
      expect(result.current.fields.email.error).toBeNull();
      expect(result.current.fields.email.touched).toBe(false);
      expect(result.current.fields.email.dirty).toBe(false);
    });

    it("should initialize fields with provided initial values", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { initialValue: "test@example.com", rules: [] },
        }),
      );

      expect(result.current.fields.email.value).toBe("test@example.com");
    });

    it("should report form as valid initially (no errors yet)", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { rules: [{ type: "required" }] },
        }),
      );

      expect(result.current.formState.isValid).toBe(true);
      expect(result.current.formState.isDirty).toBe(false);
      expect(result.current.formState.isSubmitting).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // REQUIRED VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("required validation", () => {
    it("should fail when field is empty", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [{ type: "required" }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.name.error).toBe("This field is required");
      expect(result.current.fields.name.errorAr).toBe("هذا الحقل مطلوب");
    });

    it("should fail when field is whitespace only", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { initialValue: "   ", rules: [{ type: "required" }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.name.error).toBe("This field is required");
    });

    it("should pass when field has value", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { initialValue: "Ahmed", rules: [{ type: "required" }] },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
      expect(result.current.fields.name.error).toBeNull();
    });

    it("should use custom messages when provided", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: {
            rules: [
              {
                type: "required",
                message: "Name is mandatory",
                messageAr: "الاسم إلزامي",
              },
            ],
          },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.name.error).toBe("Name is mandatory");
      expect(result.current.fields.name.errorAr).toBe("الاسم إلزامي");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // EMAIL VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("email validation", () => {
    it("should fail for invalid email", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { initialValue: "not-an-email", rules: [{ type: "email" }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.email.error).toBe("Please enter a valid email address");
      expect(result.current.fields.email.errorAr).toBe("يرجى إدخال بريد إلكتروني صحيح");
    });

    it("should pass for valid email", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { initialValue: "user@sahool.com", rules: [{ type: "email" }] },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
    });

    it("should skip validation for empty email (use required rule for that)", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { initialValue: "", rules: [{ type: "email" }] },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
    });

    it("should fail for email without domain", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { initialValue: "user@", rules: [{ type: "email" }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.email.error).toBeTruthy();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MIN/MAX LENGTH VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("minLength validation", () => {
    it("should fail when value is too short", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { initialValue: "ab", rules: [{ type: "minLength", value: 3 }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.name.error).toBe("Minimum 3 characters required");
      expect(result.current.fields.name.errorAr).toBe("الحد الأدنى 3 حرف");
    });

    it("should pass when value meets minimum length", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { initialValue: "abc", rules: [{ type: "minLength", value: 3 }] },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
    });
  });

  describe("maxLength validation", () => {
    it("should fail when value exceeds maximum length", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          code: { initialValue: "12345", rules: [{ type: "maxLength", value: 4 }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.code.error).toBe("Maximum 4 characters allowed");
      expect(result.current.fields.code.errorAr).toBe("الحد الأقصى 4 حرف");
    });

    it("should pass when value is within limit", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          code: { initialValue: "1234", rules: [{ type: "maxLength", value: 4 }] },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MIN/MAX VALUE VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("min value validation", () => {
    it("should fail when numeric value is below minimum", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          age: { initialValue: "5", rules: [{ type: "min", value: 18 }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.age.error).toBe("Value must be at least 18");
      expect(result.current.fields.age.errorAr).toBe("القيمة يجب أن تكون 18 على الأقل");
    });

    it("should pass when value meets minimum", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          age: { initialValue: "18", rules: [{ type: "min", value: 18 }] },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
    });
  });

  describe("max value validation", () => {
    it("should fail when numeric value exceeds maximum", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          quantity: { initialValue: "101", rules: [{ type: "max", value: 100 }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.quantity.error).toBe("Value must be at most 100");
      expect(result.current.fields.quantity.errorAr).toBe("القيمة يجب ألا تتجاوز 100");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PATTERN VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("pattern validation", () => {
    it("should fail when value does not match pattern", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          code: {
            initialValue: "abc",
            rules: [{ type: "pattern", value: /^\d+$/ }],
          },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.code.error).toBe("Please enter a valid format");
      expect(result.current.fields.code.errorAr).toBe("يرجى إدخال صيغة صحيحة");
    });

    it("should pass when value matches pattern", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          code: {
            initialValue: "12345",
            rules: [{ type: "pattern", value: /^\d+$/ }],
          },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MATCH VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("match validation", () => {
    it("should fail when fields do not match", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          password: { initialValue: "Secret123", rules: [] },
          confirmPassword: {
            initialValue: "Different",
            rules: [{ type: "match", field: "password" }],
          },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.confirmPassword.error).toBe("Fields do not match");
      expect(result.current.fields.confirmPassword.errorAr).toBe("الحقول غير متطابقة");
    });

    it("should pass when fields match", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          password: { initialValue: "Secret123", rules: [] },
          confirmPassword: {
            initialValue: "Secret123",
            rules: [{ type: "match", field: "password" }],
          },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PHONE VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("phone validation", () => {
    it("should fail for invalid phone number", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          phone: { initialValue: "123", rules: [{ type: "phone" }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.phone.error).toBe("Please enter a valid phone number");
      expect(result.current.fields.phone.errorAr).toBe("يرجى إدخال رقم هاتف صحيح");
    });

    it("should pass for valid phone number", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          phone: { initialValue: "+966 55 123 4567", rules: [{ type: "phone" }] },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // URL VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("url validation", () => {
    it("should fail for invalid URL", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          website: { initialValue: "not a url", rules: [{ type: "url" }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.website.error).toBe("Please enter a valid URL");
      expect(result.current.fields.website.errorAr).toBe("يرجى إدخال رابط صحيح");
    });

    it("should pass for valid URL", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          website: { initialValue: "https://sahool.com/api", rules: [{ type: "url" }] },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CUSTOM VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("custom validation", () => {
    it("should fail when custom validator returns false", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          age: {
            initialValue: "15",
            rules: [
              {
                type: "custom",
                validate: (val) => parseInt(val) >= 18,
                message: "Must be 18+",
                messageAr: "يجب أن يكون 18+",
              },
            ],
          },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.age.error).toBe("Must be 18+");
      expect(result.current.fields.age.errorAr).toBe("يجب أن يكون 18+");
    });

    it("should pass when custom validator returns true", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          age: {
            initialValue: "25",
            rules: [
              {
                type: "custom",
                validate: (val) => parseInt(val) >= 18,
              },
            ],
          },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateForm();
      });

      expect(isValid!).toBe(true);
    });

    it("should use default messages when custom messages not provided", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          field: {
            initialValue: "bad",
            rules: [{ type: "custom", validate: () => false }],
          },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.field.error).toBe("Invalid value");
      expect(result.current.fields.field.errorAr).toBe("قيمة غير صالحة");
    });

    it("should receive allValues in custom validator", () => {
      const validateFn = vi.fn().mockReturnValue(true);

      const { result } = renderHook(() =>
        useFormValidation({
          a: { initialValue: "hello", rules: [] },
          b: {
            initialValue: "world",
            rules: [{ type: "custom", validate: validateFn }],
          },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(validateFn).toHaveBeenCalledWith("world", { a: "hello", b: "world" });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MULTI-RULE VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("multi-rule validation", () => {
    it("should stop at first failing rule", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: {
            initialValue: "",
            rules: [
              { type: "required", message: "Required" },
              { type: "email", message: "Invalid email" },
            ],
          },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      // Should stop at required, not get to email
      expect(result.current.fields.email.error).toBe("Required");
    });

    it("should validate second rule when first passes", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: {
            initialValue: "not-an-email",
            rules: [
              { type: "required" },
              { type: "email", message: "Bad format" },
            ],
          },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.email.error).toBe("Bad format");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // HANDLE CHANGE
  // ═══════════════════════════════════════════════════════════════════════════

  describe("handleChange", () => {
    it("should update field value", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [] },
        }),
      );

      act(() => {
        const handler = result.current.handleChange("name");
        handler({ target: { value: "Ahmed" } } as React.ChangeEvent<HTMLInputElement>);
      });

      expect(result.current.fields.name.value).toBe("Ahmed");
    });

    it("should mark field as dirty when changed", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { initialValue: "", rules: [] },
        }),
      );

      act(() => {
        const handler = result.current.handleChange("name");
        handler({ target: { value: "new" } } as React.ChangeEvent<HTMLInputElement>);
      });

      expect(result.current.fields.name.dirty).toBe(true);
      expect(result.current.formState.isDirty).toBe(true);
    });

    it("should not mark dirty when value matches initial", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { initialValue: "same", rules: [] },
        }),
      );

      act(() => {
        const handler = result.current.handleChange("name");
        handler({ target: { value: "same" } } as React.ChangeEvent<HTMLInputElement>);
      });

      expect(result.current.fields.name.dirty).toBe(false);
    });

    it("should be a no-op for non-existent fields", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [] },
        }),
      );

      // Should not throw
      act(() => {
        const handler = result.current.handleChange("nonexistent");
        handler({ target: { value: "test" } } as React.ChangeEvent<HTMLInputElement>);
      });

      expect(result.current.fields.name.value).toBe("");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SET VALUE
  // ═══════════════════════════════════════════════════════════════════════════

  describe("setValue", () => {
    it("should set field value directly", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [] },
        }),
      );

      act(() => {
        result.current.setValue("name", "Direct Value");
      });

      expect(result.current.fields.name.value).toBe("Direct Value");
    });

    it("should be a no-op for non-existent fields", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [] },
        }),
      );

      act(() => {
        result.current.setValue("nonexistent", "test");
      });

      expect(result.current.fields.name.value).toBe("");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // HANDLE BLUR
  // ═══════════════════════════════════════════════════════════════════════════

  describe("handleBlur", () => {
    it("should mark field as touched on blur", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [{ type: "required" }] },
        }),
      );

      act(() => {
        result.current.handleBlur("name")();
      });

      expect(result.current.fields.name.touched).toBe(true);
    });

    it("should validate field on blur", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [{ type: "required" }] },
        }),
      );

      act(() => {
        result.current.handleBlur("name")();
      });

      expect(result.current.fields.name.error).toBe("This field is required");
    });

    it("should be a no-op for non-existent fields", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [] },
        }),
      );

      // Should not throw
      act(() => {
        result.current.handleBlur("nonexistent")();
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // VALIDATE FIELD BY NAME
  // ═══════════════════════════════════════════════════════════════════════════

  describe("validateFieldByName", () => {
    it("should validate a specific field", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { rules: [{ type: "required" }] },
          name: { rules: [{ type: "required" }] },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateFieldByName("email");
      });

      expect(isValid!).toBe(false);
      expect(result.current.fields.email.error).toBeTruthy();
      // name should still have no error
      expect(result.current.fields.name.error).toBeNull();
    });

    it("should return true for non-existent fields", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [] },
        }),
      );

      let isValid: boolean;
      act(() => {
        isValid = result.current.validateFieldByName("nonexistent");
      });

      expect(isValid!).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // RESET FORM
  // ═══════════════════════════════════════════════════════════════════════════

  describe("resetForm", () => {
    it("should reset all fields to initial values", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { initialValue: "initial", rules: [{ type: "required" }] },
        }),
      );

      // Change value to empty and validate to create error state
      act(() => {
        result.current.setValue("name", "");
      });

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.name.error).toBe("This field is required");

      act(() => {
        result.current.resetForm();
      });

      expect(result.current.fields.name.value).toBe("initial");
      expect(result.current.fields.name.error).toBeNull();
      expect(result.current.fields.name.touched).toBe(false);
      expect(result.current.fields.name.dirty).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CLEAR ERRORS
  // ═══════════════════════════════════════════════════════════════════════════

  describe("clearErrors", () => {
    it("should clear all errors while preserving values", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [{ type: "required" }] },
          email: { rules: [{ type: "required" }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.fields.name.error).toBeTruthy();
      expect(result.current.fields.email.error).toBeTruthy();

      act(() => {
        result.current.clearErrors();
      });

      expect(result.current.fields.name.error).toBeNull();
      expect(result.current.fields.email.error).toBeNull();
      expect(result.current.formState.isValid).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SET FIELD ERROR
  // ═══════════════════════════════════════════════════════════════════════════

  describe("setFieldError", () => {
    it("should set error on a specific field", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { rules: [] },
        }),
      );

      act(() => {
        result.current.setFieldError("email", "Email already taken", "البريد مستخدم بالفعل");
      });

      expect(result.current.fields.email.error).toBe("Email already taken");
      expect(result.current.fields.email.errorAr).toBe("البريد مستخدم بالفعل");
      expect(result.current.formState.isValid).toBe(false);
    });

    it("should use en message for ar when ar not provided", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { rules: [] },
        }),
      );

      act(() => {
        result.current.setFieldError("email", "Server error");
      });

      expect(result.current.fields.email.error).toBe("Server error");
      expect(result.current.fields.email.errorAr).toBe("Server error");
    });

    it("should be a no-op for non-existent fields", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [] },
        }),
      );

      act(() => {
        result.current.setFieldError("nonexistent", "error");
      });

      expect(result.current.formState.isValid).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GET VALUES
  // ═══════════════════════════════════════════════════════════════════════════

  describe("getValues", () => {
    it("should return all current field values", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { initialValue: "test@test.com", rules: [] },
          name: { initialValue: "Test", rules: [] },
        }),
      );

      const values = result.current.getValues();
      expect(values).toEqual({ email: "test@test.com", name: "Test" });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // HANDLE SUBMIT
  // ═══════════════════════════════════════════════════════════════════════════

  describe("handleSubmit", () => {
    it("should call onSubmit when form is valid", async () => {
      const onSubmit = vi.fn().mockResolvedValue(undefined);

      const { result } = renderHook(() =>
        useFormValidation({
          name: { initialValue: "Ahmed", rules: [{ type: "required" }] },
        }),
      );

      await act(async () => {
        const handler = result.current.handleSubmit(onSubmit);
        await handler({ preventDefault: vi.fn() } as unknown as React.FormEvent);
      });

      expect(onSubmit).toHaveBeenCalledWith({ name: "Ahmed" });
    });

    it("should not call onSubmit when form is invalid", async () => {
      const onSubmit = vi.fn();

      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [{ type: "required" }] },
        }),
      );

      await act(async () => {
        const handler = result.current.handleSubmit(onSubmit);
        await handler({ preventDefault: vi.fn() } as unknown as React.FormEvent);
      });

      expect(onSubmit).not.toHaveBeenCalled();
    });

    it("should set isSubmitting during submission", async () => {
      let resolveSubmit: () => void;
      const submitPromise = new Promise<void>((resolve) => {
        resolveSubmit = resolve;
      });
      const onSubmit = vi.fn().mockReturnValue(submitPromise);

      const { result } = renderHook(() =>
        useFormValidation({
          name: { initialValue: "test", rules: [{ type: "required" }] },
        }),
      );

      let handlerPromise: Promise<void>;
      act(() => {
        const handler = result.current.handleSubmit(onSubmit);
        handlerPromise = handler({ preventDefault: vi.fn() } as unknown as React.FormEvent);
      });

      expect(result.current.formState.isSubmitting).toBe(true);

      await act(async () => {
        resolveSubmit!();
        await handlerPromise!;
      });

      expect(result.current.formState.isSubmitting).toBe(false);
    });

    it("should reset isSubmitting even if onSubmit throws", async () => {
      const onSubmit = vi.fn().mockRejectedValue(new Error("fail"));

      const { result } = renderHook(() =>
        useFormValidation({
          name: { initialValue: "test", rules: [{ type: "required" }] },
        }),
      );

      await act(async () => {
        const handler = result.current.handleSubmit(onSubmit);
        await handler({ preventDefault: vi.fn() } as unknown as React.FormEvent).catch(() => {});
      });

      expect(result.current.formState.isSubmitting).toBe(false);
    });

    it("should call preventDefault on the event", async () => {
      const preventDefault = vi.fn();
      const onSubmit = vi.fn();

      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [{ type: "required" }] },
        }),
      );

      await act(async () => {
        const handler = result.current.handleSubmit(onSubmit);
        await handler({ preventDefault } as unknown as React.FormEvent);
      });

      expect(preventDefault).toHaveBeenCalled();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SET IS SUBMITTING
  // ═══════════════════════════════════════════════════════════════════════════

  describe("setIsSubmitting", () => {
    it("should update isSubmitting state", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          name: { rules: [] },
        }),
      );

      act(() => {
        result.current.setIsSubmitting(true);
      });

      expect(result.current.formState.isSubmitting).toBe(true);

      act(() => {
        result.current.setIsSubmitting(false);
      });

      expect(result.current.formState.isSubmitting).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FORM STATE
  // ═══════════════════════════════════════════════════════════════════════════

  describe("formState", () => {
    it("should track errors across all fields", () => {
      const { result } = renderHook(() =>
        useFormValidation({
          email: { rules: [{ type: "required" }] },
          name: { initialValue: "valid", rules: [{ type: "required" }] },
        }),
      );

      act(() => {
        result.current.validateForm();
      });

      expect(result.current.formState.isValid).toBe(false);
      expect(result.current.formState.errors.email).toBeTruthy();
      expect(result.current.formState.errors.name).toBeNull();
      expect(result.current.formState.errorsAr.email).toBeTruthy();
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// VALIDATION PATTERNS
// ═══════════════════════════════════════════════════════════════════════════════

describe("validationPatterns", () => {
  describe("email", () => {
    it("should match valid emails", () => {
      expect(validationPatterns.email.test("user@example.com")).toBe(true);
      expect(validationPatterns.email.test("a@b.co")).toBe(true);
    });

    it("should reject invalid emails", () => {
      expect(validationPatterns.email.test("noatsign")).toBe(false);
      expect(validationPatterns.email.test("@no-local.com")).toBe(false);
    });
  });

  describe("phone", () => {
    it("should match valid phone numbers", () => {
      expect(validationPatterns.phone.test("+966551234567")).toBe(true);
      expect(validationPatterns.phone.test("12345678")).toBe(true);
    });

    it("should reject short numbers", () => {
      expect(validationPatterns.phone.test("123")).toBe(false);
    });
  });

  describe("phoneYemen", () => {
    it("should match Yemen phone formats", () => {
      expect(validationPatterns.phoneYemen.test("771234567")).toBe(true);
      expect(validationPatterns.phoneYemen.test("711234567")).toBe(true);
      expect(validationPatterns.phoneYemen.test("+96771234567")).toBe(true);
    });
  });

  describe("strongPassword", () => {
    it("should match strong passwords", () => {
      expect(validationPatterns.strongPassword.test("Str0ng@Pass")).toBe(true);
    });

    it("should reject weak passwords", () => {
      expect(validationPatterns.strongPassword.test("weakpass")).toBe(false);
      expect(validationPatterns.strongPassword.test("NoDigits!")).toBe(false);
    });
  });

  describe("arabic", () => {
    it("should match Arabic text", () => {
      expect(validationPatterns.arabic.test("مرحبا")).toBe(true);
      expect(validationPatterns.arabic.test("سهول")).toBe(true);
    });

    it("should reject non-Arabic text", () => {
      expect(validationPatterns.arabic.test("hello")).toBe(false);
    });
  });

  describe("numeric", () => {
    it("should match numeric values", () => {
      expect(validationPatterns.numeric.test("12345")).toBe(true);
    });

    it("should reject non-numeric", () => {
      expect(validationPatterns.numeric.test("12.5")).toBe(false);
      expect(validationPatterns.numeric.test("abc")).toBe(false);
    });
  });

  describe("decimal", () => {
    it("should match decimal values", () => {
      expect(validationPatterns.decimal.test("12.5")).toBe(true);
      expect(validationPatterns.decimal.test("12")).toBe(true);
    });

    it("should reject non-decimal values", () => {
      expect(validationPatterns.decimal.test("abc")).toBe(false);
    });
  });

  describe("date", () => {
    it("should match YYYY-MM-DD format", () => {
      expect(validationPatterns.date.test("2025-01-15")).toBe(true);
    });

    it("should reject invalid date formats", () => {
      expect(validationPatterns.date.test("15/01/2025")).toBe(false);
    });
  });
});
