---
name: mom-intermittent-setup-crash
description: "0xC0000005 exit right after \"SPNewGameWindow.ScenarioButton used\" (KERNELBASE, no civ3log trace, surfaces clean) = the documented intermittent New-Game-setup crash — RETRY, do not re-investigate"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**Signature:** game exits `-1073741819` (0xC0000005) with the civ3log ending at
`SlicEngine.cpp@2089: SLIC: control SPNewGameWindow.ScenarioButton used` (then a unit-DB
dump), fault module KERNELBASE.dll, NO exception trace in civ3log, 0 blitter-guard hits.

**This is the documented intermittent New-Game-setup crash** — lessons_learned.md:69
("AllinoneWindow (New Game setup) crashes can be intermittent"). It fires at the scenario
picker, BEFORE any gameplay/banner renders, so it does NOT indict whatever was last changed.

**Why:** the New-Game setup screen AVs intermittently at image-load. Release/debug crash
symbols are approximate; do not over-read them.

**Correct response (do NOT repeat the mistake of re-diagnosing it each time):**
1. Confirm `validate_all_surfaces.py` is clean (it will be).
2. Just RELAUNCH — "a single retry of the launch often succeeds" (it consistently does).
3. Alternatively, load a save to bypass setup (lessons_learned:542).
4. INTERMITTENT bug: one clean launch proves nothing; one crash indicts nothing — need
   3-4 consecutive clean games to judge a real fix (lessons_learned:422).

**Why this memory exists:** across 2026-07-09..11 I repeatedly treated this crash as a
fresh mystery and rebuilt/spelunked instead of recognizing the signature and retrying.
Recognize it on sight and retry. Related: [[mom-crash-symbolication]].
