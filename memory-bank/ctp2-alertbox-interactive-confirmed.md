---
name: ctp2-alertbox-interactive-confirmed
description: "CLOSED — SLIC alertbox buttons mutate state and it persists (links 5+6); capture regression was the intro movie + accelerated SDL renderer, NOT the display"
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T16:19:54.208Z
---

**Links 3–6 all CONFIRMED 2026-07-24.** A SLIC `alertbox` button body runs
arbitrary statements and its mutations persist across `Kill()` + reopen.
Three arms, one per run, each a fresh new game (baseline `Mana: 10`):

- ARM 1 Random → `MomMagicCurDisp = 42` → reopen reads **Mana: 42** (link 5 scalar + link 6)
- ARM 2 Research → `MomMagicCur[g.player] -= 3` → reopen reads **Mana: 7** (link 5 at MODEL level)
- ARM 3 Goal → `AddGold(g.player, 500)` → HUD gold **106 → 606** (SLIC→engine boundary)

Never end a turn between click and reopen — `MomMagicPoolTick` recomputes the
Disp scalars every BeginTurn and mimics "did not persist". Control that rules
out a repaint artifact: the BeginTurn message box in the same frame still read 10.

**Capture regression CLOSED — two causes, both now baked into `uiwalk.Game.launch`:**
1. `SDL_RENDER_DRIVER=software` + `SDL_FRAMEBUFFER_ACCELERATION=0`. The default
   accelerated backend's surface is unreadable by GDI `PrintWindow`
   (61,040 → 151,173 non-black pixels on an identical frame).
2. `nointromovie` arg. `civapp.cpp:594` plays a ~40s cinematic over the whole
   client; `civ3_main.cpp:1104` clears `g_useIntroMovie`. Every "black capture"
   for days was that movie.

**FALSIFIED (do not re-litigate):** primary-monitor orientation. The mechanism is
real — `display.cpp display_EnumerateDisplayModes` reads display 0 only, so
`userprofile.txt ScreenRes*` is honoured only when it names a PRIMARY-display
mode — but it explains window SIZE only. A legal, honoured 1024x1280 window was
still black. Also falsified: stash position, modal dialogs, crop/geometry.

**Coord scale is per-surface AND per-run — MEASURE IT, never carry it forward.**
This note originally read "alertbox clicks are 1:1, the L1 ×1.25 factor does NOT
apply." **CORRECTED 2026-07-25:** in both link-7 runs the alertbox latched
`send = capture ×1.25`. So neither value is a property of the surface — the
`_calibrate` battery over `SCALE_CANDIDATES = (1.25, 1.00, 0.80)` is the only
authority, and a remembered scale is a hypothesis, not a constant. A miss lands
on empty map (safe no-op), which is what makes the battery cheap.
See [[ctp2-interactive-slic-link7]].

`--save` defaults to `uiwalk_start`; pass `--save none` to boot to the menu.
See [[feedback-diagnose-own-argv-first]], [[ctp2-environment-laws]],
[[ctp2-input-reach-by-surface]], [[mom-wiki]].
