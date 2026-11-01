# Dependency scanner reliability verification — 2026-10-31

## Scope and provenance

This record verifies that the dependency scanners execute completely, retain their
actual results, and reject incomplete reports. Vulnerability findings remain
present and are preserved; this record makes **no claim that the repository is
free of vulnerabilities**.

The verified implementation is commit
`e6af2af99b1010be05a6f4362a579c63ba4aaa14`, tree
`22e6e48da9435b6c985dac3ff92e9374d3c59959`, based on main commit
`ab53c98596daca1740d2ac5a5dbd48db7b24e34f`. The audit includes that dependency
baseline and the scanner repair's manifest changes. The separate Python and
JavaScript security candidates have their own verification evidence.

[verification.json](verification.json) is an unchanged copy of the acceptance
receipt. Its SHA-256 is:

```text
6c7cfc5c0fac021a775de4b25dd15123d7bfa2795b850822198f45cee5f7b0a8
```

The receipt's commit and tree identify the tested implementation. This subsequent
documentation commit adds the evidence without changing scanner source. Absolute
workspace paths in the receipt identify the original local logs and reports; they
are provenance references, not paths required by the workflow.

## Complete Python audit

The actual full sweep completed in **579.21 seconds**, using bounded concurrency.
It covered every tracked, non-archive file named `requirements.txt` in the
existing scan scope. The data-pipeline template was replaced by its **20 rendered
combinations**: five input sources × four output sinks. Thus **79 source
manifests became 98 audit inputs**: 78 ordinary manifests plus 20 rendered inputs.

| Measure | Result |
| --- | ---: |
| Tracked source manifests | 79 |
| Planned and completed audit inputs | 98 / 98 |
| Rendered data-pipeline combinations | 20 |
| Inputs with no reported vulnerabilities | 56 |
| Inputs with vulnerability findings | 42 |
| Execution, resolution, schema or coverage failures | 0 |
| Finding occurrences across all inputs | 533 |
| Grouped package/version/advisory records | 128 |
| Packages represented in the grouped inventory | 16 |

The **533 occurrences are not 533 unique vulnerabilities**. The same package or
advisory can occur in several manifests and template combinations. Every finding
report is retained. A completed audit does not establish repository-wide security
clearance.

Final source hashes match all audited manifests. Two narrowly scoped follow-up
audits refreshed receipts after comment formatting changed the EO and
observability input hashes. The original complete sweep and the intermediate
local bootstrap failure were preserved in the source receipt history.

### Original execution gaps

| Input | Repair and interpreter | Actual outcome |
| --- | --- | --- |
| `tools/eo-validation/requirements.txt` | Use the EO tool's existing Python 3.12 contract | Completed; zero reported findings |
| `shared/observability/requirements.txt` | Remove the unused, nonexistent Jaeger exporter; align Starlette with central constraints; Python 3.11 | Completed; zero reported findings |
| `idp/templates/python-fastapi/skeleton/requirements.txt` | Use stable OTLP HTTP exporter `1.39.1` with the stable SDK family; Python 3.11 | Completed; **11 findings retained** |
| `idp/templates/data-pipeline/skeleton/requirements.txt` | Render all 20 combinations with real Nunjucks `3.2.4`; Python 3.11 | All 20 completed; zero reported findings |

Only the EO input uses Python 3.12. Normal service audits retain Python 3.11.

## Tests and failure propagation

- **63 Python tests passed**, with zero failures, errors or skips.
- **22 real Node/Nunjucks tests passed**, including all 20 combinations and two
  invalid-template cases.
- Ruff, formatting, Actionlint and `git diff --check` passed.
- Independent review checked failure propagation, inventory and template
  coverage, interpreter routing, and agreement between the Trivy cache used by
  the command and the database recorded in its receipt.

The Python helper validates scanner exit codes together with the JSON report.
Missing output, skipped dependencies, malformed or partial reports, inconsistent
exit codes, and missing inventory results fail the check. Both workflows upload
artifacts before the completeness gate propagates failure. Valid vulnerability
findings remain advisory for pip-audit.

