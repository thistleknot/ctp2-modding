---
name: ""
metadata: 
  node_type: memory
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**Symptom:** research never advances (Science Manager shows "Turns To Discovery: -",
0 beakers) despite spending gold on science.

**Root cause:** `GOVERNMENT_ANARCHY` in the MoM scenario `govern.txt`
(`Scenarios/mom/scen0000/default/gamedata/govern.txt`) has `MaxScienceRate 0`
(and `KnowledgeCoef 0.1`), which hard-caps science at zero. The engine grants every
player the Monarchy *advance* at start (civ3log: "Player N was given Monarchy as an
initial advance") but STILL starts them in the **Anarchy government** — so science is
0 until the human manually switches government. Documented in lessons_learned.md:188.

**Fix:** set anarchy `MaxScienceRate 0.3` and `KnowledgeCoef 0.3` (the "research out of
anarchy" safety net). Re-applied 2026-07-10.

**Why this is a memory, not just the lesson:** this fix has REGRESSED at least twice —
the MVP-reset commit (`af18b2b` "Copy baseline") restored a stock govern.txt with
`MaxScienceRate 0`, silently undoing it. `govern.txt` is raw-copied and round-tripped by
`ctp2_generator.py` (loads + re-saves the scenario copy, ~line 3802), so a direct edit
survives generator runs but NOT a baseline re-copy. **How to apply:** after any
baseline/MVP reset, re-verify anarchy MaxScienceRate != 0 before playtesting.
Consider encoding it in the generator (`_ensure_*`) so a reset can't strip it.
Related: [[mom-crash-symbolication]] (separate UI-blit crash line).
