import sys
import math
import random
import pygame
import pygame.gfxdraw
import pygame_gui
from pathlib import Path

# ==================================================================
# 🔧 SETUP & CONSTANTS
# ==================================================================
try:
    pygame.init()
    pygame.mixer.init()
except AttributeError:
    pass 

# Configuration
DEFAULT_W, DEFAULT_H = 1280, 800
FPS = 60
MAX_ROUNDS = 10

# --- PATHS (Change BASE_DIR if your assets are elsewhere) ---
BASE_DIR = Path(".") 
IMG_DIR = BASE_DIR / "assets" / "images"
AUD_DIR = BASE_DIR / "assets" / "audios"

# --- PLAYER CONFIG ---
PLAYER_PROFILES = {
    0: {"name": "ASHIKA  👅",     "img": "ashika.jpg",      "audio": "ashika_asking.mp3"},
    1: {"name": "BIJAY SHAI  💀", "img": "bijay_shai.jpg",  "audio": "bijay_shai.mp3"},
    2: {"name": "GAMALA  🪴",    "img": "dhamala.jpg",     "audio": "dhamala.mp3"},
    3: {"name": "Khakar  💦",      "img": "sacar.jpg",       "audio": "sacar.mp3"},
    4: {"name": "DERE  🍑",      "img": "shere.jpg",       "audio": "shere.mp3"},
}

# --- MINIMALIST PRO THEME ---
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

# --- HELPER FUNCTIONS ---
def draw_rounded_rect(surf, color, rect, rad=10, alpha=255):
    """Draws a rounded rectangle with optional transparency."""
    shape = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shape, (*color, alpha), shape.get_rect(), border_radius=rad)
    surf.blit(shape, rect.topleft)

def draw_smooth_circle(surf, color, center, radius):
    """Draws a high-quality anti-aliased circle."""
    x, y = int(center[0]), int(center[1])
    radius = int(radius)
    pygame.gfxdraw.aacircle(surf, x, y, radius, color)
    pygame.gfxdraw.filled_circle(surf, x, y, radius, color)

