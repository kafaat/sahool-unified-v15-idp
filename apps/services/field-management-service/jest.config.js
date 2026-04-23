/** @type {import('jest').Config} */
const path = require("path");

module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/tests", "<rootDir>/src"],
  testMatch: ["**/*.spec.ts", "**/*.test.ts"],
  moduleFileExtensions: ["ts", "js", "json"],
  collectCoverageFrom: ["src/**/*.ts", "!src/**/*.d.ts"],
  coverageDirectory: "coverage",
  verbose: true,
  globals: {
    "ts-jest": {
      // Use the test-specific tsconfig that adds monorepo package paths.
      // Absolute path is required because Jest runs from the monorepo root.
      tsconfig: path.join(__dirname, "tsconfig.test.json"),
    },
  },
  moduleNameMapper: {
    "^@sahool/field-shared$": "<rootDir>/../../../packages/field-shared/src/index.ts",
    "^@sahool/shared-events$": "<rootDir>/tests/__mocks__/shared-events.js",
    // keyv is a transitive dep of @nestjs/cache-manager that is not installed
    // in the dev environment.  Stub both packages so cache.service.ts can be
    // imported in unit/integration tests that mock CacheService directly.
    "^@nestjs/cache-manager$": "<rootDir>/tests/__mocks__/cache-manager.js",
    "^cache-manager$": "<rootDir>/tests/__mocks__/cache-manager.js",
  },
};
