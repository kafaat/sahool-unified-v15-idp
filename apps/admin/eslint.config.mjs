import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    rules: {
      // Downgrade TypeScript rules to warnings for existing code
      "@typescript-eslint/no-unused-vars": "warn",
      "@typescript-eslint/no-explicit-any": "warn",
      // Disable rules that have compatibility issues with current ESLint version
      "@typescript-eslint/no-unused-expressions": "off",
      "@typescript-eslint/no-unsafe-declaration-merging": "off",
    },
  },
];

export default eslintConfig;
