#!/usr/bin/env python3
"""
SAHOOL Design Token Generator
=============================

Generates platform-specific design tokens from governance/design/design-tokens.yaml

Outputs:
- packages/design-system/tokens/tokens.css (CSS Custom Properties)
- packages/design-system/tokens/tailwind.config.js (Tailwind config)
- packages/design-system/tokens/tokens.dart (Flutter)
- packages/design-system/tokens/tokens.ts (TypeScript)
"""

import json
from datetime import datetime
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).parent.parent.parent
TOKENS_YAML = ROOT_DIR / "governance" / "design" / "design-tokens.yaml"
OUTPUT_DIR = ROOT_DIR / "packages" / "design-system" / "tokens"


def load_tokens():
    with open(TOKENS_YAML) as f:
        return yaml.safe_load(f)


def generate_css(tokens: dict) -> str:
    """Generate CSS Custom Properties"""
    lines = [
        "/* ═══════════════════════════════════════════════════════════════════════════ */",
        "/* AUTO-GENERATED - DO NOT EDIT MANUALLY */",
        "/* Generated from: governance/design/design-tokens.yaml */",
        f"/* Generated at: {datetime.now().isoformat()} */",
        "/* ═══════════════════════════════════════════════════════════════════════════ */",
        "",
        ":root {",
    ]

    # Colors
    for color_name, shades in tokens.get("colors", {}).items():
        if isinstance(shades, dict):
            for shade, value in shades.items():
                lines.append(f"  --color-{color_name}-{shade}: {value};")
        else:
            lines.append(f"  --color-{color_name}: {shades};")

    lines.append("")

    # Typography
    typo = tokens.get("typography", {})
    for size_name, size_value in typo.get("sizes", {}).items():
        lines.append(f"  --font-size-{size_name}: {size_value};")

    lines.append("")

    # Spacing
    for space_name, space_value in tokens.get("spacing", {}).items():
        lines.append(f"  --spacing-{space_name}: {space_value};")

    lines.append("")

    # Border Radius
    for radius_name, radius_value in tokens.get("borderRadius", {}).items():
        lines.append(f"  --radius-{radius_name}: {radius_value};")

    lines.append("")

    # Shadows
    shadows = tokens.get("shadows", {})
    for shadow_name, shadow_value in shadows.items():
        if isinstance(shadow_value, str):
            lines.append(f"  --shadow-{shadow_name}: {shadow_value};")

    lines.append("}")
    lines.append("")

    # Dark theme
    lines.append("[data-theme='dark'] {")
    dark = tokens.get("themes", {}).get("dark", {})
    for category, values in dark.items():
        for name, token_ref in values.items():
            lines.append(
                f"  --{category}-{name}: var(--color-{token_ref.replace('.', '-')});"
            )
    lines.append("}")

    return "\n".join(lines)


def generate_tailwind(tokens: dict) -> str:
    """Generate Tailwind CSS configuration"""
    config = {
        "colors": {},
        "spacing": {},
        "borderRadius": {},
        "fontSize": {},
        "fontFamily": {},
        "boxShadow": {},
    }

    # Colors
    for color_name, shades in tokens.get("colors", {}).items():
        if isinstance(shades, dict):
            config["colors"][color_name] = {}
            for shade, value in shades.items():
                config["colors"][color_name][str(shade)] = value
        else:
            config["colors"][color_name] = shades

    # Spacing
    for space_name, space_value in tokens.get("spacing", {}).items():
        config["spacing"][str(space_name)] = space_value

    # Border Radius
    for radius_name, radius_value in tokens.get("borderRadius", {}).items():
        config["borderRadius"][radius_name] = radius_value

    # Font sizes
    for size_name, size_value in tokens.get("typography", {}).get("sizes", {}).items():
        config["fontSize"][size_name] = size_value

    # Shadows
    for shadow_name, shadow_value in tokens.get("shadows", {}).items():
        if isinstance(shadow_value, str):
            config["boxShadow"][shadow_name] = shadow_value

    return f"""// AUTO-GENERATED - DO NOT EDIT MANUALLY
// Generated from: governance/design/design-tokens.yaml
// Generated at: {datetime.now().isoformat()}

/** @type {{import('tailwindcss').Config}} */
module.exports = {{
  theme: {{
    extend: {json.dumps(config, indent=6)}
  }}
}}
"""


def generate_typescript(tokens: dict) -> str:
    """Generate TypeScript tokens"""
    lines = [
        "// AUTO-GENERATED - DO NOT EDIT MANUALLY",
        "// Generated from: governance/design/design-tokens.yaml",
        f"// Generated at: {datetime.now().isoformat()}",
        "",
        "export const tokens = {",
    ]

    # Colors
    lines.append("  colors: {")
    for color_name, shades in tokens.get("colors", {}).items():
        if isinstance(shades, dict):
            lines.append(f"    {color_name}: {{")
            for shade, value in shades.items():
                lines.append(f"      '{shade}': '{value}',")
            lines.append("    },")
    lines.append("  },")

    # Spacing
    lines.append("  spacing: {")
    for space_name, space_value in tokens.get("spacing", {}).items():
        lines.append(f"    '{space_name}': '{space_value}',")
    lines.append("  },")

    # Typography
    lines.append("  typography: {")
    typo = tokens.get("typography", {})
    lines.append("    fonts: {")
    for font_name, font_value in typo.get("fonts", {}).items():
        lines.append(f"      {font_name}: '{font_value}',")
    lines.append("    },")
    lines.append("    sizes: {")
    for size_name, size_value in typo.get("sizes", {}).items():
        lines.append(f"      {size_name}: '{size_value}',")
    lines.append("    },")
    lines.append("  },")

    lines.append("} as const;")
    lines.append("")
    lines.append("export type TokenColors = keyof typeof tokens.colors;")
    lines.append("export type TokenSpacing = keyof typeof tokens.spacing;")

    return "\n".join(lines)


