---
name: slic-two-crash-classes
description: "TOP OF MIND — the two SLIC defect classes that took the MoM playthrough 7/25 → 25/25 clean; check both BEFORE theorising about stacks, dumps, or AI"
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T14:50:43.841Z
---

**CLOSED 2026-07-25.** `turnloop.py --turns 25` → 25/25, slic_errors=0.

**Class 1 — a 2-level USER-function chain from a HandleEvent body is a deterministic 0xC0000005.**
Builtins are free (`UnitDB`, `IsHumanPlayer`, `GetCityByIndex`, `CityHasBuilding`, `CreateUnit`, `AdvanceDB`, `BuildingDB`). The budget is per ENTRY POINT, not global. Fix = flatten; `MomPlayerIsX(p)` is literally `p == N`.

**Class 2 — SLIC event arg arrays are NOT populated for secondary args.**
`GrantAdvance` → use `value[0] == AdvanceDB(...)`. `CreateBuilding` → `value[0] == BuildingDB(...)`. Reading `advance[0].type` / `building[0].type` = "Array index 0 out of bounds", and **`advance[0] = value[0]` first does NOT fix it** — measured twice, two files, same line errored. That idiom was in the codebase and was simply wrong. Never touch the arrays.

**A crash that MOVES turn-to-turn when unrelated code changes is a threshold-crossing trigger, not a turn-N logic bug.** Here: the pool accrues from 0 and the auto-summon fires the first turn it caps, so any edit perturbing accrual moved the crash.

Falsified: AI casting (negative control gave 6/25, WORSE than 7/25); stack size (PE optional header parse = 8388608 = 8 MB, fix already in the binary — `dumpbin` silently produced nothing without the VC env, the Python PE parse was the working instrument); WER dumps (all Jul 24, `0xc0000374`, different exe path — pure noise).

See [[mom-wiki]] for the full entry. Related: [[feedback-instrument-before-environment]], [[ctp2-alertbox-interactive-confirmed]].
