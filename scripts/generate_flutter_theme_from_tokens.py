#!/usr/bin/env python3
"""Generate a Flutter ThemeData starter from SAHOOL design tokens."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TOKENS = REPO_ROOT / "governance" / "design" / "design-tokens.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "apps" / "mobile" / "lib" / "core" / "theme" / "generated" / "sahool_token_theme.dart"
ALLOWED_LOWCODE_SPACING_PX = {0.0, 4.0, 8.0, 12.0, 16.0, 24.0, 32.0, 48.0, 64.0}


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
    raw_parts = [str(part).replace("-", "_").replace(".", "_") for part in parts]
    words = [word for part in raw_parts for word in part.split("_") if word]
    if not words:
        raise ValueError("Cannot build Dart identifier from empty token name")
    return words[0].lower() + "".join(word[:1].upper() + word[1:] for word in words[1:])


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
        spacing_px = _rem_to_px(value)
        if spacing_px in ALLOWED_LOWCODE_SPACING_PX:
            lines.append(f"  static const {_constant_name('spacing', name)} = {spacing_px:.1f};")
    return lines


def _emit_radius_constants(tokens: dict) -> list[str]:
    lines: list[str] = []
    for name, value in tokens.get("borderRadius", {}).items():
        lines.append(f"  static const {_constant_name('radius', name)} = {_rem_to_px(value):.1f};")
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
            "        seedColor: SahoolGeneratedTokens.primary500,",
            "        primary: SahoolGeneratedTokens.primary500,",
            "        secondary: SahoolGeneratedTokens.secondary500,",
            "        error: SahoolGeneratedTokens.errorMain,",
            "        surface: SahoolGeneratedTokens.neutral0,",
            "      ),",
            f"      fontFamily: '{primary_font}',",
            "      textTheme: base.textTheme.apply(",
            f"        fontFamily: '{primary_font}',",
            f"        displayColor: SahoolGeneratedTokens.neutral900,",
            f"        bodyColor: SahoolGeneratedTokens.neutral900,",
            "      ),",
            "      cardTheme: CardThemeData(",
            "        color: SahoolGeneratedTokens.neutral0,",
            "        elevation: 1,",
            "        margin: const EdgeInsets.all(SahoolGeneratedTokens.spacing4),",
            "        shape: RoundedRectangleBorder(",
            "          borderRadius: BorderRadius.circular(SahoolGeneratedTokens.radiusLg),",
            "        ),",
            "      ),",
            "      inputDecorationTheme: InputDecorationTheme(",
            "        border: OutlineInputBorder(",
            "          borderRadius: BorderRadius.circular(SahoolGeneratedTokens.radiusMd),",
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
            "        seedColor: SahoolGeneratedTokens.primary300,",
            "        primary: SahoolGeneratedTokens.primary300,",
            "        secondary: SahoolGeneratedTokens.secondary300,",
            "        error: SahoolGeneratedTokens.errorLight,",
            "        surface: SahoolGeneratedTokens.neutral900,",
            "      ),",
            f"      fontFamily: '{primary_font}',",
            "      textTheme: base.textTheme.apply(",
            f"        fontFamily: '{primary_font}',",
            f"        displayColor: SahoolGeneratedTokens.neutral0,",
            f"        bodyColor: SahoolGeneratedTokens.neutral0,",
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
