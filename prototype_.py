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
    0: {"name": "ASHIKA",     "img": "ashika.jpg",      "audio": "ashika_asking.mp3"},
    1: {"name": "BIJAY SHAI", "img": "bijay_shai.jpg",  "audio": "bijay_shai.mp3"},
    2: {"name": "DHAMALA",    "img": "dhamala.jpg",     "audio": "dhamala.mp3"},
    3: {"name": "SACAR",      "img": "sacar.jpg",       "audio": "sacar.mp3"},
    4: {"name": "SHERE",      "img": "shere.jpg",       "audio": "shere.mp3"},
}

# --- MINIMALIST PALETTE ---
C_BG        = (15, 17, 26)       # Deep Midnight (Background)
C_SIDEBAR   = (20, 23, 34)       # Sidebar Background
C_LINE      = (40, 44, 52)       # Subtle dividers
C_TEXT_MAIN = (230, 236, 240)    # White-ish
C_TEXT_DIM  = (100, 110, 130)    # Grey-ish
C_ACCENT    = (110, 140, 250)    # Soft Blue
C_DANGER    = (235, 90, 90)      # Soft Red
C_SUCCESS   = (80, 210, 160)     # Soft Mint
C_GOLD      = (240, 200, 80)     # Soft Gold
C_PURPLE    = (180, 130, 250)    # Soft Purple

