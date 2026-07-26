---
name: ctp2-input-reach-by-surface
description: "L7 — which input channel reaches a control depends on the SURFACE: menus take injection only (clicks dead), in-game SLIC alertboxes take CLICKS only (keyboard dead). Also: L1 send=capture×1.25 CONFIRMED in-game."
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T16:20:07.989Z
---

**L7 — input reach is per-surface, not global.** Measured 2026-07-24, headless.

| surface | clicks | keyboard | injection |
|---|---|---|---|
| main-menu aui screens | **DEAD** (0/36 sweep) | n/a | **works** (`press:`/`select:`) |
| in-game SLIC message/alertbox | **WORKS** | **DEAD** | untested |

This **scopes** [[ctp2-menu-injection-not-clicks]]. That memory said clicks never
work in CTP2 — true of MENUS only. Do not carry it into the in-game HUD.

**L1 IS CONFIRMED IN-GAME — the generalisation test passed.** Close button sat at
capture (335,376); L1 (`send = capture × 1.25`) predicted send (419,470) *before*
the run; that click dismissed the alertbox. L1 is a real law, not scenario_select
trivia. See [[ctp2-environment-laws]].

**Re-confirmed 2026-07-25 (link 7):** the alertbox latched ×1.25 again in both
arm runs, hitting a SPECIFIC arm (not just Close) at capture (300,375) and
(181,375). The competing "alertbox is 1:1" note in
[[ctp2-alertbox-interactive-confirmed]] has been corrected — still, run the
`_calibrate` battery rather than pinning ×1.25, because the measurement is
cheap and a remembered scale is a hypothesis.
See [[ctp2-interactive-slic-link7]].

**Evidence (one arm per run — do NOT bundle arms, a bad arm kills the process and
the retry then fails early, masking which arm did it):**
- `steps/close_armA_key.json` — enter 0, space 0, esc 0 *on the box* (esc's 99k
  delta was HUD/minimap redraw; the box was still open in the screenshot).
- `steps/close_armB_click.json` — click(419,470) → box gone, queued BeginTurn
  message surfaced underneath. That is `Kill()` executing.
- `steps/close_armC_control.json` — identical walk, click removed, equal wait →
  box **still open**. Rules out elapsed time / queued events.

**What this proves about interactivity:** input reaches an alertbox button AND the
button's SLIC block executes (`Button(ID_BUTTON_CLOSE) { Kill(); }` in
`mom_msg.slc`). It does **NOT** prove state mutation — `Kill()` is message
lifecycle, not game state. Still unproven: a button body that mutates a global,
and that the mutation persists and is observable on reopen.

See [[mom-magic-menu-verified]], [[ctp2-environment-laws]],
[[feedback-explore-hypothesis-loop]].
