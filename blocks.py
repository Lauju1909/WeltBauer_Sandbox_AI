"""Alle Block-Definitionen: Farbe, Kategorie, Kosten, Symbol"""

# Kategorien
NAT = "natur"
BAU = "bau"
FLU = "fluessig"
DEK = "deko"
INF = "infra"

# Format: id -> {name_key, color(R,G,B), cat, solid, passable, cost, sym}
BLOCKS = {
    # ── Boden ──────────────────────────────────────────────────────
    "gras":       {"name":"b_gras",       "color":(76,153,0),    "cat":NAT, "solid":True,  "pass":True,  "cost":0,   "sym":"~"},
    "erde":       {"name":"b_erde",       "color":(101,67,33),   "cat":NAT, "solid":True,  "pass":True,  "cost":5,   "sym":"."},
    "sand":       {"name":"b_sand",       "color":(244,215,103), "cat":NAT, "solid":True,  "pass":True,  "cost":5,   "sym":"s"},
    "schnee":     {"name":"b_schnee",     "color":(230,240,255), "cat":NAT, "solid":True,  "pass":True,  "cost":0,   "sym":"*"},
    "pfad":       {"name":"b_pfad",       "color":(180,150,100), "cat":INF, "solid":True,  "pass":True,  "cost":15,  "sym":"="},
    "eis":        {"name":"b_eis",        "color":(173,216,230), "cat":NAT, "solid":True,  "pass":True,  "cost":20,  "sym":"#"},

    # ── Natur ──────────────────────────────────────────────────────
    "baum":       {"name":"b_baum",       "color":(0,100,0),     "cat":NAT, "solid":True,  "pass":False, "cost":30,  "sym":"T"},
    "blume":      {"name":"b_blume",      "color":(255,105,180), "cat":DEK, "solid":False, "pass":True,  "cost":10,  "sym":"f"},
    "busch":      {"name":"b_busch",      "color":(34,120,15),   "cat":NAT, "solid":True,  "pass":False, "cost":20,  "sym":"b"},
    "fels":       {"name":"b_fels",       "color":(100,100,100), "cat":NAT, "solid":True,  "pass":False, "cost":10,  "sym":"F"},
    "weizen":     {"name":"b_weizen",     "color":(240,200,50),  "cat":NAT, "solid":False, "pass":True,  "cost":15,  "sym":"w"},
    "pilz":       {"name":"b_pilz",       "color":(180,50,50),   "cat":NAT, "solid":False, "pass":True,  "cost":10,  "sym":"p"},
    "kaktus":     {"name":"b_kaktus",     "color":(0,180,0),     "cat":NAT, "solid":True,  "pass":False, "cost":20,  "sym":"k"},

    # ── Flüssigkeiten ──────────────────────────────────────────────
    "wasser":     {"name":"b_wasser",     "color":(30,144,255),  "cat":FLU, "solid":False, "pass":False, "cost":0,   "sym":"≈"},
    "lava":       {"name":"b_lava",       "color":(255,80,0),    "cat":FLU, "solid":False, "pass":False, "cost":0,   "sym":"!"},

    # ── Baumaterial ───────────────────────────────────────────────
    "steinwand":  {"name":"b_steinwand",  "color":(90,90,90),    "cat":BAU, "solid":True,  "pass":False, "cost":50,  "sym":"W"},
    "ziegelwand": {"name":"b_ziegelwand", "color":(178,65,35),   "cat":BAU, "solid":True,  "pass":False, "cost":60,  "sym":"Z"},
    "holzwand":   {"name":"b_holzwand",   "color":(139,90,43),   "cat":BAU, "solid":True,  "pass":False, "cost":40,  "sym":"H"},
    "glaswand":   {"name":"b_glaswand",   "color":(200,230,255), "cat":BAU, "solid":True,  "pass":False, "cost":80,  "sym":"G"},
    "dach":       {"name":"b_dach",       "color":(150,50,50),   "cat":BAU, "solid":True,  "pass":False, "cost":70,  "sym":"^"},
    "boden":      {"name":"b_boden",      "color":(200,180,140), "cat":BAU, "solid":True,  "pass":True,  "cost":30,  "sym":"_"},
    "tuer":       {"name":"b_tuer",       "color":(100,60,20),   "cat":BAU, "solid":True,  "pass":True,  "cost":100, "sym":"D"},
    "fenster":    {"name":"b_fenster",    "color":(150,220,255), "cat":BAU, "solid":True,  "pass":False, "cost":90,  "sym":"O"},
    "zaun":       {"name":"b_zaun",       "color":(120,80,40),   "cat":BAU, "solid":True,  "pass":False, "cost":25,  "sym":"|"},
    "mauer":      {"name":"b_mauer",      "color":(60,60,60),    "cat":BAU, "solid":True,  "pass":False, "cost":45,  "sym":"M"},

    # ── Infrastruktur ─────────────────────────────────────────────
    "strasse":    {"name":"b_strasse",    "color":(80,80,80),    "cat":INF, "solid":True,  "pass":True,  "cost":20,  "sym":"-"},
    "bruecke":    {"name":"b_bruecke",    "color":(120,100,60),  "cat":INF, "solid":True,  "pass":True,  "cost":150, "sym":"+"},

    # ── Dekoration ────────────────────────────────────────────────
    "laterne":    {"name":"b_laterne",    "color":(255,215,0),   "cat":DEK, "solid":True,  "pass":False, "cost":80,  "sym":"l"},
    "bank":       {"name":"b_bank",       "color":(139,90,43),   "cat":DEK, "solid":True,  "pass":False, "cost":60,  "sym":"B"},
    "brunnen":    {"name":"b_brunnen",    "color":(64,164,223),  "cat":DEK, "solid":True,  "pass":False, "cost":200, "sym":"o"},
    "denkmal":    {"name":"b_denkmal",    "color":(192,192,192), "cat":DEK, "solid":True,  "pass":False, "cost":500, "sym":"X"},
}

