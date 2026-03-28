// Ensure Redis client is created in tests (so ioredis mocks work)
process.env.REDIS_HOST = process.env.REDIS_HOST || "localhost";

/** @type {import('jest').Config} */
module.exports = {
  moduleFileExtensions: ["js", "json", "ts"],
  rootDir: ".",
  testRegex: ".*\\.spec\\.ts$",
  transform: {
    "^.+\\.(t|j)s$": ["ts-jest", {
      tsconfig: {
        paths: {
          "@sahool/shared-events": ["../../../packages/shared-events/src/index.ts"],
        },
      },
    }],
  },
  collectCoverageFrom: ["src/**/*.(t|j)s"],
  coverageDirectory: "./coverage",
  testEnvironment: "node",
  roots: ["<rootDir>/test/", "<rootDir>/src/"],
  moduleNameMapper: {
    "^src/(.*)$": "<rootDir>/src/$1",
    "^@sahool/shared-events$": "<rootDir>/../../../packages/shared-events/src/index.ts",
  },
};
