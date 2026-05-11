"""NPC-System: Personen und Tiere die durch die Welt laufen"""
import random

NPC_TYPES = {
    "frau":   {"color":(255,150,200), "sym":"F", "name_de":"Frau",   "name_en":"Woman"},
    "mann":   {"color":(100,149,237), "sym":"M", "name_de":"Mann",   "name_en":"Man"},
    "kind":   {"color":(255,215,0),   "sym":"K", "name_de":"Kind",   "name_en":"Child"},
    "hund":   {"color":(139,90,43),   "sym":"H", "name_de":"Hund",   "name_en":"Dog"},
    "katze":  {"color":(150,150,150), "sym":"K", "name_de":"Katze",  "name_en":"Cat"},
    "vogel":  {"color":(50,200,50),   "sym":"V", "name_de":"Vogel",  "name_en":"Bird"},
    "kuh":    {"color":(230,200,150), "sym":"K", "name_de":"Kuh",    "name_en":"Cow"},
    "schaf":  {"color":(240,240,240), "sym":"S", "name_de":"Schaf",  "name_en":"Sheep"},
}

NPC_ALIASES = {
    # DE
    "frau":"frau","mann":"mann","kind":"kind","hund":"hund","katze":"katze",
    "vogel":"vogel","kuh":"kuh","schaf":"schaf","tier":"hund","mensch":"mann",
    # EN
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
        info = NPC_TYPES.get(npc_type, NPC_TYPES["mann"])
        self.color = info["color"]
        self.sym   = info["sym"]
        self.name  = name or info["name_de"]
        self.name_en = info["name_en"]

        self.move_timer  = 0
        self.move_delay  = random.randint(40, 90)   # frames zwischen Schritten
        self.dx = 0
        self.dy = 0
        self._pick_dir()

    def _pick_dir(self):
        dirs = [(1,0),(-1,0),(0,1),(0,-1),(0,0)]
        self.dx, self.dy = random.choice(dirs)

    def update(self, world):
        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return
        self.move_timer = 0

        # Zufällig neue Richtung wählen (30 % Chance)
        if random.random() < 0.3:
            self._pick_dir()

        nx = int(self.x + self.dx)
        ny = int(self.y + self.dy)

        if world.can_npc_enter(nx, ny):
            self.x = float(nx)
            self.y = float(ny)
        else:
            self._pick_dir()   # Hindernis -> neue Richtung

    def display_name(self, lang="de"):
        return self.name

    def tile_x(self):
        return int(self.x)

    def tile_y(self):
        return int(self.y)

def resolve_type(raw):
    return NPC_ALIASES.get(raw.lower().strip())
