/// <reference types="vitest" />
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/__tests__/setup.ts"],
    include: ["src/**/*.{test,spec}.{js,ts,tsx}"],
    coverage: {
      reporter: ["text", "json", "html"],
      exclude: ["node_modules/", "src/__tests__/setup.ts"],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@sahool/shared-ui": path.resolve(__dirname, "../../packages/shared-ui/src"),
      "@sahool/ui": path.resolve(__dirname, "../../packages/shared-ui/src"),
      "@sahool/shared-hooks": path.resolve(__dirname, "../../packages/shared-hooks/src"),
      "@sahool/hooks": path.resolve(__dirname, "../../packages/shared-hooks/src"),
      "@sahool/shared-utils": path.resolve(__dirname, "../../packages/shared-utils/src"),
      "@sahool/utils": path.resolve(__dirname, "../../packages/shared-utils/src"),
      "@sahool/api-client": path.resolve(__dirname, "../../packages/api-client/src"),
      "@sahool/api": path.resolve(__dirname, "../../packages/api-client/src"),
      "@sahool/i18n": path.resolve(__dirname, "../../packages/i18n/src"),
      "@sahool/shared-types/contracts": path.resolve(__dirname, "../../packages/shared-types/src/contracts"),
      "@sahool/shared-types": path.resolve(__dirname, "../../packages/shared-types/src"),
    },
  },
});