def load_and_crop_avatar(filename, size):
    """Loads image, scales, and creates a circular surface."""
    path = IMG_DIR / filename
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    try:
        if not path.exists(): raise FileNotFoundError
        img = pygame.image.load(path).convert_alpha()
        # Scale keeping aspect ratio (cover)
        if img.get_width() < img.get_height():
            ratio = size / img.get_width()
        else:
            ratio = size / img.get_height()
        
        scaled = pygame.transform.smoothscale(img, (int(img.get_width()*ratio), int(img.get_height()*ratio)))
        
        # Center crop
        offset_x = (scaled.get_width() - size) // 2
        offset_y = (scaled.get_height() - size) // 2
        
        # Mask
        pygame.draw.circle(surf, (255, 255, 255), (size//2, size//2), size//2)
        surf.blit(scaled, (-offset_x, -offset_y), special_flags=pygame.BLEND_RGBA_MIN)
        
        # Add a subtle inner border
        pygame.draw.circle(surf, (255,255,255, 30), (size//2, size//2), size//2, 2)
        
    except Exception as e:
        # Fallback placeholder
        pygame.draw.circle(surf, (50, 50, 60), (size//2, size//2), size//2)
        f = pygame.font.SysFont("Arial", 40)
        t = f.render("?", True, (100,100,100))
        surf.blit(t, t.get_rect(center=(size//2, size//2)))
    
    return surf

# --- UI CLASSES ---

class LogFeed:
    """A sleek, modern history feed with card-style entries."""
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.messages = [] 
        self.font = pygame.font.SysFont("Verdana", 12)
        self.icon_font = pygame.font.SysFont("Segoe UI Symbol", 14)

    def add(self, text, color=C_TEXT_MAIN):
        # Format: (text_surf, color, anim_offset, alpha)
        surf = self.font.render(text, True, color)
        self.messages.insert(0, {"surf": surf, "col": color, "offset": -20, "alpha": 0, "life": 400})
        if len(self.messages) > 8: self.messages.pop()

    def draw(self, screen):
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
            if msg['offset'] < 0: msg['offset'] += 2
            if msg['alpha'] < 255: msg['alpha'] += 15
            
            y_pos = start_y + (i * 35)
            if y_pos > self.rect.bottom: break
            
            # Entry Background (Alternating subtle)
            row_rect = pygame.Rect(self.rect.x + 10, y_pos, self.rect.width - 20, 28)
            # draw_rounded_rect(screen, (40, 42, 50), row_rect, 6, 100 if i%2==0 else 50)
            
            # Text
            s = msg['surf'].copy()
            s.set_alpha(msg['alpha'])
            screen.blit(s, (self.rect.x + 20 + msg['offset'], y_pos + 6))
            
            # Bullet point
            pygame.draw.circle(screen, msg['col'], (self.rect.x + 12, y_pos + 14), 3)

        screen.set_clip(None)

class Player:
    def __init__(self, idx):
        self.idx = idx
        data = PLAYER_PROFILES.get(idx, {})
        self.name = data.get("name", f"P{idx}")
        self.hp = 20
        self.max_hp = 20
        self.vp = 0
        self.alive = True
        
        # Visuals
        self.pos = (0,0)
        self.base_size = 120
        self.rect = pygame.Rect(0,0, self.base_size, self.base_size)
        self.scale = 1.0
        self.avatar_surf = load_and_crop_avatar(data.get("img", ""), self.base_size)
        
        # Audio
        audio_path = AUD_DIR / data.get("audio", "")
        self.sound = None
        if audio_path.exists():
            try: self.sound = pygame.mixer.Sound(audio_path)
            except: pass

    def calculate_position(self, center, radius):
        angle = -90 + (self.idx * (360 / 5))
        rad = math.radians(angle)
        self.pos = (center[0] + radius * math.cos(rad), center[1] + radius * math.sin(rad))
        self.rect.center = self.pos

    def update(self, is_hovered):
        target = 1.15 if is_hovered else 1.0
        self.scale += (target - self.scale) * 0.15

    def draw(self, surf, is_active, is_target):
        cx, cy = self.pos
        s = self.scale
        
        # 0. Shadow
        shadow_r = int(self.base_size * s * 0.5)
        draw_smooth_circle(surf, (0,0,0,60), (cx, cy+5), shadow_r + 2)

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
            draw_smooth_circle(surf, (*C_ACCENT, 40), (cx, cy), pulse * s)

        # 3. Avatar
        if self.avatar_surf:
            final_size = int(self.base_size * s)
            scaled = pygame.transform.smoothscale(self.avatar_surf, (final_size, final_size))
            
            # Desaturate if dead
            if not self.alive:
                grayscale = pygame.Surface(scaled.get_size()).convert_alpha()
                grayscale.fill((20,20,25))
                scaled.blit(grayscale, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                
            r = scaled.get_rect(center=(cx, cy))
            surf.blit(scaled, r)
            
            # Crisp Ring Border
            pygame.draw.circle(surf, border_col, (cx, cy), (final_size//2), border_width)

        # 4. Modern Stats Badge
        if self.alive:
            # HP Bar pill
            bar_w = 70 * s
            bar_h = 14 * s
            bar_rect = pygame.Rect(0, 0, bar_w, bar_h)
            bar_rect.center = (cx, cy + (60*s))
            
            draw_rounded_rect(surf, (20,20,25), bar_rect, 6)
            
            pct = max(0, self.hp / self.max_hp)
            fill_w = int((bar_w-4) * pct)
            fill_rect = pygame.Rect(bar_rect.x+2, bar_rect.y+2, fill_w, bar_h-4)
            col = C_SUCCESS if pct > 0.4 else C_DANGER
            if fill_w > 0:
                pygame.draw.rect(surf, col, fill_rect, border_radius=4)
                
            # VP Badge
            vp_rect = pygame.Rect(0,0, 40*s, 20*s)
            vp_rect.center = (cx, cy - (65*s))
            draw_rounded_rect(surf, C_GOLD, vp_rect, 6)
            
            f_vp = pygame.font.SysFont("Verdana", int(12*s), bold=True)
            t_vp = f_vp.render(f"{self.vp} VP", True, (20,20,20))
            surf.blit(t_vp, t_vp.get_rect(center=vp_rect.center))
            
            # Name
            # Use Segoe UI Emoji to support special characters (reverts to monochrome in Pygame)
            try:
                f_nm = pygame.font.SysFont("segoeuiemoji", int(28*s), bold=True)
            except:
                f_nm = pygame.font.SysFont("Segoe UI", int(28*s), bold=True)
            
            t_nm = f_nm.render(self.name.upper(), True, C_TEXT_MAIN)
            surf.blit(t_nm, t_nm.get_rect(center=(cx, cy - (82*s))))

        else:
            f_d = pygame.font.SysFont("Verdana", int(14*s), bold=True)
            t_d = f_d.render("ELIMINATED", True, C_DANGER)
            surf.blit(t_d, t_d.get_rect(center=(cx, cy + 60*s)))

class Dice:
    def __init__(self):
        self.rect = pygame.Rect(0,0, 100, 100)
        self.val = 6
        self.rolling = False
        self.timer = 0
        self.target = 1
        self.offset = (0,0)
        self.hover_scale = 1.0

    def roll(self, target):
        self.rolling = True
        self.timer = 40
        self.target = target

    def update(self, hover):
        # Interactive hover spring
        target_s = 1.1 if hover else 1.0
        self.hover_scale += (target_s - self.hover_scale) * 0.2

        if self.rolling:
            self.timer -= 1
            self.offset = (random.randint(-2,2), random.randint(-2,2))
            if self.timer % 5 == 0: self.val = random.randint(1,6)
            if self.timer <= 0:
                self.rolling = False
                self.val = self.target
                self.offset = (0,0)
                return True
        return False

    def draw(self, surf):
        cx, cy = self.rect.centerx + self.offset[0], self.rect.centery + self.offset[1]
        sz = int(100 * self.hover_scale)
        
        # Glow Effect on Hover/Roll
        if self.rolling or self.hover_scale > 1.01:
             pulse = 50 + int(math.sin(pygame.time.get_ticks() * 0.01) * 20)
             draw_smooth_circle(surf, (*C_ACCENT, pulse), (cx, cy), sz * 0.7)

        # Shadow
        shadow_rect = pygame.Rect(0,0, sz, sz)
        shadow_rect.center = (cx, cy + 10)
        draw_rounded_rect(surf, (0,0,0), shadow_rect, 24, 60)

        # Body
        main_rect = pygame.Rect(0,0, sz, sz)
        main_rect.center = (cx, cy)
        col = (245, 245, 250) if not self.rolling else (220, 230, 255)
        
        draw_rounded_rect(surf, col, main_rect, 24)
        
        # Border
        b_col = (200,200,210) if not self.rolling else C_ACCENT
        pygame.draw.rect(surf, b_col, main_rect, 3, border_radius=24)

        # Pips
        pip_col = (40, 45, 60)
        pip_sz = 9
        space = 26
        pips = []
        if self.val == 1: pips = [(0,0)]
        elif self.val == 2: pips = [(-1,-1), (1,1)]
        elif self.val == 3: pips = [(-1,-1), (0,0), (1,1)]
        elif self.val == 4: pips = [(-1,-1), (1,-1), (-1,1), (1,1)]
        elif self.val == 5: pips = [(-1,-1), (1,-1), (-1,1), (1,1), (0,0)]
        elif self.val == 6: pips = [(-1,-1), (1,-1), (-1,1), (1,1), (-1,0), (1,0)]

        for dx, dy in pips:
            # Subtle pip shadow
            pygame.draw.circle(surf, (200,200,200), (cx + dx*space + 1, cy + dy*space + 1), pip_sz)
            pygame.draw.circle(surf, pip_col, (cx + dx*space, cy + dy*space), pip_sz)

        # "ROLL" Hint
        if not self.rolling and self.hover_scale > 1.01:
            f = pygame.font.SysFont("Verdana", 10, bold=True)
            t = f.render("ROLL", True, (100,100,100))
            surf.blit(t, t.get_rect(center=(cx, main_rect.bottom + 15)))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((DEFAULT_W, DEFAULT_H), pygame.RESIZABLE)
        pygame.display.set_caption("DO OR DICE // PRO")
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((DEFAULT_W, DEFAULT_H))
        
        self.voice_channel = pygame.mixer.Channel(0)

        # --- BGM SETUP ---
        # Plays bgm.mp3 from assets/audios/ if available
        try:
            bgm_path = AUD_DIR / "sansari_maya.mp3"
            if bgm_path.exists():
                pygame.mixer.music.load(str(bgm_path))
                pygame.mixer.music.set_volume(0.2)  # Volume (0.0 - 1.0)
                pygame.mixer.music.play(-1)         # Loop: -1 = infinite
            else:
                print(f"[BGM] Placeholder: Add 'bhajan.mp3' to {bgm_path}")
        except Exception as e:
            print(f"[BGM] Error: {e}")
        self.players = [Player(i) for i in range(5)]
        self.dice = Dice()
        self.log_feed = None
        
        self.round = 1
        self.turn = 0
        self.state = "IDLE"
        self.prompt = "WELCOME"
        self.sub_prompt = "Click the Dice to Start"
        self.payload = None
        self.particles = []
        self.buttons = []
        self.last_played_player = -1
        self.current_audio = None
        
        # Move Display
        self.move_display = None  # {"text": str, "color": tuple, "timer": int}
        
        # Audio & Background Extras
        self.audio_cooldown = 0
        self.bg_scroll = 0
        self.bg_particles = [[random.randint(0, DEFAULT_W), random.randint(0, DEFAULT_H), random.randint(1,3)] for _ in range(30)]
        
        self.layout(DEFAULT_W, DEFAULT_H)
        self.add_log("System Ready. Game Initialized.", C_SUCCESS)
        self.play_audio()
        
    def draw_bg(self):
        # 0. Base
        self.screen.fill(C_BG)
        
        # 1. Scrolling Grid
        self.bg_scroll = (self.bg_scroll + 0.2) % 60
        grid_sz = 60
        rows = self.h // grid_sz + 2
        cols = (self.w - 320) // grid_sz + 2
        
        for y in range(rows):
            pygame.draw.line(self.screen, C_GRID, (0, y*grid_sz + self.bg_scroll - 60), (self.w-340, y*grid_sz + self.bg_scroll - 60))
        for x in range(cols):
            pygame.draw.line(self.screen, C_GRID, (x*grid_sz, 0), (x*grid_sz, self.h))

        # 2. Ambient Particles
        for p in self.bg_particles:
            p[1] -= p[2] * 0.2 # Float up
            if p[1] < -10: 
                p[1] = self.h + 10
                p[0] = random.randint(0, self.w - 340)
            
            val = 50 + (p[2] * 40)
            pygame.draw.circle(self.screen, (val, val, val+20), (int(p[0]), int(p[1])), p[2])
            
        # 3. Vignette Overlay (Simulated)
        # Using a few big circles with low alpha on the corners/edges
        v = pygame.Surface((self.w - 340, self.h), pygame.SRCALPHA)
        pygame.draw.rect(v, (5, 5, 10, 80), v.get_rect()) # Dim everything slightly
        # Center glow cutout (by drawing darker around) - simple approach: just draw dark corners
        self.screen.blit(v, (0,0))


    def layout(self, w, h):
        self.manager.set_window_resolution((w, h))
        self.w, self.h = w, h
        
        # Sidebar is fixed 320px on the right
        self.sidebar_rect = pygame.Rect(w - 340, 0, 340, h)
        self.arena_rect = pygame.Rect(0, 0, w - 340, h)
        
        # Positioning Players
        cx, cy = self.arena_rect.center
        rad = min(self.arena_rect.width, self.arena_rect.height) * 0.35
        for p in self.players: p.calculate_position((cx, cy), rad)
        self.dice.rect.center = (cx, cy)
        
        # Log Feed in Sidebar (Bottom)
        self.log_feed = LogFeed(self.sidebar_rect.x + 20, h - 350, 300, 330)

    def add_log(self, text, col=C_TEXT_MAIN):
        if self.log_feed: self.log_feed.add(text, col)

    def create_buttons(self, labels, actions):
        """Creates minimal styling buttons manually or via GUI manager."""
        # Clean old buttons
        for b in self.buttons: b.kill()
        self.buttons = []
        
        start_y = 120
        for i, lbl in enumerate(labels):
            rect = pygame.Rect(self.sidebar_rect.x + 20, start_y + (i * 45), 300, 38)
            # We use standard pygame_gui buttons but could skin them
            btn = pygame_gui.elements.UIButton(relative_rect=rect, text=lbl, manager=self.manager)
            btn.action = actions[i]
            self.buttons.append(btn)

    def play_audio(self, force=False):
        p = self.players[self.turn]
        
        # Logic to only play if new player turn OR forced loop
        if self.last_played_player != p.idx or force:
            self.last_played_player = p.idx
            if self.voice_channel.get_busy(): self.voice_channel.stop()
            if p.sound: self.voice_channel.play(p.sound)

    # --- LOGIC ---
    def roll_dice(self):
        self.state = "ROLLING"
        p = self.players[self.turn]
        # Restart audio cooldown prevent double loop immediately
        self.voice_channel.stop()
        self.last_played_player = -1 # Force replay next time if needed
        self.play_audio()
        
        roll = random.randint(1, 6)
        
        # Rules Logic
        live_rules = {
            1: ("BACKFIRE", "Take 3 DMG", C_DANGER, "self_dmg", 3),
            2: ("JAB", "Deal 2 DMG", C_TEXT_MAIN, "target_dmg", 2),
            3: ("PICKPOCKET", "Steal 1 VP", C_PURPLE, "steal", 1),
            4: ("STRIKE", "Deal 4 DMG", C_TEXT_MAIN, "target_dmg", 4),
            5: ("RECOVER", "Heal 3 HP", C_SUCCESS, "heal", 3),
            6: ("POWER MOVE", "Choice: DMG or VP", C_GOLD, "choice", 0)
        }
        dead_rules = {
            1: ("VOID MIST", "No Effect", C_TEXT_DIM, "none", 0),
            2: ("VOID MIST", "No Effect", C_TEXT_DIM, "none", 0),
            3: ("SPIRIT BLESS", "Buff a Player", C_SUCCESS, "buff", 0),
            4: ("SPIRIT BLESS", "Buff a Player", C_SUCCESS, "buff", 0),
            5: ("HAUNT", "Curse a Player", C_DANGER, "curse", 0),
            6: ("HAUNT", "Curse a Player", C_DANGER, "curse", 0)
        }
        
        r = live_rules[roll] if p.alive else dead_rules[roll]
        
        self.dice.roll(roll)
        self.prompt = r[0]
        self.sub_prompt = r[1]
        self.payload = {"type": r[3], "val": r[4], "color": r[2]}

    def finish_roll(self):
        p = self.players[self.turn]
        act = self.payload['type']
        val = self.payload['val']
        col = self.payload['color']
        
        # Display move on screen
        self.move_display = {"text": self.prompt, "color": col, "timer": 120}
        
        self.add_log(f"{p.name} rolled {self.dice.val}", col)
        
        if act == "self_dmg":
            p.hp = max(0, p.hp - val)
            self.add_particle(p.pos, f"-{val}", C_DANGER)
            if p.hp == 0: 
                p.alive = False
                self.add_log(f"{p.name} DIED!", C_DANGER)
            self.next_turn()
        
        elif act == "heal":
            p.hp = min(p.max_hp, p.hp + val)
            self.add_particle(p.pos, f"+{val}", C_SUCCESS)
            self.next_turn()
            
        elif act == "target_dmg":
            self.state = "TARGET"
            self.sub_prompt = f"Select Target for {val} DMG"
            
        elif act == "steal":
            self.state = "TARGET"
            self.sub_prompt = "Select Target to Steal VP"
            
        elif act == "choice":
            self.state = "CHOICE"
            self.create_buttons(["DEAL 6 DMG", "GAIN 3 VP"], ["dmg_6", "vp_3"])
            
        elif act == "buff":
            self.state = "TARGET_FALLEN"
            self.sub_prompt = "Select Alive Player to Bless"
            
        elif act == "curse":
            self.state = "TARGET_FALLEN"
            self.sub_prompt = "Select Alive Player to Curse"
            
        elif act == "none":
            self.next_turn()

    def handle_target(self, target):
        actor = self.players[self.turn]
        
        # Validate selection
        if self.state == "TARGET":
            if not target.alive or target == actor: return
        elif self.state == "TARGET_FALLEN":
            if not target.alive: return

        act = self.payload['type']
        val = self.payload['val']

        if act == "target_dmg" or (act == "choice" and val == 6):
            target.hp = max(0, target.hp - val)
            self.add_particle(target.pos, f"-{val}", C_DANGER)
            if target.hp == 0:
                target.alive = False
                self.add_log(f"{target.name} ELIMINATED", C_DANGER)
                if actor.alive: actor.vp += 2
        
        elif act == "steal":
            amt = 1 if target.vp > 0 else 0
            target.vp -= amt
            actor.vp += amt
            self.add_particle(target.pos, f"-{amt}VP", C_DANGER)
            self.add_particle(actor.pos, f"+{amt}VP", C_GOLD)
            
        elif act == "buff":
            target.hp = min(target.max_hp, target.hp + 2)
            self.add_particle(target.pos, "+2 HP", C_SUCCESS)
            
        elif act == "curse":
            target.hp = max(0, target.hp - 2)
            self.add_particle(target.pos, "-2 HP", C_DANGER)

        self.next_turn()

    def handle_choice(self, action_id):
        actor = self.players[self.turn]
        
        for b in self.buttons: b.kill()
        self.buttons = []
        
        if action_id == "vp_3":
            actor.vp += 3
            self.add_particle(actor.pos, "+3 VP", C_GOLD)
            self.next_turn()
        elif action_id == "dmg_6":
            self.state = "TARGET"
            self.payload['type'] = "choice"
            self.payload['val'] = 6
            self.sub_prompt = "Select Target for 6 DMG"

    def next_turn(self):
        self.turn += 1
        if self.turn >= 5:
            self.round += 1
            self.turn = 0
            self.add_log(f"--- ROUND {self.round} START ---", C_TEXT_DIM)
            # Living Bonus
            alive_count = 0
            for p in self.players:
                if p.alive:
                    p.vp += 1
                    alive_count += 1
            if alive_count <= 1 or self.round > MAX_ROUNDS:
                self.game_over()
                return

        self.state = "IDLE"
        active = self.players[self.turn]
        
        # Skip dead players roll logic usually, but keep them for 'ghost' turns
        self.dice.val = 6 # Reset dice visual
        self.prompt = f"{active.name}'S TURN"
        self.sub_prompt = "Click Dice to Roll"
        
        if not active.alive:
            self.sub_prompt = "Ghost Turn - Click Dice"
        
        self.play_audio()

    def game_over(self):
        self.state = "GAME_OVER"
        self.prompt = "GAME OVER"
        self.sub_prompt = "See Standings"
        self.create_buttons(["RESTART GAME"], ["restart"])
        
        # Sort winners
        ranked = sorted(self.players, key=lambda x: (x.alive, x.vp, x.hp), reverse=True)
        self.add_log("--- FINAL STANDINGS ---", C_GOLD)
        for i, p in enumerate(ranked):
            status = "ALIVE" if p.alive else "DEAD"
            self.add_log(f"#{i+1} {p.name}: {p.vp}VP ({status})", C_TEXT_MAIN)

    def add_particle(self, pos, text, col):
        self.particles.append({"pos": list(pos), "vel": [random.uniform(-1,1), -2], "text": text, "col": col, "life": 60})

    def run(self):
        font_big = pygame.font.SysFont("Consolas", 32, bold=True)
        font_small = pygame.font.SysFont("Consolas", 14)
        font_particle = pygame.font.SysFont("Arial", 20, bold=True)

        while True:
            dt = self.clock.tick(FPS) / 1000.0
            mx, my = pygame.mouse.get_pos()
            
            # --- EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.VIDEORESIZE: self.layout(event.w, event.h)
                
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element.action == "restart": 
                        self.__init__() # Cheat restart
                    else:
                        self.handle_choice(event.ui_element.action)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "IDLE" and self.dice.rect.collidepoint((mx,my)):
                        self.roll_dice()
                    elif "TARGET" in self.state:
                        for p in self.players:
                            if p.rect.collidepoint((mx,my)): self.handle_target(p)

                self.manager.process_events(event)

            # --- UPDATES ---
            # Calculate dice hover ONCE
            dice_hover = self.dice.rect.collidepoint((mx,my))
            
            if self.state == "ROLLING":
                if self.dice.update(dice_hover): self.finish_roll()
            else:
                # Update hover state when not rolling
                self.dice.update(dice_hover)
            
            for p in self.players: p.update(p.rect.collidepoint((mx,my)))
            
            # --- AUDIO LOOP LOGIC ---
            # If waiting for roll and audio finished
            if self.state == "IDLE" and not self.voice_channel.get_busy():
                self.audio_cooldown += dt
                if self.audio_cooldown > 1.0: # 1 Second Delay
                    self.play_audio(force=True)
                    self.audio_cooldown = 0
            else:
                 self.audio_cooldown = 0
                 
            self.manager.update(dt)

            # --- DRAW ---
            self.draw_bg()
            
            # 1. Sidebar Background & Decor
            pygame.draw.rect(self.screen, C_SIDEBAR, self.sidebar_rect)
            pygame.draw.line(self.screen, C_LINE, (self.sidebar_rect.x, 0), (self.sidebar_rect.x, self.h))
            
            # Sidebar Header Band
            pygame.draw.rect(self.screen, C_PANEL, (self.sidebar_rect.x, 0, self.sidebar_rect.width, 90))
            pygame.draw.line(self.screen, C_LINE, (self.sidebar_rect.x, 90), (self.w, 90))

            # 2. Connection Lines (Arena)
            cx, cy = self.arena_rect.center
            active_p = self.players[self.turn]
            if self.state != "GAME_OVER":
                # Pulse line
                alpha = 100 + int(math.sin(pygame.time.get_ticks() * 0.005) * 50)
                # Draw varied width line
                if active_p.alive:
                    color_line = (*C_ACCENT, alpha)
                    line_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
                    pygame.draw.line(line_surf, color_line, (cx, cy), active_p.pos, 3)
                    self.screen.blit(line_surf, (0,0))
                else:
                    pygame.draw.line(self.screen, (30,30,35), (cx, cy), active_p.pos, 2)

            # 3. Dice
            self.dice.draw(self.screen)

            # 4. Players
            for p in self.players:
                is_active = (p.idx == self.turn)
                is_target = False
                if "TARGET" in self.state:
                    if self.state == "TARGET_FALLEN": is_target = not p.alive
                    else: is_target = (p.alive and p.idx != self.turn)
                
                p.draw(self.screen, is_active, is_target)
            
            # 4.5 Move Display (Modern & Minimal)
            if self.move_display:
                self.move_display['timer'] -= 1
                if self.move_display['timer'] <= 0:
                    self.move_display = None
                else:
                    # Fade effect
                    alpha = int((self.move_display['timer'] / 120) * 255)
                    
                    # Minimal Text above dice
                    font_move = pygame.font.SysFont("Verdana", 48, bold=True)
                    txt = self.move_display['text'].upper()
                    
                    # Shadow
                    move_surf_s = font_move.render(txt, True, (0,0,0))
                    move_surf_s.set_alpha(max(0, alpha-50))
                    r_s = move_surf_s.get_rect(center=(cx+2, cy - 128))
                    self.screen.blit(move_surf_s, r_s)
                    
                    # Main Text
                    move_surf = font_move.render(txt, True, self.move_display['color'])
                    move_surf.set_alpha(alpha)
                    r_m = move_surf.get_rect(center=(cx, cy - 130))
                    self.screen.blit(move_surf, r_m)

            # 5. Sidebar UI Elements
            
            # A) Header / Prompt Area
            t1 = font_big.render(self.prompt, True, C_TEXT_MAIN)
            t2 = font_small.render(self.sub_prompt, True, C_ACCENT)
            sx = self.sidebar_rect.x + 20
            self.screen.blit(t1, (sx, 20))
            self.screen.blit(t2, (sx, 56))
            
            # B) Turn/Round Indicator Pill (Top Right of sidebar)
            round_pill = pygame.Rect(self.w - 100, 25, 80, 28)
            draw_rounded_rect(self.screen, (30, 32, 40), round_pill, 8, 255)
            tr = font_particle.render(f"RND {self.round}", True, C_GOLD)
            self.screen.blit(tr, tr.get_rect(center=round_pill.center))
            
            # C) Player Stats Panel (Card Style)
            stats_y = 110
            
            for i, p in enumerate(self.players):
                card_h = 50
                card_y = stats_y + (i * (card_h + 10))
                card_rect = pygame.Rect(self.sidebar_rect.x + 15, card_y, 310, card_h)
                
                # Card Background
                bg_col = (25, 27, 33) if p.alive else (15, 15, 18)
                border_c = C_ACCENT if p.idx == self.turn else (40, 42, 50)
                border_w = 2 if p.idx == self.turn else 1
                
                draw_rounded_rect(self.screen, bg_col, card_rect, 8)
                pygame.draw.rect(self.screen, border_c, card_rect, border_w, border_radius=8)
                
                # Content
                # 1. Name
                nm_col = C_TEXT_MAIN if p.alive else C_TEXT_DIM
                nm_font = pygame.font.SysFont("Verdana", 13, bold=True)
                nm_surf = nm_font.render(p.name, True, nm_col)
                self.screen.blit(nm_surf, (card_rect.x + 12, card_rect.y + 8))
                
                # 2. HP Bar
                bar_bg = pygame.Rect(card_rect.x + 12, card_rect.y + 30, 180, 8)
                pygame.draw.rect(self.screen, (10, 10, 15), bar_bg, border_radius=4)
                
                if p.alive:
                    pct = max(0, p.hp / p.max_hp)
                    fill_w = int(180 * pct)
                    fill_rect = pygame.Rect(card_rect.x + 12, card_rect.y + 30, fill_w, 8)
                    hp_col = C_SUCCESS if pct > 0.4 else C_DANGER
                    pygame.draw.rect(self.screen, hp_col, fill_rect, border_radius=4)
                
                # 3. VP Badge
                vp_surf = font_particle.render(f"{p.vp}", True, C_GOLD)
                # Star icon (simple circle for now)
                pygame.draw.circle(self.screen, (50, 45, 20), (card_rect.right - 35, card_rect.centery), 16)
                pygame.draw.circle(self.screen, C_GOLD, (card_rect.right - 35, card_rect.centery), 16, 2)
                self.screen.blit(vp_surf, vp_surf.get_rect(center=(card_rect.right - 35, card_rect.centery)))

            # D) Log Feed
            if self.log_feed: self.log_feed.draw(self.screen)

            # 6. Particles
            for part in self.particles[:]:
                part['pos'][0] += part['vel'][0]
                part['pos'][1] += part['vel'][1]
                part['life'] -= 1
                if part['life'] <= 0: self.particles.remove(part); continue
                
                # Shadow first
                pt_s = font_particle.render(part['text'], True, (0,0,0))
                pt_s.set_alpha(int((part['life']/60)*100))
                self.screen.blit(pt_s, (part['pos'][0]+1, part['pos'][1]+1))
                
                pt = font_particle.render(part['text'], True, part['col'])
                pt.set_alpha(int((part['life']/60)*255))
                self.screen.blit(pt, part['pos'])

            self.manager.draw_ui(self.screen)
            pygame.display.flip()

if __name__ == "__main__":
    Game().run()