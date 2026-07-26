---
name: ctp2-interactive-slic-link7
description: "CLOSED 2026-07-25 — interactive SLIC round-trips a turn boundary; two arms discriminate; the failure was a harness PHASE error (+1 vs +2), not SLIC"
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T16:12:45.125Z
---

**Link 7 CLOSED (commit `6de6eb1`).** A MagicMenu alertbox arm writes
`MomSummonChoice[g.player]`; the `MomSummonOrderTick` BeginTurn consumer in
mom_msg.slc reads it the FOLLOWING turn, spawns the unit, and clears it. Both
arms measured headless, `VERDICT OK 6/6 slic_errors=0`:

- arm 1 → "A Guardian Spirit manifests in your capital.", stack 1→2
- arm 2 → "Zombies claw their way up in your capital.", stack 1→3

TWO arms is the whole point — with one, "the ordered unit appeared" cannot be
told apart from "the handler always summons that unit". See
[[ctp2-alertbox-interactive-confirmed]] for links 3–6 (all intra-turn).

**Rules that held:** a `Button` body carries the same Class 1 nested-call budget
as a HandleEvent body → arm bodies stay assignment-only, consumer calls ZERO
user functions (see [[slic-two-crash-classes]]). Clear the order
unconditionally, else an unfillable order re-fires and stops pinning which turn
consumed the click.

**Harness (turnloop.py):** alertbox geometry now DERIVED (components + dark
column runs), never absolute capture constants — changing button CAPTIONS moved
every button (159/206/263/330 → 54/101/181/300), so fractions would have missed
all four arms. Engine renders buttons in REVERSE declaration order: decl index
i is `detected[-(i+1)]`. Alertbox latched send = capture **×1.25** here,
contradicting the older 1:1 note — `_calibrate` is the authority
([[ctp2-input-reach-by-surface]]).

**The defect was mine and it was a PHASE error.** Readout at `summon_turn+1`
printed `msg_box=None`. The arm is clicked at the END of iteration N, *after*
that iteration's `end_turn` already ran the next BeginTurn — so the first
BeginTurn that can see the order is fired in iteration N+1 and its popup shows
at N+2. Reading the captured FRAME (`turn_004.png`, popup + new unit plainly
visible) settled it in one look, before any SLIC hunting.
See [[feedback-instrument-before-environment]].

Still open: the "somewhere nearby within their territory" placement rule — the
consumer spawns at city index 0.
