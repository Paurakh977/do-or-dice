"""
UI Components for DO OR DICE.
Contains LogFeed, PlayerVisual, and Dice classes.
"""
from __future__ import annotations
import math
import random
import pygame

from .theme import (
    C_BG_TOP, C_SIDEBAR, C_PANEL, C_GRID, C_LINE,
    C_TEXT_MAIN, C_TEXT_DIM, C_ACCENT, C_DANGER, C_SUCCESS, C_GOLD, C_PURPLE, C_PINK,
    draw_rounded_rect, draw_smooth_circle, draw_glass_rect, load_and_crop_avatar, AUD_DIR
)
from .player_profiles import PLAYER_PROFILES

from models import Player, Status


class LogFeed:
    """A sleek, modern history feed with card-style entries."""
    
    def __init__(self, x: int, y: int, w: int, h: int):
        self.rect = pygame.Rect(x, y, w, h)
        self.messages = []
        self.font = pygame.font.SysFont("Verdana", 12)
        # self.icon_font = pygame.font.SysFont("Segoe UI Symbol", 14) # Unused and causes warning

    def add(self, text: str, color: tuple = C_TEXT_MAIN) -> None:
        """Add a message to the log feed."""
        surf = self.font.render(text, True, color)
        # Entries slide in from left (-20 offset) and fade in (alpha 0)
        self.messages.insert(0, {"surf": surf, "col": color, "offset": -20, "alpha": 0})
        if len(self.messages) > 10:
            self.messages.pop()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the log feed on screen."""
        # Draw Glassy Container
        draw_glass_rect(screen, self.rect, 16)
        
        # Header
        pygame.draw.line(screen, (255, 255, 255, 20), (self.rect.x + 10, self.rect.y + 35), (self.rect.right - 10, self.rect.y + 35))
        head_font = pygame.font.SysFont("Verdana", 11, bold=True)
        t = head_font.render("GAME HISTORY", True, (200, 200, 255))
        screen.blit(t, (self.rect.x + 15, self.rect.y + 12))

        # Content area clip
        clip_rect = pygame.Rect(self.rect.x, self.rect.y + 40, self.rect.width, self.rect.height - 45)
        screen.set_clip(clip_rect)
        
        start_y = self.rect.y + 50
        
        for i, msg in enumerate(self.messages):
            # Animation Logic
            if msg['offset'] < 0:
                msg['offset'] += 2
            if msg['alpha'] < 255:
                msg['alpha'] = min(255, msg['alpha'] + 25)
            
            y_pos = start_y + (i * 30)
            if y_pos > self.rect.bottom - 20:
                break
            
            # Text
            s = msg['surf'].copy()
            s.set_alpha(msg['alpha'])
            screen.blit(s, (self.rect.x + 25 + msg['offset'], y_pos))
            
            # Bullet point (glowing dot)
            # Ensure col is RGB before adding alpha
            bullet_col = (*msg['col'][:3], int(msg['alpha']))
            draw_smooth_circle(screen, bullet_col, (self.rect.x + 15, y_pos + 8), 3)

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
        self.pulse_phase = random.uniform(0, 6.28)
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
        # Smooth hover scale
        target = 1.25 if is_hovered else 1.0
        self.scale += (target - self.scale) * 0.15
        
        # Idle breathing animation phase
        self.pulse_phase += 0.05

    def draw(self, surf: pygame.Surface, is_active: bool, is_target: bool) -> None:
        """Draw the player visual on the surface."""
        cx, cy = self.pos
        
        # Apply breathing to scale if active
        current_scale = self.scale
        if is_active and self.alive:
            current_scale += math.sin(self.pulse_phase) * 0.03

        final_size = int(self.base_size * current_scale)
        
        # 0. Shadow / Glow
        if self.alive:
            if is_active:
                # Active player gets a big pulsing aura
                glow_r = int(final_size * 0.6 + math.sin(self.pulse_phase * 2) * 5)
                draw_smooth_circle(surf, (*C_ACCENT, 60), (cx, cy), glow_r + 10)
                draw_smooth_circle(surf, (*C_ACCENT, 100), (cx, cy), glow_r)
            elif is_target:
                # Target gets a danger glow
                draw_smooth_circle(surf, (*C_DANGER, 80), (cx, cy), int(final_size * 0.6))
            else:
                # Normal shadow
                draw_smooth_circle(surf, (0, 0, 0, 80), (cx, cy + 8), int(final_size * 0.5))
        
        # 1. Avatar
        if self.avatar_surf:
            scaled = pygame.transform.smoothscale(self.avatar_surf, (final_size, final_size))
            
            # Desaturate/Darken if dead
            if not self.alive:
                grayscale = pygame.Surface(scaled.get_size()).convert_alpha()
                grayscale.fill((30, 30, 40))
                scaled.blit(grayscale, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
            r = scaled.get_rect(center=(int(cx), int(cy)))
            surf.blit(scaled, r)
            
            # Ring Border
            border_col = C_LINE
            border_width = 3
            if is_active:
                border_col = C_ACCENT
                border_width = 4
            elif is_target:
                border_col = C_DANGER
                border_width = 4
            elif not self.alive:
                border_col = (60, 60, 70)
                
            pygame.draw.circle(surf, border_col, (int(cx), int(cy)), (final_size // 2), border_width)

        # 2. Modern Stats Badge (Floating below)
        if self.alive:
            # HP Bar pill
            bar_w = 80 * current_scale
            bar_h = 10 * current_scale
            bar_rect = pygame.Rect(0, 0, int(bar_w), int(bar_h))
            bar_rect.center = (int(cx), int(cy + (70 * current_scale)))
            
            # Bar background
            draw_rounded_rect(surf, (40, 40, 50), bar_rect, 5)
            
            # Bar fill
            pct = max(0, self.hp / self.max_hp)
            fill_w = int(bar_w * pct)
            if fill_w > 0:
                fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_rect.height)
                # Color gradient based on health
                col = C_SUCCESS if pct > 0.5 else (C_GOLD if pct > 0.25 else C_DANGER)
                draw_rounded_rect(surf, col, fill_rect, 5)
            
            # HP Number (shown when hovered - scale > 1.05)
            if current_scale > 1.05:
                f_hp = pygame.font.SysFont("Verdana", int(11 * current_scale), bold=True)
                hp_text = f"{self.hp}/{self.max_hp}"
                # Shadow
                t_hp_s = f_hp.render(hp_text, True, (0, 0, 0))
                surf.blit(t_hp_s, t_hp_s.get_rect(center=(bar_rect.centerx + 1, bar_rect.centery + 1)))
                # Main text
                t_hp = f_hp.render(hp_text, True, C_TEXT_MAIN)
                surf.blit(t_hp, t_hp.get_rect(center=bar_rect.center))
                
            # VP Badge (Floating Bubble)
            vp_pos = (cx + (40 * current_scale), cy - (45 * current_scale))
            draw_smooth_circle(surf, C_GOLD, vp_pos, 14 * current_scale)
            
            f_vp = pygame.font.SysFont("Verdana", int(14 * current_scale), bold=True)
            t_vp = f_vp.render(f"{self.vp}", True, (20, 20, 20))
            surf.blit(t_vp, t_vp.get_rect(center=vp_pos))
            
            # Name Tag
            try:
                f_nm = pygame.font.SysFont("segoeuiemoji", int(20 * current_scale), bold=True)
            except Exception:
                f_nm = pygame.font.SysFont("Segoe UI", int(20 * current_scale), bold=True)
            
            # Name shadow
            t_nm_s = f_nm.render(self.display_name, True, (0,0,0))
            surf.blit(t_nm_s, t_nm_s.get_rect(center=(int(cx) + 1, int(cy - (75 * current_scale)) + 1)))
            
            # Name main
            t_nm = f_nm.render(self.display_name, True, C_TEXT_MAIN)
            surf.blit(t_nm, t_nm.get_rect(center=(int(cx), int(cy - (75 * current_scale)))))

        else:
            f_d = pygame.font.SysFont("Verdana", int(16 * current_scale), bold=True)
            t_d = f_d.render("ELIMINATED", True, C_DANGER)
            surf.blit(t_d, t_d.get_rect(center=(int(cx), int(cy + 60 * current_scale))))


class Dice:
    """Visual dice component with rolling animation and juicy effects."""
    
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 110, 110)
        self.val = 6
        self.rolling = False
        self.timer = 0
        self.target = 1
        self.offset = [0, 0]
        self.hover_scale = 1.0
        self.rotation = 0

    def roll(self, target: int) -> None:
        """Start a roll animation with target value."""
        self.rolling = True
        self.timer = 40
        self.target = target

    def update(self, hover: bool) -> bool:
        """Update dice state. Returns True when roll animation completes."""
        # Interactive hover spring
        target_s = 1.15 if hover else 1.0
        self.hover_scale += (target_s - self.hover_scale) * 0.2

        if self.rolling:
            self.timer -= 1
            # Shake effect
            self.offset = [random.randint(-5, 5), random.randint(-5, 5)]
            if self.timer % 4 == 0:
                self.val = random.randint(1, 6)
                self.rotation = random.randint(-10, 10)
            
            if self.timer <= 0:
                self.rolling = False
                self.val = self.target
                self.offset = [0, 0]
                self.rotation = 0
                return True
        else:
            # Gentle float
            self.offset[1] = math.sin(pygame.time.get_ticks() * 0.003) * 5
            self.rotation *= 0.8
            
        return False

    def draw(self, surf: pygame.Surface) -> None:
        """Draw the dice on the surface."""
        cx, cy = self.rect.centerx + self.offset[0], self.rect.centery + self.offset[1]
        sz = int(110 * self.hover_scale)
        
        # Glow Effect on Hover/Roll
        if self.rolling or self.hover_scale > 1.01:
            pulse = 60 + int(math.sin(pygame.time.get_ticks() * 0.01) * 30)
            draw_smooth_circle(surf, (*C_ACCENT, pulse), (cx, cy), int(sz * 0.8))

        # Dice Surface (to handle rotation if we wanted, but keeping simple rect for crispness)
        # Using rounded rect with gradient-ish look
        main_rect = pygame.Rect(0, 0, sz, sz)
        main_rect.center = (cx, cy)
        
        # Body color - bright and "vanilla" white
        col = (250, 250, 255)
        if self.rolling:
            col = (230, 240, 255) # Slight blue tint when rolling
            
        draw_rounded_rect(surf, col, main_rect, 28)
        
        # Thick Border - "Goofy" style
        b_col = (180, 180, 200)
        if self.hover_scale > 1.05:
            b_col = C_ACCENT
            
        pygame.draw.rect(surf, b_col, main_rect, 4, border_radius=28)

        # Pips - large and friendly
        pip_col = (40, 45, 60)
        pip_sz = int(10 * self.hover_scale)
        space = int(28 * self.hover_scale)
        pips = []
        
        # Standard pip positions
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
            # Subtle pip shadow/inset
            pygame.draw.circle(surf, (200, 200, 220), (cx + dx * space + 1, cy + dy * space + 2), pip_sz)
            pygame.draw.circle(surf, pip_col, (cx + dx * space, cy + dy * space), pip_sz)

        # "ROLL" Hint
        if not self.rolling and self.hover_scale > 1.01:
            f = pygame.font.SysFont("Verdana", 12, bold=True)
            t = f.render("ROLL ME!", True, C_ACCENT)
            surf.blit(t, t.get_rect(center=(cx, main_rect.bottom + 20)))
