# Example: MoM Junior

**The mod itself lives at
[github.com/thistleknot/ctp2-momjr](https://github.com/thistleknot/ctp2-momjr).**
Clone it there; it carries the scenario, the workbook and the distributable
`mom.zip`. Only the control plane is reproduced here, as the worked example of
what this harness consumes.

MoM Junior is a Civ2 Master of Magic total conversion, encoded into the control
plane and regenerated as a CTP2 scenario on the Apolyton Edition. It is the mod
that every gate in `tools/` was written against.

## What's in `control-plane/`

The per-dimension CSVs the generator reads, plus the policy that keeps mod
decisions out of the engine code:

| file | dimension |
|---|---|
| `units.csv`, `advances.csv`, `improvements.csv`, `wonders.csv`, `terrain.csv`, `tileimp.csv`, `feats.csv`, `players.csv` | the game entities |
| `mod_policy.json` | every MoM-specific decision the generator would otherwise hardcode |
| `*_mask.csv` | which merged rows survive into the scenario |
| `sprite_pick_rules.csv`, `civ2_converted_graphics.csv`, `building_uniticon.csv`, `improveicon.csv`, `governicon_fallback.csv` | the art chain |
| `advance_cost_bands.csv`, `advance_code_map.csv`, `stub_advances.csv`, `advances_cell_remap.csv` | advance-tree shaping |
| `gl_section_overrides.csv`, `gl_text_rewrites.csv` | Great Library text |
| `slic_inventory.csv`, `slic_purpose.json` | the SLIC dimension: what exists, and the curated intent the backcast merges forward |

## Running the pipeline against it

From a checkout of ctp2-momjr, with this harness's `tools/` on hand:

```
set CTP2_GENERATOR_CSV_DIR=<this control-plane dir>
python tools\ctp2_generator.py        # control plane -> scenario
python tools\validate_scenario.py     # 9 crash-class gates
python tools\mom_audit.py             # post-generation validation
python tools\export_mod_workbook.py   # csv -> xlsx, forward dimensions
python tools\backcast_slic.py         # scenario SLIC -> the slic tab
python tools\build_mod_zip.py         # package mom.zip
```

The generator is deterministic: two runs from the same control plane produce
byte-identical output, and that is the pipeline's regression gate.

## Converting a different Civ2 mod

```
python tools\encode_civ2_mod.py --mod-dir <civ2 mod dir> --out <new csv dir>
# hand-curate: wonders block_text, players ctp2 columns, mod_policy.json, atlas
set CTP2_GENERATOR_CSV_DIR=<new csv dir>
python tools\ctp2_generator.py
```
