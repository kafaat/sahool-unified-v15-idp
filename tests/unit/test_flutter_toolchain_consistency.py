"""Prevent Flutter SDK and localization drift across apps and their CI consumers.

Pub remains the compatibility solver. These tests check SDK/localization policy
and the existing CocoaPods integration, including release and preview jobs.
The primary app's explicit Flutter minimum is the canonical CI SDK version.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path

import pytest
import yaml
from packaging.specifiers import SpecifierSet
from packaging.version import Version

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = (
    "apps/mobile/pubspec.yaml",
    "apps/mobile/sahool_field_app/pubspec.yaml",
    "apps/mobile/sahool_app/pubspec.yaml",
    "packages/sahool-mobile-core/pubspec.yaml",
)
COCOAPODS_MANIFESTS = MANIFESTS[:2]
WORKFLOW_DIRS = (
    ".github/workflows",
    "apps/mobile/.github/workflows",
    "apps/mobile/sahool_field_app/.github/workflows",
)


def _yaml(path: str | Path) -> dict:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def _sdk_version(manifest: dict) -> str:
    constraint = manifest.get("environment", {}).get("flutter", "")
    match = re.fullmatch(r">=([0-9]+\.[0-9]+\.[0-9]+)", str(constraint))
    assert match, "Declare an explicit stable Flutter minimum in the primary pubspec."
    return match.group(1)


def _check_manifests(manifests: dict[str, dict]) -> None:
    primary = manifests[MANIFESTS[0]]
    _sdk_version(primary)
    environment = primary["environment"]
    dart = SpecifierSet(",".join(environment["sdk"].split()))
    assert Version("3.12.2") in dart, "The validated Dart SDK must remain supported."
    assert Version("3.13.0") not in dart, "Dart 3.13 requires a separately validated generator migration."
    intl = primary["dependencies"]["intl"]
    for path, manifest in manifests.items():
        assert manifest.get("environment") == environment, f"SDK declarations drifted: {path}"
        dependencies = manifest.get("dependencies", {})
        if "intl" in dependencies:
            assert dependencies["intl"] == intl, f"intl constraint drifted: {path}"
        overrides = manifest.get("dependency_overrides", {})
        assert not {"intl", "flutter_localizations"}.intersection(overrides), (
            f"Do not override Flutter's localization dependency resolution: {path}"
        )
        if path in COCOAPODS_MANIFESTS:
            config = manifest.get("flutter", {}).get("config", {})
            assert config.get("enable-swift-package-manager") is False, (
                f"Preserve CocoaPods until the flutter_native_splash SwiftPM migration is validated: {path}"
            )


def _resolve_workflow_value(value: str, workflow: dict, job: dict, step: dict) -> str:
    value = str(value)
    env_match = re.fullmatch(r"\$\{\{\s*env\.([A-Za-z_][A-Za-z0-9_]*)\s*\}\}", value)
    if env_match:
        environment = {**workflow.get("env", {}), **job.get("env", {}), **step.get("env", {})}
        return str(environment.get(env_match.group(1), ""))
    input_match = re.fullmatch(r"\$\{\{\s*inputs\.([A-Za-z_][A-Za-z0-9_-]*)\s*\}\}", value)
    if input_match:
        # PyYAML's YAML1.1 loader parses GitHub's unquoted `on` key as True.
        events = workflow.get("on", workflow.get(True, {}))
        inputs = events.get("workflow_call", {}).get("inputs", {})
        return str(inputs.get(input_match.group(1), {}).get("default", ""))
    return value


def _check_workflow(workflow: dict, sdk: str, path: str = "workflow") -> int:
    setups = 0
    for job_name, job in workflow.get("jobs", {}).items():
        if str(job.get("uses", "")).endswith("/reusable-setup.yml"):
            override = job.get("with", {}).get("flutter-version")
            if override is not None:
                assert _resolve_workflow_value(override, workflow, job, {}) == sdk, (
                    f"Reusable Flutter SDK override drifted: {path}:{job_name}"
                )
        for step in job.get("steps", []):
            if not str(step.get("uses", "")).startswith("subosito/flutter-action@"):
                continue
            setups += 1
            options = step.get("with", {})
            version = _resolve_workflow_value(options.get("flutter-version", ""), workflow, job, step)
            channel = _resolve_workflow_value(options.get("channel", "stable"), workflow, job, step)
            assert version == sdk, f"Flutter SDK pin drifted: {path}:{job_name}: {version!r} != {sdk!r}"
            assert channel == "stable", f"Flutter channel drifted: {path}:{job_name}"
    return setups


def test_all_mobile_manifests_share_sdk_and_intl_constraints() -> None:
    _check_manifests({path: _yaml(path) for path in MANIFESTS})


def test_all_flutter_ci_release_and_preview_jobs_use_the_declared_sdk() -> None:
    sdk = _sdk_version(_yaml(MANIFESTS[0]))
    setups = 0
    for directory in WORKFLOW_DIRS:
        for path in sorted((ROOT / directory).glob("*.y*ml")):
            setups += _check_workflow(_yaml(path), sdk, str(path.relative_to(ROOT)))
    assert setups, "No Flutter setup jobs were checked."


def test_committed_app_locks_share_localization_and_sdk_constraints() -> None:
    primary = _yaml(MANIFESTS[0])
    primary_lock = _yaml(Path(MANIFESTS[0]).with_name("pubspec.lock"))
    expected_intl = primary_lock["packages"]["intl"]["version"]
    for manifest_path in MANIFESTS[:-1]:
        lock_path = Path(manifest_path).with_name("pubspec.lock")
        assert (ROOT / lock_path).is_file(), f"Application lockfile is missing: {lock_path}"
        lock = _yaml(lock_path)
        assert lock["packages"]["intl"]["version"] == expected_intl, f"intl lock drifted: {lock_path}"
        assert lock["sdks"]["flutter"] == primary["environment"]["flutter"], (
            f"Flutter lock constraint drifted: {lock_path}"
        )
        assert lock["sdks"]["dart"] == primary["environment"]["sdk"], f"Dart lock constraint drifted: {lock_path}"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("flutter", ">=3.27.1", "SDK declarations drifted"),
        ("sdk", ">=3.2.0 <4.0.0", "SDK declarations drifted"),
        ("intl", "0.19.0", "intl constraint drifted"),
        ("override", "0.19.0", "Do not override"),
    ],
)
def test_guard_rejects_stale_secondary_app_or_core_constraints(field: str, value: str, message: str) -> None:
    manifests = {path: _yaml(path) for path in MANIFESTS}
    target = manifests["packages/sahool-mobile-core/pubspec.yaml"]
    if field in {"sdk", "flutter"}:
        target["environment"][field] = value
    elif field == "intl":
        target["dependencies"][field] = value
    else:
        target.setdefault("dependency_overrides", {})["intl"] = value
    with pytest.raises(AssertionError, match=message):
        _check_manifests(manifests)


def test_guard_requires_an_explicit_primary_flutter_sdk_floor() -> None:
    primary = _yaml(MANIFESTS[0])
    primary["environment"].pop("flutter", None)
    with pytest.raises(AssertionError, match="explicit stable Flutter minimum"):
        _sdk_version(primary)


def test_guard_rejects_broadening_all_apps_to_the_known_broken_dart_version() -> None:
    manifests = {path: _yaml(path) for path in MANIFESTS}
    for manifest in manifests.values():
        manifest["environment"]["sdk"] = ">=3.10.0 <4.0.0"
    with pytest.raises(AssertionError, match="separately validated generator migration"):
        _check_manifests(manifests)


@pytest.mark.parametrize("path", COCOAPODS_MANIFESTS)
@pytest.mark.parametrize("value", [None, True, "false"], ids=["missing", "enabled", "string-false"])
def test_guard_rejects_implicit_or_enabled_swiftpm_for_cocoapods_apps(path: str, value: object) -> None:
    manifests = {manifest_path: _yaml(manifest_path) for manifest_path in MANIFESTS}
    config = manifests[path]["flutter"]["config"]
    if value is None:
        config.pop("enable-swift-package-manager")
    else:
        config["enable-swift-package-manager"] = value
    with pytest.raises(AssertionError, match="Preserve CocoaPods"):
        _check_manifests(manifests)


@pytest.fixture
def workflow_fixture() -> dict:
    sdk = _sdk_version(_yaml(MANIFESTS[0]))
    return {
        "env": {"FLUTTER_VERSION": sdk},
        "jobs": {
            "build": {
                "steps": [
                    {"uses": "subosito/flutter-action@v2", "with": {"flutter-version": "${{ env.FLUTTER_VERSION }}"}}
                ]
            }
        },
    }


@pytest.mark.parametrize("scope", ["workflow", "job", "step", "literal", "unversioned", "channel"])
def test_guard_rejects_stale_shadowed_or_floating_workflow_sdks(workflow_fixture: dict, scope: str) -> None:
    workflow = copy.deepcopy(workflow_fixture)
    job = workflow["jobs"]["build"]
    step = job["steps"][0]
    if scope in {"workflow", "job", "step"}:
        target = {"workflow": workflow, "job": job, "step": step}[scope]
        target.setdefault("env", {})["FLUTTER_VERSION"] = "3.27.1"
    elif scope == "literal":
        step["with"]["flutter-version"] = "3.27.1"
    elif scope == "unversioned":
        step["with"].pop("flutter-version")
    else:
        step["with"]["channel"] = "beta"
    with pytest.raises(AssertionError, match="Flutter (SDK pin|channel) drifted"):
        _check_workflow(workflow, _sdk_version(_yaml(MANIFESTS[0])))


def test_guard_checks_reusable_workflow_default() -> None:
    workflow = _yaml(".github/workflows/reusable-setup.yml")
    events = workflow.get("on", workflow.get(True, {}))
    events["workflow_call"]["inputs"]["flutter-version"]["default"] = "3.27.1"
    with pytest.raises(AssertionError, match="Flutter SDK pin drifted"):
        _check_workflow(workflow, _sdk_version(_yaml(MANIFESTS[0])))


def test_guard_checks_reusable_workflow_caller_override() -> None:
    workflow = {
        "jobs": {
            "build": {
                "uses": "./.github/workflows/reusable-setup.yml",
                "with": {"setup-flutter": True, "flutter-version": "3.27.1"},
            }
        }
    }
    with pytest.raises(AssertionError, match="Reusable Flutter SDK override drifted"):
        _check_workflow(workflow, _sdk_version(_yaml(MANIFESTS[0])))