## Trivy: actual findings and event gates

The real Trivy `0.69.3` scan used the original frozen database and preserved the
existing filesystem scope, vulnerability scanner, CRITICAL severity and
`--exit-code 1` policy.

| Observation | Result |
| --- | ---: |
| CRITICAL findings in the recorded baseline | 26 |
| Raw Trivy exit code | 1 |
| Pull-request findings gate exit code | 0 |
| Push findings gate exit code | 1 |
| Missing scanner: PR and push completeness gates | 2 / 2 |
| Malformed JSON from a simulated scanner returning zero: PR and push completeness gates | 2 / 2 |

Findings are informational on pull requests and enforcing on other events.
Incomplete scans fail on every event. The helper retains genuine SARIF, actual
exit status, report digest and database metadata. It never creates synthetic
empty SARIF. Validation enforces the configured Trivy CRITICAL SARIF structural
contract; it is not a complete implementation of the SARIF JSON Schema.

Recorded database SHA-256:

```text
d81ea576fbcd02c304b980d8eec4dd1a372648b648bfb876f48790d63ee58f93
```

Database `UpdatedAt`: `2026-10-31T13:09:00.83322165Z`.
Recorded SARIF SHA-256:

```text
f9f5946d569f6b3fe5cb57154261376e8d03dcca81dd0cce72c9a424c1592aa1
```

The missing-scanner and malformed-report cases are explicitly labeled fault
simulations in the receipt history. The 26-finding scan used the real scanner and
database.

## Optional Safety provider

The actual Safety status was **`not_configured`**: `SAFETY_API_KEY` was absent, so
Safety was not invoked. This status is separate from the mandatory pip-audit
inventory. No successful authenticated Safety scan is claimed.

When configured, Safety runs once against a directory. Its pinned `3.8.1` source
and `safety-schemas==0.0.16` report structure informed the deterministic tests:
findings exit `64` remains advisory; authentication, execution and invalid-report
failures are retained and fail the configured check. No API key is invented or
printed.

## Local CONNECT compatibility adaptation

The first local Python 3.11 sweep failed before dependency resolution: the
workspace proxy rejected the interpreter's HTTP/1.0 CONNECT request with HTTP
**426 Upgrade Required**. Those attempts remain recorded as execution errors.

The successful local run applied only `HTTPConnection.set_tunnel` and `_tunnel`
from official CPython **3.12.14** to its Python 3.11 scan processes through a
temporary, process-scoped `PYTHONPATH`/`sitecustomize` directory. This adaptation
and its executable source remain **outside the repository and normal CI**. No
stdlib file, global proxy configuration, destination, TLS verification setting
or dependency resolver option was changed.

The downloaded official module and the local source module had the same SHA-256:

```text
c2c0694155837d72fc710a4138e5d1e53ae1a652b117a2e23a5b1b0db527a0f9
```

The receipt records the extracted-method and adapter hashes, source comparison,
and actual execution evidence: interpreter **3.11.17**, packaging marker
`python_version == "3.11"`, certificate verification required, and hostname
verification enabled.

Primary references:

