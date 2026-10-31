"""Deterministic monitor-fetch regressions: no GitHub requests or real sleeps."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import textwrap
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parents[2] / "scripts/ci/fetch_pr_status.py"
_SPEC = importlib.util.spec_from_file_location("pr_status_fetch", _PATH)
monitor = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(monitor)

pytestmark = pytest.mark.unit


def pr(number: int = 1, *, checks=None) -> dict:
    return {
        "number": number,
        "title": "Test PR",
        "headRefName": "fix/example",
        "baseRefName": "main",
        "mergeable": "MERGEABLE",
        "statusCheckRollup": checks,
        "updatedAt": "2026-10-31T12:00:00Z",
        "createdAt": "2026-10-30T12:00:00Z",
    }


def response(stdout: str = "[]", *, code: int = 0, stderr: str = ""):
    return subprocess.CompletedProcess(["gh", "pr", "list"], code, stdout, stderr)


def fake_runner(results):
    pending = iter(results)
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        result = next(pending)
        if isinstance(result, Exception):
            raise result
        return result

    return run, calls


@pytest.mark.parametrize("diagnostic", ["HTTP 502: 502 Bad Gateway", "unexpected end of JSON input"])
def test_retry_cli_failure_then_return_valid_snapshot(diagnostic):
    data = [pr()]
    run, calls = fake_runner([response(code=1, stderr=diagnostic), response(json.dumps(data))])
    delays = []
    assert monitor.fetch_pr_status("owner/repository", runner=run, sleeper=delays.append) == data
    assert len(calls) == 2
    assert delays == [2]
    assert calls[0][0][:5] == ["gh", "pr", "list", "--repo", "owner/repository"]
    assert "--limit" in calls[0][0]
    assert calls[0][1]["timeout"] == 60


def test_retry_truncated_json_even_when_cli_reports_success():
    run, calls = fake_runner([response('[{"number":'), response(json.dumps([pr()]))])
    delays = []
    assert monitor.fetch_pr_status("owner/repository", runner=run, sleeper=delays.append) == [pr()]
    assert len(calls) == 2
    assert delays == [2]


def test_valid_empty_list_is_success_without_retry():
    run, calls = fake_runner([response("[]")])
    delays = []
    assert monitor.fetch_pr_status("owner/repository", runner=run, sleeper=delays.append) == []
    assert len(calls) == 1
    assert delays == []


def test_timeout_is_bounded_and_retried():
    run, calls = fake_runner([subprocess.TimeoutExpired(["gh"], 60), response(json.dumps([pr()]))])
    delays = []
    assert monitor.fetch_pr_status("owner/repository", runner=run, sleeper=delays.append) == [pr()]
    assert len(calls) == 2
    assert delays == [2]


@pytest.mark.parametrize(
    "failed_response",
    [response(code=1, stderr="HTTP 502"), response(""), response('[{"number":'), response('{"errors": []}')],
    ids=["cli-error", "empty-output", "truncated-json", "error-object"],
)
def test_retry_exhaustion_never_returns_empty_success(failed_response):
    run, calls = fake_runner([failed_response] * 3)
    delays = []
    with pytest.raises(monitor.FetchError, match="after 3 attempts"):
        monitor.fetch_pr_status("owner/repository", runner=run, sleeper=delays.append)
    assert len(calls) == 3
    assert delays == [2, 4]


def test_missing_gh_fails_immediately_without_retry():
    run, calls = fake_runner([FileNotFoundError("gh unavailable")])
    delays = []
    with pytest.raises(monitor.FetchError, match="Cannot execute GitHub CLI"):
        monitor.fetch_pr_status("owner/repository", runner=run, sleeper=delays.append)
    assert len(calls) == 1
    assert delays == []


@pytest.mark.parametrize("invalid", [None, {}, [None], [{}], [pr(), pr()]])
def test_invalid_response_shape_cannot_become_a_snapshot(invalid):
    with pytest.raises(ValueError):
        monitor.validate_pr_data(json.dumps(invalid))


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_nonstandard_json_constants_are_rejected(constant):
    with pytest.raises(ValueError, match="Nonstandard JSON constant"):
        monitor.validate_pr_data(f"[{constant}]")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("number", True),
        ("number", 0),
        ("title", None),
        ("headRefName", ""),
        ("mergeable", "invalid"),
        ("updatedAt", "not-a-date"),
        ("createdAt", "2026-10-31"),
        ("statusCheckRollup", {}),
        ("statusCheckRollup", [{}]),
        ("statusCheckRollup", [{"conclusion": 1}]),
    ],
)
def test_invalid_fields_cannot_produce_false_counts(field, value):
    item = pr()
    item[field] = value
    with pytest.raises(ValueError):
        monitor.validate_pr_data(json.dumps([item]))


def test_missing_status_data_is_rejected():
    item = pr()
    del item["statusCheckRollup"]
    with pytest.raises(ValueError, match="missing statusCheckRollup"):
        monitor.validate_pr_data(json.dumps([item]))


@pytest.mark.parametrize(
    "checks", [None, [], [{"conclusion": None}], [{"conclusion": "FAILURE"}], [{"state": "SUCCESS"}]]
)
def test_legitimate_check_run_and_status_context_shapes_are_accepted(checks):
    data = [pr(checks=checks)]
    assert monitor.validate_pr_data(json.dumps(data)) == data


def test_saturated_limit_cannot_be_reported_as_complete():
    data = [pr(number) for number in range(1, monitor.PR_LIMIT + 1)]
    with pytest.raises(ValueError, match="completeness is unproven"):
        monitor.validate_pr_data(json.dumps(data))


@pytest.mark.parametrize("existing", [False, True])
def test_exhaustion_returns_nonzero_without_publishing_partial_or_stale_data(tmp_path, monkeypatch, existing):
    destination = tmp_path / "pr-data.json"
    if existing:
        destination.write_text("previous snapshot\n", encoding="utf-8")
    run, calls = fake_runner([response('[{"number":')] * 3)
    monkeypatch.setattr(monitor.subprocess, "run", run)
    monkeypatch.setattr(monitor.time, "sleep", lambda _: None)
    assert monitor.main(["--repository", "owner/repository", "--output", str(destination)]) == 1
    assert len(calls) == 3
    if existing:
        assert destination.read_text(encoding="utf-8") == "previous snapshot\n"
    else:
        assert not destination.exists()
    assert not list(tmp_path.glob(".pr-data.json.*"))


def test_success_publishes_validated_empty_snapshot(tmp_path, monkeypatch):
    destination = tmp_path / "pr-data.json"
    destination.write_text("previous snapshot\n", encoding="utf-8")
    run, _ = fake_runner([response("[]")])
    monkeypatch.setattr(monitor.subprocess, "run", run)
    assert monitor.main(["--repository", "owner/repository", "--output", str(destination)]) == 0
    assert json.loads(destination.read_text(encoding="utf-8")) == []
    assert not list(tmp_path.glob(".pr-data.json.*"))


def test_failed_atomic_publish_preserves_existing_snapshot(tmp_path, monkeypatch):
    destination = tmp_path / "pr-data.json"
    destination.write_text("previous snapshot\n", encoding="utf-8")

    def fail_replace(*_):
        raise OSError("simulated publication failure")

    monkeypatch.setattr(monitor.os, "replace", fail_replace)
    with pytest.raises(OSError, match="publication failure"):
        monitor.write_snapshot(destination, [pr()])
    assert destination.read_text(encoding="utf-8") == "previous snapshot\n"
    assert not list(tmp_path.glob(".pr-data.json.*"))


def _run_status_step(tmp_path, data):
    """Execute the workflow's fetch/helper/jq/output path with a read-only fake gh."""
    executables = tmp_path / "bin"
    executables.mkdir()
    fake_gh = executables / "gh"
    fake_gh.write_text(
        '#!/bin/sh\nif [ "$1" != "pr" ] || [ "$2" != "list" ]; then exit 90; fi\ncat "$FAKE_PR_DATA"\n',
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    source = tmp_path / "gh-response.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    helper = tmp_path / "scripts/ci/fetch_pr_status.py"
    helper.parent.mkdir(parents=True)
    helper.write_text(_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    output = tmp_path / "step-output.txt"
    workflow = (_PATH.parents[2] / ".github/workflows/pr-status-monitor.yml").read_text(encoding="utf-8")
    step = workflow.split("      - name: Check PR status\n", 1)[1]
    script = step.split("        run: |\n", 1)[1].split("\n      - name: Upload PR data", 1)[0]
    environment = {
        **os.environ,
        "PATH": str(executables) + os.pathsep + os.environ["PATH"],
        "FAKE_PR_DATA": str(source),
        "GITHUB_REPOSITORY": "owner/repository",
        "GITHUB_OUTPUT": str(output),
    }
    result = subprocess.run(
        ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c", textwrap.dedent(script)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads((tmp_path / "pr-data.json").read_text(encoding="utf-8")) == data
    return dict(line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines())


@pytest.mark.parametrize(
    ("checks", "failing"),
    [
        (None, "0"),
        ([], "0"),
        ([{"conclusion": "SUCCESS"}], "0"),
        ([{"conclusion": "FAILURE"}], "1"),
        ([{"state": "SUCCESS"}], "0"),
        ([{"state": "FAILURE"}], "1"),
        ([{"state": "ERROR"}], "1"),
        ([{"conclusion": "SUCCESS"}, {"conclusion": "FAILURE"}, {"state": "ERROR"}], "1"),
    ],
    ids=[
        "null",
        "empty",
        "check-success",
        "check-failure",
        "status-success",
        "status-failure",
        "status-error",
        "mixed",
    ],
)
def test_actual_status_step_counts_check_runs_and_legacy_status_contexts(tmp_path, checks, failing):
    item = pr(checks=checks)
    item["updatedAt"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert _run_status_step(tmp_path, [item]) == {
        "total_prs": "1",
        "conflicted_prs": "0",
        "failing_ci_prs": failing,
        "stale_prs": "0",
    }


def test_actual_status_step_reports_valid_empty_snapshot(tmp_path):
    assert _run_status_step(tmp_path, []) == {
        "total_prs": "0",
        "conflicted_prs": "0",
        "failing_ci_prs": "0",
        "stale_prs": "0",
    }


def test_actual_status_step_counts_overlapping_conflicts_failures_and_staleness(tmp_path):
    current = datetime.now(UTC)
    conflicted = pr(1, checks=[{"conclusion": "FAILURE"}, {"state": "ERROR"}])
    conflicted["mergeable"] = "CONFLICTING"
    conflicted["updatedAt"] = (current - timedelta(days=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
    healthy = pr(2, checks=[{"conclusion": "SUCCESS"}])
    healthy["updatedAt"] = current.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert _run_status_step(tmp_path, [conflicted, healthy]) == {
        "total_prs": "2",
        "conflicted_prs": "1",
        "failing_ci_prs": "1",
        "stale_prs": "1",
    }


def test_report_does_not_claim_readiness_or_subtract_overlapping_failures(tmp_path):
    """Execute the real report step with a PR that is both conflicted and failing."""
    workflow = (_PATH.parents[2] / ".github/workflows/pr-status-monitor.yml").read_text(encoding="utf-8")
    report_step = workflow.split("      - name: Generate report\n", 1)[1]
    script = report_step.split("        run: |\n", 1)[1].split("\n      - name: Upload report", 1)[0]
    script = textwrap.dedent(script)
    values = {
        "needs.monitor-prs.outputs.total_prs": "2",
        "needs.monitor-prs.outputs.conflicted_prs": "1",
        "needs.monitor-prs.outputs.failing_ci_prs": "2",
        "needs.monitor-prs.outputs.stale_prs": "0",
        "github.repository": "owner/repository",
    }
    for expression, value in values.items():
        script = script.replace("${{ " + expression + " }}", value)
    assert "${{" not in script
    mergeable = pr(1, checks=[{"conclusion": "FAILURE"}])
    conflicted = pr(2, checks=[{"conclusion": "FAILURE"}])
    conflicted["mergeable"] = "CONFLICTING"
    (tmp_path / "pr-data.json").write_text(json.dumps([mergeable, conflicted]), encoding="utf-8")
    result = subprocess.run(["bash", "-e", "-c", script], cwd=tmp_path, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    reports = list(tmp_path.glob("pr-health-report-*.md"))
    assert len(reports) == 1
    report = reports[0].read_text(encoding="utf-8")
    assert "**Total Open PRs**: 2" in report
    assert "**Conflicted PRs**: 1" in report
    assert "**Failing CI**: 2" in report
    assert "Ready" not in report
    assert "🟢 Mergeable" in report
    assert "🔴 Conflicts" in report
    assert "$(date" not in report
    assert "$((" not in report