# Alias-Tabelle: Tippeingaben -> Block-ID (Deutsch + Englisch)
ALIASES = {
    # Deutsch
    "gras":"gras","erde":"erde","sand":"sand","schnee":"schnee","pfad":"pfad","eis":"eis",
    "baum":"baum","blume":"blume","busch":"busch","fels":"fels","stein":"steinwand",
    "weizen":"weizen","pilz":"pilz","kaktus":"kaktus",
    "wasser":"wasser","lava":"lava",
    "steinwand":"steinwand","ziegelwand":"ziegelwand","ziegel":"ziegelwand",
    "holzwand":"holzwand","holz":"holzwand","glaswand":"glaswand","glas":"glaswand",
    "dach":"dach","boden":"boden","fussboden":"boden","tür":"tuer","tuer":"tuer",
    "fenster":"fenster","zaun":"zaun","mauer":"mauer",
    "straße":"strasse","strasse":"strasse","brücke":"bruecke","bruecke":"bruecke",
    "laterne":"laterne","bank":"bank","brunnen":"brunnen","denkmal":"denkmal",
    # Englisch
    "grass":"gras","dirt":"erde","snow":"schnee","path":"pfad","ice":"eis",
    "tree":"baum","flower":"blume","bush":"busch","rock":"fels","wheat":"weizen",
    "mushroom":"pilz","cactus":"kaktus","water":"wasser",
    "stone":"steinwand","brick":"ziegelwand","wood":"holzwand","glass":"glaswand",
    "roof":"dach","floor":"boden","door":"tuer","window":"fenster",
    "fence":"zaun","wall":"mauer","road":"strasse","bridge":"bruecke",
    "lantern":"laterne","bench":"bank","fountain":"brunnen","monument":"denkmal",
}

def resolve(name):
    """Gibt Block-ID zurück oder None."""
    return ALIASES.get(name.lower().strip())

def get(block_id):
    return BLOCKS.get(block_id)
