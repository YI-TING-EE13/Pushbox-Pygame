"""UI components for menus and buttons."""

import math
from typing import Callable, Optional

import pygame

from ..utils.constants import COLORS, ColorLike


class ModernButton:
    """A modern, clickable button with hover effects and rounded corners."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Optional[Callable[[], None]] = None,
        font: Optional[pygame.font.Font] = None,
        bg_color: ColorLike = COLORS["button_default"],
        hover_color: ColorLike = COLORS["button_hover"],
        text_color: ColorLike = COLORS["text_main"],
        icon: str = "",
    ) -> None:
        """Initialize button."""
        self.rect = pygame.Rect(x, y, width, height)
        self.original_y = y
        self.text = text
        self.callback = callback
        self.font = font

        # Colors
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.shadow_color: ColorLike = COLORS["button_shadow"]

        # State
        self.hovered = False
        self.pressed = False
        self.hover_anim = 0.0  # 0.0 to 1.0
        self.selected = False

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button."""
        # Animation logic
        target_anim = 1.0 if (self.hovered or self.selected) else 0.0
        self.hover_anim += (target_anim - self.hover_anim) * 0.2

        # Calculate visual position (lift up when hovered)
        offset_y = int(-2 * self.hover_anim)
        if self.pressed:
            offset_y = 2

        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(screen, self.shadow_color, shadow_rect, border_radius=8)

        # Draw main body
        body_rect = self.rect.copy()
        body_rect.y += offset_y

        color = self.hover_color if (self.hovered or self.selected) else self.bg_color
        pygame.draw.rect(screen, color, body_rect, border_radius=8)

        # Draw Border (subtle highlight)
        pygame.draw.rect(screen, (255, 255, 255, 30), body_rect, 1, border_radius=8)

        # Draw text
        if self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=body_rect.center)
            screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle event."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.pressed = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and event.button == 1:
                self.pressed = False
                if self.hovered and self.callback:
                    self.callback()
                return True

        return False


