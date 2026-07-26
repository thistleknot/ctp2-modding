---
name: ""
metadata: 
  node_type: memory
  originSessionId: c5fa2bd2-0b1c-4e75-a617-6e92217b1336
---

**Working build command** (PowerShell — note `$env:CDKDIR = ...` MUST be a separate
statement before the `&&` chain; `&&` cannot follow an assignment statement, only a command):

```powershell
$env:CDKDIR = "H:\Games\civctp2\bin"
& "H:\BuildTools\VC\Auxiliary\Build\vcvars32.bat" && & "H:\BuildTools\MSBuild\Current\Bin\MSBuild.exe" H:\Games\civctp2\ctp2_code\ctp\civctp.vcxproj /p:Configuration=Debug-SDL /p:Platform=Win32 /p:WindowsTargetPlatformVersion=10.0.26100.0 /p:PlatformToolset=v145 /m
```

**Three gotchas found in order, each a distinct failure until fixed:**

1. **`msbuild` bare command not found**, even inside the "Developer Command Prompt"
   vcvars32.bat prints — this is the standalone BuildTools install (not a full VS
   install), so `msbuild` is never added to PATH. Must call the full path:
   `H:\BuildTools\MSBuild\Current\Bin\MSBuild.exe` (resolves `find /h/BuildTools
   -iname MSBuild.exe`).
2. **MSB8020: toolset 'v141' cannot be found** — `civctp.vcxproj` is pinned to the
   VS2017 toolset, but only one MSVC version is installed
   (`H:\BuildTools\VC\Tools\MSVC\14.51.36231`, a `v143`-generation compiler). Override
   on the command line with `/p:PlatformToolset=<X>` — do NOT edit the vcxproj.
   **The exact override value is NOT `v143`** (also errors, not registered) — check
   `H:\BuildTools\MSBuild\Microsoft\VC\v180\Platforms\Win32\PlatformToolsets\` for what's
   actually there. Was `v145` on this machine 2026-07-18 — re-check if BuildTools is
   ever updated.
3. **MSB8066 exit 9009 on the flex/bison custom-build step** (`DBLexer.l`, `slic.l/.y`,
   `sliccmd.l/.y`, `ldl.l/.y`) — the vcxproj invokes `$(CDKDIR)\flex` /
   `$(CDKDIR)\byacc`; `CDKDIR` is unset in this environment, so the command becomes a
   bare `\flex` (leading backslash, no dir) → "not recognized," exit 9009. The tools
   exist at `H:\Games\civctp2\bin\flex.exe` / `byacc.exe` — set
   `$env:CDKDIR = "H:\Games\civctp2\bin"` before invoking MSBuild (env vars set on the
   parent PowerShell process ARE inherited by MSBuild.exe launched via `&`, even though
   vcvars32.bat's OWN internal env changes are lost when that separate `.bat` subprocess
   exits — the two are independent facts, don't conflate them).

Confirmed working build output: `H:\Games\civctp2\ctp2_code\ctp\ctp2-dbg.exe` (fresh
timestamp after build). `run-ctp2-dbg-crashcapture.ps1` stages this into the install dir
automatically on every launch — no manual copy needed.

**4th gotcha (2026-07-18): `SlicEngine.obj : fatal error LNK1000: Internal error during
IncrCalcPtrs`.** MSVC's incremental linker (`/INCREMENTAL`, the default here) can
corrupt its own state when a diff SHRINKS a function (e.g. reverting/removing code) —
not a real code error. Fix: delete the stale `.ilk`
(`H:\Games\civctp2\ctp2_code\ctp\ctp2\Debug-SDL\ctp2-dbg.ilk`) and rebuild; MSBuild
regenerates it cleanly. Don't waste time debugging the "error" itself — it's linker
state corruption, not a compile/link defect in the changed code.

Related: [[feedback-always-launch-game]] (build-authorization default),
[[mom-engine-build-toolchain]] (original BuildTools location note, less detailed than this).
