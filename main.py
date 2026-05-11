"""
WeltBauer - Minecraft-Style KI-Sandbox
Steuert das komplette Spiel: Rendering, Tastatur, TTS, KI-Eingabefeld
"""
import sys, os, pygame, math, random
import lang_mgr as L
import blocks as B
import ai_command as AI
import save_load as SL
from speech import Speech
from world import World
from audio import AudioManager

# ── Konstanten ───────────────────────────────────────────────────────────────
WIN_W, WIN_H = 960, 640
PANEL_H = 120          # Unterer UI-Bereich
MAP_H   = WIN_H - PANEL_H
TILE    = 24           # Pixel pro Kachel
FONT_PATH = None       # Systemschrift

# Farben
C_BG      = (15,  15,  25)
C_CURSOR  = (255, 255,   0)
C_GRID    = ( 30,  30,  45)
C_PANEL   = ( 20,  20,  35)
C_INPUT   = ( 10,  10,  20)
C_WHITE   = (255, 255, 255)
C_YELLOW  = (255, 215,   0)
C_GREEN   = ( 80, 200,  80)
C_RED     = (220,  80,  80)
C_GRAY    = (150, 150, 150)

COLS = WIN_W  // TILE   # sichtbare Spalten
ROWS = MAP_H  // TILE   # sichtbare Zeilen

START_MONEY = 50_000


