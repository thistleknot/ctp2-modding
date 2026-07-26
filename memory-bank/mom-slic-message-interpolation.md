---
name: mom-slic-message-interpolation
description: "MoM SLIC popups with dynamic numbers silently drop if they use {Arr[Idx]} string interpolation — base CTP2 injects numbers via messagebox-body Text()/AddText(), not string-DB brace substitution"
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

M1 magic-power popup (`Message(g.player,'MomMagicPower')`) compiled cleanly and
the bytecode fired (`argid MomMagicPower; call _Message` present in slicdbg.txt),
but NO popup appeared in-game.

**Root cause:** the string used array-indexed interpolation —
`"Magic Power: {MomMagicCur[MomMagicMsgP]} / ..."` in scen_str.txt. That
`{Arr[Idx]}` form is the momjr/Cradle *unverified* string-based API kind (see
[[reference_momjr_source]]). It is the ONLY non-static message in the mod. Every
proven-working MoM popup (MomBless*, [[mom-gl-dbname-crash]] era) is **static text
with no interpolation**. The CTP2 message renderer can't resolve
`{Array[Global]}` and silently drops the whole message.

**Base-verified mechanism for dynamic numbers:** stock CTP2 does NOT do plain
`{var}` numeric substitution in the string DB. Dynamic values come through a
**messagebox body block** using builtins — `messagebox 'ID' { Text(ID_...) ... }`
(see base `ctp2_data/default/gamedata/test.slc`). The number is injected by the
message-definition body, not by brace-substituting a SLIC array into a flat string.

**Why:** confirms the momjr SLIC forms are the UNVERIFIED string kind; use
base-verified message-body builtins for any dynamic-number popup.

**RESOLVED — the base-verified form is `{scalar}`.** AlexanderTheGreat (a shipping
scenario) interpolates plain SLIC scalar globals by name: `{cityScore}`, `{civScore}`,
`{barbNum}`, `{totalScore}` (all numbers), plus `{obj[lit].member}` (`{city[0].name}`,
`{player[0].civ_name_plural}`). The renderer resolves a plain `int_t` global name and an
engine object.member path — but NOT an array indexed by a global. `%d`/`%s` in stock
strings are `str_code_*`/`*_FORMAT` C++ sprintf formats, not SLIC-reachable.

**How to apply (all magic messages M1–M5):** to show a computed number, copy it into a
plain `int_t` DISPLAY SCALAR immediately before the `Message`, and interpolate `{thatScalar}`.
Never `{Arr[Idx]}`. M1 popup fixed this way: `MomMagicCurDisp/MaxDisp/GenDisp` set in the
BeginTurn handler, string `"Magic Power: {MomMagicCurDisp} / {MomMagicMaxDisp}  (+{MomMagicGenDisp} per turn)"`.
test_mom_slic.py now asserts the scalar form + a regression guard against `{Arr[Idx]}`.
Spec (slic-magic-system.md :ManaVerbs:) updated to forbid array-indexed interpolation.
M2 committed 765d5e9; popup fix staged, awaiting in-game confirmation.