- [Official CPython 3.12.14 HTTP client source](https://github.com/python/cpython/blob/v3.12.14/Lib/http/client.py)
- [Python documentation: HTTP CONNECT changed to HTTP/1.1 in 3.12](https://docs.python.org/3.12/library/http.client.html#http.client.HTTPConnection.set_tunnel)
- [Nunjucks 3.2.4 release](https://github.com/mozilla/nunjucks/releases/tag/v3.2.4)
- [Safety: commands and directory targets](https://docs.safetycli.com/safety-docs/safety-cli/scanning-for-vulnerable-and-malicious-packages/available-commands-and-inputs)

## Reproduce the checks

Run from the repository root with Python 3.11, Python 3.12, Node.js 20 or newer,
and Git available. Use an isolated output directory. These commands match the
normal CI tooling; the workspace-specific CONNECT adaptation is not required on
an ordinary runner. A run in the original restricted workspace must apply the
separately recorded local adapter to the audit process, with its hashes verified.

```bash
set -euo pipefail
SCAN_LAB="$(mktemp -d)"
python3.11 -m venv "$SCAN_LAB/python311"
python3.12 -m venv "$SCAN_LAB/python312"
"$SCAN_LAB/python311/bin/python" -m pip install \
  pip-audit==2.10.1 PyYAML==6.0.3 pytest==9.0.3 ruff==0.15.11
"$SCAN_LAB/python312/bin/python" -m pip install pip-audit==2.10.1
npm install --prefix "$SCAN_LAB/renderer" \
  --no-save --ignore-scripts --no-audit --no-fund nunjucks@3.2.4

"$SCAN_LAB/python311/bin/python" -m pytest \
  tests/unit/ci/test_dependency_scan_integrity.py \
  --confcutdir=tests/unit/ci -q -o addopts= \
  --junitxml="$SCAN_LAB/scanner-tests.xml"
NUNJUCKS_MODULE="$SCAN_LAB/renderer/node_modules/nunjucks" \
  node --test scripts/ci/tests/render_security_requirements.test.cjs

"$SCAN_LAB/python311/bin/python" scripts/ci/audit_python_requirements.py \
  --repository . --output "$SCAN_LAB/python-audit" \
  --nunjucks-module "$SCAN_LAB/renderer/node_modules/nunjucks" \
  --python311 "$SCAN_LAB/python311/bin/python" \
  --python312 "$SCAN_LAB/python312/bin/python" --jobs 4
```

Inspect `summary.json`, `summary.md`, the complete plan, and each input's report,
logs and receipt under the output directory. The helper returns `0` for completed
coverage, including advisory findings; incomplete execution or coverage returns
`2`.

Optional Safety uses an existing configured key, if one is available:

```bash
if [ -n "${SAFETY_API_KEY:-}" ]; then
  "$SCAN_LAB/python311/bin/python" -m pip install safety==3.8.1
fi
"$SCAN_LAB/python311/bin/python" scripts/ci/run_optional_safety.py \
  --directory . --output "$SCAN_LAB/safety"
```

For an exact Trivy snapshot comparison, install Trivy `0.69.3`, provision the
recorded database and its metadata in a dedicated cache, and verify the database
SHA-256 above before running:

```bash
TRIVY_CACHE=/path/to/the/verified/frozen-cache
sha256sum "$TRIVY_CACHE/db/trivy.db"
TRIVY_SKIP_DB_UPDATE=true \
  "$SCAN_LAB/python311/bin/python" scripts/ci/trivy_scan_receipt.py scan \
  --repository . --binary trivy --cache "$TRIVY_CACHE" \
  --output "$SCAN_LAB/trivy"
"$SCAN_LAB/python311/bin/python" scripts/ci/trivy_scan_receipt.py gate \
  --receipt "$SCAN_LAB/trivy/receipt.json" --event pull_request
"$SCAN_LAB/python311/bin/python" scripts/ci/trivy_scan_receipt.py gate \
  --receipt "$SCAN_LAB/trivy/receipt.json" --event push
```

The recorded vulnerable baseline produces the event-gate codes shown above. A
fresh database or different dependency tree produces a separate current result;
retain its own metadata, digest and reports. Missing or invalid reports must
return `2`, including on pull requests.

## EO input-manifest follow-up

PR #2000's EO job correctly rejected a stale hash after two comments were added
to its requirements file. The NumPy pin, Python policy, guard, expected test IDs,
and sample data were unchanged. After the official runner passed on an isolated
copy of the reviewed inputs, only `files.requirements.txt` in the existing EO
manifest was refreshed. The real worktree then passed the same gate: **39 unit
cases and 18 independent cases**, with no failures, errors, or skips and unchanged
inputs. Both Ruff checks passed. [The follow-up receipt](eo-manifest-followup.json)
preserves the original failure, exact hash change, commands, and validated receipts.
The result remains `PASSED_OFFLINE_RESEARCH_ONLY`, with production approval false.
