"""Integration tests for persistent naming of imported custom levels."""

import os

import pytest

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

from src.pushbox.models.level import Level, LevelManager
from src.pushbox.utils.level_share import export_level_to_code
from src.pushbox.views.ui_components import LevelSelector


@pytest.fixture(autouse=True)
def initialize_pygame():
    """Initialize the font subsystem required by the level selector."""
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.mark.parametrize(
    ("existing_name", "shared_name"),
    [("Foo", "foo"), ("foo", "FOO")],
)
def test_case_conflicts_import_and_repeated_import_stay_unique(
    tmp_path,
    existing_name: str,
    shared_name: str,
) -> None:
    levels = LevelManager(levels_dir=str(tmp_path / "levels"))
    grid = [
        [1, 1, 1, 1, 1],
        [1, 4, 3, 2, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    levels.save_level(Level(existing_name, grid))
    selector = LevelSelector(pygame.Surface((800, 600)), levels)
    share_code = export_level_to_code(shared_name, grid)

    selector._import_level(share_code)
    first_import_name = f"{shared_name} (2)"
    assert selector.import_error_message is None
    assert levels.get_level(first_import_name) is not None

    selector._import_level(share_code)
    second_import_name = f"{shared_name} (3)"
    assert selector.import_error_message is None
    assert levels.get_level(second_import_name) is not None
