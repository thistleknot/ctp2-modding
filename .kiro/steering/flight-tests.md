# Flight Tests

Every feature change that touches generated game files MUST be flight-tested before
presenting to the user. "Untested" means "not done."

## What counts as a flight test

1. **Generator runs clean** — `python ctp2_generator.py` exits 0.
2. **Audit passes** — `python mom_audit.py` reports FAIL: 0.
3. **SLIC parse check** — if the change touches `.slc` files, verify no new
   `Symbol X is undefined` errors would occur by grepping for all referenced
   `ID_*` string keys and confirming each has a matching entry in `scen_str.txt`.
4. **Cascade check** — if a dimension record was added/removed, confirm all
   downstream files were regenerated (uniticon, gl_str, Great_Library, etc.).
5. **Headless game launch** — run the turnloop or a probe to confirm no SLIC
   error dialogs fire during the first N turns of gameplay.

## Headless test harness

Location: `tools/uiwalk/`

The harness launches CTP2 in windowed mode, drives it with PostMessage input
(no physical mouse/keyboard needed), and catches SLIC errors via Win32
MessageBox enumeration. Key entry points:

```powershell
cd "H:\Program Files(x86)\Activision\Call To Power 2\tools\uiwalk"

# Quick boot + N turns -- catches any SLIC error dialog:
& "C:\Users\user\py310\Scripts\python.exe" turnloop.py --turns 5

# Spellbook-specific probe (opens magic menu, exercises Cast a Working):
& "C:\Users\user\py310\Scripts\python.exe" probe_spellbook.py

# Full-game probe (longer run, checks endgame):
& "C:\Users\user\py310\Scripts\python.exe" probe_long_game.py
```

Preconditions:
- `ctp2_program/ctp/` has a runnable exe with runtime overlay staged.
- `userprofile.txt` has `WindowedMode=Yes` (1024x768).
- py310 packages: pyautogui, pygetwindow, pywin32, mss, opencv-python, numpy.

The turnloop's assertion channel: SLIC errors fire a native Win32 MessageBox
(parentless, title contains "Error"). The watcher enumerates these, logs the
error text, and answers IDYES (continue). Any dialog appearance = test FAIL.

## When to run headless tests

- After any change to `.slc` files or the spellbook generator.
- After pacing changes (DiffDB, Const.txt, advance costs) — run 5-10 turns to
  confirm the game doesn't choke on the new values.
- Before committing if the change could cause a runtime SLIC failure.

## What does NOT count

- "The generator ran" without checking its output.
- Audit passing on the OLD thresholds when you changed the scale.
- Committing and telling the user to "load it up and see."

## When to tell the user

Only after steps 1-5 pass. If you cannot verify a step (e.g. harness deps missing),
say so explicitly: "Audit green, SLIC string check clean, but turnloop could not
run because [reason]."

## Design docs first

Before implementing any pacing, scaling, or balance change:
1. Check `C:\Users\user\Documents\wiki\games\ctp2\` for existing design docs.
2. Check `Scenarios/mom/lessons_learned.md` for prior decisions.
3. Check `mod_policy.json` comments and `_doc` fields for design intent.

If a design doc already specifies the approach, implement THAT — do not invent a
new approach without acknowledging the deviation and getting user sign-off.
