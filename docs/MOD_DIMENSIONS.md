# Mod Dimensions Reference

**1st-class citizen.** This file lists every game dimension in the Civ2 MoMJR and CTP2 MoM mods,
with canonical source files, image files, and record counts. Update this alongside
`dimension_inventory.md` whenever dimensions change.
`Scenarios\mom\mom_dimension_inventory.xlsx` is the Excel control-plane export of
these surfaces and must be regenerated on every scenario update; it is a generated
artifact, not a hand-edited workbook.

Patching tool: `Scenarios/mom/tools/ctpedit.py`
Workbook export: `Scenarios/mom/mom_dimension_inventory.xlsx`

---

## Civ2 → CTP2 Dimension Mapping

| Civ2 (MOMJR) | Count | CTP2 (MoM) | Count | Notes |
|---|---|---|---|---|
| Advances | 100 | Advances | 100 | 1:1 mapped; IDs translated |
| Units | 62 | Units | 62 | 1:1; UNIT_CLERIC + UNIT_APPRENTICE_MAGE masked out |
| City Improvements | 38 | City Improvements / Buildings | 68 | CTP2 adds 30 CTP2-only buildings with proxy TGAs |
| Wonders (sub-type of @IMPROVE + @ENDWONDER) | 29 | Wonders | 30 | Split into own dimension; 1 extra (XAPOLLO_PROGRAM stub) |
| Terrain | 33 | Terrain | 26 | CTP2 collapses some terrain types |
| Caravan commodities / trade lanes | — | Goods | 72 | Expanded in CTP2; no 1:1 Civ2 record |
| Tile Improvements | 8 | Tile Improvements | 81 | CTP2 greatly expands; Civ2 has basic 8 |
| Governments | 7 | Governments | 5 | Pruned for MoM theme |
| Orders / command text | — | Unit Orders | 47 | Text-only; Civ2 @ORDERS maps loosely |
| Leaders / Personalities | 23 | Civilizations | 70 | Civ2: 1 leader per civ; CTP2: full civ records |
| Events | — | SLIC | — | Civ2 events → CTP2 script events; translation unclear; may relate to epochs |
| Civilopedia / labels / game text | — | Concepts | 61 | GL entry text + Civilopedia descriptions |
| Scenario art sheets and sounds | — | Scenario Art | — | BMP sprite sheets → TGA + sprite atlas |
| — | — | Goods Icons | 17 | CTP2-specific icon dimension |
| — | — | Government Icons | 5 | CTP2-specific icon dimension |
| — | — | Terrain Icons | 24 | CTP2-specific icon dimension |
| — | — | Wonder Icons | 36 | CTP2-specific icon dimension |
| — | — | Wonder Movies | 30 | CTP2-specific movie dimension |

---

## CTP2 MoM Dimensions — Full Kit

### 1. Advances {100}
- **Data:** `Scenarios/mom/scen0000/default/gamedata/Advance.txt`
- **CSV:** `Scenarios/mom/tools/momjr_csv/advances.csv`
- **Icons (TGA):** `Scenarios/mom/scen0000/default/graphics/pictures/ICON_ADVANCE_*.tga` (51 TGAs)
- **Civ2 source:** `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` (`@CIVILIZE` section)

### 2. Units {62}
- **Data:** `Scenarios/mom/scen0000/default/gamedata/Units.txt`
- **CSV:** `Scenarios/mom/tools/momjr_csv/units.csv`
- **Icons (TGA):** `Scenarios/mom/scen0000/default/graphics/pictures/ICON_UNIT_*.tga` (61 TGAs)
- **Icon index:** `Scenarios/mom/scen0000/default/gamedata/uniticon.txt`
- **Sprite sheets (BMP):** `Scenarios/mom/tools/civ2_bitmaps/units*.bmp`
- **Civ2 source:** `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` (`@UNITS` section)
- **Mask:** `Scenarios/mom/tools/momjr_csv/unit_mask.csv` (units to remove at generation time)

### 3. City Improvements / Buildings {68}
- **Data:** `Scenarios/mom/scen0000/default/gamedata/buildings.txt`
  (the engine loads `buildings.txt` per `gamefile.txt`; `Improve.txt` is NOT in the
  manifest and is never loaded — improvements MUST be authored into `buildings.txt`)
- **CSV:** `Scenarios/mom/tools/momjr_csv/improvements.csv`
- **Icons (TGA):** `Scenarios/mom/scen0000/default/graphics/pictures/ICON_IMPROVE_*.tga` (68 TGAs)
- **Icon index:** `Scenarios/mom/scen0000/default/gamedata/uniticon.txt`
- **Sprite sheet (BMP):** `Scenarios/mom/tools/civ2_bitmaps/Improvements.bmp`
- **Proxy map:** `Scenarios/mom/tools/momjr_csv/building_uniticon.csv` (CTP2-only buildings; no Civ2 source art)
- **Civ2 source:** `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` (`@IMPROVE` section, non-wonder rows)

