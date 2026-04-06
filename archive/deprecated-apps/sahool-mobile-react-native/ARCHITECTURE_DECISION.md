# sahool-mobile (React Native) — Architectural Decision Required

> **Status:** ⚠️ PENDING DECISION  
> **Last Updated:** 2026-04-04

## What is this path?

`sahool-mobile` is a React Native project containing a well-implemented
offline sync manager (`syncManager.ts`) with good test coverage (~80%).
However, it lacks an app shell, UI components, navigation, and platform setup.

## Current Implementation

| Aspect | Status |
|--------|--------|
| Sync Manager | ✅ Complete (1,432 lines) |
| Type Definitions | ✅ Complete (426 lines) |
| Tests | ✅ Good (~526 lines, ~80% coverage of sync) |
| Documentation | ✅ Comprehensive |
| App Shell (App.tsx) | ❌ Missing |
| UI Components | ❌ Missing |
| Navigation | ❌ Missing |
| API Client | ❌ Missing |
| Platform Setup | ❌ Missing |
| .env Config | ⚠️ Added `.env.example` in this update |

## Decision Required

**One of the following must be chosen:**

| Option | Description | Effort |
|--------|-------------|--------|
| **A. Continue** | Build this into a full React Native app with clear roadmap | 4–6 weeks to functional app |
| **B. Extract & Merge** | Extract `syncManager` as a standalone package; archive the rest | 1 week |
| **C. Freeze** | Stop development; keep as-is for reference | 0 effort |
| **D. Archive** | Move to `archive/deprecated-mobile/sahool-mobile` | 1 day |

## Recommendation

Given that the platform's primary mobile stack is **Flutter** (3 Flutter apps exist),
maintaining a parallel React Native path creates:
- Split team expertise
- Duplicate sync/offline implementations
- Divergent UI/UX patterns

**Recommended: Option B or D** — Extract the sync logic if valuable, then archive.

## Risks of Not Deciding

- Ambiguous project status blocks resource allocation
- New developers don't know if they should contribute here
- CI/CD pipeline treats this as an active project unnecessarily

## Next Steps

1. Engineering lead selects Option A, B, C, or D
2. Update this file with the decision
3. If A: add to CI pipeline and create development roadmap
4. If B: extract syncManager to a shared package
5. If C/D: update CI to skip this directory