# ── Hauptklasse ───────────────────────────────────────────────────────────────
class WeltBauer:
    def __init__(self):
        pygame.init()
        pygame.mixer.pre_init(44100,-16,2,512)
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("WeltBauer")
        self.clock  = pygame.time.Clock()

        # Schrift
        self.fnt   = pygame.font.SysFont("Consolas,Courier New,Arial", 16)
        self.fnt_b = pygame.font.SysFont("Consolas,Courier New,Arial", 18, bold=True)
        self.fnt_lg = pygame.font.SysFont("Consolas,Courier New,Arial", 22, bold=True)

        # TTS & Audio
        self.tts = Speech()
        self.audio = AudioManager()

        # Sprache: Standard Deutsch
        L.load("de")

        # Welt
        self.world  = World()
        self.money  = START_MONEY
        self.cam_x  = 0     # Kamera-Offset in Kacheln
        self.cam_y  = 0
        self.cur_x  = 40    # Cursor-Position
        self.cur_y  = 30

        # Bau-Modus
        self.selected_block = "steinwand"  # aktuell gewählter Block

        # KI-Eingabefeld
        self.ai_input_active = False
        self.ai_input_text   = ""
        self.ai_result_msg   = ""
        self.ai_result_ok    = True
        self.ai_result_timer = 0

        # Status
        self.running  = True
        self.show_help = False
        self.move_cooldown = 0
        self.income_timer = 0
        self.last_income = 0
        
        # Zeit & Licht
        self.world_time = 600 # Start um 6:00 Uhr morgens
        self.time_speed = 0.5 # Wie schnell die Zeit vergeht
        self.night_overlay = pygame.Surface((WIN_W, MAP_H), pygame.SRCALPHA)
        
        # Wetter
        self.weather = "clear" # "clear", "rain", "snow"
        self.weather_timer = random.randint(1000, 3000)
        self.particles = [] # List of [x, y, speed, type]

        # Hilfetext
        self._help_lines = [
            "F1: Hilfe an/aus",
            "Pfeiltasten: Cursor bewegen",
            "Enter: Aktuellen Block platzieren",
            "Entf: Block entfernen",
            "Tab: Nächster Block",
            "Shift+Tab: Vorheriger Block",
            "K: KI-Eingabefeld öffnen",
            "I: Feld-Info vorlesen",
            "S: Statistik",
            "L: Sprache DE/EN wechseln",
            "F5: Speichern  F9: Laden",
            "Ende/Esc+Q: Beenden",
        ]

        # Block-Liste für Tab-Durchlauf
        self._block_ids = list(B.BLOCKS.keys())

        # Ankündigung beim Start
        self.tts.say(L.get("ready"))

    # ── Kamera ──────────────────────────────────────────────────────────────
    def _center_camera(self):
        """Kamera so setzen, dass Cursor sichtbar (mit Rand)."""
        margin = 3
        self.cam_x = max(0, min(self.world.w - COLS,
                                 self.cur_x - COLS//2))
        self.cam_y = max(0, min(self.world.h - ROWS,
                                 self.cur_y - ROWS//2))

    # ── Cursor-Bewegung ──────────────────────────────────────────────────────
    def _move(self, dx, dy):
        nx, ny = self.cur_x + dx, self.cur_y + dy
        if 0 <= nx < self.world.w and 0 <= ny < self.world.h:
            self.cur_x, self.cur_y = nx, ny
            self._center_camera()
            tile = self.world.get(self.cur_x, self.cur_y)
            self.audio.play_step(tile)
            self._announce_tile()
        else:
            self.audio.play_bump()
            self.tts.say(L.get("bump_sound_text"))

    def _announce_tile(self):
        tile = self.world.get(self.cur_x, self.cur_y)
        npcs = self.world.npcs_at(self.cur_x, self.cur_y)
        binfo = B.get(tile) if tile else None
        bname = L.get(binfo["name"]) if binfo else tile or "?"
        if tile == "gras":
            msg = L.get("tile_empty")
        else:
            msg = L.get("tile_occupied", name=bname)
        if npcs:
            npc_names = ", ".join(n.name for n in npcs)
            msg += f" — {npc_names}"
        self.tts.say(f"{L.get('cursor_at', x=self.cur_x, y=self.cur_y)} {msg}")

    # ── Block platzieren/entfernen ────────────────────────────────────────────
    def _place_block(self):
        old_tile = self.world.get(self.cur_x, self.cur_y)
        if old_tile != "gras":
            self.tts.say(L.get("build_failed_occupied"))
            self.audio.play_bump() # Benutze Bump als "Besetzt"-Feedback
            return

        binfo = B.get(self.selected_block)
        cost = binfo["cost"] if binfo else 0
        
        if self.money < cost:
            self.tts.say(L.get("no_money"))
            self.audio.play_remove()
            return

        if self.world.set(self.cur_x, self.cur_y, self.selected_block):
            self.money -= cost
            name = L.get(binfo["name"]) if binfo else self.selected_block
            self.audio.play_build()
            self.tts.say(L.get("build_success", name=name))

    def _remove_block(self):
        old = self.world.get(self.cur_x, self.cur_y)
        if old == "gras":
            self.tts.say(L.get("remove_empty"))
            self.audio.play_click()
        else:
            binfo = B.get(old)
            name = L.get(binfo["name"]) if binfo else old
            self.world.remove(self.cur_x, self.cur_y)
            self.audio.play_remove()
            self.tts.say(L.get("remove_success", name=name))

    def _cycle_block(self, direction=1):
        try:
            idx = self._block_ids.index(self.selected_block)
        except ValueError:
            idx = 0
        idx = (idx + direction) % len(self._block_ids)
        self.selected_block = self._block_ids[idx]
        binfo = B.get(self.selected_block)
        name = L.get(binfo["name"]) if binfo else self.selected_block
        self.audio.play_click()
        self.tts.say(L.get("current_building", name=name, cost=binfo["cost"] if binfo else 0))

    # ── KI-Eingabe ───────────────────────────────────────────────────────────
    def _open_ai_input(self):
        self.ai_input_active = True
        self.ai_input_text   = ""
        self.tts.say("KI-Eingabe: Tippe deinen Befehl, Enter zum Ausführen, Escape zum Abbrechen.")

    def _submit_ai_command(self):
        text = self.ai_input_text.strip()
        if not text:
            self.ai_input_active = False
            return
        # Jetzt mit 5 Rückgabewerten (Kosten am Ende)
        ok, msg, nx, ny, cost = AI.execute(
            text, self.world, self.cur_x, self.cur_y, L.current(), self.money
        )
        if ok:
            self.money -= cost
            self.cur_x, self.cur_y = nx, ny
            self._center_camera()
            self.ai_result_msg   = msg
            self.ai_result_ok    = True
            self.audio.play_build()
            self.tts.say(msg)
        else:
            self.ai_result_msg   = msg
            self.ai_result_ok    = False
            self.audio.play_remove()
            self.tts.say(msg)
            
        self.ai_result_timer = 180
        self.ai_input_active = False
        self.ai_input_text   = ""

    # ── Info & Statistik ─────────────────────────────────────────────────────
    def _info(self):
        tile = self.world.get(self.cur_x, self.cur_y)
        npcs = self.world.npcs_at(self.cur_x, self.cur_y)
        binfo = B.get(tile) if tile else None
        if tile == "gras" and not npcs:
            msg = L.get("info_empty", x=self.cur_x, y=self.cur_y)
        else:
            bname = L.get(binfo["name"]) if binfo else tile or "?"
            npc_str = ", ".join(n.name for n in npcs) if npcs else ""
            msg = L.get("info_building", name=bname, x=self.cur_x, y=self.cur_y,
                        pop=len(npcs), happy=100, income=0)
            if npc_str:
                msg += f" NPCs: {npc_str}"
        self.tts.say(msg)

    def _stats(self):
        st = self.world.stats()
        msg = (f"{L.get('stats_buildings', count=st['placed'])}. "
               f"NPCs: {st['npcs']}. "
               f"Kasse: {self.money} Euro.")
        self.tts.say(msg)

    # ── Events ───────────────────────────────────────────────────────────────
    def _handle_events(self):
        mods = pygame.key.get_mods()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False

            elif ev.type == pygame.KEYDOWN:
                # --- KI-Eingabefeld aktiv ---
                if self.ai_input_active:
                    if ev.key == pygame.K_RETURN:
                        self._submit_ai_command()
                    elif ev.key == pygame.K_ESCAPE:
                        self.ai_input_active = False
                        self.tts.say("Abgebrochen.")
                    elif ev.key == pygame.K_BACKSPACE:
                        self.ai_input_text = self.ai_input_text[:-1]
                    else:
                        char = ev.unicode
                        if char and char.isprintable():
                            self.ai_input_text += char
                    continue

                # --- Normalmodus ---
                if ev.key == pygame.K_UP:       self._move( 0,-1)
                elif ev.key == pygame.K_DOWN:   self._move( 0, 1)
                elif ev.key == pygame.K_LEFT:   self._move(-1, 0)
                elif ev.key == pygame.K_RIGHT:  self._move( 1, 0)

                elif ev.key == pygame.K_RETURN: self._place_block()
                elif ev.key == pygame.K_DELETE: self._remove_block()

                elif ev.key == pygame.K_TAB:
                    if mods & pygame.KMOD_SHIFT:
                        self._cycle_block(-1)
                    else:
                        self._cycle_block(1)

                elif ev.key == pygame.K_k:      self._open_ai_input()
                elif ev.key == pygame.K_i:      self._info()
                elif ev.key == pygame.K_s:      self._stats()
                elif ev.key == pygame.K_l:
                    L.toggle()
                    self.tts.say(L.get("language_changed"))

                elif ev.key == pygame.K_F1:
                    self.show_help = not self.show_help
                    if self.show_help:
                        self.tts.say("Hilfe geöffnet. " + " ".join(self._help_lines))

                elif ev.key == pygame.K_F5:
                    SL.save(self.world, self.cur_x, self.cur_y, L.current(), self.money, self.world_time, self.weather)
                    self.tts.say(L.get("game_saved"))
                    self.audio.play_build()

                elif ev.key == pygame.K_F9:
                    d = SL.load(self.world)
                    if d:
                        self.cur_x = d["cursor"]["x"]
                        self.cur_y = d["cursor"]["y"]
                        self.money = d.get("money", START_MONEY)
                        self.world_time = d.get("time", 600)
                        self.weather = d.get("weather", "clear")
                        self.world.weather = self.weather
                        L.load(d.get("lang","de"))
                        self._center_camera()
                        self.tts.say(L.get("game_loaded"))
                    else:
                        self.tts.say(L.get("game_load_failed"))

                elif ev.key in (pygame.K_END, pygame.K_ESCAPE):
                    self.running = False

    # ── Zeichnen ─────────────────────────────────────────────────────────────
    def _draw_world(self):
        for row in range(ROWS + 1):
            for col in range(COLS + 1):
                wx = self.cam_x + col
                wy = self.cam_y + row
                px = col * TILE
                py = row * TILE

                tile = self.world.get(wx, wy)
                if tile is None:
                    color = (5, 5, 10)
                else:
                    binfo = B.get(tile)
                    color = binfo["color"] if binfo else (40,40,40)

                pygame.draw.rect(self.screen, color, (px, py, TILE, TILE))
                # Gitter-Linie
                pygame.draw.rect(self.screen, C_GRID,  (px, py, TILE, TILE), 1)

                # Symbol des Blocks
                if tile and tile != "gras":
                    binfo = B.get(tile)
                    sym = binfo["sym"] if binfo else "?"
                    s = self.fnt.render(sym, True, (0,0,0,120))
                    self.screen.blit(s, (px+TILE//2-s.get_width()//2,
                                        py+TILE//2-s.get_height()//2))

        # NPCs zeichnen
        for npc in self.world.npcs:
            col = npc.tile_x() - self.cam_x
            row = npc.tile_y() - self.cam_y
            if 0 <= col < COLS and 0 <= row < ROWS:
                cx = col*TILE + TILE//2
                cy = row*TILE + TILE//2
                r  = TILE//2 - 2
                pygame.draw.circle(self.screen, npc.color, (cx,cy), r)
                pygame.draw.circle(self.screen, (255,255,255), (cx,cy), r, 1)
                s = self.fnt.render(npc.sym, True, (20,20,20))
                self.screen.blit(s, (cx-s.get_width()//2, cy-s.get_height()//2))

        # Cursor zeichnen
        cc = self.cur_x - self.cam_x
        cr = self.cur_y - self.cam_y
        if 0 <= cc < COLS and 0 <= cr < ROWS:
            t_ms = pygame.time.get_ticks()
            alpha = int(128 + 100*math.sin(t_ms/200))
            surf = pygame.Surface((TILE,TILE), pygame.SRCALPHA)
            surf.fill((255,255,0,alpha))
            self.screen.blit(surf, (cc*TILE, cr*TILE))
            pygame.draw.rect(self.screen, C_CURSOR, (cc*TILE, cr*TILE, TILE, TILE), 2)

        # Tag/Nacht Overlay
        t = self.world_time
        darkness = 0
        if t > 1800 or t < 600:
            # Es wird dunkel
            if t > 2200 or t < 200: darkness = 180 # Maximale Dunkelheit
            elif t > 1800: darkness = int((t-1800) / 400 * 180)
            else: darkness = int((600-t) / 400 * 180)
        
        if darkness > 0:
            self.night_overlay.fill((0, 0, 40, darkness))
            # Lichtquellen ausstanzen
            for row in range(ROWS + 1):
                for col in range(COLS + 1):
                    wx, wy = self.cam_x + col, self.cam_y + row
                    tile = self.world.get(wx, wy)
                    binfo = B.get(tile)
                    if binfo and binfo.get("light"):
                        # Kreis zeichnen mit abnehmender Helligkeit
                        lx, ly = col*TILE + TILE//2, row*TILE + TILE//2
                        for r in range(3, 0, -1):
                            alpha = max(0, darkness - (r * 50))
                            pygame.draw.circle(self.night_overlay, (255, 255, 200, alpha), (lx, ly), r * TILE)
            
            self.screen.blit(self.night_overlay, (0, 0))

        # Partikel (Regen/Schnee) zeichnen
        for p in self.particles:
            px, py, speed, ptype = p
            if ptype == "rain":
                pygame.draw.line(self.screen, (100, 100, 255), (px, py), (px, py+4), 1)
            else: # snow
                pygame.draw.circle(self.screen, (255, 255, 255), (int(px), int(py)), 2)

    def _draw_panel(self):
        py = MAP_H
        pygame.draw.rect(self.screen, C_PANEL, (0, py, WIN_W, PANEL_H))
        pygame.draw.line(self.screen, C_YELLOW, (0, py), (WIN_W, py), 2)

        # Ausgewählter Block
        binfo = B.get(self.selected_block)
        bname = L.get(binfo["name"]) if binfo else self.selected_block
        bcolor = binfo["color"] if binfo else (100,100,100)
        pygame.draw.rect(self.screen, bcolor, (10, py+10, 30, 30))
        pygame.draw.rect(self.screen, C_WHITE, (10, py+10, 30, 30), 1)
        s = self.fnt_b.render(f"Block: {bname}  [Tab]", True, C_WHITE)
        self.screen.blit(s, (50, py+15))

        # Kasse & Zeit
        hh = int(self.world_time / 100) % 24
        mm = int((self.world_time % 100) * 0.6)
        time_str = f"{hh:02}:{mm:02}"
        inc_str = f" (+{self.last_income}€)" if self.last_income > 0 else ""
        s = self.fnt_b.render(f"Kasse: {self.money}€{inc_str}  |  Zeit: {time_str}", True, C_YELLOW)
        self.screen.blit(s, (10, py+50))
        s = self.fnt.render(f"X:{self.cur_x} Y:{self.cur_y}", True, C_GRAY)
        self.screen.blit(s, (WIN_W - 120, py+50))

        # KI-Eingabefeld
        if self.ai_input_active:
            pygame.draw.rect(self.screen, C_INPUT, (0, py+70, WIN_W, 46))
            pygame.draw.rect(self.screen, C_YELLOW, (0, py+70, WIN_W, 46), 2)
            prompt = self.fnt_b.render("🤖 KI > " + self.ai_input_text + "▌", True, C_YELLOW)
            self.screen.blit(prompt, (10, py+82))
        else:
            hint = self.fnt.render("K = KI-Befehl  |  Enter = Bauen  |  Entf = Entfernen  |  Tab = Block  |  F1 = Hilfe", True, C_GRAY)
            self.screen.blit(hint, (10, py+80))

        # KI-Ergebnis-Nachricht
        if self.ai_result_timer > 0:
            self.ai_result_timer -= 1
            col = C_GREEN if self.ai_result_ok else C_RED
            s = self.fnt_b.render(f"✓ {self.ai_result_msg}" if self.ai_result_ok
                                   else f"✗ {self.ai_result_msg}", True, col)
            self.screen.blit(s, (WIN_W - s.get_width() - 10, py+15))

    def _draw_help(self):
        overlay = pygame.Surface((WIN_W, MAP_H), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.screen.blit(overlay, (0,0))
        title = self.fnt_lg.render("── HILFE ──", True, C_YELLOW)
        self.screen.blit(title, (WIN_W//2 - title.get_width()//2, 20))
        for i, line in enumerate(self._help_lines):
            s = self.fnt.render(line, True, C_WHITE)
            self.screen.blit(s, (WIN_W//2 - 200, 60 + i*26))

    # ── Haupt-Loop ────────────────────────────────────────────────────────────
    def run(self):
        self._center_camera()
        while self.running:
            self.clock.tick(60)
            self._handle_events()
            
            # Welt-Updates
            self.world_time = (self.world_time + self.time_speed) % 2400
            self.world.update_npcs()
            
            # Ambiente
            tile_here = self.world.get(self.cur_x, self.cur_y)
            self.audio.update_ambience(self.world_time, at_water=(tile_here == "wasser"))
            
            # Wetter-Update
            self.weather_timer -= 1
            if self.weather_timer <= 0:
                old_w = self.weather
                self.weather = random.choice(["clear", "clear", "rain", "snow"])
                self.world.weather = self.weather # Sync mit Welt für NPCs
                self.weather_timer = random.randint(2000, 5000)
                if old_w != self.weather:
                    self.tts.say(L.get(f"weather_{self.weather}"))
            
            # Wetter-Effekte (Audio & Partikel)
            if self.weather != "clear":
                # Audio
                if self.weather == "rain":
                    self.audio.play_rain(0.6)
                    if random.random() < 0.002: self.audio.play_thunder()
                else: # snow
                    self.audio.play_rain(0.1) # Schnee ist leise

                # Partikel spawnen
                if len(self.particles) < 100:
                    self.particles.append([random.randint(0, WIN_W), 0, random.uniform(4, 7), self.weather])
            
            # Partikel bewegen
            for p in self.particles[:]:
                p[1] += p[2] # y += speed
                if p[1] > MAP_H:
                    self.particles.remove(p)
            
            # Einkommen
            self.income_timer += 1
            if self.income_timer >= 600: # Alle 10 Sekunden
                self.income_timer = 0
                inc = self.world.get_total_income()
                if inc > 0:
                    self.money += inc
                    self.last_income = inc
                    # Kurzes Feedback? Vielleicht nur in der UI
            
            # NPC Interaktion
            for npc in self.world.npcs:
                if npc.tile_x() == self.cur_x and npc.tile_y() == self.cur_y:
                    if npc.talk_timer <= 0:
                        msg = npc.get_greeting(L.current() == "de", self.weather)
                        self.tts.say(f"{npc.name}: {msg}")
                        npc.talk_timer = 600 # 10 Sekunden Pause

            self.screen.fill(C_BG)
            self._draw_world()
            self._draw_panel()
            if self.show_help:
                self._draw_help()
            pygame.display.flip()

        self.tts.stop()
        pygame.quit()

# ── Einstiegspunkt ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    game = WeltBauer()
    game.run()
