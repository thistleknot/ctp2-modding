# Generator Refactor Spec

## Problem

`tools/ctp2_generator.py` is 6000 lines in a single file. This makes:
- Feature grafting painful (merge conflicts span hundreds of lines)
- Comprehension difficult (no clear module boundaries)
- Testing impossible at the function level
- Parallel work by multiple agents/sessions conflicty

## Target

Each module < 1000 lines. Orchestrator (`ctp2_generator.py`) becomes ~200 lines
that imports modules and calls them in dependency order.

## Proposed Decomposition

| Module | Concern | Key functions (current) |
|--------|---------|------------------------|
| `gen_common.py` | Shared helpers: policy loading, file I/O, sanitize, humanize | `_read_rel`, `_write_rel`, `_policy_csv_rows`, `_load_mod_policy`, `sanitize`, `humanize_ident`, `_csv_path`, `_csv_rows` |
| `gen_advances.py` | Advance registration, cost banding, prereqs, age layout, AI lists | `_load_ae_advance_cost_bands`, `_retune_mom_advance_costs`, `_relayout_advance_ages`, `_apply_advance_mask`, `_apply_advance_reanchor`, `_apply_sphere_gating`, `_reconcile_advance_prereqs`, `_write_mom_advance_lists`, `reconcile_advance_statistics` |
| `gen_units.py` | Unit stat casting, sprite picking, cost banding, build lists | `_stat_cast`, `_stat_source_dist`, `_pick_sprite`, `_pick_size`, `_retune_mom_unit_costs`, `_write_mom_unit_build_lists`, `_scan_unit_blocks` |
| `gen_buildings.py` | Improvement merge into buildings.txt, cost bands, icon wiring | `_merge_mom_improvements_into_buildings`, `_retune_mom_improvement_costs`, `_scan_improve_blocks`, `_load_ae_improvement_cost_bands` |
| `gen_wonders.py` | Wonder migration from Improve, GL surfaces, cost bands, effects | `_load_canonical_momjr_wonders`, `_remove_migrated_wonder_improvements`, `_synchronize_runtime_wonder_blocks`, `_ensure_runtime_wonder_gl_surfaces`, `_prune_wonder_surfaces`, `_retune_mom_wonder_costs`, `_apply_wonder_effects` |
| `gen_gl.py` | Great Library pruning, string pruning, description injection, link stripping | `_prune_gl_sections`, `_prune_gl_strings`, `_strip_stale_database_links`, `_restore_base_advance_gl_prose`, `_restore_missing_uniticon_gl_sections`, `_apply_gl_section_overrides` |
| `gen_calendar.py` | DiffDB TIME_SCALE rewrite, Const.txt END_OF_GAME_YEAR, calendar_periods.csv | `_write_calendar` (new — port from mom-base-clean) |
| `gen_spellbook.py` | Two-tier spellbook hub, paged alertboxes, cast chain, scen_str entries | `_emit_spellbook_pages`, `_emit_spell_effects` (new — port from mom-base-clean) |
| `gen_civs.py` | civilisation.txt tribes, civ_str.txt strings | `_generate_civilisation_tribes`, `_generate_civstr_tribes` |
| `gen_governance.py` | Government pruning, governicon restoration, DiffDB start-tech guarantee | `_government_ids_enabled_by_live_advances`, `_ensure_diffdb_start_government`, `_prune_government_advice_lines`, `_prune_strategy_government_lines` |
| `gen_gating.py` | Sphere gating SLIC, summon SLIC, faction detection | `_emit_mom_gating_slc`, `_emit_mom_summon_slc`, `_summon_pool_by_rung`, `sphere_gate_targets` |
| `gen_icons.py` | uniticon.txt writing, advance icon file, counted icon handling | `_write_advance_icon_file`, `_load_counted_icon_file`, `_save_counted_icon_file`, `_filter_counted_icon_entries` |
| `gen_tileimp.py` | Tile improvement scrubbing, order/concept hiding | `_scrub_dead_tileimp_surfaces`, `_scrub_hidden_tileimp_gl_file`, `_scrub_hidden_order_gl_file`, `_scrub_hidden_concept_gl_file` |
| `ctp2_generator.py` | Orchestrator: imports, dependency order, main() | ~200 lines max |

## Dependency Order (main() call sequence)

```
1. gen_common        — bootstrap policy, file registry
2. gen_advances      — advance dimension (everything else depends on advance ages)
3. gen_units         — unit dimension (needs advance ages for cost banding)
4. gen_buildings     — improvement merge + cost banding
5. gen_wonders       — wonder migration (after buildings cleared)
6. gen_icons         — icon surfaces for all dimensions
7. gen_gl            — Great Library for all dimensions (after all DB files stable)
8. gen_governance    — government pruning + DiffDB start-tech
9. gen_calendar      — DiffDB TIME_SCALE + Const.txt (after governance touches DiffDB)
10. gen_gating       — sphere gating SLIC (needs advance idents)
11. gen_spellbook    — spellbook SLIC + scen_str (independent of DB files)
12. gen_tileimp      — tileimp scrubbing (last, after all GL work done)
13. gen_civs         — civilisation + civ_str (independent)
```

## Shared State

Modules communicate through:
- `MOD_POLICY` dict (loaded once in gen_common, imported by all)
- `SCENARIO` / `CTP2_DATA` / `MOMJR` paths (gen_common)
- Return values from prior steps (e.g. `advance_ages` dict returned by gen_advances, passed to gen_units)
- File registry (`_read_rel` / `_write_rel` in gen_common)

No module writes to another module's files. Each module owns its output set.

## Migration Strategy

1. Extract `gen_common.py` first (all shared helpers) — nothing breaks, just imports change
2. Extract one module at a time, starting from the leaf (gen_civs, gen_tileimp)
3. Work inward toward gen_advances (the most interconnected)
4. Keep `ctp2_generator.py` as the orchestrator throughout — it shrinks with each extraction
5. After each extraction: run generator + audit + turnloop to confirm no regression

## Acceptance Criteria

- No file > 1000 lines
- `python ctp2_generator.py` produces byte-identical output before and after refactor
- `python mom_audit.py` FAIL: 0
- Headless turnloop 5 turns, 0 SLIC errors
- Each module importable independently for unit testing