### 4. Wonders {30}
- **Data:** `Scenarios/mom/scen0000/default/gamedata/Wonder.txt`
- **CSV:** `Scenarios/mom/tools/momjr_csv/wonders.csv`
- **Icons (TGA):** `Scenarios/mom/scen0000/default/graphics/pictures/ICON_WONDER_*.TGA` (28 TGAs + X-prefixed stubs)
- **Movies:** `Scenarios/mom/scen0000/default/movies/wonder_movies/`
- **Civ2 source:** `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` (`@IMPROVE` wonder rows + `@ENDWONDER`)

### 5. Terrain {26}
- **Data:** `Scenarios/mom/scen0000/default/gamedata/Terrain.txt`
- **CSV:** `Scenarios/mom/tools/momjr_csv/terrain.csv`
- **Icons (TGA):** `Scenarios/mom/scen0000/default/graphics/pictures/ICON_TILEIMP_*.tga` (terrain icon set)
- **Civ2 source:** `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` (`@TERRAIN` section)

### 6. Goods {72}
- **Data:** `Scenarios/mom/scen0000/default/gamedata/goods.txt`
- **CSV:** `Scenarios/mom/tools/momjr_csv/goods.csv`
- **Icons (TGA):** `Scenarios/mom/scen0000/default/graphics/pictures/ICON_GOOD_*.tga`
- **Civ2 analog:** `@CARAVAN` (trade commodities; no direct 1:1)

### 7. Tile Improvements {81}
- **Data:** `Scenarios/mom/scen0000/default/gamedata/tileimp.txt`
- **CSV:** `Scenarios/mom/tools/momjr_csv/tile_improvements.csv`
- **Icons (TGA):** `Scenarios/mom/scen0000/default/graphics/pictures/ICON_TILEIMP_*.tga` (36 TGAs)
- **Civ2 analog:** Game terrain overlay mechanic (8 types: Airbase, Farmland, Fortress, Immigration, Mine, Pollution, Railroad, Road)
- **Field schema:** [`tileimp_schema.md`](tileimp_schema.md) — complete field inventory per Class type

### 8. Governments {5}
- **Data:** `Scenarios/mom/scen0000/default/gamedata/govern.txt`
- **CSV:** `Scenarios/mom/tools/momjr_csv/governments.csv`
- **Icons (TGA):** `Scenarios/mom/scen0000/default/graphics/pictures/ICON_GOVERN_*.tga`
- **Civ2 source:** `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` (`@GOVERNMENTS` section; 7 in Civ2, pruned to 5 in MoM)

### 9. Unit Orders {47}
- **Data:** `Scenarios/mom/scen0000/english/gamedata/orders_str.txt`
- **Civ2 analog:** `@ORDERS` (command text labels)

### 10. Concepts {61}
- **Data:** `Scenarios/mom/scen0000/english/gamedata/gl_str.txt` + `Great_Library.txt`
- **Civ2 analog:** Civilopedia / labels / game text

### 11. SLIC (Scripted Events)
- **Data:** `Scenarios/mom/scen0000/default/slic/*.slc`
- **Civ2 analog:** Events (uncertain mapping; may relate to epoch/age triggers)

### 12. Scenario Art
- **BMP sheets:** `Scenarios/mom/tools/civ2_bitmaps/`
- **TGA output:** `Scenarios/mom/scen0000/default/graphics/pictures/`
- **Pipeline:** `Scenarios/mom/tools/ctp2_generator.py` → sprite extraction scripts

### 13. Civilizations {70}
- **Data:** `Scenarios/mom/scen0000/default/gamedata/civilisation.txt`
- **Strings:** `Scenarios/mom/scen0000/english/gamedata/civ_str.txt`
- **Civ2 analog:** Leaders / Personalities (`@LEADERS` section; 23 in MoMJR)
- **Note:** CTP2 defines full civ records (leader names, personalities, city styles); Civ2 has a simpler per-row entry per civilization

---

## Excel Control Plane Rule

- `Scenarios/mom/mom_dimension_inventory.xlsx` is generated from:
  - `dimension_inventory.md`
  - `Scenarios/mom/tools/momjr_csv/*.csv`
- It intentionally excludes support/reference CSV surfaces such as `data_csv` and `roundtrip_csv`.
- Regenerate it every time `ctp2_generator.py` or `ctpedit.py patch ...` updates the scenario.
- Do not hand-edit the workbook; change the markdown or CSV source surfaces, then rerun the generator.

---

## Civ2 MoMJR Dimensions — Source Files

### 1. Advances {100}
- `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` → `@CIVILIZE`

### 2. City Improvements {38}
- `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` → `@IMPROVE` (non-wonder rows 0–37)

### 3. Wonders {29} (sub-type of improvements)
- `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` → `@IMPROVE` (wonder rows) + `@ENDWONDER`

### 4. Units {62}
- `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` → `@UNITS`

