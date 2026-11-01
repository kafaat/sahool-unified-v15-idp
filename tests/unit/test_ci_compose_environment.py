"""CI infrastructure startup must interpolate without application credentials."""

import os
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_integration_environment_covers_required_compose_interpolation(tmp_path):
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    steps = workflow["jobs"]["integration"]["steps"]
    setup = next(step["run"] for step in steps if step["name"] == "Create .env file for Docker Compose")
    subprocess.run(
        ["bash", "-eu", "-c", setup],
        cwd=tmp_path,
        env={"PATH": os.environ["PATH"]},
        check=True,
        capture_output=True,
    )
    values = dict(line.split("=", 1) for line in (tmp_path / ".env").read_text().splitlines())
    required = set(re.findall(r"\$\{([A-Z][A-Z0-9_]*):\?", (ROOT / "docker-compose.yml").read_text()))
    assert required, "The production Compose contract must be inspected"
    assert not {name for name in required if not values.get(name)}

    # The provider placeholder is only for whole-file interpolation. Never
    # start a provider-using application with this deliberately invalid key.
    start = next(step["run"] for step in steps if step["name"] == "Start services")
    startup = next(line.strip() for line in start.splitlines() if "compose up" in line)
    assert startup == "docker compose up -d postgres nats redis"
    assert values["ANTHROPIC_API_KEY"] == "ci_interpolation_placeholder_not_a_provider_credential"
