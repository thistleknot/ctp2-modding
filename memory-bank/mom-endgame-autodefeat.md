---
name: mom-endgame-autodefeat
description: "Deterministic DEFEAT at ~turn 12 / 3750BC (human alive, 2 cities, no log trigger) = wonder-only EndGameObject + GaiaController::CanStartCountdown ignoring the wonder → AI auto-wins science victory; fixed by gating the countdown on holding endgame wonders"
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**Symptom:** every game, the human is shown the DEFEAT score window at a fixed early
turn (~turn 12, year 3750BC) while still ALIVE (2 cities intact). civ3log has NO player
death, NO victory, NO game-over line. NOT a crash. Cap-to-5-players did NOT fix it, and
it is NOT the duplicate-civ issue (that's cosmetic; defeat is player-indexed).

**Root cause (engine + data interaction):** MoM's `EndGameObjects.txt` defines
`ENDGAME_MOM_MASTERY { Wonder WONDER_RUNE_OF_RULERSHIP; TurnsToActivate 10 }` — a
WONDER-only victory. But `GaiaController::InitializeStatics` (gaiacontroller.cpp:107-151)
resolves endgame requirements only by the HARD-CODED names ENDGAME_PROCESSING_TOWER /
_POWER_SATELLITE / _GAIA_COMPUTER. MoM's object matches none, so tower/mainframe/satellite
required-counts are all 0, and `CanStartCountdown()` (gaiacontroller.cpp:830-845) — which
checked only those — returned TRUE for EVERY player from turn 1, never checking the wonder.
The AI auto-starts the countdown (ctpai.cpp:641-644); TotalCountdownTurns = TurnsToActivate
= 10; ~10 rounds later `Player::EndTurn` (Player.cpp:2531-2534) fires
`GameOver(GAME_OVER_WON_SCIENCE)` for that AI → `Player::GameOver` (6831-6847) flags all
others `GAME_OVER_LOST_SCIENCE` → the DEFEAT window (6900-6905). That LOST_SCIENCE path
(6871-6876) does NOT call StartDeath — so the human keeps cities and nothing logs.

**Fix (2026-07-11, engine):** added a wonder gate to `CanStartCountdown()` — count the
endgame wonders (popcount of the `sm_endgameWonders` bitmask built in InitializeStatics)
and `return false` if `NumWondersBuilt() < wondersRequired`. Now a player must actually
HOLD the Rune of Rulership before the countdown starts, so MoM's intended mastery victory
works (build Rune → win 10 turns later) and no AI can auto-defeat everyone. No-op for
stock science victory (0 endgame wonders).

**Diagnosis lesson:** a DEFEAT with the human alive + no log trigger = the
LOST_SCIENCE/LOST_DIPLOMACY/LOST_OUT_OF_TIME path (no StartDeath, no log). Look at the
GaiaController endgame countdown, not elimination. Related: [[mom-duplicate-civ-overflow]]
(the cosmetic red herring), [[mom-intermittent-setup-crash]].
