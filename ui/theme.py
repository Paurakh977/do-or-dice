"""
Theme constants and helper functions for the DO OR DICE UI.
Replicates the minimalist pro theme from the prototype.
"""
import pygame
import pygame.gfxdraw
import sys
from pathlib import Path

# ==================================================================
# 🔧 PATHS
# ==================================================================
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Running in a normal Python environment
    BASE_DIR = Path(__file__).parent.parent

IMG_DIR = BASE_DIR / "assets" / "images"
AUD_DIR = BASE_DIR / "assets" / "audios"

# ==================================================================
# 🎨 LUXURY / MODERN THEME
# ==================================================================
# Deep, rich background colors
C_BG_TOP      = (15, 12, 25)       # Deep violet-black
C_BG_BOTTOM   = (5, 5, 10)         # Near black

C_SIDEBAR     = (20, 20, 28)       # Dark slate
C_PANEL       = (35, 35, 45)       # Lighter panel
C_GRID        = (40, 40, 60)       # Subtle purple-tinted grid
C_LINE        = (60, 60, 80)       # Borders

# Typography
C_TEXT_MAIN   = (240, 240, 250)    # Off-white
C_TEXT_DIM    = (150, 150, 170)    # Dimmed lavender-grey

# Accents - Vibrant and "Fun"
C_ACCENT      = (100, 100, 255)    # Neon Blue
C_ACCENT_GLOW = (100, 100, 255, 100) # Glow for accent
C_DANGER      = (255, 80, 100)     # Hot Coral
C_SUCCESS     = (50, 220, 150)     # Mint Green
C_GOLD        = (255, 215, 0)      # Pure Gold
C_PURPLE      = (180, 100, 255)    # Electric Purple
C_PINK        = (255, 105, 180)    # Hot Pink (for "goofy/cute" vibes)

C_SHADOW      = (0, 0, 0, 100)     # Stronger shadow for depth

# ==================================================================
# 🔧 HELPER FUNCTIONS
# ==================================================================

def draw_rounded_rect(surf: pygame.Surface, color: tuple, rect: pygame.Rect, rad: int = 10, alpha: int = 255) -> None:
    """Draws a rounded rectangle with optional transparency."""
    if alpha < 255:
        shape = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shape, (*color[:3], alpha), shape.get_rect(), border_radius=rad)
        surf.blit(shape, rect.topleft)
    else:
        pygame.draw.rect(surf, color, rect, border_radius=rad)


def draw_glass_rect(surf: pygame.Surface, rect: pygame.Rect, rad: int = 10) -> None:
    """Draws a modern glassmorphism-style rectangle."""
    # Base semi-transparent white/blue layer
    shape = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shape, (30, 35, 50, 180), shape.get_rect(), border_radius=rad)
    
    # Subtle top highlight (simulate light source)
    pygame.draw.line(shape, (255, 255, 255, 50), (rad, 1), (rect.width - rad, 1), 1)
    
    surf.blit(shape, rect.topleft)
    # Border
    pygame.draw.rect(surf, (100, 100, 120), rect, 1, border_radius=rad)


def draw_gradient_bg(surf: pygame.Surface) -> None:
    """Fills the surface with a vertical gradient."""
    h = surf.get_height()
    w = surf.get_width()
    # Create a small surface to draw the gradient on, then scale it up (optimization)
    grad_surf = pygame.Surface((1, h))
    
    # Interpolate
    r1, g1, b1 = C_BG_TOP
    r2, g2, b2 = C_BG_BOTTOM
    
    for y in range(h):
        r = r1 + (r2 - r1) * y / h
        g = g1 + (g2 - g1) * y / h
        b = b1 + (b2 - b1) * y / h
        pygame.draw.line(grad_surf, (int(r), int(g), int(b)), (0, y), (1, y))
    
    scaled = pygame.transform.scale(grad_surf, (w, h))
    surf.blit(scaled, (0, 0))


def draw_smooth_circle(surf: pygame.Surface, color: tuple, center: tuple, radius: int) -> None:
    """Draws a high-quality anti-aliased circle."""
    x, y = int(center[0]), int(center[1])
    radius = int(radius)
    if radius <= 0:
        return
    # Handle alpha colors
    if len(color) == 4:
        temp = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
        pygame.gfxdraw.aacircle(temp, radius + 1, radius + 1, radius, color)
        pygame.gfxdraw.filled_circle(temp, radius + 1, radius + 1, radius, color)
        surf.blit(temp, (x - radius - 1, y - radius - 1))
    else:
        pygame.gfxdraw.aacircle(surf, x, y, radius, color)
        pygame.gfxdraw.filled_circle(surf, x, y, radius, color)


def load_and_crop_avatar(filename: str, size: int) -> pygame.Surface:
    """Loads image, scales, and creates a circular surface."""
    path = IMG_DIR / filename
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    try:
        if not path.exists():
            raise FileNotFoundError
        img = pygame.image.load(str(path)).convert_alpha()
        # Scale keeping aspect ratio (cover)
        if img.get_width() < img.get_height():
            ratio = size / img.get_width()
        else:
            ratio = size / img.get_height()
        
        scaled = pygame.transform.smoothscale(img, (int(img.get_width() * ratio), int(img.get_height() * ratio)))
        
        # Center crop
        offset_x = (scaled.get_width() - size) // 2
        offset_y = (scaled.get_height() - size) // 2
        
        # Mask
        pygame.draw.circle(surf, (255, 255, 255), (size // 2, size // 2), size // 2)
        surf.blit(scaled, (-offset_x, -offset_y), special_flags=pygame.BLEND_RGBA_MIN)
        
        # Add a subtle inner border
        pygame.draw.circle(surf, (255, 255, 255, 30), (size // 2, size // 2), size // 2, 2)
        
    except Exception:
        # Fallback placeholder - colorful!
        import random
        base_hue = random.randint(0, 360)
        c = pygame.Color(0)
        c.hsla = (base_hue, 60, 50, 100)
        pygame.draw.circle(surf, c, (size // 2, size // 2), size // 2)
        
        f = pygame.font.SysFont("Arial", 40, bold=True)
        t = f.render("?", True, (255, 255, 255))
        surf.blit(t, t.get_rect(center=(size // 2, size // 2)))
    
    return surf
