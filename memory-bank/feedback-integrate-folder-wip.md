---
name: feedback-integrate-folder-wip
description: "WIP items get moved to an integrate/ folder (not deleted) when reverting to a known-good baseline, so nothing is lost"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c5fa2bd2-0b1c-4e75-a617-6e92217b1336
  modified: 2026-07-23T00:54:07.072Z
---

When a change regresses a working state and the fix is to restore a known-good baseline (e.g. the last-working `mom.zip`), do NOT delete the in-progress additions — **move them to an `integrate/` folder** (the user's WIP convention) with a README documenting what/why/how-to-reintegrate. Then restore the baseline to the live tree.

**Why:** the user tracks work-in-progress in an integrate folder so a revert never loses the new work; it can be re-added incrementally later. User called this out explicitly 2026-07-22 ("move those additions to the side... I usually use an integrate folder for wip items").

**How to apply:** on any "restore the working version" / "this was working before" request — locate the known-good baseline (a `.zip` snapshot, a git tag, etc.), `diff` to find what changed, copy the current (divergent) files into `<project>/integrate/<feature>-wip/` + a README (what's stashed, the regression hypothesis, a one-module-at-a-time re-integration order), then restore the baseline files to live. Preserve unrelated improvements (e.g. art/data files) — revert only the regressing subsystem. See [[mom-wiki]] for the MoM lessons log.

Concrete instance: the MoM interactive spell/petition SLIC layer (`mom_spells.slc`, `mom_ritual.slc`, + `mom_func`/`mom_magic`/`mom_msg`/`scenario.slc` edits) hard-crashed turn 1; stashed to `Scenarios/mom/integrate/slic-magic-layer-wip/`, baseline restored from `Scenarios/mom/mom.zip` (2026-07-15).
