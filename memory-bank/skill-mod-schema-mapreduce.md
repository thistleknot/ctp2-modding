---
name: skill-mod-schema-mapreduce
description: "CORE MODDING SKILL — merging N game mods is a SCHEMA MAP-REDUCE, not a union. The xlsx/csv control plane is the COMMON OBSERVATION FORMAT: encode each mod into it, compare their native (civilization, age) axes side by side, derive one UNIVERSAL schema, then MAP each mod's dimensions onto it and REDUCE. Naive first-wins union loses the per-mod civ/age semantics and forces hacky post-hoc gating."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**The methodology (user-defined, 2026-07-15): merging mods = schema map-reduce.**

1. **Control plane = common observation format.** The whole point of encoding each mod into the SAME xlsx/csv schema (`encode_civ2_mod.py`) is to OBSERVE and COMPARE mods in one format, then DERIVE a new unified schema. Not to dump them into one dimension.
2. **MAP** — each mod's dimensions carry native context that MUST be preserved:
   - **Civilization/faction**: civ2 fantasy mods tag every unit with its faction via the prereq short-code. HoMM2 `X1..X7` = the 7 @LEADERS factions (X1 Wizard, X2 Sorcerer, X3 Barbarian, X4 Necromancer, X5 Knight, X6 Warlock, X7 Neutral). Midgard `X1..X7` = Elves/Merfolk/Goblins/Stygians/etc. Crusades = historical civs, real tech-gated (no X#).
   - **Age/epoch**: @CIVILIZE advance rows carry an epoch column; HoMM2's tech tree is literally "Creatures Lvl. 1-6" + "Knowledge Lvl. N" (creature-tier = age). Units gate on those.
3. **NORMALIZE** — per-mod maps into the universal axes: `mod_faction -> universal_civ` (e.g. the 5 magic spheres Life/Nature/Death/Chaos/Sorcery + neutral), `mod_epoch -> universal_age`. These live in a per-mod schema file the user reviews.
4. **REDUCE** — dedup same-concept dimensions ACROSS mods (not first-wins-by-name), each carrying its universal (civ, age). Then gate units on their universal civ's ladder + age.

**What I did WRONG first (anti-pattern):** naive union of units.csv with first-source-wins name dedup, treating the X# faction codes as ordinary advance prereqs. Result: faction/age semantics lost, everything ungated/turn-1-buildable, then hacky keyword-inference faction gating bolted on. The fix is to map-reduce the SCHEMA, not the rows.

**Upstream repo (user, 2026-07-15):** the modding abilities (wiki/memory-bank/skills/harness) are being extracted to a standalone repo to resume AI-driven mod merging later. These skill memories are that repo's seed.

Related: [[mom-universal-encoder]], [[skill-ctp2-crash-classes]], [[smm-super-magic-mod]].
