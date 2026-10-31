# Root Python lock and security verification — 2026-10-31

The root lock was regenerated with **uv 0.13.4**, using the normal resolver and
the declared project dependencies. The final frozen environments pass **102
tests with no skips on each of Python 3.11, 3.12 and 3.13**. A complete audit of
the **110 installed packages in each environment reports no known
vulnerabilities**. These results apply to the root extras; independently packaged
services have separate dependency closures.

Base: `ab53c98596daca1740d2ac5a5dbd48db7b24e34f`.

Final `uv.lock` SHA256:
`831299956612d4366b8806387f8d23df2ac61d7f5b2aee1b234e9064d97e39ef`.

The adjacent [verification.json](verification.json) binds the source files,
runtime results, installed manifests, JUnit reports and audit reports to hashes.

## Resolver repair and preserved behavior

The original `uv lock --check` failed. TensorFlow 2.21.0 requires `ml-dtypes`,
whose Python 3.13+ dependency requires NumPy >=2.1. The project's unconditional
NumPy <2 constraint therefore made its universal lock unsatisfiable.

The repaired NumPy declarations are:

```text
numpy>=1.26.0,<2.0.0; python_version < '3.13'
numpy>=2.1.0,<2.5.0; python_version >= '3.13'
```

This preserves the existing NumPy 1.x ABI on Python 3.11/3.12 and permits the
upstream requirement on Python 3.13+. The generated lock selects NumPy 1.26.4 and
2.4.2 respectively. `requires-python` remains **`>=3.11`** and
`tensorflow-cpu==2.21.0` remains an unconditional dependency of the ML extra.
There are no resolver overrides, dependency exclusions or manual lock edits.

The old lock also lagged existing project declarations for FastAPI, TensorFlow,
OpenTelemetry and several testing tools. Regeneration reconciles those existing
specifications. Pydantic 2.13.1, Tenacity 8.5.0, SQLAlchemy 2.0.49 and
`bcrypt>=4.2,<5` were aligned with their **existing central constraints**; in
particular, the bcrypt bound preserves the declared Passlib integration.

