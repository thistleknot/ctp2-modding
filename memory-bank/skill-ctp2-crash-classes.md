---
name: skill-ctp2-crash-classes
description: "CORE MODDING SKILL — the CTP2 DB-load/runtime crash classes a generated scenario must pass, each now a validate_scenario.py gate. Generator exit-0 ≠ engine-parseable; run the validator before EVERY playtest. Each gate was learned from a live crash dialog."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**`validate_scenario.py --scenario <dir>` — 9 gates, each a real crash class (2026-07-15). Run before every playtest; generator exit-0 only means the Python ran.**

1. **newsprite grammar** — every entry `NAME <int>`; punctuated names (`Water/Air Elementals`) leak `/` → "Expected integer". Fix: `sanitize()` everywhere an ident is derived.
2. **ident charset** — DefaultSprite/DefaultIcon/unit-idents must be `[A-Za-z0-9_]`.
3. **engine reserved tokens** — a unit/id equal to a Token.cpp keyword crashes StringDB ("Missing string id" → exit). `UNIT_SPRITE` (unit literally named "Sprite") is the exemplar; `engine_reserved_tokens.txt` has all 76.
4. **string-ref integrity** — every `Description` id resolves in gl_str ("Expected string ID" exit). Merge lanes must agree on skipped rows (SS spaceship parts).
5. **icon-DB integrity** — DefaultIcon refs must exist in **uniticon.txt** (the runtime IconDB per civapp.cpp `g_theIconDB->Parse(g_uniticondb_filename)` — NOT improveicon.txt, a red herring). Backfill missing improve icons as uniticon BLOCKS.
6. **advance prereq cap** — `k_MAX_Prerequisites=4`; a 5th `Prerequisites` line = "too many entries". Enchanted-Road remap can collapse to 5. Truncate to 4 (don't dedupe — self-prereqs are the engine disable pattern).
7. **build-list dangling ref** — Building/Unit refs in aidata build lists must resolve ("X not found in Building/Unit database" exit). Masking a building leaves a dangling `Building IMPROVE_X` in BuildingBuildLists.
8. **visible art** — no visible advance/unit on the UPLG001 placeholder (aesthetic gate; `assign_proxy_art.py` borrows real icons).
9. **city-unit coverage** — need a `HasPopAndCanBuild` unit reachable on BOTH Land AND Sea. `unitutil_GetLandCity/GetSeaCity` scan for pop-flag+MovementType; none found → return index 0 → flagless unit → null CityData → AV when founding a city on that terrain (THE coastal-settle crash; UNIT_CITY needs MovementType Sea/ShallowWater added).

**Other hard-won**: 1 MB debug-exe stack blows on deep chains → 8 MB via editbin/vcxproj (classifier-blocks Claude; hand to user). Genre mask NEVER touches source=base content (CTP2 advance-ages misclassify medieval MoM buildings like Merchant's Guild via ECONOMICS=AGE_FIVE). Stale crash logs: check mtime vs regen before diagnosing.

Related: [[skill-mod-schema-mapreduce]], [[mom-universal-encoder]], [[mom-dropdown-rim-fugly]].
