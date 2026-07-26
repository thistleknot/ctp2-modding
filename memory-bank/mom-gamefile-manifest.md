---
name: mom-gamefile-manifest
description: CTP2 loads record files per gamefile.txt; improvements = buildings.txt (NOT Improve.txt) — root of the buildings.txt/Improve.txt confusion
metadata: 
  node_type: memory
  type: project
  originSessionId: 1075e678-fc47-4aa4-862a-540bfb34401c
---

`ctp2_data/default/gamedata/gamefile.txt` is the engine's authoritative record-file load
manifest. Line 26 = **`buildings.txt`**; **`Improve.txt` is NOT in it — never loaded.**
This was the project-long buildings.txt-vs-Improve.txt confusion: `ctp2_generator.py`
authored MoM improvements into `Improve.txt` (dead file), so MoM buildings never loaded
and SLIC/GL refs to them were undefined ("Symbol IMPROVE_BARRACKS is undefined"). Proof:
AE_Mod ships only buildings.txt (no Improve.txt) and works.

Schemas differ: buildings.txt (AE) uses `EnableAdvance`/`ProductionCost`/`DefaultIcon`/
`Description` (CamelCase, multi-line); Improve.txt (old CTP2) uses `ENABLING_ADVANCE`/
`IMPROVEMENT_PRODUCTION_COST`/`IMPROVE_DEFAULT_ICON` (UPPER_SNAKE, single-line). Convert
fields when moving blocks; do not raw-append.

Phase A (done): converted the 20 real MoM improvements from Improve.txt → buildings.txt
(AE schema), dropped 13 stale sci-fi base blocks, deleted Improve.txt. Game loads, build
menu shows MoM buildings. `validate_all_surfaces.py` now checks IMPROVE_ against
buildings.txt only, base-fallback surface scoped to gamefile.txt.

Phase B (DONE): ctp2_generator.py now has `_merge_mom_improvements_into_buildings()`
(post-pass, called before reg.save_all) that converts the authored Improve.txt blocks
(old schema) into buildings.txt (RawBlockTextFile, AE schema — CTP2BlockFile is LOSSY on
bare flags/repeated keys, would corrupt AE base blocks) and deletes dead Improve.txt.
mom_audit.py file-population check updated to buildings.txt (was Improve.txt). Result:
`ctpedit patch all` → 57 PASS / 0 FAIL, validate_all_surfaces ALL CLEAN, buildings.txt =
52 AE + 20 MoM, Improve.txt gone. Regens are now correct.

Rule: cross-check every generator target against gamefile.txt — a target not in the
manifest is dead. AllinoneWindow setup crashes can be intermittent; retry a clean build
before treating it as a data bug. See [[mom-db-error-class]].
