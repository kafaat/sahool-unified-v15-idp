import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
  resolve: {
    alias: {
      "@sahool/shared-types/contracts": path.resolve(__dirname, "../shared-types/src/contracts"),
      "@sahool/shared-types": path.resolve(__dirname, "../shared-types/src"),
    },
  },
});
