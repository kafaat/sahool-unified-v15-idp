# @sahool/typescript-config

Shared TypeScript `tsconfig.json` base configurations for all SAHOOL frontend packages and applications. Enforces strict type checking, consistent module resolution, and target compatibility across the monorepo.

## Installation

```bash
npm install --save-dev @sahool/typescript-config
```

## Available Configurations

| Config | Extends | Use For |
|--------|---------|---------|
| `base.json` | — | Shared packages, libraries, Node.js utilities |
| `nextjs.json` | `base.json` | Next.js 15.x apps (`apps/web`, `apps/admin`) |
| `react-library.json` | `base.json` | React component packages (`shared-ui`, `design-system`) |

## Usage

### Next.js Application

```json
{
  "extends": "@sahool/typescript-config/nextjs.json",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

### Shared Library / Package

```json
{
  "extends": "@sahool/typescript-config/base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

### React Component Library

```json
{
  "extends": "@sahool/typescript-config/react-library.json",
  "compilerOptions": {
    "outDir": "./dist"
  }
}
```

## Compiler Options Summary

### base.json

| Option | Value | Rationale |
|--------|-------|-----------|
| `target` | `ES2020` | Supported by Node.js 20+ and modern browsers |
| `module` | `ESNext` | Tree-shakeable ESM output |
| `moduleResolution` | `bundler` | Vite/tsup/Next.js bundler-compatible |
| `strict` | `true` | Enables all strict flags |
| `strictNullChecks` | `true` | Prevents null dereference errors |
| `noImplicitAny` | `true` | Requires explicit types |
| `noImplicitReturns` | `true` | All code paths must return |
| `noFallthroughCasesInSwitch` | `true` | Prevents accidental switch fallthrough |
| `noUncheckedIndexedAccess` | `true` | Index access returns `T \| undefined` |
| `isolatedModules` | `true` | Required for esbuild/tsup compatibility |
| `declaration` | `true` | Generates `.d.ts` files |
| `declarationMap` | `true` | Source maps for declarations |
| `sourceMap` | `true` | Runtime source maps |

### nextjs.json additions

- `target: ES2017` (Next.js preferred)
- `jsx: preserve` (Next.js handles JSX transform)
- `noEmit: true` (Next.js compiles, not tsc)
- `incremental: true` (faster rebuilds)
- `plugins: [{ name: "next" }]` (Next.js language server plugin)

## Node.js Requirement

All configurations require Node.js >= 20.0.0.
