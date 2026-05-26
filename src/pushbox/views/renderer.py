"""Game renderer using pygame."""

import math
import os
from typing import Any, Optional

import pygame

from ..models.game_state import GameState
from ..utils.constants import CELL_SIZE, COLORS, CellType, ColorLike
from ..utils.paths import get_resource_path


class Animation:
    """Base class for all transient screen animations."""

    def __init__(self, duration: float, start_time: float) -> None:
        """Initialize the base animation with duration and start timestamp."""
        self.duration = duration
        self.start_time = start_time
        self.finished = False

    def update(self, current_time: float) -> None:
        """Update animation status, checking if it has finished."""
        if current_time - self.start_time >= self.duration:
            self.finished = True

    def get_progress(self, current_time: float) -> float:
        """Get the current progress of the animation (from 0.0 to 1.0)."""
        elapsed = current_time - self.start_time
        return min(1.0, elapsed / self.duration) if self.duration > 0 else 1.0

    def render(
        self,
        screen: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int = CELL_SIZE,
    ) -> None:
        """Render the animation frame onto the screen canvas."""
        pass


class MoveAnimation(Animation):
    """Animation for player and box movement interpolations."""

    def __init__(
        self,
        from_pos: tuple[int, int],
        to_pos: tuple[int, int],
        cell_type: int,
        duration: float,
        start_time: float,
    ) -> None:
        """Initialize a move animation with start/end positions and cell type."""
        super().__init__(duration, start_time)
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.cell_type = cell_type

    def render(
        self,
        screen: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int = CELL_SIZE,
    ) -> None:
        current_time = pygame.time.get_ticks() / 1000.0
        progress = self.get_progress(current_time)

        # Easing function (Ease Out Cubic)
        t = progress - 1
        ease_progress = t * t * t + 1

        fr, fc = self.from_pos
        tr, tc = self.to_pos

        current_r = fr + (tr - fr) * ease_progress
        current_c = fc + (tc - fc) * ease_progress

        x = offset_x + int(current_c * cell_size)
        y = offset_y + int(current_r * cell_size)

        if self.cell_type == CellType.PLAYER:
            Renderer.draw_player(screen, x, y, cell_size)
        elif self.cell_type in [CellType.BOX, CellType.BOX_ON_TARGET]:
            Renderer.draw_box(
                screen,
                x,
                y,
                on_target=(self.cell_type == CellType.BOX_ON_TARGET),
                cell_size=cell_size,
            )


class WinAnimation(Animation):
    """Victory celebration screen particle effect animation."""

    def __init__(
        self, start_time: float, screen_width: int = 800, screen_height: int = 600
    ) -> None:
        """Initialize the victory confetti animation."""
        super().__init__(3.0, start_time)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particles: list[dict[str, Any]] = []
        self._init_particles()

    def _init_particles(self) -> None:
        """Create random colored confetti particle descriptors."""
        import random

        colors = [COLORS["success"], COLORS["warning"], COLORS["target"]]
        for _ in range(100):
            self.particles.append(
                {
                    "x": random.randint(0, self.screen_width),
                    "y": random.randint(0, self.screen_height),
                    "vx": random.uniform(-4, 4),
                    "vy": random.uniform(-8, -2),
                    "color": random.choice(colors),
                    "size": random.randint(3, 8),
                    "life": 1.0,
                    "decay": random.uniform(0.005, 0.02),
                }
            )

    def update(self, current_time: float) -> None:
        """Update particles position, gravity, and life cycle decay."""
        super().update(current_time)
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.2  # Gravity
            p["life"] -= p["decay"]

    def render(
        self,
        screen: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int = CELL_SIZE,
    ) -> None:
        """Render all active fading particles onto the screen."""
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


