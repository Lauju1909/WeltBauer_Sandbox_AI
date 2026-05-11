"""Weltraster, Kamera und Karten-Logik"""
import blocks as B
import entities as E

WORLD_W = 80
WORLD_H = 60

class World:
    def __init__(self):
        self.w = WORLD_W
        self.h = WORLD_H
        # Standardmäßig: alles Gras
        self.tiles = [["gras"] * self.w for _ in range(self.h)]
        self.npcs  = []

    # ── Kacheln ─────────────────────────────────────────────────────
    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.tiles[y][x]
        return None

    def set(self, x, y, block_id):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.tiles[y][x] = block_id
            return True
        return False

    def remove(self, x, y):
        """Kachel entfernen (zurück zu Gras)."""
        return self.set(x, y, "gras")

    def can_npc_enter(self, x, y):
        b = self.get(x, y)
        if b is None: return False
        info = B.get(b)
        if info is None: return True
        return info.get("pass", True)

    # ── Massen-Operationen (für KI-Befehle) ─────────────────────────
    def fill_rect(self, x1, y1, x2, y2, block_id):
        """Füllt Rechteck (inkl. Ränder) mit Block."""
        for y in range(min(y1,y2), max(y1,y2)+1):
            for x in range(min(x1,x2), max(x1,x2)+1):
                self.set(x, y, block_id)

    def build_wall_h(self, x, y, length, block_id):
        """Horizontale Wand der Länge `length`."""
        for i in range(length):
            self.set(x+i, y, block_id)

    def build_wall_v(self, x, y, height, block_id):
        """Vertikale Wand der Höhe `height`."""
        for i in range(height):
            self.set(x, y+i, block_id)

    def build_rect_outline(self, x1, y1, x2, y2, block_id):
        """Nur den Rahmen eines Rechtecks setzen."""
        x1,x2 = min(x1,x2), max(x1,x2)
        y1,y2 = min(y1,y2), max(y1,y2)
        for x in range(x1, x2+1):
            self.set(x, y1, block_id)
            self.set(x, y2, block_id)
        for y in range(y1, y2+1):
            self.set(x1, y, block_id)
            self.set(x2, y, block_id)

    def build_house(self, x, y, w, h, wall_id="steinwand", roof_id="dach", floor_id="boden"):
        """Komplett-Haus: Boden + Rahmen + Dach-Reihe."""
        # Boden
        self.fill_rect(x, y, x+w-1, y+h-1, floor_id)
        # Wände (Rahmen)
        self.build_rect_outline(x, y, x+w-1, y+h-1, wall_id)
        # Dach oben
        for i in range(w):
            self.set(x+i, y-1, roof_id)
        # Tür (Mitte)
        self.set(x + w//2, y+h-1, "tuer")

    # ── NPCs ────────────────────────────────────────────────────────
    def add_npc(self, x, y, npc_type="mann", name=""):
        npc = E.NPC(x, y, npc_type, name)
        self.npcs.append(npc)
        return npc

    def npcs_at(self, x, y):
        return [n for n in self.npcs if n.tile_x() == x and n.tile_y() == y]

    def update_npcs(self):
        for npc in self.npcs:
            npc.update(self)

    # ── Statistik ───────────────────────────────────────────────────
    def stats(self):
        counts = {}
        for row in self.tiles:
            for cell in row:
                counts[cell] = counts.get(cell, 0) + 1
        total = sum(v for k,v in counts.items() if k != "gras")
        return {"placed": total, "npcs": len(self.npcs), "counts": counts}

    # ── Serialisierung ──────────────────────────────────────────────
    def to_dict(self):
        return {
            "tiles": self.tiles,
            "npcs": [{"x":n.x,"y":n.y,"type":n.type,"name":n.name} for n in self.npcs]
        }

    def from_dict(self, d):
        self.tiles = d.get("tiles", self.tiles)
        self.npcs  = []
        for nd in d.get("npcs", []):
            self.npcs.append(E.NPC(nd["x"], nd["y"], nd.get("type","mann"), nd.get("name","")))
