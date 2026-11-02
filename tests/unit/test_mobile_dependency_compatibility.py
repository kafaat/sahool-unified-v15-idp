"""Keep the native SQLCipher and generator migration atomic.

These checks enforce the documented compatibility boundary, not dependency
resolution. Flutter pub still resolves the graph and validates package hashes.
"""

from __future__ import annotations

import re
import shlex
from fnmatch import fnmatchcase
from pathlib import Path

import pytest
import yaml
from packaging.specifiers import SpecifierSet
from packaging.version import Version

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]
GENERATOR_MANIFESTS = (
    "apps/mobile/pubspec.yaml",
    "apps/mobile/sahool_field_app/pubspec.yaml",
    "packages/sahool-mobile-core/pubspec.yaml",
)
CONSUMER_MANIFEST = "apps/mobile/sahool_app/pubspec.yaml"
MANIFESTS = (*GENERATOR_MANIFESTS, CONSUMER_MANIFEST)
APP_MANIFESTS = (*GENERATOR_MANIFESTS[:2], CONSUMER_MANIFEST)
# First incompatible version, verified against the published package manifests.
BOUNDARIES = {
    "drift": "2.29.0",
    "drift_dev": "2.28.1",
    "sqlite3": "3.0.0",
    "sqlcipher_flutter_libs": "0.7.0",
    "flutter_riverpod": "3.0.0",
    "riverpod_annotation": "3.0.0",
    "riverpod_generator": "2.6.5",
    "freezed": "3.0.0",
    "freezed_annotation": "3.0.0",
    "riverpod": "3.0.0",
    "analyzer": "8.0.0",
    "build": "3.0.0",
    "source_gen": "3.0.0",
    "riverpod_analyzer_utils": "0.5.10",
}
DIRECT_PACKAGES = set(BOUNDARIES) - {"riverpod", "analyzer", "build", "source_gen", "riverpod_analyzer_utils"}
RUNTIME_PACKAGES = {
    "drift",
    "sqlite3",
    "sqlcipher_flutter_libs",
    "flutter_riverpod",
    "riverpod",
    "riverpod_annotation",
    "freezed_annotation",
}


def _load(path: str | Path) -> dict:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def _constraint(value: str) -> SpecifierSet:
    """Handle the stable exact, caret and comparison forms used by these apps."""
    value = str(value)
    if value.startswith("^"):
        release = Version(value[1:]).release
        major, minor, patch = release
        upper = (major + 1, 0, 0) if major else ((0, minor + 1, 0) if minor else (0, 0, patch + 1))
        return SpecifierSet(f">={value[1:]},<{'.'.join(map(str, upper))}")
    if re.fullmatch(r"\d+\.\d+\.\d+", value):
        return SpecifierSet(f"=={value}")
    return SpecifierSet(",".join(value.split()))


def _check_manifest(manifest: dict, *, generators: bool = True) -> None:
    dependencies = {**manifest.get("dependencies", {}), **manifest.get("dev_dependencies", {})}
    assert not set(BOUNDARIES).intersection(manifest.get("dependency_overrides", {})), (
        "Do not bypass the native storage/generator compatibility graph with an override."
    )
    required = DIRECT_PACKAGES if generators else {"flutter_riverpod", "sahool_mobile_core"}
    assert required <= dependencies.keys(), (
        f"Missing compatibility dependencies: {sorted(required - dependencies.keys())}"
    )
    for name, boundary in BOUNDARIES.items():
        if name not in dependencies:
            continue
        assert not re.search(r"\d+-", str(dependencies[name])), f"Unvalidated prerelease constraint: {name}"
        constraint = _constraint(dependencies[name])
        # Require an actual upper bound; merely excluding one version is insufficient.
        bounded = any(
            (item.operator == "<" and Version(item.version) <= Version(boundary))
            or (item.operator in {"<=", "=="} and Version(item.version) < Version(boundary))
            for item in constraint
        )
        assert bounded, f"{name} requires a validated generator/encryption migration at {boundary}."


