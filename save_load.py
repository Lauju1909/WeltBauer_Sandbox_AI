"""Speichern & Laden (JSON)"""
import json, os

SAVE_PATH = os.path.join(os.path.dirname(__file__), "saves", "world.json")

def save(world, cx, cy, lang, money, time, weather):
    data = {
        "cursor": {"x": cx, "y": cy},
        "lang": lang,
        "money": money,
        "time": time,
        "weather": weather,
        "world": world.to_dict()
    }
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load(world):
    if not os.path.exists(SAVE_PATH):
        return None
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    world.from_dict(data.get("world", {}))
    return data