### 5. Terrain {33}
- `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` → `@TERRAIN`

### 6. Governments {7}
- `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` → `@GOVERNMENTS`

### 7. Leaders / Personalities {23}
- `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` → `@LEADERS`
- Americans, Arabs, Aztecs, Babylonians, Carthaginians, Celts, Chinese, Egyptians,
  English, French, Germands, Greeks, Incas, Indians, Japanese, Mongols, Persians,
  Romans, Russians, Sioux, Spanish, Vikings, Zulus

### 8. Caravan Commodities
- `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` → `@CARAVAN`

### 9. Orders / Command Text
- `H:\games\civ2\SCENARIO\MOMJR\RULES.TXT` → `@ORDERS`

### 10. Events
- `H:\games\civ2\SCENARIO\MOMJR\EVENTS.TXT` (if present)
- Uncertain mapping to CTP2 SLIC

### 11. Civilopedia / Labels / Game Text
- `H:\games\civ2\SCENARIO\MOMJR\LABELS.TXT` or game strings

### 12. Scenario Art / Sounds
- `H:\games\civ2\SCENARIO\MOMJR\UNITS.GIF` or sprite sheets
- `H:\games\civ2\SCENARIO\MOMJR\*.BMP` sprite sheets

### 13. Tile Improvements {8}
- Game mechanic (terrain overlay layer); not in RULES.TXT as a named section
- Types: Airbase, Farmland, Fortress, Immigration, Mine, Pollution, Railroad, Road

---

## Image File Inventory

| Dimension | CTP2 TGA folder / prefix | Count | CTP2 BMP sheet |
|---|---|---|---|
| Advances | `ICON_ADVANCE_*.tga` | 51 | — |
| City Improvements | `ICON_IMPROVE_*.tga` | 68 | `Improvements.bmp` |
| Wonders | `ICON_WONDER_*.TGA` | 28 | `Improvements.bmp` (wonder slots) |
| Tile Improvements | `ICON_TILEIMP_*.tga` | 36 | — |
| Units | `ICON_UNIT_*.tga` | 61 | `units*.bmp` sprite sheets |
| Terrain | `ICON_TERRAIN_*.tga` | 24 | — |
| Goods | `ICON_GOOD_*.tga` | 17 | — |
| Governments | `ICON_GOVERN_*.tga` | 5 | — |

All TGA files live in: `Scenarios/mom/scen0000/default/graphics/pictures/`

---

## ctpedit.py Patch Commands

```
python Scenarios/mom/tools/ctpedit.py status
python Scenarios/mom/tools/ctpedit.py show advances
python Scenarios/mom/tools/ctpedit.py patch advances
python Scenarios/mom/tools/ctpedit.py patch units
python Scenarios/mom/tools/ctpedit.py patch improvements
python Scenarios/mom/tools/ctpedit.py patch wonders
python Scenarios/mom/tools/ctpedit.py patch all --dry-run
```

Cascade effects (already wired in ctpedit.py):
- `advances` → `Advance.txt` + `gl_str.txt` + advance icon TGAs
- `units` → `Units.txt` + `uniticon.txt` + unit icon TGAs; unit_mask.csv gates removal
- `improvements` → `Improve.txt` + `uniticon.txt` + building TGAs; proxy via `building_uniticon.csv`
- `wonders` → `Wonder.txt` + `uniticon.txt` + wonder TGAs + wonder movies

---

## Key Lessons Learned

1. **Wonders in Civ2 are not a separate dimension** — they live in `@IMPROVE` with `@ENDWONDER` expiry; CTP2 splits them into `Wonder.txt`.
2. **Tile Improvements in Civ2** are a game mechanic layer (8 types), not a named block dimension like CTP2's 81-entry `tileimp.txt`.
3. **Civ2 Leaders → CTP2 Civilizations**: Civ2 has one row per civ leader; CTP2 stores full civilization records including city styles, personality, emissary photos.
4. **Events → SLIC**: Civ2 scripted events may translate to CTP2 SLIC scripts; mapping to epochs/ages is uncertain.
5. **Never use regex for CTP2 block removal** — always use `UnitsFile.remove_unit()` or depth-tracking parser (nested sub-blocks corrupt with `[^}]*` regex).
6. **`reg.save_all()` overwrites disk** — always mutate via the object returned by `reg.load()`; never write directly to disk if the generator is running.
7. **CTP2-only buildings** (30 added vs Civ2) use proxy TGAs from `building_uniticon.csv` since no Civ2 art source exists.
8. **unit_mask.csv cascades to ALL three unit files** — `Units.txt`, `Units_historic.txt`, and `Units_release.txt` must all have masked units removed. The CTP2 engine can load any of them depending on scenario load path; leaving a unit in a backup file causes "X not found in Unit database" at startup even if `Units.txt` is correct. Register both backup files in `PARSER_MAP` (as `UnitsFile`) so `reg.load()` handles them.
