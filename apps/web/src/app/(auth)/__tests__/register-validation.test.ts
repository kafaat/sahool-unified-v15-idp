/**
 * Registration Form Validation Tests
 * اختبارات التحقق من نموذج التسجيل
 *
 * Tests the pure validateForm function extracted from RegisterClient.tsx
 * These are unit tests of the validation logic without rendering React components.
 */
import { describe, it, expect } from "vitest";

// Re-implement the validateForm function for testing since it's not exported
// This mirrors the exact logic in RegisterClient.tsx

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  phone: string;
}

interface RegisterError {
  field?: string;
  message: string;
}

function validateForm(data: RegisterFormData): RegisterError[] {
  const errors: RegisterError[] = [];

  // Email validation
  if (!data.email) {
    errors.push({ field: "email", message: "Email is required" });
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.push({ field: "email", message: "Invalid email format" });
  }

  // First name validation
  if (!data.firstName.trim()) {
    errors.push({ field: "firstName", message: "First name is required" });
  } else if (data.firstName.trim().length < 2) {
    errors.push({ field: "firstName", message: "First name must be at least 2 characters" });
  }

  // Last name validation
  if (!data.lastName.trim()) {
    errors.push({ field: "lastName", message: "Last name is required" });
  } else if (data.lastName.trim().length < 2) {
    errors.push({ field: "lastName", message: "Last name must be at least 2 characters" });
  }

  // Password validation
  if (!data.password) {
    errors.push({ field: "password", message: "Password is required" });
  } else if (data.password.length < 8) {
    errors.push({ field: "password", message: "Password must be at least 8 characters" });
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(data.password)) {
    errors.push({
      field: "password",
      message: "Password must contain uppercase, lowercase, and number",
    });
  }

  // Confirm password validation
  if (!data.confirmPassword) {
    errors.push({ field: "confirmPassword", message: "Please confirm your password" });
  } else if (data.password !== data.confirmPassword) {
    errors.push({ field: "confirmPassword", message: "Passwords do not match" });
  }

  // Phone validation (optional but must be valid if provided)
  if (data.phone && !/^\+?[\d\s-]{7,15}$/.test(data.phone)) {
    errors.push({ field: "phone", message: "Invalid phone number format" });
  }

  return errors;
}

// Also test getErrorMessage function
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    const axiosError = error as { response?: { data?: { message?: string; detail?: string } } };
    if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    return error.message;
  }
  return "Registration failed. Please try again.";
}

