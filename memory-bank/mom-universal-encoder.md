---
name: mom-universal-encoder
description: "2026-07-15 universal mod encoder SHIPPED (d213155+a60a147): civ2 mod → csv/xlsx control plane → ctp2, proven end-to-end on HoMM2Mod1.1. A mod = one csv dir (dimension csvs + 9 policy files + atlas config). Gate = regen byte-stability into scratch scenario via env vars. Round 2 (embedded main() literals) still pending — see policy inventory spec."
metadata:
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**Universal mod encoder (2026-07-15, commits d213155 + a60a147, user-directed "shore up"):**

- **Flow**: `encode_civ2_mod.py --mod-dir <civ2 mod> --out <csv dir>` → hand-curate → `CTP2_GENERATOR_CSV_DIR/_SCENARIO_DIR` + `CIV2_MOD_BMP_DIR` env → `ctp2_generator.py`. xlsx ⇄ csv: `export_mod_workbook.py` / `sync_excel_to_csv.py` (all sheets, header-drift refusal, --check).
- **A mod = one csv dir**: dimension csvs + mod_policy.json + 8 policy csvs (masks, gl_text_rewrites, advance_code_map, stub_advances, governicon_fallback, advance_cost_bands) + sprite_atlas_config.csv. `dump_mod_policy.py` scaffolds MoM defaults.
- **THE gate**: regen byte-stability — scratch-run the generator (env vars), md5 all 603 files, diff across runs/changes. Found real set-iteration nondeterminism (fixed: sorted _unit_ids).
- **Dry-run on a FOREIGN mod is the universality test** — each failure names the next hidden assumption. HoMM2 ran exit-0; scenario contained UNIT_HALFLING/PHOENIX/TITAN.
- **Encoder-vs-curated diff = the curation ledger**: encode MOMJR, diff vs momjr_csv → only documented hand decisions (hero Mys gating, X-icon renames, wonders-as-buildings).
- **Round 2 DONE (1c33df1)**: all embedded main() literals extracted — Enchanted Road remap family (db_text_swaps/tileimp_block_swaps + gl_section_overrides.csv set/replace/pop), sprite_pick_rules.csv (ordered rule evaluator), unit stat scaling/roles/settler category/GL branding (mod_policy.json), UNIT_SETTLER/PEASANTS blocks (unit_block_overrides.csv). Only ENGINE items remain in code. The engine/policy split is COMPLETE per the 58-row inventory spec.
- Wiki: lessons_learned § "[PIPELINE] Universal mod encoder" (2026-07-15).

- **BOTH ENGINES NOW (2026-07-15)**: `encode_ctp2_mod.py` is the inverse of ctp2_generator — parses NATIVE ctp2 gamedata block files into the SAME per-dimension csv schema, so ctp2 mods join the merge equal to civ2 mods. Cross-engine normalization: atk/def ÷5, cost ÷100 (undo generator's ×5/×100), domain from MovementType, prereq from EnableAdvance, identity advance_code_map. Key robustness: dimension files found by SUFFIX glob (`*Units.txt`/`*Advance.txt`/`*buildings.txt`→`*Improve.txt`) + `dedup_last_wins` (CTP2 DB later-Parse-overwrites semantics) → multi-file mods work (LotR `LOTR_Advance.txt`+`LOTR2_Advance.txt` carry the SAME 333 idents; concat+dedup = 333 not 666). Verified Cradle 5.1 (191/181/71), AoM IV (107/72/52), LotR (333/214/0; 0 improvements = LotR ships no buildings file, inherits base — correct not a bug). Pushed to ctp2-modding (commit 123db97) + mom repo (a042fbd). Own use of a `first(...)`-style parse via local `parse_blocks` (CTP2BlockFile is lossy on repeated keys).

Related: [[mom-canonical-toolchain]], [[mom-advance-icons]], [[mom-wiki]], [[skill-mod-schema-mapreduce]], [[smm-super-magic-mod]].
