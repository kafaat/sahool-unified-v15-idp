#!/usr/bin/env python3
"""Generate a Flutter ThemeData starter from SAHOOL design tokens."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TOKENS = REPO_ROOT / "governance" / "design" / "design-tokens.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "apps" / "mobile" / "lib" / "core" / "theme" / "generated" / "sahool_token_theme.dart"


def _load_tokens(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _hex_to_color(value: str) -> str:
    if not isinstance(value, str) or not value.startswith("#") or len(value) != 7:
        raise ValueError(f"Expected #RRGGBB color, got {value!r}")
    return f"Color(0xFF{value[1:].upper()})"


def _rem_to_px(value: str) -> float:
    if isinstance(value, str) and value.endswith("rem"):
        return float(value.removesuffix("rem")) * 16
    if isinstance(value, str) and value.endswith("px"):
        return float(value.removesuffix("px"))
    return float(value)


def _constant_name(*parts: object) -> str:
    raw = "_".join(str(part) for part in parts)
    cleaned = raw.replace("-", "_").replace(".", "_")
    return cleaned.lower()


def _emit_color_constants(tokens: dict) -> list[str]:
    lines: list[str] = []
    for group_name, group_value in tokens.get("colors", {}).items():
        if not isinstance(group_value, dict):
            continue
        for color_name, color_value in group_value.items():
            if not isinstance(color_value, str):
                continue
            lines.append(f"  static const {_constant_name(group_name, color_name)} = {_hex_to_color(color_value)};")
    return lines


def _emit_spacing_constants(tokens: dict) -> list[str]:
    lines: list[str] = []
    for name, value in tokens.get("spacing", {}).items():
        lines.append(f"  static const spacing_{name} = {_rem_to_px(value):.1f};")
    return lines


def _emit_radius_constants(tokens: dict) -> list[str]:
    lines: list[str] = []
    for name, value in tokens.get("borderRadius", {}).items():
        lines.append(f"  static const radius_{name} = {_rem_to_px(value):.1f};")
    return lines


def generate_theme(tokens: dict) -> str:
    fonts = tokens.get("typography", {}).get("fonts", {})
    primary_font = str(fonts.get("primary", "IBM Plex Sans Arabic")).replace(" ", "")
    secondary_font = str(fonts.get("secondary", "Inter"))

    return "\n".join(
        [
            "// AUTO-GENERATED - DO NOT EDIT MANUALLY",
            "// Generated from: governance/design/design-tokens.yaml",
            "// Purpose: SAHOOL Low-Code PoC token-fed Flutter ThemeData.",
            "",
            "import 'dart:ui' show FontFeature;",
            "",
            "import 'package:flutter/material.dart';",
            "",
            "/// Token constants used by generated Low-Code PoC screens.",
            "class SahoolGeneratedTokens {",
            "  const SahoolGeneratedTokens._();",
            "",
            *(_emit_color_constants(tokens)),
            "",
            *(_emit_spacing_constants(tokens)),
            "",
            *(_emit_radius_constants(tokens)),
            "}",
            "",
            "/// Flutter themes generated from SAHOOL governance design tokens.",
            "class SahoolGeneratedTheme {",
            "  const SahoolGeneratedTheme._();",
            "",
            "  static ThemeData light() {",
            "    final base = ThemeData.light(useMaterial3: true);",
            "    return base.copyWith(",
            "      colorScheme: ColorScheme.fromSeed(",
            "        seedColor: SahoolGeneratedTokens.primary_500,",
            "        primary: SahoolGeneratedTokens.primary_500,",
            "        secondary: SahoolGeneratedTokens.secondary_500,",
            "        error: SahoolGeneratedTokens.error_main,",
            "        surface: SahoolGeneratedTokens.neutral_0,",
            "      ),",
            f"      fontFamily: '{primary_font}',",
            "      textTheme: base.textTheme.apply(",
            f"        fontFamily: '{primary_font}',",
            f"        displayColor: SahoolGeneratedTokens.neutral_900,",
            f"        bodyColor: SahoolGeneratedTokens.neutral_900,",
            "      ),",
            "      cardTheme: CardThemeData(",
            "        color: SahoolGeneratedTokens.neutral_0,",
            "        elevation: 1,",
            "        margin: const EdgeInsets.all(SahoolGeneratedTokens.spacing_4),",
            "        shape: RoundedRectangleBorder(",
            "          borderRadius: BorderRadius.circular(SahoolGeneratedTokens.radius_lg),",
            "        ),",
            "      ),",
            "      inputDecorationTheme: InputDecorationTheme(",
            "        border: OutlineInputBorder(",
            "          borderRadius: BorderRadius.circular(SahoolGeneratedTokens.radius_md),",
            "        ),",
            "      ),",
            "    );",
            "  }",
            "",
            "  static ThemeData dark() {",
            "    final base = ThemeData.dark(useMaterial3: true);",
            "    return base.copyWith(",
            "      colorScheme: ColorScheme.fromSeed(",
            "        brightness: Brightness.dark,",
            "        seedColor: SahoolGeneratedTokens.primary_300,",
            "        primary: SahoolGeneratedTokens.primary_300,",
            "        secondary: SahoolGeneratedTokens.secondary_300,",
            "        error: SahoolGeneratedTokens.error_light,",
            "        surface: SahoolGeneratedTokens.neutral_900,",
            "      ),",
            f"      fontFamily: '{primary_font}',",
            "      textTheme: base.textTheme.apply(",
            f"        fontFamily: '{primary_font}',",
            f"        displayColor: SahoolGeneratedTokens.neutral_0,",
            f"        bodyColor: SahoolGeneratedTokens.neutral_0,",
            "      ),",
            "    );",
            "  }",
            "",
            "  static TextStyle get monoMetric => const TextStyle(",
            f"    fontFamily: '{secondary_font}',",
            "    fontFeatures: [FontFeature.tabularFigures()],",
            "  );",
            "}",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokens", type=Path, default=DEFAULT_TOKENS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    tokens = _load_tokens(args.tokens)
    content = generate_theme(tokens)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print(f"Generated {args.output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
