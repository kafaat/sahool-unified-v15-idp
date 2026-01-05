"""
JSON Report Generator
"""

import json
from datetime import datetime


def generate(results: dict) -> str:
    """Generate JSON report from audit results"""

    # Clean up results for JSON serialization
    output = {
        "metadata": {
            "project": results.get("project", {}),
            "timestamp": results.get("timestamp", datetime.utcnow().isoformat()),
            "generator": "SAHOOL Audit Engine",
            "version": "1.0.0",
        },
        "summary": {
            "health_score": results.get("health_score", 0),
            "thresholds": results.get("thresholds", {}),
            "readiness": {
                "production": results.get("health_score", 0)
                >= results.get("thresholds", {}).get("production_ready", 8.0),
                "staging": results.get("health_score", 0)
                >= results.get("thresholds", {}).get("staging_ready", 6.0),
                "development": results.get("health_score", 0)
                >= results.get("thresholds", {}).get("development_ready", 4.0),
            },
        },
        "statistics": results.get("stats", {}),
        "findings": results.get("findings", []),
    }

    return json.dumps(output, indent=2, default=str)
