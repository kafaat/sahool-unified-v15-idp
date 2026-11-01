"""Reject stale root lock metadata and regressions in the repaired ML/security closure.

These checks are offline. The resolver and wheel-install acceptance commands are
``uv lock --check`` and ``uv sync --all-extras --frozen`` for the target runtime.
"""

from __future__ import annotations

import copy
import tomllib
from collections import Counter
from pathlib import Path

import pytest
from packaging.markers import Marker, default_environment
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[2]
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
LOCK = tomllib.loads((ROOT / "uv.lock").read_text())
SECURITY_FLOORS = {
    "aiohttp": "3.14.4",
    "black": "26.10.1",
    "filelock": "4.2.1",
    "idna": "3.15",
    "keras": "3.15.0",
    "multidict": "6.9.1",
    "opentelemetry-api": "1.45.1",
    "pygments": "2.20.0",
    "pyjwt": "2.15.1",
    "requests": "2.33.0",
    "setuptools": "84.1.0",
    "starlette": "1.3.1",
    "urllib3": "2.8.0",
    "virtualenv": "21.14.10",
    "cryptography": "50.0.2",
    "pillow": "13.0.0",
    "anyio": "4.14.2",
    "certifi": "2026.10.18",
}


def _environment(python_version: str, extra: str = "") -> dict[str, str]:
    return {
        **default_environment(),
        "python_version": python_version,
        "python_full_version": f"{python_version}.0",
        "extra": extra,
    }


def _root_package(lock: dict) -> dict:
    return next(package for package in lock["package"] if package["name"] == canonicalize_name(PROJECT["name"]))


def _requirement_key(requirement: Requirement) -> tuple:
    return canonicalize_name(requirement.name), tuple(sorted(requirement.extras)), str(requirement.specifier)


def _assert_current_metadata(project: dict, lock: dict, python_version: str) -> None:
    """Compare semantics; uv normalizes python_version to python_full_version."""
    root = _root_package(lock)
    assert lock["requires-python"] == project["requires-python"]
    assert root["version"] == project["version"]
    groups = project["optional-dependencies"]
    assert set(root["metadata"]["provides-extras"]) == set(groups)
    metadata = root["metadata"]["requires-dist"]
    for group, values in groups.items():
        env = _environment(python_version, group)
        declared = [Requirement(value) for value in values]
        expected = Counter(_requirement_key(req) for req in declared if req.marker is None or req.marker.evaluate(env))
        actual = Counter()
        for entry in metadata:
            if entry.get("marker") and not Marker(entry["marker"]).evaluate(env):
                continue
            extras = f"[{','.join(entry['extras'])}]" if entry.get("extras") else ""
            req = Requirement(entry["name"] + extras + entry.get("specifier", ""))
            actual[_requirement_key(req)] += 1
        assert actual == expected, f"Stale uv.lock metadata for {group} on Python {python_version}"


@pytest.mark.parametrize("python_version", ["3.11", "3.12", "3.13", "3.14"])
def test_root_lock_metadata_matches_current_project(python_version):
    _assert_current_metadata(PROJECT, LOCK, python_version)


def test_python_support_policy_is_preserved():
    assert PROJECT["requires-python"] == LOCK["requires-python"] == ">=3.11"


def test_active_root_auth_does_not_reintroduce_obsolete_jose_closure():
    requirements = [Requirement(value) for value in PROJECT["optional-dependencies"]["infrastructure"]]
    assert any(canonicalize_name(req.name) == "pyjwt" for req in requirements)
    assert not {"python-jose", "ecdsa"} & {package["name"] for package in LOCK["package"]}


@pytest.mark.parametrize("python_version", ["3.11", "3.12", "3.13", "3.14"])
def test_locked_versions_respect_canonical_constraints(python_version):
    env = _environment(python_version)
    packages = [
        package
        for package in LOCK["package"]
        if not package.get("resolution-markers")
        or any(Marker(marker).evaluate(env) for marker in package["resolution-markers"])
    ]
    for line in (ROOT / "constraints.txt").read_text().splitlines():
        value = line.split("#", 1)[0].strip()
        if not value:
            continue
        requirement = Requirement(value)
        if requirement.marker is not None and not requirement.marker.evaluate(env):
            continue
        for package in packages:
            if canonicalize_name(requirement.name) == package["name"]:
                assert package["version"] in requirement.specifier, (python_version, value, package["version"])


@pytest.mark.parametrize("name,minimum", SECURITY_FLOORS.items())
def test_locked_security_versions_meet_patched_floor(name, minimum):
    versions = [Version(package["version"]) for package in LOCK["package"] if package["name"] == name]
    assert versions, f"{name} missing from root lock"
    assert all(version >= Version(minimum) for version in versions), (name, versions)


@pytest.mark.parametrize("python_version,major", [("3.11", 1), ("3.12", 1), ("3.13", 2), ("3.14", 2)])
def test_numpy_partition_matches_project_constraints_and_lock(python_version, major):
    env = _environment(python_version)
    declared = [Requirement(value) for value in PROJECT["optional-dependencies"]["ml"]]
    constraints = [
        Requirement(line.split("#", 1)[0].strip())
        for line in (ROOT / "constraints.txt").read_text().splitlines()
        if line.split("#", 1)[0].strip()
    ]
    requirements = [req for req in declared if req.name == "numpy" and (req.marker is None or req.marker.evaluate(env))]
    active_constraints = [
        req for req in constraints if req.name == "numpy" and (req.marker is None or req.marker.evaluate(env))
    ]
    resolved = [
        entry
        for entry in _root_package(LOCK)["optional-dependencies"]["ml"]
        if entry["name"] == "numpy" and (not entry.get("marker") or Marker(entry["marker"]).evaluate(env))
    ]
    assert len(requirements) == len(active_constraints) == len(resolved) == 1
    version = Version(resolved[0]["version"])
    assert version.major == major
    assert version in requirements[0].specifier and version in active_constraints[0].specifier
    assert Version("2.5.0") not in requirements[0].specifier
    if major == 2:
        assert version >= Version("2.1.0"), "ml-dtypes requires NumPy >=2.1 on Python 3.13+"


def test_tensorflow_feature_is_not_removed_on_newer_python():
    requirements = [Requirement(value) for value in PROJECT["optional-dependencies"]["ml"]]
    tensorflow = [req for req in requirements if req.name == "tensorflow-cpu"]
    assert len(tensorflow) == 1
    assert tensorflow[0].marker is None
    assert str(tensorflow[0].specifier) == "==2.21.0"
    entries = [
        entry for entry in _root_package(LOCK)["optional-dependencies"]["ml"] if entry["name"] == "tensorflow-cpu"
    ]
    assert len(entries) == 1 and not entries[0].get("marker")


@pytest.mark.parametrize("mutation", ["stale_pyjwt", "missing_tensorflow", "stale_extra"])
def test_metadata_guard_rejects_stale_lock(mutation):
    stale = copy.deepcopy(LOCK)
    metadata = _root_package(stale)["metadata"]
    if mutation == "stale_pyjwt":
        next(entry for entry in metadata["requires-dist"] if entry["name"] == "pyjwt")["specifier"] = ">=2.8.0,<3.0.0"
    elif mutation == "missing_tensorflow":
        metadata["requires-dist"] = [entry for entry in metadata["requires-dist"] if entry["name"] != "tensorflow-cpu"]
    else:
        metadata["provides-extras"].append("removed-extra")
    with pytest.raises(AssertionError):
        _assert_current_metadata(PROJECT, stale, "3.13")
