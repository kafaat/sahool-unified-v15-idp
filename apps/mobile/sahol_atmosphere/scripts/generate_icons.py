#!/usr/bin/env python3
"""
SAHOOL Atmosphere Icon Generator
مولد أيقونات ساهول أتموسفير

Generates placeholder app icons with Atmosphere's dark bio-luminescent theme.
Uses PIL (Pillow) for image generation.

Usage:
    python scripts/generate_icons.py

Requirements:
    pip install Pillow
"""

import math
import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: PIL (Pillow) is required. Install with: pip install Pillow")
    exit(1)

# Theme colors (Atmosphere dark theme)
COLORS = {
    "bg_primary": "#0D1F12",  # Dark forest
    "bg_secondary": "#050A06",  # Near black
    "success": "#00E676",  # Bio-luminescent green
    "glow": "#00FF88",  # Atmosphere glow
    "white": "#FFFFFF",
}


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def draw_plant_icon(draw: ImageDraw, center: tuple, size: int, color: tuple, glow: tuple = None):
    """Draw a stylized plant/leaf icon."""
    cx, cy = center

    # Stem
    stem_width = size // 15
    stem_height = size // 2
    draw.rectangle([cx - stem_width // 2, cy, cx + stem_width // 2, cy + stem_height], fill=color)

    # Main leaf (center)
    leaf_size = size // 3
    points = [
        (cx, cy - leaf_size),  # Top
        (cx + leaf_size // 2, cy),  # Right
        (cx, cy + leaf_size // 4),  # Bottom
        (cx - leaf_size // 2, cy),  # Left
    ]
    draw.polygon(points, fill=color)

    # Side leaves
    for dx in [-1, 1]:
        side_leaf_size = size // 4
        offset_x = dx * side_leaf_size // 2
        offset_y = stem_height // 3
        side_points = [
            (cx + offset_x, cy + offset_y - side_leaf_size // 2),
            (cx + offset_x + dx * side_leaf_size // 2, cy + offset_y),
            (cx + offset_x, cy + offset_y + side_leaf_size // 4),
        ]
        draw.polygon(side_points, fill=color)


def draw_atmosphere_glow(draw: ImageDraw, center: tuple, size: int, color: tuple):
    """Draw circular glow effect."""
    cx, cy = center
    # Draw concentric circles with decreasing opacity
    for i in range(5, 0, -1):
        radius = size // 2 + i * 20
        alpha = int(30 * (6 - i) / 5)
        glow_color = color + (alpha,)
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=glow_color, width=10)


def generate_app_icon(output_path: str, size: int = 1024):
    """Generate the main app icon with dark background and glowing plant."""
    # Create image with RGBA mode for transparency support
    img = Image.new("RGBA", (size, size), hex_to_rgb(COLORS["bg_primary"]) + (255,))
    draw = ImageDraw.Draw(img)

    # Add gradient effect (simulated with circles)
    center = (size // 2, size // 2)

    # Draw glow effect
    glow_color = hex_to_rgb(COLORS["glow"])
    for i in range(20, 0, -1):
        radius = size // 3 + i * 10
        alpha = int(20 * i / 20)
        draw.ellipse(
            [center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
            fill=hex_to_rgb(COLORS["bg_primary"]) + (255,),
            outline=glow_color + (alpha,),
            width=3,
        )

    # Draw plant icon
    plant_size = size // 2
    plant_center = (size // 2, size // 2 - size // 10)
    draw_plant_icon(draw, plant_center, plant_size, hex_to_rgb(COLORS["success"]), hex_to_rgb(COLORS["glow"]))

    # Add "SAHOOL" text at bottom (optional, commented out for clean icon)
    # try:
    #     font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size // 12)
    #     text = "SAHOOL"
    #     text_bbox = draw.textbbox((0, 0), text, font=font)
    #     text_width = text_bbox[2] - text_bbox[0]
    #     draw.text(
    #         ((size - text_width) // 2, size - size // 6),
    #         text,
    #         fill=hex_to_rgb(COLORS['white']),
    #         font=font
    #     )
    # except:
    #     pass

    # Save as PNG
    img = img.convert("RGB")  # Convert to RGB for PNG without alpha in background
    img.save(output_path, "PNG")
    print(f"Generated: {output_path}")


def generate_foreground_icon(output_path: str, size: int = 1024):
    """Generate app icon foreground with transparent background."""
    # Create transparent image
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw plant icon centered (with safe zone padding for adaptive icons)
    safe_zone = size // 4  # 25% padding for adaptive icons
    plant_size = size // 2 - safe_zone // 2
    plant_center = (size // 2, size // 2 - size // 15)

    draw_plant_icon(draw, plant_center, plant_size, hex_to_rgb(COLORS["white"]))

    img.save(output_path, "PNG")
    print(f"Generated: {output_path}")


def generate_splash_logo(output_path: str, size: int = 512):
    """Generate splash screen logo with transparent background."""
    # Create transparent image
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw plant icon
    plant_size = size // 2
    plant_center = (size // 2, size // 2 - size // 10)

    draw_plant_icon(draw, plant_center, plant_size, hex_to_rgb(COLORS["success"]))

    img.save(output_path, "PNG")
    print(f"Generated: {output_path}")


def main():
    """Generate all required icons."""
    # Get script directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    icon_dir = project_dir / "assets" / "icon"

    # Ensure output directory exists
    icon_dir.mkdir(parents=True, exist_ok=True)

    print("🎨 SAHOOL Atmosphere Icon Generator")
    print("=" * 40)

    # Generate icons
    generate_app_icon(str(icon_dir / "app_icon.png"), 1024)
    generate_foreground_icon(str(icon_dir / "app_icon_foreground.png"), 1024)
    generate_splash_logo(str(icon_dir / "splash_logo.png"), 512)

    print("=" * 40)
    print("✅ Icon generation complete!")
    print()
    print("Next steps:")
    print("  1. dart run flutter_launcher_icons")
    print("  2. dart run flutter_native_splash:create")


if __name__ == "__main__":
    main()
