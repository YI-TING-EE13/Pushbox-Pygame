#!/usr/bin/env python3
"""
Pushbox-Pygame - A modern Sokoban puzzle game
使用 Pygame 重新設計的推箱子遊戲

控制方式:
- 方向鍵 ↑↓←→ 或 WASD: 移動
- Z / Backspace: 撤銷 (Undo)
- Y / R: 重做 (Redo)
- F5 / Delete: 重置關卡 (Reset)
- M: 返回選單
- H / F1: 遊戲說明 (Help)
"""

import sys
from typing import Any

import pygame

from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.solver import SolverStatus, solve
from src.pushbox.utils.constants import COLORS
from src.pushbox.utils.constants import GameState as GameStateEnum
from src.pushbox.views.level_editor import LevelEditor
from src.pushbox.views.renderer import Renderer
from src.pushbox.views.ui_components import (
    LevelSelector,
    Menu,
    ModernButton,
    SettingsScreen,
    TutorialScreen,
)


class GameApp:
    """Main game application."""

    def __init__(self) -> None:
        """Initialize the game application."""
        # Initialize game systems
        self.controller = GameController()

        # Load window dimensions from config
        self.width = self.controller.config.get("window_width", 1024)
        self.height = self.controller.config.get("window_height", 768)
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Pushbox-Pygame - 推箱子")
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.renderer = Renderer(self.screen)

        # UI screens
        self.menu = Menu(self.screen, "PushBox")
        self.level_selector = LevelSelector(self.screen, self.controller.level_manager)
        self.tutorial = TutorialScreen(self.screen)
        self.settings = SettingsScreen(
            self.screen, self.controller.config, self.controller.save_manager
        )
        self.editor: LevelEditor | None = None

        # In-Game UI Buttons
        self.game_buttons = []
        self._init_game_buttons()

        # Game state
        if self.controller.config.get_bool("show_tutorial", True):
            self.current_screen = "game"
            self.controller.load_level("Level 0")
        else:
            self.current_screen = "menu"
        self.show_help = False
        self.running = True
        self.control_feedback_timer = 0  # For showing control scheme change
        self.control_feedback_text = ""
        self.menu_selected_index = 0

        # Transition state
        self.transition_alpha = 0
        self.transition_target = None
        self.transition_speed = 15  # Alpha speed per frame
        self.transition_state = "none"  # "none", "fade_out", "fade_in"

        # Setup callbacks
        self._setup_callbacks()
        self._setup_menu()

        # Attract Mode Background State
        self.attract_game_state = None
        self.attract_path = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 1), (-1, 0), (-1, 0)]
        self.attract_index = 0
        self.attract_timer = 0.0
        self.attract_reset_timer = 0.0

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

        # Calculate positions to be centered (4 buttons with 20px spacing)
        total_w = btn_w * 4 + 60
        start_x = (self.width - total_w) // 2

        self.btn_undo = ModernButton(
            start_x,
            btn_y,
            btn_w,
            btn_h,
            "撤銷 (Z)",
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
            "重做 (Y)",
            self.controller._on_redo,
            font,
            bg_color=COLORS["button_default"],
        )

        self.btn_hint = ModernButton(
            start_x + (btn_w + 20) * 3,
            btn_y,
            btn_w,
            btn_h,
            "💡 提示 (I)",
            self._trigger_hint,
            font,
            bg_color=COLORS["button_default"],
        )

        self.game_buttons = [
            self.btn_undo,
            self.btn_reset,
            self.btn_redo,
            self.btn_hint,
        ]

    def _setup_callbacks(self) -> None:
        """Setup game controller callbacks."""
        self.controller.register_callback("win", self._on_win)
        self.controller.register_callback("game_over", self._on_game_over)
        self.controller.register_callback("invalid_move", self._on_invalid_move)
        self.controller.register_callback("box_on_target", self._on_box_on_target)
        self.controller.register_callback("undo", self._on_undo)
        self.controller.register_callback("redo", self._on_redo)
        self.settings.set_on_back(self._back_to_menu)

        # Register hint input and state clearing callbacks
        self.controller.input_handler.register_callback("hint", self._trigger_hint)
        self.controller.register_callback("move", self._clear_hint)
        self.controller.register_callback("undo", self._clear_hint)
        self.controller.register_callback("redo", self._clear_hint)
        self.controller.register_callback("reset", self._clear_hint)

    def _clear_hint(self, *args: Any, **kwargs: Any) -> None:
        """Clear active solver hint path and message from renderer."""
        self.renderer.hint_path = []
        self.renderer.hint_message = None
        self.renderer.hint_end_time = 0

    def _trigger_hint(self) -> None:
        """Trigger BFS path solver for the current level state and cache results."""
        # 1. Overlay state checks (Do not trigger hint if win,
        # deadlock, pause, or help is open)
        if self.current_screen != "game" or self.show_help or self.controller.is_paused:
            return

        if not self.controller.game_state:
            return

        if self.controller.game_state.status != GameStateEnum.PLAYING:
            return

        # 2. Block hint in onboarding Level 0 to prevent UX confusion
        if self.controller.get_current_level_name() == "Level 0":
            return

        # Run the BFS path solver on the current level representation
        res = solve(self.controller.current_level)

        # Set 1.5 seconds visibility ticks in Pygame Renderer
        current_ticks = pygame.time.get_ticks()
        self.renderer.hint_end_time = current_ticks + 1500

        if res.status == SolverStatus.SOLVED:
            if res.path:
                self.renderer.hint_path = res.path[:3]
                self.renderer.hint_message = "提示：請沿著高亮方向移動"
            else:
                self.renderer.hint_path = []
                self.renderer.hint_message = "目前已在完成狀態"
        elif res.status == SolverStatus.NODE_LIMIT_EXCEEDED:
            self.renderer.hint_path = []
            self.renderer.hint_message = "此局面較複雜，暫時找不到可靠提示。"
        elif res.status == SolverStatus.UNSOLVED:
            self.renderer.hint_path = []
            self.renderer.hint_message = (
                "目前局面可能無法完成，建議按 Z 撤銷或 F5 重置。"
            )
        elif res.status == SolverStatus.INVALID_LEVEL:
            self.renderer.hint_path = []
            self.renderer.hint_message = "目前關卡資料無法產生提示。"

    def _setup_menu(self) -> None:
        """Setup main menu."""
        self.menu.buttons.clear()
        self.menu.add_button("開始遊戲", self._start_game, -120)
        self.menu.add_button("選擇關卡", self._show_level_select, -60)
        self.menu.add_button("編輯器", lambda: self._show_editor(), 0)
        self.menu.add_button("教學說明", self._show_tutorial, 60)
        self.menu.add_button("設定", self._show_settings, 120)
        self.menu.add_button("退出", self._quit, 180)

    def _start_transition(self, target_screen: str) -> None:
        """Start a screen fade transition."""
        if target_screen == self.current_screen:
            return
        self.transition_target = target_screen
        self.transition_state = "fade_out"
        self.transition_alpha = 0

    def _show_settings(self) -> None:
        """Show settings screen."""
        self._start_transition("settings")

    def _start_game(self) -> None:
        """Start the game with current level."""
        current = self.controller.get_current_level_name()
        if not current or current == "Level 0":
            levels = self.controller.get_available_levels()
            if levels:
                self.controller.load_level(levels[0])
        self._start_transition("game")

    def _show_level_select(self) -> None:
        """Show level selection screen."""
        self._start_transition("level_select")

    def _on_level_selected(self, level_name: str) -> None:
        """Handle level selection."""
        self.controller.load_level(level_name)
        self._start_transition("game")

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
        self.editor.set_on_playtest(self._on_editor_playtest)
        self._start_transition("editor")

    def _on_editor_save(self, level) -> None:
        """Handle editor save."""
        self.controller.level_manager.save_level(level)
        self.control_feedback_text = f"關卡已儲存: {level.name}"
        self.control_feedback_timer = 180
        self._back_to_menu()

    def _on_editor_playtest(self, level) -> None:
        """Start playtesting a level from editor."""
        self.controller.load_level_instance(level, is_playtest=True)
        self._start_transition("game")

    def _back_to_editor(self) -> None:
        """Return to level editor from playtest."""
        self._start_transition("editor")

    def _on_invalid_move(self) -> None:
        """Handle invalid move (hit wall or push multiple boxes) for screen shake."""
        self.renderer.trigger_screen_shake()

    def _toggle_controls(self) -> None:
        """Toggle control scheme with UI feedback."""
        scheme = self.controller.toggle_control_scheme()
        self.control_feedback_text = f"控制方式: {scheme}"
        self.control_feedback_timer = 120

    def _show_tutorial(self) -> None:
        """Show tutorial screen."""
        self._start_transition("tutorial")

    def _back_to_menu(self) -> None:
        """Return to main menu."""
        self._start_transition("menu")

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

            # Global Ctrl+Q Quit shortcut
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_q
                and (getattr(event, "mod", 0) & pygame.KMOD_CTRL)
            ):
                self.running = False
                return

            # Handle Resize
            elif event.type == pygame.VIDEORESIZE:
                self.width = event.w
                self.height = event.h
                self.controller.config.set("window_width", self.width)
                self.controller.config.set("window_height", self.height)
                # In Pygame 2, set_mode again updates the window
                self.screen = pygame.display.set_mode(
                    (self.width, self.height), pygame.RESIZABLE
                )
                # Re-init UI elements that depend on screen size
                self._init_game_buttons()
                if self.editor:
                    self.editor._init_buttons()  # Re-layout editor buttons
                if self.current_screen == "menu":
                    self._setup_menu()
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
                # Help overlay dismissal on any keypress (only KEYDOWN)
                if self.current_screen == "game" and self.show_help:
                    self.show_help = False
                    continue

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
                            if not self.controller.is_paused:
                                self.show_help = not self.show_help
                        continue
                    elif event.key == pygame.K_m:
                        if self.current_screen != "tutorial":
                            self._back_to_menu()
                        continue
                    elif event.key == pygame.K_ESCAPE:
                        if self.current_screen == "game" and self.show_help:
                            self.show_help = False
                            continue

            # Screen-specific event handling
            if self.current_screen == "tutorial":
                if self.tutorial.handle_event(event):
                    self.controller.config.set("show_tutorial", False)
                    self.current_screen = "menu"

            elif self.current_screen == "settings":
                self.settings.handle_event(event)

            elif self.current_screen == "menu":
                if event.type == pygame.KEYDOWN:
                    if self.menu.buttons:
                        if event.key in [pygame.K_UP, pygame.K_w]:
                            self.menu_selected_index = (
                                self.menu_selected_index - 1
                            ) % len(self.menu.buttons)
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            self.menu_selected_index = (
                                self.menu_selected_index + 1
                            ) % len(self.menu.buttons)
                        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                            if 0 <= self.menu_selected_index < len(self.menu.buttons):
                                button = self.menu.buttons[self.menu_selected_index]
                                if button.callback:
                                    button.callback()
                elif event.type == pygame.MOUSEMOTION:
                    for idx, button in enumerate(self.menu.buttons):
                        if button.rect.collidepoint(event.pos):
                            self.menu_selected_index = idx
                self.menu.handle_event(event)

            elif self.current_screen == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.controller.is_playtest:
                        self._back_to_editor()
                        continue
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
                elif self.controller.is_paused:
                    self._handle_pause_screen_input(event)
                else:
                    if self.show_help:
                        pass
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
                if self.controller.is_playtest:
                    self._back_to_editor()
                else:
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
            elif event.key in [pygame.K_m, pygame.K_ESCAPE]:
                if self.controller.is_playtest:
                    self._back_to_editor()
                else:
                    self._back_to_menu()

    def _handle_game_over_input(self, event) -> None:
        """Handle input on game-over (deadlock) screen."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z or event.key == pygame.K_BACKSPACE:
                # Undo last move to recover from deadlock
                self.controller._on_undo()
            elif event.key == pygame.K_r or event.key == pygame.K_F5:
                self.controller._on_reset()
            elif event.key in [pygame.K_m, pygame.K_ESCAPE]:
                if self.controller.is_playtest:
                    self._back_to_editor()
                else:
                    self._back_to_menu()

    def _handle_pause_screen_input(self, event) -> None:
        """Handle input when the game is paused."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_p]:
                if self.controller.is_playtest:
                    self._back_to_editor()
                else:
                    self.controller.toggle_pause()
            elif event.key == pygame.K_r:
                self.controller.toggle_pause()  # Unpause first
                self.controller._on_reset()  # Reset level
            elif event.key == pygame.K_s:
                self.controller.toggle_pause()  # Unpause first
                self._show_settings()
            elif event.key == pygame.K_m:
                if self.controller.is_playtest:
                    self._back_to_editor()
                else:
                    self._back_to_menu()

    def update(self) -> None:
        """Update game state."""
        self.controller.update()
        self.renderer.update_animations()
        if self.control_feedback_timer > 0:
            self.control_feedback_timer -= 1

        # Check Level 0 completion direct-exit flow
        if (
            self.current_screen == "game"
            and self.controller.get_current_level_name() == "Level 0"
            and self.controller.game_state
            and self.controller.game_state.status == GameStateEnum.WON
            and self.transition_state == "none"
        ):
            self.controller.config.set("show_tutorial", False)
            self._back_to_menu()
            return

        # Attract Mode Background Update
        if self.current_screen == "menu":
            self._update_attract_mode()

        # Update screen transitions
        if self.transition_state == "fade_out":
            self.transition_alpha += self.transition_speed
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                # Perform actual screen switch
                self.current_screen = self.transition_target
                # Reset editor or pauses if returning to menu
                if self.transition_target == "menu":
                    self.editor = None
                    self.controller.is_paused = False
                    self.controller.input_handler.clear_input_state()
                    self.menu_selected_index = 0
                elif self.transition_target == "editor":
                    self.controller.is_playtest = False
                    self.controller.game_state = None
                elif self.transition_target == "level_select":
                    # setup level selector when transition finishes
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

                self.transition_state = "fade_in"
        elif self.transition_state == "fade_in":
            self.transition_alpha -= self.transition_speed
            if self.transition_alpha <= 0:
                self.transition_alpha = 0
                self.transition_state = "none"
                self.transition_target = None

    def render(self) -> None:
        """Render current screen."""
        self.screen.fill(COLORS["background"])

        if self.current_screen == "tutorial":
            self.tutorial.draw()

        elif self.current_screen == "menu":
            for idx, button in enumerate(self.menu.buttons):
                button.selected = idx == self.menu_selected_index
            current = self.controller.get_current_level_name() or "未選擇"
            progress = self.controller.save_manager.get_all_progress()
            self.menu.draw(
                self.controller.get_available_levels(),
                current,
                progress,
                draw_bg_callback=self._draw_attract_bg,
            )
            self._draw_feedback()

        elif self.current_screen == "settings":
            self.settings.draw()
            self._draw_feedback()

        elif self.current_screen == "game":
            self._render_game()

        elif self.current_screen == "level_select":
            progress = self.controller.save_manager.get_all_progress()
            self.level_selector.draw(progress)
            self._draw_feedback()

        elif self.current_screen == "editor" and self.editor:
            self.editor.draw()

        # Draw transition overlay
        if self.transition_state != "none" and self.transition_alpha > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            bg_col = COLORS["background"]
            overlay.fill((bg_col[0], bg_col[1], bg_col[2], self.transition_alpha))
            self.screen.blit(overlay, (0, 0))

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

    def _on_box_on_target(self, pos: tuple[int, int]) -> None:
        """Handle box pushed onto target event for particle burst."""
        from src.pushbox.views.renderer import TargetSparkAnimation

        self.renderer.add_animation(
            TargetSparkAnimation(pos, pygame.time.get_ticks() / 1000.0)
        )

    def _on_undo(self, command: Any) -> None:
        """Handle undo event to trigger smooth slide backward animations."""
        if self.controller.config.is_animation_enabled():
            from src.pushbox.utils.constants import CellType

            # Player slides backward: player_to -> player_from
            self.renderer.add_move_animation(
                command.player_to,
                command.player_from,
                CellType.PLAYER,
                duration=0.10,  # 100ms
            )
            # Box slides backward if it was pushed: box_to -> box_from
            if command.is_push() and command.box_to and command.box_from:
                lvl = self.controller.current_level
                is_on_target = (
                    lvl
                    and lvl.initial_grid[command.box_from[0], command.box_from[1]]
                    == CellType.TARGET
                )
                cell_type = CellType.BOX_ON_TARGET if is_on_target else CellType.BOX
                self.renderer.add_move_animation(
                    command.box_to,
                    command.box_from,
                    cell_type,
                    duration=0.10,
                )

    def _on_redo(self, command: Any) -> None:
        """Handle redo event to trigger smooth slide forward animations."""
        if self.controller.config.is_animation_enabled():
            from src.pushbox.utils.constants import CellType

            # Player slides forward: player_from -> player_to
            self.renderer.add_move_animation(
                command.player_from,
                command.player_to,
                CellType.PLAYER,
                duration=0.10,  # 100ms
            )
            # Box slides forward if it was pushed: box_from -> box_to
            if command.is_push() and command.box_from and command.box_to:
                lvl = self.controller.current_level
                is_on_target = (
                    lvl
                    and lvl.initial_grid[command.box_to[0], command.box_to[1]]
                    == CellType.TARGET
                )
                cell_type = CellType.BOX_ON_TARGET if is_on_target else CellType.BOX
                self.renderer.add_move_animation(
                    command.box_from,
                    command.box_to,
                    cell_type,
                    duration=0.10,
                )

    def _update_attract_mode(self) -> None:
        """Update the background attract mode demo solver."""
        if self.attract_game_state is None:
            level = self.controller.level_manager.get_level("Level 1")
            if level:
                level.reset()
                from copy import deepcopy

                from src.pushbox.models.game_state import GameState

                self.attract_game_state = GameState(deepcopy(level))
                self.attract_index = 0
                self.attract_timer = 0.0
                self.attract_reset_timer = 0.0
            else:
                return

        # Frame delta time (approx 1/60s per frame)
        dt = 1.0 / self.fps

        if self.attract_reset_timer > 0:
            self.attract_reset_timer -= dt
            if self.attract_reset_timer <= 0:
                self.attract_game_state = None  # Force reload next frame
        else:
            self.attract_timer += dt
            if self.attract_timer >= 1.2:
                self.attract_timer = 0.0
                if self.attract_index < len(self.attract_path):
                    direction = self.attract_path[self.attract_index]

                    # Check if pushing a box to a target for particle spawning
                    pr, pc = self.attract_game_state.level.get_player_position() or (
                        0,
                        0,
                    )
                    dr, dc = direction
                    box_pos = (pr + dr, pc + dc)
                    box_dest = (pr + 2 * dr, pc + 2 * dc)

                    is_push = self.attract_game_state.level.get_cell(
                        box_pos[0], box_pos[1]
                    ) in [3, 5]
                    is_target = (
                        self.attract_game_state.level.get_cell(box_dest[0], box_dest[1])
                        == 2
                    )

                    success = self.attract_game_state.move(direction)

                    if success and is_push and is_target:
                        from src.pushbox.views.renderer import TargetSparkAnimation

                        self.renderer.add_animation(
                            TargetSparkAnimation(
                                box_dest, pygame.time.get_ticks() / 1000.0
                            )
                        )

                    self.attract_index += 1

                    from src.pushbox.utils.constants import GameState as GameStateEnum

                    if (
                        self.attract_game_state.status == GameStateEnum.WON
                        or self.attract_index >= len(self.attract_path)
                    ):
                        self.attract_reset_timer = 3.0
                else:
                    self.attract_reset_timer = 3.0

    def _draw_attract_bg(self) -> None:
        """Render the attract mode background board translucently."""
        if self.attract_game_state is None:
            return

        attract_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        attract_surf.fill((0, 0, 0, 0))

        orig_screen = self.renderer.screen
        self.renderer.screen = attract_surf

        # Render board center offset
        self.renderer.render_game(self.attract_game_state, offset_y=60)

        self.renderer.screen = orig_screen
        attract_surf.set_alpha(38)
        self.screen.blit(attract_surf, (0, 0))

    def _render_game(self) -> None:
        """Render the game screen."""
        if self.controller.game_state:
            # Render game board
            # We want to keep the board above the controls
            self.renderer.render_game(self.controller.game_state, offset_y=60)
            self.renderer.render_ui(
                self.controller.game_state,
                show_help=self.show_help,
                control_scheme=self.controller.get_control_scheme(),
            )

            if self.controller.game_state.status == GameStateEnum.WON:
                stats = self.controller.get_level_stats()
                current_level = self.controller.get_current_level_name()
                if current_level:
                    best_moves = self.controller.save_manager.get_level_progress(
                        current_level
                    ).get("best_moves")
                    is_record = best_moves == stats["moves"]
                    self.renderer.render_win_screen(stats, is_record, best_moves)
            elif self.controller.game_state.status == GameStateEnum.GAME_OVER:
                self.renderer.render_game_over_screen()
            elif self.controller.is_paused:
                self.renderer.render_pause_screen()
            else:
                # Draw ModernButtons
                for btn in self.game_buttons:
                    if (
                        self.controller.get_current_level_name() == "Level 0"
                        and btn == self.btn_hint
                    ):
                        continue
                    btn.draw(self.screen)

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
