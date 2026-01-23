/**
 * Tests for SAHOOL Event Subjects
 * اختبارات موضوعات أحداث سهول
 */

import { describe, it, expect } from "vitest";
import {
  // Subject constants
  EventSubjects,
  SAHOOL_FIELD_CREATED,
  SAHOOL_FIELD_UPDATED,
  SAHOOL_FIELD_DELETED,
  SAHOOL_WEATHER_ALERT,
  SAHOOL_BILLING_PAYMENT_COMPLETED,

  // Utility functions
  getSubjectForEvent,
  getWildcardSubject,
  isValidSubject,
  getTenantSubject,
  getTenantWildcard,
  extractDomain,
} from "../subjects";

describe("Subject Constants", () => {
  it("should have correct field subjects", () => {
    expect(SAHOOL_FIELD_CREATED).toBe("sahool.field.created");
    expect(SAHOOL_FIELD_UPDATED).toBe("sahool.field.updated");
    expect(SAHOOL_FIELD_DELETED).toBe("sahool.field.deleted");
  });

  it("should have correct weather subjects", () => {
    expect(SAHOOL_WEATHER_ALERT).toBe("sahool.weather.alert");
  });

  it("should have correct billing subjects", () => {
    expect(SAHOOL_BILLING_PAYMENT_COMPLETED).toBe("sahool.billing.payment.completed");
  });

  it("should expose EventSubjects object with all subjects", () => {
    expect(EventSubjects.FIELD_CREATED).toBe("sahool.field.created");
    expect(EventSubjects.WEATHER_ALERT).toBe("sahool.weather.alert");
    expect(EventSubjects.BILLING_PAYMENT_COMPLETED).toBe("sahool.billing.payment.completed");
    expect(EventSubjects.IOT_SENSOR_READING).toBe("sahool.iot.sensor.reading");
    expect(EventSubjects.AGENT_EXECUTION_STARTED).toBe("sahool.agent.execution.started");
  });
});

describe("getSubjectForEvent", () => {
  it("should add sahool prefix to event type", () => {
    expect(getSubjectForEvent("field.created")).toBe("sahool.field.created");
  });

  it("should not double-prefix if already has sahool prefix", () => {
    expect(getSubjectForEvent("sahool.field.created")).toBe("sahool.field.created");
  });

  it("should work with complex event types", () => {
    expect(getSubjectForEvent("billing.payment.completed")).toBe(
      "sahool.billing.payment.completed"
    );
  });
});

describe("getWildcardSubject", () => {
  it("should create wildcard subject for domain", () => {
    expect(getWildcardSubject("field")).toBe("sahool.field.*");
    expect(getWildcardSubject("weather")).toBe("sahool.weather.*");
    expect(getWildcardSubject("billing")).toBe("sahool.billing.*");
  });
});

describe("isValidSubject", () => {
  it("should validate correct subjects", () => {
    expect(isValidSubject("sahool.field.created")).toBe(true);
    expect(isValidSubject("sahool.weather.alert.frost")).toBe(true);
    expect(isValidSubject("sahool.billing.payment.completed")).toBe(true);
  });

  it("should reject subjects without sahool prefix", () => {
    expect(isValidSubject("field.created")).toBe(false);
    expect(isValidSubject("weather.alert")).toBe(false);
  });

  it("should reject subjects with insufficient parts", () => {
    expect(isValidSubject("sahool.field")).toBe(false);
    expect(isValidSubject("sahool")).toBe(false);
  });
});

describe("getTenantSubject", () => {
  it("should create tenant-scoped subject", () => {
    expect(getTenantSubject("org_123", "field", "created")).toBe(
      "sahool.tenant.org_123.field.created"
    );
  });

  it("should work with different domains and actions", () => {
    expect(getTenantSubject("org_123", "billing", "payment.completed")).toBe(
      "sahool.tenant.org_123.billing.payment.completed"
    );
  });

  it("should throw for empty tenant ID", () => {
    expect(() => getTenantSubject("", "field", "created")).toThrow();
  });
});

describe("getTenantWildcard", () => {
  it("should create wildcard for all tenant events", () => {
    expect(getTenantWildcard("org_123")).toBe("sahool.tenant.org_123.>");
  });

  it("should create wildcard for specific domain", () => {
    expect(getTenantWildcard("org_123", "field")).toBe("sahool.tenant.org_123.field.*");
  });

  it("should throw for empty tenant ID", () => {
    expect(() => getTenantWildcard("")).toThrow();
  });
});

describe("extractDomain", () => {
  it("should extract domain from standard subject", () => {
    expect(extractDomain("sahool.field.created")).toBe("field");
    expect(extractDomain("sahool.weather.alert.frost")).toBe("weather");
    expect(extractDomain("sahool.billing.payment.completed")).toBe("billing");
  });

  it("should extract domain from tenant-scoped subject", () => {
    expect(extractDomain("sahool.tenant.org_123.field.created")).toBe("field");
    expect(extractDomain("sahool.tenant.org_123.billing.payment.completed")).toBe("billing");
  });

  it("should return null for invalid subjects", () => {
    expect(extractDomain("invalid.subject")).toBe(null);
    expect(extractDomain("field.created")).toBe(null);
  });
});
