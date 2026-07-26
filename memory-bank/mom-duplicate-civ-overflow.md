---
name: mom-duplicate-civ-overflow
description: "Duplicate \"Tribe of Life\" (>1 player on civ"
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**Symptom:** the Power/score graph shows the same tribe more than once (observed: 3×
"Life Tribe" out of 7 players) because MoM defines only 5 tribes (civilisation.txt
TRIBES_LIFE #1 .. TRIBES_CHAOS #5, + BARBARIAN) but the game ran 7 players.

**Root cause (engine bug):** `CivilisationPool::Create` (civilisationpool.cpp:114-140).
Its de-dup loop wraps the civ index back to 1 when it passes `numCivs`, so after all civs
are used `civ` is always `< numCivs` — the intended `if (civ >= numCivs)` FATAL "no more
civs" guard NEVER fires, and a DUPLICATE civ index is silently assigned (lands on a low
index, usually 1 = Life). Player count is never capped by civ count
(spnewgamescreen.cpp:600 `SetNPlayers(index+3)`).

**NOT a defeat hazard — corrects a plausible-but-wrong theory:** all defeat/victory/
elimination logic keys on the unique PLAYER index (`m_owner`), never civ name/index.
`Player::CheckPlayerDead` (Player.cpp:6916) uses only that player's own cities/units;
`GameOver`/`GameOverCheck` (6784/6795) loop by player index; no civ StringCompare in the
fate path. So two players sharing civ #1 do NOT share fate — one Life dying cannot
collaterally defeat the human Life. Duplicate civ = cosmetic (same name/flag) only.

**Fix (2026-07-11, engine):** cap players to distinct-civ count at both gameinit paths —
`nPlayers = min(nPlayers, g_theCivilisationDB->NumRecords()-1)` (gameinit.cpp ~1143 and
~1544; added `#include "CivilisationRecord.h"`). MoM now runs exactly 5 tribes and also
sheds the 7-on-one-map crowding. General correctness fix, only engages when players exceed
civs. Editing civilisation.txt alone would NOT fix it (the wraparound guard is still broken).

**Still open:** the early turn-5 DEFEAT (human alive with 2 cities, no logged game-over
trigger) is a SEPARATE issue — duplicate civ is not its cause. Needs the on-screen trigger
captured (message/turn at the instant it flips to DEFEAT). Related: [[mom-intermittent-setup-crash]].
