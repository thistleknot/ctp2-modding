---
name: ctp2-environment-laws
description: "THE LAWS — one transition function underlies every CTP2 screen; coordinate transform, click protocol, injection channel, delta decoder, SLIC persistence, binary identity. Per-state pixel tables are derived from these, not independent facts."
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T01:23:38.839Z
---

**There is ONE transition function under every screen. The latent space does not
collapse between states.** Build the model; derive per-state coordinates from it.
A per-state lookup table cannot be wrong usefully — it just goes silent off-table.
**A law is only real if it predicts a state never visited.**

Full detail + evidence: `Scenarios/mom/tools/uiwalk/ui_map.json -> environment_model`

**L1 — coordinate transform.** `send = capture × 1.25`. Engine renders 1024x768,
client is 1280x960; incoming click coords are scaled by 0.8. Captures are 1:1
with logical coords; only the SEND path is scaled.
*Evidence:* predicted row1 needs send(625,300) before running it → row1 selected.
*Scope:* claimed global. **Confirmed only in scenario_select; untested in-game.**

**L2 — click protocol.** Before each click, move to and post `WM_LBUTTONUP` at the
**PREVIOUS** click position. Otherwise the first click grabs a control that is
never released and every later click is swallowed.
*Evidence:* 1/3 clicks landed before the fix, 3/3 after (5180/79455/4338 px,
reproduced exactly). Releasing at the NEW position was tested and FALSIFIED.
*Scope:* claimed global. **Confirmed only in scenario_select.**

**L3 — injection channel.** `press:<ldl>` / `select:<ldl>,<idx>` call
`InjectPress` / `SelectItem` in C++ — no cursor, no coords, no grab, works
regardless of scroll or visibility. `CTP2_LISTBOX` is `atomic true`, so its rows
and scrollbar have NO ldl path and require L1+L2 clicks instead.

**L4 — observation decoder.** Pixel delta between consecutive shots classifies the
outcome: `0` = input never landed (or a modal ate it) · `~4-5k` = row selected /
button enabled · `~75-80k` = list scrolled a page · `~180k` = panel opened or
closed · `~477k` = whole screen, i.e. crash or blank, NOT a UI response.

**L5 — SLIC persistence.** CTP2 serializes compiled SLIC into saves; a loaded save
ignores edited `.slc` until `/reloadslic`. A NEW game compiles fresh. This decides
which entry path can test a SLIC change at all. SLIC only enters scope AFTER
scenario load begins — pre-load crashes are never SLIC.

**L6 — binary identity.** Assert the exe under test, never assume it. `build.bat`
builds only Final-SDL (`ctp2.exe`); the launcher re-stages `ctp2-dbg.exe` over
manual copies on every run. Enforced by `preflight_exe()`.

**Weak point to attack:** L1 and L2 make global claims on local evidence. The
in-game HUD is different LDL entirely — if they hold there unchanged the model is
real; if not, they were per-state trivia in a general costume.

See [[feedback-explore-hypothesis-loop]], [[ctp2-menu-injection-not-clicks]],
[[feedback-hypothesis-not-assertion]].
