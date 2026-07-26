---
name: mom-citypanel-fugly-engine
description: "RESOLVED — city-panel name-banner fugly WAS data after all - upfg03/04/05/06 needed desc=1 + TRUEVISION footer + row-flip (same treatment as upfg01). User confirmed fixed. Earlier \"engine paint-ordering, not data\" conclusion was WRONG."
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**RESOLVED 2026-07-13.** The city-control-panel name-banner black boxes ("fuglies") were fixed by converting `ctp2_data/default/graphics/pictures/upfg03.tga, upfg04.tga, upfg05.tga, upfg06.tga` to the exact format of the working `upfg01.tga`: **desc byte 0x01 + 26-byte TRUEVISION-XFILE footer + vertically flipped rows** (they were desc=0x21 top-origin, no footer). User confirmed: "no crash + no fuglies". Fix survives restarts.

**Self-correction (important):** an earlier session pass concluded "engine paint-ordering bug, not data" because (a) `targautils.cpp Load_TGA_File_Simple` ignores desc/footer, and (b) blit instruments logged 0. That conclusion was **refuted empirically** — the data fix held across multiple restarts. Lesson: the control-panel banner images evidently load through a path that DOES honor orientation/format (or the flip itself was the operative fix); trust the in-game outcome over a single-loader source read.

**Gotcha that nearly reintroduced it:** during a later investigation these 4 files were restored to their broken backups "to test" and left on disk — a restart would have brought the fugly back. Re-applied. Rule: after any diagnostic restore, RE-VERIFY the fix state on disk before moving on ([[feedback-surgical-changes]]).

**Family rule:** upfg01/03/04/05/06 (CityControlPanel banner family, controlpanel.ldl:550-556 + 61) = desc=1 + footer. But `uptg20e/uptg20e2` (tiling patterns) and loose advance icons = desc=0x21/0x00 respectively — desc requirements are PER TEXTURE FAMILY (lessons_learned:462). Never blanket-apply.

Related: [[mom-fugly-double-load]] (the 3-cause compound playbook), [[mom-ai-endturn-stackoverflow]] (the crash that was entangled with this).
