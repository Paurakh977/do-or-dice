"""
Main Game UI for DO OR DICE.
Integrates the pygame visual interface with the backend services.
"""
from __future__ import annotations
import sys
import math
import random
import pygame
import pygame.gfxdraw
import pygame_gui

from .theme import (
    C_BG, C_SIDEBAR, C_PANEL, C_GRID, C_LINE,
    C_TEXT_MAIN, C_TEXT_DIM, C_ACCENT, C_DANGER, C_SUCCESS, C_GOLD, C_PURPLE,
    draw_rounded_rect, draw_smooth_circle, AUD_DIR
)
from .player_profiles import PLAYER_PROFILES, BGM_FILE
from .components import LogFeed, PlayerVisual, Dice

from src.controllers.orchestrator import GameController
from src.controllers.api import Action_service
from src.services import HistoryService, TurnResolverService, IngameRankService
from src.models import Player, Status, ActiveFace, FallenFace, active_face_vals, fallen_face_vals
from src.configs.constants import MAX_ROUNDS, TOTAL_PLAYERS


# Configuration
DEFAULT_W, DEFAULT_H = 1280, 800
FPS = 60


class Game:
    """Main game class that manages the UI and integrates with backend services."""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((DEFAULT_W, DEFAULT_H), pygame.RESIZABLE)
        pygame.display.set_caption("DO OR DICE // PRO")
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((DEFAULT_W, DEFAULT_H))
        
        self.voice_channel = pygame.mixer.Channel(0)
        
        # --- BGM SETUP ---
        try:
            bgm_path = AUD_DIR / BGM_FILE
            if bgm_path.exists():
                pygame.mixer.music.load(str(bgm_path))
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)  # Loop infinite
            else:
                print(f"[BGM] Placeholder: Add '{BGM_FILE}' to {AUD_DIR}")
        except Exception as e:
            print(f"[BGM] Error: {e}")
        
        # --- BACKEND SERVICES ---
        self.history_service = HistoryService()
        self.action_service = Action_service(self.history_service)
        self.ranking_service = IngameRankService()
        self.turn_resolver = TurnResolverService(self.action_service)
        
        # Clear any existing players from previous runs
        Player.player_arrangement.clear()
        
        # Initialize players with names from profiles
        self.backend_players: list[Player] = []
        for i in range(TOTAL_PLAYERS):
            profile = PLAYER_PROFILES.get(i, {})
            name = profile.get("name", f"Player {i+1}").split()[0]  # Use first word as name
            player = Player(name=name)
            self.backend_players.append(player)
        
        # Set up turn resolver with participants
        self.turn_resolver.set_participants(Player.player_arrangement)
        self.ranking_service.initiate_ranks()
        
        # --- VISUAL PLAYERS ---
        self.player_visuals: list[PlayerVisual] = []
        for i, player in enumerate(Player.player_arrangement):
            self.player_visuals.append(PlayerVisual(player, i))
        
        # --- UI COMPONENTS ---
        self.dice = Dice()
        self.log_feed: LogFeed | None = None
        
        # --- GAME STATE ---
        self.round = 1
        self.turn = 0
        self.state = "IDLE"  # IDLE, ROLLING, TARGET, CHOICE, TARGET_FALLEN, GAME_OVER
        self.prompt = "WELCOME"
        self.sub_prompt = "Click the Dice to Start"
        self.payload: dict | None = None
        self.particles: list[dict] = []
        self.buttons: list = []
        self.last_played_player = -1
        self.current_audio = None
        
        # Move Display
        self.move_display: dict | None = None  # {"text": str, "color": tuple, "timer": int}
        
        # Audio & Background Extras
        self.audio_cooldown = 0.0
        self.bg_scroll = 0.0
        self.bg_particles = [
            [random.randint(0, DEFAULT_W), random.randint(0, DEFAULT_H), random.randint(1, 3)]
            for _ in range(30)
        ]
        
        self.layout(DEFAULT_W, DEFAULT_H)
        self.add_log("System Ready. Game Initialized.", C_SUCCESS)
        self.play_audio()

    def draw_bg(self) -> None:
        """Draw the animated background."""
        # 0. Base
        self.screen.fill(C_BG)
        
        # 1. Scrolling Grid
        self.bg_scroll = (self.bg_scroll + 0.2) % 60
        grid_sz = 60
        rows = self.h // grid_sz + 2
        cols = (self.w - 320) // grid_sz + 2
        
        for y in range(rows):
            pygame.draw.line(
                self.screen, C_GRID,
                (0, y * grid_sz + self.bg_scroll - 60),
                (self.w - 340, y * grid_sz + self.bg_scroll - 60)
            )
        for x in range(cols):
            pygame.draw.line(self.screen, C_GRID, (x * grid_sz, 0), (x * grid_sz, self.h))

        # 2. Ambient Particles
        for p in self.bg_particles:
            p[1] -= p[2] * 0.2  # Float up
            if p[1] < -10:
                p[1] = self.h + 10
                p[0] = random.randint(0, self.w - 340)
            
            val = 50 + (p[2] * 40)
            pygame.draw.circle(self.screen, (val, val, val + 20), (int(p[0]), int(p[1])), p[2])
            
        # 3. Vignette Overlay
        v = pygame.Surface((self.w - 340, self.h), pygame.SRCALPHA)
        pygame.draw.rect(v, (5, 5, 10, 80), v.get_rect())
        self.screen.blit(v, (0, 0))

    def layout(self, w: int, h: int) -> None:
        """Update layout for window resize."""
        self.manager.set_window_resolution((w, h))
        self.w, self.h = w, h
        
        # Sidebar is fixed 320px on the right
        self.sidebar_rect = pygame.Rect(w - 340, 0, 340, h)
        self.arena_rect = pygame.Rect(0, 0, w - 340, h)
        
        # Positioning Players
        cx, cy = self.arena_rect.center
        rad = min(self.arena_rect.width, self.arena_rect.height) * 0.35
        for p in self.player_visuals:
            p.calculate_position((cx, cy), rad)
        self.dice.rect.center = (cx, cy)
        
        # Log Feed in Sidebar (Bottom)
        self.log_feed = LogFeed(self.sidebar_rect.x + 20, h - 350, 300, 330)

    def add_log(self, text: str, col: tuple = C_TEXT_MAIN) -> None:
        """Add a message to the game log."""
        if self.log_feed:
            self.log_feed.add(text, col)

    def create_buttons(self, labels: list[str], actions: list[str]) -> None:
        """Create UI buttons in the arena area (centered below dice)."""
        # Clean old buttons
        for b in self.buttons:
            b.kill()
        self.buttons = []
        
        # Position buttons in the arena, below the dice
        cx, cy = self.arena_rect.center
        btn_width = 180
        btn_height = 42
        btn_spacing = 15
        total_width = len(labels) * btn_width + (len(labels) - 1) * btn_spacing
        start_x = cx - total_width // 2
        btn_y = cy + 80  # Below the dice
        
        for i, lbl in enumerate(labels):
            rect = pygame.Rect(start_x + i * (btn_width + btn_spacing), btn_y, btn_width, btn_height)
            btn = pygame_gui.elements.UIButton(relative_rect=rect, text=lbl, manager=self.manager)
            btn.action = actions[i]
            self.buttons.append(btn)

    def play_audio(self, force: bool = False) -> None:
        """Play audio for current player's turn."""
        if not self.player_visuals:
            return
        p = self.player_visuals[self.turn]
        
        # Logic to only play if new player turn OR forced loop
        if self.last_played_player != p.idx or force:
            self.last_played_player = p.idx
            if self.voice_channel.get_busy():
                self.voice_channel.stop()
            if p.sound:
                self.voice_channel.play(p.sound)

    # --- GAME LOGIC ---
    def roll_dice(self) -> None:
        """Handle dice roll initiation."""
        self.state = "ROLLING"
        player_visual = self.player_visuals[self.turn]
        backend_player = player_visual.player
        
        # Roll using backend player's roll_dice method
        face_value = backend_player.roll_dice()
        
        # Get the numeric value for the dice visual
        if isinstance(face_value, ActiveFace):
            roll = [k for k, v in active_face_vals.items() if v == face_value][0]
        else:
            roll = [k for k, v in fallen_face_vals.items() if v == face_value][0]
        
        # Map face values to display info (matching prototype format)
        if backend_player.status == Status.ALIVE:
            # Active face rules
            rules_map = {
                ActiveFace.BACKFIRE: ("BACKFIRE", "Take 3 DMG", C_DANGER, "self_dmg", 3),
                ActiveFace.JAB: ("JAB", "Deal 2 DMG", C_TEXT_MAIN, "target_dmg", 2),
                ActiveFace.PICKPOCKET: ("PICKPOCKET", "Steal 1 VP", C_PURPLE, "steal", 1),
                ActiveFace.STRIKE: ("STRIKE", "Deal 4 DMG", C_TEXT_MAIN, "target_dmg", 4),
                ActiveFace.RECOVER: ("RECOVER", "Heal 3 HP", C_SUCCESS, "heal", 3),
                ActiveFace.POWER_MOVE: ("POWER MOVE", "Choice: DMG or VP", C_GOLD, "choice", 0),
            }
            r = rules_map.get(face_value, ("UNKNOWN", "Unknown", C_TEXT_DIM, "none", 0))
        else:
            # Fallen face rules
            rules_map = {
                FallenFace.NOTHING_1: ("VOID MIST", "No Effect", C_TEXT_DIM, "none", 0),
                FallenFace.NOTHING_2: ("VOID MIST", "No Effect", C_TEXT_DIM, "none", 0),
                FallenFace.PLUS2HP_OR_PLUS1VP: ("SPIRIT BLESS", "Buff a Player", C_SUCCESS, "buff", 0),
                FallenFace.PLUS2HP_OR_PLUS1VP_2: ("SPIRIT BLESS", "Buff a Player", C_SUCCESS, "buff", 0),
                FallenFace.REMOVE2HP_OR_MINUS1VP: ("HAUNT", "Curse a Player", C_DANGER, "curse", 0),
                FallenFace.REMOVE2HP_OR_MINUS1VP_2: ("HAUNT", "Curse a Player", C_DANGER, "curse", 0),
            }
            r = rules_map.get(face_value, ("VOID MIST", "No Effect", C_TEXT_DIM, "none", 0))
        
        self.dice.roll(roll)
        self.prompt = r[0]
        self.sub_prompt = r[1]
        self.payload = {
            "type": r[3],
            "val": r[4],
            "color": r[2],
            "face_value": face_value,
            "roll": roll
        }

    def finish_roll(self) -> None:
        """Handle completion of dice roll animation."""
        player_visual = self.player_visuals[self.turn]
        backend_player = player_visual.player
        act = self.payload['type']
        val = self.payload['val']
        col = self.payload['color']
        face_value = self.payload['face_value']
        
        # Display move on screen
        self.move_display = {"text": self.prompt, "color": col, "timer": 120}
        
        self.add_log(f"{player_visual.display_name} rolled {self.dice.val}", col)
        
        if act == "self_dmg":
            # BACKFIRE - use backend
            self.action_service.execute_action(player=backend_player, action=face_value)
            self.add_particle(player_visual.pos, f"-{val}", C_DANGER)
            if backend_player.status == Status.FALLEN:
                self.add_log(f"{player_visual.display_name} DIED!", C_DANGER)
            self.next_turn()
        
        elif act == "heal":
            # RECOVER - use backend
            self.action_service.execute_action(player=backend_player, action=face_value)
            self.add_particle(player_visual.pos, f"+{val}", C_SUCCESS)
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
            # No effect - still record in history
            self.action_service.execute_action(player=backend_player, action=face_value)
            self.next_turn()

    def handle_target(self, target_visual: PlayerVisual) -> None:
        """Handle target selection for actions."""
        actor_visual = self.player_visuals[self.turn]
        actor = actor_visual.player
        target = target_visual.player
        
        # Validate selection
        if self.state == "TARGET":
            if not target_visual.alive or target_visual == actor_visual:
                return
        elif self.state == "TARGET_FALLEN":
            if not target_visual.alive:
                return

        act = self.payload['type']
        val = self.payload['val']
        face_value = self.payload['face_value']

        if act == "target_dmg":
            # JAB or STRIKE
            self.action_service.execute_action(player=actor, action=face_value, target=target)
            self.add_particle(target_visual.pos, f"-{val}", C_DANGER)
            if target.status == Status.FALLEN:
                self.add_log(f"{target_visual.display_name} ELIMINATED", C_DANGER)
                # Award VP for elimination
                if actor.status == Status.ALIVE:
                    # Not using backend's VP gain here since elimination bonus isn't in backend
                    pass
        
        elif act == "choice":
            # POWER_MOVE damage choice
            self.action_service.execute_action(player=actor, action=face_value, target=target, choice_action="damage_hp")
            self.add_particle(target_visual.pos, f"-6", C_DANGER)
            if target.status == Status.FALLEN:
                self.add_log(f"{target_visual.display_name} ELIMINATED", C_DANGER)
        
        elif act == "steal":
            # PICKPOCKET
            if target.vp > 0:
                self.action_service.execute_action(player=actor, action=face_value, target=target)
                self.add_particle(target_visual.pos, f"-1VP", C_DANGER)
                self.add_particle(actor_visual.pos, f"+1VP", C_GOLD)
            else:
                self.action_service.execute_action(player=actor, action=face_value, target=target)
                self.add_log(f"{target_visual.display_name} has no VP to steal!", C_TEXT_DIM)
            
        elif act == "buff":
            # SPIRIT BLESS - fallen player buffs alive player
            # Create choice buttons for buff type
            self.payload['target_visual'] = target_visual
            self.state = "BUFF_CHOICE"
            self.create_buttons(["+2 HP", "+1 VP"], ["buff_hp", "buff_vp"])
            return
            
        elif act == "curse":
            # HAUNT - fallen player curses alive player
            self.payload['target_visual'] = target_visual
            self.state = "CURSE_CHOICE"
            self.create_buttons(["-2 HP", "-1 VP"], ["curse_hp", "curse_vp"])
            return

        self.next_turn()

    def handle_choice(self, action_id: str) -> None:
        """Handle button choices."""
        actor_visual = self.player_visuals[self.turn]
        actor = actor_visual.player
        face_value = self.payload.get('face_value')
        
        for b in self.buttons:
            b.kill()
        self.buttons = []
        
        if action_id == "vp_3":
            # POWER_MOVE VP gain
            self.action_service.execute_action(player=actor, action=face_value, choice_action="gain_vp")
            self.add_particle(actor_visual.pos, "+3 VP", C_GOLD)
            self.next_turn()
            
        elif action_id == "dmg_6":
            # POWER_MOVE damage - need to select target
            self.state = "TARGET"
            self.payload['type'] = "choice"
            self.payload['val'] = 6
            self.sub_prompt = "Select Target for 6 DMG"
            
        elif action_id == "buff_hp":
            target_visual = self.payload.get('target_visual')
            if target_visual:
                self.action_service.execute_action(
                    player=actor, action=face_value, 
                    target=target_visual.player, choice_action="heal_hp"
                )
                self.add_particle(target_visual.pos, "+2 HP", C_SUCCESS)
            self.next_turn()
            
        elif action_id == "buff_vp":
            target_visual = self.payload.get('target_visual')
            if target_visual:
                self.action_service.execute_action(
                    player=actor, action=face_value,
                    target=target_visual.player, choice_action="gain_vp"
                )
                self.add_particle(target_visual.pos, "+1 VP", C_GOLD)
            self.next_turn()
            
        elif action_id == "curse_hp":
            target_visual = self.payload.get('target_visual')
            if target_visual:
                self.action_service.execute_action(
                    player=actor, action=face_value,
                    target=target_visual.player, choice_action="damage_hp"
                )
                self.add_particle(target_visual.pos, "-2 HP", C_DANGER)
            self.next_turn()
            
        elif action_id == "curse_vp":
            target_visual = self.payload.get('target_visual')
            if target_visual:
                if target_visual.vp > 0:
                    self.action_service.execute_action(
                        player=actor, action=face_value,
                        target=target_visual.player, choice_action="steal_vp"
                    )
                    self.add_particle(target_visual.pos, "-1 VP", C_DANGER)
                else:
                    self.add_log(f"{target_visual.display_name} has no VP!", C_TEXT_DIM)
            self.next_turn()

    def next_turn(self) -> None:
        """Advance to the next turn."""
        self.turn += 1
        if self.turn >= TOTAL_PLAYERS:
            self.round += 1
            self.turn = 0
            self.add_log(f"--- ROUND {self.round} START ---", C_TEXT_DIM)
            
            # Award VP to survivors (from turn resolver logic)
            alive_count = 0
            for pv in self.player_visuals:
                if pv.alive:
                    pv.player.gain_vp(1)
                    alive_count += 1
            
            # Reset targeting restrictions for new round
            for p in Player.player_arrangement:
                p.last_targetedby = None
                p.last_targetedto = None
            
            # Check game over conditions
            if alive_count <= 1 or self.round > MAX_ROUNDS:
                self.game_over()
                return
            
            # Update rankings
            self.ranking_service.check_rank()

        self.state = "IDLE"
        active = self.player_visuals[self.turn]
        
        self.dice.val = 6  # Reset dice visual
        self.prompt = f"{active.display_name}'S TURN"
        self.sub_prompt = "Click Dice to Roll"
        
        if not active.alive:
            self.sub_prompt = "Ghost Turn - Click Dice"
        
        self.play_audio()

    def game_over(self) -> None:
        """Handle game over state."""
        self.state = "GAME_OVER"
        self.prompt = "GAME OVER"
        self.sub_prompt = "See Standings"
        self.create_buttons(["RESTART GAME"], ["restart"])
        
        # Sort winners using backend ranking
        self.ranking_service.check_rank()
        ranked = self.ranking_service.get_ranks_list
        
        self.add_log("--- FINAL STANDINGS ---", C_GOLD)
        for i, rank_record in enumerate(ranked):
            player = next((p for p in Player.player_arrangement if p.name == rank_record['player_name']), None)
            if player:
                status = "ALIVE" if player.status == Status.ALIVE else "DEAD"
                self.add_log(f"#{i+1} {rank_record['player_name']}: {rank_record['vp_count']}VP ({status})", C_TEXT_MAIN)

    def add_particle(self, pos: tuple, text: str, col: tuple) -> None:
        """Add a floating particle effect."""
        self.particles.append({
            "pos": list(pos),
            "vel": [random.uniform(-1, 1), -2],
            "text": text,
            "col": col,
            "life": 60
        })

    def restart_game(self) -> None:
        """Restart the game."""
        # Clear buttons
        for b in self.buttons:
            b.kill()
        self.buttons = []
        
        # Clear players
        Player.player_arrangement.clear()
        
        # Reinitialize
        self.__init__()

    def run(self) -> None:
        """Main game loop."""
        font_big = pygame.font.SysFont("Consolas", 32, bold=True)
        font_small = pygame.font.SysFont("Consolas", 14)
        font_particle = pygame.font.SysFont("Arial", 20, bold=True)

        while True:
            dt = self.clock.tick(FPS) / 1000.0
            mx, my = pygame.mouse.get_pos()
            
            # --- EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    self.layout(event.w, event.h)
                
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element.action == "restart":
                        self.restart_game()
                    else:
                        self.handle_choice(event.ui_element.action)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "IDLE" and self.dice.rect.collidepoint((mx, my)):
                        self.roll_dice()
                    elif self.state in ("TARGET", "TARGET_FALLEN"):
                        for pv in self.player_visuals:
                            if pv.rect.collidepoint((mx, my)):
                                self.handle_target(pv)

                self.manager.process_events(event)

            # --- UPDATES ---
            # Calculate dice hover ONCE
            dice_hover = self.dice.rect.collidepoint((mx, my))
            
            if self.state == "ROLLING":
                if self.dice.update(dice_hover):
                    self.finish_roll()
            else:
                self.dice.update(dice_hover)
            
            # Update player hover states (visual only, no audio)
            for pv in self.player_visuals:
                pv.update(pv.rect.collidepoint((mx, my)))
                 
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
            active_pv = self.player_visuals[self.turn]
            if self.state != "GAME_OVER":
                alpha = 100 + int(math.sin(pygame.time.get_ticks() * 0.005) * 50)
                if active_pv.alive:
                    color_line = (*C_ACCENT, alpha)
                    line_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
                    pygame.draw.line(line_surf, color_line, (cx, cy), active_pv.pos, 3)
                    self.screen.blit(line_surf, (0, 0))
                else:
                    pygame.draw.line(self.screen, (30, 30, 35), (cx, cy), active_pv.pos, 2)

            # 3. Dice
            self.dice.draw(self.screen)

            # 4. Players
            for pv in self.player_visuals:
                is_active = (pv.idx == self.turn)
                is_target = False
                if self.state in ("TARGET", "TARGET_FALLEN", "BUFF_CHOICE", "CURSE_CHOICE"):
                    if self.state == "TARGET_FALLEN":
                        is_target = pv.alive
                    else:
                        is_target = (pv.alive and pv.idx != self.turn)
                
                pv.draw(self.screen, is_active, is_target)
            
            # 4.5 Move Display (Modern & Minimal)
            if self.move_display:
                self.move_display['timer'] -= 1
                if self.move_display['timer'] <= 0:
                    self.move_display = None
                else:
                    alpha = int((self.move_display['timer'] / 120) * 255)
                    font_move = pygame.font.SysFont("Verdana", 48, bold=True)
                    txt = self.move_display['text'].upper()
                    
                    # Shadow
                    move_surf_s = font_move.render(txt, True, (0, 0, 0))
                    move_surf_s.set_alpha(max(0, alpha - 50))
                    r_s = move_surf_s.get_rect(center=(cx + 2, cy - 128))
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
            
            # B) Turn/Round Indicator Pill
            round_pill = pygame.Rect(self.w - 100, 25, 80, 28)
            draw_rounded_rect(self.screen, (30, 32, 40), round_pill, 8, 255)
            tr = font_particle.render(f"RND {self.round}", True, C_GOLD)
            self.screen.blit(tr, tr.get_rect(center=round_pill.center))
            
            # C) Player Stats Panel (Card Style)
            stats_y = 110
            
            for i, pv in enumerate(self.player_visuals):
                card_h = 50
                card_y = stats_y + (i * (card_h + 10))
                card_rect = pygame.Rect(self.sidebar_rect.x + 15, card_y, 310, card_h)
                
                # Card Background
                bg_col = (25, 27, 33) if pv.alive else (15, 15, 18)
                border_c = C_ACCENT if pv.idx == self.turn else (40, 42, 50)
                border_w = 2 if pv.idx == self.turn else 1
                
                draw_rounded_rect(self.screen, bg_col, card_rect, 8)
                pygame.draw.rect(self.screen, border_c, card_rect, border_w, border_radius=8)
                
                # Content
                # 1. Name
                nm_col = C_TEXT_MAIN if pv.alive else C_TEXT_DIM
                nm_font = pygame.font.SysFont("Verdana", 13, bold=True)
                nm_surf = nm_font.render(pv.display_name, True, nm_col)
                self.screen.blit(nm_surf, (card_rect.x + 12, card_rect.y + 8))
                
                # 2. HP Bar
                bar_bg = pygame.Rect(card_rect.x + 12, card_rect.y + 30, 180, 8)
                pygame.draw.rect(self.screen, (10, 10, 15), bar_bg, border_radius=4)
                
                if pv.alive:
                    pct = max(0, pv.hp / pv.max_hp)
                    fill_w = int(180 * pct)
                    fill_rect = pygame.Rect(card_rect.x + 12, card_rect.y + 30, fill_w, 8)
                    hp_col = C_SUCCESS if pct > 0.4 else C_DANGER
                    pygame.draw.rect(self.screen, hp_col, fill_rect, border_radius=4)
                
                # 3. VP Badge
                vp_surf = font_particle.render(f"{pv.vp}", True, C_GOLD)
                pygame.draw.circle(self.screen, (50, 45, 20), (card_rect.right - 35, card_rect.centery), 16)
                pygame.draw.circle(self.screen, C_GOLD, (card_rect.right - 35, card_rect.centery), 16, 2)
                self.screen.blit(vp_surf, vp_surf.get_rect(center=(card_rect.right - 35, card_rect.centery)))

            # D) Log Feed
            if self.log_feed:
                self.log_feed.draw(self.screen)

            # 6. Particles
            for part in self.particles[:]:
                part['pos'][0] += part['vel'][0]
                part['pos'][1] += part['vel'][1]
                part['life'] -= 1
                if part['life'] <= 0:
                    self.particles.remove(part)
                    continue
                
                # Shadow first
                pt_s = font_particle.render(part['text'], True, (0, 0, 0))
                pt_s.set_alpha(int((part['life'] / 60) * 100))
                self.screen.blit(pt_s, (part['pos'][0] + 1, part['pos'][1] + 1))
                
                pt = font_particle.render(part['text'], True, part['col'])
                pt.set_alpha(int((part['life'] / 60) * 255))
                self.screen.blit(pt, part['pos'])

            self.manager.draw_ui(self.screen)
            pygame.display.flip()


def run_game() -> None:
    """Entry point function to run the game."""
    game = Game()
    game.run()