describe("RegisterClient - validateForm", () => {
  const validData: RegisterFormData = {
    email: "ahmed@sahool.com",
    password: "SecurePass1",
    confirmPassword: "SecurePass1",
    firstName: "Ahmed",
    lastName: "Al-Rashid",
    phone: "",
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // VALID FORM
  // ═══════════════════════════════════════════════════════════════════════════

  it("should return no errors for valid form data", () => {
    const errors = validateForm(validData);
    expect(errors).toHaveLength(0);
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // EMAIL VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("email validation", () => {
    it("should require email", () => {
      const errors = validateForm({ ...validData, email: "" });
      expect(errors).toContainEqual({ field: "email", message: "Email is required" });
    });

    it("should reject invalid email format", () => {
      const errors = validateForm({ ...validData, email: "not-an-email" });
      expect(errors).toContainEqual({ field: "email", message: "Invalid email format" });
    });

    it("should reject email without @", () => {
      const errors = validateForm({ ...validData, email: "useratexample.com" });
      expect(errors).toContainEqual({ field: "email", message: "Invalid email format" });
    });

    it("should reject email without domain", () => {
      const errors = validateForm({ ...validData, email: "user@" });
      expect(errors).toContainEqual({ field: "email", message: "Invalid email format" });
    });

    it("should accept valid email", () => {
      const errors = validateForm({ ...validData, email: "user@sahool.com" });
      const emailErrors = errors.filter((e) => e.field === "email");
      expect(emailErrors).toHaveLength(0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FIRST NAME VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("first name validation", () => {
    it("should require first name", () => {
      const errors = validateForm({ ...validData, firstName: "" });
      expect(errors).toContainEqual({ field: "firstName", message: "First name is required" });
    });

    it("should require at least 2 characters", () => {
      const errors = validateForm({ ...validData, firstName: "A" });
      expect(errors).toContainEqual({
        field: "firstName",
        message: "First name must be at least 2 characters",
      });
    });

    it("should reject whitespace-only first name", () => {
      const errors = validateForm({ ...validData, firstName: "   " });
      expect(errors).toContainEqual({ field: "firstName", message: "First name is required" });
    });

    it("should accept valid Arabic first name", () => {
      const errors = validateForm({ ...validData, firstName: "أحمد" });
      const nameErrors = errors.filter((e) => e.field === "firstName");
      expect(nameErrors).toHaveLength(0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // LAST NAME VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("last name validation", () => {
    it("should require last name", () => {
      const errors = validateForm({ ...validData, lastName: "" });
      expect(errors).toContainEqual({ field: "lastName", message: "Last name is required" });
    });

    it("should require at least 2 characters", () => {
      const errors = validateForm({ ...validData, lastName: "B" });
      expect(errors).toContainEqual({
        field: "lastName",
        message: "Last name must be at least 2 characters",
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PASSWORD VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("password validation", () => {
    it("should require password", () => {
      const errors = validateForm({ ...validData, password: "", confirmPassword: "" });
      expect(errors).toContainEqual({ field: "password", message: "Password is required" });
    });

    it("should require at least 8 characters", () => {
      const errors = validateForm({ ...validData, password: "Short1", confirmPassword: "Short1" });
      expect(errors).toContainEqual({
        field: "password",
        message: "Password must be at least 8 characters",
      });
    });

    it("should require uppercase letter", () => {
      const errors = validateForm({
        ...validData,
        password: "alllowercase1",
        confirmPassword: "alllowercase1",
      });
      expect(errors).toContainEqual({
        field: "password",
        message: "Password must contain uppercase, lowercase, and number",
      });
    });

    it("should require lowercase letter", () => {
      const errors = validateForm({
        ...validData,
        password: "ALLUPPERCASE1",
        confirmPassword: "ALLUPPERCASE1",
      });
      expect(errors).toContainEqual({
        field: "password",
        message: "Password must contain uppercase, lowercase, and number",
      });
    });

    it("should require digit", () => {
      const errors = validateForm({
        ...validData,
        password: "NoDigitsHere",
        confirmPassword: "NoDigitsHere",
      });
      expect(errors).toContainEqual({
        field: "password",
        message: "Password must contain uppercase, lowercase, and number",
      });
    });

    it("should accept strong password", () => {
      const errors = validateForm({
        ...validData,
        password: "StrongPass1",
        confirmPassword: "StrongPass1",
      });
      const pwErrors = errors.filter((e) => e.field === "password");
      expect(pwErrors).toHaveLength(0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CONFIRM PASSWORD VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("confirm password validation", () => {
    it("should require confirmation", () => {
      const errors = validateForm({ ...validData, confirmPassword: "" });
      expect(errors).toContainEqual({
        field: "confirmPassword",
        message: "Please confirm your password",
      });
    });

    it("should reject mismatched passwords", () => {
      const errors = validateForm({
        ...validData,
        password: "SecurePass1",
        confirmPassword: "DifferentPass1",
      });
      expect(errors).toContainEqual({
        field: "confirmPassword",
        message: "Passwords do not match",
      });
    });

    it("should accept matching passwords", () => {
      const errors = validateForm({
        ...validData,
        password: "SecurePass1",
        confirmPassword: "SecurePass1",
      });
      const confirmErrors = errors.filter((e) => e.field === "confirmPassword");
      expect(confirmErrors).toHaveLength(0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PHONE VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("phone validation", () => {
    it("should accept empty phone (optional field)", () => {
      const errors = validateForm({ ...validData, phone: "" });
      const phoneErrors = errors.filter((e) => e.field === "phone");
      expect(phoneErrors).toHaveLength(0);
    });

    it("should reject invalid phone format", () => {
      const errors = validateForm({ ...validData, phone: "abc" });
      expect(errors).toContainEqual({
        field: "phone",
        message: "Invalid phone number format",
      });
    });

    it("should reject too-short phone number", () => {
      const errors = validateForm({ ...validData, phone: "12345" });
      expect(errors).toContainEqual({
        field: "phone",
        message: "Invalid phone number format",
      });
    });

    it("should accept valid phone with international prefix", () => {
      const errors = validateForm({ ...validData, phone: "+966551234567" });
      const phoneErrors = errors.filter((e) => e.field === "phone");
      expect(phoneErrors).toHaveLength(0);
    });

    it("should accept valid phone with dashes", () => {
      const errors = validateForm({ ...validData, phone: "055-123-4567" });
      const phoneErrors = errors.filter((e) => e.field === "phone");
      expect(phoneErrors).toHaveLength(0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MULTIPLE ERRORS
  // ═══════════════════════════════════════════════════════════════════════════

  describe("multiple validation errors", () => {
    it("should return all errors for completely empty form", () => {
      const errors = validateForm({
        email: "",
        password: "",
        confirmPassword: "",
        firstName: "",
        lastName: "",
        phone: "",
      });

      expect(errors.length).toBeGreaterThanOrEqual(5);
      expect(errors.some((e) => e.field === "email")).toBe(true);
      expect(errors.some((e) => e.field === "firstName")).toBe(true);
      expect(errors.some((e) => e.field === "lastName")).toBe(true);
      expect(errors.some((e) => e.field === "password")).toBe(true);
      expect(errors.some((e) => e.field === "confirmPassword")).toBe(true);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// ERROR MESSAGE EXTRACTION
// ═══════════════════════════════════════════════════════════════════════════════

describe("RegisterClient - getErrorMessage", () => {
  it("should extract message from standard Error", () => {
    const error = new Error("Something went wrong");
    expect(getErrorMessage(error)).toBe("Something went wrong");
  });

  it("should extract message from axios-style error", () => {
    const error = new Error("Request failed");
    (error as any).response = { data: { message: "Email already exists" } };
    expect(getErrorMessage(error)).toBe("Email already exists");
  });

  it("should extract detail from axios-style error", () => {
    const error = new Error("Request failed");
    (error as any).response = { data: { detail: "Duplicate email" } };
    expect(getErrorMessage(error)).toBe("Duplicate email");
  });

  it("should prefer message over detail", () => {
    const error = new Error("Request failed");
    (error as any).response = { data: { message: "msg", detail: "det" } };
    expect(getErrorMessage(error)).toBe("msg");
  });

  it("should return default for non-Error values", () => {
    expect(getErrorMessage("string error")).toBe("Registration failed. Please try again.");
    expect(getErrorMessage(null)).toBe("Registration failed. Please try again.");
    expect(getErrorMessage(undefined)).toBe("Registration failed. Please try again.");
    expect(getErrorMessage(42)).toBe("Registration failed. Please try again.");
  });
});
