import tseslint from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import nextPlugin from "@next/eslint-plugin-next";

/**
 * ESLint 9.x flat config for Next.js Web Application
 * Using native flat config to avoid compatibility issues with eslint-plugin-react and ESLint 9.x
 * TypeScript errors are primarily caught by `npm run typecheck`
 */
const eslintConfig = [
  js.configs.recommended,
  {
    ignores: [
      ".next/**",
      "node_modules/**",
      "out/**",
      "coverage/**",
      "*.config.js",
      "*.config.mjs",
    ],
  },
  {
    files: ["**/*.ts", "**/*.tsx"],
    plugins: {
      "@typescript-eslint": tseslint,
      "react-hooks": reactHooks,
      "@next/next": nextPlugin,
    },
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        ...globals.browser,
        ...globals.node,
        React: "readonly",
        JSX: "readonly",
      },
    },
    rules: {
      // Turn off rules that TypeScript handles
      "no-unused-vars": "off",
      "no-undef": "off", // TypeScript handles this

      // TypeScript-specific rules (relaxed for now)
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-unused-expressions": "off",
      "@typescript-eslint/ban-ts-comment": "off",
      "@typescript-eslint/no-empty-object-type": "off",

      // React hooks rules
      "react-hooks/exhaustive-deps": "warn",
      "react-hooks/rules-of-hooks": "error",

      // Next.js rules (defined so eslint-disable comments work)
      "@next/next/no-page-custom-font": "off",
      "@next/next/no-img-element": "off",

      // Enforce unified API contracts - import from @sahool/shared-types/contracts
      "no-restricted-imports": [
        "warn",
        {
          patterns: [
            {
              group: ["**/service-ports*", "**/error-codes*"],
              message:
                "Import service ports and error codes from @sahool/shared-types/contracts instead of local definitions.",
            },
          ],
        },
      ],
    },
  },
  {
    files: ["**/*.js", "**/*.mjs"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.node,
      },
    },
  },
];

export default eslintConfig;
