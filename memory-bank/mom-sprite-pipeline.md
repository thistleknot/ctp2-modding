---
name: mom-sprite-pipeline
description: "Why MoM unit sprites render invisible/empty — TRUE cause: anim transparency 0 (fixed in pack_anim); plus mini-frames, keying, cow-clobber, and engine load order"
metadata: 
  node_type: memory
  type: project
  originSessionId: 82bcfca6-1cd2-40d7-8709-28a3c1dccf26
---

MoM unit sprites (`ctp2_data/.../graphics/sprites/GU###.SPR`) render **invisible on the map** (unit
banner shows, body does not; portrait is a separate system and works).

**TRUE ROOT CAUSE (confirmed 2026-07-03, decode + engine source): anim transparency 0.**
Every SPR anim block carries per-frame u16 transparencies; the engine uses them as blend alpha
(`alpha = value << 3`): `Action::GetTransparency()` → `UnitActor.cpp:470` → `pixelutils_Blend16`
returns pure background at alpha 0. `Actor.h: NO_TRANSPARENCY = 15` (opaque); ALL stock sprites
carry 15s. makespr.py's `pack_anim` zero-padded omitted transparencies → every makespr.py-built
unit was drawn at 0% opacity at every zoom — pixels perfect, structure valid, unit invisible.
Fixed in `pack_anim`: pad with 15 + warn on explicit all-zero list. NOTE: `ANIM_TRANSPARENCIES 0`
in GU scripts is a FLAG ("no explicit list"), not a value — the script templates were never wrong.
Verify any SPR without launching the game by decoding the MOVE-anim transparencies (must be 15s).
Spec: `Scenarios/mom/specs/spr-anim-transparency.md`.

**SECONDARY root cause (earlier fix, still real): blank mini-frames.** CTP2 renders the half-size *mini* frame at
normal map zoom and the full frame only when fully zoomed in. `makespr.py` stubbed every mini as a
blank 74-byte frame (`_encode_blank_spr_frame`), while stock sprites carry ~850-byte minis. So every
makespr-built unit was invisible at default zoom even though its full frame was intact. Proven by
comparing GU104 (peasant, mini=74) vs stock GU01/GU02 (mini≈850) and reading the engine's
`SpriteFile::ReadFacedSpriteDataBasic` in `H:\Games\civctp2\ctp2_code\gfx\spritesys\spritefile.cpp`.
Fix (done): makespr.py now downscales each frame to `w/2×h/2` and encodes a real mini
(`_downscale_half`); the RLE scanline encoder itself is still a faithful port of `spriteutils.cpp` —
do NOT edit that. (Version note: makespr writes VERSION0=0x00010003 v13; base sprites are
VERSION1=0x00020000 v20 — both are engine-supported, so version was NOT the bug.)

**ALSO REAL (art quality, not invisibility): keying.** `build_sprites.py._convert_tga_to_tifs`
keyed **every** pure-black pixel to alpha 0; the opaque black-background TGAs with dark fantasy art
(Archangel ~88% black) lost foreground too. Fixed with **border flood-fill** keying, nudge interior
black to `(8,8,8)`, empty-SPR guard, and optional `LEFT_FACING` flip. `_facing_images()` casts one
source across 5 facings — the 1:n→n:n unroll point.

To apply: rebuild with `python Scenarios\mom\tools\build_sprites.py --force` (reruns makespr.py), then
verify GU104 mini sizes are ~hundreds of bytes (not 74) and units are visible at normal zoom.

**TERTIARY (2026-07-03): WRONG art, correct wiring — SPR content clobbered.** Peasants (GU104)
rendered as the makespr tutorial **Cow**: an errant manual makespr run at repo root (litter:
loose `GU104.TXT`, `104/` TIFs, `MSVCRTD.DLL`) built the GU01 Cow example and overwrote
`ctp2_data/.../GU104.SPR`. Wiring (Units.txt → newsprite.txt → SPR path) was 100% correct — only
the binary payload was wrong. Diagnosis: decode SPR frame 0 and *look at it* (decoder at
scratchpad `decode_spr.py` pattern; a build_sprites.py SPR is 1 static frame — 11 animated frames
+ shadow + extra actions = tutorial Cow signature). Fix: `tools/rebuild_peasant_spr.py`, which now
also removes tiny disconnected specks (`_remove_islands`, <20 px, 8-connectivity) that colour
keying can't catch (bright star-field stars). Run with `PYTHONIOENCODING=utf-8` (cp1252 console
chokes on the script's `→`).

**ENGINE SPRITE-FILE LOADING ORDER (verified in source, `SpriteGroupList::LoadSprite`,
`H:\Games\civctp2\ctp2_code\gfx\spritesys\SpriteGroupList.cpp:100`):** the engine builds the
filename as `sprintf("GU%.3d.SPR", index)` (3-digit zero-padded) and tries that FIRST; only if
`FindFile` misses does it fall back to `sprintf("GU%.2d.SPR", index)` (2-digit). So for index 91 it
loads `GU091.SPR` if present, else `GU91.SPR`. Consequence: `build_sprites.py` writes 2-digit
`GU{num:02d}.SPR` (→ `GU91.SPR`), so any pre-existing 3-digit `GU091.SPR` **silently shadows** the
MoM static build. This is the loading mechanic behind "correct build, wrong art on map." A
`build_sprites.py` MoM sprite is 1-frame MOVE-only; a shadowing base/AE sprite is multi-frame
(MOVE+ATTACK+IDLE+VICTORY, ~500KB) — decode frame 0 to tell them apart. (Goods=`GX%.2d`,
cities=`GC%.3d`, effects=`GG%.3d`.)

**GOLDEN PARITY (2026-07-03): makespr.py is byte-identical to makespr.exe** on Kull's Cradle 5
Legion fixture (`H:\Games\ctp2\16-makespr\16\` = inputs + Gu16.txt + exe-built GU16.SPR; full kit
with MAKESPR.EXE at `H:\Games\ctp2\MakeSprite\`, from http://www.ctp2.info/download/MakeSprite.zip).
The golden diff exposed and fixed: green-instead-of-magenta shadow stamp (shadows encoded as opaque
copy runs), missing ceil alpha-premultiply at load, wrong mini pipeline (must quarter pristine image
ceil-averaging all 4 RGBA components incl. alpha, nearest-sample shadow separately, then merge),
facing-4 filenames for 1-facing actions (IDLE/VICTORY), unparsed ATTACK_IS_DIRECTIONAL/IS_DEATH →
trailing hasDirectional/hasDeath, hardcoded shield points. Rerun the golden test after any
makespr.py change. Full detail: project skill `.claude/skills/ctp2-sprite-creation/SKILL.md` §1b
and `Scenarios/mom/lessons_learned.md`. MoM art lead for placeholder units (zombies/spearmen/
swordsmen): Civ3 CoMM3 mod, civfanatics thread 619720 (full HoMM3 creature graphics).

Sprites (`newsprite.txt` → `GU###.SPR`) and still-pictures (`uniticon.txt` → `pictures/*.tga`) are
independent systems. Full process captured in the `ctp2-sprite-creation` skill. Diagnose with
`tools/diagnose_spr.py` (H1 blank source vs H2 keying erased art). See [[mom-canonical-toolchain]],
[[feedback_harness_only]].
