"""
UI Components for DO OR DICE.
Contains LogFeed, PlayerVisual, and Dice classes that replicate the prototype visuals.
"""
from __future__ import annotations
import math
import random
import pygame

from .theme import (
    C_BG, C_SIDEBAR, C_PANEL, C_GRID, C_LINE,
    C_TEXT_MAIN, C_TEXT_DIM, C_ACCENT, C_DANGER, C_SUCCESS, C_GOLD, C_PURPLE,
    draw_rounded_rect, draw_smooth_circle, load_and_crop_avatar, AUD_DIR
)
from .player_profiles import PLAYER_PROFILES

from src.models import Player, Status


class LogFeed:
    """A sleek, modern history feed with card-style entries."""
    
    def __init__(self, x: int, y: int, w: int, h: int):
        self.rect = pygame.Rect(x, y, w, h)
        self.messages = []
        self.font = pygame.font.SysFont("Verdana", 12)
        self.icon_font = pygame.font.SysFont("Segoe UI Symbol", 14)

    def add(self, text: str, color: tuple = C_TEXT_MAIN) -> None:
        """Add a message to the log feed."""
        surf = self.font.render(text, True, color)
        self.messages.insert(0, {"surf": surf, "col": color, "offset": -20, "alpha": 0, "life": 400})
        if len(self.messages) > 8:
            self.messages.pop()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the log feed on screen."""
        # Draw Container Background
        draw_rounded_rect(screen, C_PANEL, self.rect, 12, 255)
        # Header
        pygame.draw.line(screen, C_LINE, (self.rect.x + 10, self.rect.y + 30), (self.rect.right - 10, self.rect.y + 30))
        head_font = pygame.font.SysFont("Verdana", 11, bold=True)
        t = head_font.render("GAME HISTORY", True, C_TEXT_DIM)
        screen.blit(t, (self.rect.x + 15, self.rect.y + 8))

        # Content area clip
        clip_rect = pygame.Rect(self.rect.x, self.rect.y + 32, self.rect.width, self.rect.height - 35)
        screen.set_clip(clip_rect)
        
        start_y = self.rect.y + 45
        
        for i, msg in enumerate(self.messages):
            # Animation Logic
            if msg['offset'] < 0:
                msg['offset'] += 2
            if msg['alpha'] < 255:
                msg['alpha'] += 15
            
            y_pos = start_y + (i * 35)
            if y_pos > self.rect.bottom:
                break
            
            # Text
            s = msg['surf'].copy()
            s.set_alpha(msg['alpha'])
            screen.blit(s, (self.rect.x + 20 + msg['offset'], y_pos + 6))
            
            # Bullet point
            pygame.draw.circle(screen, msg['col'], (self.rect.x + 12, y_pos + 14), 3)

        screen.set_clip(None)


class PlayerVisual:
    """Visual representation of a player in the game arena."""
    
    def __init__(self, player: Player, idx: int):
        self.player = player
        self.idx = idx
        data = PLAYER_PROFILES.get(idx, {})
        self.display_name = data.get("name", player.name)
        
        # Visuals
        self.pos = (0, 0)
        self.base_size = 120
        self.rect = pygame.Rect(0, 0, self.base_size, self.base_size)
        self.scale = 1.0
        self.avatar_surf = load_and_crop_avatar(data.get("img", ""), self.base_size)
        
        # Audio
        audio_path = AUD_DIR / data.get("audio", "")
        self.sound = None
        if audio_path.exists():
            try:
                self.sound = pygame.mixer.Sound(str(audio_path))
            except Exception:
                pass

    @property
    def hp(self) -> int:
        return self.player.hp
    
    @property
    def max_hp(self) -> int:
        return 20
    
    @property
    def vp(self) -> int:
        return self.player.vp
    
    @property
    def alive(self) -> bool:
        return self.player.status == Status.ALIVE
    
    @property
    def name(self) -> str:
        return self.player.name

    def calculate_position(self, center: tuple, radius: float) -> None:
        """Calculate position on the circular arena."""
        angle = -90 + (self.idx * (360 / 5))
        rad = math.radians(angle)
        self.pos = (center[0] + radius * math.cos(rad), center[1] + radius * math.sin(rad))
        self.rect.center = self.pos

    def update(self, is_hovered: bool) -> None:
        """Update visual state."""
        target = 1.15 if is_hovered else 1.0
        self.scale += (target - self.scale) * 0.15

    def draw(self, surf: pygame.Surface, is_active: bool, is_target: bool) -> None:
        """Draw the player visual on the surface."""
        cx, cy = self.pos
        s = self.scale
        
        # 0. Shadow
        shadow_r = int(self.base_size * s * 0.5)
        draw_smooth_circle(surf, (0, 0, 0, 60), (cx, cy + 5), shadow_r + 2)

        # 1. Styles
        border_col = C_LINE
        border_width = 3
        
        if not self.alive:
            border_col = (40, 40, 40)
            self.scale = 0.95
        elif is_active:
            border_col = C_ACCENT
            border_width = 4
        elif is_target:
            border_col = C_DANGER
            border_width = 4

        # 2. Active Glow
        if is_active and self.alive:
            pulse = 70 + math.sin(pygame.time.get_ticks() * 0.005) * 5
            draw_smooth_circle(surf, (*C_ACCENT, 40), (cx, cy), int(pulse * s))

        # 3. Avatar
        if self.avatar_surf:
            final_size = int(self.base_size * s)
            scaled = pygame.transform.smoothscale(self.avatar_surf, (final_size, final_size))
            
            # Desaturate if dead
            if not self.alive:
                grayscale = pygame.Surface(scaled.get_size()).convert_alpha()
                grayscale.fill((20, 20, 25))
                scaled.blit(grayscale, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
            r = scaled.get_rect(center=(int(cx), int(cy)))
            surf.blit(scaled, r)
            
            # Crisp Ring Border
            pygame.draw.circle(surf, border_col, (int(cx), int(cy)), (final_size // 2), border_width)

        # 4. Modern Stats Badge
        if self.alive:
            # HP Bar pill
            bar_w = 70 * s
            bar_h = 14 * s
            bar_rect = pygame.Rect(0, 0, int(bar_w), int(bar_h))
            bar_rect.center = (int(cx), int(cy + (60 * s)))
            
            draw_rounded_rect(surf, (20, 20, 25), bar_rect, 6)
            
            pct = max(0, self.hp / self.max_hp)
            fill_w = int((bar_w - 4) * pct)
            fill_rect = pygame.Rect(bar_rect.x + 2, bar_rect.y + 2, fill_w, int(bar_h - 4))
            col = C_SUCCESS if pct > 0.4 else C_DANGER
            if fill_w > 0:
                pygame.draw.rect(surf, col, fill_rect, border_radius=4)
                
            # VP Badge
            vp_rect = pygame.Rect(0, 0, int(40 * s), int(20 * s))
            vp_rect.center = (int(cx), int(cy - (65 * s)))
            draw_rounded_rect(surf, C_GOLD, vp_rect, 6)
            
            f_vp = pygame.font.SysFont("Verdana", int(12 * s), bold=True)
            t_vp = f_vp.render(f"{self.vp} VP", True, (20, 20, 20))
            surf.blit(t_vp, t_vp.get_rect(center=vp_rect.center))
            
            # Name
            try:
                f_nm = pygame.font.SysFont("segoeuiemoji", int(28 * s), bold=True)
            except Exception:
                f_nm = pygame.font.SysFont("Segoe UI", int(28 * s), bold=True)
            
            t_nm = f_nm.render(self.display_name.upper(), True, C_TEXT_MAIN)
            surf.blit(t_nm, t_nm.get_rect(center=(int(cx), int(cy - (82 * s)))))

        else:
            f_d = pygame.font.SysFont("Verdana", int(14 * s), bold=True)
            t_d = f_d.render("ELIMINATED", True, C_DANGER)
            surf.blit(t_d, t_d.get_rect(center=(int(cx), int(cy + 60 * s))))


class Dice:
    """Visual dice component with rolling animation."""
    
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 100, 100)
        self.val = 6
        self.rolling = False
        self.timer = 0
        self.target = 1
        self.offset = (0, 0)
        self.hover_scale = 1.0

    def roll(self, target: int) -> None:
        """Start a roll animation with target value."""
        self.rolling = True
        self.timer = 40
        self.target = target

    def update(self, hover: bool) -> bool:
        """Update dice state. Returns True when roll animation completes."""
        # Interactive hover spring
        target_s = 1.1 if hover else 1.0
        self.hover_scale += (target_s - self.hover_scale) * 0.2

        if self.rolling:
            self.timer -= 1
            self.offset = (random.randint(-2, 2), random.randint(-2, 2))
            if self.timer % 5 == 0:
                self.val = random.randint(1, 6)
            if self.timer <= 0:
                self.rolling = False
                self.val = self.target
                self.offset = (0, 0)
                return True
        return False

    def draw(self, surf: pygame.Surface) -> None:
        """Draw the dice on the surface."""
        cx, cy = self.rect.centerx + self.offset[0], self.rect.centery + self.offset[1]
        sz = int(100 * self.hover_scale)
        
        # Glow Effect on Hover/Roll
        if self.rolling or self.hover_scale > 1.01:
            pulse = 50 + int(math.sin(pygame.time.get_ticks() * 0.01) * 20)
            draw_smooth_circle(surf, (*C_ACCENT, pulse), (cx, cy), int(sz * 0.7))

        # Shadow
        shadow_rect = pygame.Rect(0, 0, sz, sz)
        shadow_rect.center = (cx, cy + 10)
        draw_rounded_rect(surf, (0, 0, 0), shadow_rect, 24, 60)

        # Body
        main_rect = pygame.Rect(0, 0, sz, sz)
        main_rect.center = (cx, cy)
        col = (245, 245, 250) if not self.rolling else (220, 230, 255)
        
        draw_rounded_rect(surf, col, main_rect, 24)
        
        # Border
        b_col = (200, 200, 210) if not self.rolling else C_ACCENT
        pygame.draw.rect(surf, b_col, main_rect, 3, border_radius=24)

        # Pips
        pip_col = (40, 45, 60)
        pip_sz = 9
        space = 26
        pips = []
        if self.val == 1:
            pips = [(0, 0)]
        elif self.val == 2:
            pips = [(-1, -1), (1, 1)]
        elif self.val == 3:
            pips = [(-1, -1), (0, 0), (1, 1)]
        elif self.val == 4:
            pips = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        elif self.val == 5:
            pips = [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
        elif self.val == 6:
            pips = [(-1, -1), (1, -1), (-1, 1), (1, 1), (-1, 0), (1, 0)]

        for dx, dy in pips:
            # Subtle pip shadow
            pygame.draw.circle(surf, (200, 200, 200), (cx + dx * space + 1, cy + dy * space + 1), pip_sz)
            pygame.draw.circle(surf, pip_col, (cx + dx * space, cy + dy * space), pip_sz)

        # "ROLL" Hint
        if not self.rolling and self.hover_scale > 1.01:
            f = pygame.font.SysFont("Verdana", 10, bold=True)
            t = f.render("ROLL", True, (100, 100, 100))
            surf.blit(t, t.get_rect(center=(cx, main_rect.bottom + 15)))

