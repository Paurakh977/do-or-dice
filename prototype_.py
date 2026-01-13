import sys
import math
import random
import pygame
import pygame.gfxdraw
import pygame_gui
from pygame_gui.elements import UITextBox, UIButton
from pathlib import Path

# ==================================================================
# 🔧 PYTHON 3.13 COMPATIBILITY SETUP
# ==================================================================
try:
    pygame.init()
    pygame.mixer.init()
except AttributeError:
    pass 

# Force-load submodules
if not hasattr(pygame, 'surface'): pygame.surface = sys.modules.get('pygame.surface')
if not hasattr(pygame, 'draw'): pygame.draw = sys.modules.get('pygame.draw')
if not hasattr(pygame, 'image'): pygame.image = sys.modules.get('pygame.image')
if not hasattr(pygame, 'transform'): pygame.transform = sys.modules.get('pygame.transform')

# --- CONFIGURATION ---
DEFAULT_W, DEFAULT_H = 1280, 800
FPS = 60
MAX_ROUNDS = 10

# --- PLAYER PROFILES (Image & Audio Mapping) ---
PLAYER_PROFILES = {
    0: {"name": "Ashika", "image": "assets/images/ashika.jpg", "audio": "assets/audios/ashika_asking.mp3"},
    1: {"name": "Bijay Shai", "image": "assets/images/bijay_shai.jpg", "audio": "assets/audios/bijay_shai.mp3"},
    2: {"name": "Jhamala", "image": "assets/images/dhamala.jpg", "audio": "assets/audios/dhamala.mp3"},
    3: {"name": "Khakar", "image": "assets/images/sacar.jpg", "audio": "assets/audios/khakar.mp3"},
    4: {"name": "Dere", "image": "assets/images/shere.jpg", "audio": "assets/audios/shere.mp3"},
}

# --- "SUPER MINIMAL" PALETTE ---
# Backgrounds
C_BG        = (18, 18, 20)       # Almost Black (Void)
C_SIDEBAR   = (25, 25, 28)       # Slightly lighter for UI
C_PANEL     = (35, 35, 40)       # Interactive Elements

# Accents (High Contrast)
C_WHITE     = (240, 240, 240)    # Primary Text
C_GREY      = (100, 100, 110)    # Secondary Text
C_ACCENT    = (50, 150, 255)     # Electric Blue (Dice/Active)
C_DANGER    = (255, 80, 80)      # Flat Red
C_SUCCESS   = (80, 220, 150)     # Mint Green
C_GOLD      = (255, 200, 50)     # Flat Gold
C_PURPLE    = (160, 100, 255)    # Lavender

# --- GRAPHICS HELPERS ---
def draw_circle(surf, color, center, radius):
    x, y = int(center[0]), int(center[1])
    pygame.gfxdraw.aacircle(surf, x, y, int(radius), color)
    pygame.gfxdraw.filled_circle(surf, x, y, int(radius), color)

def draw_ring(surf, color, center, radius, thickness):
    x, y = int(center[0]), int(center[1])
    for i in range(thickness):
        pygame.gfxdraw.aacircle(surf, x, y, int(radius-i), color)

def draw_arc_bar(surf, color, center, radius, thickness, percent):
    """Draws a smooth circular progress bar."""
    if percent <= 0: return
    rect = pygame.Rect(center[0]-radius, center[1]-radius, radius*2, radius*2)
    # Pygame draws arcs in radians, 0 is right. We want 0 at top (-90 deg).
    start_angle = math.radians(-90)
    end_angle = math.radians(-90 + (360 * percent))
    
    # Draw arc is thick, but jagged. We draw thick line using polygon approximation for smoothness
    # But for minimalism, standard pygame.draw.arc with width is okay if background is dark
    pygame.draw.arc(surf, color, rect, start_angle, end_angle, thickness)

# --- VISUAL EFFECTS CLASSES ---

