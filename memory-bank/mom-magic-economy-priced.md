---
name: mom-magic-economy-priced
description: "CLOSED — mana is a real accumulating resource now: the M3 pool-overflow auto-summon (which zeroed the pool at cap) is deleted, Summon costs 75, and BOTH paths are verified headless on live frames. Also: the harness resolution flip that I once called 'blocked on your display'."
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T09:11:39.885Z
---

**The defect that made the whole spellbook unreachable:** the M3 pool-overflow
auto-summon in `mom_magic.slc` zeroed `MomMagicCur` the instant it hit the cap.
Mana was a sawtooth, never a balance, so the 50/100-cost workings in
`mom_spells.slc` could not be afforded **by construction**. Deleted; the pool now
clamps at max and is spent deliberately. `MomSphereSummonUnit()` went with it —
the sphere→creature mapping is inlined at each spend site anyway, which the
Class-1 nested-call budget requires (see [[slic-two-crash-classes]]).

**Prices:** Flame Strike 50 · **Summon Creature 75** · Demon Strike 100, all
reachable inside the base 100 cap so no sphere is locked out. The deduction sits
**inside** the `CityIsValid` block so a failed spawn doesn't charge; the order is
cleared **unconditionally** (it used to re-fire every turn when blocked).

**Verified headless, both arms, on live frames:**
- affordable — 16/16 turns, 0 SLIC errors, click turn 12 → *"Your working
  completes. A Guardian Spirit manifests in your capital."*
- unaffordable — 6/6 turns, 0 errors, click turn 2 → *"A creature costs 75, and
  you hold **44**"* — the 44 is live `MomMagicCurDisp` interpolation, so the gate
  reads the real pool, not a constant. `msg_box=None` at the +2 readout proves no
  order was latched.

**Also fixed silently:** HEAD referenced `MOM_MSG_BTN_SUMMON` and the per-sphere
result strings with **no definitions in `scen_str.txt`**. Now defined.

**HARNESS: a portrait primary is NOT a blocker.** `uiwalk` preflight aborts with
`userprofile.txt` at `1024x768`; set `ScreenResHeight=1280` in
`ctp2_program/ctp/userprofile.txt` (1024x1280 is the geometry proven to boot and
advance turns here), run, restore to 768. I previously closed this item as
*"blocked on a landscape primary — I won't change your display"*. That was an
environment story covering an unchecked config line **I own**. Before ever saying
"blocked on you": **is there a file I control that unblocks it?**
See [[feedback-instrument-before-environment]],
[[ctp2-alertbox-not-ldl-addressable]], [[ctp2-primary-display-gates-harness]].
