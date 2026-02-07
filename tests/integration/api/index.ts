/**
 * SAHOOL API Integration Tests Index
 * فهرس اختبارات تكامل API لمنصة سهول
 *
 * This module exports all API integration test utilities and configurations.
 * These tests verify that all services are properly registered and responding
 * through Kong API Gateway.
 *
 * Test Files:
 * - auth-flow.test.ts: Authentication flow tests (registration, login, JWT, OTP)
 * - field-management.test.ts: Field CRUD operations with GeoJSON support
 * - weather-integration.test.ts: Weather data and forecast API tests
 * - irrigation-advisory.test.ts: Smart irrigation recommendations
 * - ai-services.test.ts: Vision, crop health, yield prediction, advisory AI
 * - notification.test.ts: Notification delivery and preferences
 *
 * @author SAHOOL Platform Team
 * @version 16.0.0
 */

// Re-export all setup utilities
export * from "./setup";

// Test module information
export const API_INTEGRATION_TESTS = {
  version: "16.0.0",
  testFiles: [
    "auth-flow.test.ts",
    "field-management.test.ts",
    "weather-integration.test.ts",
    "irrigation-advisory.test.ts",
    "ai-services.test.ts",
    "notification.test.ts",
  ],
  services: [
    { name: "user-service", port: 3025, type: "nestjs" },
    { name: "field-management-service", port: 3000, type: "nestjs" },
    { name: "weather-service", port: 8092, type: "python" },
    { name: "irrigation-smart", port: 8094, type: "python" },
    { name: "yolo26-vision-service", port: 8150, type: "python" },
    { name: "crop-intelligence-service", port: 8095, type: "python" },
    { name: "yield-engine", port: 8098, type: "python" },
    { name: "advisory-service", port: 8093, type: "python" },
    { name: "notification-service", port: 8110, type: "python" },
  ],
  description: {
    en: "Comprehensive API integration tests for SAHOOL platform services through Kong Gateway",
    ar: "اختبارات تكامل API شاملة لخدمات منصة سهول عبر بوابة Kong",
  },
};

/**
 * Run all API integration tests
 * Usage: npx vitest run tests/integration/api/
 */
export function getTestInfo(): typeof API_INTEGRATION_TESTS {
  return API_INTEGRATION_TESTS;
}
