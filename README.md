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
  - `Baue einen Freizeitpark`
- **Wirtschaftssystem** — Bestimmte Gebäude (Brunnen, Denkmäler, Freizeitparks) generieren regelmäßig Einkommen
- **Tag/Nacht-Zyklus** — Beobachte, wie es in deiner Welt dunkel wird
- **Beleuchtungssystem** — Laternen spenden nachts Licht und hellen die Umgebung auf
- **Lebendige NPCs** — Frauen, Männer, Kinder, Tiere laufen durch deine Welt. Sie reagieren nun auf das Wetter und suchen bei Regen oder Schnee Schutz in Gebäuden!
- **Wetter-System** — Dynamischer Wechsel zwischen Sonnenschein, Regen und Schnee inklusive Audio-Atmosphäre
- **100% blind-zugänglich** — Tolk/SAPI TTS, Bump-Sounds an Grenzen, Belegungs-Warnungen, nur Tastatur nötig.
- **Intelligente Sprach-Priorität** — Die KI sagt nun immer zuerst, WAS auf einem Feld ist und erst danach, WO es sich befindet (z.B. "Haus. Position 40, 30").
- **Proaktive KI-Partner** — Die KI wartet nicht nur auf dich! Sie macht Vorschläge, baut nachts Laternen oder hilft dir bei Regen mit Unterkünften.
- **KI-Agentik & Reflexion** — Die KI "denkt" nun nach, bevor sie handelt. Sie plant komplexe Bauvorhaben in mehreren Schritten und korrigiert sich selbst.
- **Internetsuche** — Wenn die KI etwas nicht weiß (z. B. "Wie sieht ein japanischer Garten aus?"), kann sie im Internet recherchieren, um authentische Bauten zu erstellen.
- **Akustische Status-Signale** — Neue Sounds signalisieren, wenn die KI "denkt", "sucht" oder "fertig" ist.
- **Deutsch & Englisch** (`L`-Taste zum Wechseln)

## Starten

### Windows
Doppelklicke einfach auf die [start_weltbauer.bat](file:///C:/Users/lauri/.gemini/antigravity/scratch/WeltBauer/start_weltbauer.bat). Das Skript kümmert sich um alles Weitere.

### Manuell
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
| **I** | Feld-Infos vorlesen (inkl. Bewohner & Einkommen) |
| **S** | Stadtstatistik (Gebäude, NPCs, Kontostand) |
| **L** | Sprache DE/EN wechseln |
| **F1** | Hilfe |
| **F5** | Speichern |
| **F9** | Laden |
| **Ende** | Beenden |

## 🤖 Die WeltBauer Kreativ-KI
Die integrierte KI (erfordert LM Studio auf `localhost:1234`) wurde massiv verbessert. Sie kann nun nicht mehr nur einzelne Blöcke setzen, sondern ganze **Szenen und komplexe Strukturen** erschaffen.

### Was du die KI fragen kannst:
- **Komplexe Bauten**: "Baue ein kleines Schloss aus Steinwänden mit einem Wassergraben."
- **Natur-Szenen**: "Erstelle einen dichten Wald mit Pilzen und Blumen."
- **Lern-Hilfe**: "Wie baue ich ein Karussell? Gib mir eine Anleitung und bau den Anfang."
- **Rollenspiel**: "Besiedle das Dorf mit 5 Menschen und nenne sie die Pioniere."

### Technische Details
Die KI nutzt nun ein **Multi-Aktions-System**. Ein einziger Befehl kann Dutzende von Aktionen auslösen (Blöcke setzen, Wände ziehen, Flächen füllen und mit dir sprechen). 

> [!TIP]
> Wenn du LM Studio nutzt, verwende ein Modell wie `Qwen2.5-Coder` oder `Llama-3` für beste Ergebnisse bei der räumlichen Planung.

## KI-Befehle (Beispiele)

```
Baue eine Wand 10 breit aus Stein
Erstelle eine Frau namens Lisa
Baue ein Haus 6x5 aus Ziegel
Baue einen Freizeitpark
Fülle den Bereich 10 10 bis 20 20 mit Wasser
Platziere einen Baum
Erstelle einen Hund namens Bello
```

## Blöcke (Auswahl)

| Block | Beschreibung | Einkommen |
|---|---|---|
| Gras, Erde, Sand, Schnee | Boden-Typen | - |
| Baum, Blume, Busch, Pilz | Natur | - |
| Wasser, Lava, Eis | Flüssigkeiten | - |
| Steinwand, Ziegelwand, Holzwand, Glaswand | Baumaterial | - |
| Dach, Boden, Tür, Fenster | Haus-Teile | - |
| Zaun, Mauer, Straße, Brücke | Infrastruktur | - |
| Laterne, Bank, Brunnen, Denkmal | Dekoration | Brunnen/Denkmal: Ja |
| Achterbahn, Riesenrad, Karussell, Eisstand | Freizeitpark | Ja (viel!) |
| Goldblock, Diamant, Hecke | Premium & Deko | Ja (Sehr viel!) |

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
