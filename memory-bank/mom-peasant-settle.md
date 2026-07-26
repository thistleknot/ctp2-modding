---
name: mom-peasant-settle
description: MoM has NO settler unit — peasants found cities; engine spawns first SettleLand DB unit at game start; UNIT_CITY must be the complete base block
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**MoM design (canonical, in-game confirmed 2026-07-03, commit 49bbd5e):** there is NO settler
unit. `UNIT_PEASANTS` is the only city builder — it carries the full settle kit lifted from the AE
base settler (`SettleCityType UNIT_CITY`, `SettleSize 1`, `Settle: Land/Mountain`, `Civilian`).
`UNIT_SETTLER` stays in the Units DB but retired (`CantBuild`, **no** `Settle:` lines) purely to
avoid dangling Great Library/string references and DB index shifts. Do NOT restore its Settle
lines.

**Why that matters at game start:** `gameinit_PlaceInitalUnits`
(`H:\Games\civctp2\ctp2_code\gs\utility\gameinit.cpp:404`) spawns as starting units the FIRST unit
in the DB with `SettleLand` — no hardcoded settler. Settler without Settle lines ⇒ new games start
with Peasants.

**Settle failure modes:** the settle order spawns `UNIT_CITY` — that block must be the COMPLETE
base-game block (terrain classes, CantBuild/NoIndex/GLHidden/NeedsNoSupport, Revolution), not a
stub. With scenario SLIC disabled, settle failures are SILENT; the two legit runtime gates are
(1) unit already moved this turn (needs unspent move points), (2) tile inside another city's
radius. Fix lives in `ctp2_generator.py` templates (control plane) + scenario `Units.txt`. See
[[mom-sprite-pipeline]], [[mom-canonical-toolchain]], [[mom-db-error-class]].
