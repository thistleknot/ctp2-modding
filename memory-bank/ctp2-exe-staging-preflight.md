---
name: ctp2-exe-staging-preflight
description: build.bat only builds Final-SDL (ctp2.exe); ctp2-dbg.exe is stale and gets re-staged over manual copies — ALWAYS preflight a marker string in the exe that will actually launch
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-24T22:23:34.333Z
---

**The five-day "SLIC bug" (2026-07-24) was a stale binary, not SLIC.**

- `build.bat` builds ONLY `Configuration=Final-SDL` → produces `ctp2.exe`. It
  **never** refreshes `ctp2-dbg.exe`, which is the `Debug-SDL` artifact.
- `uiwalk.py`'s `EXE_CANDIDATES` is **dead code**. Launch delegates to
  `ctp2_program/ctp/run-ctp2-dbg-crashcapture.ps1` → `Resolve-LaunchSource`,
  whose default order is `ctp2-dbg.exe, ctp2-log.exe, ctp2.exe`.
- That script **re-stages the chosen exe from `H:\Games\civctp2\ctp2_code\ctp`
  on every launch and restores backups on exit** — silently reverting any manual
  `cp ctp2.exe ctp2-dbg.exe`.

Net effect: every headless run executed a Jul-22 binary containing none of the
changes under test, and the crashes seen were the old build's known bugs.

**Fix in place:** `uiwalk.py::preflight_exe()` resolves the exe that will really
launch and ABORTS unless a marker string is in it (`--marker MagicMenu`, `none`
to skip); `-PreferRelease` is threaded into the launcher so `ctp2.exe` wins.
`--use-debug-exe` opts back into Debug-SDL (which also has a documented 1 MB
stack — see [[mom-ai-endturn-stackoverflow]]).

To rebuild the debug exe deliberately: same MSBuild line as `build.bat` but
`/p:Configuration=Debug-SDL /p:Platform=Win32`.

**RULE: never trust "I rebuilt it." Assert a marker string inside the launched
binary before believing any test result.** See [[ctp2-headless-checkpoint-method]]
and the full write-up at the top of `Scenarios/mom/lessons_learned.md`.
