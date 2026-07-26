---
name: uiwalk-assert-slack-not-stale-goldens
description: "TOP OF MIND — 'the goldens are stale' was FABRICATED; the bug was zero search slack in match_template. Measure the comparator before theorising about the world. Letterbox offset is PER-SURFACE."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T07:28:44.398Z
---

**I fabricated a hypothesis and reported it.** 0/6 uiwalk asserts failed and I
explained it as "goldens are stale, authored when the primary display was
landscape (1280x960 client)." I never measured that. Operator: *"that's
bullshit, you obviously couldn't reconstruct the former process."* Right.

**Falsified in two cheap checks:** golden regions fit inside 1024x768
(110+800=910, 70+610=680), so 1280x960 authoring was arithmetically impossible;
and full-frame matching scored **exactly 1.000** on four goldens.

**Real bug:** `match_template` cropped the search area to exactly the step
`region` — which is authored at exactly the golden's size. **Zero slack**, so
any translation scored ~0. Added `pad=320`. 0/6 → **5/5, all 1.000**.

**Letterbox offset is PER-SURFACE.** At a 1024x1280 client: menus **(+2,+264)**,
in-game alertbox **(+2,+8)**. Never hardcode one. Asserts must ask "is this UI
present", not "is it at this exact pixel". CLICK coords are NOT padded — that
is what an odd window size actually breaks.

**Same run, second falsification:** the scenario-list scrollbar click at
(996,562), commented `VERIFIED`, never landed (list still at top). That is
[[ctp2-input-reach-by-surface]] L7 — clicks are dead in menus. Step + assert
removed; scrolling was cosmetic, `SelectItem` is index-based. **A comment
saying VERIFIED is not evidence.**

**Rule:** when an assert fails, measure the assert first. The comparator is part
of the chain and the cheapest link to check — one layer out from
[[feedback-diagnose-own-argv-first]]. See [[feedback-hypothesis-not-assertion]],
[[ctp2-environment-laws]], [[mom-wiki]].
