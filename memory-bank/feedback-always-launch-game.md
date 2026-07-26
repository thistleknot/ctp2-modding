---
name: feedback-always-launch-game
description: "User wants Claude to always launch the CTP2 game itself (via the crash-capture overlay) — never hand back a \"run this\" instruction for launching"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

The user wants the game **launched for them automatically**, every time a test run is
needed — do not tell them to run the launcher or wait for them to start it.

**Why:** stated directly ("start the game for me always"); the interactive test loop is
faster when Claude drives the launch and then reads the resulting log.

**How to apply:** launch in the background with
`powershell.exe -ExecutionPolicy Bypass -File "ctp2_program/ctp/run-ctp2-dbg-crashcapture.ps1"`
(run_in_background) whenever a launch is warranted, then read the fresh
`ctp2_program/ctp/logs/civ3log*.txt` after the task completes.

**GOTCHA (2026-07-13):** the install path `H:\Program Files(x86)\...` has a SPACE.
When launching via `Start-Process pwsh -ArgumentList ...`, an array element for `-File`
gets split at the space (`-File` receives `H:\Program`) → pwsh prints usage and NOTHING
launches (the game never starts, log mtime never changes — do NOT misread this as a load
crash). Pass the args as ONE pre-quoted string instead:
`$arg = '-NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $scriptPath; Start-Process pwsh -ArgumentList $arg`.
The script itself blocks on `WaitForExit()` and prints the civ3log tail + crash.txt on exit,
so redirect its stdout to a file to capture that. Confirm success by polling
`Get-Process ctp2-dbg` (stable ~180MB, 27 threads = reached menu). This is the ONE project
script exempt from the general [[feedback_harness_only]] "never run project scripts" rule —
launching is explicitly, durably authorized. See [[mom-crash-symbolication]] (overlay stages
the dbg exe/map).

**Building the engine — default is still "hand it to the user," UPDATED 2026-07-18:** the
user explicitly said "build it for me" when a headless-playtest engine patch needed
compiling, overriding the prior default for that occasion. Default behavior is unchanged
(hand the build command to the user) — but Claude MAY run the build directly when the user
says so explicitly in the moment, same as any other live instruction overriding a standing
default. See [[mom-engine-build-cdkdir-toolset]] for the working command once these gotchas
are fixed (MSBuild.exe needs its FULL path — `msbuild` alone is not on PATH even after
vcvars32.bat in this standalone BuildTools install; PlatformToolset must be overridden to
whatever's actually registered under `MSBuild\Microsoft\VC\v180\Platforms\Win32\PlatformToolsets\`
— was `v145` here, NOT the vcxproj's pinned `v141`; `CDKDIR` env var must be set to
`H:\Games\civctp2\bin` for the flex/byacc custom-build steps, or they fail with exit 9009).
