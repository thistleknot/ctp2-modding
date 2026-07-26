---
name: mom-db-error-class
description: "How to diagnose/fix CTP2 \"X not found in <DB> database\" + SLIC symbol errors in the MoM mod — validate all 7 reference surfaces"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1075e678-fc47-4aa4-862a-540bfb34401c
---

CTP2 validates entity references from 7 surfaces, not one. Discovering them one launch
at a time is the trap the user hates. `Scenarios/mom/tools/validate_all_surfaces.py`
checks ALL of them against the live DBs and is wired into `ctpedit patch`
(generator → fix_gl_links → validate_all_surfaces → audit). Run it (PYTHONIOENCODING=utf-8)
before declaring a build launch-clean.

The 7 surfaces (with the real errors each produced):
1. Data-file gating fields (EnableAdvance/Prerequisites/UpgradeTo...) — "Cyber Ninja
   not found" (UNIT_SPY UpgradeTo a base unit the build half-kept).
2. Great Library <L:DATABASE_<TYPE>,<TOKEN>> links — "Desert Mountain"
   (TERRAIN_BROWN_MOUNTAIN). Fixed in bulk by `fix_gl_links.py`.
3. GL advance sections [ADVANCE_X_*] — "Drama not found" (handled by the generator's
   advance-stub pass).
4. AI build lists / strategies (default/aidata/*.txt).
5. EndGameObjects.txt victory wonders — "The Solaris Project not found" (file was
   missing → fell back to stock requiring base wonders; authored a MoM version).
6. Base-fallback gamedata files (any ctp2_data/*.txt the scenario doesn't override).
7. SLIC entity symbols UNIT_/IMPROVE_/ADVANCE_/WONDER_ in *.slc (runtime) — "Symbol
   UNIT_SHAMAN is undefined".

KEY policy (dimension_inventory.md): KEEP dimensions (terrain, governments, orders,
concepts, goods, tile improvements) use BASE content — never regenerate from a
structured CSV via a "raw" importer (that wiped terrain.txt to 1 line). MoM dimensions
(advances/units/improvements/wonders) are CSV-authored; everything referencing them
must be authored/repaired to match. See [[mom-canonical-toolchain]].
