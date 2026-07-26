---
name: feedback_harness_only
description: User wants file edits via harness tools only — do not execute shell commands to run scripts or build tools
metadata: 
  node_type: memory
  type: feedback
  originSessionId: db43a103-679c-4689-a7b1-d0a1a5514e74
---

Never directly edit generated output files (Units.txt, uniticon.txt, buildings.txt, etc.). Always edit the harness/generator source files (control plane), then RUN the regen yourself.

**Why:** The harness is the single source of truth. Direct edits to output files get overwritten on the next regen.

**Division of labor:** Claude runs the generator scripts (ctpedit.py patch units/all, verification scripts, etc.); user only tests in-game. User explicitly said "that's your job to run, I just test game."

**How to apply:** Edit harness source, then run `python ctpedit.py patch units` (or `patch all`) via Bash/PowerShell from `Scenarios\mom\tools\`. Verify output files after running.

2026-07-14 re-confirmed forcefully ("that is your fucking job") after Claude kept queueing `civ2_sprite_extractor.py` / `ctp2_generator.py` / `mom_audit.py` for the user to run. **The MEMORY.md index line had inverted this rule** ("never execute project scripts — tell user what to run") — index hooks must match the memory body. Claude runs: extractor, generator, audit, verification, launches. User runs: nothing but the game itself.
