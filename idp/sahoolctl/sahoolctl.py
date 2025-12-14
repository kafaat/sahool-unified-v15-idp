#!/usr/bin/env python3
"""sahoolctl - internal developer CLI for SAHOOL

Features:
- scaffold a new service from a golden path template
- generate GitOps application stub
- generate Helm values snippet for the service
"""

import argparse, os, shutil, re
from pathlib import Path

TEMPLATES = {
    "python-fastapi": "idp/templates/python-fastapi/skeleton",
    "node-service": "idp/templates/node-service/skeleton",
}


def kebab(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def render(text: str, values: dict) -> str:
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text


def copy_template(src: Path, dst: Path, values: dict):
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        (dst / rel).mkdir(parents=True, exist_ok=True)
        for f in files:
            sp = Path(root) / f
            dp = dst / rel / f
            content = sp.read_text(encoding="utf-8")
            dp.write_text(render(content, values), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="service name (kebab-case recommended)")
    ap.add_argument("--template", choices=TEMPLATES.keys(), default="python-fastapi")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument(
        "--layer", default="decision", choices=["signal-producer", "decision", "action"]
    )
    ap.add_argument("--out", default="apps")
    args = ap.parse_args()

    name = kebab(args.name)
    out = Path(args.out) / name
    if out.exists():
        raise SystemExit(f"Destination exists: {out}")

    src = Path(TEMPLATES[args.template])
    values = {"name": name, "port": args.port, "layer": args.layer}
    copy_template(src, out, values)

    # write a Helm values snippet
    (out / "deploy").mkdir(exist_ok=True)
    (out / "deploy" / "values.snippet.yaml").write_text(
        render(
            """services:
  {{name}}:
    enabled: true
    image:
      repository: REPLACE_WITH_IMAGE_REPO/{{name}}
      tag: "0.1.0"
    service:
      port: {{port}}
    rollouts:
      enabled: true
      strategy: canary
    autoscaling:
      enabled: true
      minReplicas: 2
      maxReplicas: 10
""",
            values,
        ),
        encoding="utf-8",
    )

    print(f"✅ Created service: {out}")
    print("Next: add it to Git, wire CI build, and add GitOps application/values.")


if __name__ == "__main__":
    main()
