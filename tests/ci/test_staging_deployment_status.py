"""Deployment reporting must reflect the full job graph, including skipped jobs."""

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("staging_status", ROOT / "scripts/ci/staging_deployment_status.py")
reporter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reporter)


def completed_jobs():
    workflow = yaml.safe_load((ROOT / ".github/workflows/cd-staging.yml").read_text())
    names = workflow["jobs"]["deployment-summary"]["needs"]
    jobs = {name: {"result": "success"} for name in names}
    jobs["pre-deploy-checks"]["outputs"] = {"kubeconfig_available": "true"}
    return jobs


def test_complete_success():
    assert reporter.deployment_status(completed_jobs()) == "success"


@pytest.mark.parametrize("result,expected", [("failure", "failed"), ("cancelled", "failed"), ("skipped", "incomplete")])
def test_deploy_or_validation_not_successful(result, expected):
    for name in ("deploy-starter", "test-professional", "smoke-tests", "post-deploy-validation"):
        jobs = completed_jobs()
        jobs[name]["result"] = result
        assert reporter.deployment_status(jobs) == expected


def test_missing_kubeconfig_is_skipped():
    jobs = completed_jobs()
    jobs["pre-deploy-checks"]["outputs"]["kubeconfig_available"] = "false"
    for name in jobs:
        if name != "pre-deploy-checks":
            jobs[name]["result"] = "skipped"
    assert reporter.deployment_status(jobs) == "skipped"


def test_missing_validation_is_incomplete():
    jobs = completed_jobs()
    del jobs["post-deploy-validation"]
    assert reporter.deployment_status(jobs) == "incomplete"


def test_report_records_real_outcomes(tmp_path, monkeypatch):
    jobs = completed_jobs()
    jobs["deploy-enterprise"]["result"] = "failure"
    output, summary = tmp_path / "output", tmp_path / "summary"
    for key, value in {
        "STAGING_JOB_RESULTS": json.dumps(jobs),
        "GITHUB_OUTPUT": str(output),
        "GITHUB_STEP_SUMMARY": str(summary),
        "GITHUB_SHA": "abc123",
    }.items():
        monkeypatch.setenv(key, value)
    reporter.main()
    assert output.read_text() == "deployment_status=failed\n"
    assert "| deploy-enterprise | failure |" in summary.read_text()
    assert "Services Deployed" not in summary.read_text()
