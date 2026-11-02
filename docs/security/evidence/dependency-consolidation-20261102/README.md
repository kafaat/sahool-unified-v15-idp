# Dependency PR consolidation — 2026-11-02

## Scope and current base

This change repairs dependency compatibility and security regressions discovered while reviewing the repository's **12 initially open Dependabot PRs**. The original inventory is in [source-prs.json](source-prs.json); [live-source-prs.json](live-source-prs.json) records the state observed before publication.

During review, six source PRs were merged independently into `main`. This work did not perform those merges. The consolidated candidate includes main commit `0f17b625047ea6d5108f42a240d507d7c855c912`. Its reconciliation preserved every newly merged dependency update without changing the already tested candidate tree; see [main-reconciliation.json](main-reconciliation.json).

**The requested Flutter major upgrades are deferred.** This PR supplies verified compatibility bounds and mandatory checks for the current generator/SQLCipher stack. It does not represent completion of a Riverpod/Freezed/sqlite3 major migration.

**This is not an all-tests-green claim.** Inspection of actual CI logs also established existing field-app Flutter failures and field-management Node test-compilation failures. Their source and lock files match main; the existing jobs misleadingly report success. These baseline limitations are detailed below.

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

### SQLite deletion follow-up from remote security review

Remote Semgrep identified two dynamically constructed deletion statements in the existing SQLite backend. The values were already bound, but inspection also found real FTS ordering, collection-isolation and deletion-count defects. The follow-up uses constant SQL with bound parameters, removes FTS entries while their source rows still exist, restricts both operations to the requested collection, deduplicates IDs and returns the document count. The old suppressions were removed.

The exact official Semgrep rule reports **2 findings before and 0 after**. Real SQLite/FTS tests cover hostile-looking values, cross-collection isolation, duplicate and missing IDs, idempotency, empty batches and bounded parameter counts. The final ten SQLite cases fail six times against the old source and all pass after repair. They now run in the mandatory Python Lock Security job. The integrated SDK/SQLite/embedding suite passes **26/26**; see [the follow-up receipt](python/sqlite-semgrep-followup-receipt.json).

This code repair does not automatically rebuild an already inconsistent persisted FTS index or perform a data migration.

### Flutter compatibility boundaries

The requested sqlite3 major removes an import used by the current SQLCipher binding. Newer drift_dev releases also require generator dependencies incompatible with the project's Freezed/Riverpod stack. Actual resolution showed that even Riverpod generator 2.6.5 introduces an incompatible transitive Freezed annotation dependency.

The tested manifest bounds cover the main app, field app and shared core. The policy checks also inspect the path-consuming app, three application locks, dependency overrides and transitive analyzer/build/source_gen/Riverpod boundaries. The Mobile CI analysis job runs these checks as a mandatory step. Dependabot remains enabled for compatible updates.

See [the toolchain decision](../../../mobile/FLUTTER_TOOLCHAIN.md) and [the final guard receipt](flutter/flutter-review-guard-receipt.json). The earlier [Flutter decision receipt](flutter-pr1822-decision.json) describes the initial 41-case stage; the final integrated guard suite contains **86 passing cases**.

Remote review also exposed a separate analyzer setup defect: Frontend Tests generated only the primary app, then recursively analyzed uninitialized nested apps. Its success fallback hid **3,462 errors**. The follow-up prepares the shared core and both nested apps, then uses explicit Bash/pipefail without that fallback. Actual analysis of the same complete tree now returns **exit 0 and zero errors**, with no new excludes or production Dart changes. Existing warnings/info remain nonfatal. See [the setup receipt](flutter/flutter-ci-setup-receipt.json).

## Local verification

