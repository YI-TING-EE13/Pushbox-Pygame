"""Level sharing encoder, decoder, and validation logic."""

import base64
import json
import re
import sys
import zlib
from typing import Any


class LevelShareError(Exception):
    """Custom exception raised during level import/export operations."""

    pass


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
        raise LevelShareError("分享碼格式不正確（必須是 JSON 物件）。")

    schema = payload_dict.get("schema")
    if schema != "pushbox-level-share-v1":
        raise LevelShareError("不支援此分享碼的版本。")

    name = payload_dict.get("name")
    if name is not None and not isinstance(name, str):
        raise LevelShareError("關卡名稱必須是文字。")

    grid = payload_dict.get("grid")
    if not isinstance(grid, list) or not grid:
        raise LevelShareError("關卡資料不合法：網格不可為空。")

    rows = len(grid)
    for r_idx, row in enumerate(grid):
        if not isinstance(row, list):
            raise LevelShareError(f"關卡資料不合法：第 {r_idx} 行必須是列表。")

    cols = len(grid[0])
    for _r_idx, row in enumerate(grid):
        if len(row) != cols:
            raise LevelShareError("關卡資料不合法：網格必須是矩形。")

    if not (5 <= rows <= 20) or not (5 <= cols <= 20):
        raise LevelShareError("關卡資料不合法：地圖尺寸需在 5x5 到 20x20 之間。")

    # Allowed cells are 0 (EMPTY), 1 (WALL), 2 (TARGET), 3 (BOX), 4 (PLAYER)
    # 5 is not allowed in imported starting grid
    player_count = 0
    box_count = 0
    target_count = 0

    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if not isinstance(cell, int) or cell < 0 or cell > 4:
                raise LevelShareError(f"關卡資料不合法：包含非法物件值 {cell}。")
            if cell == 4:  # CellType.PLAYER
                player_count += 1
            elif cell == 3:  # CellType.BOX
                box_count += 1
            elif cell == 2:  # CellType.TARGET
                target_count += 1

    if player_count != 1:
        raise LevelShareError("關卡資料不合法：必須恰好只有 1 位玩家。")
    if box_count < 1:
        raise LevelShareError("關卡資料不合法：至少需要一個箱子。")
    if box_count != target_count:
        raise LevelShareError(
            f"關卡資料不合法：箱子({box_count})與目標({target_count})數量需一致。"
        )

    # Perimeter wall check
    for c in range(cols):
        if grid[0][c] != 1 or grid[rows - 1][c] != 1:
            raise LevelShareError("關卡資料不合法：外圍邊界必須完全封閉為牆壁。")
    for r in range(rows):
        if grid[r][0] != 1 or grid[r][cols - 1] != 1:
            raise LevelShareError("關卡資料不合法：外圍邊界必須完全封閉為牆壁。")


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
        raise LevelShareError(f"匯出失敗，請確認地圖資料完整。({e})") from e


def import_level_from_code(code: str) -> dict[str, Any]:
    """Import a level payload dictionary from a PBX_ code string."""
    if not isinstance(code, str):
        raise LevelShareError("分享碼格式不正確（必須是字串）。")

    code = code.strip()
    if len(code) > 20000:
        raise LevelShareError("分享碼過長或資料過大。")

    if not code.startswith("PBX_"):
        raise LevelShareError("分享碼格式不正確（必須以 PBX_ 開頭）。")

    b64_part = code[4:]

    try:
        compressed = base64.b64decode(b64_part)
    except Exception as e:
        raise LevelShareError("分享碼格式不正確（無法進行 Base64 解碼）。") from e

    # Preliminary size check of compressed data
    if len(compressed) > 100000:
        raise LevelShareError("分享碼解壓後資料過大。")

    try:
        utf8_bytes = zlib.decompress(compressed)
    except Exception as e:
        raise LevelShareError("分享碼格式不正確（無法進行 zlib 解壓縮）。") from e

    # STRICT check on decompressed string length (max 100,000 characters)
    if len(utf8_bytes) > 100000:
        raise LevelShareError("分享碼解壓後資料過大。")

    try:
        payload_str = utf8_bytes.decode("utf-8")
    except Exception as e:
        raise LevelShareError("分享碼格式不正確（無法進行 UTF-8 解碼）。") from e

    try:
        payload = json.loads(payload_str)
    except Exception as e:
        raise LevelShareError("分享碼格式不正確（無法進行 JSON 解析）。") from e

    validate_import_payload(payload)
    if isinstance(payload, dict):
        return payload
    raise LevelShareError("分享碼格式不正確。")


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