class Notification:
    """A massive, centered text pop-up that tells you what happened."""
    def __init__(self, text, subtext, color):
        self.text = text.upper()
        self.subtext = subtext
        self.color = color
        self.life = 120 # 2 seconds
        self.max_life = 120
        self.y_offset = 0
        
        # Fonts
        self.font_big = pygame.font.SysFont("Segoe UI", 80, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 30)

    def update(self):
        self.life -= 1
        # Gentle float up
        self.y_offset -= 0.5
        return self.life > 0

    def draw(self, surf, center_rect):
        if self.life <= 0: return
        
        cx, cy = center_rect.centerx, center_rect.centery
        
        # Fade out logic
        alpha = 255
        if self.life < 30: alpha = int((self.life / 30) * 255)
        
        # 1. Main Text
        txt = self.font_big.render(self.text, True, self.color)
        txt.set_alpha(alpha)
        
        # Shadow
        shd = self.font_big.render(self.text, True, (0,0,0))
        shd.set_alpha(alpha // 2)
        
        # Position
        pos_x = cx - txt.get_width() // 2
        pos_y = cy - txt.get_height() // 2 + self.y_offset
        
        surf.blit(shd, (pos_x + 4, pos_y + 4))
        surf.blit(txt, (pos_x, pos_y))
        
        # 2. Subtext
        if self.subtext:
            sub = self.font_small.render(self.subtext, True, C_WHITE)
            sub.set_alpha(alpha)
            surf.blit(sub, (cx - sub.get_width()//2, pos_y + 90))

class Particle:
    """Small floating numbers for Damage/Heal."""
    def __init__(self, x, y, text, color):
        self.pos = [x, y]
        self.vel = [random.uniform(-1, 1), -2]
        self.text = text
        self.color = color
        self.life = 60
        self.font = pygame.font.SysFont("Verdana", 24, bold=True)

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        alpha = min(255, self.life * 5)
        t = self.font.render(self.text, True, self.color)
        t.set_alpha(alpha)
        surf.blit(t, (self.pos[0], self.pos[1]))

class Dice:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 120, 120)
        self.val = 1
        self.rolling = False
        self.anim_timer = 0
        self.target_val = 1
        self.color = C_ACCENT
        self.shake_offset = (0,0)

    def reposition(self, cx, cy):
        self.rect.center = (cx, cy)

    def roll(self, target):
        self.rolling = True
        self.anim_timer = 40
        self.target_val = target

    def update(self):
        if self.rolling:
            self.anim_timer -= 1
            # Vibrate effect
            self.shake_offset = (random.randint(-3, 3), random.randint(-3, 3))
            
            if self.anim_timer % 4 == 0:
                self.val = random.randint(1, 6)
                
            if self.anim_timer <= 0:
                self.rolling = False
                self.val = self.target_val
                self.shake_offset = (0,0)
                return True
        return False

    def draw(self, surf, hover):
        cx = self.rect.centerx + self.shake_offset[0]
        cy = self.rect.centery + self.shake_offset[1]
        size = 110
        
        # Dynamic Color
        col = self.color
        if hover: col = (100, 200, 255)
        if self.rolling: col = C_WHITE

        # Draw Rounded Square (Squircle) - Modern Look
        r = pygame.Rect(0, 0, size, size)
        r.center = (cx, cy)
        pygame.draw.rect(surf, col, r, border_radius=20)
        
        # Border
        pygame.draw.rect(surf, C_BG, r, width=3, border_radius=20)

        # Pips (Dots)
        pip_col = C_BG
        pip_r = 7
        offset = 28
        
        dots = []
        if self.val == 1: dots = [(0,0)]
        elif self.val == 2: dots = [(-1,-1), (1,1)]
        elif self.val == 3: dots = [(-1,-1), (0,0), (1,1)]
        elif self.val == 4: dots = [(-1,-1), (1,-1), (-1,1), (1,1)]
        elif self.val == 5: dots = [(-1,-1), (1,-1), (-1,1), (1,1), (0,0)]
        elif self.val == 6: dots = [(-1,-1), (1,-1), (-1,1), (1,1), (-1,0), (1,0)]

        for dx, dy in dots:
            draw_circle(surf, pip_col, (cx + dx*offset, cy + dy*offset), pip_r)

        # "ROLL" Text hint
        if not self.rolling and hover:
            f = pygame.font.SysFont("Verdana", 12, bold=True)
            t = f.render("CLICK", True, C_GREY)
            surf.blit(t, t.get_rect(center=(cx, r.bottom + 15)))

class Player:
    def __init__(self, idx):
        self.idx = idx
        profile = PLAYER_PROFILES.get(idx, {})
        self.name = profile.get("name", f"P{idx + 1}")
        self.hp = 20
        self.max_hp = 20
        self.vp = 0
        self.alive = True
        self.pos = (0,0)
        self.rect = pygame.Rect(0,0,100,100)
        self.scale = 1.0
        
        # Load player image
        self.image = None
        self.image_original = None
        image_path = profile.get("image")
        if image_path and Path(image_path).exists():
            try:
                self.image_original = pygame.image.load(image_path)
            except Exception as e:
                print(f"Error loading image for {self.name}: {e}")
        
        # Load audio
        self.audio_path = profile.get("audio")

    def calculate_position(self, center, radius):
        angle = -90 + (self.idx * (360 / 5))
        rad = math.radians(angle)
        self.pos = (center[0] + radius * math.cos(rad), center[1] + radius * math.sin(rad))
        self.rect = pygame.Rect(self.pos[0]-50, self.pos[1]-50, 100, 100)

    def take_dmg(self, amount, r_num):
        if not self.alive: return False
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True
        return False

    def update(self, hover):
        # Smooth scale on hover
        target_scale = 1.15 if hover else 1.0
        self.scale += (target_scale - self.scale) * 0.2
        
        # Scale and cache image at current scale
        if self.image_original:
            size = int(100 * self.scale)
            self.image = pygame.transform.scale(self.image_original, (size, size))

    def draw(self, surf, is_active, is_target, hover):
        x, y = self.pos
        s = self.scale
        
        # 1. Selection Ring (If targeted)
        if is_target:
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 2
            draw_ring(surf, C_GOLD, (x, y), 65*s + pulse, 2)

        # 2. Active Turn Indicator (Glow behind)
        if is_active:
             draw_circle(surf, (40, 40, 50), (x, y), 65*s)

        # 3. Avatar Circle / Image
        if self.image:
            # Draw image as circular avatar
            img_rect = self.image.get_rect(center=(x, y))
            # Create circular mask
            mask_surf = pygame.Surface((img_rect.width, img_rect.height), pygame.SRCALPHA)
            pygame.draw.circle(mask_surf, (255, 255, 255, 255), 
                             (img_rect.width//2, img_rect.height//2), img_rect.width//2)
            img_copy = self.image.copy()
            img_copy.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(img_copy, img_rect)
        else:
            # Fallback to circle if no image
            base_col = (50, 50, 55)
            if not self.alive: base_col = (30, 30, 30)
            draw_circle(surf, base_col, (x, y), 50*s)

        # 4. Health Ring (The Minimalist Health Bar)
        if self.alive:
            hp_pct = self.hp / self.max_hp
            hp_col = C_SUCCESS if hp_pct > 0.4 else C_DANGER
            # Draw faint background ring
            pygame.draw.circle(surf, (30,30,30), (x, y), 50*s, width=4)
            # Draw progress arc
            draw_arc_bar(surf, hp_col, (x,y), 50*s, 4, hp_pct)

        # 5. Text (Name & VP)
        font_name = pygame.font.SysFont("Segoe UI", int(18*s), bold=True)
        col_name = C_WHITE if self.alive else C_GREY
        t_name = font_name.render(self.name, True, col_name)
        surf.blit(t_name, t_name.get_rect(center=(x, y - 65*s)))
        
        font_vp = pygame.font.SysFont("Verdana", int(14*s), bold=True)
        t_vp = font_vp.render(f"{self.vp} VP", True, C_GOLD)
        surf.blit(t_vp, t_vp.get_rect(center=(x, y + 65*s)))

        # 6. Dead Marker
        if not self.alive:
            pygame.draw.line(surf, C_DANGER, (x-20, y-20), (x+20, y+20), 4)
            pygame.draw.line(surf, C_DANGER, (x+20, y-20), (x-20, y+20), 4)

# --- GAME ENGINE ---

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((DEFAULT_W, DEFAULT_H), pygame.RESIZABLE)
        pygame.display.set_caption("DO or DICE: Minimal")
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((DEFAULT_W, DEFAULT_H))
        
        self.init_game()
        
    def init_game(self):
        self.players = [Player(i) for i in range(5)]
        self.dice = Dice()
        self.particles = []
        self.notification = None # The active "Toast" message
        self.round = 1
        self.turn = 0
        self.state = "IDLE"
        self.payload = None
        self.current_audio = None  # Track currently playing audio
        self.last_played_player = -1  # Track which player's audio is currently playing
        
        self.prompt = "PLAYER 1"
        self.sub_prompt = "Click Dice to Roll"
        self.log_history = []
        self.btn_opts = []

        # Layout
        self.arena_rect = pygame.Rect(0,0,0,0)
        self.sidebar_rect = pygame.Rect(0,0,0,0)
        
        self.log_box = UITextBox("", pygame.Rect(0,0,100,100), self.manager)
        self.resize_layout(DEFAULT_W, DEFAULT_H)
        self.log("System Ready.")
        
        # Auto-play Player 1's audio at game start
        self.play_current_player_audio()

    def resize_layout(self, w, h):
        self.manager.set_window_resolution((w, h))
        
        sb_width = 320
        ar_width = w - sb_width
        
        self.arena_rect = pygame.Rect(0, 0, ar_width, h)
        self.sidebar_rect = pygame.Rect(ar_width, 0, sb_width, h)

        cx, cy = self.arena_rect.center
        rad = min(ar_width, h) * 0.32
        for p in self.players: p.calculate_position((cx, cy), rad)
        self.dice.reposition(cx, cy)
        
        # UI Positioning
        self.log_box.set_relative_position((self.sidebar_rect.x + 20, 140))
        self.log_box.set_dimensions((self.sidebar_rect.width - 40, h - 250))
        self.refresh_buttons()

    def refresh_buttons(self):
        bx = self.sidebar_rect.x + 20
        by = self.sidebar_rect.bottom - 80
        bw = (self.sidebar_rect.width - 50) // 2
        
        for i, btn in enumerate(self.btn_opts):
            btn.set_relative_position((bx + i*(bw+10), by))
            btn.set_dimensions((bw, 60))

    def log(self, text):
        self.log_history.append(text)
        if len(self.log_history) > 30: self.log_history.pop(0)
        self.log_box.set_text("<br>".join(self.log_history))

    def show_notification(self, title, sub, color):
        self.notification = Notification(title, sub, color)

    def get_active(self): return self.players[self.turn]
    
    def play_current_player_audio(self):
        """Play audio for the current active player."""
        p = self.get_active()
        
        # Only play if not already playing this player's audio
        if self.last_played_player != p.idx:
            self.last_played_player = p.idx
            
            # Stop previous audio
            if self.current_audio:
                pygame.mixer.Sound.stop(self.current_audio)
                self.current_audio = None
            
            # Play current player's audio
            if p.audio_path and Path(p.audio_path).exists():
                try:
                    self.current_audio = pygame.mixer.Sound(p.audio_path)
                    self.current_audio.play()
                except Exception as e:
                    print(f"Error playing audio for {p.name}: {e}")

    # --- ACTION LOGIC ---
    def start_roll(self):
        self.state = "ROLLING"
        p = self.get_active()
        roll = random.randint(1, 6)
        
        # Rules Dictionary
        rules_live = {
            1: ("BACKFIRE", "Take 3 DMG", C_DANGER),
            2: ("JAB", "Deal 2 DMG", C_WHITE),
            3: ("STEAL", "Steal 1 VP", C_PURPLE),
            4: ("STRIKE", "Deal 4 DMG", C_WHITE),
            5: ("RECOVER", "Heal 3 HP", C_SUCCESS),
            6: ("POWER", "Ultimate Choice", C_GOLD)
        }
        rules_dead = {
            1: ("MIST", "Nothing Happens", C_GREY),
            2: ("MIST", "Nothing Happens", C_GREY),
            3: ("BOON", "Buff Player", C_SUCCESS),
            4: ("BOON", "Buff Player", C_SUCCESS),
            5: ("CURSE", "Debuff Player", C_DANGER),
            6: ("CURSE", "Debuff Player", C_DANGER)
        }
        
        data = rules_live[roll] if p.alive else rules_dead[roll]
        
        self.dice.roll(roll)
        self.prompt = "ROLLING..."
        self.sub_prompt = ""
        self.payload = {"roll": roll, "title": data[0], "sub": data[1], "col": data[2]}

    def finish_roll(self):
        p = self.get_active()
        d = self.payload
        roll = d['roll']
        
        # 1. TRIGGER BIG VISUAL NOTIFICATION
        self.show_notification(d['title'], d['sub'], d['col'])
        
        self.log(f"<b>{p.name}</b> rolled {roll}: {d['title']}")
        
        if p.alive:
            if roll == 1: # Backfire
                self.particles.append(Particle(p.pos[0], p.pos[1], "-3", C_DANGER))
                if p.take_dmg(3, self.round): self.log(f"{p.name} Died!")
                self.next_turn()
            elif roll == 5: # Recover
                p.hp = min(p.hp+3, p.max_hp)
                self.particles.append(Particle(p.pos[0], p.pos[1], "+3", C_SUCCESS))
                self.next_turn()
            elif roll == 2: self.set_target("JAB", "Select Enemy (-2 HP)", "dmg", 2)
            elif roll == 3: self.set_target("STEAL", "Select Enemy (-1 VP)", "steal")
            elif roll == 4: self.set_target("STRIKE", "Select Enemy (-4 HP)", "dmg", 4)
            elif roll == 6: self.set_choice("POWER MOVE", "DMG (-6)", "VP (+3)", "pdmg", "pvp")
        else:
            if roll <= 2: self.next_turn()
            elif roll <= 4: self.set_target("BOON", "Buff Living", "boon", fallen=True)
            else: self.set_target("CURSE", "Debuff Living", "curse", fallen=True)

    def set_target(self, title, sub, act, val=0, fallen=False):
        self.state = "TARGETING"
        self.prompt = title
        self.sub_prompt = sub
        self.payload = {"act": act, "val": val, "fallen": fallen}

    def resolve_target(self, target):
        actor = self.get_active()
        data = self.payload
        
        # Validation
        if data.get('fallen'):
            if not target.alive: return
        else:
            if not target.alive or target == actor: return

        # Execute
        act = data['act']
        val = data.get('val', 0)
        
        if act == "dmg":
            self.particles.append(Particle(target.pos[0], target.pos[1], f"-{val}", C_DANGER))
            if target.take_dmg(val, self.round):
                self.log(f"{target.name} Eliminated!")
                self.show_notification("ELIMINATED", target.name, C_DANGER)
                if actor.alive: actor.vp += 2
            self.next_turn()
            
        elif act == "steal":
            amt = 1 if target.vp > 0 else 0
            target.vp -= amt; actor.vp += amt
            self.particles.append(Particle(target.pos[0], target.pos[1], f"-{amt} VP", C_DANGER))
            self.particles.append(Particle(actor.pos[0], actor.pos[1], f"+{amt} VP", C_GOLD))
            self.next_turn()
            
        elif act == "boon":
            actor.last_target = target
            self.set_choice(f"Bless {target.name}", "+2 HP", "+1 VP", 
                {"act": "app", "t": target, "m": "hp"}, {"act": "app", "t": target, "m": "vp"})
                
        elif act == "curse":
            actor.last_target = target
            self.set_choice(f"Curse {target.name}", "-2 HP", "-1 VP",
                {"act": "neg", "t": target, "m": "hp"}, {"act": "neg", "t": target, "m": "vp"})

    def set_choice(self, title, l1, l2, d1, d2):
        self.state = "CHOOSING"
        self.prompt = title
        self.sub_prompt = "Select Option ->"
        b1 = UIButton(pygame.Rect(0,0,100,50), l1, self.manager)
        b1.action = d1
        b2 = UIButton(pygame.Rect(0,0,100,50), l2, self.manager)
        b2.action = d2
        self.btn_opts = [b1, b2]
        self.refresh_buttons()

    def resolve_choice(self, data):
        for b in self.btn_opts: b.kill()
        self.btn_opts = []
        actor = self.get_active()

        if data == "pvp":
            actor.vp += 3
            self.particles.append(Particle(actor.pos[0], actor.pos[1], "+3 VP", C_GOLD))
            self.next_turn()
        elif data == "pdmg":
            self.set_target("CRITICAL", "Select Target (-6 HP)", "dmg", 6)
        elif isinstance(data, dict):
            t = data['t']
            if data['act'] == "app":
                if data['m'] == "hp": t.hp += 2; txt="+2 HP"; col=C_SUCCESS
                else: t.vp += 1; txt="+1 VP"; col=C_GOLD
            else:
                if data['m'] == "hp": t.take_dmg(2, self.round); txt="-2 HP"; col=C_DANGER
                else: t.vp = max(0, t.vp-1); txt="-1 VP"; col=C_DANGER
            
            self.particles.append(Particle(t.pos[0], t.pos[1], txt, col))
            self.next_turn()

    def next_turn(self):
        self.turn += 1
        if self.turn >= 5: self.end_round()
        else: self.check_state()

    def end_round(self):
        self.show_notification(f"ROUND {self.round} END", "Survivors gain +1 VP", C_WHITE)
        alive = 0
        for p in self.players:
            if p.alive:
                p.vp += 1
                self.particles.append(Particle(p.pos[0], p.pos[1], "+1 VP", C_GOLD))
                alive += 1
        self.round += 1
        self.turn = 0
        if alive <= 1 or self.round > MAX_ROUNDS: self.game_over()
        else: self.check_state()

    def check_state(self):
        alive = [p for p in self.players if p.alive]
        if len(alive) <= 1: self.game_over()
        else:
            p = self.get_active()
            self.state = "IDLE"
            self.prompt = f"{p.name}'S TURN"
            self.sub_prompt = "Click Dice to Roll"
            self.dice.color = C_ACCENT if p.alive else C_GREY
            
            # Auto-play current player's audio
            self.play_current_player_audio()

    def game_over(self):
        # Stop all audio
        if self.current_audio:
            pygame.mixer.Sound.stop(self.current_audio)
            self.current_audio = None
        
        self.state = "GAME_OVER"
        self.prompt = "GAME OVER"
        self.sub_prompt = "View Results in Sidebar"
        self.show_notification("GAME OVER", "Check Sidebar for Winner", C_GOLD)
        
        ranked = sorted(self.players, key=lambda x: (x.alive, x.vp, x.hp), reverse=True)
        res = "<br><font size=6 color='#FFD700'><b>STANDINGS</b></font><br>"
        for i, p in enumerate(ranked):
            c = "#FFFFFF" if p.alive else "#666666"
            res += f"{i+1}. <font color='{c}'>{p.name}</font> : {p.vp} VP<br>"
        self.log_box.set_text(res)
        
        b = UIButton(pygame.Rect(0,0,100,50), "RESTART", self.manager)
        b.action = "restart"
        self.btn_opts = [b]
        self.refresh_buttons()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.VIDEORESIZE: self.resize_layout(event.w, event.h)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.arena_rect.collidepoint(event.pos):
                        if self.state == "IDLE" and self.dice.rect.collidepoint(event.pos):
                            self.start_roll()
                        elif self.state == "TARGETING":
                             for p in self.players:
                                if p.rect.collidepoint(event.pos): self.resolve_target(p)
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if hasattr(event.ui_element, 'action'):
                        if event.ui_element.action == "restart": self.init_game()
                        else: self.resolve_choice(event.ui_element.action)
                self.manager.process_events(event)
            
            # Update
            if self.state == "ROLLING": 
                if self.dice.update(): self.finish_roll()
            if self.notification:
                if not self.notification.update(): self.notification = None
            self.particles = [p for p in self.particles if p.update()]
            
            mx, my = pygame.mouse.get_pos()
            for p in self.players: p.update(p.rect.collidepoint((mx,my)))
            self.manager.update(dt)
            
            # Draw
            self.screen.fill(C_BG)
            
            # Sidebar
            pygame.draw.rect(self.screen, C_SIDEBAR, self.sidebar_rect)
            
            # Arena Connections
            if self.state != "GAME_OVER":
                cx, cy = self.arena_rect.center
                pygame.draw.line(self.screen, C_PANEL, (cx, cy), self.get_active().pos, 2)

            # Dice
            dice_hover = self.dice.rect.collidepoint((mx,my)) and self.state == "IDLE"
            self.dice.draw(self.screen, dice_hover)
            
            # Players
            for p in self.players:
                is_active = (p == self.get_active())
                is_target = False
                if self.state == "TARGETING":
                    d = self.payload
                    actor = self.get_active()
                    if d.get('fallen'): is_target = p.alive
                    else: is_target = (p.alive and p != actor)
                p.draw(self.screen, is_active, is_target, p.rect.collidepoint((mx,my)))
            
            # Notifications & Particles
            for p in self.particles: p.draw(self.screen)
            if self.notification: self.notification.draw(self.screen, self.arena_rect)
            
            # Sidebar UI
            f_head = pygame.font.SysFont("Segoe UI", 36, bold=True)
            f_sub = pygame.font.SysFont("Segoe UI", 18)
            t_h = f_head.render(self.prompt, True, C_WHITE)
            t_s = f_sub.render(self.sub_prompt, True, C_ACCENT)
            
            sx = self.sidebar_rect.x + 20
            self.screen.blit(t_h, (sx, 40))
            self.screen.blit(t_s, (sx, 85))
            
            self.manager.draw_ui(self.screen)
            pygame.display.flip()

if __name__ == "__main__":
    Game().run()