"""PR monitor transient failures must not become successful empty reports."""

import importlib.util
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

SPEC = importlib.util.spec_from_file_location(
    "fetch_pr_status", Path(__file__).resolve().parents[2] / "scripts/ci/fetch_pr_status.py"
)
fetch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetch)


def result(code=0, stdout="[]", stderr=""):
    return subprocess.CompletedProcess(fetch.COMMAND, code, stdout, stderr)


@pytest.mark.parametrize("status", [408, 429, 500, 502, 503, 504])
def test_transient_failure_then_success(status):
    with (
        patch.object(
            fetch.subprocess,
            "run",
            side_effect=[result(1, "partial", f"HTTP {status}: failure"), result(stdout='[{"number": 7}]')],
        ) as gh,
        patch.object(fetch.time, "sleep") as sleep,
    ):
        assert fetch.fetch_pr_status() == [{"number": 7}]
    assert gh.call_count == 2
    sleep.assert_called_once_with(2)
    assert gh.call_args.kwargs["timeout"] == 60


@pytest.mark.parametrize(
    "error", ["HTTP 401: unauthorized", "HTTP 403: forbidden", "HTTP 404: not found", "unknown flag"]
)
def test_terminal_error_is_not_retried(error):
    with (
        patch.object(fetch.subprocess, "run", return_value=result(1, stderr=error)) as gh,
        patch.object(fetch.time, "sleep") as sleep,
    ):
        with pytest.raises(RuntimeError, match="GitHub PR query failed"):
            fetch.fetch_pr_status()
    assert gh.call_count == 1
    sleep.assert_not_called()


def test_retry_exhaustion_emits_no_successful_json(capsys):
    with (
        patch.object(fetch.subprocess, "run", return_value=result(1, "partial", "HTTP 502: Bad Gateway")) as gh,
        patch.object(fetch.time, "sleep") as sleep,
    ):
        assert fetch.main() == 1
    assert gh.call_count == 3
    assert [call.args for call in sleep.call_args_list] == [(2,), (4,)]
    assert capsys.readouterr().out == ""


def test_timeout_exhaustion_is_bounded():
    with (
        patch.object(fetch.subprocess, "run", side_effect=subprocess.TimeoutExpired(fetch.COMMAND, 60)) as gh,
        patch.object(fetch.time, "sleep"),
    ):
        with pytest.raises(RuntimeError, match="timed out"):
            fetch.fetch_pr_status()
    assert gh.call_count == 3


@pytest.mark.parametrize("payload", ["partial", "null", "{}", "[1]"])
def test_malformed_success_is_rejected_without_retry(payload):
    with patch.object(fetch.subprocess, "run", return_value=result(stdout=payload)) as gh:
        with pytest.raises(ValueError):
            fetch.fetch_pr_status()
    assert gh.call_count == 1


def test_real_empty_list_is_success(capsys):
    with patch.object(fetch.subprocess, "run", return_value=result()):
        assert fetch.main() == 0
    assert capsys.readouterr().out == "[]\n"


def test_workflow_counts_failed_checks_and_accepts_null_rollups():
    import json
    import re

    import yaml

    workflow = yaml.safe_load(
        (Path(__file__).resolve().parents[2] / ".github/workflows/pr-status-monitor.yml").read_text()
    )
    step = next(step for step in workflow["jobs"]["monitor-prs"]["steps"] if step.get("id") == "check-prs")
    assert "PR_DATA=$(python3 scripts/ci/fetch_pr_status.py)" in step["run"]
    expression = re.search(r"FAILING_CI=.*jq '([^']+)'", step["run"]).group(1)
    data = [
        {"statusCheckRollup": [{"conclusion": "SUCCESS"}, {"conclusion": "FAILURE"}]},
        {"statusCheckRollup": [{"conclusion": "SUCCESS"}]},
        {"statusCheckRollup": None},
        {},
    ]
    counted = subprocess.run(
        ["jq", expression], input=json.dumps(data), text=True, capture_output=True, check=True, timeout=5
    )
    assert counted.stdout.strip() == "1"
