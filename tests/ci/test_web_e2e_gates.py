"""Exercise workflow failure propagation and the web-server port contract."""

import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[2]


def steps():
    workflow = yaml.safe_load((ROOT / ".github/workflows/e2e-tests.yml").read_text())
    return {step["name"]: step for step in workflow["jobs"]["e2e-tests"]["steps"]}


def execute_step(tmp_path, script, failures):
    for command in ("npm", "npx", "curl", "sleep"):
        stub = tmp_path / command
        stub.write_text(f"#!/bin/sh\nexit {failures.get(command, 0)}\n")
        stub.chmod(0o700)
    return subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", script],
        cwd=tmp_path,
        env={"PATH": f"{tmp_path}:{os.defpath}"},
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    ).returncode


def test_unavailable_web_server_fails_readiness(tmp_path):
    assert execute_step(tmp_path, steps()["Start application"]["run"], {"curl": 37}) == 37


def test_failed_browser_suite_fails_its_step(tmp_path):
    assert execute_step(tmp_path, steps()["Run E2E tests"]["run"], {"npx": 23}) == 23


def test_browser_and_readiness_use_the_application_start_port():
    package = json.loads((ROOT / "apps/web/package.json").read_text())
    port = int(re.search(r"-p\s+(\d+)", package["scripts"]["start"])[1])
    workflow_steps = steps()
    assert urlparse(workflow_steps["Run E2E tests"]["env"]["PLAYWRIGHT_BASE_URL"]).port == port
    readiness_ports = re.findall(r"http://localhost:(\d+)", workflow_steps["Start application"]["run"])
    assert readiness_ports and set(readiness_ports) == {str(port)}
