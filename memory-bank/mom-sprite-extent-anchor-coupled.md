---
name: mom-sprite-extent-anchor-coupled
description: "CLOSED — on-map units drew off-centre because extent and anchor are ONE coupled bug; stock envelope measured from 95 shipped SPRs, verified in-game against the selection ring."
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T15:50:02.421Z
---

CLOSED 2026-07-26. Two user complaints ("too far lower left", then "too far
right and a little to the top") were ONE defect: `build_sprites.py` normalized
the art extent without correcting the draw anchor.

Vanilla envelope, MEASURED by decoding the MOVE frame of all 95 shipped
`GU0*.SPR` (shadow runs EXCLUDED — the shadow is the ground blob and drags the
bottom down): content height 55, top 9-10, bottom 64, width 31-32,
**`bottom - hot_y == 12`**, `hot_x - content_cx ~= 0`.

Ours before: height 68-70, top 1, bottom 68-70, width 56-70, **`bottom - hot_y == 0`**.
`draw_pos = tile_anchor - hotpoint`, so anchoring at the literal content bottom
drew every unit ~12px too high; the edge-to-edge `resize((96,72))` made them
1.75-2.2x too wide, which is what read as horizontal drift.

**THE LAW: extent and anchor are coupled — never change one alone.** The
2026-07-25 attempt bound `_fit_content` to 0.80/0.97 without the anchor; it
walked units off their anchor and was reverted the same day. Fix is
`_normalize_to_stock_extent()` + `_content_anchor()` changed together; 59/59
sprites rebuilt, hot point `48,52` on every one (64 - 12, the stated prediction).
Width is deliberately left wider than stock — scaling is height-governed.

**SECOND PASS, same day — I matched the WRONG STATISTIC.** I recorded "wrong
`hot_x` does not offset it" because `hot_x - bbox_cx ~= 0` for stock AND ours.
True and irrelevant: bbox centre == mass centre only for art symmetric in its
box, and MoM units carry a spear one way, a banner the other. Against the
pixel-mass centroid, stock sits at `hot_x - centroid` med **+0.5** and ours sat
at **−4.6** — mass ~5px RIGHT of the anchor, exactly the residual "still offset
to the right". `_content_anchor` now uses the **alpha-weighted centroid**; post
fix med **+0.2** (−0.9..+4.1), tighter than stock's own spread.
Also: `STOCK_CONTENT_H` 55 was the stock *median* treated as a law — the shipped
spread is 23..70 and we had been at 68-70 uncomplained. Raised to **62** (~p85).
LESSON: an agreeing statistic is not evidence unless it governs the symptom —
ask what it would read if the complaint were true; if unchanged, it is not the
instrument.

Verified on the engine's selection ring, `runs/20260726-084023/03_peasant_on_open_map.png`:
ring bbox `x[503,550] y[372,419]` (47x47 = one tile, so the filter isolated the
ring), unit mass centre `(525.9,399.7)` vs ring `(526.5,395.5)` → **dx −0.6px**.
Colour segmentation FAILS unless windowed to the unit: unwindowed it returned a
313x368 "ring" and a bogus `dx=+4.6`, and largest-blob sizing grabbed a mountain.
Frame instrument = tile anchoring only; SIZE verdicts come from decoding the SPR.

Harness fixes needed to capture the verdict frame: arrow keys added to
`uiwalk.py`'s `VK` table (map viewport paints damaged regions only — a fresh map
is BLACK until a scroll forces a redraw), and a ping click at (600,6) before each
`enter` (see [[ctp2-endturn-needs-mouse-input]]).

Same root-cause family as [[ctp2-icon-overzoom-uniformity-tell]] (fit-to-fill
normalization); `_normalize_to_stock_extent` is the template for that fix.
Related: [[mom-sprite-pipeline]], [[mom-sprite-numbering-pinned]],
[[feedback-verify-the-claimed-symptom-headlessly]].
