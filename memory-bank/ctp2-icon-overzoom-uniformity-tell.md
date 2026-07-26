---
name: ctp2-icon-overzoom-uniformity-tell
description: Unit icons looked wrong two different ways from ONE cause — fit-to-fill normalization; the tell was a measurement that was IDENTICAL across every file.
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T12:56:48.491Z
---

CLOSED 2026-07-25, confirmed live in-game. Two reported defects — "guardian spirit
too big for the unit preview ui" and "the carpet (spearman) doesn't match the
drapes (on map icon)" — were **one** cause: `build_unit_icon_art.fit_pad` was
called as `fit_pad(crop_to_content(im))`, i.e. crop tight then scale until the
content FILLS the 160x120 frame.

**The diagnostic tell: uniformity.** Height content extent measured EXACTLY 0.95
on all 55 MoM icons (median == max). A distribution with zero variance is not
source variance, it's deterministic normalization. The same units' SPRITE art sat
at median 0.66. Broad figures overran the 96x72 preview box; thin figures with a
protruding weapon had the tip severed by the frame, leaving a floating sliver.

Fixes, both needed: generator capped at `ICON_CONTENT_MAX_FRAC = 0.80`, AND the 55
durable TGAs repaired by `tools/reframe_unit_icons.py` — a regen cannot restore
pixels already clipped away, and shipped TGAs are durable truth (ICON_ADVANCE
precedent). Gate after: median 0.62, max 0.78, edge-clipped 0, format violations 0.

**FULLY CLOSED 2026-07-26 — there was a THIRD producer.** The repair kept
regressing because `ICON_UNIT_*.tga` is written by *three* tools:
`civ2_sprite_extractor.py`, `build_unit_icon_art.py`, `reframe_unit_icons.py`.
Only the last two capped at 0.80; the extractor's `_scale_rgba_to_canvas` was
unconditional fit-to-fill, so **every regen silently un-repaired the icons.**
Now it takes `max_frac`/`floor_margin`; the sprite call sites keep fit-to-fill
(their consumer does its own 96x72 fit), the icon call site passes 0.80 + a 6px
floor. Post-fix gate: height median 0.77 / **max 0.78**, over-cap 0,
edge-clipped 0, and all 62 `SPRITE_*.tga` **byte-identical**. Pipeline is now
idempotent — `reframe_unit_icons` over the new output is a no-op.

Two traps the measurement caught, both invisible to reading the code:
* **`int()` → `round()` is not cosmetic.** "Tidying" the shared scale math moved
  33 sprites by a pixel. The byte-identical sprite gate caught it in one run.
* **Never-upscale is right for the repair tool, WRONG for the extractor.**
  `reframe` clamps at 1.0 because its input is already 160x120; the extractor's
  input is a ~40px atlas cell, so the same clamp left every figure at **0.28**
  of the frame. Divergence is documented in the docstring so it isn't "fixed"
  back.
* **Method:** when a repair keeps regressing, stop repairing and count the
  *producers* of the artifact.

**Correlation collapse ≠ different art.** My first plan was a wholesale
sprite→icon copy; 30/62 pairs scored below 0.80 Pearson, which *looked* like
mismatched art. Visual inspection of the 8 worst showed 7/8 were the same subject
— the zoom difference alone destroyed the correlation. `SAME_SUBJECT_MIN_CORR =
0.20` now separates them (same-subject floor 0.26 ZOMBIES; true mismatch 0.06
SETTLER). **Still open: SETTLER proxy art** — icon is a robed settler, sprite is a
blue Wraith.

**Measure the instrument first** (see [[uiwalk-assert-slack-not-stale-goldens]]):
faint 1px background "stars" defeat a naive threshold and return full-frame bboxes
for everything — that produced a bogus uniform "0.97" earlier. Threshold 40 +
`ImageFilter.MinFilter(3)` yields the real silhouette.

Off-centre units (same report) were separate: SPRITE_HOT_POINTS is the engine's
draw anchor, so a wrong hot point *translates* without resizing. Fixed in
`build_sprites.py`, 59/59 SPRs uniform. Confirmed in-game — feet land on tile
centre.

Verification note: the map capturing black was the modal BeginTurn box suppressing
the paint, NOT a renderer defect (133,827 → 183,035 non-black after dismiss).
Related: [[ctp2-primary-display-gates-harness]], [[feedback-instrument-before-environment]].