# --- HELPER FUNCTIONS ---
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
    """A custom, minimal log rendering system (Replace UITextBox)."""
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.messages = [] # List of (text_surf, alpha, y_pos)
        self.font = pygame.font.SysFont("Consolas", 14)

    def add(self, text, color=C_TEXT_MAIN):
        # Render text immediately
        surf = self.font.render(text, True, color)
        self.messages.insert(0, {"surf": surf, "alpha": 255, "life": 300})
        if len(self.messages) > 12: self.messages.pop()

    def draw(self, screen):
        # Draw messages from bottom up
        curr_y = self.rect.bottom - 25
        
        for msg in self.messages:
            if curr_y < self.rect.top: break
            
            # Fade logic
            msg['life'] -= 1
            if msg['life'] < 50: msg['alpha'] = int((msg['life']/50) * 255)
            
            s = msg['surf'].copy()
            s.set_alpha(msg['alpha'])
            screen.blit(s, (self.rect.x, curr_y))
            curr_y -= 22 # Line height

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
        self.base_size = 110
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
        target = 1.1 if is_hovered else 1.0
        self.scale += (target - self.scale) * 0.15

    def draw(self, surf, is_active, is_target):
        cx, cy = self.pos
        s = self.scale
        
        # 1. State Colors
        border_col = C_LINE
        if not self.alive: 
            border_col = (30, 30, 30)
            self.scale = 0.9 # Shrink dead
        elif is_active: border_col = C_ACCENT
        elif is_target: border_col = C_DANGER

        # 2. Draw Active Pulse / Glow
        if is_active and self.alive:
            pulse = 60 + math.sin(pygame.time.get_ticks() * 0.005) * 5
            draw_smooth_circle(surf, (*C_ACCENT, 30), (cx, cy), pulse * s)

        # 3. Avatar
        if self.avatar_surf:
            final_size = int(self.base_size * s)
            scaled = pygame.transform.smoothscale(self.avatar_surf, (final_size, final_size))
            
            # Grayscale if dead
            if not self.alive:
                grayscale = pygame.Surface(scaled.get_size()).convert_alpha()
                grayscale.fill((30,30,30))
                scaled.blit(grayscale, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                
            r = scaled.get_rect(center=(cx, cy))
            surf.blit(scaled, r)
            
            # Ring Border
            pygame.draw.circle(surf, border_col, (cx, cy), (final_size//2) + 2, 2)

        # 4. Health Bar (Underneath)
        if self.alive:
            bar_w = 80 * s
            bar_h = 6
            bar_rect = pygame.Rect(cx - bar_w/2, cy + 65*s, bar_w, bar_h)
            
            # Background
            pygame.draw.rect(surf, (30,33,40), bar_rect, border_radius=3)
            # Foreground
            pct = max(0, self.hp / self.max_hp)
            fill_rect = pygame.Rect(cx - bar_w/2, cy + 65*s, bar_w * pct, bar_h)
            col = C_SUCCESS if pct > 0.4 else C_DANGER
            pygame.draw.rect(surf, col, fill_rect, border_radius=3)

        # 5. Text Stats
        font = pygame.font.SysFont("Consolas", int(12*s), bold=True)
        
        # Name (Top)
        name_surf = font.render(self.name, True, C_TEXT_MAIN if self.alive else C_TEXT_DIM)
        surf.blit(name_surf, name_surf.get_rect(center=(cx, cy - 70*s)))
        
        # Stats (Bottom)
        if self.alive:
            stat_surf = font.render(f"{self.hp}HP | {self.vp}VP", True, C_TEXT_DIM)
            surf.blit(stat_surf, stat_surf.get_rect(center=(cx, cy + 80*s)))
        else:
            dead_surf = font.render("ELIMINATED", True, C_DANGER)
            surf.blit(dead_surf, dead_surf.get_rect(center=(cx, cy + 80*s)))

class Dice:
    def __init__(self):
        self.rect = pygame.Rect(0,0, 100, 100)
        self.val = 6
        self.rolling = False
        self.timer = 0
        self.target = 1
        self.offset = (0,0)

    def roll(self, target):
        self.rolling = True
        self.timer = 40
        self.target = target

    def update(self):
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

    def draw(self, surf, hover):
        cx, cy = self.rect.centerx + self.offset[0], self.rect.centery + self.offset[1]
        sz = 90 if not hover else 95 # Subtle hover grow
        
        # Shadow
        shadow_rect = pygame.Rect(0,0, sz, sz)
        shadow_rect.center = (cx, cy + 5)
        pygame.draw.rect(surf, (10,10,12), shadow_rect, border_radius=18)

        # Body
        main_rect = pygame.Rect(0,0, sz, sz)
        main_rect.center = (cx, cy)
        col = C_TEXT_MAIN if not self.rolling else C_ACCENT
        pygame.draw.rect(surf, col, main_rect, border_radius=18)

        # Pips
        pip_col = C_BG
        pip_sz = 8
        space = 24
        pips = []
        if self.val == 1: pips = [(0,0)]
        elif self.val == 2: pips = [(-1,-1), (1,1)]
        elif self.val == 3: pips = [(-1,-1), (0,0), (1,1)]
        elif self.val == 4: pips = [(-1,-1), (1,-1), (-1,1), (1,1)]
        elif self.val == 5: pips = [(-1,-1), (1,-1), (-1,1), (1,1), (0,0)]
        elif self.val == 6: pips = [(-1,-1), (1,-1), (-1,1), (1,1), (-1,0), (1,0)]

        for dx, dy in pips:
            pygame.draw.circle(surf, pip_col, (cx + dx*space, cy + dy*space), pip_sz)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((DEFAULT_W, DEFAULT_H), pygame.RESIZABLE)
        pygame.display.set_caption("DO OR DICE // MINIMAL")
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((DEFAULT_W, DEFAULT_H))
        
        self.voice_channel = pygame.mixer.Channel(0)
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
        
        self.layout(DEFAULT_W, DEFAULT_H)
        self.add_log("System Ready. Game Initialized.", C_SUCCESS)
        self.play_audio()

    def layout(self, w, h):
        self.manager.set_window_resolution((w, h))
        self.w, self.h = w, h
        
        # Sidebar is fixed 300px on the right
        self.sidebar_rect = pygame.Rect(w - 320, 0, 320, h)
        self.arena_rect = pygame.Rect(0, 0, w - 320, h)
        
        # Positioning Players
        cx, cy = self.arena_rect.center
        rad = min(self.arena_rect.width, self.arena_rect.height) * 0.35
        for p in self.players: p.calculate_position((cx, cy), rad)
        self.dice.rect.center = (cx, cy)
        
        # Log Feed in Sidebar
        self.log_feed = LogFeed(self.sidebar_rect.x + 20, h - 300, 280, 280)

    def add_log(self, text, col=C_TEXT_MAIN):
        if self.log_feed: self.log_feed.add(text, col)

    def create_buttons(self, labels, actions):
        """Creates minimal styling buttons manually or via GUI manager."""
        # Clean old buttons
        for b in self.buttons: b.kill()
        self.buttons = []
        
        start_y = 150
        for i, lbl in enumerate(labels):
            rect = pygame.Rect(self.sidebar_rect.x + 20, start_y + (i * 50), 280, 40)
            btn = pygame_gui.elements.UIButton(relative_rect=rect, text=lbl, manager=self.manager)
            btn.action = actions[i]
            self.buttons.append(btn)

    def play_audio(self):
        p = self.players[self.turn]
        if self.voice_channel.get_busy(): self.voice_channel.stop()
        if p.sound: self.voice_channel.play(p.sound)

    # --- LOGIC ---
    def roll_dice(self):
        self.state = "ROLLING"
        p = self.players[self.turn]
        self.play_audio()
        
        roll = random.randint(1, 6)
        
        # Rules Logic
        live_rules = {
            1: ("CRITICAL FAIL", "Take 3 DMG", C_DANGER, "self_dmg", 3),
            2: ("QUICK JAB", "Deal 2 DMG", C_TEXT_MAIN, "target_dmg", 2),
            3: ("THIEF", "Steal 1 VP", C_PURPLE, "steal", 1),
            4: ("HEAVY STRIKE", "Deal 4 DMG", C_TEXT_MAIN, "target_dmg", 4),
            5: ("REGENERATE", "Heal 3 HP", C_SUCCESS, "heal", 3),
            6: ("ULTIMATE", "Choice: DMG or VP", C_GOLD, "choice", 0)
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
            if self.state == "ROLLING":
                if self.dice.update(): self.finish_roll()
            
            for p in self.players: p.update(p.rect.collidepoint((mx,my)))
            self.manager.update(dt)

            # --- DRAW ---
            self.screen.fill(C_BG)
            
            # 1. Sidebar Background
            pygame.draw.rect(self.screen, C_SIDEBAR, self.sidebar_rect)
            pygame.draw.line(self.screen, C_LINE, (self.sidebar_rect.x, 0), (self.sidebar_rect.x, self.h))

            # 2. Connection Lines (Arena)
            cx, cy = self.arena_rect.center
            active_p = self.players[self.turn]
            if self.state != "GAME_OVER":
                pygame.draw.line(self.screen, C_LINE, (cx, cy), active_p.pos, 2)

            # 3. Dice
            self.dice.draw(self.screen, self.dice.rect.collidepoint((mx,my)))

            # 4. Players
            for p in self.players:
                is_active = (p == self.players[self.turn])
                is_target = False
                if "TARGET" in self.state:
                    if self.state == "TARGET_FALLEN": is_target = not p.alive
                    else: is_target = (p.alive and p != self.players[self.turn])
                
                p.draw(self.screen, is_active, is_target)

            # 5. Sidebar UI
            # Prompt
            t1 = font_big.render(self.prompt, True, C_TEXT_MAIN)
            t2 = font_small.render(self.sub_prompt, True, C_ACCENT)
            sx = self.sidebar_rect.x + 20
            self.screen.blit(t1, (sx, 50))
            self.screen.blit(t2, (sx, 90))
            
            # Log Feed
            if self.log_feed: self.log_feed.draw(self.screen)

            # 6. Particles
            for part in self.particles[:]:
                part['pos'][0] += part['vel'][0]
                part['pos'][1] += part['vel'][1]
                part['life'] -= 1
                if part['life'] <= 0: self.particles.remove(part); continue
                
                pt = font_particle.render(part['text'], True, part['col'])
                pt.set_alpha(int((part['life']/60)*255))
                self.screen.blit(pt, part['pos'])

            self.manager.draw_ui(self.screen)
            pygame.display.flip()

if __name__ == "__main__":
    Game().run()