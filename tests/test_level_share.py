"""Unit tests for level sharing, compression, encoding, and validation."""

import pytest

from src.pushbox.utils.level_share import (
    LevelShareError,
    deduplicate_level_name,
    export_level_to_code,
    import_level_from_code,
    sanitize_level_name,
)


def test_round_trip_success() -> None:
    """Verify that export followed by import correctly restores name and grid."""
    name = "測試關卡-Sokoban"
    grid = [
        [1, 1, 1, 1, 1],
        [1, 4, 0, 2, 1],
        [1, 0, 3, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    code = export_level_to_code(name, grid)
    assert code.startswith("PBX_")

    payload = import_level_from_code(code)
    assert payload["schema"] == "pushbox-level-share-v1"
    assert payload["name"] == name
    assert payload["grid"] == grid


def test_invalid_prefix() -> None:
    """Verify that a code without the PBX_ prefix raises an error."""
    with pytest.raises(LevelShareError, match="必須以 PBX_ 開頭"):
        import_level_from_code("INVALID_CODE_XYZ")


def test_invalid_base64_format() -> None:
    """Verify that a non-base64 code raises an error."""
    with pytest.raises(LevelShareError, match="無法進行 Base64 解碼"):
        import_level_from_code("PBX_!!!notbase64!!!")


def test_invalid_zlib_decompression() -> None:
    """Verify that a base64-valid but zlib-invalid payload raises an error."""
    import base64

    bad_bytes = b"Some plain text, not compressed by zlib"
    bad_b64 = base64.b64encode(bad_bytes).decode("ascii")
    with pytest.raises(LevelShareError, match="無法進行 zlib 解壓縮"):
        import_level_from_code(f"PBX_{bad_b64}")


def test_invalid_json_format() -> None:
    """Verify that decompressed bytes that are not valid JSON raise an error."""
    import base64
    import zlib

    compressed = zlib.compress(b"{bad json, missing brackets")
    bad_b64 = base64.b64encode(compressed).decode("ascii")
    with pytest.raises(LevelShareError, match="無法進行 JSON 解析"):
        import_level_from_code(f"PBX_{bad_b64}")


def test_schema_mismatch() -> None:
    """Verify that schema versions other than pushbox-level-share-v1 raise an error."""
    import base64
    import json
    import zlib

    bad_payload = {
        "schema": "pushbox-level-share-v2",
        "name": "Level",
        "grid": [[1, 1, 1], [1, 4, 1], [1, 1, 1]],
    }
    json_bytes = json.dumps(bad_payload).encode("utf-8")
    compressed = zlib.compress(json_bytes)
    b64 = base64.b64encode(compressed).decode("ascii")
    with pytest.raises(LevelShareError, match="不支援此分享碼的版本"):
        import_level_from_code(f"PBX_{b64}")


def test_code_length_limit() -> None:
    """Verify that sharing code string exceeding 20000 chars is rejected."""
    long_code = "PBX_" + "A" * 20001
    with pytest.raises(LevelShareError, match="分享碼過長或資料過大"):
        import_level_from_code(long_code)


def test_empty_grid_rejected() -> None:
    """Verify that an empty grid payload is rejected."""
    payload = {"schema": "pushbox-level-share-v1", "name": "Empty", "grid": []}
    # Direct encode to bypass export_level_to_code's normal state checks
    import base64
    import json
    import zlib

    json_bytes = json.dumps(payload).encode("utf-8")
    code = "PBX_" + base64.b64encode(zlib.compress(json_bytes)).decode("ascii")
    with pytest.raises(LevelShareError, match="網格不可為空"):
        import_level_from_code(code)


def test_non_rectangular_grid_rejected() -> None:
    """Verify that a grid with rows of varying lengths is rejected."""
    name = "NonRect"
    grid = [
        [1, 1, 1, 1, 1],
        [1, 4, 0, 2],  # Length 4 instead of 5
        [1, 0, 3, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    # We directly build a code to bypass export checking and test imports
    import base64
    import json
    import zlib

    payload = {"schema": "pushbox-level-share-v1", "name": name, "grid": grid}
    json_bytes = json.dumps(payload).encode("utf-8")
    code = "PBX_" + base64.b64encode(zlib.compress(json_bytes)).decode("ascii")
    with pytest.raises(LevelShareError, match="網格必須是矩形"):
        import_level_from_code(code)


def test_dimension_bounds() -> None:
    """Verify size constraints: must be 5x5 to 20x20."""
    # Under 5x5 (e.g. 4x5)
    under_grid = [
        [1, 1, 1, 1, 1],
        [1, 4, 3, 2, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    # 4 rows is too small
    import base64
    import json
    import zlib

    payload = {"schema": "pushbox-level-share-v1", "name": "Under", "grid": under_grid}
    json_bytes = json.dumps(payload).encode("utf-8")
    code = "PBX_" + base64.b64encode(zlib.compress(json_bytes)).decode("ascii")
    with pytest.raises(LevelShareError, match="地圖尺寸需在 5x5 到 20x20 之間"):
        import_level_from_code(code)


def test_illegal_cell_value() -> None:
    """Verify that cell values other than 0 to 4 are rejected (e.g. 5 or negative)."""
    grid = [
        [1, 1, 1, 1, 1],
        [1, 4, 5, 2, 1],  # 5 (BOX_ON_TARGET) is not allowed in imported starting layout
        [1, 0, 3, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    import base64
    import json
    import zlib

    payload = {"schema": "pushbox-level-share-v1", "name": "IllegalCell", "grid": grid}
    json_bytes = json.dumps(payload).encode("utf-8")
    code = "PBX_" + base64.b64encode(zlib.compress(json_bytes)).decode("ascii")
    with pytest.raises(LevelShareError, match="包含非法物件值 5"):
        import_level_from_code(code)


def test_player_count() -> None:
    """Verify exactly one player requirement."""
    # Scenario A: No player
    grid_no_player = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 2, 1],
        [1, 0, 3, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    import base64
    import json
    import zlib

    payload = {
        "schema": "pushbox-level-share-v1",
        "name": "NoPlayer",
        "grid": grid_no_player,
    }
    json_bytes = json.dumps(payload).encode("utf-8")
    code = "PBX_" + base64.b64encode(zlib.compress(json_bytes)).decode("ascii")
    with pytest.raises(LevelShareError, match="必須恰好只有 1 位玩家"):
        import_level_from_code(code)

    # Scenario B: Multiple players
    grid_multi_player = [
        [1, 1, 1, 1, 1],
        [1, 4, 4, 2, 1],  # Two players
        [1, 0, 3, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    payload["grid"] = grid_multi_player
    json_bytes = json.dumps(payload).encode("utf-8")
    code = "PBX_" + base64.b64encode(zlib.compress(json_bytes)).decode("ascii")
    with pytest.raises(LevelShareError, match="必須恰好只有 1 位玩家"):
        import_level_from_code(code)


def test_box_and_target_counts() -> None:
    """Verify box count, target count, and box == target constraints."""
    # Scenario A: No boxes
    grid_no_box = [
        [1, 1, 1, 1, 1],
        [1, 4, 0, 2, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    import base64
    import json
    import zlib

    payload = {"schema": "pushbox-level-share-v1", "name": "NoBox", "grid": grid_no_box}
    json_bytes = json.dumps(payload).encode("utf-8")
    code = "PBX_" + base64.b64encode(zlib.compress(json_bytes)).decode("ascii")
    with pytest.raises(LevelShareError, match="至少需要一個箱子"):
        import_level_from_code(code)

    # Scenario B: Boxes != Targets
    grid_unbalanced = [
        [1, 1, 1, 1, 1],
        [1, 4, 0, 2, 1],  # 1 target
        [1, 0, 3, 3, 1],  # 2 boxes
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    payload["grid"] = grid_unbalanced
    json_bytes = json.dumps(payload).encode("utf-8")
    code = "PBX_" + base64.b64encode(zlib.compress(json_bytes)).decode("ascii")
    with pytest.raises(LevelShareError, match="箱子\\(2\\)與目標\\(1\\)數量需一致"):
        import_level_from_code(code)


def test_perimeter_enclosure() -> None:
    """Verify that boundaries must be completely enclosed by walls."""
    grid_open_boundary = [
        [1, 1, 0, 1, 1],  # Gap in top boundary
        [1, 4, 0, 2, 1],
        [1, 0, 3, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    import base64
    import json
    import zlib

    payload = {
        "schema": "pushbox-level-share-v1",
        "name": "OpenBoundary",
        "grid": grid_open_boundary,
    }
    json_bytes = json.dumps(payload).encode("utf-8")
    code = "PBX_" + base64.b64encode(zlib.compress(json_bytes)).decode("ascii")
    with pytest.raises(LevelShareError, match="外圍邊界必須完全封閉為牆壁"):
        import_level_from_code(code)


def test_name_sanitization() -> None:
    """Verify sanitization of names (no slashes, dots, path traversal, excess chars)."""
    assert sanitize_level_name("../Level 1") == "Level 1"
    assert sanitize_level_name("My/Bad\\Level.json") == "MyBadLeveljson"
    assert sanitize_level_name("   ") == "Imported Level"
    assert sanitize_level_name(None) == "Imported Level"
    # Chinese name is allowed
    assert sanitize_level_name("我的精緻關卡-1") == "我的精緻關卡-1"
    # Truncation
    assert len(sanitize_level_name("A" * 100)) == 30


def test_name_deduplication() -> None:
    """Verify unique suffix generation when duplicate name exists."""
    existing = ["Custom Level", "Custom Level (2)", "Level 1"]
    assert deduplicate_level_name("Custom Level", existing) == "Custom Level (3)"
    assert deduplicate_level_name("Level 1", existing) == "Level 1 (2)"
    assert deduplicate_level_name("Unique Level", existing) == "Unique Level"
