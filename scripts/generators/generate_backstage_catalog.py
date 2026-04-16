#!/usr/bin/env python3
"""
SAHOOL Backstage Catalog Generator
==================================

Generates Backstage Component entities for every service in
governance/services.yaml, matching the existing hand-written style
of idp/catalog/*.yaml (see yolo26-vision-service.yaml for reference).

Outputs:
  - idp/backstage/catalog/services/<service>.yaml  (one Component per service)
  - idp/backstage/catalog/services-location.yaml   (Location aggregator)

Skips services that already have a hand-written entity in idp/catalog/,
to avoid duplicate-entity errors in Backstage.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent.parent
GOVERNANCE = ROOT / "governance" / "services.yaml"
EXISTING_CATALOG = ROOT / "idp" / "catalog"
OUT_DIR = ROOT / "idp" / "backstage" / "catalog" / "services"
OUT_LOCATION = ROOT / "idp" / "backstage" / "catalog" / "services-location.yaml"

GITHUB_SLUG = "kafaat/sahool-unified-v15-idp"
SYSTEM = "sahool-platform"

# Governance `type` -> Backstage tags.
TYPE_TAGS: dict[str, list[str]] = {
    "python": ["python", "fastapi"],
    "fastapi": ["python", "fastapi"],
    "nestjs": ["nodejs", "nestjs", "typescript"],
    "nodejs": ["nodejs", "typescript"],
}

# Governance `lifecycle` -> Backstage spec.lifecycle.
# Backstage only accepts: experimental, production, deprecated.
LIFECYCLE_MAP: dict[str, str] = {
    "production": "production",
    "deprecated": "deprecated",
    "experimental": "experimental",
}


def _load_existing_names() -> set[str]:
    """Return metadata.name set of hand-written catalog entities we must not duplicate."""
    seen: set[str] = set()
    if not EXISTING_CATALOG.exists():
        return seen
    for yaml_file in EXISTING_CATALOG.rglob("*.yaml"):
        try:
            for doc in yaml.safe_load_all(yaml_file.read_text()):
                if not isinstance(doc, dict):
                    continue
                if doc.get("kind") in {"Component", "API", "Resource"}:
                    name = doc.get("metadata", {}).get("name")
                    if name:
                        seen.add(name)
        except yaml.YAMLError:
            continue
    return seen


def _normalize_owner(svc: dict) -> str:
    """Pick a Backstage owner ref: prefer `team`, fallback to email local-part of `owner`."""
    team = svc.get("team")
    if isinstance(team, str) and team:
        team = team.strip()
        if "-team" in team:
            return f"group:{team}"
        return f"group:{team}-team"
    owner = svc.get("owner", "")
    if isinstance(owner, str) and "@" in owner:
        local = owner.split("@", 1)[0].strip()
        if local:
            return f"group:{local}"
    return "group:sahool-platform"


def _build_tags(svc_key: str, svc: dict) -> list[str]:
    tags: list[str] = []
    svc_type = svc.get("type", "")
    tags.extend(TYPE_TAGS.get(svc_type, [svc_type] if svc_type else []))
    category = svc.get("category")
    if category:
        tags.append(f"category-{category}")
    layer = svc.get("layer")
    if layer:
        tags.append(f"layer-{layer}")
    tier = svc.get("tier")
    if tier:
        tags.append(str(tier))
    if svc.get("status") == "deprecated" or svc.get("lifecycle") == "deprecated":
        tags.append("deprecated")
    # Dedup while preserving order.
    seen: set[str] = set()
    return [t for t in tags if not (t in seen or seen.add(t))]


def _build_depends_on(svc: dict, known_services: set[str]) -> list[str]:
    deps = svc.get("dependencies")
    if not isinstance(deps, list):
        return []
    out: list[str] = []
    for dep in deps:
        if not isinstance(dep, str):
            continue
        dep = dep.strip()
        if not dep:
            continue
        # Resource-shaped dependencies (postgres, redis, nats, kong) become resource refs.
        if dep.lower() in {"postgres", "postgresql", "pgbouncer", "redis", "nats", "kong", "minio", "vault", "mqtt"}:
            out.append(f"resource:{dep.lower()}")
        elif dep in known_services:
            out.append(f"component:{dep}")
        else:
            # Unknown — register as an external component so Backstage doesn't break.
            out.append(f"component:{dep}")
    # Dedup preserving order.
    seen: set[str] = set()
    return [d for d in out if not (d in seen or seen.add(d))]


def _build_component(svc_key: str, svc: dict, known_services: set[str]) -> dict:
    title = svc.get("name") or svc_key
    name_ar = svc.get("name_ar")
    description = svc.get("description") or (
        f"{title} — {name_ar}" if name_ar else title
    )

    lifecycle = LIFECYCLE_MAP.get(
        svc.get("lifecycle") or svc.get("status") or "production",
        "production",
    )

    path = svc.get("path", f"apps/services/{svc_key}")
    annotations = {
        "github.com/project-slug": GITHUB_SLUG,
        "backstage.io/techdocs-ref": f"dir:./{path}",
        "backstage.io/source-location": f"url:https://github.com/{GITHUB_SLUG}/tree/main/{path}",
    }

    # Layer is a first-class concept in SAHOOL; expose as a dedicated annotation.
    if svc.get("layer"):
        annotations["sahool.io/event-layer"] = svc["layer"]
    if svc.get("port"):
        annotations["sahool.io/port"] = str(svc["port"])
    if svc.get("health_endpoint"):
        annotations["sahool.io/health-endpoint"] = svc["health_endpoint"]

    replaced_by = svc.get("replaced_by")
    if replaced_by:
        annotations["sahool.io/replaced-by"] = replaced_by
    sunset = svc.get("sunset_date") or svc.get("archive_date")
    if sunset:
        annotations["sahool.io/sunset-date"] = str(sunset)

    tags = _build_tags(svc_key, svc)
    depends_on = _build_depends_on(svc, known_services)

    component: dict = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Component",
        "metadata": {
            "name": svc_key,
            "title": title,
            "description": description,
            "annotations": annotations,
            "tags": tags,
        },
        "spec": {
            "type": "service",
            "lifecycle": lifecycle,
            "owner": _normalize_owner(svc),
            "system": SYSTEM,
        },
    }

    if depends_on:
        component["spec"]["dependsOn"] = depends_on

    return component


def _yaml_dump(doc: dict) -> str:
    return yaml.safe_dump(
        doc,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=120,
    )


def main() -> int:
    data = yaml.safe_load(GOVERNANCE.read_text())
    services: dict = data.get("services", {})
    if not services:
        print("no services found in governance/services.yaml", file=sys.stderr)
        return 1

    skip = _load_existing_names()
    known = set(services.keys())

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Clean stale generated files: remove any .yaml in OUT_DIR not matching a current service.
    kept_files: list[str] = []
    for existing_file in OUT_DIR.glob("*.yaml"):
        stem = existing_file.stem
        if stem not in services or stem in skip:
            existing_file.unlink()

    generated = 0
    skipped = 0
    for svc_key, svc in services.items():
        if not isinstance(svc, dict):
            continue
        if svc_key in skip:
            skipped += 1
            continue

        component = _build_component(svc_key, svc, known)
        header = (
            "# AUTO-GENERATED - DO NOT EDIT MANUALLY\n"
            "# Generated from: governance/services.yaml\n"
            "# Generator: scripts/generators/generate_backstage_catalog.py\n"
            f"# Service key: {svc_key}\n"
        )
        target = OUT_DIR / f"{svc_key}.yaml"
        target.write_text(header + _yaml_dump(component))
        kept_files.append(f"./services/{svc_key}.yaml")
        generated += 1

    # Location aggregator: one entity that registers all generated files.
    # No `spec.type` — matches the style of idp/backstage/catalog/all.yaml
    # so Backstage resolves the targets via the parent Location's scheme.
    location = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Location",
        "metadata": {
            "name": "sahool-services-catalog",
            "description": (
                "Auto-generated Backstage entities for every service in "
                "governance/services.yaml. Regenerate with "
                "scripts/generators/generate_backstage_catalog.py."
            ),
        },
        "spec": {
            "targets": sorted(kept_files),
        },
    }
    OUT_LOCATION.write_text(
        "# AUTO-GENERATED - DO NOT EDIT MANUALLY\n"
        "# Generated from: governance/services.yaml\n"
        + _yaml_dump(location)
    )

    print(f"Generated {generated} Component entities in {OUT_DIR.relative_to(ROOT)}")
    print(f"Skipped  {skipped} services already registered in idp/catalog/")
    print(f"Location aggregator: {OUT_LOCATION.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
