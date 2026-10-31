# CI follow-up after the shared PyJWT repair — 2026-10-31

## Scope

This independent change starts from `main` at
`52041a321868c4c71633a149f596f91bd569307c`, after PyJWT PR #1995 was merged and
its dedicated Python 3.11/3.12 acceptance passed. It repairs demonstrated CI
checkout, monitoring, import-isolation, and test-result reporting defects.
Dependency manifests, Python support policy, constraints, and `uv.lock` are
unchanged. Product authentication and LLM provider code are unchanged.

## Defects and repairs

### Scorecard checkout

The repository tracked 38 mode-160000 entries under `.claude/worktrees/agent-*`
without a `.gitmodules` file. These point to seven historical commits of this
same repository, rather than declared external dependencies. Recursive Git
credential cleanup therefore failed before Scorecard analysis started.

The repair removes exactly those tracked references with `git rm --cached`;
all local directories and their contents were preserved. It adds a root-scoped
ignore rule and a Governance Structure Guard check that rejects future tracked
local worktrees, including forced additions. Normal Claude configuration and
legitimate declared submodules elsewhere remain supported.

The Scorecard workflow, `persist-credentials: false`, analysis, publication,
and SARIF upload are unchanged. Baseline recursive traversal exits 128;
the corrected index exits 0. Actual Scorecard acceptance requires a successful
main-branch analysis and upload: its upstream publisher requires the default
branch for published results. A branch-only dispatch is not a substitute.

### PR Status Monitor

The read-only `gh pr list` request previously failed immediately on HTTP 502
or truncated JSON. A standard-library helper now makes at most three attempts,
each limited to 60 seconds, with two- and four-second retry delays. It validates
the response before atomically publishing the snapshot. Exhaustion fails;
it never substitutes an empty list for an API failure. The explicit 1000-PR
limit replaces the CLI's default 30-item limit, and reaching that limit fails
because completeness cannot be established.

The status-count expression also had an independently reproduced jq error:
it applied `.conclusion` to an entire array. The corrected expression iterates
checks and counts failing PRs once, including legacy FAILURE/ERROR status
contexts. Reports describe technical mergeability without claiming merge
readiness or subtracting overlapping failure categories. Existing notification
and branch-update jobs, conditions, permissions, and triggers are unchanged.

### Import isolation and Quality Gate

The smoke import test deleted live modules from `sys.modules`. Unit tests
collected earlier retained functions from the old module while their mocks
targeted the new module. The two LLM convenience tests then attempted Ollama.

Fresh imports now run in a separate interpreter with a 30-second timeout and
a required completion record. The existing optional-ImportError skip policy
is retained; circular imports, runtime failures, timeouts, and missing reports
fail. The parent interpreter's module identities remain intact.

The Quality Gate now records both pytest and tee exit codes, uploads logs,
JUnit, and coverage evidence, then enforces the test result. The aggregate
also fails when the test job failed, was skipped, or lacks successful evidence.
A security warning cannot overwrite a blocking report. This change enforces
**test execution and its evidence**; it does not redesign the policies of
the other quality stages.

## Executed local validation

| Check | Result |
| --- | --- |
| Combined new regressions, original LLM sequence, existing LLM unit file, and PyJWT regressions | 149 passed, zero failures/skips |
| Complete smoke folder followed by the LLM unit file | 443 passed, 7 existing skips, zero failures |
| New CI regression cases within the combined selection | 91 passed: 50 monitor, 5 repository hygiene, 12 import isolation, 24 result propagation |
| Original smoke-before-unit sequence on unchanged baseline | 2 failed, 1 passed; candidate sequence passes |
| New module-identity guards against baseline | 3 expected failures |
| Same controlled pytest failure through actual workflow shell | Baseline final exit 0; repaired final exit 1 after evidence preservation |
| Original / corrected jq failure-count expression | Exit 5 / exit 0 with one failing PR |
| Ruff lint/format, actionlint 1.7.12, whitespace and package consistency | Passed |

These selections overlap and should not be added into one total. The seven
smoke skips concern optional packages and absent historical service/schema
paths; all 40 fresh branch-import probes passed. The first wider local run
lacked `jsonschema` and `tenacity`, which are already CI prerequisites. Only
the scratch environment was completed under the existing constraints before
the exact selection was rerun successfully.

The monitor tests execute the actual workflow shell, actual helper, and real
jq with a controlled local `gh` executable. They do not send API requests,
notifications, or branch updates. Workflow-result tests similarly execute
the actual shell with controlled pytest exits; they do not dispatch actions.

Commands, source hashes, negative controls, skip reasons, tool identity, and
validation summaries are recorded in [verification.json](verification.json).

## Existing separate work

- Flutter 3.27.1 pins `intl` 0.19.0, while the mobile manifest requires
  `intl ^0.20.2`. The same dependency-resolution failure exists before and
  after PR #1995; no Flutter SDK or dependency decision is included here.
- Root `uv.lock` still contains PyJWT 2.11.0 and its TensorFlow/NumPy/Python
  resolver conflict remains separate. No frozen-lock repair is claimed.
- The existing `python-multipart` security findings are unchanged.
- The push-only Dependency Vulnerability Scan still fails its CRITICAL gate:
  the PyJWT merge reports 26 findings, compared with 28 on the exact earlier
  baseline. The workflow is unchanged. Counts alone do not prove which
  advisories remain, and this CI repair does not relax that gate.
- Other masked service, contract, and security checks are not certified as
  successful by this repair. No deployment acceptance is claimed.

## Primary execution and upstream references

- [Scorecard checkout failure on the PyJWT merge](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41229094050/job/124619311659)
- [PR monitor API failure on the PyJWT merge](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41229094111/job/124619311831)
- [Integrated Quality Gate baseline failures](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41217450326/job/124584980521)
- [Flutter baseline failure](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41152335408/job/124391539781)
- [Remaining critical dependency gate](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41229094009/job/124619312085)
- [Same dependency gate on the earlier baseline](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41152335427/job/124391457999)
- [Scorecard publishing restrictions](https://github.com/ossf/scorecard-action/blob/v2.4.3/README.md#workflow-restrictions)
- [Scorecard default-branch validation](https://github.com/ossf/scorecard-webapp/blob/9c2f66d5f6ff56ca4a4ac2fba6ec8dcc5379d31c/app/server/post_results.go)
