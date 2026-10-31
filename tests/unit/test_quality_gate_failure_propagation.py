"""Exercise the workflow's actual shell boundary with controlled pytest exits."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/quality-gate.yml"


@pytest.fixture(scope="module")
def workflow():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _step(workflow, job: str, name: str):
    return next(step for step in workflow["jobs"][job]["steps"] if step.get("name") == name)


def _run_step(step, directory: Path, environment: dict[str, str]):
    return subprocess.run(
        ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c", step["run"]],
        cwd=directory,
        env={**os.environ, **environment},
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


@pytest.fixture
def capture_environment(tmp_path):
    executables = tmp_path / "bin"
    executables.mkdir()
    pytest_command = executables / "pytest"
    pytest_command.write_text(
        "#!/bin/sh\n"
        "printf '<coverage/>\\n' > coverage.xml\n"
        "printf '<testsuites/>\\n' > test-results.xml\n"
        "printf 'controlled pytest output\\nTOTAL 10 0 100%%\\n'\n"
        'exit "$FAKE_PYTEST_EXIT"\n',
        encoding="utf-8",
    )
    pytest_command.chmod(0o755)
    return {
        "PATH": str(executables) + os.pathsep + os.environ["PATH"],
        "GITHUB_OUTPUT": str(tmp_path / "step-output.txt"),
    }


def _outputs(environment):
    text = Path(environment["GITHUB_OUTPUT"]).read_text(encoding="utf-8")
    return dict(line.split("=", 1) for line in text.splitlines())


def _enforce(workflow, tmp_path, outputs, outcome="success"):
    return _run_step(
        _step(workflow, "tests", "Enforce test result after report upload"),
        tmp_path,
        {
            "TEST_STEP_OUTCOME": outcome,
            "TESTS_PASS": outputs.get("pass", ""),
            "PYTEST_EXIT_CODE": outputs.get("pytest_exit_code", ""),
            "LOG_EXIT_CODE": outputs.get("log_exit_code", ""),
        },
    )


@pytest.mark.parametrize("exit_code", [0, 1, 2, 3, 4, 5, 130])
def test_pytest_exit_is_recorded_then_enforced_after_reports(workflow, tmp_path, capture_environment, exit_code):
    capture_environment["FAKE_PYTEST_EXIT"] = str(exit_code)
    captured = _run_step(_step(workflow, "tests", "Run tests with coverage"), tmp_path, capture_environment)
    assert captured.returncode == 0, captured.stderr
    outputs = _outputs(capture_environment)
    assert outputs["pytest_exit_code"] == str(exit_code)
    assert outputs["log_exit_code"] == "0"
    assert outputs["pass"] == ("true" if exit_code == 0 else "false")
    assert outputs["coverage"] == "100"
    assert "controlled pytest output" in (tmp_path / "test-output.txt").read_text()
    assert (tmp_path / "coverage.xml").is_file()
    assert (tmp_path / "test-results.xml").is_file()
    assert _enforce(workflow, tmp_path, outputs).returncode == exit_code


def test_failed_log_capture_cannot_produce_a_passing_gate(workflow, tmp_path, capture_environment):
    tee = tmp_path / "bin/tee"
    tee.write_text("#!/bin/sh\ncat > /dev/null\nexit 9\n", encoding="utf-8")
    tee.chmod(0o755)
    capture_environment["FAKE_PYTEST_EXIT"] = "0"
    captured = _run_step(_step(workflow, "tests", "Run tests with coverage"), tmp_path, capture_environment)
    assert captured.returncode == 0, captured.stderr
    outputs = _outputs(capture_environment)
    assert outputs["pytest_exit_code"] == "0"
    assert outputs["log_exit_code"] == "9"
    assert outputs["pass"] == "false"
    assert _enforce(workflow, tmp_path, outputs).returncode != 0


@pytest.mark.parametrize(
    ("outcome", "outputs"),
    [
        ("skipped", {}),
        ("failure", {}),
        ("success", {}),
        ("success", {"pass": "true", "pytest_exit_code": "0"}),
        ("success", {"pass": "true", "pytest_exit_code": "invalid", "log_exit_code": "0"}),
        ("success", {"pass": "false", "pytest_exit_code": "0", "log_exit_code": "0"}),
    ],
)
def test_absent_or_inconsistent_test_evidence_fails_closed(workflow, tmp_path, outcome, outputs):
    assert _enforce(workflow, tmp_path, outputs, outcome).returncode != 0


def test_reports_are_uploaded_before_test_failure_is_enforced(workflow):
    steps = workflow["jobs"]["tests"]["steps"]
    capture = _step(workflow, "tests", "Run tests with coverage")
    upload = next(step for step in steps if step.get("uses", "").startswith("actions/upload-artifact@"))
    enforce = _step(workflow, "tests", "Enforce test result after report upload")
    assert steps.index(capture) < steps.index(upload) < steps.index(enforce)
    assert upload["if"] == enforce["if"] == "always()"
    assert upload["with"]["if-no-files-found"] == "error"
    assert {"test-output.txt", "coverage.xml", "test-results.xml"} <= set(upload["with"]["path"].splitlines())
    assert "continue-on-error" not in enforce


def _summary_environment(result: str, passed: str):
    return {
        "PYTHON_ISSUES": "0",
        "SQL_ISSUES": "0",
        "SPEC_VALID": "true",
        "CONTRACT_PASS": "true",
        "NEWMAN_PASS": "true",
        "BANDIT_ISSUES": "0",
        "SEMGREP_ISSUES": "0",
        "TESTS_RESULT": result,
        "TESTS_PASS": passed,
        "COVERAGE": "100",
    }


@pytest.mark.parametrize(
    ("result", "passed", "expected_exit"),
    [
        ("success", "true", 0),
        ("success", "false", 1),
        ("failure", "true", 1),
        ("skipped", "", 1),
        ("cancelled", "", 1),
        ("success", "", 1),
    ],
)
def test_aggregate_matches_actual_test_job_result(workflow, tmp_path, result, passed, expected_exit):
    environment = _summary_environment(result, passed)
    report = _run_step(_step(workflow, "quality-summary", "Generate Quality Report"), tmp_path, environment)
    assert report.returncode == 0, report.stderr
    report_text = (tmp_path / "quality-report.md").read_text(encoding="utf-8")
    assert ("BLOCKED" in report_text) == (expected_exit != 0)
    enforced = _run_step(
        _step(workflow, "quality-summary", "Enforce aggregated test result after reporting"), tmp_path, environment
    )
    assert enforced.returncode == expected_exit


@pytest.mark.parametrize("blocker", ["tests", "spec"])
def test_security_warning_cannot_replace_a_blocking_report(workflow, tmp_path, blocker):
    environment = _summary_environment("success", "true")
    environment["BANDIT_ISSUES"] = "11"
    if blocker == "tests":
        environment.update(TESTS_RESULT="failure", TESTS_PASS="false")
    else:
        environment["SPEC_VALID"] = "false"
    report = _run_step(_step(workflow, "quality-summary", "Generate Quality Report"), tmp_path, environment)
    assert report.returncode == 0, report.stderr
    decision = (tmp_path / "quality-report.md").read_text().split("### Gate Decision", 1)[1]
    assert "BLOCKED" in decision
    assert "WARNING" not in decision


def test_aggregate_enforcement_follows_report_and_comment(workflow):
    steps = workflow["jobs"]["quality-summary"]["steps"]
    report = _step(workflow, "quality-summary", "Generate Quality Report")
    comment = _step(workflow, "quality-summary", "Post Quality Report to PR")
    enforce = _step(workflow, "quality-summary", "Enforce aggregated test result after reporting")
    assert steps.index(report) < steps.index(comment) < steps.index(enforce)
    assert enforce["if"] == "always()"
    assert "continue-on-error" not in enforce