class InputBox:
    """Text input box for naming levels."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str = "",
        font: Optional[pygame.font.Font] = None,
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = COLORS["grid_lines"]
        self.color_active = COLORS["text_highlight"]
        self.color = self.color_inactive
        self.text = text
        self.font = font
        self.active = False
        self.txt_surface: Optional[pygame.Surface] = None
        self._render_text()

    def _render_text(self) -> None:
        if self.font:
            # Handle empty text prompt
            display_text = self.text if self.text else "請輸入名稱..."
            color = COLORS["text_main"] if self.text else COLORS["text_dim"]
            self.txt_surface = self.font.render(display_text, True, color)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.
        Returns: True if the input box processed the event (consumed it).
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                # Start text input support for IME (Chinese input)
                if self.active:
                    pygame.key.start_text_input()
            else:
                self.active = False
                pygame.key.stop_text_input()
            self.color = self.color_active if self.active else self.color_inactive
            return self.active

        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = self.color_inactive
                    pygame.key.stop_text_input()
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Fallback for simple ASCII if TEXTINPUT not triggered
                    pass
                self._render_text()
                return True  # Consume event

            elif event.type == pygame.TEXTINPUT:
                # Handle Unicode input (Traditional Chinese, etc.)
                if len(self.text) < 20:  # Limit length
                    self.text += event.text
                self._render_text()
                return True  # Consume event

        return False

    def draw(self, screen: pygame.Surface) -> None:
        # Draw background
        pygame.draw.rect(screen, COLORS["button_shadow"], self.rect, border_radius=5)

        # Blit the text
        if self.txt_surface:
            # Center vertically
            y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2
            # Clip text if too long
            area = pygame.Rect(
                0, 0, self.rect.width - 20, self.txt_surface.get_height()
            )
            screen.blit(self.txt_surface, (self.rect.x + 10, y), area)

        # Draw the rect (border)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=5)


class Menu:
    """Game menu screen."""

    def __init__(self, screen: pygame.Surface, title: str = "推箱子") -> None:
        self.screen = screen
        self.title = title
        self.buttons: list[ModernButton] = []
        self.font: Optional[pygame.font.Font] = None
        self.big_font: Optional[pygame.font.Font] = None
        self._init_fonts()
        self.time = 0.0

    def _init_fonts(self) -> None:
        try:
            self.font = pygame.font.SysFont("microsoftyahei", 24)
            self.big_font = pygame.font.SysFont("microsoftyahei", 64, bold=True)
        except (OSError, pygame.error):
            self.font = pygame.font.Font(None, 36)
            self.big_font = pygame.font.Font(None, 72)

    def add_button(
        self, text: str, callback: Callable[[], None], y_offset: int = 0
    ) -> ModernButton:
        button_width = 240
        button_height = 56
        x = (self.screen.get_width() - button_width) // 2
        y = self.screen.get_height() // 2 + y_offset

        button = ModernButton(
            x, y, button_width, button_height, text, callback, self.font
        )
        self.buttons.append(button)
        return button

    def handle_event(self, event: pygame.event.Event) -> bool:
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False

    def draw(
        self,
        level_names: Optional[list[str]] = None,
        current_level: Optional[str] = None,
    ) -> None:
        self.screen.fill(COLORS["background"])
        self.time += 0.05

        self._draw_grid_bg()

        # Recalculate center based on current screen size (for resizable window)
        center_x = self.screen.get_width() // 2

        if self.big_font:
            float_y = math.sin(self.time) * 5
            title_text = self.title

            title_shadow = self.big_font.render(
                title_text, True, COLORS["button_shadow"]
            )
            shadow_rect = title_shadow.get_rect(centerx=center_x, y=55 + float_y)
            self.screen.blit(title_shadow, shadow_rect)

            title_surface = self.big_font.render(title_text, True, COLORS["text_main"])
            title_rect = title_surface.get_rect(centerx=center_x, y=50 + float_y)
            self.screen.blit(title_surface, title_rect)

        if current_level and self.font:
            text = f"當前關卡: {current_level}"
            text_surf = self.font.render(text, True, COLORS["text_highlight"])
            pill_rect = text_surf.get_rect()
            pill_rect.inflate_ip(30, 10)
            pill_rect.centerx = center_x
            pill_rect.y = 130
            pygame.draw.rect(
                self.screen, COLORS["panel_bg"], pill_rect, border_radius=15
            )
            pygame.draw.rect(
                self.screen, COLORS["grid_lines"], pill_rect, 1, border_radius=15
            )
            text_rect = text_surf.get_rect(center=pill_rect.center)
            self.screen.blit(text_surf, text_rect)

        # Update button positions for resizable window
        for button in self.buttons:
            button.rect.centerx = center_x
            button.draw(self.screen)

    def _draw_grid_bg(self) -> None:
        width = self.screen.get_width()
        height = self.screen.get_height()
        spacing = 40
        color = COLORS["grid_lines"]
        for x in range(0, width, spacing):
            pygame.draw.line(self.screen, color, (x, 0), (x, height), 1)
        for y in range(0, height, spacing):
            pygame.draw.line(self.screen, color, (0, y), (width, y), 1)


class TutorialScreen:
    """Tutorial screen for new players."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self._init_fonts()
        self.time = 0.0

    def _init_fonts(self) -> None:
        try:
            self.font = pygame.font.SysFont("microsoftyahei", 22)
            self.title_font = pygame.font.SysFont("microsoftyahei", 36, bold=True)
        except (OSError, pygame.error):
            self.font = pygame.font.Font(None, 28)
            self.title_font = pygame.font.Font(None, 48)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            return True
        return False

    def draw(self) -> None:
        self.screen.fill(COLORS["background"])
        self.time += 0.05

        card_width = 600
        card_height = 500
        card_x = (self.screen.get_width() - card_width) // 2
        card_y = (self.screen.get_height() - card_height) // 2

        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)

        shadow_rect = card_rect.copy()
        shadow_rect.y += 10
        pygame.draw.rect(self.screen, (0, 0, 0, 50), shadow_rect, border_radius=12)

        pygame.draw.rect(self.screen, COLORS["panel_bg"], card_rect, border_radius=12)
        pygame.draw.rect(
            self.screen, COLORS["grid_lines"], card_rect, 1, border_radius=12
        )

        if self.title_font:
            title = self.title_font.render("遊戲教學", True, COLORS["text_highlight"])
            title_rect = title.get_rect(centerx=card_rect.centerx, y=card_rect.y + 30)
            self.screen.blit(title, title_rect)
            pygame.draw.line(
                self.screen,
                COLORS["grid_lines"],
                (card_rect.left + 50, title_rect.bottom + 10),
                (card_rect.right - 50, title_rect.bottom + 10),
                2,
            )

        sections = [
            (
                "🎯 遊戲目標",
                [
                    "將所有箱子推到目標點上",
                    "箱子只能推，不能拉",
                    "仔細規劃路線，避免卡住",
                ],
            ),
            (
                "🎮 控制方式",
                [
                    "方向鍵 或 WASD 移動",
                    "Z / Backspace 撤銷",
                    "Y / R 重做",
                    "F5 重置關卡",
                    "Ctrl+Q 退出遊戲",
                ],
            ),
            ("💡 提示", ["點擊下方按鈕也可操作", "按 H 隨時查看說明"]),
        ]

        y = card_rect.y + 100
        for section_title, items in sections:
            if self.font:
                t_surf = self.font.render(section_title, True, COLORS["text_main"])
                self.screen.blit(t_surf, (card_rect.left + 60, y))
                y += 30

                for item in items:
                    i_surf = self.font.render("• " + item, True, COLORS["text_dim"])
                    self.screen.blit(i_surf, (card_rect.left + 80, y))
                    y += 25
                y += 15

        if self.font:
            alpha = int((math.sin(self.time * 0.1) + 1) * 127.5)
            prompt = self.font.render(
                "按任意鍵開始遊戲...", True, COLORS["text_highlight"]
            )
            prompt.set_alpha(alpha)
            prompt_rect = prompt.get_rect(
                centerx=card_rect.centerx, bottom=card_rect.bottom - 30
            )
            self.screen.blit(prompt, prompt_rect)