class TargetSparkAnimation(Animation):
    """Animation for target spark explosion when a box is pushed onto a target."""

    def __init__(
        self, pos: tuple[int, int], start_time: float, duration: float = 0.25
    ) -> None:
        """Initialize target spark animation at a grid position (row, col)."""
        super().__init__(duration, start_time)
        self.pos = pos
        self.particles: list[dict[str, Any]] = []
        self._init_particles()

    def _init_particles(self) -> None:
        """Create explosive spark particle descriptors."""
        import random

        colors = [
            (152, 195, 121),  # success green
            (180, 220, 150),  # light green
            (210, 255, 180),  # extra light green
        ]
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 4.0)
            self.particles.append(
                {
                    "dx": math.cos(angle) * speed,
                    "dy": math.sin(angle) * speed,
                    "color": random.choice(colors),
                    "size": random.randint(2, 5),
                    "life": 1.0,
                    "decay": random.uniform(0.04, 0.08),
                }
            )

    def update(self, current_time: float) -> None:
        """Update particle physics and decay."""
        super().update(current_time)
        for p in self.particles:
            p["life"] -= p["decay"]

    def render(
        self,
        screen: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int = CELL_SIZE,
    ) -> None:
        row, col = self.pos
        center_x = offset_x + int((col + 0.5) * cell_size)
        center_y = offset_y + int((row + 0.5) * cell_size)

        current_time = pygame.time.get_ticks() / 1000.0
        progress = self.get_progress(current_time)

        for p in self.particles:
            if p["life"] > 0:
                px = center_x + p["dx"] * progress * cell_size * 0.6
                py = center_y + p["dy"] * progress * cell_size * 0.6

                color = list(p["color"])
                if len(color) == 3:
                    color.append(255)
                color[3] = int(255 * p["life"])

                size = max(1, int(p["size"] * p["life"]))

                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (size, size), size)
                screen.blit(surf, (int(px - size), int(py - size)))


