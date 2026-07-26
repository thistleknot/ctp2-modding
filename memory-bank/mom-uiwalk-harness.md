---
name: mom-uiwalk-harness
description: "uiwalk = scripted in-game UI verification (launch → keys/clicks → screenshot → template-match vs contract-derived goldens). Claude RUNS this directly (reads screen, sends input, mutates nothing). Deterministic boot via engine arg -l\"<save>\"."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8e98ae7c-8285-43fe-8244-da734fb5365b
---

`Scenarios/mom/tools/uiwalk/uiwalk.py` — Claude-run in-game verification (user-approved plan 2026-07-14). Key facts:
- Boot: `-l"<save>"` auto-skips intro+menu; needs user's one-time `uiwalk_start` save of the static turn-0 start. `runinbackground` keeps it rendering unfocused.
- Nav: `Ctrl+5` opens Great Library (keymap.txt); GL Search box → type advance name = deterministic navigation. Search-box coord (246,94)@1024x768 client is provisional (calibrate via `--record`).
- Goldens from contract, not screenshots: `make_goldens.py` renders advances.csv cell_index cells via the extractor's helpers → `goldens/cell_<n>.png` + advance_map.json.
- Usage: `uiwalk.py --run steps/gl_advances.json` (PASS/FAIL table, exit 1 on fail); `--baseline`, `--dry`, `--attach`, `--keep`, `--record` (F12 stops). Kills by PID only.
- **HARD USER REQUIREMENT: never touch their physical mouse/keyboard.** Default backend = PostMessage to the game HWND + PrintWindow capture (game unfocused/background, zero interference). `--global-input` (pyautogui real cursor, FAILSAFE on) only with explicit user consent. `--record` observes clicks only, never generates input.
- NEVER run against / inject input into the user's own live game session — launch a fresh instance (or `--attach` only when asked).
- Full detail: wiki `lessons_learned.md` § "[TOOLING] uiwalk". Related: [[mom-wiki]], [[mom-advance-icons]], [[feedback-always-launch-game]].
