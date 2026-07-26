---
name: ctp2-primary-display-gates-harness
description: "The engine reads the PRIMARY display; a portrait primary makes 1024x768 illegal, the profile is discarded, the UI letterboxes, and harness clicks AV. Also — the 1.25 ratio corrected, and sprite content-extent normalization."
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T04:11:10.384Z
---

**The 1.25 ratio, corrected (deliverable (c), 2026-07-25).** Two separate facts,
do not collapse them:

1. **Geometry is 1:1.** PrintWindow captures the engine's 1024x768 surface blitted
   UNSCALED into the client's top-left (measured content bbox `(0,0)-(1021,759)`
   at a 1280x960 client). Capture coords ARE engine coords. My earlier note
   calling the unscaled-blit model "FALSIFIED" was itself wrong.
2. **The SEND scale is NOT derived from that geometry.** It is empirical and
   PER-SURFACE: message = x0.80, alertbox = x1.25. Sending x1.25 on the message
   surface is **process-lethal** — 0xC0000005, 2/2 runs. See
   [[ctp2-input-reach-by-surface]] and [[ctp2-environment-laws]].

**The harness's real gate: `1024x768 LEGAL on the PRIMARY display`.**
`display_IsLegalResolution()` honours `userprofile.txt`'s `ScreenRes*` only on an
exact match in the **primary** display's mode list. Measured 2026-07-25:

```
\\.\DISPLAY4 PRIMARY=True   1080x1920 orient=1  1024x768_legal=False
\\.\DISPLAY5 PRIMARY=False  1920x1080 orient=0  1024x768_legal=True
```

**CORRECTED 2026-07-26.** The letterbox chain below is WRONG and the
"do not open a code investigation" instruction was over-broad -- see
[[ctp2-alertbox-not-ldl-addressable]]. What is actually true: `1024x1280` IS
legal on the portrait primary, boots, and advances turns; `1024x768` is not, and
`768x1024` fails `boot asserts failed: new_game_check`. Clicks do not miss a
letterboxed offset -- a posted mouse BUTTON is process-lethal at this client
regardless of coordinate, while a posted `WM_MOUSEMOVE` is safe. Superseded text
follows for provenance only:

~~Portrait primary -> profile discarded -> fallback head mode -> letterboxed UI at an
unknown offset.~~ Goldens still PASS (template search is padded) but **clicks are
not padded**, so the aim point misses and the process AVs at `turns_reached=0`.
A run that starts with that preflight line False is not a valid observation of
anything. Fixing it means changing the user's desktop (primary assignment or
rotation) — **surface it, never do it silently**.

**RE-CONFIRMED BY FULL BISECT, 2026-07-26 — read this memory BEFORE debugging a
`turns_reached=0` AV.** I spent a long session attributing that AV to my own
code and walked the whole ladder for nothing. Every rung came back clean:
scenario SLIC (all six `#include`s disabled → still crashed), the four MoM
BeginTurn handlers (neutered → still crashed), founding a city (`--turns 3`
with NO city → still crashed), ending a turn (`--endturn none`, zero end-turn
input → **still crashed**), the 1 MB stack (PE header says StackReserve =
8388608, the fix is present), `validate_scenario.py` (all gates pass), and AI
build lists (0 dangling across all four lists). The `--endturn none` run is the
decisive one: it crashes with no end-turn action at all, which retires "the
crash is in the city/end-turn path" entirely. The preflight ABORT is the
harness correctly refusing to produce an observation; `UIWALK_ALLOW_ILLEGAL_RES=1`
buys a run, not a valid one. **If that preflight line reads False, stop and
surface it — do not open a code investigation.**

**Bisect by flag, not by argument.** I suspected a sprite rebuild caused the AV.
Because the new bound was made env-overridable (`MOM_SPRITE_MAX_W_FRAC=1.0`), I
rebuilt the exact pre-fix artifacts and re-ran: still crashed. Hypothesis
rejected in one run. Make a change revertible by a flag and the bisect is cheap.

**Sprite preview overflow (defect 2, fixed).** `_facing_images` did a bare
`resize((96,72))` — that fixes the CANVAS, not the CONTENT, so an edge-to-edge
source overflows the control panel's fixed ~77x65 viewport while the map (no
viewport) draws it fine. Fix = `_fit_content`: crop to opaque bbox, downscale
only if past `0.80 w / 0.97 h`, re-paste **bottom-centred** (a unit stands on the
ground), scale clamped <=1 so conforming sprites are byte-identical, then
re-apply the `DARK_FLOOR` nudge (LANCZOS over a transparent surround manufactures
pure-black pixels that makespr's chromakey would eat). The defect is WIDTH, not
height. **21 of 62 sources change** — Guardian Spirit (0.875 w) is 14th worst,
not an outlier; it is just the one the user clicked. Gate tolerance must be ONE
PIXEL per axis (0.80*96 = 76.8 → 77px = 0.8021; float-exact can never pass).

**The visual channel for this defect is dead**: PrintWindow renders the control
panel black, and `n` does not cycle units (byte-identical captures — keyboard is
dead on in-game surfaces). Verification is therefore ARTIFACT-level: run the real
`_facing_images` path over every source and assert the bbox fraction.

Full detail: `Scenarios/mom/lessons_learned.md` (three entries dated 2026-07-25).
