---
name: mom-magic-verified-clean
description: "MoM magic+gold SLIC is ground-truth-verified clean; turn-10 crash guards already in the exe; \"magic didn't fire\" was upstream crashes, not broken magic"
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

2026-07-13: Full ground-truth (engine-source) verification of the MoM magic/gold system. Do NOT re-diagnose the magic SLIC as the cause of "no Guardian Spirit / gold regressed" — it is verified correct.

**Verified against H:\Games\civctp2\ctp2_code engine source:**
- Every SLIC builtin the magic uses exists and is called in shipped-correct form (matches base `tut2_func.slc`): `GetCityByIndex(player[p],i,c)`, `GetNeighbor(loc,j,out)`, `HasGood(loc)>=0`, `CityIsValid`, `CreateUnit(p,type,loc,1)` (engine Count 4-5, GetPlayer/GetInt/GetPos/GetInt).
- All DB symbols resolve (10 IMPROVE_, 5 UNIT_, 5 ADVANCE_ records present).
- `BeginTurn` event = `%P%i` → `player[0]` is the turn's player; human=player 1 (Life). Seating player N = civ N holds.
- M4 mana-node scan is exonerated (identical pattern to shipped tut2_func.slc). The old "tick aborts mid-execution" bisection was unnecessary — breadcrumbs removed, files back to committed baseline.

**Engine turn-10 Militia crash guards are ALREADY in the running exe** — do NOT re-apply or re-diagnose. `Player::GetCheapestMilitaryUnit` (Player.cpp:6740) returns -1 gracefully (Assert removed); `CityData::Militia` (CityData.cpp:11674) has `if(cheapUnit<0) return;`. exe mtime 07/11 20:06:27 is NEWER than both sources (20:05:xx) → compiled in. That's why it once reached turn 25.

**Self-prereq is the engine-sanctioned advance-disable** — Advances.cpp:498 `ResetCanResearch` checks `rec->GetIndex()==GetPrerequisitesIndex()` → `canResearch=FALSE`, flat/iterative, NO cycle risk. Used for USER_DEF_TECH_A (committed ce7bc3a). See [[mom-anarchy-science-regression]] for the reversion-by-baseline-reset pattern that keeps eating uncommitted fixes.

**Conclusion:** the only thing blocking observation of magic is the intermittent load crash (RETRY class, [[mom-intermittent-setup-crash]]) — the crash log's last line "Unit 55: City" is a buffered DPRINTF inside unitutil_Initialize, NOT the crash point. No gameplay log survives (game overwrites civ3log000.txt each launch), so all "didn't fire" reports are unlogged visual observations during runs that likely crashed early.
