---
name: mom-fs-corruption-recovery
description: "2026-07-11 H: drive FS corruption during MoM session — nothing meaningful lost (all committed); recovery bundle on C: scratchpad; needs chkdsk H: /f first"
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

On 2026-07-11 the H: volume corrupted mid-session: Windows reported "The file or directory
is corrupted and unreadable" on `H:\...\Scenarios\mom\scen0000\default`, and `.git/objects`
in BOTH the scenario repo and `H:\Games\civctp2\ctp2_code` returned `Function not implemented`
(`git show` = 0 bytes). Cause: repeated hard `0xC0000005` game crashes left NTFS dirty
(`chkdsk` flagged `Scan Needed`). NOT a delete — only Edit was used on those files.

**Loss = essentially nothing.** All substantial work is committed (fuglies fix `5a1c1c2`,
hero-gating `73e7a6f`, advance prune `bd4b99e`, magic M2/M3/M4, sprite wiring `af39dc5`,
banner sprites `f3ecf9e`, tech-cost `8ce386b`; engine banner `16af7c743`). Uncommitted deltas
(git does NOT have these): engine Militia crash fix (Player.cpp assert removal + CityData
Militia `if(cheapUnit<0)return;`, already in the 20:06 ctp2-dbg.exe), the SPEARMEN
`EnableAdvance ADVANCE_WARRIOR_CODE` removal, and the in-progress magic sphere-guard
(`if (p < 1) return;` at top of MomMagicPoolTick — the turn-10 crash was magic running for
player 0; isolation with magic OFF reached turn 28 clean).

**Recovery bundle (C:, healthy):** `<scratchpad>/RECOVERY_2026-07-11.md` (full state, commit
list, exact re-apply steps, build cmd) and `mom_magic.RECOVERED.slc` (reconstructed M1-M4 +
sphere-guard fix). Scratchpad =
`C:\Users\user\AppData\Local\Temp\claude\H--Program-Files-x86--Activision-Call-To-Power-2\77eb8577-a451-4ba1-84c7-af8b7cf3cf0e\scratchpad`.

**Recovery order:** (1) `chkdsk H: /f` (H: is not the system drive); (2)
`git checkout HEAD -- Scenarios/mom/scen0000/{default,english}/gamedata/` to restore all
committed files; (3) re-apply the 3 uncommitted deltas above; (4) re-enable magic
(scenario.slc `#include "mom_magic.slc"`), drop the in-game popup per user, add a magic README.
**RESOLVED 2026-07-12:** user ran `chkdsk H: /f`; `git checkout HEAD -- Scenarios/mom/scen0000/`
restored all committed files except 2 corrupted git objects (mom_magic.slc -> restored from
the C: reconstruction WITH the sphere-guard fix; WAW_Great_Library.txt -> git-rm, orphan).
Re-applied the deltas; game confirmed working (no fuglies, units correct, no crash turn 12).
Commits a6a47cc/b62bed5/b09c857/60f326f.

**Two gap-fill (`cp -rn` from the `- Copy` pristine backup) gotchas learned:**
1. It added base 3-digit `GUxxx.SPR` that SHADOW the MoM 2-digit unit builds (engine tries
   3-digit first) -> wrong unit sprites. Fix: rm the 3-digit shadow where the 2-digit is a
   small MoM build ([[mom-sprite-pipeline]]).
2. Base `ctp2_data` `.ldl` (controlpanel.ldl) carried CRLF -> LDL parser breaks -> banner
   FUGLIES. This is a FOURTH fugly surface beyond [[mom-fugly-double-load]]'s three (the
   `.gitattributes` LF rule now covers ctp2_data uidata too). Grep byte-accurate (`open(...,'rb').count(b'\r')`), never `grep -c $'\r'` (counts lines, lies).

Do NOT write to H: until chkdsk clears it — writing to a failing volume turns "recoverable"
into "lost". See [[mom-intermittent-setup-crash]] (the 0xC0000005 class) and
[[mom-engine-build-toolchain]].
