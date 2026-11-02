# Dependency PR consolidation — 2026-11-02

## Scope and current base

This change repairs dependency compatibility and security regressions discovered while reviewing the repository's **12 initially open Dependabot PRs**. The original inventory is in [source-prs.json](source-prs.json); [live-source-prs.json](live-source-prs.json) records the state observed before publication.

During review, six source PRs were merged independently into `main`. This work did not perform those merges. The consolidated candidate includes main commit `0f17b625047ea6d5108f42a240d507d7c855c912`. Its reconciliation preserved every newly merged dependency update without changing the already tested candidate tree; see [main-reconciliation.json](main-reconciliation.json).

**The requested Flutter major upgrades are deferred.** This PR supplies verified compatibility bounds and mandatory checks for the current generator/SQLCipher stack. It does not represent completion of a Riverpod/Freezed/sqlite3 major migration.

## Disposition of the source PRs

| Source | State observed before publication | Consolidated result |
| --- | --- | --- |
| #1822 | Open | Replace incompatible Flutter upgrade ranges with tested bounds. Retain Drift 2.28.2, drift_dev 2.28.0, Riverpod generator 2.6.4, annotation/flutter_riverpod 2.6.x, Freezed 2.5.8 and sqlite3 2.9.4. Major migration deferred. |
| #2009 | Open | Regenerate inconsistent npm locks; use compatible patched Nest 10.4.22/cache-manager 2.3.0, Express 4.22.3, body-parser 1.20.9/2.4.0 and Vitest 4.1.12. Repair affected mocks and service test lifecycle. |
| #2017 | Merged independently | Preserve Vite 7.3.7 and synchronize all affected workspace manifests and locks. |
| #2018 | Open | FastAPI 0.162.0, Uvicorn >=0.54.0, Pydantic 2.14.2; synchronize service pins with central constraints. |
| #2019 | Merged independently | Preserve Qdrant client >=1.20; migrate three real consumers to `query_points` and repair collection statistics. |
| #2020 | Open | Certifi >=2026.10.23 in central/copied constraints, root declaration and frozen lock. |
| #2021 | Merged independently | Preserve Anthropic >=2.3,<3; align LangChain >=1.7.9,<2 and repair four SDK consumers while retaining API version 2023-06-01. |
| #2022 | Merged independently | Preserve pytest-html >=4.2 and exercise real report generation. |
| #2023 | Open; rebased during review | Include all 13 proposed upgrades, regenerate `uv.lock`, align service/CI pins and update OTel instrumentation to 0.66b2 for SDK 1.45.2. The rebased head `3796fd148ab93e569005c48788189aca61868ddd` was checked against the candidate. |
| #2024 | Open | Vulture >=2.16; resolve complete development requirements with pytest-asyncio 1.3.0 and pytest 9.2.0. |
| #2025 | Merged independently | Preserve SciPy >=1.17.1,<1.18 and synchronize field constraints; test real numerical execution. |
| #2026 | Merged independently | Preserve central Qdrant client >=1.20 and align the service manifests and CI server image. |

The npm proposals' incompatible Nest 12/cache-manager 12 and Vitest 5 upgrades are replaced with patched, tested versions that preserve the project's current Nest and Node 20 contracts.

## Defects repaired

### JavaScript dependency and runtime failures

The #2009 manifests and workspace lock disagreed, causing `npm ci` failures. The rebuilt root and affected standalone locks install consistently. All 15 tracked npm locks were inspected for the targeted packages; all 12 body-parser resolutions are on patched releases. Untouched standalone lock metadata is not claimed to have been fully synchronized.

The added runtime security tests exercise actual installed packages. They demonstrate that trailing bytes after a gzip request no longer crash body-parser, and that Vitest's mock generator safely quotes module URLs and export names. The same source fails against body-parser 1.20.8/Vitest 3.2.7 and passes against patched installations. The parser 2.4.0 case uses the actual code-review-agent standalone manifest and lock.

Constructor mocks now use constructible functions. Chat testing modules close their real interval handles. Marketplace's NATS readiness fixture restores the original environment and explicitly checks the unconfigured state.

### Python SDK and resolver failures

Qdrant 1.20 removed the old search method and collection field. Real in-memory acceptance tests verify retrieval, tenant/metadata filtering, top-k, thresholds, returned vectors/ranks and statistics. Copilot's keyword fallback is cleared during acceptance so it cannot conceal an SDK failure. Agent Evaluation's Qdrant image is aligned with the existing repository server version 1.10.1, which supports the Query API.

