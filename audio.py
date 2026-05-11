"""Audio-Manager: Erzeugt synthetische Klänge für verschiedene Materialien."""
import pygame
import math
import array
import random

class AudioManager:
    def __init__(self):
        self.enabled = True
        self.ambience_channel = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
        except Exception:
            self.enabled = False

    def _generate_beep(self, freq, ms=50, vol=0.3, wave_type="sine"):
        if not self.enabled: return
        try:
            sr = 44100
            n = int(sr * ms / 1000)
            samples = array.array('h', [0] * (n * 2))
            
            for i in range(n):
                fade = min(1.0, min(i, n - i) / max(1, sr * 0.01))
                if wave_type == "sine":
                    val = int(vol * 32767 * fade * math.sin(2 * math.pi * freq * i / sr))
                elif wave_type == "square":
                    val = int(vol * 32767 * fade * (1 if math.sin(2 * math.pi * freq * i / sr) > 0 else -1))
                elif wave_type == "noise":
                    val = int(vol * 32767 * fade * (random.random() * 2 - 1))
                else: # Default
                    val = int(vol * 32767 * fade * math.sin(2 * math.pi * freq * i / sr))
                
                samples[i*2] = val
                samples[i*2 + 1] = val
                
            sound = pygame.mixer.Sound(buffer=samples)
            sound.set_volume(vol)
            return sound
        except Exception:
            return None

    def play_step(self, block_id):
        """Spielt ein Schrittgeräusch passend zum Block."""
        if not self.enabled: return
        
        if block_id in ["gras", "erde"]:
            s = self._generate_beep(100, 60, 0.05, "noise")
        elif block_id in ["sand", "schnee"]:
            s = self._generate_beep(1000, 80, 0.04, "noise")
        elif block_id in ["steinwand", "mauer", "fels", "strasse", "stein"]:
            s = self._generate_beep(800, 30, 0.1, "sine")
        elif block_id in ["holzwand", "tuer", "zaun", "boden"]:
            s = self._generate_beep(300, 50, 0.15, "sine")
        elif block_id == "wasser":
            s = self._generate_beep(150, 100, 0.1, "sine")
        elif block_id == "lava":
            s = self._generate_beep(80, 200, 0.2, "square")
        else:
            s = self._generate_beep(400, 40, 0.05)
            
        if s: s.play()

    def play_bump(self):
        s = self._generate_beep(60, 150, 0.3, "square")
        if s: s.play()

    def play_build(self):
        s1 = self._generate_beep(523, 60, 0.2)
        if s1: s1.play()
        # Zeitverzögerter Zweit-Klang ist schwer ohne Threading hier, 
        # wir belassen es bei einem einfachen Signal.

    def play_remove(self):
        s = self._generate_beep(200, 180, 0.2, "sine")
        if s: s.play()

    def play_click(self):
        s = self._generate_beep(1000, 15, 0.1)
        if s: s.play()

    def update_ambience(self, world_time, at_water=False):
        """Spielt zufällige Hintergrundgeräusche."""
        if not self.enabled: return
        
        # Chance auf einen Klang pro Frame (sehr gering)
        if random.random() < 0.005:
            # Tag: Vögel
            if 500 < world_time < 1900:
                freq = random.randint(1500, 3000)
                dur  = random.randint(50, 150)
                s = self._generate_beep(freq, dur, 0.03, "sine")
                if s: s.play()
            # Nacht: Grillen/Eule
            else:
                if random.random() < 0.5: # Grillen (hohes Zirpen)
                    s = self._generate_beep(4000, 20, 0.02, "noise")
                    if s: s.play()
                else: # Eule (tiefes Uhu)
                    s = self._generate_beep(200, 300, 0.05, "sine")
                    if s: s.play()
        
        if at_water and random.random() < 0.01:
            s = self._generate_beep(150, 200, 0.04, "noise")
            if s: s.play()
