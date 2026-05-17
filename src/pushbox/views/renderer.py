"""Game renderer using pygame."""

import os
from typing import Any, Optional

import pygame

from ..models.game_state import GameState
from ..utils.constants import CELL_SIZE, COLORS, CellType, ColorLike


class Animation:
    """Base class for animations."""

    def __init__(self, duration: float, start_time: float) -> None:
        self.duration = duration
        self.start_time = start_time
        self.finished = False

    def update(self, current_time: float) -> None:
        if current_time - self.start_time >= self.duration:
            self.finished = True

    def get_progress(self, current_time: float) -> float:
        elapsed = current_time - self.start_time
        return min(1.0, elapsed / self.duration) if self.duration > 0 else 1.0

    def render(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        pass


class MoveAnimation(Animation):
    """Animation for player/box movement."""

    def __init__(
        self,
        from_pos: tuple[int, int],
        to_pos: tuple[int, int],
        cell_type: int,
        duration: float,
        start_time: float,
    ) -> None:
        super().__init__(duration, start_time)
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.cell_type = cell_type

    def render(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        current_time = pygame.time.get_ticks() / 1000.0
        progress = self.get_progress(current_time)

        # Easing function (Ease Out Cubic)
        t = progress - 1
        ease_progress = t * t * t + 1

        fr, fc = self.from_pos
        tr, tc = self.to_pos

        current_r = fr + (tr - fr) * ease_progress
        current_c = fc + (tc - fc) * ease_progress

        x = offset_x + int(current_c * CELL_SIZE)
        y = offset_y + int(current_r * CELL_SIZE)

        if self.cell_type == CellType.PLAYER:
            Renderer.draw_player(screen, x, y)
        elif self.cell_type in [CellType.BOX, CellType.BOX_ON_TARGET]:
            Renderer.draw_box(
                screen, x, y, on_target=(self.cell_type == CellType.BOX_ON_TARGET)
            )


class WinAnimation(Animation):
    """Victory celebration animation."""

    def __init__(self, start_time: float) -> None:
        super().__init__(3.0, start_time)
        self.particles: list[dict[str, Any]] = []
        self._init_particles()

    def _init_particles(self) -> None:
        import random

        colors = [COLORS["success"], COLORS["warning"], COLORS["target"]]
        for _ in range(100):
            self.particles.append(
                {
                    "x": random.randint(0, 800),
                    "y": random.randint(0, 600),
                    "vx": random.uniform(-4, 4),
                    "vy": random.uniform(-8, -2),
                    "color": random.choice(colors),
                    "size": random.randint(3, 8),
                    "life": 1.0,
                    "decay": random.uniform(0.005, 0.02),
                }
            )

    def update(self, current_time: float) -> None:
        super().update(current_time)
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.2  # Gravity
            p["life"] -= p["decay"]

    def render(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        for p in self.particles:
            if p["life"] > 0:
                # Fade out
                color = list(p["color"])
                if len(color) == 3:
                    color.append(255)
                color[3] = int(255 * p["life"])

                surf = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (p["size"], p["size"]), p["size"])
                screen.blit(surf, (int(p["x"]), int(p["y"])))


class Renderer:
    """Main game renderer."""

    PLAYER_IMAGE: Optional[pygame.Surface] = None

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font: Optional[pygame.font.Font] = None
        self.big_font: Optional[pygame.font.Font] = None
        self._init_fonts()

        self.animations: list[Animation] = []
        self.animation_enabled = True

        if Renderer.PLAYER_IMAGE is None:
            self._load_resources()

    def _load_resources(self) -> None:
        """Load game assets."""
        try:
            # Use absolute path relative to this file location or project root
            # Assuming src/pushbox/assets/images/player.jpeg structure
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            img_path = os.path.join(base_path, "assets", "images", "player.jpeg")

            if os.path.exists(img_path):
                img = pygame.image.load(img_path)
                # Scale image to be slightly smaller than cell size
                target_size = int(CELL_SIZE * 0.8)
                Renderer.PLAYER_IMAGE = pygame.transform.scale(
                    img, (target_size, target_size)
                )
                # Optional: Make white background transparent if needed, or use colorkey
                # Renderer.PLAYER_IMAGE.set_colorkey((255, 255, 255))
            else:
                print(f"Player image not found at: {img_path}")
        except Exception as e:
            print(f"Failed to load player image: {e}")

    def _init_fonts(self) -> None:
        try:
            self.font = pygame.font.SysFont("microsoftyahei", 20)
            self.big_font = pygame.font.SysFont("microsoftyahei", 48, bold=True)
        except (OSError, pygame.error):
            self.font = pygame.font.Font(None, 24)
            self.big_font = pygame.font.Font(None, 64)

    def set_animation_enabled(self, enabled: bool) -> None:
        self.animation_enabled = enabled

    def add_animation(self, animation: Animation) -> None:
        if self.animation_enabled:
            self.animations.append(animation)

    def add_move_animation(
        self,
        from_pos: tuple[int, int],
        to_pos: tuple[int, int],
        cell_type: int,
        duration: float = 0.15,
    ) -> None:
        if self.animation_enabled:
            anim = MoveAnimation(
                from_pos, to_pos, cell_type, duration, pygame.time.get_ticks() / 1000.0
            )
            self.add_animation(anim)

    def add_win_animation(self) -> None:
        if self.animation_enabled:
            anim = WinAnimation(pygame.time.get_ticks() / 1000.0)
            self.add_animation(anim)

    def update_animations(self) -> None:
        current_time = pygame.time.get_ticks() / 1000.0
        for anim in self.animations[:]:
            anim.update(current_time)
            if anim.finished:
                self.animations.remove(anim)

    def render_game(
        self, game_state: GameState, offset_x: int = 0, offset_y: int = 0
    ) -> None:
        level = game_state.level

        # Draw background pattern first
        self.screen.fill(COLORS["background"])

        # Calculate board dimensions and centering based on current screen size
        board_width = level.cols * CELL_SIZE
        board_height = level.rows * CELL_SIZE

        if offset_x == 0:
            offset_x = (self.screen.get_width() - board_width) // 2
        if offset_y == 0:
            offset_y = (self.screen.get_height() - board_height) // 2

        # Draw Board Shadow/Border
        bg_rect = pygame.Rect(
            offset_x - 10, offset_y - 10, board_width + 20, board_height + 20
        )
        pygame.draw.rect(self.screen, COLORS["panel_bg"], bg_rect, border_radius=10)
        pygame.draw.rect(
            self.screen, COLORS["grid_lines"], bg_rect, 2, border_radius=10
        )

        # Draw Static Grid Elements (Floor, Walls, Targets)
        # We draw static boxes/players only if they are NOT being animated
        animating_cells = set()
        for anim in self.animations:
            if isinstance(anim, MoveAnimation):
                animating_cells.add(anim.to_pos)  # Don't draw at destination yet

        for row in range(level.rows):
            for col in range(level.cols):
                x = offset_x + col * CELL_SIZE
                y = offset_y + row * CELL_SIZE

                cell = level.get_cell(row, col)
                initial_cell = level.initial_grid[row, col]

                # 1. Always draw floor
                self._draw_floor(x, y, (row + col) % 2 == 0)

                # 2. Draw Target
                if initial_cell == CellType.TARGET:
                    self._draw_target(x, y)
                elif cell == CellType.TARGET:  # In case level modified
                    self._draw_target(x, y)

                # 3. Draw Objects (if not animating)
                if (row, col) not in animating_cells:
                    if cell == CellType.WALL:
                        self._draw_wall(x, y)
                    elif cell == CellType.BOX:
                        Renderer.draw_box(self.screen, x, y, False)
                    elif cell == CellType.BOX_ON_TARGET:
                        Renderer.draw_box(self.screen, x, y, True)
                    elif cell == CellType.PLAYER:
                        Renderer.draw_player(self.screen, x, y)

        # Draw Animations on top
        for anim in self.animations:
            anim.render(self.screen, offset_x, offset_y)

    def _draw_floor(self, x: int, y: int, is_light: bool) -> None:
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        color = COLORS["floor_light"] if is_light else COLORS["floor"]
        pygame.draw.rect(self.screen, color, rect)

    def _draw_wall(self, x: int, y: int) -> None:
        # Pseudo 3D Wall
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

        # Shadow/Side (Darker)
        pygame.draw.rect(
            self.screen, COLORS["wall_shadow"], rect.move(0, 4), border_radius=4
        )

        # Top Face (Lighter)
        top_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE - 4)
        pygame.draw.rect(self.screen, COLORS["wall"], top_rect, border_radius=4)

        # Highlight (Top Edge)
        pygame.draw.line(
            self.screen,
            (255, 255, 255, 50),
            (x + 2, y + 2),
            (x + CELL_SIZE - 2, y + 2),
            2,
        )

    def _draw_target(self, x: int, y: int) -> None:
        center_x = x + CELL_SIZE // 2
        center_y = y + CELL_SIZE // 2
        radius = CELL_SIZE // 4

        # Glow
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(
            surf, (*COLORS["target"], 50), (CELL_SIZE // 2, CELL_SIZE // 2), radius + 4
        )
        self.screen.blit(surf, (x, y))

        # Dot
        pygame.draw.circle(self.screen, COLORS["target"], (center_x, center_y), radius)
        pygame.draw.circle(
            self.screen, COLORS["target_glow"], (center_x, center_y), radius - 2
        )

    @staticmethod
    def draw_box(
        screen: pygame.Surface, x: int, y: int, on_target: bool = False
    ) -> None:
        # Pseudo 3D Box
        margin = 4
        size = CELL_SIZE - margin * 2
        rect = pygame.Rect(x + margin, y + margin, size, size)

        base_color = COLORS["box_on_target"] if on_target else COLORS["box"]
        shadow_color = (
            COLORS["box_on_target_shadow"] if on_target else COLORS["box_shadow"]
        )

        # Shadow/Side
        pygame.draw.rect(screen, shadow_color, rect.move(0, 4), border_radius=6)

        # Top Face
        top_rect = pygame.Rect(x + margin, y + margin, size, size - 4)
        pygame.draw.rect(screen, base_color, top_rect, border_radius=6)

        # Decoration (Inner square)
        inner_margin = 8
        inner_rect = top_rect.inflate(-inner_margin * 2, -inner_margin * 2)
        pygame.draw.rect(screen, shadow_color, inner_rect, 2, border_radius=4)

        # Highlight
        if on_target:
            pygame.draw.rect(screen, (255, 255, 255, 100), top_rect, 2, border_radius=6)

    @staticmethod
    def draw_player(screen: pygame.Surface, x: int, y: int) -> None:
        center_x = x + CELL_SIZE // 2
        center_y = y + CELL_SIZE // 2

        if Renderer.PLAYER_IMAGE:
            rect = Renderer.PLAYER_IMAGE.get_rect(center=(center_x, center_y))
            # Draw shadow
            pygame.draw.circle(
                screen,
                COLORS["player_shadow"],
                (center_x, center_y + 3),
                rect.width // 2,
            )
            screen.blit(Renderer.PLAYER_IMAGE, rect)
        else:
            # Fallback: Cuter Player Design (Bear-ish)
            radius = int(CELL_SIZE * 0.35)

            # Ears
            ear_radius = int(radius * 0.4)
            ear_offset_x = int(radius * 0.7)
            ear_offset_y = int(radius * 0.7)

            ear_color = COLORS["player_shadow"]
            pygame.draw.circle(
                screen,
                ear_color,
                (center_x - ear_offset_x, center_y - ear_offset_y),
                ear_radius,
            )
            pygame.draw.circle(
                screen,
                ear_color,
                (center_x + ear_offset_x, center_y - ear_offset_y),
                ear_radius,
            )

            # Shadow
            pygame.draw.circle(
                screen, COLORS["player_shadow"], (center_x, center_y + 3), radius
            )

            # Main Body
            pygame.draw.circle(screen, COLORS["player"], (center_x, center_y), radius)

            # Blush (Cheeks)
            blush_offset_x = int(radius * 0.6)
            blush_offset_y = int(radius * 0.1)
            blush_radius = int(radius * 0.2)
            pygame.draw.circle(
                screen,
                (255, 180, 200),
                (center_x - blush_offset_x, center_y + blush_offset_y),
                blush_radius,
            )
            pygame.draw.circle(
                screen,
                (255, 180, 200),
                (center_x + blush_offset_x, center_y + blush_offset_y),
                blush_radius,
            )

            # Eyes
            eye_offset_x = int(radius * 0.35)
            eye_offset_y = -int(radius * 0.15)
            eye_radius = int(radius * 0.12)

            pygame.draw.circle(
                screen,
                (40, 40, 40),
                (center_x - eye_offset_x, center_y + eye_offset_y),
                eye_radius,
            )
            pygame.draw.circle(
                screen,
                (40, 40, 40),
                (center_x + eye_offset_x, center_y + eye_offset_y),
                eye_radius,
            )

            # Nose/Mouth area (optional small dot)
            pygame.draw.circle(
                screen, (40, 40, 40), (center_x, center_y + int(radius * 0.15)), 2
            )

    def render_ui(self, game_state: GameState, show_help: bool = False) -> None:
        stats = game_state.get_stats()

        # Top Bar Background
        bar_height = 40
        pygame.draw.rect(
            self.screen, COLORS["panel_bg"], (0, 0, self.screen.get_width(), bar_height)
        )
        pygame.draw.line(
            self.screen,
            COLORS["grid_lines"],
            (0, bar_height),
            (self.screen.get_width(), bar_height),
            1,
        )

        # Stats Text
        if self.font:
            font = self.font

            # Helper to draw stats pill
            def draw_stat(
                text: str, x: int, color: ColorLike = COLORS["text_main"]
            ) -> int:
                surf = font.render(text, True, color)
                rect = surf.get_rect(midleft=(x, bar_height // 2))
                self.screen.blit(surf, rect)
                return rect.right + 20

            x_pos = 20
            x_pos = draw_stat(f"步數: {stats['moves']}", x_pos)
            x_pos = draw_stat(f"推動: {stats['pushes']}", x_pos)
            x_pos = draw_stat(f"時間: {stats['time']}", x_pos)

            # Helper prompt
            help_surf = self.font.render("按 H 顯示說明", True, COLORS["text_dim"])
            help_rect = help_surf.get_rect(
                midright=(self.screen.get_width() - 20, bar_height // 2)
            )
            self.screen.blit(help_surf, help_rect)

        if show_help and self.font:
            self._render_help_overlay()

    def _render_help_overlay(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill(COLORS["overlay"])
        self.screen.blit(overlay, (0, 0))

        # Card
        w, h = 400, 350
        rect = pygame.Rect(
            (self.screen.get_width() - w) // 2,
            (self.screen.get_height() - h) // 2,
            w,
            h,
        )
        pygame.draw.rect(self.screen, COLORS["panel_bg"], rect, border_radius=12)
        pygame.draw.rect(
            self.screen, COLORS["text_highlight"], rect, 2, border_radius=12
        )

        lines = [
            "遊戲控制",
            "",
            "移動: ↑↓←→ / WASD",
            "撤銷: Z / Backspace",
            "重做: Y / R",
            "重置: F5",
            "選單: M",
        ]

        y = rect.top + 40
        for i, line in enumerate(lines):
            if not self.font:
                break
            color = COLORS["text_highlight"] if i == 0 else COLORS["text_main"]
            surf = self.font.render(line, True, color)
            x = rect.centerx - surf.get_width() // 2
            self.screen.blit(surf, (x, y))
            y += 35

    def render_win_screen(self, stats: dict[str, Any], is_record: bool = False) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill(COLORS["overlay"])
        self.screen.blit(overlay, (0, 0))

        # Victory Card
        w, h = 500, 400
        rect = pygame.Rect(
            (self.screen.get_width() - w) // 2,
            (self.screen.get_height() - h) // 2,
            w,
            h,
        )

        # Glow
        glow_rect = rect.inflate(20, 20)
        pygame.draw.rect(
            self.screen, (*COLORS["success"], 50), glow_rect, border_radius=20
        )

        pygame.draw.rect(self.screen, COLORS["panel_bg"], rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["success"], rect, 3, border_radius=15)

        if self.big_font:
            title = self.big_font.render("MISSION COMPLETE!", True, COLORS["success"])
            title_rect = title.get_rect(centerx=rect.centerx, y=rect.y + 40)
            self.screen.blit(title, title_rect)

        if self.font:
            y = rect.y + 120
            lines = [
                f"步數: {stats['moves']}",
                f"推動: {stats['pushes']}",
                f"時間: {stats['time']}",
            ]

            for line in lines:
                surf = self.font.render(line, True, COLORS["text_main"])
                self.screen.blit(surf, (rect.x + 150, y))
                y += 40

            if is_record:
                rec_surf = self.font.render("🏆 新紀錄!", True, COLORS["warning"])
                rec_rect = rec_surf.get_rect(centerx=rect.centerx, y=y)
                self.screen.blit(rec_surf, rec_rect)
                y += 40

            # Hint
            hint_surf = self.font.render(
                "按 N 下一關 / R 重玩 / M 選單", True, COLORS["text_dim"]
            )
            hint_rect = hint_surf.get_rect(
                centerx=rect.centerx, bottom=rect.bottom - 30
            )
            self.screen.blit(hint_surf, hint_rect)

    def render_game_over_screen(self) -> None:
        """Render deadlock / game-over overlay."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill(COLORS["overlay"])
        self.screen.blit(overlay, (0, 0))

        # Game Over Card
        w, h = 500, 320
        rect = pygame.Rect(
            (self.screen.get_width() - w) // 2,
            (self.screen.get_height() - h) // 2,
            w,
            h,
        )

        # Red glow
        glow_rect = rect.inflate(20, 20)
        pygame.draw.rect(
            self.screen, (*COLORS["error"], 50), glow_rect, border_radius=20
        )

        pygame.draw.rect(self.screen, COLORS["panel_bg"], rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["error"], rect, 3, border_radius=15)

        if self.big_font:
            title = self.big_font.render("死鎖!", True, COLORS["error"])
            title_rect = title.get_rect(centerx=rect.centerx, y=rect.y + 40)
            self.screen.blit(title, title_rect)

        if self.font:
            # Explanation
            msg = self.font.render(
                "箱子被卡住了，這一關無法繼續。", True, COLORS["text_main"]
            )
            msg_rect = msg.get_rect(centerx=rect.centerx, y=rect.y + 120)
            self.screen.blit(msg, msg_rect)

            # Hint
            hint_surf = self.font.render(
                "按 Z 撤銷 / R 重玩 / M 選單", True, COLORS["text_dim"]
            )
            hint_rect = hint_surf.get_rect(
                centerx=rect.centerx, bottom=rect.bottom - 30
            )
            self.screen.blit(hint_surf, hint_rect)