Anthropic SDK 2 defaults to an API that rejects the existing sampling parameters. Following the [official migration guide](https://platform.claude.com/docs/en/api/migration-2026-10-21), all four consumers explicitly retain `anthropic-version: 2023-06-01`. The direct SDK call passes temperature through `extra_body`; the compatible LangChain release handles its own SDK adaptation. Tests inspect actual generated request bodies and headers and invoke the real agent/router/vision methods with local HTTP mock transports and blocked sockets. Model, max-token, system/message, sampling and token-accounting behavior are preserved.

This is an SDK upgrade with the supported older API contract. It does not claim migration to API 2026-10-21.

Central constraints, copied field constraints, affected service pins and CI installs are synchronized. OTel instrumentation 0.66b2 is required by the upgraded SDK's semantic-conventions dependency. The stale root lock is regenerated.

### Flutter compatibility boundaries

The requested sqlite3 major removes an import used by the current SQLCipher binding. Newer drift_dev releases also require generator dependencies incompatible with the project's Freezed/Riverpod stack. Actual resolution showed that even Riverpod generator 2.6.5 introduces an incompatible transitive Freezed annotation dependency.

The tested manifest bounds cover the main app, field app and shared core. The policy checks also inspect the path-consuming app, three application locks, dependency overrides and transitive analyzer/build/source_gen/Riverpod boundaries. The Mobile CI analysis job runs these checks as a mandatory step. Dependabot remains enabled for compatible updates.

See [the toolchain decision](../../../mobile/FLUTTER_TOOLCHAIN.md) and [the final guard receipt](flutter/flutter-review-guard-receipt.json). The earlier [Flutter decision receipt](flutter-pr1822-decision.json) describes the initial 41-case stage; the final integrated guard suite contains **86 passing cases**.

## Local verification

| Verification | Result |
| --- | --- |
| Node 20.20.2 / npm 10.9.0 application and existing security suites | **6,063 distinct tests passed**: root 2,793; admin 2,515; code-review 90; chat 278; marketplace 356; existing security gate 31. |
| Added JavaScript runtime security cases | **4 passed**, included in the consolidated **35/35** security run; also exercised against the real parser 2.4.0 standalone lock. |
| Root frozen Python lock/runtime | **102 passed**, repeated successfully on the final integration. |
| Shared authentication/security and Copilot authentication | **162 + 11 passed**. |
| AI SDK, Qdrant, numerical and CPU embedding acceptance | **16 passed** on genuine Anthropic 2.4.0 and 2.3.0 installations; repeated on the final integration with 2.3.0. |
| Flutter toolchain/dependency policy | **86 passed** on the final integrated constraints and sources. |
| Flutter native compatibility tests | **2 passed**; actual code generation succeeded with 373 outputs. |
| Frozen dependency checks | Actual root npm install; targeted standalone frozen checks; frozen Python lock with 115 packages; Flutter main/field lock-preserving resolution and shared-core resolution. |
| Builds/static analysis | Shared packages/events, admin Storybook, Chat/Marketplace Nest builds, code-review, web and admin TypeScript; full Python Ruff check and zero Python dependency-drift errors. |

The Python suites contain **291 distinct cases**. Repeated environments/integration runs and repeated shared-hook/UI coverage cases are not counted again.

The root and AI Python environment audits covered **110 and 86 packages**, respectively, with **zero known vulnerabilities and zero skipped packages**. The npm audit is **not clean**: the complete workspace audit changed from 114 findings (19 high) to **107 findings (17 high, 79 moderate, 11 low)** relative to the initial main commit. No new direct advisory was introduced. Counts include npm's dependent-package propagation and are not a count of unique CVEs. Full reports and the advisory comparison are included.

### Negative controls

| Control | Before repair | After repair |
| --- | --- | --- |
| body-parser/Vitest runtime cases | 3 failures out of 4 | 4 passed |
| Targeted parser checks across all tracked locks | 5 failures out of 31 | 31 passed |
| Qdrant consumers | 5 failures | All 5 included cases passed |
| Anthropic SDK consumers | 5 failures | All 5 included cases passed |
| Additional Flutter transitive override/lock cases | 10 failures | All 10 included cases passed |
| Frozen root Python lock | Rejected as stale | Accepted |

## Evidence and verification limits

[SHA256SUMS.json](SHA256SUMS.json) hashes the evidence files. [integration-validation.json](integration-validation.json) binds the final integration checks to the tested code and verifies that the independent reviews' source hashes still match. The Python, Node, Flutter and JavaScript receipts preserve source PR heads, package versions, commands/results and known limitations.

Local Python execution used 3.12.14. Complete service requirements were resolved for 3.11, while the PR workflow provides runtime checks for 3.11/3.12/3.13. This receipt predates GitHub CI for the published PR; consult the checks on its current head.

No live provider inference, remote Qdrant server, deployment, Android/iOS application build or encrypted-database major migration was performed. The existing npm audit backlog and the separate Flutter major migration remain visible follow-up work.
