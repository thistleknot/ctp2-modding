---
name: ctp2-endturn-needs-mouse-input
description: "CLOSED 2026-07-25 - END TURN needs a mouse message to have reached the engine, NOT a cleared modal; unhittable widget != useless input"
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T02:39:25.691Z
---

CLOSED, 14/14 turns clean. CTP2's injected END TURN press resolves the LDL path
and returns OK but does NOT advance the turn unless some mouse message has
reached the engine that turn. An off-screen window receiving no pointer input
leaves aui in the state where `EndTurnButtonActionCallback` takes its silent
early-return (`GetCurPlayer() != GetVisiblePlayer()`).

**The falsified claim was mine.** I wrote that the message-dismiss clicks were
pure collateral damage and dropped them; the run went 4/4 -> 0/12. The green run
showed `closed=False` on EVERY turn while `advanced=True` on every turn -- the
click never closes the box but is still required. I had inferred "these clicks do
nothing" from "these clicks do not close the box", which is strictly weaker.

**Fix:** `engine_ping()` in turnloop.py posts one click at
`TOP_BAR_INERT = (600, 6)` (blank top-status-bar chrome, no widget, cannot
scroll) immediately before `end_turn()`. Keep the input, drop the aim. This also
closes the user's "clicking down into unexplored area" complaint -- misses used
to land on the map and pan it.

Eliminated by test, not argument: timing race (3 bounded retries, identical
failure) and the SLIC removals (restored to HEAD, box on screen, still no
advance).

**Residual now CLOSED too (2026-07-25).** I claimed these boxes were un-closable
because "the window is built at runtime, so there is no named LDL node". Wrong --
my four tried paths were all under `MessageBoxDialog`, a DIFFERENT engine dialog.
`messagewindow.cpp:114` hard-codes `StandardMessageWindow`; L330 builds
`.StandardMinimizeButton`; `aui_region.cpp:299` Associates it into the by-string
table `inject_press` searches. Runtime-created controls ARE addressable by static
LDL path. Measured: `dismiss message -> delta=99148 closed=True via
StandardMessageWindow.StandardMinimizeButton`, first candidate, first try.
Injection never touches the cursor, so the process-lethal x1.25 click on that
surface is irrelevant. See [[ctp2-alertbox-interactive-confirmed]],
[[ctp2-input-reach-by-surface]], [[feedback-instrument-before-environment]].