class Renderer:
    """Main game view rendering orchestrator using Pygame."""

    PLAYER_IMAGE: Optional[pygame.Surface] = None

    def __init__(self, screen: pygame.Surface) -> None:
        """Initialize game board renderer, font systems, and graphics assets."""
        self.screen = screen
        self.font: Optional[pygame.font.Font] = None
        self.big_font: Optional[pygame.font.Font] = None
        self._init_fonts()

        self.animations: list[Animation] = []
        self.animation_enabled = True

        # Screen Shake state
        self.shake_duration = 0.0
        self.shake_intensity = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        # Solver Hint state
        self.hint_path: list[tuple[int, int]] = []
        self.hint_message: Optional[str] = None
        self.hint_end_time: int = 0

        if Renderer.PLAYER_IMAGE is None:
            self._load_resources()

    def _load_resources(self) -> None:
        """Load game assets."""
        try:
            img_path = get_resource_path("assets/images/player.jpeg")

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
        """Initialize display and overlay fonts with fallbacks."""
        try:
            self.font = pygame.font.SysFont("microsoftyahei", 20)
            self.big_font = pygame.font.SysFont("microsoftyahei", 48, bold=True)
        except (OSError, pygame.error):
            self.font = pygame.font.Font(None, 24)
            self.big_font = pygame.font.Font(None, 64)

    def set_animation_enabled(self, enabled: bool) -> None:
        """Enable or disable visual transition animations."""
        self.animation_enabled = enabled

    def add_animation(self, animation: Animation) -> None:
        """Register a new screen animation to the execution loop."""
        if self.animation_enabled:
            self.animations.append(animation)

    def add_move_animation(
        self,
        from_pos: tuple[int, int],
        to_pos: tuple[int, int],
        cell_type: int,
        duration: float = 0.15,
    ) -> None:
        """Create and queue a move interpolation animation."""
        if self.animation_enabled:
            anim = MoveAnimation(
                from_pos, to_pos, cell_type, duration, pygame.time.get_ticks() / 1000.0
            )
            self.add_animation(anim)

    def add_win_animation(self) -> None:
        """Create and queue a win celebration confetti animation."""
        if self.animation_enabled:
            width = self.screen.get_width()
            height = self.screen.get_height()
            anim = WinAnimation(pygame.time.get_ticks() / 1000.0, width, height)
            self.add_animation(anim)

    def trigger_screen_shake(self, duration: float = 0.15, intensity: int = 4) -> None:
        """Trigger screen shake effect for the board.

        Args:
            duration: Shake duration in seconds.
            intensity: Shake offset intensity in pixels.
        """
        if self.animation_enabled:
            self.shake_duration = duration
            self.shake_intensity = intensity

    def update_animations(self) -> None:
        """Update and purge finished animation descriptors and screen shake."""
        current_time = pygame.time.get_ticks() / 1000.0

        # Calculate dt (time difference since last update)
        if not hasattr(self, "_last_update_time"):
            self._last_update_time = current_time
        dt = current_time - self._last_update_time
        self._last_update_time = current_time

        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            if self.shake_duration <= 0:
                self.shake_duration = 0.0
                self.shake_offset_x = 0
                self.shake_offset_y = 0
            else:
                import random

                self.shake_offset_x = random.randint(
                    -self.shake_intensity, self.shake_intensity
                )
                self.shake_offset_y = random.randint(
                    -self.shake_intensity, self.shake_intensity
                )
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

        for anim in self.animations[:]:
            anim.update(current_time)
            if anim.finished:
                self.animations.remove(anim)

    def render_game(
        self, game_state: GameState, offset_x: int = 0, offset_y: int = 0
    ) -> None:
        """Render the complete game board, grid walls, floors, targets, and objects."""
        level = game_state.level

        # Calculate dynamic cell_size based on screen dimensions and level bounds
        # Reserve space for upper HUD (60px) and bottom buttons (60px)
        available_width = self.screen.get_width() - 40  # 20px padding each side
        available_height = (
            self.screen.get_height() - 140
        )  # 60 top + 60 bottom + 20 padding

        cell_w = available_width // level.cols
        cell_h = available_height // level.rows
        cell_size = min(cell_w, cell_h, 60)  # max size 60px
        cell_size = max(cell_size, 25)  # min size 25px

        # Draw background pattern first
        self.screen.fill(COLORS["background"])

        # Calculate board dimensions and centering based on dynamic cell_size
        board_width = level.cols * cell_size
        board_height = level.rows * cell_size

        if offset_x == 0:
            offset_x = (self.screen.get_width() - board_width) // 2
        if offset_y == 0:
            offset_y = (self.screen.get_height() - board_height) // 2

        # Apply screen shake offsets
        offset_x += self.shake_offset_x
        offset_y += self.shake_offset_y

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
                x = offset_x + col * cell_size
                y = offset_y + row * cell_size

                cell = level.get_cell(row, col)
                initial_cell = level.initial_grid[row, col]

                # 1. Always draw floor
                self._draw_floor(x, y, (row + col) % 2 == 0, cell_size)

                # 2. Draw Target
                if initial_cell == CellType.TARGET:
                    self._draw_target(x, y, cell_size)
                elif cell == CellType.TARGET:  # In case level modified
                    self._draw_target(x, y, cell_size)

                # 3. Draw Objects (if not animating)
                if (row, col) not in animating_cells:
                    if cell == CellType.WALL:
                        self._draw_wall(x, y, cell_size)
                    elif cell == CellType.BOX:
                        Renderer.draw_box(self.screen, x, y, False, cell_size)
                    elif cell == CellType.BOX_ON_TARGET:
                        Renderer.draw_box(self.screen, x, y, True, cell_size)
                    elif cell == CellType.PLAYER:
                        Renderer.draw_player(self.screen, x, y, cell_size)

        # Draw Animations on top
        for anim in self.animations:
            anim.render(self.screen, offset_x, offset_y, cell_size)

        # Draw Solver Hint Path on top of animations
        current_ticks = pygame.time.get_ticks()
        if (
            hasattr(self, "hint_end_time")
            and current_ticks < self.hint_end_time
            and getattr(self, "hint_path", None)
        ):
            self._draw_hint_path(level, offset_x, offset_y, cell_size, current_ticks)

    def _draw_hint_path(
        self,
        level: Any,
        offset_x: int,
        offset_y: int,
        cell_size: int,
        current_ticks: int,
    ) -> None:
        """Draw a beautiful semi-transparent hint path on the game board."""
        player_pos = level.get_player_position()
        if not player_pos:
            return

        import math

        pr, pc = player_pos
        points = [(pr, pc)]
        for dr, dc in self.hint_path:
            nr, nc = points[-1][0] + dr, points[-1][1] + dc
            points.append((nr, nc))

        # 1. Draw glowing highlight pulse for the next immediate step (points[1])
        if len(points) >= 2:
            tr, tc = points[1]
            tx = offset_x + tc * cell_size
            ty = offset_y + tr * cell_size

            pulse = (math.sin(current_ticks * 0.008) + 1) / 2.0  # 0.0 to 1.0
            alpha = int(80 + pulse * 100)  # 80 to 180

            surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            highlight_color = COLORS["text_highlight"]

            # Light fill
            pygame.draw.rect(
                surf,
                (*highlight_color[:3], alpha // 2),
                (2, 2, cell_size - 4, cell_size - 4),
                border_radius=8,
            )
            # Outer border pulsing
            pygame.draw.rect(
                surf,
                (*highlight_color[:3], alpha),
                (0, 0, cell_size, cell_size),
                3,
                border_radius=8,
            )
            self.screen.blit(surf, (tx, ty))

        # 2. Draw lines connecting the path steps
        if len(points) >= 2:
            line_surf = pygame.Surface(
                (self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA
            )
            highlight_color = COLORS["text_highlight"]

            for i in range(len(points) - 1):
                r1, c1 = points[i]
                r2, c2 = points[i + 1]

                x1 = offset_x + int((c1 + 0.5) * cell_size)
                y1 = offset_y + int((r1 + 0.5) * cell_size)
                x2 = offset_x + int((c2 + 0.5) * cell_size)
                y2 = offset_y + int((r2 + 0.5) * cell_size)

                # Draw bold semi-transparent line
                pygame.draw.line(
                    line_surf, (*highlight_color[:3], 150), (x1, y1), (x2, y2), 5
                )
                # Draw small circles at intermediate nodes
                if i > 0:
                    pygame.draw.circle(
                        line_surf, (*highlight_color[:3], 200), (x1, y1), 6
                    )

            self.screen.blit(line_surf, (0, 0))

    def _draw_floor(
        self, x: int, y: int, is_light: bool, cell_size: int = CELL_SIZE
    ) -> None:
        """Draw flat checkerboard grid floor tiles."""
        rect = pygame.Rect(x, y, cell_size, cell_size)
        color = COLORS["floor_light"] if is_light else COLORS["floor"]
        pygame.draw.rect(self.screen, color, rect)

    def _draw_wall(self, x: int, y: int, cell_size: int = CELL_SIZE) -> None:
        """Draw pseudo-3D grid wall blocks with shadows and highlights."""
        # Pseudo 3D Wall
        rect = pygame.Rect(x, y, cell_size, cell_size)

        shadow_h = max(2, int(cell_size * 0.08))
        border_r = max(1, int(cell_size * 0.08))

        # Shadow/Side (Darker)
        pygame.draw.rect(
            self.screen,
            COLORS["wall_shadow"],
            rect.move(0, shadow_h),
            border_radius=border_r,
        )

        # Top Face (Lighter)
        top_rect = pygame.Rect(x, y, cell_size, cell_size - shadow_h)
        pygame.draw.rect(self.screen, COLORS["wall"], top_rect, border_radius=border_r)

        # Highlight (Top Edge)
        pygame.draw.line(
            self.screen,
            (255, 255, 255, 50),
            (x + 2, y + 2),
            (x + cell_size - 2, y + 2),
            2,
        )

    def _draw_target(self, x: int, y: int, cell_size: int = CELL_SIZE) -> None:
        """Draw circular target point tiles with glow borders."""
        center_x = x + cell_size // 2
        center_y = y + cell_size // 2
        radius = cell_size // 4

        # Glow
        surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
        pygame.draw.circle(
            surf, (*COLORS["target"], 50), (cell_size // 2, cell_size // 2), radius + 4
        )
        self.screen.blit(surf, (x, y))

        # Dot
        pygame.draw.circle(self.screen, COLORS["target"], (center_x, center_y), radius)
        pygame.draw.circle(
            self.screen, COLORS["target_glow"], (center_x, center_y), max(1, radius - 2)
        )

    @staticmethod
    def draw_box(
        screen: pygame.Surface,
        x: int,
        y: int,
        on_target: bool = False,
        cell_size: int = CELL_SIZE,
    ) -> None:
        """Draw pseudo-3D crate objects with target coloring decorations."""
        # Pseudo 3D Box
        margin = max(1, int(cell_size * 0.08))
        size = cell_size - margin * 2
        rect = pygame.Rect(x + margin, y + margin, size, size)

        base_color = COLORS["box_on_target"] if on_target else COLORS["box"]
        shadow_color = (
            COLORS["box_on_target_shadow"] if on_target else COLORS["box_shadow"]
        )

        shadow_h = max(2, int(cell_size * 0.08))
        border_r = max(1, int(cell_size * 0.12))

        # Shadow/Side
        pygame.draw.rect(
            screen, shadow_color, rect.move(0, shadow_h), border_radius=border_r
        )

        # Top Face
        top_rect = pygame.Rect(x + margin, y + margin, size, size - shadow_h)
        pygame.draw.rect(screen, base_color, top_rect, border_radius=border_r)

        # Decoration (Inner square)
        inner_margin = max(2, int(cell_size * 0.16))
        inner_rect = top_rect.inflate(-inner_margin * 2, -inner_margin * 2)
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(
                screen,
                shadow_color,
                inner_rect,
                2,
                border_radius=max(1, int(cell_size * 0.08)),
            )

        # Highlight
        if on_target:
            pygame.draw.rect(
                screen, (255, 255, 255, 100), top_rect, 2, border_radius=border_r
            )

    @staticmethod
    def draw_player(
        screen: pygame.Surface, x: int, y: int, cell_size: int = CELL_SIZE
    ) -> None:
        """Draw character models using loaded image files or cute fallbacks."""
        center_x = x + cell_size // 2
        center_y = y + cell_size // 2

        if Renderer.PLAYER_IMAGE:
            # Scale image to match cell_size
            scaled_img = pygame.transform.smoothscale(
                Renderer.PLAYER_IMAGE, (cell_size, cell_size)
            )
            rect = scaled_img.get_rect(center=(center_x, center_y))
            # Draw shadow
            pygame.draw.circle(
                screen,
                COLORS["player_shadow"],
                (center_x, center_y + 3),
                rect.width // 2,
            )
            screen.blit(scaled_img, rect)
        else:
            # Fallback: Cuter Player Design (Bear-ish)
            radius = int(cell_size * 0.35)

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

    def render_ui(
        self,
        game_state: GameState,
        show_help: bool = False,
        control_scheme: str = "",
    ) -> None:
        """Render top statistics bar, controls scheme indicator, and help overlays."""
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
            level_name = game_state.level.name
            if len(level_name) > 20:
                display_text = level_name[:17] + "..."
            else:
                display_text = level_name
            x_pos = draw_stat(display_text, x_pos, COLORS["text_highlight"])

            x_pos = draw_stat(f"步數: {stats['moves']}", x_pos)
            x_pos = draw_stat(f"推動: {stats['pushes']}", x_pos)
            x_pos = draw_stat(f"時間: {stats['time']}", x_pos)

            # Helper prompt
            help_surf = self.font.render("按 H 顯示說明", True, COLORS["text_dim"])
            help_rect = help_surf.get_rect(
                midright=(self.screen.get_width() - 20, bar_height // 2)
            )
            self.screen.blit(help_surf, help_rect)

            # Control scheme indicator
            if control_scheme:
                scheme_surf = self.font.render(
                    f"控制: {control_scheme}", True, COLORS["text_dim"]
                )
                scheme_rect = scheme_surf.get_rect(
                    midright=(help_rect.left - 30, bar_height // 2)
                )
                self.screen.blit(scheme_surf, scheme_rect)

            # Onboarding Level 0 instruction rendering
            if game_state.level.name == "Level 0":
                from src.pushbox.utils.constants import CellType

                moves = stats.get("moves", 0)
                is_complete = game_state.level.is_complete()

                # Find player and box positions
                player_pos = game_state.level.get_player_position()
                box_positions = []
                for r in range(game_state.level.rows):
                    for c in range(game_state.level.cols):
                        if game_state.level.get_cell(r, c) == CellType.BOX:
                            box_positions.append((r, c))

                # Determine instruction text
                if is_complete:
                    tip_text = "提示：目標點變為綠色，通關！"
                elif moves == 0:
                    tip_text = "提示：按 WASD 或方向鍵進行移動"
                else:
                    # Check adjacency
                    is_adjacent = False
                    if player_pos:
                        pr, pc = player_pos
                        for br, bc in box_positions:
                            if abs(pr - br) + abs(pc - bc) == 1:
                                is_adjacent = True
                                break
                    if is_adjacent:
                        tip_text = "提示：走到箱子旁，繼續向前推動它"
                    else:
                        tip_text = "提示：走到箱子旁，將它推向紅色的目標點"

                # Render tip banner
                text_surf = font.render(tip_text, True, COLORS["text_highlight"])
                bg_w = text_surf.get_width() + 40
                bg_h = 36
                bg_rect = pygame.Rect(
                    (self.screen.get_width() - bg_w) // 2, bar_height + 15, bg_w, bg_h
                )

                # Semi-transparent panel
                surf = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
                pygame.draw.rect(
                    surf,
                    (*COLORS["panel_bg"][:3], 230),
                    (0, 0, bg_w, bg_h),
                    border_radius=8,
                )
                pygame.draw.rect(
                    surf, COLORS["grid_lines"], (0, 0, bg_w, bg_h), 1, border_radius=8
                )
                text_rect = text_surf.get_rect(center=(bg_w // 2, bg_h // 2))
                surf.blit(text_surf, text_rect)

                self.screen.blit(surf, bg_rect)

        # Draw Solver Hint Message Banner (Unified UI Language)
        current_ticks = pygame.time.get_ticks()
        if (
            hasattr(self, "hint_end_time")
            and current_ticks < self.hint_end_time
            and self.hint_message is not None
            and self.font
        ):
            tip_text = self.hint_message
            text_surf = self.font.render(tip_text, True, COLORS["text_highlight"])
            bg_w = text_surf.get_width() + 40
            bg_h = 36
            bg_rect = pygame.Rect(
                (self.screen.get_width() - bg_w) // 2, bar_height + 15, bg_w, bg_h
            )

            surf = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
            pygame.draw.rect(
                surf,
                (*COLORS["panel_bg"][:3], 230),
                (0, 0, bg_w, bg_h),
                border_radius=8,
            )
            pygame.draw.rect(
                surf, COLORS["grid_lines"], (0, 0, bg_w, bg_h), 1, border_radius=8
            )
            text_rect = text_surf.get_rect(center=(bg_w // 2, bg_h // 2))
            surf.blit(text_surf, text_rect)

            self.screen.blit(surf, bg_rect)

        if show_help and self.font:
            self._render_help_overlay()

    def _render_help_overlay(self) -> None:
        """Draw a semi-transparent overlay and in-game shortcut card."""
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
            "退出: Ctrl+Q",
            "",
            "按任意鍵返回遊戲",
        ]

        y = rect.top + 30
        for i, line in enumerate(lines):
            if not self.font:
                break
            if i == 0:
                color = COLORS["text_highlight"]
            elif i == len(lines) - 1:
                color = COLORS["text_dim"]
            else:
                color = COLORS["text_main"]
            surf = self.font.render(line, True, color)
            x = rect.centerx - surf.get_width() // 2
            self.screen.blit(surf, (x, y))
            y += 30

    def render_win_screen(
        self,
        stats: dict[str, Any],
        is_record: bool = False,
        best_moves: Optional[int] = None,
    ) -> None:
        """Draw level clear panel overlay displaying moves, pushes, and record stats."""
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
            y = rect.y + 110
            lines = [
                f"步數: {stats['moves']}",
                f"推動: {stats['pushes']}",
                f"時間: {stats['time']}",
            ]

            for line in lines:
                surf = self.font.render(line, True, COLORS["text_main"])
                self.screen.blit(surf, (rect.x + 150, y))
                y += 35

            best = best_moves if best_moves is not None else stats["moves"]
            best_surf = self.font.render(
                f"歷史最佳: {best} 步", True, COLORS["text_dim"]
            )
            self.screen.blit(best_surf, (rect.x + 150, y))
            y += 35

            if is_record:
                rec_surf = self.font.render("🏆 新紀錄!", True, COLORS["warning"])
                rec_rect = rec_surf.get_rect(centerx=rect.centerx, y=y)
                self.screen.blit(rec_surf, rec_rect)
                y += 35

            # Hint
            hint_surf = self.font.render(
                "按 N 下一關 / R 重玩 / M 選單", True, COLORS["text_dim"]
            )
            hint_rect = hint_surf.get_rect(
                centerx=rect.centerx, bottom=rect.bottom - 30
            )
            self.screen.blit(hint_surf, hint_rect)

    def render_game_over_screen(self) -> None:
        """Render deadlock / game-over card overlay explaining stalemate state."""
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

    def render_pause_screen(self) -> None:
        """Render in-game pause card overlay offering restart or exit actions."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill(COLORS["overlay"])
        self.screen.blit(overlay, (0, 0))

        # Pause Card
        w, h = 500, 350
        rect = pygame.Rect(
            (self.screen.get_width() - w) // 2,
            (self.screen.get_height() - h) // 2,
            w,
            h,
        )

        # Glow (using warning color)
        glow_rect = rect.inflate(20, 20)
        pygame.draw.rect(
            self.screen, (*COLORS["warning"], 50), glow_rect, border_radius=20
        )

        pygame.draw.rect(self.screen, COLORS["panel_bg"], rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["warning"], rect, 3, border_radius=15)

        if self.big_font:
            title = self.big_font.render("暫停", True, COLORS["warning"])
            title_rect = title.get_rect(centerx=rect.centerx, y=rect.y + 40)
            self.screen.blit(title, title_rect)

        if self.font:
            # Explanation
            msg = self.font.render("遊戲已暫停", True, COLORS["text_main"])
            msg_rect = msg.get_rect(centerx=rect.centerx, y=rect.y + 110)
            self.screen.blit(msg, msg_rect)

            # Details/Hints
            y = rect.y + 155
            hints = [
                "Esc / P : 繼續遊戲 (Resume)",
                "R : 重置關卡 (Restart)",
                "S : 遊戲設定 (Settings)",
                "M : 返回主選單 (Main Menu)",
            ]
            for hint in hints:
                surf = self.font.render(hint, True, COLORS["text_dim"])
                surf_rect = surf.get_rect(centerx=rect.centerx, y=y)
                self.screen.blit(surf, surf_rect)
                y += 35
