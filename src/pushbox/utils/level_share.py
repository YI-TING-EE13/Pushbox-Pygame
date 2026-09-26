"""Level sharing encoder, decoder, and validation logic."""

import base64
import json
import re
import sys
import zlib
from typing import Any


class LevelShareError(Exception):
    """Custom exception raised during level import/export operations."""

    def __init__(self, translation_key: str, **values: object) -> None:
        from .i18n import t

        super().__init__(t(translation_key).format(**values))


def sanitize_level_name(name: str) -> str:
    """Sanitize the level name to avoid path traversal, excess length, or bad chars."""
    if not isinstance(name, str):
        return "Imported Level"
    name = name.strip()
    if not name:
        return "Imported Level"
    # Remove any path traversal sequences and keep alphanumeric/Chinese/spaces/dashes
    # We strip out dots, slashes, backslashes
    name = re.sub(r"[\\./\x00-\x1f]", "", name)
    # Keep only safe chars or Chinese chars
    name = re.sub(r"[^\w\s\u4e00-\u9fff\-]", "", name)
    # Truncate to maximum 30 characters for UI safety
    name = name.strip()[:30]
    return name or "Imported Level"


def deduplicate_level_name(name: str, existing_names: list[str]) -> str:
    """Generate a unique name if there is already a custom level with the same name."""
    sanitized = sanitize_level_name(name)

    # Also explicitly avoid conflict with default levels (Level 0 through Level 30)
    protected_names = {f"Level {i}" for i in range(31)}

    # Merge existing and protected
    all_forbidden = set(existing_names) | protected_names

    if sanitized not in all_forbidden:
        return sanitized

    # Try appending (2), (3), etc.
    idx = 2
    while True:
        candidate = f"{sanitized} ({idx})"
        if candidate not in all_forbidden:
            return candidate
        idx += 1


def validate_import_payload(payload_dict: Any) -> None:
    """Validate a decompressed dict payload against strict safety rules."""
    if not isinstance(payload_dict, dict):
        raise LevelShareError("level_share.error.payload_object")

    schema = payload_dict.get("schema")
    if schema != "pushbox-level-share-v1":
        raise LevelShareError("level_share.error.schema")

    name = payload_dict.get("name")
    if name is not None and not isinstance(name, str):
        raise LevelShareError("level_share.error.name")

    grid = payload_dict.get("grid")
    if not isinstance(grid, list) or not grid:
        raise LevelShareError("level_share.error.grid_empty")

    rows = len(grid)
    for r_idx, row in enumerate(grid):
        if not isinstance(row, list):
            raise LevelShareError("level_share.error.row_type", row=r_idx)

    cols = len(grid[0])
    for _r_idx, row in enumerate(grid):
        if len(row) != cols:
            raise LevelShareError("level_share.error.not_rectangular")

    if not (5 <= rows <= 20) or not (5 <= cols <= 20):
        raise LevelShareError("level_share.error.dimensions")

    # Allowed cells are 0 (EMPTY), 1 (WALL), 2 (TARGET), 3 (BOX), 4 (PLAYER)
    # 5 is not allowed in imported starting grid
    player_count = 0
    box_count = 0
    target_count = 0

    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if not isinstance(cell, int) or cell < 0 or cell > 4:
                raise LevelShareError("level_share.error.cell", cell=cell)
            if cell == 4:  # CellType.PLAYER
                player_count += 1
            elif cell == 3:  # CellType.BOX
                box_count += 1
            elif cell == 2:  # CellType.TARGET
                target_count += 1

    if player_count != 1:
        raise LevelShareError("level_share.error.players")
    if box_count < 1:
        raise LevelShareError("level_share.error.boxes")
    if box_count != target_count:
        raise LevelShareError(
            "level_share.error.box_target_counts",
            boxes=box_count,
            targets=target_count,
        )

    # Perimeter wall check
    for c in range(cols):
        if grid[0][c] != 1 or grid[rows - 1][c] != 1:
            raise LevelShareError("level_share.error.perimeter")
    for r in range(rows):
        if grid[r][0] != 1 or grid[r][cols - 1] != 1:
            raise LevelShareError("level_share.error.perimeter")


def export_level_to_code(name: str, grid: list[list[int]]) -> str:
    """Export a level name and grid to a zlib+base64 PBX_ code string."""
    try:
        payload = {
            "schema": "pushbox-level-share-v1",
            "name": name,
            "grid": grid,
            "metadata": {"source": "custom"},
        }
        json_str = json.dumps(payload, ensure_ascii=False)
        utf8_bytes = json_str.encode("utf-8")
        compressed = zlib.compress(utf8_bytes)
        b64 = base64.b64encode(compressed).decode("ascii")
        return f"PBX_{b64}"
    except Exception as e:
        raise LevelShareError("level_share.error.export") from e


def import_level_from_code(code: str) -> dict[str, Any]:
    """Import a level payload dictionary from a PBX_ code string."""
    if not isinstance(code, str):
        raise LevelShareError("level_share.error.code_type")

    code = code.strip()
    if len(code) > 20000:
        raise LevelShareError("level_share.error.too_large")

    if not code.startswith("PBX_"):
        raise LevelShareError("level_share.error.prefix")

    b64_part = code[4:]

    try:
        compressed = base64.b64decode(b64_part)
    except Exception as e:
        raise LevelShareError("level_share.error.base64") from e

    # Preliminary size check of compressed data
    if len(compressed) > 100000:
        raise LevelShareError("level_share.error.too_large")

    try:
        utf8_bytes = zlib.decompress(compressed)
    except Exception as e:
        raise LevelShareError("level_share.error.compression") from e

    # STRICT check on decompressed string length (max 100,000 characters)
    if len(utf8_bytes) > 100000:
        raise LevelShareError("level_share.error.too_large")

    try:
        payload_str = utf8_bytes.decode("utf-8")
    except Exception as e:
        raise LevelShareError("level_share.error.utf8") from e

    try:
        payload = json.loads(payload_str)
    except Exception as e:
        raise LevelShareError("level_share.error.json") from e

    validate_import_payload(payload)
    if isinstance(payload, dict):
        return payload
    raise LevelShareError("level_share.error.invalid")


def best_effort_copy_to_clipboard(text: str) -> bool:
    """Best-effort copy text to clipboard using tkinter or subprocess clip.

    Safe for non-Windows platforms, headless environments, and lacks
    external dependencies.
    """
    # Channel 1: tkinter
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        return True
    except Exception:
        pass

    # Channel 2: Windows native clip.exe command with explicit 2s timeout
    if sys.platform == "win32":
        try:
            import subprocess

            process = subprocess.Popen(
                "clip",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            process.communicate(input=text.encode("utf-8"), timeout=2)
            return True
        except Exception:
            pass

    return False


def best_effort_get_clipboard_text(max_len: int = 20000) -> str:
    """Best-effort get text from clipboard using tkinter or PowerShell Get-Clipboard.

    Safe for non-Windows platforms, headless environments, and lacks
    external dependencies.
    """
    # Channel 1: tkinter
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        if isinstance(text, str):
            return text[:max_len]
    except Exception:
        pass

    # Channel 2: Windows powershell native clip retriever with 2s timeout
    if sys.platform == "win32":
        try:
            import subprocess

            res = subprocess.run(
                ["powershell", "-Command", "Get-Clipboard"],
                capture_output=True,
                text=True,
                shell=True,
                timeout=2,
            )
            text = res.stdout
            if isinstance(text, str):
                return text.strip()[:max_len]
        except Exception:
            pass

    return ""
