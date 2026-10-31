# Shared PyJWT security repair — 2026-10-31

## Result and scope

Both independent shared-library installation entry points now pin
`PyJWT==2.15.1`:

- `apps/services/shared/requirements.txt` (previously 2.11.0)
- `apps/services/shared/auth/requirements.txt` (previously 2.10.1)

The candidate was prepared from `main` at
`c796f25eb86c6cadb2adb365c3ba439fa17b8acc`. Product authentication code is
unchanged. The new tests exercise `apps.services.shared.auth` directly, as
well as existing tests of the separate root `shared.auth` implementation.
The affected source is loaded under a private test-package name to avoid an
existing service-test namespace collision; its source path is checked, relative
imports are preserved, and the private namespace is removed after the tests.

Issue [#1562](https://github.com/kafaat/sahool-unified-v15-idp/issues/1562)
was closed by the stale bot on 2026-07-13 with `state_reason=not_planned`;
that closure was not evidence of remediation.

## Why 2.15.1

- [GHSA-752w-5fwx-jx9f / CVE-2026-32597](https://github.com/advisories/GHSA-752w-5fwx-jx9f)
  lists versions through 2.11.0 as affected and 2.12.0 as the first fix.
  The defect accepts correctly signed JWTs carrying unsupported critical
  header extensions.
- Later advisories
  [GHSA-42vr-xj54-vc7v](https://github.com/jpadilla/pyjwt/security/advisories/GHSA-42vr-xj54-vc7v)
  and [GHSA-x33g-cr3x-6449](https://github.com/jpadilla/pyjwt/security/advisories/GHSA-x33g-cr3x-6449)
  require at least 2.15.0.
- [PyPI 2.15.1](https://pypi.org/project/PyJWT/2.15.1/) is the latest stable
  release checked on 2026-10-31. It was released on 2026-09-28 and requires
  Python >=3.9. Its [changelog](https://pyjwt.readthedocs.io/en/stable/changelog.html)
  restores valid Base64URL padding compatibility while retaining stricter
  token validation.

## Executed validation

Local execution used Python 3.12.14, PyJWT 2.15.1, pytest 9.0.3, and the
actual two requirement files resolved together with existing `constraints.txt`.
`pip check` passed. All test counts below exclude the intentional negative
controls against vulnerable versions.

| Check | Result |
| --- | --- |
| New affected-module and pin-guard tests | 39 passed, 0 failed, 0 skipped |
| Extended authentication regression selection, including those 39 tests | 341 passed, 0 failed, 0 skipped |
| Existing `copilot-api` authentication dependency tests | 11 passed, 0 failed, 0 skipped |
| New tests collected/executed alongside the service namespace fixture | 39 passed, 0 failed, 0 skipped |
| Ruff check and format check of the new tests | Passed |
| Workflow YAML parsing and `git diff --check` | Passed |
| Constrained consumer dependency resolutions | 8 passed |

The new tests cover real access/refresh issuance, refresh exchange, configured
algorithm enforcement, issuer/audience checks, missing required claims, future
time claims, invalid NumericDate types, expired/tampered/malformed tokens,
unsupported critical headers, noncritical-header compatibility, and valid
signature padding. A real FastAPI test route uses `get_current_user`; valid
tokens yield HTTP 200 and invalid tokens yield HTTP 401 with the Bearer challenge.

The pin guard requires exactly one unconditional, exact stable pin in each
manifest; both must agree and be within the reviewed range >=2.15.1,<3. Eight
negative declarations prove detection of drift, downgrade, range, wildcard,
prerelease, conditional, duplicate, and missing pins. It also rejects the actual
original manifests obtained with `git show` from the base commit.

### Differential proof of CVE-2026-32597

The same signed fixture bytes were decoded by the real affected module in
separate Python processes. Only the PyJWT version changed.

| PyJWT | Valid control | Unsupported `crit` | New regression test |
| --- | --- | --- | --- |
| 2.10.1 | Accepted | Incorrectly accepted | Fails: did not raise `ValueError` |
| 2.11.0 | Accepted | Incorrectly accepted | Fails: did not raise `ValueError` |
| 2.15.1 | Accepted | Rejected; `verify_token=False` | Passes |

The candidate raises `ValueError` containing `Unsupported critical extension`,
which the actual FastAPI dependency translates into HTTP 401. No JWT decoder was
mocked. Fixture hashes, exception results, and negative-control JUnit counts are
included in [verification.json](verification.json).

### Consumer compatibility

All resolutions used actual manifests, the unchanged root constraints, an
explicit 2.15.1 candidate constraint, Linux x86-64, and `uv pip compile
--no-build`. These are dependency-resolution checks, not running service images.

| Requirements | Python target | Packages | PyJWT |
| --- | --- | --- | --- |
| Shared | 3.11 | 36 | 2.15.1 |
| Shared | 3.12 | 35 | 2.15.1 |
| Shared auth | 3.11 | 20 | 2.15.1 |
| Shared auth | 3.12 | 19 | 2.15.1 |
| irrigation-smart | 3.11 | 30 | 2.15.1 |
| advisory-service | 3.11 | 45 | 2.15.1 |
| weather-service | 3.11 | 33 | 2.15.1 |
| community-service | 3.11 | 37 | 2.15.1 |

The shared Dockerfile installs this manifest with `-c constraints.txt` and
copies `apps/services/shared/` to runtime `shared/`. The listed service Dockerfiles
also consume this code or compatible PyJWT requirements. The separate
`copilot-api` JWT consumer passed its 11 existing tests; its complete ML image
was not built.

## Security scan: exact scope and remaining findings

Scans used pip-audit 2.10.1 and the PyPI advisory service on 2026-10-31, without
ignored advisories or automatic fixes. Dependency versions, advisory IDs,
aliases, and fix versions are embedded in [verification.json](verification.json);
long advisory descriptions are omitted and original report hashes are retained.

| Scan | Exit | Result |
| --- | --- | --- |
| PyJWT 2.10.1 alone | 1 | 22 raw advisory records, including CVE-2026-32597 |
| PyJWT 2.11.0 alone | 1 | 22 raw advisory records, including CVE-2026-32597 |
| PyJWT 2.15.1 alone | 0 | No known vulnerabilities |
| Complete constrained shared-auth requirements | 0 | 19 dependencies, no known vulnerabilities |
| Complete constrained shared requirements | 1 | 35 dependencies; pre-existing python-multipart findings |

The shared scan returned eight raw records representing **four distinct CVEs**
for unchanged `python-multipart==0.0.26`: CVE-2026-42561, CVE-2026-53538,
CVE-2026-53539, and CVE-2026-53540. PyJWT 2.15.1 has no findings in that scan.
This PR does not claim the complete shared dependency set is clean. The existing
python-multipart pin is unchanged to keep this repair limited to PyJWT.

### Constraints and the separate root lock

The existing root, AI, and field-management constraints, infrastructure
requirements, and root project PyJWT range already admit 2.15.1. There is no
scoped lock for either changed manifest, and their Docker/pip installation paths
do not consume the root `uv.lock`. No constraint or lock rewrite is needed for
these two installation paths.

**The root `uv.lock` remains vulnerable and unresolved:** it still locks PyJWT
2.11.0 and already contains metadata inconsistent with the root project. Its
TensorFlow/NumPy/Python resolver conflict belongs to the separate
`wip/python-security-lock-review-20261031` effort. Frozen root-lock installations
are not repaired by this PR. `pyproject.toml`, Python policy, all constraints,
and `uv.lock` remain byte-identical to the base; no manual lock editing or
resolver bypass was performed.

## Reproduction and CI

The new `Shared PyJWT Security` workflow installs both actual requirement files
with existing constraints, runs the affected-module/root-auth and Copilot
consumer tests on Python 3.11 and 3.12, checks the exact installed package,
audits **PyJWT only**, and uploads JUnit/environment/audit artifacts. It is a
scoped regression gate; the existing repository-wide security gates remain in
place. Python versions in this test matrix do not change project support policy.

Core local commands (after installing the two manifests and test dependencies):

```bash
python -m pip check
python -m pytest tests/unit/auth/ tests/unit/test_shared_auth.py \
  tests/unit/test_jwt_handler_comprehensive.py \
  tests/unit/shared/test_auth_jwt_handler.py \
  tests/unit/shared/test_auth_jwt_handler_extended.py \
  tests/unit/shared/auth/test_jwt_handler.py \
  tests/unit/shared/test_auth_dependencies.py \
  tests/unit/shared/test_auth_dependencies_extended.py \
  tests/unit/shared/test_jwt.py -q --tb=short --timeout=30
python -m pytest apps/services/copilot-api/tests/test_deps.py -q --tb=short
ruff check tests/unit/auth/test_shared_pyjwt_security.py
ruff format --check tests/unit/auth/test_shared_pyjwt_security.py
```

For the differential test, install an old PyJWT into an isolated target directory
and prepend that directory to `PYTHONPATH`, then execute
`test_shared_pyjwt_security.py::test_unknown_critical_extension_is_rejected`.
Both old versions must fail, while the candidate passes. Do not downgrade the
candidate environment itself.

For a full constrained requirements audit, create a temporary input file with
`-c /absolute/repo/constraints.txt` and `-r /absolute/repo/<requirements path>`;
run `python -m pip_audit -r <input> --strict --progress-spinner off --format json`.
For the package-only comparison use exact `PyJWT==<version>` inputs with
`--no-deps --disable-pip`; PyJWT has no mandatory dependencies on these Python
versions.

Local TestClient runs required an execution environment permitting its event-loop
socket pair. The restricted sandbox hung for both existing and new tests; the
unchanged suites completed outside that restriction. Existing tests also emit
short synthetic-key warnings and a Starlette TestClient deprecation. No live
deployment, database-backed login, image rebuild, or production rollout is
claimed here.
