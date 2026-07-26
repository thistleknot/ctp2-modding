---
name: mom-sprite-chain-verified-clean
description: "CORRECTED 2026-07-26 — the chain was NOT clean. ctp2.exe reads BOTH GU%.2d.SPR and GU%.3d.SPR; base GU092.SPR shadowed MoM's GU92.SPR. My find query structurally could never have seen it."
metadata:
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T14:16:13.766Z
---

**The former verdict in this file — "not a defect, the UI portrait and the map
sprite are the same picture, DO NOT RE-INVESTIGATE" — was WRONG.** I asserted it
three times across three user reports. It was a real plumbing bug the whole time.
Fixed 2026-07-26, commit `b212730`, pushed to `modding` + `momjr`.

**Real cause.** `ctp2.exe` carries BOTH format strings `GU%.2d.SPR` and
`GU%.3d.SPR`, and stock CTP2 ships sprites under both conventions (124
zero-padded, 83 unpadded, all mtime 2000-11-01). `build_sprites.py` wrote only
the unpadded name, so wherever a base zero-padded twin existed the engine
resolved that one first and served **stock art for a MoM unit**.
`SPRITE_SPEARMEN 92`: MoM's `GU92.SPR` (19,190 B) lost to base `GU092.SPR`
(562,756 B). Same collision on `SPRITE_ZOMBIES 91` and `SPRITE_SWORDSMEN 93`.

**Fix.** `_dest_names(num)` returns `{GU{n:02d}.SPR, GU{n:03d}.SPR}` and the
builder writes both. Deterministic gate: all 59 MoM-owned sprite ids (91-149)
are byte-identical twins, so there is no filename the engine can resolve that
holds base art. Ids 2-90 remain divergent — that is stock CTP2's own shipped
state, untouched by MoM and not a defect.

**`%.2d` means MINIMUM two digits.** For n<10 the pair is `GU03`/`GU003`, never
`GU3`. My first audit script used `GU%d` and reported 58 phantom divergences.

**Method lesson — this is the expensive one.** The "verification" that produced
the false all-clear was `find -iname 'GU92.SPR'`. That query **structurally
cannot return `GU092.SPR`**. The defect lived in the exact blind spot of the
instrument I used to declare its absence, and eight falsified hypotheses on top
of a blind instrument produced confidence instead of doubt. A negative result is
only as strong as the search's ability to have returned a positive — before
concluding "not present", state what the query would have missed. The old
"stop generating hypotheses and render the artifact" lesson was itself the
rationalization that closed this prematurely. See
[[feedback-instrument-before-environment]], [[mom-sprite-pipeline]],
[[mom-sprite-numbering-pinned]].

**Still true from the old entry:** `units.csv` needed an explicit
`art_cell_index` column (0..62) because the `cell_index` fallback was live and
duplicated (Zombies and Spearmen both 1) — that fix stands. The
`civ2_converted_graphics.csv` numbering disagreement remains latent and
harmless.