class LevelSelector:
    """Level selection screen."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self._init_fonts()

        self.level_buttons: list[tuple[ModernButton, str, bool]] = []
        # Button, name, is_custom
        self.action_buttons: list[ModernButton] = []
        # Edit/delete buttons for custom levels
        self.back_button: Optional[ModernButton] = None

        self.on_back_cb: Optional[Callable[[], None]] = None

        self.on_select: Optional[Callable[[str], None]] = None
        self.on_edit: Optional[Callable[[str], None]] = None
        self.on_delete: Optional[Callable[[str], None]] = None

    def _init_fonts(self) -> None:
        try:
            self.font = pygame.font.SysFont("microsoftyahei", 20)
            self.small_font = pygame.font.SysFont("microsoftyahei", 14)
            self.title_font = pygame.font.SysFont("microsoftyahei", 36, bold=True)
        except (OSError, pygame.error):
            self.font = pygame.font.Font(None, 28)
            self.small_font = pygame.font.Font(None, 20)
            self.title_font = pygame.font.Font(None, 42)

    def setup(
        self,
        level_names: list[str],
        progress: dict,
        on_select: Callable[[str], None],
        on_back: Callable[[], None],
        on_edit: Callable[[str], None],
        on_delete: Callable[[str], None],
    ) -> None:
        self.level_buttons.clear()
        self.action_buttons.clear()

        self.on_select = on_select
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_back_cb = on_back  # Store callback to rebuild button on draw if needed

        # Initial layout setup
        self._layout_buttons(level_names, progress)

    def _layout_buttons(self, level_names: list[str], progress: dict) -> None:
        """Helper to layout buttons based on current screen size."""
        self.level_buttons.clear()
        self.action_buttons.clear()

        cols = 3
        button_width = 200
        button_height = 65
        spacing_x = 40
        spacing_y = 40

        start_x = (
            self.screen.get_width() - (cols * (button_width + spacing_x) - spacing_x)
        ) // 2
        start_y = 120

        for i, level_name in enumerate(level_names):
            col = i % cols
            row = i // cols

            x = start_x + col * (button_width + spacing_x)
            y = start_y + row * (button_height + spacing_y)

            is_custom = level_name.startswith("Custom") or level_name not in [
                "Level 1",
                "Level 2",
                "Level 3",
                "Level 4",
                "Level 5",
            ]

            level_prog = progress.get(level_name, {})
            bg_color = COLORS["button_default"]
            if level_prog.get("completed"):
                bg_color = (40, 60, 40)

            def handle_select(name: str = level_name) -> None:
                if self.on_select:
                    self.on_select(name)

            btn = ModernButton(
                x,
                y,
                button_width,
                button_height,
                level_name,
                handle_select,
                self.font,
                bg_color=bg_color,
            )
            self.level_buttons.append((btn, level_name, is_custom))

            if is_custom:

                def handle_edit(name: str = level_name) -> None:
                    if self.on_edit:
                        self.on_edit(name)

                edit_btn = ModernButton(
                    x,
                    y - 25,
                    60,
                    20,
                    "編輯",
                    handle_edit,
                    self.small_font,
                    bg_color=(50, 50, 150),
                )
                self.action_buttons.append(edit_btn)

                def handle_delete(name: str = level_name) -> None:
                    if self.on_delete:
                        self.on_delete(name)

                del_btn = ModernButton(
                    x + button_width - 60,
                    y - 25,
                    60,
                    20,
                    "刪除",
                    handle_delete,
                    self.small_font,
                    bg_color=(150, 50, 50),
                )
                self.action_buttons.append(del_btn)

        def handle_back() -> None:
            if self.on_back_cb:
                self.on_back_cb()

        self.back_button = ModernButton(
            (self.screen.get_width() - 140) // 2,
            self.screen.get_height() - 80,
            140,
            50,
            "返回",
            handle_back,
            self.font,
            bg_color=(60, 40, 40),
            hover_color=(80, 50, 50),
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        for button, _, _ in self.level_buttons:
            if button.handle_event(event):
                return True
        for button in self.action_buttons:
            if button.handle_event(event):
                return True
        if self.back_button and self.back_button.handle_event(event):
            return True
        return False

    def draw(self, progress: dict) -> None:
        self.screen.fill(COLORS["background"])

        # Simple relayout check - could be optimized
        # Re-layout on every draw is expensive, but okay for this simple menu
        # Ideally only on resize event.
        # For now, let's assume setup is called or we trust current layout.
        # But to support resizing, we need to re-center.
        # Let's just update the back button position at least.
        if self.back_button:
            self.back_button.rect.centerx = self.screen.get_width() // 2
            self.back_button.rect.bottom = self.screen.get_height() - 30

        if self.title_font:
            title = self.title_font.render("選擇關卡", True, COLORS["text_main"])
            title_rect = title.get_rect(centerx=self.screen.get_width() // 2, y=40)
            self.screen.blit(title, title_rect)

        for button, level_name, _ in self.level_buttons:
            button.draw(self.screen)

            level_progress = progress.get(level_name, {})
            if level_progress.get("completed") and self.small_font:
                best_moves = level_progress.get("best_moves", "-")
                info_text = f"★ 最佳: {best_moves} 步"
                info_surface = self.small_font.render(
                    info_text, True, COLORS["success"]
                )
                info_rect = info_surface.get_rect(
                    centerx=button.rect.centerx, bottom=button.rect.bottom - 10
                )
                self.screen.blit(info_surface, info_rect)

        for button in self.action_buttons:
            button.draw(self.screen)

        if self.back_button:
            self.back_button.draw(self.screen)
