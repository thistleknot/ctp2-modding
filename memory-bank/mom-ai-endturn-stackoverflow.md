---
name: mom-ai-endturn-stackoverflow
description: "ROOT CAUSE = 1 MB stack. The debug exe ships a 1 MB main-thread stack; deep call chains (DB init at load, AI goal-scheduler at turn) intermittently blow it -> 'Stack Overflow' at variable points. Fix = enlarge stack (editbin /STACK no-rebuild, or StackReserveSize in vcxproj). NOT magic/SLIC/research."
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**ROOT CAUSE (2026-07-13): the debug exe has only a 1.00 MB stack reserve (linker default).** Debug builds have far fatter frames than release; CTP2's deep call chains blow 1 MB. This unifies TWO crashes long mis-filed as separate/intermittent:
- the "intermittent load crash" (log ends at buffered "Unit 55: City", then `Stack Overflow`) = deep DB-init call chain.
- the "AI turn stack overflow" (Turn N, Player P, via CtpAi PROCESS MATCHES -> Director::AddEndTurn) = deep AI goal-scheduler/event chain.
Both throw the SAME `civ3_main.cpp@1186: Exception: 'Stack Overflow'`. Variable crash location + intermittent = marginal stack DEPTH, not a single infinite-recursion bug (that would be deterministic at one spot). A prior run reached turn 25 = it sometimes squeaks under 1 MB.

**FIX (no source-logic change, cannot reintroduce fuglies):**
- Durable: added `<StackReserveSize>8388608</StackReserveSize>` (8 MB) to the Win32 `<Link>` blocks in `H:\Games\civctp2\ctp2_code\ctp\civctp.vcxproj` -> every future Debug-SDL build bakes it in. Needs one rebuild.
- Immediate (no rebuild): `editbin /STACK:8388608,65536` on the SOURCE exe `H:\Games\civctp2\ctp2_code\ctp\ctp2-dbg.exe` (the one run-ctp2-dbg-crashcapture.ps1 overlays over the install). Claude is BLOCKED by the auto-mode classifier from patching the engine binary -> hand this command to the user. editbin at `H:\BuildTools\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x86\editbin.exe` (add the Hostx64\x64 dir to PATH for its DLLs).
- exe is NOT LARGE_ADDRESS_AWARE (2 GB space); 8 MB reserve is safe across all ~25 threads.

If it STILL overflows at 8 MB -> only THEN suspect genuine runaway recursion and instrument `GameEventManager::Process` (GameEventManager.cpp:399/441) depth. Until then, treat as stack-size.

**Signature (civ3log, no stack frames — stack exhausted so the handler can't symbolicate):**
```
CtpAi PROCESS MATCHES xN (Player P) -> CtpAi.cpp@679 AI End turn, P
GameEventManager@966 EndTurnRequest, K pending actions, not doing it yet
ArmyData ORDER_MOVE -> Director.cpp@2715 AddEndTurn curPlayer=P -> Stack Overflow
```

NOT caused by magic/gold SLIC ([[mom-magic-verified-clean]]), the USER_DEF_TECH self-prereq, or the fugly. Related: [[mom-citypanel-fugly-engine]] (separate open engine bug — do NOT bundle a blind fugly fix into the stack rebuild; it risks reintroducing the blit crash), [[mom-crash-symbolication]].