| Verification | Result |
| --- | --- |
| Node 20.20.2 / npm 10.9.0 application and existing security suites | **6,063 distinct tests passed**: root 2,793; admin 2,515; code-review 90; chat 278; marketplace 356; existing security gate 31. |
| Added JavaScript runtime security cases | **4 passed**, included in the consolidated **35/35** security run; also exercised against the real parser 2.4.0 standalone lock. |
| Root frozen Python lock/runtime | **102 passed**, repeated successfully on the final integration. |
| Shared authentication/security and Copilot authentication | **162 + 11 passed**. |
| AI SDK, Qdrant, numerical and CPU embedding acceptance | **16 passed** on genuine Anthropic 2.4.0 and 2.3.0 installations; repeated on the final integration with 2.3.0. |
| SQLite deletion and FTS isolation follow-up | **10 passed**; final integrated AI/SQLite/embedding run **26/26**. |
| Flutter toolchain/dependency policy | **86 passed** on the final integrated constraints and sources. |
| Flutter native compatibility tests | **2 passed**; actual code generation succeeded with 373 outputs. |
| Frozen dependency checks | Actual root npm install; targeted standalone frozen checks; frozen Python lock with 115 packages; Flutter main/field lock-preserving resolution and shared-core resolution. |
| Builds/static analysis | Shared packages/events, admin Storybook, Chat/Marketplace Nest builds, code-review, web and admin TypeScript; full Python Ruff check and zero Python dependency-drift errors. |

The Python suites contain **301 distinct verified cases**, including the ten SQLite cases in the follow-up. Repeated environments/integration runs and repeated shared-hook/UI coverage cases are not counted again.

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
| Exact Semgrep SQL rule on the vector store | 2 findings | 0 findings, 0 errors |
| SQLite deletion/FTS cases | 6 failed, 4 passed | 10 passed |
| Frontend recursive Flutter analyzer setup | 3,462 errors hidden by the workflow | 0 errors with the full scope and a strict exit status |

## Remote CI observations and existing test debt

On first published head `5ae806cd`, the real JavaScript security/browser checks passed; Python frozen extras passed on **3.11/3.12/3.13**; shared-auth passed on **3.11/3.12**; AI SDK/CPU embedding, dependency consistency and Agent Evaluation passed. The primary Flutter app passed **2,723 tests**, and its iOS debug/no-codesign build completed. Follow-up code has separate receipts and requires checks on the final PR head.

Two other suites have verified baseline failures which their existing workflows hide. They are not counted among the passing targeted suites above:

| Existing suite | Actual result on the first published head | Baseline evidence |
| --- | --- | --- |
| Field Flutter app | **4,727 passed / 17 failed**, although the job reports success. Four categories: notifier updates after disposal, empty default tenant, network timeout, shared mutable chat fixture. | A prior run had **4,729 passed / 15 failed** in the same categories, with a different random seed. All 2,439 Dart sources and three app locks match main. [Detailed receipt and job links](flutter/flutter-ci-tests-and-ios.json). |
| Node field-management service | **4 failed / 8 passed suites**; the **107 tests that execute pass**. Four suites fail compilation due to stale task-service arguments and unresolved shared-events output. The workflow emits a warning and reports success. | Main `0f17b625` has the identical compiler diagnostics, suite/test counts and source trees. [Comparison receipt and job links](node/ci-baseline-limitations.json). |

The remaining baseline failures were not hidden, weakened or rewritten as part of the dependency consolidation. Their misleading existing test-step behavior is explicitly recorded rather than inferred from a green GitHub badge.

## Evidence and verification limits

[SHA256SUMS.json](SHA256SUMS.json) hashes the evidence files. [integration-validation.json](integration-validation.json) records the first integrated candidate. [followup-validation.json](followup-validation.json) binds the subsequent SQLite and analyzer fixes to their tested sources and identifies the two historical Python hashes superseded by the follow-up. Historical receipts are preserved. The Python, Node, Flutter and JavaScript receipts retain source PR heads, package versions, commands/results and known limitations.

Local Python execution used 3.12.14. Complete service requirements were resolved for 3.11, and the first published PR head passed runtime checks for 3.11/3.12/3.13. Consult the checks on the current head for the final follow-up.

No live provider inference, deployment or encrypted-database major migration was performed. SDK acceptance uses local transports and in-memory Qdrant. The recorded iOS result is a remote CI debug build, not a signed release or device test. The existing npm audit backlog, baseline test failures and separate Flutter major migration remain visible follow-up work.
