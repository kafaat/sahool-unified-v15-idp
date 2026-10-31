#!/usr/bin/env python3
"""Audit every tracked, non-archive requirements.txt and retain truthful receipts.

Findings are advisory; missing inputs, failed resolution, skipped dependencies,
invalid JSON, and inconsistent exit codes fail the completeness check. The EO
tool alone uses its existing Python 3.12 contract. All 20 data-pipeline input /
output combinations are rendered by real Nunjucks before they are audited.
The summary counts findings per input, not distinct CVEs across the repository.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import itertools
import json
import os
import re
import signal
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

DATA_PIPELINE = "idp/templates/data-pipeline/skeleton/requirements.txt"
EO_REQUIREMENTS = "tools/eo-validation/requirements.txt"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def tracked_requirements(repository: Path) -> list[str]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=repository, check=True, capture_output=True, text=True)
    return sorted(
        name
        for name in result.stdout.split("\0")
        if name and Path(name).name == "requirements.txt" and Path(name).parts[0] != "archive"
    )


def pipeline_values(repository: Path) -> list[dict[str, str]]:
    import yaml

    template = (repository / DATA_PIPELINE).read_text()
    referenced = set(re.findall(r"\bvalues\.([A-Za-z_]\w*)", template))
    if referenced - {"name", "input_source", "output_sink"} or re.search(r"\bvalues\s*\[", template):
        raise ValueError("The requirements template uses an unmodeled parameter; expand the audit combinations first")
    definition = yaml.safe_load((repository / "idp/templates/data-pipeline/template.yaml").read_text())
    properties = {}
    for group in definition["spec"]["parameters"]:
        properties.update(group.get("properties", {}))
    inputs = properties["input_source"]["enum"]
    outputs = properties["output_sink"]["enum"]
    if not inputs or not outputs or any(not isinstance(value, str) for value in inputs + outputs):
        raise ValueError("Data-pipeline input/output enums must be nonempty strings")
    if len(set(inputs)) != len(inputs) or len(set(outputs)) != len(outputs):
        raise ValueError("Data-pipeline input/output enums contain duplicate values")
    return [
        {"name": "security-audit-pipeline", "input_source": source, "output_sink": sink}
        for source, sink in itertools.product(inputs, outputs)
    ]


def prepare_plan(repository: Path, output: Path, renderer: Path, python311: str, python312: str) -> dict:
    sources = tracked_requirements(repository)
    if not sources:
        raise ValueError("No tracked requirements.txt inputs were found")
    entries = []
    for name in sources:
        source = repository / name
        if not source.is_file():
            raise ValueError(f"Tracked requirements input is missing: {name}")
        variants = pipeline_values(repository) if name == DATA_PIPELINE else [None]
        for values in variants:
            identity = name if values is None else f"{name}::{values['input_source']}->{values['output_sink']}"
            key = hashlib.sha256(identity.encode()).hexdigest()[:20]
            requirement = source
            if values is not None:
                requirement = output / "rendered" / key / "requirements.txt"
                requirement.parent.mkdir(parents=True, exist_ok=True)
                rendered = subprocess.run(
                    [
                        "node",
                        str(repository / "scripts/ci/render_security_requirements.cjs"),
                        str(renderer.resolve()),
                        str(source),
                        json.dumps(values),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                requirement.write_text(rendered.stdout, encoding="utf-8")
            entries.append(
                {
                    "id": key,
                    "source": name,
                    "source_sha256": sha256(source),
                    "variant": values,
                    "requirements": str(requirement),
                    "requirements_sha256": sha256(requirement),
                    "python": python312 if name == EO_REQUIREMENTS else python311,
                    "python_contract": "3.12" if name == EO_REQUIREMENTS else "3.11",
                }
            )
    return {"sources": sources, "source_count": len(sources), "audit_input_count": len(entries), "entries": entries}


def run_command(command: list[str], stdout: Path, stderr: Path, timeout: float, cwd: Path) -> dict:
    started = time.monotonic()
    result = {"command": command, "exit_code": None, "timed_out": False, "execution_error": None}
    try:
        with stdout.open("w") as out, stderr.open("w") as err:
            process = subprocess.Popen(command, cwd=cwd, stdout=out, stderr=err, start_new_session=True)
            try:
                result["exit_code"] = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                result["timed_out"] = True
                result["execution_error"] = f"Command exceeded {timeout} seconds"
    except OSError as error:
        result["execution_error"] = str(error)
    result["duration_seconds"] = round(time.monotonic() - started, 3)
    return result


def classify_audit(exit_code: int | None, report: Path, execution_error: str | None = None) -> dict:
    result = {"status": "execution_error", "dependencies": None, "findings": None, "error": execution_error}
    if execution_error:
        return result
    try:
        data = json.loads(report.read_text())
        if not isinstance(data, dict) or not isinstance(data.get("dependencies"), list):
            raise ValueError("pip-audit JSON must contain a dependencies array")
        dependencies = data["dependencies"]
        findings = 0
        for dependency in dependencies:
            if not isinstance(dependency, dict) or dependency.get("skip_reason"):
                raise ValueError("pip-audit skipped a dependency or emitted an invalid entry")
            if not isinstance(dependency.get("name"), str) or not isinstance(dependency.get("version"), str):
                raise ValueError("Dependency name/version is missing")
            if not isinstance(dependency.get("vulns"), list):
                raise ValueError("Dependency vulnerability list is missing")
            for vulnerability in dependency["vulns"]:
                if not isinstance(vulnerability, dict) or not isinstance(vulnerability.get("id"), str):
                    raise ValueError("Vulnerability identifier is missing")
            findings += len(dependency["vulns"])
        expected_exit = 1 if findings else 0
        if exit_code != expected_exit:
            raise ValueError(f"Exit code {exit_code} disagrees with {findings} findings (expected {expected_exit})")
        result.update(status="findings" if findings else "clean", dependencies=len(dependencies), findings=findings)
    except (OSError, ValueError, TypeError) as error:
        result["error"] = str(error)
    return result


def audit_entry(entry: dict, repository: Path, output: Path, timeout: float) -> dict:
    directory = output / "inputs" / entry["id"]
    directory.mkdir(parents=True, exist_ok=True)
    report = directory / "pip-audit.json"
    report.unlink(missing_ok=True)
    command = [
        entry["python"],
        "-m",
        "pip_audit",
        "-r",
        entry["requirements"],
        "--strict",
        "--progress-spinner",
        "off",
        "--format",
        "json",
        "--output",
        str(report),
    ]
    execution = run_command(command, directory / "stdout.log", directory / "stderr.log", timeout, repository)
    result = {
        **entry,
        **execution,
        **classify_audit(execution["exit_code"], report, execution["execution_error"]),
        "report": str(report) if report.is_file() else None,
        "report_sha256": sha256(report) if report.is_file() else None,
        "stderr": str(directory / "stderr.log"),
    }
    write_json(directory / "receipt.json", result)
    return result


def summarize(plan: dict, results: list[dict]) -> dict:
    expected = {entry["id"] for entry in plan["entries"]}
    actual = [entry["id"] for entry in results]
    coverage_complete = len(actual) == len(expected) and set(actual) == expected
    counts = Counter(entry["status"] for entry in results)
    complete = coverage_complete and not counts["execution_error"]
    return {
        "complete": complete,
        "coverage_complete": coverage_complete,
        "source_count": plan["source_count"],
        "planned_inputs": len(expected),
        "attempted_inputs": len(results),
        "rendered_template_variants": sum(entry["variant"] is not None for entry in plan["entries"]),
        "clean_inputs": counts["clean"],
        "inputs_with_findings": counts["findings"],
        "failed_inputs": counts["execution_error"],
        "findings_across_inputs": sum(entry["findings"] or 0 for entry in results),
        "policy": "Vulnerabilities are advisory; incomplete execution or coverage fails the check",
        "results": results,
    }


def write_summary(summary: dict, output: Path) -> None:
    write_json(output / "summary.json", summary)
    lines = [
        "## Python dependency audit",
        "",
        f"Audit complete: **{summary['complete']}**. Findings remain advisory.",
        f"Tracked manifests: {summary['source_count']}; planned/attempted inputs: "
        f"{summary['planned_inputs']}/{summary['attempted_inputs']}; "
        f"rendered data-pipeline combinations: {summary['rendered_template_variants']}.",
        f"Clean inputs: {summary['clean_inputs']}; inputs with findings: {summary['inputs_with_findings']}; "
        f"failed/incomplete inputs: {summary['failed_inputs']}.",
        "",
        "| Input | Variant | Outcome | Findings |",
        "| --- | --- | --- | ---: |",
    ]
    for result in summary["results"]:
        values = result["variant"]
        variant = f"{values['input_source']} → {values['output_sink']}" if values else "—"
        findings = "unknown" if result["findings"] is None else result["findings"]
        lines.append(f"| {result['source']} | {variant} | {result['status']} | {findings} |")
    text = "\n".join(lines) + "\n"
    (output / "summary.md").write_text(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as handle:
            handle.write(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--nunjucks-module", type=Path, required=True)
    parser.add_argument("--python311", required=True)
    parser.add_argument("--python312", required=True)
    parser.add_argument("--jobs", type=int, choices=range(1, 9), default=4)
    parser.add_argument("--timeout", type=int, default=300)
    arguments = parser.parse_args()
    output = arguments.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    try:
        if arguments.timeout <= 0:
            raise ValueError("Timeout must be positive")
        plan = prepare_plan(
            arguments.repository.resolve(), output, arguments.nunjucks_module, arguments.python311, arguments.python312
        )
        write_json(output / "plan.json", plan)
        with concurrent.futures.ThreadPoolExecutor(max_workers=arguments.jobs) as pool:
            results = list(
                pool.map(
                    lambda entry: audit_entry(entry, arguments.repository.resolve(), output, arguments.timeout),
                    plan["entries"],
                )
            )
        summary = summarize(plan, results)
        write_summary(summary, output)
        print(json.dumps({key: value for key, value in summary.items() if key != "results"}))
        return 0 if summary["complete"] else 2
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        write_json(output / "fatal-error.json", {"complete": False, "error": str(error)})
        print(f"::error::Python dependency audit did not complete: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