The central `pydantic-settings` constraint was subsequently raised from 2.13.1 to
2.14.2 for [GHSA-4xgf-cpjx-pc3j](https://github.com/advisories/GHSA-4xgf-cpjx-pc3j).
That package is consumed by service manifests and is absent from the root lock,
so this adjustment does not change the frozen runtime closure. The 36 root
consistency tests passed again after the constraint change. The JSON records
both the matrix's original input hashes and this later constraint verification.

## Security closure

The original root lock contributed eight CRITICAL results to the reproduced
Trivy scan: AnyIO, certifi, PyJWT and five Pillow findings. The final lock has
**zero CRITICAL results** under the same Trivy 0.69.3 database, updated
`2026-10-31T13:09:00.83322165Z`.

A full audit of the first limited repair exposed additional affected packages.
Those findings were retained and the root closure was repaired before acceptance.
The final full audit is mandatory in the dedicated workflow; findings are not
ignored or converted to success.

| Dependency | Original lock | Final lock |
| --- | --- | --- |
| PyJWT | 2.11.0 | 2.15.1 |
| cryptography | 46.0.5 | 50.0.2 |
| Pillow | 11.3.0 | 13.0.0 |
| AnyIO | 4.12.1 | 4.15.1 |
| certifi | 2026.2.25 | 2026.10.23 |
| aiohttp | 3.13.3 | 3.14.4 |
| Starlette | 0.52.1 | 1.3.1 |
| OpenTelemetry API/SDK | 1.39.1 | 1.45.1 |
| OpenTelemetry FastAPI instrumentation | 0.60b1 | 0.66b1 |
| Keras | 3.13.2 | 3.15.0 |
| requests | 2.32.5 | 2.33.0 |
| urllib3 | 2.6.3 | 2.8.0 |
| idna | 3.11 | 3.15 |
| multidict | 6.7.1 | 6.9.1 |
| Pygments | 2.19.2 | 2.20.0 |
| setuptools | 82.0.0 | 84.1.0 |
| Black | 24.10.0 | 26.10.1 |
| filelock | 3.25.0 | 4.2.1 |
| virtualenv | 21.1.0 | 21.14.10 |

Appropriate lower bounds prevent these known vulnerable versions from returning.
FastAPI remains at the already declared **0.135.1**: its published dependency
metadata permits the patched Starlette release. The OpenTelemetry API, SDK and
instrumentation were updated together.

The root `python-jose` dependency was obsolete: no active Python source under
`apps/services/` or `shared/` imports it, and `apps/services/shared/versions.py`
already documents the PyJWT migration. Removing this unused root dependency also
removes its `ecdsa`, `rsa` and `pyasn1` closure. The separately packaged
`sahool-platform/apps/auth` application still imports `jose` and installs its own
requirements in its Dockerfile. This change does not silently remove or migrate
that legacy application's dependency.

### Primary package metadata used

- [TensorFlow CPU 2.21.0](https://pypi.org/pypi/tensorflow-cpu/2.21.0/json) and
  [ml-dtypes 0.5.4](https://pypi.org/pypi/ml-dtypes/0.5.4/json): the actual NumPy
  requirements and published runtime distributions.
- [FastAPI 0.135.1](https://pypi.org/pypi/fastapi/0.135.1/json) and
  [Starlette 1.3.1](https://pypi.org/pypi/starlette/1.3.1/json): compatible dependency
  specifications without raising the FastAPI version.
- [cryptography 50.0.2](https://pypi.org/pypi/cryptography/50.0.2/json),
  [Pillow 13.0.0](https://pypi.org/pypi/Pillow/13.0.0/json) and
  [PyJWT 2.15.1](https://pypi.org/pypi/PyJWT/2.15.1/json).
- [OpenTelemetry SDK 1.45.1](https://pypi.org/pypi/opentelemetry-sdk/1.45.1/json)
  and [FastAPI instrumentation 0.66b1](https://pypi.org/pypi/opentelemetry-instrumentation-fastapi/0.66b1/json):
  matching API and semantic-convention requirements.
- [virtualenv 21.14.10](https://pypi.org/pypi/virtualenv/21.14.10/json): the additional
  patch required after checking the initially considered 21.14.9 release.

## Actual verification

| Runtime | NumPy | Tests | Skips | `uv pip check` | Full package audit |
| --- | --- | --- | --- | --- | --- |
| CPython 3.11.17, Linux x86_64 | 1.26.4 | 102 passed | 0 | PASS | 110 packages, 0 findings |
| CPython 3.12.14, Linux x86_64 | 1.26.4 | 102 passed | 0 | PASS | 110 packages, 0 findings |
| CPython 3.13.16, Linux x86_64 | 2.4.2 | 102 passed | 0 | PASS | 110 packages, 0 findings |

The selected cases exercise:

- Root lock metadata against the current project extras, patched version floors,
  canonical constraints and Python markers, including negative controls for a
  stale PyJWT specification, missing TensorFlow and a stale extra.
- The existing 38 NDVI calculation tests and five dependency-constraint tests.
- RSA and ECDSA JWT signing, verification, wrong keys, modified payloads, expired
  tokens and rejection of asymmetric public keys as HMAC secrets.
- Passlib/bcrypt password hashing and rejection of a wrong password.
- PNG/JPEG decoding, truncated and invalid images, the Pillow pixel limit, and
  the actual disease-detection image-color consumer.
- Real TensorFlow matrix operations, `ml-dtypes` conversion, Keras CPU inference,
  and model save/load through the installed numerical stack.
- FastAPI request/response validation and HTTP errors with the patched Starlette.
- OpenTelemetry HTTP spans and propagated trace context with an owned in-memory
  exporter and deterministic sampling.

The same 17 cryptography/image/password cases also passed against cryptography
46.0.5 and Pillow 12.2.0 in a separate baseline environment. The real runtime
suite passes those cases with the new versions; this is a behavior comparison,
not a claim that the older versions are secure.

An attempted reuse of an earlier Python 3.13 environment failed `uv pip check`
because it contained duplicate old and new bcrypt/Pydantic distribution metadata.
That failure was preserved. A fresh environment, installed normally from the
same frozen lock, passed all checks. No duplicate metadata was manually removed
to manufacture acceptance.

### Reproduction

Use a fresh environment for each target Python version. The workflow pins uv to
0.13.4 and records the exact environment before running:

```bash
uv lock --check --python 3.11
uv sync --all-extras --frozen --python 3.11
uv pip check --python .venv/bin/python
uv pip freeze --python .venv/bin/python > environment.txt
.venv/bin/python -B -m pytest \
  tests/unit/test_python_lock_consistency.py \
  tests/unit/test_infrastructure_fixes.py::TestDependencyConstraints \
  tests/unit/test_ndvi_calculation.py \
  scripts/ci/check_python_lock_runtime.py \
  -p no:cacheprovider -q --tb=short --junitxml=runtime.xml
uv tool run --python 3.11 --from pip-audit==2.10.1 pip-audit \
  -r environment.txt --no-deps --disable-pip --strict \
  --progress-spinner off --format json --desc off -o full-lock-audit.json
```

The audit's `--no-deps` option avoids a second resolution: every package in the
actual installed closure is already listed in `environment.txt` and audited.
The normal resolver, frozen installation and `uv pip check` run beforehand.

## Coordinated service and embedding verification

The service dependency changes are included in the same branch so that higher
central security floors do not leave consumer manifests unsatisfiable. All
**44 actual consumer requirement resolutions passed**, using their adjacent
Dockerfile constraints or the applicable standalone contract. The accompanying
[consumer-verification.json](consumer-verification.json) records the exact
source hashes and results.

The 19 parser, TLS, shared-encryption and settings cases passed. These cover
multipart field smuggling and header/length limits, IDNA certificate validation,
the real AES-GCM/HMAC consumer, and rejection of a secrets-directory symlink that
escapes its configured directory. The corresponding older dependency versions
fail the relevant negative controls. The existing Shared PyJWT Security workflow
now runs these cases alongside the JWT callers.

For the two actual embedding consumers, a fresh CPU environment with
SentenceTransformers 6.0.0 and Torch 2.13.0+cpu passed all five offline tests and
`uv pip check`. Its **complete 52-package audit has zero findings**. The same test
module against the 5.6.0 loader has exactly one expected security failure and
four passing cases: the older loader executes custom local Python despite
`trust_remote_code=False`. The negative control uses a harmless marker file in
the test's temporary directory. The mandatory CPU job records both results and
checks the older loader's dependency compatibility rather than silently
substituting an incompatible environment.

PyPI does not publish the official Torch `+cpu` distribution suffix. The audit
therefore records the actual installed `2.13.0+cpu` build, normalizes that one
entry to upstream `2.13.0` for advisory lookup, and preserves the mapping and
original environment hash. No package or advisory is excluded.

## CI test environment completeness follow-up

On PR #1997 head `c147df6530ea6e1823061c192619f7bf3eb95263`, the dedicated
frozen-runtime and shared-auth jobs passed. The broader
[Quality Gate](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41237801285/job/124645312670)
and [CI Pipeline](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41237801309/job/124647078117)
each exposed one missing test-environment dependency. The real shared-crypto
consumer imports `bcrypt`, but those jobs' installation lists did not include it.
The unchanged encryption roundtrip/tamper regression failed at that import,
before executing its AES-GCM/HMAC assertions.

The follow-up declares `bcrypt>=4.2.0,<5.0.0` in `requirements/testing.txt`,
the CI Pipeline's direct dependency list and the Quality Gate's fallback list.
This matches the existing root constraint and frozen dependency. The lock,
Python support policy, production code and regression assertions are unchanged.

| Focused reproduction on fresh Python 3.11.17 | Result |
| --- | --- |
| Original testing requirements plus current constraints | Normal installation succeeds; `bcrypt` is absent |
| Original environment, exact failing regression | 1 expected failure: `ModuleNotFoundError: No module named 'bcrypt'` |
| Updated testing requirements, same regression | 1 passed |
| Updated environment, complete dependency-security regression module | 19 passed, 0 skipped |
| `uv pip check`, Actionlint and diff whitespace check | Passed |

The single regression is included in the 19-case module; these counts are not
additive. [bcrypt-ci-repair.json](bcrypt-ci-repair.json) records the commands,
versions, exit codes, JUnit counts, source hashes and preserved negative control.
These focused local results do not substitute for the next remote CI run.

To reproduce the fixed test environment from the repository root:

```bash
uv venv --python 3.11 /tmp/sahool-bcrypt-ci
uv pip install --python /tmp/sahool-bcrypt-ci/bin/python \
  -c constraints.txt -r requirements/testing.txt
PYTHONPATH=. /tmp/sahool-bcrypt-ci/bin/python -B -m pytest \
  tests/unit/security/test_dependency_security_regressions.py \
  -q -o addopts='' -p no:cacheprovider --junitxml=/tmp/bcrypt-ci-tests.xml
uv pip check --python /tmp/sahool-bcrypt-ci/bin/python
```

The separate frontend failures observed on that head remain outside this
test-environment fix: Flutter's SDK `intl` pin conflicts with the app's range,
web tests expose existing CSP/authentication contract and mock issues, and the
E2E readiness check probes port 3000 while the web server listens on 3040.
The Python PR does not change those frontend sources or their workflow.

## Remaining boundaries

TensorFlow 2.21.0 has no published CPython 3.14 wheel. The universal metadata lock
can be valid while an installation target lacks an upstream distribution.
Neither the project's Python policy nor the TensorFlow feature was narrowed to
hide that limitation. The recorded runtime acceptance covers Linux CPU on
Python 3.11–3.13, not GPU execution or every advertised platform. The legacy
authentication application's separate closure is also outside this root audit.
YOLO's separate Torch >=2.6,<2.7 compatibility cap is retained; the clean CPU
embedding audit does not cover that service. Raising the shared Docker AI floor
without a YOLO migration would make that consumer unresolvable.
