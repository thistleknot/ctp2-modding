---
name: mom-generator-pass-ordering
description: "CLOSED — every MoM building was a 1-turn build because the age-band cost rescale ran ~1300 lines BEFORE the ingest that rewrites the file. Pass ordering inside ctp2_generator.main() is a recurring bug class; _read_rel() during a pass sees the PREVIOUS run's file."
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T14:46:26.729Z
---

**TOP OF MIND when a generator transform's output looks untransformed: check
WHERE it runs before checking WHETHER it runs.** Three defects in one code path,
2026-07-26, commit `b94b679`, pushed to `modding` + `momjr`.

**1. Buildings all showed "1 turn".** `_retune_mom_improvement_costs()` maps raw
Civ2 costs (4..60) into the base CTP2 per-age band of the advance that gates
each block — the age-scaling the user described, already built, already correct.
It was called at `main():2863`; `_merge_mom_improvements_into_buildings()`
rewrites `buildings.txt` with raw CSV costs at `main():4156`. Clobbered every
run. Discriminating evidence: same function, same on-disk input, opposite
outcome when called standalone — only ordering explains that. Costs now 270..660
inside measured bands (`AGE_ONE 270-875` … `AGE_TEN 3500-7500`). Wonders
(2160-7200) and units (150-740) were never affected; their retunes run after
their own ingestion.

**2. Same class: `_read_rel()` inside a pass reads the PREVIOUS run's file.**
The registry only flushes at `save_all()`. The merge's "is this advance real"
guard was testing against stale `Advance.txt`. Use `reg.load(...)` +
`getattr(f, "_text", "")` (precedent at ~line 2693).

**3. `advance_code_map.csv` has two lanes that disagree ON PURPOSE.**
`unit,MT→ADVANCE_THEOLOGY` vs `prereq,MT→ADVANCE_COMMUNE_WITH_GODS`. Buildings
were read through the unit lane only (prereq-only codes fell to fallback), but
flat-merging prereq OVER unit is equally wrong — 5 prereq targets are dangling
(COMMUNE_WITH_GODS was never generated), which demoted Cathedral 660→360.
Correct shape is a CHAIN: prereq lane → unit lane → fallback, accepting a
candidate only if it exists AND is not self-prereq-disabled (CTP2's sanctioned
unresearchable form, `Advances.cpp:498`, applied to 169 base advances in MoM —
gating on one makes a building dead content).

**The law: a silent fallback is how all three survived.** The fallback behaviour
was correct; the silence was the defect. Generator now prints
`! prereq code 'X' for 'Y' is dangling or disabled`. Exactly one fires and it is
right: `Eco` / Merchant's Guild → ALPHABET, since `ADVANCE_ECONOMICS` is a
disabled stub.

**Control plane is intact** — `tools/momjr_csv/*.csv` (30 files) authored,
`mom_dimension_inventory.xlsx` regenerated at 33 sheets every run. Every defect
here was in the extraction/emit layer, never in the control plane.

See [[mom-canonical-toolchain]], [[feedback-instrument-before-environment]],
[[mom-wiki]].
