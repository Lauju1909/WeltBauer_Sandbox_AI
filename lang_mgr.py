"""Sprachverwaltung / Language Manager"""
import json, os

_lang = "de"
_strings = {}

def load(lang="de"):
    global _lang, _strings
    _lang = lang
    path = os.path.join(os.path.dirname(__file__), "lang", f"{lang}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            _strings = json.load(f)
    except Exception as e:
        print(f"Lang load error: {e}")

def get(key, **kwargs):
    text = _strings.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass
    return text

def current():
    return _lang

def toggle():
    load("en" if _lang == "de" else "de")
