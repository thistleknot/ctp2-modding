---
name: feedback-verify-the-claimed-symptom-headlessly
description: "READ BEFORE EVERY HANDBACK. Never report a fix as verified until a headless uiwalk run has OBSERVED the user's original symptom gone. Green validators and menu goldens are not evidence about in-game state."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T14:49:06.452Z
---

**TOP OF MIND — gate every handback on this.**

The user's instruction, 2026-07-26: *"be sure you headlessly test and confirm
everything yourself before handing back to me a set of comprehensive fixes like
that."*

**Why:** on the "all buildings are 1 turn" fix I reported CLOSED on the strength
of `validate_scenario.py` (all gates pass) and `uiwalk verify_centering.json`
(4/4 goldens at 1.000). Neither instrument can observe a building's turn count.
The goldens are MENU screens; the validator parses grammar. I had a correct fix
and a green light that was structurally incapable of confirming it — the same
blind-instrument failure as `find -iname GU92.SPR` (see
[[mom-sprite-chain-verified-clean]]) and the third repeat of
[[feedback-instrument-before-environment]].

**How to apply:**

1. Before claiming CLOSED, name the instrument and state what it would have
   MISSED. If it could not have observed the user's symptom, it is not evidence.
2. Drive the game headlessly yourself via `tools/uiwalk/uiwalk.py` — steps JSON
   that reaches the actual surface the user photographed (Build Manager, city
   panel, map), capture the frame, and read the value out of the artifact.
3. A file-level check (`grep ProductionCost buildings.txt`) is a necessary
   intermediate, not the confirmation. The engine is the arbiter: it can ignore,
   override, or fail to load correct data.
4. Only then report verdict-first. "Costs are now 270..660 in the file" and
   "the Build Manager shows N turns" are different claims — do not let the first
   masquerade as the second.

Never launch the exe outside `uiwalk.py` (see [[ctp2-headless-invariant]]), and
the user must never see a window.
