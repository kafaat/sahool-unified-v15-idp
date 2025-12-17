/**
 * Jest E2E Configuration
 * تكوين Jest للاختبارات الشاملة
 */
module.exports = {
  displayName: 'e2e',
  testEnvironment: 'node',
  rootDir: '..',
  testMatch: ['<rootDir>/tests/e2e/**/*.e2e.spec.ts'],
  transform: {
    '^.+\\.(t|j)s$': 'ts-jest',
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/services/research_core/src/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup/e2e.setup.ts'],
  testTimeout: 30000,
  verbose: true,
  collectCoverage: false,
  coverageDirectory: '<rootDir>/coverage/e2e',
  coverageReporters: ['text', 'lcov', 'html'],
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: '<rootDir>/test-results/e2e',
        outputName: 'junit.xml',
      },
    ],
  ],
  globals: {
    'ts-jest': {
      tsconfig: '<rootDir>/services/research_core/tsconfig.json',
    },
  },
  // Retry failed tests once
  retryTimes: 1,
  // Max workers for parallel execution
  maxWorkers: 2,
  // Force exit after tests complete
  forceExit: true,
  // Detect open handles
  detectOpenHandles: true,
};
