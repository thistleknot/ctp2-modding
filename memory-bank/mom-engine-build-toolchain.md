---
name: mom-engine-build-toolchain
description: How to build the CTP2 engine — standalone MSVC BuildTools at H:\BuildTools (NOT a registered VS install; vswhere/Program Files searches miss it)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

The CTP2 engine (`H:\Games\civctp2\ctp2_code`) is built with a **standalone MSVC
Build Tools at `H:\BuildTools`** — NOT a registered Visual Studio install, so
`vswhere` returns nothing and searches of `C:\Program Files*` find no
`cl.exe`/`Microsoft.Cpp.Default.props`. The VS 18 Insiders on this box lacks the
C++ workload and CANNOT build it (MSBuild errors on `VCTargetsPath`).

**Toolchain (from the 13:19 build's `ctp2.tlog/CL.read.1.tlog`):**
- Compiler: `H:\BuildTools\VC\Tools\MSVC\14.51.36231\bin\HostX86\x86\cl.exe`
- MSBuild:  `H:\BuildTools\MSBuild\Current\Bin\MSBuild.exe` (VC targets `MSBuild\Microsoft\VC\v180\`)
- Windows SDK: `D:\SDKs\Include\10.0.26100.0\...` (set by vcvars)
- vcvars: `H:\BuildTools\VC\Auxiliary\Build\vcvars32.bat` (x86 native)
- Project `ctp/civctp.vcxproj` declares `PlatformToolset v141` and
  `WindowsTargetPlatformVersion 10.0.19041.0`, but NEITHER is installed — only toolset
  **14.51 (v145)** and SDK **10.0.26100.0** exist. So the vcxproj as-read does NOT build;
  you MUST override both on the command line (the 13:19 build's PDB was `VC145.pdb`,
  confirming it used v145). Errors if you don't: MSB8036 (SDK) then MSB8020 (toolset).

- flex/byacc: the `.l`/`.y` custom-build step runs `$(CDKDIR)\flex` / `$(CDKDIR)\byacc`.
  `CDKDIR` must be set to **`H:\Games\civctp2\bin`** (where flex.exe/byacc.exe live) or the
  step fails with MSB8066 / code 9009 (`'\flex' is not recognized`). Generated parsers
  (`gs/slic/lex.yy.c`, `y.tab.c`, etc.) are usually already current, but MSBuild may still
  invoke the step, so always set CDKDIR.

**Build command (replicates the working build — all three REQUIRED: CDKDIR + 2 overrides):**
```
cmd /c '"H:\BuildTools\VC\Auxiliary\Build\vcvars32.bat" && set "CDKDIR=H:\Games\civctp2\bin" && "H:\BuildTools\MSBuild\Current\Bin\MSBuild.exe" "H:\Games\civctp2\ctp2_code\ctp\civctp.vcxproj" /p:Configuration=Debug-SDL /p:Platform=Win32 /p:LinkIncremental=false /p:WindowsTargetPlatformVersion=10.0.26100.0 /p:PlatformToolset=v145 /m'
```
Error ladder if a piece is missing: MSB8036 (SDK) → MSB8020 (toolset v141) → MSB8066/9009 (CDKDIR flex/byacc).
Delete `H:\Games\civctp2\ctp2_code\ctp\**\*.ilk` first (the LNK1000 lesson). Output
is `H:\Games\civctp2\ctp2_code\ctp\ctp2-dbg.exe`; the overlay launch script
(`run-ctp2-dbg-crashcapture.ps1`) stages THAT exe into the install dir per run, so a
rebuild there reaches the game. Config is **Debug-SDL | Win32** (x86). Only the changed
`.cpp` recompiles (PCH `c3.h`), then relink — fast, not a full rebuild.

**How to apply:** to build the engine from the CLI, use the command above (correcting
[[feedback_harness_only]]'s "tell user to build" for the engine — the toolchain IS
reachable, just at H:\BuildTools). Decode tlogs with `iconv -f UTF-16LE`. Verify the
built exe mtime is newer than the edited source before relaunching ([[mom-crash-symbolication]]
pattern) — the overlay stages a stale exe otherwise.