def _check_lock(manifest: dict, lock: dict, *, generators: bool = True) -> None:
    dependencies = {**manifest["dependencies"], **manifest["dev_dependencies"]}
    required = set(BOUNDARIES) if generators else RUNTIME_PACKAGES
    packages = lock["packages"]
    assert required <= packages.keys(), f"Missing compatibility lock entries: {sorted(required - packages.keys())}"
    for name, boundary in BOUNDARIES.items():
        if name not in packages:
            continue
        version = Version(packages[name]["version"])
        assert not version.is_prerelease, f"Unvalidated prerelease dependency: {name}"
        assert version < Version(boundary), f"Incompatible locked dependency: {name}"
        if name in dependencies:
            assert version in _constraint(dependencies[name]), f"Manifest/lock mismatch: {name}"


@pytest.mark.parametrize("path", MANIFESTS)
def test_native_storage_and_generator_constraints_remain_compatible(path: str) -> None:
    _check_manifest(_load(path), generators=path in GENERATOR_MANIFESTS)


@pytest.mark.parametrize("path", APP_MANIFESTS)
def test_existing_app_locks_satisfy_supported_dependency_constraints(path: str) -> None:
    _check_lock(_load(path), _load(Path(path).with_name("pubspec.lock")), generators=path in GENERATOR_MANIFESTS)


@pytest.mark.parametrize("name,boundary", BOUNDARIES.items())
def test_guard_rejects_a_partial_major_or_generator_upgrade(name: str, boundary: str) -> None:
    manifest = _load(MANIFESTS[0])
    section = "dependencies" if name in manifest["dependencies"] else "dev_dependencies"
    manifest[section][name] = f"^{boundary}"
    with pytest.raises(AssertionError, match=f"{name} requires a validated"):
        _check_manifest(manifest)


def test_guard_rejects_dependency_override_bypassing_the_encryption_boundary() -> None:
    manifest = _load(MANIFESTS[0])
    manifest.setdefault("dependency_overrides", {})["sqlite3"] = "^3.3.3"
    with pytest.raises(AssertionError, match="Do not bypass"):
        _check_manifest(manifest)


def test_guard_rejects_the_pr_freezed_prerelease_constraint() -> None:
    manifest = _load(MANIFESTS[0])
    manifest["dev_dependencies"]["freezed"] = "3.2.6-dev.1"
    with pytest.raises(AssertionError, match="Unvalidated prerelease constraint"):
        _check_manifest(manifest)


@pytest.mark.parametrize("name,version", [("drift", "2.34.0"), ("freezed", "3.2.6-dev.1")])
def test_guard_rejects_the_incompatible_pr_lock_even_with_unchanged_manifest(name: str, version: str) -> None:
    manifest = _load(MANIFESTS[0])
    lock = _load(Path(MANIFESTS[0]).with_name("pubspec.lock"))
    lock["packages"][name]["version"] = version
    with pytest.raises(AssertionError, match="Incompatible locked|Unvalidated prerelease"):
        _check_lock(manifest, lock)


@pytest.mark.parametrize(
    "name,version",
    [
        ("analyzer", "12.1.0"),
        ("build", "4.0.6"),
        ("source_gen", "4.2.3"),
        ("riverpod_analyzer_utils", "0.5.10"),
        ("riverpod", "3.3.2"),
    ],
)
def test_guard_rejects_transitive_override_bypasses(name: str, version: str) -> None:
    manifest = _load(MANIFESTS[0])
    manifest.setdefault("dependency_overrides", {})[name] = f"^{version}"
    with pytest.raises(AssertionError, match="Do not bypass"):
        _check_manifest(manifest)


@pytest.mark.parametrize(
    "name,version",
    [
        ("analyzer", "12.1.0"),
        ("build", "4.0.6"),
        ("source_gen", "4.2.3"),
        ("riverpod_analyzer_utils", "0.5.10"),
        ("riverpod", "3.3.2"),
    ],
)
def test_guard_rejects_incompatible_transitive_lock_versions(name: str, version: str) -> None:
    manifest = _load(MANIFESTS[0])
    lock = _load(Path(MANIFESTS[0]).with_name("pubspec.lock"))
    lock["packages"][name]["version"] = version
    with pytest.raises(AssertionError, match="Incompatible locked"):
        _check_lock(manifest, lock)


