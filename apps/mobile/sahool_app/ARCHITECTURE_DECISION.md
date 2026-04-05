# sahool_app — Architectural Decision Required

> **Status:** ⚠️ PENDING DECISION  
> **Last Updated:** 2026-04-04

## What is this app?

`sahool_app` is a lightweight Flutter entry point that wraps `sahool_mobile_core`.
It bootstraps crash reporting, error handling, security, and routing
from an external package, but contains no feature screens of its own.

## Current Implementation

- `lib/main.dart` — Full app bootstrap with security, crash reporting, sync engine
- `lib/app.dart` — App shell using `GoRouter` from `sahool_mobile_core`
- Environment files: `.env.development`, `.env.staging`, `.env.production`
- **No platform directories** (android/ios/web) within this directory
- **No feature screens** — all UI comes from the core package

## Decision Required

**One of the following must be chosen before any further investment:**

| Option | Description | Impact |
|--------|-------------|--------|
| **A. Successor App** | This becomes the unified mobile product, replacing `sahool_field_app` over time | Requires migrating all `sahool_field_app` features into `sahool_mobile_core` |
| **B. Wrapper / Launcher** | Stays as a thin bootstrap layer for testing the core package | No new features added here; `sahool_field_app` remains the production app |
| **C. Experimental Track** | Internal sandbox for testing new architecture patterns | Clearly labeled non-production; no overlap with production features |

## Risks of Not Deciding

- Duplicate development effort across `sahool_field_app` and `sahool_app`
- Confusion about which app is the production baseline
- CI/CD pipeline uncertainty about which app to build and release

## Relationship with sahool_field_app

`sahool_field_app` is currently the **production reference app** for mobile.
Any work on `sahool_app` must not create feature overlap or split the team's focus
until an explicit decision is documented here.

## Next Steps

1. Product owner selects Option A, B, or C above
2. Update this README with the decision and rationale
3. If Option A: create a migration plan from `sahool_field_app`
4. If Option B or C: freeze feature development and document scope limits
