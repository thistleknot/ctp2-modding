---
name: mom-slic-namespace-segments
description: "2026-07-17 USER-CONFIRMED WORKING: SLIC messages display in-game. Message(player,'Key') needs a DEFINED messagebox segment (scen_str keys alone = silent no-op). SLIC has ONE flat namespace: string key == segment name -> 'not a string variable' error; messagebox name == handler name -> duplicate segment = load-time AV that MIMICS the intermittent setup crash. Grep all slc for a name before adding any segment."
metadata: 
  node_type: memory
  type: project
  originSessionId: c5fa2bd2-0b1c-4e75-a617-6e92217b1336
---

**SLIC messages confirmed working in-game (2026-07-17, commit 66698e1).** The turn-1 `MomMsgSlicAlive` popup renders; blessings + magic-power popups use the same proven path.

- Engine contract (slicfunc.cpp `Slic_Message`): arg 2 must be a **defined segment** (messagebox block) — else `SFN_ERROR_NOT_SEGMENT`, silently. Base form: `messagebox 'Name' { Show(); Text(ID_STRKEY); }`; `ID_` + verbatim str-file key (tut2 convention); MessageType optional.
- **One flat namespace** (handlers, messageboxes, ID_-stripped string keys share the symbol table). Collisions produce escalating failures: string-key/segment → SLIC Error dialog "X is not a string variable" (slicif.cpp:1682); segment/segment (messagebox named same as a HandleEvent trigger) → **0xC0000005/0xC000041D during scenario load — looks exactly like the documented intermittent setup crash**. Two consecutive "intermittent" crashes right after a SLIC edit = the edit.
- Naming scheme now: handlers `Mom*`, messageboxes `MomMsg*`, string keys `MOM_MSG_*`.
- **Feature parity vs original momjr source** (h:\games\ctp2\mom scenario.slc, 8 handlers): imported/redesigned = magic init, per-turn income, school selection, mana nodes (goods-radius redesign), overflow auto-summon (replaces AI casting), event-driven magic popup. **NOT imported: keypress spellcasting (Demon Strike 'd', Flame Strike 'f'), on-demand magic-info key, AI spell targeting** (original's FindEnemyTarget was itself a placeholder, and the original uses unverified SLIC forms throughout).

Related: [[mom-slic-save-cache]], [[mom-slic-message-interpolation]], [[mom-magic-verified-clean]], [[mom-intermittent-setup-crash]].
