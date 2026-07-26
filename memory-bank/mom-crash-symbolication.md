---
name: mom-crash-symbolication
description: "In-game crash traces symbolize via <exedir>\\ctp2-dbg.map — a stale deployed map makes every symbol name fiction; verify with WER Exception Offset, re-symbolize from the build-matched map"
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

CTP2's crash handler resolves stack addresses against `<exedir>\ctp2-dbg.map`
(`DebugCallStack_Open`, debugcallstack.cpp). The launch script used to stage exe+pdb+dlls
but NOT the map, so deployed-map drift made **every symbol name in every crash trace
fiction while the addresses stayed real**. This mis-drove at least two diagnoses
(b8161ec "negative settler need"; the MakeFranchise_RegardEvent theory) before being
caught on 2026-07-09.

**Why:** the walker is a sound EBP-chain walk (frame[0] = exact faulting Eip); only the
name lookup depends on the map file. WER's `Exception Offset` (RVA) + image base
0x00400000 must equal frame[0] — if yes, addresses are trustworthy and any name weirdness
means a stale map.

**How to apply:**
- `run-ctp2-dbg-crashcapture.ps1` now stages `ctp2-dbg.map` in lockstep (Get-OverlaySources).
- To re-symbolize an old trace: parse "Publics by Value" from the build-matched map
  (`H:\Games\civctp2\ctp2_code\ctp\ctp2-dbg.map`), take greatest symbol addr <= frame addr.
- Distrust any crash-trace symbol name whose deployed map timestamp != exe timestamp.
- The 2026-07-09 "turn-0 AI crash" is really `aui_Blitter::Blt16To16` under the
  InitProgressWindow redraw. Cause OPEN (intermittent). FALSIFIED detour: the loose
  120x120 desc=0x21 TGAs (uptg20e* etc.) are NOT impostors — they are sha1-identical
  extractions of the archive's .rim entries by `patch_ctp2_images.py --base-only`,
  REQUIRED loose (archive stores .rim not .tga; launch preflight blocks without them);
  desc=0x21 is that pipeline's intended form, not a corruption signal. Instruments:
  DrawImages skips+names bad surfaces; Blt16To16 refuses physical-OOB rects with full
  geometry DPRINTF; validator surfaces 9a (baseline-diffed dangling ldl refs) and
  9b (truncated/short-payload loose TGAs). Related: [[mom-fugly-double-load]].
