---
name: mom-slic-save-cache
description: "CTP2 serializes compiled SLIC + variable state INTO saved games; a loaded save ignores edited .slc files until /reloadslic. Test SLIC fixes with a NEW game, not a loaded save."
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

2026-07-13 (web-research + engine-source confirmed): The #1 reason a MoM SLIC fix "doesn't take effect" — **saved games cache compiled SLIC.**

**Engine mechanism** (`gs/utility/gameinit.cpp:1657`):
```
if (archive) {                          // LOADING A SAVE
    g_slicEngine = new SlicEngine(*archive);  // rebuilds SLIC FROM the save
    g_slicEngine->PostSerialize();
} else {                                // NEW GAME
    SlicEngine::Reload(g_slic_filename);      // compiles FRESH from .slc files
}
```
`GameFile.cpp:323` calls `g_slicEngine->Serialize(archive)` — it serializes `m_segmentHash` (compiled segments), `m_symTab` (variables), `m_constHash`, `m_disabledClasses` into the save.

**Consequence:** editing `.slc` files does NOTHING to an in-progress/loaded save. To pick up SLIC edits:
1. **Start a NEW game** (archive==NULL → recompiles current files), OR
2. After loading a save: open console with the **apostrophe key (')** and type **`/reloadslic`** (= `SlicEngine::Reload`) — once per save game.

Community-confirmed (Apolyton/codehappy thread 48135): "after installing a new version you still have to reloadslic."

**This retroactively explains the whole "magic didn't fire / gold regressed" saga:** testing via a save created while the SLIC was broken during FS-corruption recovery ([[mom-fs-corruption-recovery]]) ran that broken SLIC out of the save archive. The corrected files ([[mom-magic-verified-clean]]) were never consulted. ALWAYS test MoM SLIC changes from a NEW game as Tribe of Life, or `/reloadslic` first.
