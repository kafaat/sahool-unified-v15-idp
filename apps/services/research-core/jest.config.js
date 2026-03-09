/** @type {import('jest').Config} */
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/test", "<rootDir>/src"],
  testMatch: ["**/*.spec.ts", "**/*.test.ts"],
  moduleFileExtensions: ["ts", "js", "json"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "^@core/(.*)$": "<rootDir>/src/core/$1",
    "^@modules/(.*)$": "<rootDir>/src/modules/$1",
    "^@config/(.*)$": "<rootDir>/src/config/$1",
  },
  collectCoverageFrom: ["src/**/*.ts", "!src/**/*.d.ts"],
  coverageDirectory: "coverage",
  verbose: true,
};