@pytest.mark.parametrize("name,boundary", BOUNDARIES.items())
def test_unified_app_cannot_override_its_shared_core_compatibility_boundary(name: str, boundary: str) -> None:
    manifest = _load(CONSUMER_MANIFEST)
    manifest.setdefault("dependency_overrides", {})[name] = f"^{boundary}"
    with pytest.raises(AssertionError, match="Do not bypass"):
        _check_manifest(manifest, generators=False)


@pytest.mark.parametrize("name", sorted(RUNTIME_PACKAGES))
def test_unified_app_lock_cannot_select_an_incompatible_shared_core_runtime(name: str) -> None:
    manifest = _load(CONSUMER_MANIFEST)
    lock = _load(Path(CONSUMER_MANIFEST).with_name("pubspec.lock"))
    lock["packages"][name]["version"] = BOUNDARIES[name]
    with pytest.raises(AssertionError, match="Incompatible locked"):
        _check_lock(manifest, lock, generators=False)


def test_unified_app_lock_must_include_its_native_runtime_closure() -> None:
    manifest = _load(CONSUMER_MANIFEST)
    lock = _load(Path(CONSUMER_MANIFEST).with_name("pubspec.lock"))
    lock["packages"].pop("sqlite3")
    with pytest.raises(AssertionError, match="Missing compatibility lock entries"):
        _check_lock(manifest, lock, generators=False)


def _check_mobile_ci(workflow: dict) -> None:
    events = workflow.get("on", workflow.get(True, {}))
    inputs = [
        *MANIFESTS,
        *(str(Path(path).with_name("pubspec.lock")) for path in APP_MANIFESTS),
        ".github/dependabot.yml",
        "constraints.txt",
        "tests/unit/test_flutter_toolchain_consistency.py",
        "tests/unit/test_mobile_dependency_compatibility.py",
    ]
    for event in ("push", "pull_request"):
        patterns = events[event]["paths"]
        for path in inputs:
            assert any(fnmatchcase(path, pattern) for pattern in patterns), f"Mobile CI misses {event} input: {path}"
    steps = workflow["jobs"]["analyze"]["steps"]
    policy = next((step for step in steps if step.get("id") == "mobile-dependency-policy"), None)
    assert policy, "Mobile CI must execute the dependency policy."
    assert policy.get("continue-on-error", False) is False and "if" not in policy, (
        "The mobile dependency policy must run unconditionally and propagate failures."
    )
    assert policy.get("working-directory") == "${{ github.workspace }}", "Run the policy from the repository root."
    command = shlex.split(policy["run"])
    assert command[:4] == ["python", "-m", "pytest", "-q"] and not {"|", "||", ";"}.intersection(command), (
        "Run pytest directly without masking its exit status."
    )
    assert {
        "tests/unit/test_flutter_toolchain_consistency.py",
        "tests/unit/test_mobile_dependency_compatibility.py",
    } <= set(command), "Execute both mobile policy suites."


def test_mobile_ci_checks_all_dependency_inputs_and_propagates_policy_failures() -> None:
    _check_mobile_ci(_load(".github/workflows/mobile-ci.yml"))


@pytest.mark.parametrize("mutation", ["core_path", "dependabot_path", "missing_step", "soft_failure", "wrong_cwd"])
def test_ci_guard_rejects_missing_inputs_or_a_bypassed_policy(mutation: str) -> None:
    workflow = _load(".github/workflows/mobile-ci.yml")
    events = workflow.get("on", workflow.get(True, {}))
    steps = workflow["jobs"]["analyze"]["steps"]
    policy = next(step for step in steps if step.get("id") == "mobile-dependency-policy")
    if mutation in {"core_path", "dependabot_path"}:
        target = "packages/sahool-mobile-core/**" if mutation == "core_path" else ".github/dependabot.yml"
        events["pull_request"]["paths"].remove(target)
    elif mutation == "missing_step":
        steps.remove(policy)
    elif mutation == "soft_failure":
        policy["continue-on-error"] = True
    else:
        policy["working-directory"] = "apps/mobile"
    with pytest.raises(AssertionError):
        _check_mobile_ci(workflow)
