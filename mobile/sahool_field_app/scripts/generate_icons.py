#!/usr/bin/env python3
"""
SAHOOL App Icon Generator
توليد أيقونات التطبيق الاحتياطية

This script generates placeholder icons for the SAHOOL app.
Run this if you don't have custom icons yet.

Requirements:
    pip install Pillow

Usage:
    python scripts/generate_icons.py
"""

import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow library required. Install with: pip install Pillow")
    sys.exit(1)


# Colors
FOREST_GREEN = (46, 125, 50)  # #2E7D32
DARK_GREEN = (27, 94, 32)     # #1B5E20
WHITE = (255, 255, 255)


def create_app_icon(output_path: str, size: int = 1024):
    """Create main app icon with green background and white symbol."""
    img = Image.new('RGBA', (size, size), FOREST_GREEN)
    draw = ImageDraw.Draw(img)

    # Draw a simple leaf/plant symbol
    center = size // 2
    leaf_size = size // 3

    # Simple leaf shape (three circles forming a plant)
    draw.ellipse(
        [center - leaf_size//2, center - leaf_size,
         center + leaf_size//2, center],
        fill=WHITE
    )
    draw.ellipse(
        [center - leaf_size, center - leaf_size//2,
         center, center + leaf_size//2],
        fill=WHITE
    )
    draw.ellipse(
        [center, center - leaf_size//2,
         center + leaf_size, center + leaf_size//2],
        fill=WHITE
    )

    # Stem
    draw.rectangle(
        [center - leaf_size//8, center,
         center + leaf_size//8, center + leaf_size],
        fill=WHITE
    )

    img.save(output_path)
    print(f"Created: {output_path}")


def create_foreground_icon(output_path: str, size: int = 1024):
    """Create adaptive icon foreground (transparent background)."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Same plant symbol but on transparent background
    center = size // 2
    leaf_size = size // 4  # Smaller for adaptive icon safe zone

    # Plant symbol
    draw.ellipse(
        [center - leaf_size//2, center - leaf_size,
         center + leaf_size//2, center],
        fill=WHITE
    )
    draw.ellipse(
        [center - leaf_size, center - leaf_size//2,
         center, center + leaf_size//2],
        fill=WHITE
    )
    draw.ellipse(
        [center, center - leaf_size//2,
         center + leaf_size, center + leaf_size//2],
        fill=WHITE
    )
    draw.rectangle(
        [center - leaf_size//8, center,
         center + leaf_size//8, center + leaf_size//1.5],
        fill=WHITE
    )

    img.save(output_path)
    print(f"Created: {output_path}")


def create_splash_logo(output_path: str, size: int = 512):
    """Create splash screen logo (white on transparent)."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Simple plant/agriculture symbol
    center = size // 2
    leaf_size = size // 4

    # Three leaves
    for angle_offset in [-60, 0, 60]:
        x_offset = int(leaf_size * 0.8 * (angle_offset / 60))
        draw.ellipse(
            [center - leaf_size//3 + x_offset, center - leaf_size - abs(x_offset)//2,
             center + leaf_size//3 + x_offset, center - abs(x_offset)//2],
            fill=WHITE
        )

    # Stem
    draw.rectangle(
        [center - leaf_size//6, center - leaf_size//4,
         center + leaf_size//6, center + leaf_size],
        fill=WHITE
    )

    # Ground/base
    draw.ellipse(
        [center - leaf_size, center + leaf_size//2,
         center + leaf_size, center + leaf_size + leaf_size//4],
        fill=WHITE
    )

    img.save(output_path)
    print(f"Created: {output_path}")


def main():
    # Get script directory and navigate to assets/icon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_dir = os.path.join(script_dir, '..', 'assets', 'icon')

    # Create directory if needed
    os.makedirs(icon_dir, exist_ok=True)

    print("=" * 50)
    print("SAHOOL App Icon Generator")
    print("مولد أيقونات تطبيق سهول")
    print("=" * 50)
    print()

    # Generate icons
    create_app_icon(os.path.join(icon_dir, 'app_icon.png'), 1024)
    create_foreground_icon(os.path.join(icon_dir, 'app_icon_foreground.png'), 1024)
    create_splash_logo(os.path.join(icon_dir, 'splash_logo.png'), 512)

    print()
    print("=" * 50)
    print("Icons generated successfully!")
    print()
    print("Next steps:")
    print("  1. cd mobile/sahool_field_app")
    print("  2. flutter pub get")
    print("  3. dart run flutter_launcher_icons")
    print("  4. dart run flutter_native_splash:create")
    print("=" * 50)


if __name__ == '__main__':
    main()
