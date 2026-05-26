"""Procedural Icon Generator for Pushbox-Pygame.

Draws the multi-resolution Option C (Nord geometric bear pushing a crate) icon
using Pygame and compiles them into a standard Windows .ico file
using pure Python struct.
Requires no external dependencies beyond pygame.
"""

import struct
import tempfile
from pathlib import Path

import pygame

# Initialize pygame
pygame.init()

# Colors
NORD_BG = (40, 44, 52)
BEAR_PURPLE = (198, 120, 221)
BEAR_SHADOW = (158, 80, 181)
BOX_YELLOW = (229, 192, 123)
BOX_OUTLINE = (100, 80, 40)
CHEEKS_PINK = (255, 180, 200)
EYES_DARK = (40, 40, 40)


def draw_icon_surface(size: int) -> pygame.Surface:
    """Draw the icon at a specific resolution on a transparent Surface."""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # Fully transparent

    # 1. Draw rounded dark card background
    if size == 256:
        margin, radius = 12, 36
    elif size == 48:
        margin, radius = 2, 8
    elif size == 32:
        margin, radius = 1, 6
    else:  # 16
        margin, radius = 0, 3

    card_rect = pygame.Rect(margin, margin, size - 2 * margin, size - 2 * margin)
    pygame.draw.rect(surface, NORD_BG, card_rect, border_radius=radius)

    # 2. Draw composition based on resolution
    if size == 256:
        # Bear
        bear_x, bear_y = 90, 128
        bear_r = 50
        # Ears
        pygame.draw.circle(surface, BEAR_SHADOW, (bear_x - 35, bear_y - 35), 20)
        pygame.draw.circle(surface, BEAR_SHADOW, (bear_x + 35, bear_y - 35), 20)
        # Head
        pygame.draw.circle(surface, BEAR_PURPLE, (bear_x, bear_y), bear_r)
        # Cheeks
        pygame.draw.circle(surface, CHEEKS_PINK, (bear_x - 30, bear_y + 10), 10)
        pygame.draw.circle(surface, CHEEKS_PINK, (bear_x + 30, bear_y + 10), 10)
        # Eyes
        pygame.draw.circle(surface, EYES_DARK, (bear_x - 18, bear_y - 8), 6)
        pygame.draw.circle(surface, EYES_DARK, (bear_x + 18, bear_y - 8), 6)

        # Crate
        crate_rect = pygame.Rect(145, 83, 90, 90)
        pygame.draw.rect(surface, BOX_YELLOW, crate_rect)
        pygame.draw.rect(surface, BOX_OUTLINE, crate_rect, width=6)
        # Wooden Cross
        pygame.draw.line(
            surface,
            BOX_OUTLINE,
            (145 + 8, 83 + 8),
            (145 + 90 - 8, 83 + 90 - 8),
            width=6,
        )
        pygame.draw.line(
            surface,
            BOX_OUTLINE,
            (145 + 90 - 8, 83 + 8),
            (145 + 8, 83 + 90 - 8),
            width=6,
        )

    elif size == 48:
        # Bear
        bear_x, bear_y = 17, 24
        bear_r = 9
        # Ears
        pygame.draw.circle(surface, BEAR_SHADOW, (bear_x - 6, bear_y - 6), 3.5)
        pygame.draw.circle(surface, BEAR_SHADOW, (bear_x + 6, bear_y - 6), 3.5)
        # Head
        pygame.draw.circle(surface, BEAR_PURPLE, (bear_x, bear_y), bear_r)
        # Cheeks
        pygame.draw.circle(surface, CHEEKS_PINK, (bear_x - 5, bear_y + 2), 1.5)
        pygame.draw.circle(surface, CHEEKS_PINK, (bear_x + 5, bear_y + 2), 1.5)
        # Eyes
        pygame.draw.circle(surface, EYES_DARK, (bear_x - 3, bear_y - 1.5), 1.2)
        pygame.draw.circle(surface, EYES_DARK, (bear_x + 3, bear_y - 1.5), 1.2)

        # Crate
        crate_rect = pygame.Rect(27, 15, 18, 18)
        pygame.draw.rect(surface, BOX_YELLOW, crate_rect)
        pygame.draw.rect(surface, BOX_OUTLINE, crate_rect, width=2)
        pygame.draw.line(
            surface, BOX_OUTLINE, (27 + 2, 15 + 2), (27 + 18 - 2, 15 + 18 - 2), width=2
        )
        pygame.draw.line(
            surface, BOX_OUTLINE, (27 + 18 - 2, 15 + 2), (27 + 2, 15 + 18 - 2), width=2
        )

    elif size == 32:
        # Bear
        bear_x, bear_y = 11, 16
        bear_r = 6
        # Ears
        pygame.draw.circle(surface, BEAR_SHADOW, (bear_x - 4, bear_y - 4), 2)
        pygame.draw.circle(surface, BEAR_SHADOW, (bear_x + 4, bear_y - 4), 2)
        # Head
        pygame.draw.circle(surface, BEAR_PURPLE, (bear_x, bear_y), bear_r)
        # Eyes
        surface.set_at((bear_x - 2, bear_y - 1), EYES_DARK)
        surface.set_at((bear_x + 2, bear_y - 1), EYES_DARK)

        # Crate
        crate_rect = pygame.Rect(18, 10, 12, 12)
        pygame.draw.rect(surface, BOX_YELLOW, crate_rect)
        pygame.draw.rect(surface, BOX_OUTLINE, crate_rect, width=1)
        pygame.draw.line(
            surface, BOX_OUTLINE, (18 + 1, 10 + 1), (18 + 12 - 1, 10 + 12 - 1), width=1
        )
        pygame.draw.line(
            surface, BOX_OUTLINE, (18 + 12 - 1, 10 + 1), (18 + 1, 10 + 12 - 1), width=1
        )

    else:  # 16
        # Bear
        bear_x, bear_y = 5, 8
        bear_r = 3
        # Ears
        surface.set_at((bear_x - 2, bear_y - 2), BEAR_SHADOW)
        surface.set_at((bear_x + 2, bear_y - 2), BEAR_SHADOW)
        # Head
        pygame.draw.circle(surface, BEAR_PURPLE, (bear_x, bear_y), bear_r)
        # Eyes
        surface.set_at((bear_x - 1, bear_y), EYES_DARK)
        surface.set_at((bear_x + 1, bear_y), EYES_DARK)

        # Crate
        crate_rect = pygame.Rect(9, 5, 6, 6)
        pygame.draw.rect(surface, BOX_YELLOW, crate_rect)
        pygame.draw.rect(surface, BOX_OUTLINE, crate_rect, width=1)

    return surface


