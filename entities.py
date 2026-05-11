"""NPC-System: Personen und Tiere mit KI-Verhalten"""
import random
import blocks as B

NPC_TYPES = {
    "frau":   {"color":(255,150,200), "sym":"F", "name_de":"Frau",   "name_en":"Woman", "speed":1.0, "pref":["pfad","strasse","boden","tuer"]},
    "mann":   {"color":(100,149,237), "sym":"M", "name_de":"Mann",   "name_en":"Man",   "speed":1.0, "pref":["pfad","strasse","boden","tuer"]},
    "kind":   {"color":(255,215,0),   "sym":"K", "name_de":"Kind",   "name_en":"Child", "speed":1.2, "pref":["gras","pfad","denkmal"]},
    "hund":   {"color":(139,90,43),   "sym":"H", "name_de":"Hund",   "name_en":"Dog",   "speed":1.3, "pref":["gras","pfad"]},
    "katze":  {"color":(150,150,150), "sym":"K", "name_de":"Katze",  "name_en":"Cat",   "speed":0.8, "pref":["zaun","mauer","dach","bank"]},
    "vogel":  {"color":(50,200,50),   "sym":"V", "name_de":"Vogel",  "name_en":"Bird",  "speed":0.5, "pref":["baum","brunnen","denkmal"]},
    "kuh":    {"color":(230,200,150), "sym":"K", "name_de":"Kuh",    "name_en":"Cow",   "speed":0.4, "pref":["gras","weizen"]},
    "schaf":  {"color":(240,240,240), "sym":"S", "name_de":"Schaf",  "name_en":"Sheep", "speed":0.4, "pref":["gras","weizen"]},
}

NPC_ALIASES = {
    "frau":"frau","mann":"mann","kind":"kind","hund":"hund","katze":"katze",
    "vogel":"vogel","kuh":"kuh","schaf":"schaf","tier":"hund","mensch":"mann",
    "woman":"frau","man":"mann","child":"kind","dog":"hund","cat":"katze",
    "bird":"vogel","cow":"kuh","sheep":"schaf","animal":"hund","person":"mann",
}

class NPC:
    _id = 0

    def __init__(self, x, y, npc_type="mann", name=""):
        NPC._id += 1
        self.id = NPC._id
        self.x = float(x)
        self.y = float(y)
        self.type = npc_type
        self.info = NPC_TYPES.get(npc_type, NPC_TYPES["mann"])
        self.color = self.info["color"]
        self.sym   = self.info["sym"]
        self.name  = name or self.info["name_de"]
        self.name_en = self.info["name_en"]

        self.move_timer  = 0
        self.move_delay  = int(random.randint(40, 90) / self.info.get("speed", 1.0))
        self.talk_timer  = 0
        self.dx, self.dy = 0, 0
        self._pick_dir()

    def _pick_dir(self, world=None):
        """Wählt eine Richtung. Wenn world gegeben, bevorzugt sie Präferenzen."""
        dirs = [(1,0),(-1,0),(0,1),(0,-1),(0,0)]
        if world:
            # Bewerte Richtungen
            scores = []
            for dx, dy in dirs:
                nx, ny = int(self.x + dx), int(self.y + dy)
                if not world.can_npc_enter(nx, ny):
                    scores.append(-100)
                    continue
                
                bid = world.get(nx, ny)
                binfo = B.get(bid)
                score = 0
                if binfo and binfo.get("danger"): score -= 50
                if bid in self.info.get("pref", []): score += 20
                
                # Zufalls-Komponente
                score += random.randint(0, 10)
                scores.append(score)
            
            # Beste Richtung wählen
            max_score = max(scores)
            best_indices = [i for i, s in enumerate(scores) if s == max_score]
            self.dx, self.dy = dirs[random.choice(best_indices)]
        else:
            self.dx, self.dy = random.choice(dirs)

    def update(self, world):
        self.move_timer += 1
        if self.talk_timer > 0: self.talk_timer -= 1
        
        if self.move_timer < self.move_delay:
            return
        self.move_timer = 0

        # Zufällig neue Richtung wählen (oder wenn blockiert)
        if random.random() < 0.2:
            self._pick_dir(world)

        nx, ny = int(self.x + self.dx), int(self.y + self.dy)

        # Gefahr-Check (Lava)
        bid = world.get(nx, ny)
        binfo = B.get(bid)
        if binfo and binfo.get("danger"):
            self._pick_dir(world) # Sofort neue Richtung suchen
            return

        if world.can_npc_enter(nx, ny):
            self.x, self.y = float(nx), float(ny)
        else:
            self._pick_dir(world)

    def get_greeting(self, is_german=True):
        """Gibt einen zufälligen Kommentar zurück."""
        if self.type in ["frau", "mann", "kind"]:
            msgs = ["Hallo!", "Schöner Tag heute.", "Was baust du da?", "Ich gehe nur spazieren."] if is_german else ["Hello!", "Nice day.", "What are you building?", "Just taking a walk."]
        else:
            # Tiere
            sounds = {
                "hund": ["Wuff!", "Hechel..."] if is_german else ["Woof!", "Panting..."],
                "katze": ["Miau.", "Schnurrr."] if is_german else ["Meow.", "Purr."],
                "vogel": ["Piep!", "Zwitscher!"] if is_german else ["Tweet!", "Chirp!"],
                "kuh": ["Muh!", "Gras ist lecker."] if is_german else ["Moo!", "Grass is tasty."],
                "schaf": ["Mäh!", "Wolle!"] if is_german else ["Baa!", "Wool!"],
            }
            msgs = sounds.get(self.type, ["..."])
        return random.choice(msgs)

    def tile_x(self): return int(self.x)
    def tile_y(self): return int(self.y)

def resolve_type(raw):
    return NPC_ALIASES.get(raw.lower().strip())
