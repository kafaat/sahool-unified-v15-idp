# JavaScript critical dependency security — 2026-10-31

This evidence records the JavaScript dependency repair based on commit
`ab53c98596daca1740d2ac5a5dbd48db7b24e34f`. The repair removes the 16 JavaScript
CRITICAL findings in the reproduced Trivy baseline and the remaining CRITICAL
entries found by the final npm audit. It does **not** make the whole dependency
tree or every application test suite clean.

The complete results and provenance are in [verification.json](verification.json).
[source-manifest.json](source-manifest.json) identifies the reviewed source bytes,
including manifests, locks, consumers, tests, and workflow. Documentation and
generated build output are excluded from that source snapshot. This evidence was
prepared before the publishing commit; the source hashes, rather than an invented
final commit ID, identify the candidate.

## Changes and compatibility decisions

| Dependency or consumer | Candidate | Reason and validation |
| --- | --- | --- |
| Next.js and matching ESLint configuration | 15.5.28 | Patched release within Next 15; exact override and both app declarations agree. Real web production build and native image conversion passed. |
| Sentry Next.js integration | 9.47.2 | Retains the existing major version. Tests exercise the actual wrapper with both valid telemetry envelopes and hostile requests. |
| MapLibre GL | 6.4.1 | Required patched release. Both direct imports use the supported namespace form; two browser tests exercise the actual map component, rendering, layers, popup text, and attribution sanitization. |
| proxy-addr | 2.0.8 | Regenerated affected active and archived lockfiles. Real trust-chain tests cover the vulnerable forwarded-address behavior. |
| Storybook packages | 8.6.19 | Keeps Storybook 8. A real Storybook build also verifies the small compiler-selection compatibility fix. |
| Handlebars | At least 4.7.10, below 5 | Root security floor and affected standalone lockfiles; real template/property-access regressions. |
| Vitest and coverage packages | 3.2.7 | Matching versions across consumers, retaining Vitest 3. |
| Vitest's Tinypool dependency | 2.1.2 | Explicit override scoped to Vitest in the root and standalone code-review-agent manifests. Tests resolve the worker pool from Vitest's own package and run real workers. |