def build_ico(png_files: list[Path], output_ico: Path) -> None:
    """Assembles PNG files into a single Windows .ico container."""
    # Header: Reserved (2B, 0), Type (2B, 1 for icon),
    # Count (2B, len(png_files))
    header = struct.pack("<HHH", 0, 1, len(png_files))

    entries = []
    image_data_list = []

    current_offset = 6 + 16 * len(png_files)

    for png_path in png_files:
        with open(png_path, "rb") as f:
            png_bytes = f.read()

        # Dimensions
        # In pygame drawing, size is extracted from filename
        size = int(png_path.stem.split("_")[-1])
        width = 0 if size >= 256 else size
        height = 0 if size >= 256 else size

        # Directory Entry:
        # width (1B), height (1B), colorCount (1B, 0), reserved (1B, 0),
        # planes (2B, 1), bitCount (2B, 32), bytesInRes (4B), imageOffset (4B)
        entry = struct.pack(
            "<BBBBHHII", width, height, 0, 0, 1, 32, len(png_bytes), current_offset
        )
        entries.append(entry)
        image_data_list.append(png_bytes)
        current_offset += len(png_bytes)

    # Write output
    with open(output_ico, "wb") as f:
        f.write(header)
        for entry in entries:
            f.write(entry)
        for image_data in image_data_list:
            f.write(image_data)


def main() -> None:
    project_root = Path(__file__).parent.parent.resolve()
    icon_dir = project_root / "src" / "pushbox" / "assets" / "icon"
    icon_dir.mkdir(parents=True, exist_ok=True)
    output_ico = icon_dir / "pushbox.ico"

    sizes = [16, 32, 48, 256]
    temp_files = []

    print("Generating geometric multi-resolution icons...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        for size in sizes:
            surface = draw_icon_surface(size)
            png_file = tmp_path / f"icon_{size}.png"
            pygame.image.save(surface, str(png_file))
            temp_files.append(png_file)
            print(f"  Generated {size}x{size} PNG...")

        print("Compiling PNGs into pushbox.ico...")
        build_ico(temp_files, output_ico)

    print(f"Successfully generated standard Windows ICO at: {output_ico}")
    print(f"File size: {output_ico.stat().st_size / 1024:.2f} KB")


if __name__ == "__main__":
    main()
