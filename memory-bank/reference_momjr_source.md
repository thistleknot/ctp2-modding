---
name: reference-momjr-source
description: The original MoM magic-system design lives at h:\games\ctp2\mom — consult it for mechanics/message content before asking the user; its SLIC API forms are the UNVERIFIED kind
metadata: 
  node_type: memory
  type: reference
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

`h:\games\ctp2\mom\mom\Scen0000\` is the **original Master of Magic magic-system
reference** (scenario.slc + civ_str/gl_str/scen_str). Check it FIRST for design intent,
mechanics, and message wording before asking the user for creative input — it is the
source material for the MoM sphere/magic layer.

**What it provides (mine for content/design):**
- Per-school themes & flavor: Chaos (high power, dangerous), Life (balanced), Death (high
  power + penalties), Nature (efficient). Message voice like "You have chosen the Life
  school of magic!".
- A richer intended design than the current committed sphere-gold economy: per-player
  magic-power pools (g_PlayerMagicPower / MaxMagicPower / PerTurn), power from
  population + magic buildings + wonders, school power multipliers, spells (Demon Strike
  = Chaos, Flame Strike = all schools) cast via KeyPress (D/F/M keys), mana nodes from
  Gold/Gems tiles, AI spell use. This is future scope beyond the current phases.

**Critical caveat — do NOT copy its SLIC API forms.** momjr uses the UNVERIFIED/aspirational
API (same class as the parked drafts that never ran): `CreateUnit("UNIT_X", p, loc)`
(string + 3 args), `city[0].hasBuilding("Sages Guild")` (string), `g.advance == "Life Magic"`
(string), `NotifyPlayer(...)`, `ShowMessageBox(...)`, `preference(...)`. The base-verified
forms the current MoM SLIC proved in-game are: `CreateUnit(p, UnitDB(UNIT_X), loc, flag)`,
`CityHasBuilding(city, BuildingDB(IMPROVE_X))`, `advance[0].type == AdvanceDB(ADVANCE_X)`,
`Message(g.player, 'KEY')`. Also note momjr's school numbering (1=Chaos,2=Life,3=Death,
4=Nature, no Sorcery) differs from the current seating (Life 1..Chaos 5, 5 spheres).

Applied 2026-07-11: Phase C blessing popups drew their voice from momjr but used the
proven Message()/scen_str plumbing. Related: [[mom-anarchy-science-regression]].

**Two distinct momjr locations (2026-07-13):**
- `H:\Games\ctp2\mom\mom\` — the **CTP2 port** (git repo): gamedata incl. `uniticon.txt` +
  `mom_uniticon.txt` (curated override; wins for advance-icon intent), 6120 unit-sprite
  PNGs (34 frames/unit under `units/<race>/<unit>/`), terrain PNGs. NO advance-portrait
  art and NO graphics/pictures — its uniticon references 482 GL pictures of which only
  ~129 exist in our install. See [[mom-advance-icons]].
- `H:\Games\civ2\MOMJR\MOMJR\` — the **Civ2 original**: Rules.txt (@CIVILIZE line 84 =
  advance order), Improvements.bmp (building/wonder art — NOT advances), Icons.bmp (UI
  chrome), Units.bmp, Pedia.txt, Events.txt. The sprite-extractor's BMP_DIR points here.
