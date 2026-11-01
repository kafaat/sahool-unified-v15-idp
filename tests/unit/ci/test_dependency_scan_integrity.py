"""Exercise scanner processes, retained reports and fail-closed event policies."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
HELPERS = ROOT / "scripts/ci"


def load_helper(name):
    spec = importlib.util.spec_from_file_location(name, HELPERS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


audit = load_helper("audit_python_requirements")
trivy = load_helper("trivy_scan_receipt")
safety = load_helper("run_optional_safety")


def sarif(count=0):
    return {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "Trivy", "version": "0.69.3"}},
                "results": [
                    {"ruleId": f"CVE-fixture-{index}", "level": "error", "message": {"text": "fixture finding"}}
                    for index in range(count)
                ],
            }
        ],
    }


@pytest.mark.parametrize(
    ("code", "content", "status"),
    [
        (0, {"dependencies": [{"name": "fixture", "version": "1", "vulns": []}]}, "clean"),
        (1, {"dependencies": [{"name": "fixture", "version": "1", "vulns": [{"id": "CVE-fixture"}]}]}, "findings"),
        (2, {"dependencies": []}, "execution_error"),
        (1, {"dependencies": []}, "execution_error"),
        (
            0,
            {"dependencies": [{"name": "fixture", "version": "1", "vulns": [{"id": "CVE-fixture"}]}]},
            "execution_error",
        ),
        (1, {"dependencies": [{"name": "fixture", "skip_reason": "not on PyPI"}]}, "execution_error"),
        (0, {"dependencies": [{"name": "fixture", "version": "1"}]}, "execution_error"),
        (0, {}, "execution_error"),
        (0, [], "execution_error"),
        (0, "truncated", "execution_error"),
    ],
)
def test_pip_audit_classifies_real_exit_and_report_together(tmp_path, code, content, status):
    report = tmp_path / "audit.json"
    report.write_text(content if isinstance(content, str) else json.dumps(content))
    assert audit.classify_audit(code, report)["status"] == status


def test_missing_audit_report_is_incomplete(tmp_path):
    assert audit.classify_audit(0, tmp_path / "absent.json")["status"] == "execution_error"


def test_timed_out_process_is_recorded_without_a_clean_verdict(tmp_path):
    result = audit.run_command(
        [sys.executable, "-c", "import time; time.sleep(10)"],
        tmp_path / "stdout",
        tmp_path / "stderr",
        0.05,
        tmp_path,
    )
    assert result["timed_out"]
    assert result["exit_code"] is None
    assert result["execution_error"]


def test_missing_executable_is_recorded(tmp_path):
    result = audit.run_command([str(tmp_path / "absent")], tmp_path / "stdout", tmp_path / "stderr", 1, tmp_path)
    assert result["execution_error"]
    assert result["exit_code"] is None


@pytest.mark.parametrize("outcome", ["clean", "findings", "resolution-failure", "malformed"])
def test_actual_audit_cli_covers_more_than_ten_inputs_and_propagates_incomplete_results(tmp_path, outcome):
    repository = tmp_path / "repository"
    repository.mkdir()
    for index in range(12):
        path = repository / f"service {index}" / "requirements.txt"
        path.parent.mkdir()
        path.write_text(outcome if index == 11 else "clean")
    ignored = repository / "archive/old/requirements.txt"
    ignored.parent.mkdir(parents=True)
    ignored.write_text("resolution-failure")
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(["git", "add", "."], cwd=repository, check=True)
    fake_tools = tmp_path / "fake-tools"
    fake_tools.mkdir()
    (fake_tools / "pip_audit.py").write_text(
        "import json,sys\nfrom pathlib import Path\n"
        "args=sys.argv[1:]; content=Path(args[args.index('-r')+1]).read_text()\n"
        "report=Path(args[args.index('--output')+1])\n"
        "if content=='resolution-failure': sys.exit(2)\n"
        "if content=='malformed': report.write_text('{'); sys.exit(0)\n"
        "vulns=[{'id':'CVE-fixture'}] if content=='findings' else []\n"
        "report.write_text(json.dumps({'dependencies':[{'name':'fixture','version':'1','vulns':vulns}]}))\n"
        "sys.exit(1 if vulns else 0)\n"
    )
    output = tmp_path / "receipts"
    process = subprocess.run(
        [
            sys.executable,
            str(HELPERS / "audit_python_requirements.py"),
            "--repository",
            str(repository),
            "--output",
            str(output),
            "--nunjucks-module",
            str(tmp_path / "unused"),
            "--python311",
            sys.executable,
            "--python312",
            sys.executable,
            "--jobs",
            "3",
        ],
        env=dict(os.environ, PYTHONPATH=str(fake_tools)),
        capture_output=True,
        text=True,
        timeout=30,
    )
    summary = json.loads((output / "summary.json").read_text())
    assert summary["source_count"] == summary["planned_inputs"] == summary["attempted_inputs"] == 12
    assert summary["coverage_complete"]
    assert len(list((output / "inputs").glob("*/receipt.json"))) == 12
    incomplete = outcome in {"resolution-failure", "malformed"}
    assert process.returncode == (2 if incomplete else 0), process.stderr
    assert summary["complete"] is not incomplete
    assert summary["failed_inputs"] == int(incomplete)
    assert summary["inputs_with_findings"] == int(outcome == "findings")


def test_pipeline_plan_includes_all_twenty_declared_combinations():
    values = audit.pipeline_values(ROOT)
    assert len(values) == 20
    assert {(item["input_source"], item["output_sink"]) for item in values} == {
        (source, sink)
        for source in ["nats", "kafka", "postgres", "s3", "api"]
        for sink in ["nats", "postgres", "s3", "api"]
    }


@pytest.mark.parametrize("expression", ["values.pipeline_type", "values['pipeline_type']"])
def test_new_template_parameter_cannot_silently_escape_combination_coverage(tmp_path, expression):
    template = tmp_path / audit.DATA_PIPELINE
    template.parent.mkdir(parents=True)
    template.write_text(f'{{% if {expression} == "batch" %}}\nfixture==1\n{{% endif %}}')
    with pytest.raises(ValueError, match="unmodeled parameter"):
        audit.pipeline_values(tmp_path)


def test_missing_and_duplicate_receipts_cannot_complete_the_inventory():
    plan = {"source_count": 2, "entries": [{"id": "first", "variant": None}, {"id": "second", "variant": None}]}
    receipt = {"id": "first", "status": "clean", "findings": 0}
    assert not audit.summarize(plan, [receipt])["complete"]
    assert not audit.summarize(plan, [receipt, receipt])["complete"]


@pytest.mark.parametrize("event", ["pull_request", "push", "schedule", "workflow_dispatch"])
@pytest.mark.parametrize("count", [0, 2])
def test_trivy_gate_preserves_findings_policy_and_validates_all_runs(tmp_path, event, count):
    report = tmp_path / "trivy.sarif"
    data = sarif(count)
    data["runs"].append(sarif(count)["runs"][0])
    report.write_text(json.dumps(data))
    validated = trivy.validate_scan(1 if count else 0, report, "")
    assert validated["critical_count"] == count * 2
    receipt = tmp_path / "receipt.json"
    audit.write_json(
        receipt,
        {
            **validated,
            "report": str(report),
            "report_sha256": trivy.file_digest(report),
            "exit_code": 1 if count else 0,
        },
    )
    assert trivy.gate(receipt, event) == (1 if count and event != "pull_request" else 0)


@pytest.mark.parametrize("data", [{}, [], {"version": "2.1.0", "runs": []}, {"version": "2.1.0", "runs": [{}]}])
def test_trivy_rejects_incomplete_sarif_shapes(tmp_path, data):
    report = tmp_path / "trivy.sarif"
    report.write_text(json.dumps(data))
    assert trivy.validate_scan(0, report, "")["status"] == "incomplete"


@pytest.mark.parametrize("code,count,log", [(1, 0, ""), (0, 1, ""), (2, 0, ""), (1, 1, "2026-10-31 FATAL scan failed")])
def test_trivy_execution_failure_cannot_be_interpreted_as_clean(tmp_path, code, count, log):
    report = tmp_path / "trivy.sarif"
    report.write_text(json.dumps(sarif(count)))
    assert trivy.validate_scan(code, report, log)["status"] == "incomplete"


def test_trivy_rejects_unknown_severity_in_critical_only_report(tmp_path):
    report = tmp_path / "trivy.sarif"
    data = sarif(1)
    data["runs"][0]["results"][0]["level"] = "warning"
    report.write_text(json.dumps(data))
    assert trivy.validate_scan(1, report, "")["status"] == "incomplete"


def test_trivy_missing_binary_retains_failure_without_synthetic_report(tmp_path):
    output = tmp_path / "results"
    output.mkdir()
    (output / "trivy-results.sarif").write_text(json.dumps(sarif()))
    assert trivy.scan(tmp_path, output, str(tmp_path / "missing-trivy"), tmp_path / "cache") == 2
    assert not (output / "trivy-results.sarif").exists()
    receipt = json.loads((output / "receipt.json").read_text())
    assert receipt["status"] == "incomplete"
    assert receipt["exit_code"] is None
    assert receipt["report"] is None


@pytest.mark.parametrize("relative_cache", [False, True])
def test_trivy_scan_uses_the_database_directory_recorded_in_its_receipt(tmp_path, monkeypatch, relative_cache):
    cache = tmp_path / "custom-cache"
    repository = tmp_path / "repository"
    repository.mkdir()
    monkeypatch.chdir(tmp_path)
    (cache / "db").mkdir(parents=True)
    (cache / "db/trivy.db").write_bytes(b"fixture-database")
    audit.write_json(cache / "db/metadata.json", {"UpdatedAt": "fixture-time"})

    def execute(command, stdout, stderr, timeout, cwd):
        assert command[command.index("--cache-dir") + 1] == str(cache)
        Path(command[command.index("--output") + 1]).write_text(json.dumps(sarif()))
        stdout.write_text("")
        stderr.write_text("")
        return {"command": command, "exit_code": 0, "execution_error": None}

    monkeypatch.setattr(trivy, "run_command", execute)
    output = tmp_path / "results"
    assert trivy.scan(repository, output, "trivy", Path("custom-cache") if relative_cache else cache) == 0
    receipt = json.loads((output / "receipt.json").read_text())
    assert receipt["database"]["database_sha256"] == trivy.file_digest(cache / "db/trivy.db")
    assert receipt["database"]["metadata"]["UpdatedAt"] == "fixture-time"


@pytest.mark.parametrize("event", ["pull_request", "push", "schedule", "workflow_dispatch"])
def test_trivy_missing_receipt_fails_every_event(tmp_path, event):
    assert trivy.gate(tmp_path / "absent.json", event) == 2


def test_trivy_modified_report_is_rejected(tmp_path):
    report = tmp_path / "trivy.sarif"
    report.write_text(json.dumps(sarif()))
    receipt = tmp_path / "receipt.json"
    audit.write_json(
        receipt,
        {
            **trivy.validate_scan(0, report, ""),
            "report": str(report),
            "report_sha256": trivy.file_digest(report),
            "exit_code": 0,
        },
    )
    report.write_text(json.dumps(sarif(1)))
    assert trivy.gate(receipt, "pull_request") == 2


def test_unconfigured_safety_is_explicitly_skipped_without_invocation(tmp_path, monkeypatch):
    monkeypatch.delenv("SAFETY_API_KEY", raising=False)
    assert safety.run(tmp_path, tmp_path / "results", binary=str(tmp_path / "missing")) == 0
    receipt = json.loads((tmp_path / "results/receipt.json").read_text())
    assert receipt["status"] == "not_configured"
    assert "exit_code" not in receipt


@pytest.mark.parametrize("code", [0, 64, 65, 68, 71])
def test_configured_safety_uses_directory_and_distinguishes_nonfindings_failures(tmp_path, monkeypatch, code):
    monkeypatch.setenv("SAFETY_API_KEY", "fixture-only")
    binary = tmp_path / "safety-fixture"
    binary.write_text(
        f"#!{sys.executable}\nimport json,sys\nfrom pathlib import Path\n"
        "assert sys.argv[1]=='scan'\nassert Path(sys.argv[sys.argv.index('--target')+1]).is_dir()\n"
        "assert '--key' not in sys.argv\n"
        "print(json.dumps({'meta': {}, 'scan_results': {'files': [], 'projects': []}}))\n"
        f"sys.exit({code})\n"
    )
    binary.chmod(0o755)
    assert safety.run(tmp_path, tmp_path / "results", str(binary)) == (0 if code in (0, 64) else 2)
    receipt = json.loads((tmp_path / "results/receipt.json").read_text())
    assert receipt["exit_code"] == code
    assert "fixture-only" not in json.dumps(receipt)


@pytest.mark.parametrize("report", [{"error": "authentication failed"}, {}, {"meta": {}, "scan_results": {}}])
def test_safety_error_or_partial_json_cannot_be_a_successful_report(tmp_path, monkeypatch, report):
    monkeypatch.setenv("SAFETY_API_KEY", "fixture-only")

    def execute(command, stdout, stderr, timeout, cwd):
        stdout.write_text(json.dumps(report))
        stderr.write_text("")
        return {"command": command, "exit_code": 0, "execution_error": None}

    monkeypatch.setattr(safety, "run_command", execute)
    assert safety.run(tmp_path, tmp_path / "results") == 2
    assert json.loads((tmp_path / "results/receipt.json").read_text())["status"] == "execution_error"


@pytest.mark.parametrize("workflow", ["security.yml", "security-checks.yml"])
@pytest.mark.parametrize("outcome", ["success", "failure", "skipped", "cancelled"])
def test_workflow_completeness_gate_propagates_audit_step_failure(tmp_path, workflow, outcome):
    content = yaml.safe_load((ROOT / ".github/workflows" / workflow).read_text())
    job = content["jobs"]["dependency-scan-python" if workflow == "security.yml" else "dependency-scan"]
    steps = job["steps"]
    gate = next(step for step in steps if step.get("name") == "Require a complete Python dependency audit")
    upload = next(
        index for index, step in enumerate(steps) if step.get("uses", "").startswith("actions/upload-artifact@")
    )
    assert steps.index(gate) > upload
    assert gate["if"] == "always()"
    script = gate["run"].replace("${{ steps.python_audit.outcome }}", outcome)
    result = subprocess.run(["bash", "-euo", "pipefail", "-c", script], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == (0 if outcome == "success" else 1)
