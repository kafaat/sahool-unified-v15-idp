"""Report observed staging job outcomes without claiming skipped work succeeded."""

import json
import os
from pathlib import Path


def deployment_status(needs: dict) -> str:
    results = [job.get("result") for job in needs.values()]
    if any(result in {"failure", "cancelled"} for result in results):
        return "failed"
    preflight = needs.get("pre-deploy-checks", {})
    if preflight.get("result") != "success":
        return "incomplete"
    if preflight.get("outputs", {}).get("kubeconfig_available") == "false":
        return "skipped"
    if preflight.get("outputs", {}).get("kubeconfig_available") != "true":
        return "incomplete"
    required = {
        "pre-deploy-checks",
        "agent-evaluation-gate",
        "deploy-starter",
        "test-starter",
        "deploy-professional",
        "test-professional",
        "deploy-enterprise",
        "test-enterprise",
        "smoke-tests",
        "post-deploy-validation",
    }
    if required.issubset(needs) and all(needs[name].get("result") == "success" for name in required):
        return "success"
    return "incomplete"


def main() -> None:
    needs = json.loads(os.environ["STAGING_JOB_RESULTS"])
    status = deployment_status(needs)
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
        output.write(f"deployment_status={status}\n")
    with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as summary:
        summary.write(f"## Staging deployment: {status}\n\n")
        summary.write(f"Commit: `{os.environ['GITHUB_SHA']}`\n\n")
        if status == "skipped":
            summary.write("Deployment skipped: KUBE_CONFIG_STAGING is not configured.\n\n")
        elif status == "incomplete":
            summary.write(
                "The complete deployment and validation chain did not succeed; no full deployment claim is made.\n\n"
            )
        summary.write("| Job | Observed result |\n| --- | --- |\n")
        for name, job in sorted(needs.items()):
            summary.write(f"| {name} | {job.get('result', 'unknown')} |\n")


if __name__ == "__main__":
    main()
