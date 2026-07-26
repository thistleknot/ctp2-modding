---
name: mom-magic-menu-verified
description: "CLOSED 2026-07-24 — the j hotkey opens the MoM MagicMenu alertbox in-game, verified headlessly twice; the five-day 'SLIC is broken' saga was never SLIC. One command reproduces it."
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T07:28:57.597Z
---

**DO NOT RE-LITIGATE.** `j` → `MAGIC STATUS` alertbox WORKS in a loaded MoM game.

Reproduce (nothing required from the user; window never visible):
```
cd Scenarios/mom/tools/uiwalk
python uiwalk.py --run steps/magic_j_e2e.json --marker MagicMenu --save none
```
Expect **5/5 PASS, every check 1.000** (2026-07-25). Step count dropped from 6:
the scenario-list scroll click + its assert were removed as a dead menu click
(law L7) — see [[uiwalk-assert-slack-not-stale-goldens]]. `magic_menu_check`
also scored **0.992 on an independently generated map** — reproducible, not a
lucky frame.

**Evidence:** `runs/20260725-002704`; golden `goldens/post_j_settled.png`
re-baselined to the four-button box, region `[10,228,372,186]`. Box reads `MAGIC STATUS / Mana: 10 / 100 /
Income: +10 per turn / Close`. Pixel delta 69,465 (L4 addendum: ~69k = mid-size
alertbox; the ~180k prediction was wrong in magnitude, right in kind).

**Scope.** This run proved the **display-only** path: key delivery → segment
lookup → SLIC execution → render → correct interpolated scalars.
**Interactive buttons are now ALSO confirmed** (2026-07-24, links 5+6) — a
button body mutates state and it persists across reopen. See
[[ctp2-alertbox-interactive-confirmed]].

Also confirmed in-game: the `BeginTurn` magic message fires on its own
(`Magic Power: 10 / 100 (+10 per turn)` visible before any key), so L5 holds —
a NEW game compiles SLIC fresh, no `/reloadslic` needed.

Path to the map, all verified headless (`steps/reach_in_game.json`):
main_menu → new_game → scenario_select → scroll → pack_contents →
`select AvailableListBox,0` + `press ScenarioWindow.LoadButton` →
`press SPNewGameWindow.StartButton` → in_game_mom.

**Never golden a region containing terrain** — the map is generated per run.

See [[ctp2-headless-invariant]], [[ctp2-environment-laws]],
[[mom-slic-namespace-segments]], [[mom-slic-save-cache]].
