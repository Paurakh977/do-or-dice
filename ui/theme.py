"""
Theme constants and helper functions for the DO OR DICE UI.
Replicates the minimalist pro theme from the prototype.
"""
import pygame
import pygame.gfxdraw
from pathlib import Path

# ==================================================================
# 🔧 PATHS
# ==================================================================
BASE_DIR = Path(__file__).parent.parent
IMG_DIR = BASE_DIR / "assets" / "images"
AUD_DIR = BASE_DIR / "assets" / "audios"

# ==================================================================
# 🎨 MINIMALIST PRO THEME
# ==================================================================
C_BG        = (10, 12, 18)       # Darker Deep Space
C_SIDEBAR   = (15, 17, 22)       # Sidebar BG
C_PANEL     = (25, 27, 35)       # Inner Panels/Cards
C_GRID      = (30, 35, 50)       # Grid Lines
C_LINE      = (40, 42, 50)       # Borders
C_TEXT_MAIN = (235, 240, 245)    # Primary Text
C_TEXT_DIM  = (130, 135, 145)    # Secondary Text
C_ACCENT    = (60, 130, 240)     # Electric Blue
C_DANGER    = (235, 80, 85)      # Coral Red
C_SUCCESS   = (70, 200, 150)     # Seafoam Green
C_GOLD      = (245, 195, 60)     # Amber
C_PURPLE    = (160, 110, 235)    # Iris
C_SHADOW    = (0, 0, 0, 80)      # Alpha Shadow

# ==================================================================
# 🔧 HELPER FUNCTIONS
# ==================================================================

def draw_rounded_rect(surf: pygame.Surface, color: tuple, rect: pygame.Rect, rad: int = 10, alpha: int = 255) -> None:
    """Draws a rounded rectangle with optional transparency."""
    shape = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shape, (*color[:3], alpha), shape.get_rect(), border_radius=rad)
    surf.blit(shape, rect.topleft)


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
        # Fallback placeholder
        pygame.draw.circle(surf, (50, 50, 60), (size // 2, size // 2), size // 2)
        f = pygame.font.SysFont("Arial", 40)
        t = f.render("?", True, (100, 100, 100))
        surf.blit(t, t.get_rect(center=(size // 2, size // 2)))
    
    return surf

