---
name: mom-canonical-toolchain
description: "How the MoM (Civ2→CTP2) mod is actually built — control plane is source of truth, ctpedit/ctp2_generator is canonical"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1075e678-fc47-4aa4-862a-540bfb34401c
---

The MoM mod has TWO generation front-ends; do not confuse them:
- `modder_files/mom_translator.py` — one-shot Civ2 import that **wholesale-replaces** 4
  dimensions (writes `buildings.txt`, reduced record sets). Causes "X not found in Y
  database" whack-a-mole because it orphans base cross-references.
- `Scenarios/mom/tools/ctp2_generator.py` via `tools/ctpedit.py patch all` — **canonical**,
  control-plane driven, idempotent, keeps/hides base records and keeps the Great Library
  consistent (writes `Improve.txt`, full record sets).

Source of truth = the Excel control plane `Scenarios/mom/mom_dimension_inventory.xlsx`
+ `tools/momjr_csv/*.csv`. Design rule: MoM = base records that don't conflict with the
fantasy genre ∪ Civ2 MoMJR imports (a curated SUPERSET, not a replacement).

Build command: `cd Scenarios/mom/tools && PYTHONIOENCODING=utf-8 python ctpedit.py patch all`.
Diagnostic tools live in `tools/`: `scan_interconnections.py`, `crossref_audit.py`,
`mask_manager.py`, `apply_masks.py`. Always run them with `PYTHONIOENCODING=utf-8` (they
crash on Windows cp1252). See [[mom-db-error-class]] and `Scenarios/mom/lessons_learned.md`.
