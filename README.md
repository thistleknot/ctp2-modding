# ctp2-modding

AI-driven mod-merging abilities for Call to Power 2 — the reusable **harness,
wiki, skills, and control-plane pipeline** extracted so mod merges can be
resumed later.

**This repo is the code, not the mods.** No scenario ships here. The mods this
tooling produced live in their own repos —
[ctp2-momjr](https://github.com/thistleknot/ctp2-momjr) is the worked example —
and `examples/` carries only the control plane that drives one, so the pipeline
has something real to run against.

## The core idea: merging mods is a schema map-reduce

The pipeline encodes each source mod — **civ2 OR native ctp2** — into ONE
common xlsx/csv **control plane**, the single format to observe and compare
mods side by side, then derives a unified schema, MAPs each mod's native
`(civilization, age)` onto it, and REDUCEs into a new merged mod. See
`memory-bank/skill-mod-schema-mapreduce.md`.

```
civ2 mod ──encode_civ2_mod──►┐
                             ├─► csv/xlsx control plane ──curate──► ctp2_generator ──► scenario
ctp2 mod ──encode_ctp2_mod──►┘   (observe / compare / merge)         (engine files)
   (schema)                               ▲
                                          │
scenario *.slc  ──backcast_slic───────────┘
```

Both encoders emit the **same** per-dimension csv schema, so a ctp2-sourced
row is indistinguishable from a civ2-sourced one downstream. `encode_ctp2_mod`
normalizes cross-engine: stats back to civ2-scale (attack/defense ÷5, cost
÷100), domain from `MovementType`, prereq from `EnableAdvance`; it discovers
dimension files by suffix (`*Units.txt`, `*Advance.txt`) and last-wins-dedups,
so multi-file mods (LotR's `LOTR_Units.txt` + `LOTR3_Units.txt`) encode
cleanly.

### The control plane is a workbook, one tab per dimension

`export_mod_workbook.py` renders the csv layer into `*_dimension_inventory.xlsx`
with **one tab per dimension** — units, advances, improvements, terrain,
players, wonders, tileimp, sprite pick rules, cost bands, atlas geometry, and
**slic**. A cell holds a file and/or a set of constants, classes and functions:
the actual content, not a manifest describing it.

### SLIC flows the other way

Every dimension is forward-generated except SLIC, which has no civ2 upstream —
there is nothing to encode *from*. `backcast_slic.py` runs
`scenario/*.slc → xlsx` and **never writes SLIC back**, so the text stays
diffable and compilable. It writes the `slic` tab (module rows, whole blocks
under `constants` / `functions` / `handlers` / `triggers` / `segments` /
`source`) plus the flat `slic_index`. Structure is re-derived every run; the
`purpose`/`status` prose is merged forward by name from `slic_purpose.json`, so
new code surfaces with an empty purpose — a visible TODO — and curated intent
is never clobbered.

Run it **after** `export_mod_workbook.py`, which rebuilds the forward tabs and
does not know about SLIC. `--check` exits 1 if the tab drifted from the code; it
normalizes `None`/`""` on both sides, because openpyxl round-trips an empty
string as `None`.

## Layout

- `tools/` — the pipeline:
  - `encode_civ2_mod.py` — civ2 RULES.TXT → per-dimension CSVs (+ workbook)
  - `encode_ctp2_mod.py` — native ctp2 gamedata → same CSVs, cross-engine
    normalized (suffix file-discovery + last-wins dedup for multi-file mods)
  - `merge_control_planes.py` — union/normalize N encoded mods (+ genre mask)
  - `make_genre_mask.py` / `apply_masks.py` / `mask_manager.py` — era and
    keyword masks, staged then applied
  - `assign_unit_factions.py` — sphere/faction unit gating
  - `assign_proxy_art.py` — borrow real icon art for merged entities
  - `ctp2_generator.py` — control plane → CTP2 scenario files (engine only)
  - `export_mod_workbook.py` / `sync_excel_to_csv.py` — xlsx ⇄ csv round-trip
  - `backcast_slic.py` — scenario SLIC → the `slic` dimension (+ `--check` gate)
  - `build_schema.py` / `enrich_csv_schema.py` / `schema_*.py` — schema
    induction, query, and drift checks over the control plane
  - `validate_scenario.py` — **9 crash-class gates; run before every playtest**
  - `mom_audit.py`, `crossref_audit.py`, `scan_interconnections.py` —
    post-generation validation and cross-dimension reference tracing
  - `civ2_sprite_extractor.py`, `build_sprites.py`, `build_unit_sprite.py`,
    `makespr.py`, `gate_sprite_extent.py`, `golden_test_makespr.py` — the art
    chain, with the extent/anchor gate that keeps units centred on their tile
  - `build_mod_zip.py` — package a scenario for distribution: `packicon.tga`,
    `packlist.txt`, `scen0000/**` under a top-level prefix, and nothing else.
    **The repo holds the code; the zip holds the mod.**
- `tools/uiwalk/` — the headless in-game harness. Launches CTP2 off-screen,
  drives it by scripted steps (`steps/*.json`), and asserts screen state against
  `goldens/`. Menus are driven by injection (`press:` / `select:`), never by
  clicks; in-game alertboxes take clicks. Run output (`runs/`) is not tracked.
- `examples/momjr/` — the MoM Junior control plane, and a pointer to its repo
- `docs/` — `HARNESS.md`, `MOD_DIMENSIONS.md`, `PROTECTED_FILES.md`,
  `SMM_DESIGN.md`, the pipeline reviews, the dimension map, and `specs/`
- `wiki/lessons_learned.md` — the running lessons log (newest first)
- `memory-bank/` — durable skills and the environment laws that govern the
  harness: crash classes, schema map-reduce, headless invariants, SLIC classes

## Hard-won rules (see memory-bank + wiki)

- **Generator exit-0 ≠ engine-parseable** — always run `validate_scenario.py`.
- The genre mask never touches base (curated) content — only merged sources.
- The runtime Icon DB is `uniticon.txt`, not `improveicon.txt`.
- `k_MAX_Prerequisites = 4`; a city unit needs Land **and** Sea movement or
  coastal settles crash; reserved engine tokens crash StringDB.
- Sprite **extent and anchor are one coupled bug** — never change one alone.
- A 2-level user-function call chain from a SLIC `HandleEvent` is an access
  violation; compare against `AdvanceDB(...)` via `value[0]`.
- Saves cache compiled SLIC — test SLIC changes from a **new** game.

Source game content © Activision / Firaxis / original mod authors; this repo
contains only tooling, docs, and control-plane schemas.
