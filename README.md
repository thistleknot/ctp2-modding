# ctp2-modding

AI-driven mod-merging abilities for Call to Power 2 — the reusable **harness,
wiki, skills, and control-plane pipeline** extracted so mod merges can be
resumed later. Game scenario data lives in its own repos (e.g.
[ctp2-momjr](https://github.com/thistleknot/ctp2-momjr)); this repo is *just the
abilities*.

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
   (schema)
```

Both encoders emit the **same** per-dimension csv schema, so a ctp2-sourced
row is indistinguishable from a civ2-sourced one downstream. `encode_ctp2_mod`
normalizes cross-engine: stats back to civ2-scale (attack/defense ÷5, cost
÷100), domain from `MovementType`, prereq from `EnableAdvance`; it discovers
dimension files by suffix (`*Units.txt`, `*Advance.txt`) and last-wins-dedups,
so multi-file mods (LotR's `LOTR_Units.txt` + `LOTR3_Units.txt`) encode
cleanly.

## Layout

- `tools/` — the pipeline:
  - `encode_civ2_mod.py` — civ2 RULES.TXT → per-dimension CSVs (+ workbook)
  - `encode_ctp2_mod.py` — native ctp2 gamedata → same CSVs, cross-engine
    normalized (suffix file-discovery + last-wins dedup for multi-file mods)
  - `merge_control_planes.py` — union/normalize N encoded mods (+ genre mask)
  - `make_genre_mask.py` — era/keyword mask staging sheet (age-gated)
  - `assign_unit_factions.py` — sphere/faction unit gating
  - `assign_proxy_art.py` — borrow real icon art for merged entities
  - `ctp2_generator.py` — control plane → CTP2 scenario files (engine only)
  - `export_mod_workbook.py` / `sync_excel_to_csv.py` — xlsx ⇄ csv round-trip
  - `validate_scenario.py` — **9 crash-class gates; run before every playtest**
  - `mom_audit.py`, `civ2_sprite_extractor.py`, `build_sprites.py`, `makespr.py`, …
- `control-plane/` — the MoM control plane as the reference schema (dimension
  CSVs + `mod_policy.json` + masks + faction/atlas config)
- `docs/` — `HARNESS.md`, `MOD_DIMENSIONS.md`, `PROTECTED_FILES.md`,
  `SMM_DESIGN.md` (Super Magic merge design), `specs/`
- `wiki/lessons_learned.md` — the running lessons log (newest first)
- `memory-bank/` — durable skills: schema map-reduce, CTP2 crash classes

## Hard-won rules (see memory-bank + wiki)

- **Generator exit-0 ≠ engine-parseable** — always run `validate_scenario.py`.
- The genre mask never touches base (curated) content — only merged sources.
- The runtime Icon DB is `uniticon.txt`, not `improveicon.txt`.
- `k_MAX_Prerequisites = 4`; a city unit needs Land **and** Sea movement or
  coastal settles crash; reserved engine tokens crash StringDB; etc.

Source game content © Activision / Firaxis / original mod authors; this repo
contains only tooling, docs, and control-plane schemas.
