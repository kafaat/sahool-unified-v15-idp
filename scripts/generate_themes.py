#!/usr/bin/env python3
"""Generate SAHOOL Low-Code design artifacts from governance design tokens."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from generate_flutter_theme_from_tokens import ALLOWED_LOWCODE_SPACING_PX, generate_theme


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TOKENS = REPO_ROOT / "governance" / "design" / "design-tokens.yaml"
DEFAULT_JSON_OUTPUT = REPO_ROOT / "shared" / "design-system" / "tokens.json"
DEFAULT_FLUTTER_OUTPUT = REPO_ROOT / "apps" / "mobile" / "lib" / "core" / "theme" / "generated" / "sahool_token_theme.dart"
COMPAT_FLUTTER_OUTPUT = REPO_ROOT / "apps" / "mobile" / "lib" / "core" / "theme" / "generated_theme.dart"


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _rem_to_px(value: Any) -> float:
    if isinstance(value, str) and value.endswith("rem"):
        return float(value.removesuffix("rem")) * 16
    if isinstance(value, str) and value.endswith("px"):
        return float(value.removesuffix("px"))
    return float(value)


def _lowcode_tokens(tokens: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(tokens)
    normalized["$schema"] = "https://sahool.app/schemas/design-tokens.lowcode.json"
    normalized["source"] = "governance/design/design-tokens.yaml"
    normalized["generatedBy"] = "scripts/generate_themes.py"
    normalized["constraints"] = {
        "colors": "Only values from governance/design/design-tokens.yaml are allowed.",
        "fontFamilies": "Only typography.fonts entries are allowed.",
        "spacingPx": sorted(int(value) for value in ALLOWED_LOWCODE_SPACING_PX),
    }

    spacing = normalized.get("spacing", {})
    if isinstance(spacing, dict):
        normalized["spacing"] = {
            str(name): value
            for name, value in spacing.items()
            if _rem_to_px(value) in ALLOWED_LOWCODE_SPACING_PX
        }
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokens", type=Path, default=DEFAULT_TOKENS)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--flutter-output", type=Path, default=DEFAULT_FLUTTER_OUTPUT)
    parser.add_argument("--compat-flutter-output", type=Path, default=COMPAT_FLUTTER_OUTPUT)
    args = parser.parse_args()

    tokens = _load_yaml(args.tokens)
    normalized_tokens = _lowcode_tokens(tokens)

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(normalized_tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    theme = generate_theme(normalized_tokens)
    args.flutter_output.parent.mkdir(parents=True, exist_ok=True)
    args.flutter_output.write_text(theme, encoding="utf-8")

    args.compat_flutter_output.parent.mkdir(parents=True, exist_ok=True)
    args.compat_flutter_output.write_text(theme, encoding="utf-8")

    print(f"Generated {args.json_output.relative_to(REPO_ROOT)}")
    print(f"Generated {args.flutter_output.relative_to(REPO_ROOT)}")
    print(f"Generated {args.compat_flutter_output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
