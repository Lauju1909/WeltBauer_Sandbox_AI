# WeltBauer 🏗️

**Minecraft-Style KI-Sandbox** — Baue deine eigene Welt mit KI-Unterstützung!

## Was ist WeltBauer?

WeltBauer ist ein blind-zugängliches 2D-Sandbox-Spiel in Python (pygame), bei dem du Schritt für Schritt eine eigene Welt erschaffen kannst:

- **Block-für-Block bauen** — Steinwände, Holz, Glas, Dächer, Türen, Bäume, Wasser, Lava, und vieles mehr
- **KI-Eingabefeld** — Tippe auf `K` und gib einen natürlichsprachigen Befehl ein:
  - `Baue eine Steinwand 5x3`
  - `Erstelle eine Frau namens Maria`
  - `Fülle den Bereich mit Wasser`
  - `Baue ein Haus 8x6 aus Ziegel`
- **Lebendige NPCs** — Frauen, Männer, Kinder, Tiere laufen durch deine Welt
- **100% blind-zugänglich** — Tolk/SAPI TTS, nur Tastatur nötig
- **Deutsch & Englisch** (`L`-Taste zum Wechseln)

## Starten

```bash
python main.py
```

**Voraussetzung:** `pygame` installiert (`pip install pygame`)

## Tastenbelegung

| Taste | Funktion |
|---|---|
| **Pfeiltasten** | Cursor bewegen |
| **Enter** | Aktuellen Block platzieren |
| **Entf** | Block entfernen |
| **Tab / Shift+Tab** | Nächster / Vorheriger Block |
| **K** | KI-Eingabefeld öffnen |
| **I** | Feld-Infos vorlesen |
| **S** | Stadtstatistik |
| **L** | Sprache DE/EN wechseln |
| **F1** | Hilfe |
| **F5** | Speichern |
| **F9** | Laden |
| **Ende** | Beenden |

## KI-Befehle (Beispiele)

```
Baue eine Wand 10 breit aus Stein
Erstelle eine Frau namens Lisa
Baue ein Haus 6x5 aus Ziegel
Fülle den Bereich 10 10 bis 20 20 mit Wasser
Platziere einen Baum
Erstelle einen Hund namens Bello
```

## Blöcke (Auswahl)

| Block | Beschreibung |
|---|---|
| Gras, Erde, Sand, Schnee | Boden-Typen |
| Baum, Blume, Busch, Pilz | Natur |
| Wasser, Lava, Eis | Flüssigkeiten |
| Steinwand, Ziegelwand, Holzwand, Glaswand | Baumaterial |
| Dach, Boden, Tür, Fenster | Haus-Teile |
| Zaun, Mauer, Straße, Brücke | Infrastruktur |
| Laterne, Bank, Brunnen, Denkmal | Dekoration |

## NPCs

| Typ | Beschreibung |
|---|---|
| Frau, Mann, Kind | Personen |
| Hund, Katze, Vogel | Haustiere |
| Kuh, Schaf | Nutztiere |

## Struktur

```
WeltBauer/
├── main.py          # Spielschleife + Rendering
├── world.py         # Weltraster, Massen-Operationen
├── blocks.py        # Alle Block-Definitionen
├── entities.py      # NPC-System
├── ai_command.py    # KI-Befehlsparser (LM Studio + Fallback)
├── speech.py        # Tolk/SAPI TTS-Wrapper
├── save_load.py     # JSON Speichern/Laden
├── lang_mgr.py      # Sprachverwaltung
├── lang/de.json     # Deutsche Texte
├── lang/en.json     # Englische Texte
└── saves/           # Spielstände
```
