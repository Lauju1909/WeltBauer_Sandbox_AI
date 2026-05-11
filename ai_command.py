"""KI-Befehlsparser: Natürlichsprachige Eingaben -> Weltaktionen
Versucht zuerst LM Studio (localhost:1234), dann Regex-Fallback."""
import re, json
import blocks as B
import entities as E

# ── LM Studio ────────────────────────────────────────────────────────────────
def _try_lm_studio(text, lang):
    """Ruft lokales LLM auf. Gibt JSON-Aktion(en) zurück oder None."""
    try:
        import urllib.request
        system = (
            "Du bist ein kreativer Spielbefehlsparser fuer ein Sandbox-Spiel namens 'WeltBauer'.\n"
            "Deine Aufgabe ist es, Spielerwuensche in Weltaktionen umzusetzen.\n"
            "Antworte AUSSCHLIESSLICH mit einem JSON-Objekt oder einer Liste von JSON-Objekten.\n"
            "Du kannst ALLES bauen, was der Spieler sich wuenscht, indem du einfache Aktionen kombinierst.\n"
            "\n"
            "Moegliche Aktionen:\n"
            '{"action":"place","block":"BLOCK_ID","x":X,"y":Y}\n'
            '{"action":"wall","block":"BLOCK_ID","x":X,"y":Y,"width":W,"height":H,"dir":"h/v"}\n'
            '{"action":"fill","block":"BLOCK_ID","x1":X1,"y1":Y1,"x2":X2,"y2":Y2}\n'
            '{"action":"house","x":X,"y":Y,"w":W,"h":H,"wall":"BLOCK_ID"}\n'
            '{"action":"npc","type":"TYPE","name":"NAME","x":X,"y":Y} (Erschaffe Menschen/Tiere)\n'
            '{"action":"remove","x":X,"y":Y}\n'
            '{"action":"talk","text":"NACHRICHT"} (Erklaere, was du tust oder gib Bauanleitungen)\n'
            "\n"
            "KREATIVITAET & KOMPLEXITAET:\n"
            "Wenn der Spieler etwas Komplexes moechte (z.B. Karussell, Riesenrad, Schloss, Wald, Jahrmarkt),\n"
            "nutze eine LISTE von Aktionen. Baue es detailreich!\n"
            "Beispiel fuer 'Baue ein Karussell':\n"
            '[\n'
            '  {"action":"talk","text":"Ich baue ein buntes Karussell für deinen Park!"},\n'
            '  {"action":"place","block":"karussell","x":cx,"y":cy},\n'
            '  {"action":"place","block":"laterne","x":cx+1,"y":cy},\n'
            '  {"action":"place","block":"laterne","x":cx-1,"y":cy},\n'
            '  {"action":"npc","type":"kind","name":"Timmy","x":cx,"y":cy}\n'
            ']\n'
            "\n"
            "Beispiel fuer 'Setze eine Frau namens Lisa hierher':\n"
            '{"action":"npc","type":"frau","name":"Lisa","x":cx,"y":cy}\n'
            "\n"
            "Gueltige Block-IDs: gras,erde,sand,schnee,baum,blume,busch,fels,wasser,lava,eis,"
            "steinwand,ziegelwand,holzwand,glaswand,dach,boden,tuer,fenster,zaun,mauer,"
            "strasse,bruecke,laterne,bank,brunnen,denkmal,weizen,pilz,kaktus,"
            "achterbahn,karussell,riesenrad,eisstand\n"
            "Gueltige NPC-Typen: frau,mann,kind,hund,katze,vogel,kuh,schaf\n"
            "Koordinaten: 0-79 (x) und 0-59 (y). Nutze den aktuellen Cursor (cx, cy) als Referenz.\n"
            "Wichtig: Du bist der Schöpfer dieser Welt. Wenn der Spieler 'alles' machen will, hilf ihm dabei!"
        )
        payload = json.dumps({
            "model": "local-model",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": text}
            ],
            "temperature": 0.3
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:1234/v1/chat/completions",
            data=payload,
            headers={"Content-Type":"application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = json.loads(resp.read())
            content = body["choices"][0]["message"]["content"].strip()
            # JSON/Liste aus Antwort extrahieren
            m = re.search(r'\[.*\]|\{.*\}', content, re.DOTALL)
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

    # 5) "freizeitpark / park"
    if re.search(r'freizeitpark|park|amusement', t):
        x = nums[0] if len(nums)>=1 else cx
        y = nums[1] if len(nums)>=2 else cy
        return {"action":"park","x":x,"y":y}

    # 6) "abreiß / remove / löschen"
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
    Verarbeitet Befehlstext. Gibt (Erfolg, Nachricht, neue_x, neue_y, kosten) zurück.
    Kann nun auch Listen von Aktionen verarbeiten.
    """
    ai_resp = _try_lm_studio(text, lang)
    if ai_resp:
        if isinstance(ai_resp, list):
            actions = ai_resp
        else:
            actions = [ai_resp]
    else:
        actions = [_fallback(text, cx, cy, lang)]

    total_success = False
    total_cost = 0
    nx, ny = cx, cy
    
    # Für die Rückmeldung sammeln wir alle Texte
    messages = []

    for action in actions:
        act = action.get("action", "unknown")
        
        def _clamp_x(v): return max(0, min(world.w-1, int(v)))
        def _clamp_y(v): return max(0, min(world.h-1, int(v)))

        if act == "talk":
            messages.append(action.get("text", ""))
            total_success = True # Talk gilt als Erfolg

        elif act == "place":
            x,y = _clamp_x(action.get("x",nx)), _clamp_y(action.get("y",ny))
            bid = action.get("block","gras")
            binfo = B.get(bid)
            cost = binfo["cost"] if binfo else 0
            if money is not None and (total_cost + cost) > money:
                messages.append(f"Nicht genug Geld für {bid}")
            else:
                world.set(x, y, bid)
                total_cost += cost
                total_success = True
                nx, ny = x, y

        elif act == "wall":
            x,y = _clamp_x(action.get("x",nx)), _clamp_y(action.get("y",ny))
            bid = action.get("block","steinwand")
            dirn = action.get("dir","h")
            length = int(action.get("width",5))
            height = max(1, int(action.get("height",1)))
            binfo = B.get(bid)
            cost = (length * height) * (binfo["cost"] if binfo else 10)
            
            if money is not None and (total_cost + cost) > money:
                messages.append(f"Wand zu teuer")
            else:
                if dirn == "h":
                    length = min(length, world.w - x)
                    for row in range(height): world.build_wall_h(x, y+row, length, bid)
                else:
                    height = min(height, world.h - y)
                    world.build_wall_v(x, y, height, bid)
                total_cost += cost
                total_success = True
                nx, ny = x, y

        elif act == "fill":
            x1,y1 = _clamp_x(action.get("x1",nx)), _clamp_y(action.get("y1",ny))
            x2,y2 = _clamp_x(action.get("x2",nx+5)), _clamp_y(action.get("y2",ny+5))
            bid = action.get("block","gras")
            binfo = B.get(bid)
            count = (abs(x2-x1)+1) * (abs(y2-y1)+1)
            cost = count * (binfo["cost"] if binfo else 5)
            if money is not None and (total_cost + cost) > money:
                messages.append("Fläche zu teuer")
            else:
                world.fill_rect(x1, y1, x2, y2, bid)
                total_cost += cost
                total_success = True

        elif act == "house":
            x,y = _clamp_x(action.get("x",nx)), _clamp_y(action.get("y",ny))
            w = max(3, min(int(action.get("w",5)), 15))
            h = max(3, min(int(action.get("h",4)), 10))
            wall = action.get("wall","steinwand")
            cost = ((w*h) + (2*(w+h)) + w) * (B.get(wall)["cost"] if B.get(wall) else 20)
            if money is not None and (total_cost + cost) > money:
                messages.append("Haus zu teuer")
            else:
                world.build_house(x, y, w, h, wall)
                total_cost += cost
                total_success = True

        elif act == "npc":
            x,y = _clamp_x(action.get("x",nx)), _clamp_y(action.get("y",ny))
            ntype = action.get("type","mann")
            cost = 500
            if money is not None and (total_cost + cost) > money:
                messages.append("Nicht genug Geld für NPC")
            else:
                world.add_npc(x, y, ntype, action.get("name",""))
                total_cost += cost
                total_success = True

        elif act == "park":
            x,y = _clamp_x(action.get("x",nx)), _clamp_y(action.get("y",ny))
            cost = 5000
            if money is not None and (total_cost + cost) > money:
                messages.append("Park zu teuer")
            else:
                world.build_park(x, y)
                total_cost += cost
                total_success = True

        elif act == "remove":
            x,y = _clamp_x(action.get("x",nx)), _clamp_y(action.get("y",ny))
            world.remove(x, y)
            total_success = True

    if not messages and total_success:
        messages.append("Befehl ausgeführt.")
    elif not total_success:
        messages.append("Befehl nicht verstanden oder zu teuer.")

    return total_success, " ".join(messages), nx, ny, total_cost