Tinypool 2 is outside Vitest 3's declared `^1.1.1` dependency range. This is a
deliberate compatibility decision, not an unnoticed resolver change: the upstream
2.0 release drops Node 18, while this repository uses Node 20. The repaired worker
behavior, Vitest execution, and coverage were tested on **Node 20.20.2** with
**npm 10.9.0**. This does not establish compatibility with every Node 20 patch.
Published package metadata and upstream advisory responses are retained under
[metadata](metadata/), including the
[Tinypool release](https://github.com/tinylibs/tinypool/releases/tag/v2.0.0),
[Tinypool advisory](https://github.com/advisories/GHSA-85c8-ppgw-ccpr),
[Storybook advisory](https://github.com/advisories/GHSA-f2ph-cmg5-wxc8), and
[Handlebars advisory](https://github.com/advisories/GHSA-p8wg-vrv2-v86f).

The existing local `shared-events` consumers in chat-service and
field-management-service use the workspace package path. Their Dockerfiles already
translate that path for their build contexts. Lock regeneration also reconciles
pre-existing manifest/lock drift; [the semantic lock diff](receipts/final-lock-semantic-diff.json)
records those additional resolver changes rather than describing every lock edit
as a security-version substitution.

## Security results and their boundaries

| Scan | Actual result | Interpretation |
| --- | --- | --- |
| Final complete root npm audit | **0 critical, 34 high, 88 moderate, 11 low; 133 total** | `npm audit --audit-level=critical --json` exits 0 because the threshold is critical. The other 133 findings remain visible in the complete report. |
| Trivy baseline | **26 CRITICAL results** | 16 JavaScript findings and 10 Python findings. These are scanner result entries, not a claim of 26 unique CVEs. |
| JavaScript branch, same Trivy database | **10 CRITICAL results**, exit 1 | All 16 targeted JavaScript entries are absent. The remaining 10 exactly match the baseline Python findings. |
| Python plus JavaScript manifest composition, same database | **0 CRITICAL results**, exit 0 | The composed dependency inputs resolve all 26 original entries. This is a manifest-only projection, not a Git merge, application build, container image, or deployed runtime. |

The final npm report is preserved byte-for-byte in
[npm-audit-final.json](reports/npm-audit-final.json) (150,574 bytes). It includes
the residual high and moderate findings, including the remaining Vitest advisory;
there is no whole-tree zero-vulnerability claim.

The fixed Trivy scan uses **Trivy 0.69.3**, vulnerability scanning only, severity
`CRITICAL`, `--exit-code 1`, and both database/check-update skips. Database SHA-256:

```text
d81ea576fbcd02c304b980d8eec4dd1a372648b648bfb876f48790d63ee58f93
```

Its recorded `UpdatedAt` is `2026-10-31T13:09:00.83322165Z`. The comparison therefore
controls database drift; it does not predict findings in a future database.
The original JavaScript scan preserved all 206 dependency input hashes. The
baseline and combined projections contain those inputs plus 12 supplementary
dependency metadata files, **218 files total**, and both enumerate 110 language
inputs. The Python overlay uses commit
`a5372955f0becf5810c46e3159bbaabe741fc8e1`, tree
`cd60192df2a3bf39b1fdf0d1f5d17d112fd6349d`, with 48 overlay files. Neither worktree
was modified to create the projection.

The preserved [16-finding comparison](trivy/javascript-sixteen-findings-comparison.json),
[26-finding comparison](trivy/python-js-composite-comparison.json),
[composite source manifest](trivy/composite-source-manifest.json), command receipts,
and all three SARIF reports provide the exact inputs and outcomes. The combined
SARIF's empty results array is output from the successful real scan, not a fabricated
replacement for a failed scanner.

## Runtime and regression acceptance

| Check | Result |
| --- | --- |
| Clean root `npm ci --ignore-scripts --no-audit --no-fund` | Exit 0; 54.651 seconds. This is the actual workspace installation used for final Node 20 checks. |
| Security regression module | **31 passed, 0 failed, 0 skipped**; final JUnit retained. |
| Chromium browser security/consumer tests | **2 passed**; native WebGL2 and actual MapView/MapLibre, with fixture API and raster tiles. |
| shared-hooks with coverage | **60 passed**; coverage report generated. |
| shared-ui with coverage | **23 passed**; coverage report generated. |
| Final shared package build | Exit 0; 15.694 seconds. |
| Web and Admin TypeScript checks | Both exit 0. |
| Web Next.js production build | Exit 0; **146.17 seconds**. |
| Storybook config-only build | Exit 0; **17.874 seconds**, with the flag absent from the launch environment and no diagnostic preload. |
| Standalone lock consistency | **11/11 frozen npm ci dry-runs passed**, offline, with unchanged lock hashes. These are not eleven independent installations or service deployments. |
| Old-package negative control | Selected behavior cases: **9 failed, 3 passed**, exit 1. The test-name filter intentionally excluded 19 other cases. |

The negative control uses baseline `ab53c985` and the preserved older packages.
It covers proxy-addr, Handlebars, the actual Vitest worker pool, and Sentry.
`NODE_PATH` supplies the already-installed Next 15.5.14 peer required by the old
Sentry package; it does not replace the assertions or install candidate packages.
The receipt and complete selected-run log are retained. This is not a claim that
every patched package has its own differential exploit test.

Browser coverage demonstrates the real component under the test Vite server; it
does not substitute for a full production Next.js browser session. The native
image regression uses the Sharp instance resolved by Next and performs real image
conversion rather than merely inspecting its version string.

### Storybook compiler selection

Both the preserved baseline (Next 15.5.14 / Storybook 8.6.18) and the candidate
(Next 15.5.28 / Storybook 8.6.19) initially failed. The first cause was external
Webpack 5.105.4's DefinePlugin requesting
`collectDestructuringAssignmentProperties` from Next's bundled Webpack 5.98.0
parser, which lacks that hook. The later shutdown `tap` stack was not the cause.

`apps/admin/.storybook/main.ts` sets `NEXT_PRIVATE_LOCAL_WEBPACK=true` while loading
Storybook configuration so its compiler and plugins use the same installed Webpack.
No global environment, production Next.js script, or dependency policy was changed.
The final build launched with no inherited flag, used no diagnostic preload, and
produced 16 stories plus 3 documentation entries. Baseline diagnosis reused the
preserved old installation, so it is not presented as a fresh baseline npm ci.
Asset-size and react-leaflet metadata warnings remain in the successful build.

### Reports survive Playwright

The browser configuration writes temporary browser output into its own artifact
directory and places JUnit at the explicit repository report path. The actual
rerun recorded identical before/after hashes for the npm audit, Node JUnit,
shared-hooks JUnit, and shared-ui JUnit. The new browser JUnit also exists and
matches its recorded hash. See
[browser-evidence-preservation.json](receipts/browser-evidence-preservation.json).
This verifies that Playwright no longer removes the preceding security evidence.

## Application suites that remain non-clean on this branch

These are the results on the JavaScript branch, which does not contain the separate
frontend contract repair in [PR #1998](https://github.com/kafaat/sahool-unified-v15-idp/pull/1998).
Do not replace them with the results of that PR.

| Consumer | Final result | First cause or limitation |
| --- | --- | --- |
| Web app | **1293 passed / 19 failed**, plus Sidebar collection error | Eight existing CSP nonce assertions; tenant/auth/refresh contract drift; missing DatabaseZap mock. |
| Admin app | **2513 passed / 2 failed** | Existing dynamic-rendering expectation and FieldCreateDialog endpoint contract. |
| chat-service | **278 test cases passed**, process terminated with exit -15 | Jest reported outstanding asynchronous handles after completing the cases. This is not a successful process exit. |
| crop-growth-model | **5 passed**, one suite could not compile, exit 1 | Existing health test calls `readinessCheck()` without its required response argument. |
| disaster-assessment | **45 passed**, exit 0 | Actual Jest execution. |
| field-management-service | **177 passed / 1 failed**, one further suite compile error, exit 1 | Existing stats expectation and missing required userId arguments in task tests. |
| lai-estimation | **8 passed**, exit 0 | Actual Jest execution. |
| marketplace-service | **354 passed / 1 failed**, exit 1 | Readiness test expects NATS connected; the test environment reports not_configured. |
| yield-prediction | **5 passed**, exit 0 | Actual Jest execution. |

Exact counts, failed case names, error messages, command receipts, and original
report hashes are in [consumer-test-results.json](consumer-test-results.json).
Baseline comparisons established the frontend contract drift independently;
not every service defect received a fresh old-dependency differential run here.
The CSP helper's deliberate nonce omission is a genuine policy gap retained for
separate work; this dependency repair neither skips those tests nor weakens them.

## Reproduction and evidence integrity

Use the checked-in JavaScript security workflow for a fresh installation, the
31-case security module, browser cases, shared coverage, Storybook build, complete
npm audit output, and evidence upload. The gate fails critical npm findings; it
does not reinterpret the remaining 133 findings as absent. Existing broader test
and security policies are not changed by this evidence bundle.

[artifact-manifest.json](artifact-manifest.json) maps each retained artifact to its
original local source, byte count, and SHA-256. The original Trivy receipts also
record scanner commands, database identity, input hashes, and output hashes.
The large database itself and generated build directories are not committed.
Raw `.log` files are retained byte-for-byte, including their original trailing
whitespace and blank final lines; their recorded hashes must not be normalized.
The earlier unstaged `git diff --check` did not inspect these then-untracked
artifacts. The staged source/documentation whitespace check passes when the raw
logs under this evidence directory are explicitly excluded; an unrestricted
staged check reports the preserved log whitespace.
Validate the source manifest against the candidate before applying these results
to a later source revision. No Python policy, uv.lock, Flutter configuration,
deployment, or frontend test-contract implementation is changed by this JavaScript
repair.
