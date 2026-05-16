#!/usr/bin/env python3
"""
PushBox - A modern Sokoban puzzle game
使用 Pygame 重新設計的推箱子遊戲

控制方式:
- 方向鍵 ↑↓←→ 或 WASD: 移動
- Z / Backspace: 撤銷
- Y / R: 重做
- F5 / Delete: 重置關卡
- Esc / P: 暫停
- M: 選單
- E: 編輯器
- H / F1: 說明
"""

import sys

import pygame

from src.pushbox.controllers.game_controller import GameController
from src.pushbox.utils.constants import COLORS
from src.pushbox.utils.constants import GameState as GameStateEnum
from src.pushbox.views.level_editor import LevelEditor
from src.pushbox.views.renderer import Renderer
from src.pushbox.views.ui_components import (
    LevelSelector,
    Menu,
    ModernButton,
    TutorialScreen,
)


class GameApp:
    """Main game application."""

    def __init__(self) -> None:
        """Initialize the game application."""
        pygame.init()
        pygame.display.set_caption("PushBox - 推箱子")

        # Create window (Resizable)
        self.width = 800
        self.height = 650
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE
        )
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Initialize game systems
        self.controller = GameController()
        self.renderer = Renderer(self.screen)

        # UI screens
        self.menu = Menu(self.screen, "PushBox")
        self.level_selector = LevelSelector(self.screen)
        self.tutorial = TutorialScreen(self.screen)
        self.editor: LevelEditor | None = None

        # In-Game UI Buttons
        self.game_buttons = []
        self._init_game_buttons()

        # Game state
        self.current_screen = "tutorial"  # tutorial, menu, game, level_select, editor
        self.show_help = False
        self.running = True
        self.control_feedback_timer = 0  # For showing control scheme change
        self.control_feedback_text = ""

        # Setup callbacks
        self._setup_callbacks()
        self._setup_menu()

    def _init_game_buttons(self) -> None:
        """Initialize in-game control buttons."""
        font = pygame.font.SysFont("microsoftyahei", 20)
        try:
            font = pygame.font.Font(None, 24)
        except (OSError, pygame.error):
            pass

        # Recalculate based on current dimensions
        btn_y = self.height - 50
        btn_w = 100
        btn_h = 36

        # Calculate positions to be centered
        total_w = btn_w * 3 + 40  # 20px spacing
        start_x = (self.width - total_w) // 2

        self.btn_undo = ModernButton(
            start_x,
            btn_y,
            btn_w,
            btn_h,
            "Undo (Z)",
            self.controller._on_undo,
            font,
            bg_color=COLORS["button_default"],
        )

        self.btn_reset = ModernButton(
            start_x + btn_w + 20,
            btn_y,
            btn_w,
            btn_h,
            "重置 (F5)",
            self.controller._on_reset,
            font,
            bg_color=COLORS["warning"],
            text_color=COLORS["background"],
        )

        self.btn_redo = ModernButton(
            start_x + (btn_w + 20) * 2,
            btn_y,
            btn_w,
            btn_h,
            "Redo (Y)",
            self.controller._on_redo,
            font,
            bg_color=COLORS["button_default"],
        )

        self.game_buttons = [self.btn_undo, self.btn_reset, self.btn_redo]

    def _setup_callbacks(self) -> None:
        """Setup game controller callbacks."""
        self.controller.register_callback("win", self._on_win)
        self.controller.register_callback("game_over", self._on_game_over)

    def _setup_menu(self) -> None:
        """Setup main menu."""
        self.menu.buttons.clear()
        self.menu.add_button("開始遊戲", self._start_game, -100)
        self.menu.add_button("選擇關卡", self._show_level_select, -30)
        self.menu.add_button("編輯器", lambda: self._show_editor(), 40)
        self.menu.add_button("切換控制", self._toggle_controls, 110)
        self.menu.add_button("教學說明", self._show_tutorial, 180)
        self.menu.add_button("退出", self._quit, 250)

    def _start_game(self) -> None:
        """Start the game with current level."""
        if not self.controller.get_current_level_name():
            levels = self.controller.get_available_levels()
            if levels:
                self.controller.load_level(levels[0])
        self.current_screen = "game"

    def _show_level_select(self) -> None:
        """Show level selection screen."""
        levels = self.controller.get_available_levels()
        progress = self.controller.save_manager.get_all_progress()

        self.level_selector.setup(
            levels,
            progress,
            self._on_level_selected,
            self._back_to_menu,
            self._on_edit_level,
            self._on_delete_level,
        )
        self.current_screen = "level_select"

    def _on_level_selected(self, level_name: str) -> None:
        """Handle level selection."""
        self.controller.load_level(level_name)
        self.current_screen = "game"

    def _on_edit_level(self, level_name: str) -> None:
        """Handle edit level request."""
        level = self.controller.level_manager.get_level(level_name)
        if level:
            self._show_editor(level)

    def _on_delete_level(self, level_name: str) -> None:
        """Handle delete level request."""
        success = self.controller.level_manager.delete_level(level_name)
        if success:
            self._show_level_select()
            self.control_feedback_text = f"已刪除: {level_name}"
            self.control_feedback_timer = 120

    def _show_editor(self, existing_level=None) -> None:
        """Show level editor."""
        self.editor = LevelEditor(self.screen, existing_level)
        self.editor.set_on_save(self._on_editor_save)
        self.editor.set_on_exit(self._back_to_menu)
        self.current_screen = "editor"

    def _on_editor_save(self, level) -> None:
        """Handle editor save."""
        self.controller.level_manager.save_level(level)
        self.control_feedback_text = f"關卡已儲存: {level.name}"
        self.control_feedback_timer = 180
        self._back_to_menu()

    def _toggle_controls(self) -> None:
        """Toggle control scheme with UI feedback."""
        scheme = self.controller.toggle_control_scheme()
        self.control_feedback_text = f"控制方式: {scheme}"
        self.control_feedback_timer = 120

    def _show_tutorial(self) -> None:
        """Show tutorial screen."""
        self.current_screen = "tutorial"

    def _back_to_menu(self) -> None:
        """Return to main menu."""
        self.current_screen = "menu"
        self.editor = None

    def _quit(self) -> None:
        """Quit the game."""
        self.running = False

    def _on_win(self, stats, is_record) -> None:
        """Handle win condition."""
        self.renderer.add_win_animation()

    def _on_game_over(self) -> None:
        """Handle game over condition."""
        pass

    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Handle Resize
            elif event.type == pygame.VIDEORESIZE:
                self.width = event.w
                self.height = event.h
                # In Pygame 2, set_mode again updates the window
                self.screen = pygame.display.set_mode(
                    (self.width, self.height), pygame.RESIZABLE
                )
                # Re-init UI elements that depend on screen size
                self._init_game_buttons()
                if self.editor:
                    self.editor._init_buttons()  # Re-layout editor buttons
                if self.current_screen == "level_select":
                    # Re-layout level selector
                    levels = self.controller.get_available_levels()
                    progress = self.controller.save_manager.get_all_progress()
                    self.level_selector.setup(
                        levels,
                        progress,
                        self._on_level_selected,
                        self._back_to_menu,
                        self._on_edit_level,
                        self._on_delete_level,
                    )

            # Global shortcuts
            if event.type == pygame.KEYDOWN:
                # If editing and typing, ignore global shortcuts
                if (
                    self.current_screen == "editor"
                    and self.editor
                    and self.editor.name_input.active
                ):
                    pass  # Don't trigger globals while typing
                else:
                    if event.key == pygame.K_F1 or event.key == pygame.K_h:
                        if self.current_screen == "game":
                            self.show_help = not self.show_help
                        continue
                    elif event.key == pygame.K_m:
                        if self.current_screen != "tutorial":
                            self._back_to_menu()
                        continue

            # Screen-specific event handling
            if self.current_screen == "tutorial":
                if self.tutorial.handle_event(event):
                    self.current_screen = "menu"

            elif self.current_screen == "menu":
                self.menu.handle_event(event)

            elif self.current_screen == "game":
                if (
                    self.controller.game_state
                    and self.controller.game_state.status == GameStateEnum.WON
                ):
                    self._handle_win_screen_input(event)
                elif (
                    self.controller.game_state
                    and self.controller.game_state.status == GameStateEnum.GAME_OVER
                ):
                    self._handle_game_over_input(event)
                else:
                    self.controller.handle_event(event)
                    # Handle ModernButtons
                    for btn in self.game_buttons:
                        if btn.handle_event(event):
                            break

            elif self.current_screen == "level_select":
                self.level_selector.handle_event(event)

            elif self.current_screen == "editor" and self.editor:
                self.editor.handle_event(event)

    def _handle_win_screen_input(self, event) -> None:
        """Handle input on win screen."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                # Next level logic
                levels = self.controller.get_available_levels()
                current = self.controller.get_current_level_name()

                next_level = None
                if current in levels:
                    idx = levels.index(current)
                    if idx + 1 < len(levels):
                        next_level = levels[idx + 1]

                if next_level:
                    self.controller.load_level(next_level)
                else:
                    # No next level (Game Completed)
                    self.control_feedback_text = "恭喜! 已完成所有關卡"
                    self.control_feedback_timer = 180
                    self._back_to_menu()

            elif event.key == pygame.K_r:
                self.controller._on_reset()
            elif event.key == pygame.K_m:
                self._back_to_menu()

    def _handle_game_over_input(self, event) -> None:
        """Handle input on game-over (deadlock) screen."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z or event.key == pygame.K_BACKSPACE:
                # Undo last move to recover from deadlock
                self.controller._on_undo()
            elif event.key == pygame.K_r or event.key == pygame.K_F5:
                self.controller._on_reset()
            elif event.key == pygame.K_m:
                self._back_to_menu()

    def update(self) -> None:
        """Update game state."""
        self.controller.update()
        self.renderer.update_animations()
        if self.control_feedback_timer > 0:
            self.control_feedback_timer -= 1

    def render(self) -> None:
        """Render current screen."""
        self.screen.fill(COLORS["background"])

        if self.current_screen == "tutorial":
            self.tutorial.draw()

        elif self.current_screen == "menu":
            current = self.controller.get_current_level_name() or "未選擇"
            self.menu.draw(self.controller.get_available_levels(), current)
            self._draw_feedback()

        elif self.current_screen == "game":
            self._render_game()

        elif self.current_screen == "level_select":
            progress = self.controller.save_manager.get_all_progress()
            self.level_selector.draw(progress)
            self._draw_feedback()

        elif self.current_screen == "editor" and self.editor:
            self.editor.draw()

        pygame.display.flip()

    def _draw_feedback(self) -> None:
        """Draw control scheme change feedback."""
        if self.control_feedback_timer > 0:
            alpha = min(255, self.control_feedback_timer * 5)
            font = pygame.font.SysFont("microsoftyahei", 24) or pygame.font.Font(
                None, 32
            )

            # Use text_highlight color for feedback
            text_surface = font.render(
                self.control_feedback_text, True, COLORS["text_main"]
            )

            bg_rect = text_surface.get_rect()
            bg_rect.inflate_ip(40, 20)
            bg_rect.centerx = self.width // 2
            bg_rect.bottom = self.height - 50

            # Semi-transparent panel
            surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                surf, (*COLORS["success"], alpha), surf.get_rect(), border_radius=10
            )

            text_rect = text_surface.get_rect(center=surf.get_rect().center)
            surf.blit(text_surface, text_rect)

            self.screen.blit(surf, bg_rect)

    def _render_game(self) -> None:
        """Render the game screen."""
        if self.controller.game_state:
            # Render game board
            # We want to keep the board above the controls
            self.renderer.render_game(self.controller.game_state, offset_y=60)
            self.renderer.render_ui(
                self.controller.game_state, show_help=self.show_help
            )

            if self.controller.game_state.status == GameStateEnum.WON:
                stats = self.controller.get_level_stats()
                current_level = self.controller.get_current_level_name()
                if current_level:
                    is_record = (
                        self.controller.save_manager.get_level_progress(
                            current_level
                        ).get("best_moves")
                        == stats["moves"]
                    )
                    self.renderer.render_win_screen(stats, is_record)
            elif self.controller.game_state.status == GameStateEnum.GAME_OVER:
                self.renderer.render_game_over_screen()
            else:
                # Draw ModernButtons
                for btn in self.game_buttons:
                    btn.draw(self.screen)

                # Current control scheme indicator
                font = pygame.font.SysFont("microsoftyahei", 16) or pygame.font.Font(
                    None, 20
                )
                scheme_text = f"控制: {self.controller.get_control_scheme()}"
                scheme_surface = font.render(scheme_text, True, COLORS["text_dim"])
                self.screen.blit(scheme_surface, (self.width - 120, 10))

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)

        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    app = GameApp()
    app.run()


if __name__ == "__main__":
    main()
