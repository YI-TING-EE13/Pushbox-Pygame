"""Level editor for creating custom levels."""

from typing import Callable, Optional

import pygame

from ..models.level import Level
from ..utils.constants import COLORS, CellType
from .ui_components import InputBox, ModernButton


class LevelEditor:
    """Level editor interface for creating and modifying custom Sokoban levels.

    Provides tools for placing walls, floors, targets, boxes, and the player,
    supporting keyboard shortcuts, mouse paint/erase operations, undo/redo
    stacks, map resizing, validation checks before saving, and local file storage.
    """

    TOOLS = [
        ("牆壁 (1)", CellType.WALL, COLORS["wall"]),
        ("地板 (2)", CellType.EMPTY, COLORS["floor_light"]),
        ("目標 (3)", CellType.TARGET, COLORS["target"]),
        ("箱子 (4)", CellType.BOX, COLORS["box"]),
        ("玩家 (5)", CellType.PLAYER, COLORS["player"]),
    ]

    def __init__(
        self, screen: pygame.Surface, existing_level: Optional[Level] = None
    ) -> None:
        """Initialize the level editor with screen and optional existing level."""
        self.screen = screen

        # Grid Data
        self.rows = 10
        self.cols = 10
        self.grid: list[list[int]] = [
            [CellType.EMPTY for _ in range(self.cols)] for _ in range(self.rows)
        ]

        if existing_level:
            self.rows = existing_level.rows
            self.cols = existing_level.cols
            self.grid = existing_level.initial_grid.tolist()
            self.level_name = existing_level.name
        else:
            self.level_name = "Custom Level"

        self.selected_tool = CellType.WALL
        self.player_placed = False

        # UI Resources
        self.font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        self._init_fonts()

        # Layout Config
        self.sidebar_width = 260
        self.bottom_bar_height = 80
        self.cell_size = 40
        self.offset_x = self.sidebar_width + 20
        self.offset_y = 20

        self.on_save: Optional[Callable[[Level], None]] = None
        self.on_exit: Optional[Callable[[], None]] = None
        self.on_playtest: Optional[Callable[[Level], None]] = None

        self.original_grid = [row[:] for row in self.grid]
        self.original_name = self.level_name
        self.show_confirm_dialog = False

        self.status_message = ""
        self.status_timer = 0

        # History
        self.history: list[list[list[int]]] = []
        self.redo_stack: list[list[list[int]]] = []
        self._save_state()

        # UI Elements
        self.name_input = InputBox(20, 60, 220, 32, self.level_name, self.font)
        self.buttons: list[ModernButton] = []
        self._init_buttons()

    def _init_fonts(self) -> None:
        """Initialize UI fonts for titles, labels, and status bar, with fallbacks."""
        try:
            self.font = pygame.font.SysFont("microsoftyahei", 20)
            self.small_font = pygame.font.SysFont("microsoftyahei", 16)
            self.title_font = pygame.font.SysFont("microsoftyahei", 32, bold=True)
        except (OSError, pygame.error):
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 20)
            self.title_font = pygame.font.Font(None, 40)

    def _init_buttons(self) -> None:
        """Initialize editor UI buttons including grid resizing and action bar."""
        self.buttons = []

        # --- Map Size Controls (In Sidebar) ---
        # Rows
        y_pos = 420
        self.buttons.append(
            ModernButton(
                20, y_pos, 30, 30, "-", lambda: self._change_size("rows", -1), self.font
            )
        )
        self.buttons.append(
            ModernButton(
                120, y_pos, 30, 30, "+", lambda: self._change_size("rows", 1), self.font
            )
        )

        # Cols
        y_pos += 50
        self.buttons.append(
            ModernButton(
                20, y_pos, 30, 30, "-", lambda: self._change_size("cols", -1), self.font
            )
        )
        self.buttons.append(
            ModernButton(
                120, y_pos, 30, 30, "+", lambda: self._change_size("cols", 1), self.font
            )
        )

        # --- Bottom Action Bar ---
        bar_y = self.screen.get_height() - 60
        btn_w = 90
        spacing = 15
        start_x = self.sidebar_width + 20

        # Undo/Redo
        self.buttons.append(
            ModernButton(start_x, bar_y, btn_w, 40, "Undo(Z)", self._undo, self.font)
        )
        self.buttons.append(
            ModernButton(
                start_x + btn_w + spacing,
                bar_y,
                btn_w,
                40,
                "Redo(Y)",
                self._redo,
                self.font,
            )
        )

        # Functional
        start_x += (btn_w + spacing) * 2 + 20
        self.buttons.append(
            ModernButton(
                start_x,
                bar_y,
                btn_w,
                40,
                "清除(C)",
                self._clear_grid,
                self.font,
                bg_color=COLORS["warning"],
            )
        )

        # Save/Exit (Right aligned)
        right_x = self.screen.get_width() - 20 - btn_w
        self.buttons.append(
            ModernButton(
                right_x,
                bar_y,
                btn_w,
                40,
                "退出",
                self._request_exit,
                self.font,
                bg_color=COLORS["error"],
            )
        )
        self.buttons.append(
            ModernButton(
                right_x - btn_w - spacing,
                bar_y,
                btn_w,
                40,
                "儲存(S)",
                self._save_level,
                self.font,
                bg_color=COLORS["success"],
            )
        )
        self.buttons.append(
            ModernButton(
                right_x - (btn_w + spacing) * 2,
                bar_y,
                btn_w,
                40,
                "試玩(T)",
                self._playtest_level,
                self.font,
                bg_color=COLORS["text_highlight"],
            )
        )

    def set_on_save(self, callback: Callable[[Level], None]) -> None:
        """Set callback function for when the level is saved."""
        self.on_save = callback

    def set_on_exit(self, callback: Callable[[], None]) -> None:
        """Set callback function for when the editor is exited."""
        self.on_exit = callback

    def set_on_playtest(self, callback: Callable[[Level], None]) -> None:
        """Set callback function for when playtest is requested."""
        self.on_playtest = callback

    def show_status(self, message: str) -> None:
        """Display a status message in the editor status bar."""
        self.status_message = message
        self.status_timer = 120

    def _save_state(self) -> None:
        """Save the current grid state to the undo history stack."""
        current_state = [row[:] for row in self.grid]
        if self.history and self.history[-1] == current_state:
            return
        self.history.append(current_state)
        if len(self.history) > 50:
            self.history.pop(0)
        self.redo_stack.clear()

    def _undo(self) -> None:
        """Undo the last grid modification."""
        if len(self.history) > 1:
            current_state = self.history.pop()
            self.redo_stack.append(current_state)
            previous_state = self.history[-1]
            self.grid = [row[:] for row in previous_state]
            self._update_dimensions()
            self.show_status("撤銷")

    def _redo(self) -> None:
        """Redo the last undone grid modification."""
        if self.redo_stack:
            next_state = self.redo_stack.pop()
            self.history.append(next_state)
            self.grid = [row[:] for row in next_state]
            self._update_dimensions()
            self.show_status("重做")

    def _update_dimensions(self) -> None:
        """Update rows and columns attributes based on the current grid shape."""
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 else 0

    def _change_size(self, dimension: str, delta: int) -> None:
        """Change map grid size (rows or columns) within valid limits (5 to 20)."""
        if dimension == "rows":
            new_rows = self.rows + delta
            if 5 <= new_rows <= 20:
                if delta > 0:
                    self.grid.append([CellType.EMPTY for _ in range(self.cols)])
                else:
                    self.grid.pop()
                self.rows = new_rows
        elif dimension == "cols":
            new_cols = self.cols + delta
            if 5 <= new_cols <= 20:
                if delta > 0:
                    for row in self.grid:
                        row.append(CellType.EMPTY)
                else:
                    for row in self.grid:
                        row.pop()
                self.cols = new_cols

        self._save_state()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle Pygame events for inputs, buttons, paint, and shortcuts."""
        # Confirmation Dialog intercept
        if self.show_confirm_dialog:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._check_confirm_click(event.pos):
                    return True
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_y, pygame.K_RETURN]:
                    self.show_confirm_dialog = False
                    if self.on_exit:
                        self.on_exit()
                    return True
                elif event.key in [pygame.K_n, pygame.K_ESCAPE]:
                    self.show_confirm_dialog = False
                    return True
            return True

        # 1. Handle Input Box - If active, it consumes input and BLOCKS other shortcuts
        if self.name_input.handle_event(event):
            return True

        # If input box is active (typing), ignore other keys
        if self.name_input.active:
            return True

        # 2. Handle Buttons
        for btn in self.buttons:
            if btn.handle_event(event):
                return True

        # 3. Handle Mouse Actions
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left Click
                if self._check_tool_click(event.pos):
                    return True
                if self._is_on_grid(event.pos):
                    self._handle_paint(event.pos, erase=False)
                    self._save_state()
                    return True
            elif event.button == 3:  # Right Click (Erase)
                if self._is_on_grid(event.pos):
                    self._handle_paint(event.pos, erase=True)
                    self._save_state()
                    return True

        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:  # Left Drag
                if self._is_on_grid(event.pos):
                    self._handle_paint(event.pos, erase=False)
                    return True
            elif event.buttons[2]:  # Right Drag
                if self._is_on_grid(event.pos):
                    self._handle_paint(event.pos, erase=True)
                    return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1, 3):
                self._save_state()

        # 4. Handle Shortcuts (Only when input box inactive)
        elif event.type == pygame.KEYDOWN:
            key_map = {
                pygame.K_1: CellType.WALL,
                pygame.K_2: CellType.EMPTY,
                pygame.K_3: CellType.TARGET,
                pygame.K_4: CellType.BOX,
                pygame.K_5: CellType.PLAYER,
            }
            if event.key in key_map:
                self.selected_tool = key_map[event.key]
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self._save_level()
            elif event.key == pygame.K_z:
                self._undo()
            elif event.key == pygame.K_y or event.key == pygame.K_r:
                self._redo()
            elif event.key == pygame.K_ESCAPE:
                self._request_exit()
            elif event.key == pygame.K_t:
                self._playtest_level()
            elif event.key == pygame.K_c:
                self._clear_grid()
                self._save_state()

        return False

    def _is_on_grid(self, pos: tuple[int, int]) -> bool:
        """Check if a screen position is inside the editor grid area."""
        x, y = pos
        # Dynamic centering based on current screen size
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        # Center in the remaining space
        avail_w = self.screen.get_width() - self.sidebar_width
        avail_h = self.screen.get_height() - self.bottom_bar_height

        start_x = self.sidebar_width + (avail_w - grid_width) // 2
        start_y = (avail_h - grid_height) // 2

        grid_x = (x - start_x) // self.cell_size
        grid_y = (y - start_y) // self.cell_size
        return 0 <= grid_x < self.cols and 0 <= grid_y < self.rows

    def _check_tool_click(self, pos: tuple[int, int]) -> bool:
        """Check if a sidebar tool selection button was clicked."""
        tool_x = 20
        tool_y = 130
        tool_height = 40
        for i, _ in enumerate(self.TOOLS):
            btn_rect = pygame.Rect(
                tool_x, tool_y + i * (tool_height + 10), 220, tool_height
            )
            if btn_rect.collidepoint(pos):
                self.selected_tool = self.TOOLS[i][1]
                return True
        return False

    def _handle_paint(self, pos: tuple[int, int], erase: bool) -> None:
        """Paint or erase cell elements on the grid based on selected tool."""
        x, y = pos

        # Re-calculate offsets (same logic as _is_on_grid)
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size
        avail_w = self.screen.get_width() - self.sidebar_width
        avail_h = self.screen.get_height() - self.bottom_bar_height
        start_x = self.sidebar_width + (avail_w - grid_width) // 2
        start_y = (avail_h - grid_height) // 2

        grid_x = (x - start_x) // self.cell_size
        grid_y = (y - start_y) // self.cell_size

        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
            target_val = CellType.EMPTY if erase else self.selected_tool

            # Logic: If placing player, remove old one
            if target_val == CellType.PLAYER:
                for r in range(self.rows):
                    for c in range(self.cols):
                        if self.grid[r][c] == CellType.PLAYER:
                            self.grid[r][c] = CellType.EMPTY
                self.player_placed = True
            elif (
                target_val == CellType.EMPTY
                and self.grid[grid_y][grid_x] == CellType.PLAYER
            ):
                self.player_placed = False

            self.grid[grid_y][grid_x] = target_val

    def _clear_grid(self) -> None:
        """Clear all cells on the grid and reset player status."""
        self.grid = [
            [CellType.EMPTY for _ in range(self.cols)] for _ in range(self.rows)
        ]
        self.player_placed = False
        self.show_status("網格已清除")

    def _save_level(self) -> None:
        """Perform grid validation checks and invoke the save callback."""
        has_player = any(CellType.PLAYER in row for row in self.grid)
        if not has_player:
            self.show_status("錯誤: 必須放置玩家!")
            return

        box_count = sum(row.count(CellType.BOX) for row in self.grid)
        target_count = sum(row.count(CellType.TARGET) for row in self.grid)

        if box_count == 0:
            self.show_status("錯誤: 至少需要一個箱子!")
            return
        if box_count != target_count:
            self.show_status(
                f"無法儲存: 箱子({box_count})與目標({target_count})數量必須相同!"
            )
            return

        level_name = self.name_input.text.strip()
        if not level_name:
            self.show_status("請輸入關卡名稱!")
            return

        trimmed_grid = [row[:] for row in self.grid]
        level = Level(level_name, trimmed_grid)
        if self.on_save:
            self.original_grid = trimmed_grid
            self.original_name = level_name
            self.on_save(level)

    def draw(self) -> None:
        """Draw the entire editor interface including sidebar, tools, and grid."""
        self.screen.fill(COLORS["background"])

        # --- Draw Sidebar ---
        pygame.draw.rect(
            self.screen,
            COLORS["panel_bg"],
            (0, 0, self.sidebar_width, self.screen.get_height()),
        )
        pygame.draw.line(
            self.screen,
            COLORS["grid_lines"],
            (self.sidebar_width, 0),
            (self.sidebar_width, self.screen.get_height()),
            2,
        )

        # Title
        if self.title_font:
            title = self.title_font.render("關卡編輯器", True, COLORS["text_main"])
            self.screen.blit(title, (20, 20))

        # Name Input
        if self.font:
            label = self.font.render("關卡名稱:", True, COLORS["text_dim"])
            self.screen.blit(label, (20, 35))
        self.name_input.draw(self.screen)

        # Tools
        self._draw_tool_selector()

        # Map Size Controls
        self._draw_size_controls()

        # Shortcuts Hints
        self._draw_hints()

        # --- Draw Grid Area ---
        self._draw_grid()

        # --- Draw Buttons (Re-layout on draw for responsiveness) ---
        # Update button positions in case window resized
        # This is simple manual layout logic
        btn_y = self.screen.get_height() - 60
        start_x = self.sidebar_width + 20
        # Fixed index order: Rows-, Rows+, Cols-, Cols+, Undo, Redo, Clear, Exit, Save
        # Rows/Cols buttons are in the sidebar; bottom bar buttons are updated here.

        # Update bottom bar buttons
        # Indices 4-9: Undo, Redo, Clear, PlayTest, Exit, Save
        if len(self.buttons) >= 10:
            # Undo
            self.buttons[4].rect.y = btn_y
            self.buttons[4].rect.x = start_x

            # Redo
            self.buttons[5].rect.y = btn_y
            self.buttons[5].rect.x = start_x + 105

            # Clear
            self.buttons[6].rect.y = btn_y
            self.buttons[6].rect.x = start_x + 230

            # PlayTest
            self.buttons[7].rect.y = btn_y
            self.buttons[7].rect.x = self.screen.get_width() - 340

            # Exit (Right)
            self.buttons[8].rect.y = btn_y
            self.buttons[8].rect.x = self.screen.get_width() - 110

            # Save (Right next to Exit)
            self.buttons[9].rect.y = btn_y
            self.buttons[9].rect.x = self.screen.get_width() - 225

        for btn in self.buttons:
            btn.draw(self.screen)

        # Status Message
        if self.status_timer > 0:
            self.status_timer -= 1
            self._draw_status()

        if self.show_confirm_dialog:
            self._draw_confirm_dialog()

    def _draw_tool_selector(self) -> None:
        """Draw the sidebar tool selector showing available grid elements."""
        tool_x = 20
        tool_y = 130
        tool_height = 40

        if self.font:
            label = self.font.render("選擇工具:", True, COLORS["text_dim"])
            self.screen.blit(label, (tool_x, tool_y - 25))

        for i, (name, tool_type, color) in enumerate(self.TOOLS):
            btn_rect = pygame.Rect(
                tool_x, tool_y + i * (tool_height + 6), 220, tool_height
            )

            if tool_type == self.selected_tool:
                pygame.draw.rect(
                    self.screen,
                    COLORS["text_highlight"],
                    btn_rect.inflate(4, 4),
                    border_radius=6,
                )

            pygame.draw.rect(
                self.screen, COLORS["button_default"], btn_rect, border_radius=5
            )

            # Color indicator
            pygame.draw.rect(
                self.screen,
                color,
                (btn_rect.left + 10, btn_rect.centery - 10, 20, 20),
                border_radius=3,
            )

            if self.font:
                text = self.font.render(name, True, COLORS["text_main"])
                self.screen.blit(
                    text,
                    (btn_rect.left + 40, btn_rect.centery - text.get_height() // 2),
                )

    def _draw_size_controls(self) -> None:
        """Draw grid size adjustment labels in the sidebar."""
        y_base = 390
        if self.font:
            label = self.font.render("地圖大小:", True, COLORS["text_dim"])
            self.screen.blit(label, (20, y_base))

            # Labels for Rows/Cols
            r_label = self.font.render(f"行數: {self.rows}", True, COLORS["text_main"])
            self.screen.blit(r_label, (55, y_base + 35))

            c_label = self.font.render(f"列數: {self.cols}", True, COLORS["text_main"])
            self.screen.blit(c_label, (55, y_base + 85))

    def _draw_grid(self) -> None:
        """Draw the level grid and centered cell elements."""
        # Dynamic centering
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size
        avail_w = self.screen.get_width() - self.sidebar_width
        avail_h = self.screen.get_height() - self.bottom_bar_height

        start_x = self.sidebar_width + (avail_w - grid_width) // 2
        start_y = (avail_h - grid_height) // 2

        grid_rect = pygame.Rect(
            start_x - 5, start_y - 5, grid_width + 10, grid_height + 10
        )

        pygame.draw.rect(self.screen, COLORS["panel_bg"], grid_rect, border_radius=5)
        pygame.draw.rect(
            self.screen, COLORS["grid_lines"], grid_rect, 2, border_radius=5
        )

        for row in range(self.rows):
            for col in range(self.cols):
                x = start_x + col * self.cell_size
                y = start_y + row * self.cell_size

                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                cell = self.grid[row][col]

                color = (
                    COLORS["floor_light"] if (row + col) % 2 == 0 else COLORS["floor"]
                )
                pygame.draw.rect(self.screen, color, rect)

                if cell == CellType.WALL:
                    pygame.draw.rect(
                        self.screen,
                        COLORS["wall"],
                        rect.inflate(-2, -2),
                        border_radius=2,
                    )
                elif cell == CellType.TARGET:
                    pygame.draw.circle(
                        self.screen, COLORS["target"], rect.center, self.cell_size // 4
                    )
                elif cell == CellType.BOX:
                    pygame.draw.rect(
                        self.screen,
                        COLORS["box"],
                        rect.inflate(-6, -6),
                        border_radius=4,
                    )
                elif cell == CellType.PLAYER:
                    pygame.draw.circle(
                        self.screen, COLORS["player"], rect.center, self.cell_size // 3
                    )

                pygame.draw.rect(self.screen, COLORS["grid_lines"], rect, 1)

    def _draw_status(self) -> None:
        """Draw the semi-transparent status message card."""
        if not self.status_message or not self.font:
            return
        surf = self.font.render(self.status_message, True, COLORS["text_main"])
        bg = surf.get_rect()
        bg.inflate_ip(20, 10)
        bg.centerx = (
            self.sidebar_width + (self.screen.get_width() - self.sidebar_width) // 2
        )
        bg.bottom = self.screen.get_height() - 80
        pygame.draw.rect(self.screen, COLORS["panel_bg"], bg, border_radius=5)
        pygame.draw.rect(self.screen, COLORS["text_highlight"], bg, 1, border_radius=5)
        self.screen.blit(surf, surf.get_rect(center=bg.center))

    def _draw_hints(self) -> None:
        """Draw shortcut hints in sidebar."""
        if not self.small_font:
            return

        y = 505
        # Line separator
        pygame.draw.line(
            self.screen,
            COLORS["grid_lines"],
            (20, y),
            (self.sidebar_width - 20, y),
            1,
        )
        y += 15

        label = self.small_font.render("操作提示:", True, COLORS["text_dim"])
        self.screen.blit(label, (20, y))
        y += 25

        hints = [
            "左鍵：放置 | 右鍵：清除",
            "1-5：切換工具",
            "Z：撤銷 | Y / R：重做",
            "Ctrl + S：儲存關卡",
            "C：清空地圖",
            "T：試玩關卡",
            "Esc：離開編輯器",
        ]

        for hint in hints:
            surf = self.small_font.render(hint, True, COLORS["text_dim"])
            self.screen.blit(surf, (20, y))
            y += 20

    def is_dirty(self) -> bool:
        """Check if there are unsaved modifications in grid or level name."""
        if self.name_input.text.strip() != self.original_name:
            return True
        return self.grid != self.original_grid

    def _request_exit(self) -> None:
        """Request editor exit, triggering confirmation dialog if dirty."""
        if self.is_dirty():
            self.show_confirm_dialog = True
        else:
            if self.on_exit:
                self.on_exit()

    def _playtest_level(self) -> None:
        """Validate grid layout and request a playtest session."""
        has_player = any(CellType.PLAYER in row for row in self.grid)
        if not has_player:
            self.show_status("錯誤: 必須放置玩家!")
            return

        box_count = sum(row.count(CellType.BOX) for row in self.grid)
        target_count = sum(row.count(CellType.TARGET) for row in self.grid)

        if box_count == 0:
            self.show_status("錯誤: 至少需要一個箱子!")
            return
        if box_count != target_count:
            self.show_status(
                f"無法試玩: 箱子({box_count})與目標({target_count})數量必須相同!"
            )
            return

        level_name = self.name_input.text.strip() or "Play Test"
        trimmed_grid = [row[:] for row in self.grid]
        level = Level(level_name, trimmed_grid)
        if self.on_playtest:
            self.on_playtest(level)

    def _draw_confirm_dialog(self) -> None:
        """Draw a beautiful confirmation overlay dialog."""
        # 1. Full-screen dark semi-transparent overlay
        overlay = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # 2. Dialog box dimensions
        dialog_w = 400
        dialog_h = 180
        dialog_x = (self.screen.get_width() - dialog_w) // 2
        dialog_y = (self.screen.get_height() - dialog_h) // 2

        # 3. Draw dialog panel
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], dialog_rect, border_radius=12)
        pygame.draw.rect(
            self.screen, COLORS["grid_lines"], dialog_rect, 2, border_radius=12
        )

        # 4. Draw warning title / message
        if self.font and self.small_font:
            # Title
            title_text = self.font.render("防呆警告", True, COLORS["error"])
            self.screen.blit(title_text, (dialog_x + 30, dialog_y + 25))

            # Body text
            msg_text = self.small_font.render(
                "地圖有未儲存的變更，確定要退出嗎？", True, COLORS["text_main"]
            )
            self.screen.blit(msg_text, (dialog_x + 30, dialog_y + 65))

        # 5. Draw buttons
        self.confirm_yes_rect = pygame.Rect(dialog_x + 40, dialog_y + 110, 140, 36)
        self.confirm_no_rect = pygame.Rect(dialog_x + 220, dialog_y + 110, 140, 36)

        # Draw "Yes" Button
        pygame.draw.rect(
            self.screen, COLORS["error"], self.confirm_yes_rect, border_radius=6
        )
        # Draw "No" Button
        pygame.draw.rect(
            self.screen, COLORS["button_default"], self.confirm_no_rect, border_radius=6
        )

        # Draw button labels
        if self.font:
            yes_lbl = self.font.render("確定退出 (Y)", True, COLORS["background"])
            no_lbl = self.font.render("留在編輯 (N)", True, COLORS["text_main"])
            self.screen.blit(
                yes_lbl, yes_lbl.get_rect(center=self.confirm_yes_rect.center)
            )
            self.screen.blit(
                no_lbl, no_lbl.get_rect(center=self.confirm_no_rect.center)
            )

    def _check_confirm_click(self, pos: tuple[int, int]) -> bool:
        """Check clicks inside the confirmation dialog."""
        if not self.show_confirm_dialog:
            return False

        yes_rect = getattr(self, "confirm_yes_rect", None)
        no_rect = getattr(self, "confirm_no_rect", None)

        if yes_rect and yes_rect.collidepoint(pos):
            self.show_confirm_dialog = False
            if self.on_exit:
                self.on_exit()
            return True
        elif no_rect and no_rect.collidepoint(pos):
            self.show_confirm_dialog = False
            return True
        return False