def generate_dart(tokens: dict) -> str:
    """Generate Flutter/Dart tokens"""
    lines = [
        "// AUTO-GENERATED - DO NOT EDIT MANUALLY",
        "// Generated from: governance/design/design-tokens.yaml",
        f"// Generated at: {datetime.now().isoformat()}",
        "",
        "import 'package:flutter/material.dart';",
        "",
        "/// SAHOOL Design Tokens",
        "class SahoolTokens {",
        "  SahoolTokens._();",
        "",
        "  // ─────────────────────────────────────────────────────────────────────",
        "  // Colors",
        "  // ─────────────────────────────────────────────────────────────────────",
    ]

    # Colors
    for color_name, shades in tokens.get("colors", {}).items():
        if isinstance(shades, dict):
            for shade, value in shades.items():
                hex_value = value.replace("#", "0xFF")
                dart_name = f"{color_name}{shade}".replace("-", "")
                lines.append(f"  static const Color {dart_name} = Color({hex_value});")

    lines.append("")
    lines.append(
        "  // ─────────────────────────────────────────────────────────────────────"
    )
    lines.append("  // Spacing")
    lines.append(
        "  // ─────────────────────────────────────────────────────────────────────"
    )

    # Spacing
    for space_name, space_value in tokens.get("spacing", {}).items():
        if space_value != "0":
            # Convert rem to double
            if "rem" in space_value:
                value = float(space_value.replace("rem", "")) * 16
            else:
                value = 0
            lines.append(f"  static const double spacing{space_name} = {value};")

    lines.append("")
    lines.append(
        "  // ─────────────────────────────────────────────────────────────────────"
    )
    lines.append("  // Border Radius")
    lines.append(
        "  // ─────────────────────────────────────────────────────────────────────"
    )

    # Border Radius
    for radius_name, radius_value in tokens.get("borderRadius", {}).items():
        if radius_value != "0" and radius_value != "9999px":
            if "rem" in radius_value:
                value = float(radius_value.replace("rem", "")) * 16
            else:
                value = 0
            lines.append(
                f"  static const double radius{radius_name.capitalize()} = {value};"
            )

    lines.append("")
    lines.append(
        "  // ─────────────────────────────────────────────────────────────────────"
    )
    lines.append("  // Typography")
    lines.append(
        "  // ─────────────────────────────────────────────────────────────────────"
    )

    typo = tokens.get("typography", {})
    for size_name, size_value in typo.get("sizes", {}).items():
        if "rem" in size_value:
            value = float(size_value.replace("rem", "")) * 16
            lines.append(
                f"  static const double fontSize{size_name.capitalize()} = {value};"
            )

    lines.append("}")
    lines.append("")

    # Theme Data
    lines.append("/// SAHOOL Theme Data")
    lines.append("class SahoolTheme {")
    lines.append("  static ThemeData get light => ThemeData(")
    lines.append("    primaryColor: SahoolTokens.primary500,")
    lines.append("    colorScheme: ColorScheme.light(")
    lines.append("      primary: SahoolTokens.primary500,")
    lines.append("      secondary: SahoolTokens.secondary500,")
    lines.append("      surface: SahoolTokens.neutral0,")
    lines.append("      error: SahoolTokens.errorMain ?? SahoolTokens.primary500,")
    lines.append("    ),")
    lines.append("    fontFamily: 'IBMPlexSansArabic',")
    lines.append("  );")
    lines.append("")
    lines.append("  static ThemeData get dark => ThemeData(")
    lines.append("    primaryColor: SahoolTokens.primary400,")
    lines.append("    colorScheme: ColorScheme.dark(")
    lines.append("      primary: SahoolTokens.primary400,")
    lines.append("      secondary: SahoolTokens.secondary400,")
    lines.append("      surface: SahoolTokens.neutral900,")
    lines.append("    ),")
    lines.append("    fontFamily: 'IBMPlexSansArabic',")
    lines.append("  );")
    lines.append("}")

    return "\n".join(lines)


def main():
    print("🎨 Loading design tokens...")
    tokens = load_tokens()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("📝 Generating CSS...")
    css = generate_css(tokens)
    (OUTPUT_DIR / "tokens.css").write_text(css)

    print("📝 Generating Tailwind config...")
    tailwind = generate_tailwind(tokens)
    (OUTPUT_DIR / "tailwind.tokens.js").write_text(tailwind)

    print("📝 Generating TypeScript...")
    ts = generate_typescript(tokens)
    (OUTPUT_DIR / "tokens.ts").write_text(ts)

    print("📝 Generating Dart/Flutter...")
    dart = generate_dart(tokens)
    (OUTPUT_DIR / "tokens.dart").write_text(dart)

    print("✅ Design tokens generated!")
    print(f"   Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
