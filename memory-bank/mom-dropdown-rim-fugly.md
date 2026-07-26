---
name: mom-dropdown-rim-fugly
description: "RESOLVED 2026-07-15 — 5th fugly cause: zfs-RIM-backed surfaces (uppd02* dropdown chrome) AV on every blit, SEH guard skips the paint, stale setup-screen slice shows (tan strip + beaded 'rope'). Fix = extract RIMs from pic555.zfs to loose 16-bit TGAs (upfg01 conventions). Any zfs-only texture is one loose-TGA extraction from a fix."
metadata:
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**RESOLVED 2026-07-15, user-confirmed.** The City-tab dropdown fugly (city-name + MAYOR pulldowns showing tan parchment with a beaded rope line instead of beige/gold chrome) = **5th fugly cause**: the 13 `uppd02*` chrome images exist ONLY inside pic555/565.zfs as RIM records; `LoadRIM` wraps the RIM bytes as the surface, and blitting those surfaces **access-violates every draw** (`DrawImages: blit FAILED (err=4) for image 'uppd02aX.tga'`). The f9a529266 SEH guard contains the AV → paint skipped → stale surface memory shows (a coherent slice of the setup screen, NOT rainbow noise).

**Fix (data-only, no engine rebuild):** extract from **pic555.zfs** (555=ARGB1555=16-bit TGA payload, lossless), row-flip (RIM top-down → TGA bottom-up), write loose TGAs to `ctp2_data/default/graphics/pictures/` with upfg01 conventions: type 2, 16bpp, desc=0x01, `TRUEVISION-XFILE.\0` footer. Loose TGA shadows zfs RIM.

**Key rules:**
- Coherent-but-wrong texture = paint never happened; rainbow noise = unpainted heap. Both "surface never painted".
- "zfs caps → not a data fix" (2026-07-11) was WRONG: loose OVERRIDE bypasses the archive.
- When a commit message cites "session logs" that were rotated, **grep the conversation transcript jsonl** — it preserved the exact failing log line here.
- ZFS3/RIM format documented in lessons_learned (2026-07-15 entry) for future extractions.

Related: [[mom-citypanel-fugly-engine]] (4 earlier causes), [[mom-fugly-double-load]] (compound playbook), [[mom-wiki]].
