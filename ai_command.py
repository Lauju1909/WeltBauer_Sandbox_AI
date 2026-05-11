"""KI-Befehlsparser: Natürlichsprachige Eingaben -> Weltaktionen
Versucht zuerst LM Studio (localhost:1234), dann Regex-Fallback."""
import re, json
import blocks as B
import entities as E

# ── LM Studio ────────────────────────────────────────────────────────────────
def _try_lm_studio(text, lang):
    """Ruft lokales LLM auf. Gibt JSON-Aktion zurück oder None."""
    try:
        import urllib.request
        system = (
            "Du bist ein Spielbefehlsparser fuer ein Sandbox-Spiel. "
            "Antworte AUSSCHLIESSLICH mit einem JSON-Objekt, ohne Erklaerung.\n"
            "Moegliche Aktionen:\n"
            '{"action":"place","block":"BLOCK_ID","x":X,"y":Y}\n'
            '{"action":"wall","block":"BLOCK_ID","x":X,"y":Y,"width":W,"height":H,"dir":"h/v"}\n'
            '{"action":"fill","block":"BLOCK_ID","x1":X1,"y1":Y1,"x2":X2,"y2":Y2}\n'
            '{"action":"house","x":X,"y":Y,"w":W,"h":H,"wall":"BLOCK_ID"}\n'
            '{"action":"npc","type":"TYPE","name":"NAME","x":X,"y":Y}\n'
            '{"action":"remove","x":X,"y":Y}\n'
            '{"action":"unknown"}\n'
            "Gueltige Block-IDs: gras,erde,sand,schnee,baum,blume,busch,fels,wasser,lava,eis,"
            "steinwand,ziegelwand,holzwand,glaswand,dach,boden,tuer,fenster,zaun,mauer,"
            "strasse,bruecke,laterne,bank,brunnen,denkmal,weizen,pilz,kaktus\n"
            "Gueltige NPC-Typen: frau,mann,kind,hund,katze,vogel,kuh,schaf\n"
            "Koordinaten 0-79 (x) und 0-59 (y). Wenn unklar, nutze x=40,y=30."
        )
        payload = json.dumps({
            "model": "local-model",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": text}
            ],
            "temperature": 0.1
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:1234/v1/chat/completions",
            data=payload,
            headers={"Content-Type":"application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            body = json.loads(resp.read())
            content = body["choices"][0]["message"]["content"].strip()
            # JSON aus Antwort extrahieren
            m = re.search(r'\{.*\}', content, re.DOTALL)
            if m:
                return json.loads(m.group())
    except Exception:
        pass
    return None

# ── Regex-Fallback ────────────────────────────────────────────────────────────
_NUM = r'(\d+)'

def _fallback(text, cx, cy, lang):
    """Einfacher Regex-Parser als Offline-Fallback."""
    t = text.lower().strip()

    # Zahlen aus Text extrahieren (Reihenfolge wichtig)
    nums = [int(x) for x in re.findall(r'\d+', t)]

    # 1) "erstelle/spawne <npc_typ> [namens <name>]"
    m = re.search(r'(erstell\w*|spawn\w*|erzeug\w*|create|add|mach\w*)\s+(\w+)', t)
    if m:
        raw_type = m.group(2)
        npc_t = E.resolve_type(raw_type)
        if npc_t:
            # Name suchen
            nm = re.search(r'namens?\s+([A-Za-zÄÖÜäöüß]+)', text, re.IGNORECASE)
            name = nm.group(1) if nm else ""
            x = nums[0] if len(nums)>=1 else cx
            y = nums[1] if len(nums)>=2 else cy
            return {"action":"npc","type":npc_t,"name":name,"x":x,"y":y}

    # 2) "baue haus [Bx By Bw Bh]"
    if re.search(r'haus|house|hütte|cottage', t):
        x = nums[0] if len(nums)>=1 else cx
        y = nums[1] if len(nums)>=2 else cy
        w = nums[2] if len(nums)>=3 else 5
        h = nums[3] if len(nums)>=4 else 4
        wall = _find_block(t)
        return {"action":"house","x":x,"y":y,"w":w,"h":h,"wall":wall or "steinwand"}

    # 3) "fülle [x1 y1 x2 y2] mit <block>"
    if re.search(r'füll\w*|fill\w*|bereich', t):
        block = _find_block(t) or "gras"
        if len(nums) >= 4:
            return {"action":"fill","block":block,"x1":nums[0],"y1":nums[1],"x2":nums[2],"y2":nums[3]}
        else:
            return {"action":"fill","block":block,"x1":cx,"y1":cy,"x2":cx+5,"y2":cy+5}

    # 4) "wand/mauer [breite höhe] [h/v] aus <block>"
    if re.search(r'wand|wall|mauer|zaun|fence', t):
        block = _find_block(t) or "steinwand"
        length = nums[0] if nums else 5
        height = nums[1] if len(nums)>=2 else 1
        dirn = "v" if re.search(r'hoch|vert\w*|vertical', t) else "h"
        return {"action":"wall","block":block,"x":cx,"y":cy,"width":length,"height":height,"dir":dirn}

    # 5) "abreiß / remove / löschen"
    if re.search(r'abreiß\w*|remove|lösch\w*|delete|demolish', t):
        x = nums[0] if len(nums)>=1 else cx
        y = nums[1] if len(nums)>=2 else cy
        return {"action":"remove","x":x,"y":y}

    # 6) "platziere/setze <block> [x y]"
    block = _find_block(t)
    if block:
        x = nums[0] if len(nums)>=1 else cx
        y = nums[1] if len(nums)>=2 else cy
        return {"action":"place","block":block,"x":x,"y":y}

    return {"action":"unknown"}

def _find_block(text):
    """Findet ersten bekannten Block-Namen im Text."""
    words = re.findall(r'\w+', text.lower())
    for w in words:
        bid = B.resolve(w)
        if bid:
            return bid
    return None

# ── Ausführen ────────────────────────────────────────────────────────────────
def execute(text, world, cx, cy, lang="de", money=None):
    """
    Verarbeitet Befehlstext. Gibt (Erfolg, Nachricht, neue_x, neue_y) zurück.
    money: None = kein Geld-Check (kreativ), sonst int-Budget.
    """
    # KI zuerst, Fallback danach
    action = _try_lm_studio(text, lang) or _fallback(text, cx, cy, lang)

    act = action.get("action","unknown")

    def _clamp_x(v): return max(0, min(world.w-1, int(v)))
    def _clamp_y(v): return max(0, min(world.h-1, int(v)))

    if act == "place":
        x,y = _clamp_x(action.get("x",cx)), _clamp_y(action.get("y",cy))
        bid = action.get("block","gras")
        binfo = B.get(bid)
        cost = binfo["cost"] if binfo else 0
        if money is not None and cost > money:
            return False, f"Zu wenig Geld. Kosten: {cost}", x, y
        world.set(x, y, bid)
        bname = binfo["name"] if binfo else bid
        return True, bname, x, y

    elif act == "wall":
        x,y = _clamp_x(action.get("x",cx)), _clamp_y(action.get("y",cy))
        bid = action.get("block","steinwand")
        dirn = action.get("dir","h")
        binfo = B.get(bid)
        if dirn == "h":
            length = min(int(action.get("width",5)), world.w - x)
            height = max(1, int(action.get("height",1)))
            for row in range(height):
                world.build_wall_h(x, y+row, length, bid)
            desc = f"Wand {length}x{height}"
        else:
            height = min(int(action.get("height",5)), world.h - y)
            world.build_wall_v(x, y, height, bid)
            desc = f"Wand 1x{height}"
        return True, desc, x, y

    elif act == "fill":
        x1,y1 = _clamp_x(action.get("x1",cx)), _clamp_y(action.get("y1",cy))
        x2,y2 = _clamp_x(action.get("x2",cx+5)), _clamp_y(action.get("y2",cy+5))
        bid = action.get("block","gras")
        world.fill_rect(x1,y1,x2,y2,bid)
        binfo = B.get(bid)
        return True, f"Bereich mit {binfo['name'] if binfo else bid} gefüllt", x1, y1

    elif act == "house":
        x,y = _clamp_x(action.get("x",cx)), _clamp_y(action.get("y",cy))
        w = max(3, min(int(action.get("w",5)), 15))
        h = max(3, min(int(action.get("h",4)), 10))
        wall = action.get("wall","steinwand")
        world.build_house(x, y, w, h, wall)
        return True, f"Haus {w}x{h} gebaut", x, y

    elif act == "npc":
        x,y = _clamp_x(action.get("x",cx)), _clamp_y(action.get("y",cy))
        ntype = action.get("type","mann")
        name  = action.get("name","") or ""
        npc = world.add_npc(x, y, ntype, name)
        return True, f"{npc.name} erschaffen", x, y

    elif act == "remove":
        x,y = _clamp_x(action.get("x",cx)), _clamp_y(action.get("y",cy))
        old = world.get(x,y)
        world.remove(x,y)
        binfo = B.get(old) if old else None
        return True, f"{binfo['name'] if binfo else old} entfernt", x, y

    else:
        return False, "Befehl nicht verstanden.", cx, cy
