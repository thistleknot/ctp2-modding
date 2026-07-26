# Example: MoM Junior

**The mod itself lives at
[github.com/thistleknot/ctp2-momjr](https://github.com/thistleknot/ctp2-momjr)**
— which *is* the `Scenarios\mom` folder of a CTP2 install. Clone it there; it
carries the scenario, the authored SLIC, the full workbook and the
distributable `mom.zip`.

What lives here is the **in-between**: the control plane this harness consumes,
and the workbook it produces from it. MoM Junior is a Civ2 Master of Magic total
conversion, and it is the mod every gate in `tools/` was written against.

## The two artifacts in this folder

### `control-plane/*.csv` + `*.json` — the input

The per-dimension CSVs the generator reads, plus the policy that keeps
mod-specific decisions out of the engine code:

| file | dimension |
|---|---|
| `units.csv`, `advances.csv`, `improvements.csv`, `wonders.csv`, `terrain.csv`, `tileimp.csv`, `feats.csv`, `players.csv` | the game entities |
| `mod_policy.json` | every MoM-specific decision the generator would otherwise hardcode |
| `*_mask.csv` | which merged rows survive into the scenario |
| `sprite_pick_rules.csv`, `civ2_converted_graphics.csv`, `building_uniticon.csv`, `improveicon.csv`, `governicon_fallback.csv` | the art chain |
| `advance_cost_bands.csv`, `advance_code_map.csv`, `stub_advances.csv`, `advances_cell_remap.csv` | advance-tree shaping |
| `gl_section_overrides.csv`, `gl_text_rewrites.csv` | Great Library text |
| `slic_inventory.csv`, `slic_purpose.json` | the SLIC dimension: what exists, and the curated intent the backcast merges forward |

### `control-plane/mod_inventory.xlsx` — the generated middle

27 sheets, one per csv plus an `index`. Committed **on purpose**, so you can see
what the csv → xlsx step actually produces without running anything, and so a
rerun surfaces drift as a diff. Every generator run refreshes it.

It has 27 sheets here rather than the mod's 35 because the `slic` tab is
backcast from the `.slc` sources, which live in the ctp2-momjr repo — see
[SLIC flows the other way](../../README.md).

## Running the pipeline against it

Three environment variables point the generator at input, output and the base
game. All three have defaults, and **the defaults are the author's install
paths** — set them.

```
set CTP2_GENERATOR_CSV_DIR=<...>\examples\momjr\control-plane
set CTP2_GENERATOR_SCENARIO_DIR=<...>\out\scen0000
set CTP2_GENERATOR_CTP2_DATA_DIR=<CTP2 install>\ctp2_data

python tools\ctp2_generator.py        # control plane -> scenario
python tools\validate_scenario.py     # 9 crash-class gates
python tools\mom_audit.py             # post-generation validation
python tools\build_mod_zip.py         # package the scenario
```

A CTP2 install is required: the generator merges against base `ctp2_data` — the
Great Library, DiffDB, the sprite definitions — rather than writing every file
from nothing.

The generator is deterministic: two runs from the same control plane produce
byte-identical output, and that is the pipeline's regression gate.

### What that produces

31 text files, verified from a clean clone of this repo:

- `scen0000/default/gamedata/` — `Units.txt`, `Advance.txt`, `buildings.txt`,
  `Wonder.txt`, `tileimp.txt`, `goods.txt`, `govern.txt`, `concept.txt`,
  `Orders.txt`, `civilisation.txt`, `DiffDB.txt`
- the icon **bindings** — `uniticon.txt`, `improveicon.txt`, `wondericon.txt`,
  `governicon.txt`, `newsprite.txt`
- `scen0000/default/aidata/` — `AdvanceLists`, `Goals`, `UnitBuildLists`,
  `WonderBuildLists`, `strategies`
- `scen0000/english/gamedata/` — `Great_Library.txt`, `civ_str.txt`,
  `gl_str.txt` and the other string tables

### What it does *not* produce, and why

Two things sit outside this step. Neither is missing tooling — both are separate
commands whose inputs do not belong in a code repo.

- **Icon and sprite art (`.tga`, `.spr`).** `uniticon.txt` binds names to art;
  the pixels come from the Civ2 mod's own `GRAPHICS` folder. Run
  `civ2_sprite_extractor.py` → `build_sprites.py` / `build_unit_sprite.py` →
  `makespr.py` with that mod on disk, and gate the result with
  `gate_sprite_extent.py` — sprite **extent and anchor are one coupled bug**, so
  never change one without the other.
- **SLIC.** Civ2 has no equivalent, so there is nothing to generate *from*.
  SLIC is authored directly against CTP2 in the mod repo and flows **backward**
  into the workbook via `backcast_slic.py`, which never writes `.slc`.
  `backcast_slic.py --check` is the drift gate; `docs/SLIC_TEMPLATE_CATALOG.md`
  is the pattern reference.

## Converting a different Civ2 mod

```
python tools\encode_civ2_mod.py --mod-dir <civ2 mod dir> --out <new csv dir>
# hand-curate: wonders block_text, players ctp2 columns, mod_policy.json, atlas
set CTP2_GENERATOR_CSV_DIR=<new csv dir>
python tools\ctp2_generator.py
```

`dump_mod_policy.py` scaffolds a starting `mod_policy.json`. Everything a
different conversion would decide differently belongs in that file, never in the
generator.
