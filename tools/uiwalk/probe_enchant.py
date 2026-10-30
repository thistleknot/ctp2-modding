"""probe_enchant.py -- cast unit enchantments in a live MoM game and photograph the result.

NO GOVERNING SPEC. Basis: operator 2026-10-28 ("test every type of unit enchantment spell
to confirm it works ... reload when you run out of magic, don't save, same unit"),
plan in .tmp/pland.md.

Usage:  python probe_enchant.py <tag> <action> [<action> ...]
Actions (each is followed by a screenshot named <n>_<action>):
  fire     press the Magic button (opens the spellbook hub)
  type:X   type the characters X (number keys answer spellbook alertboxes)
  j        open the 'j' magic status box (mana)
  esc      Escape
  end      press the END TURN key (enter)
  wait     5 s settle
  stats    just a screenshot

Boots MoM through the first 40 prologue steps: the game is on the map with the starting unit
selected (the unit panel shows its stats). Nothing is saved; the game is killed at the end.
"""
from __future__ import annotations

import ctypes
import json
import os
import shutil
import sys
import time
from pathlib import Path

import cv2

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import uiwalk  # noqa: E402

PROLOGUE = 40  # through 'peasant_on_open_map': the starting unit is selected


def main() -> int:
    tag, actions = sys.argv[1], sys.argv[2:]
    uiwalk.PREFER_RELEASE = False
    uiwalk.LAUNCH_TIMEOUT_S = 3 * 90  # slow machine + antivirus (operator 2026-10-27)
    uiwalk.SOURCE_ROOT = Path(r"H:\Games\civctp2-gaia-integration\ctp2_code\ctp")
    uiwalk.preflight_exe("select:")
    uiwalk.preflight_display()
    ctypes.windll.user32.SetProcessDPIAware()

    steps = json.loads((HERE / "steps/full_game_v3.json").read_text())
    row = uiwalk.scenario_pack_index("mom")
    for s in steps[:PROLOGUE]:
        if s.get("path") == "ScenarioWindow.AvailableListBox" and s.get("index"):
            s["index"] = row
            break

    run_dir = uiwalk.RUNS / (time.strftime("%Y%m%d-%H%M%S") + f"-enchant-{tag}")
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"artifacts -> {run_dir}")

    game = uiwalk.Game()
    save_name = os.environ.get("CTP2_SAVE")
    ariel_dir = uiwalk.EXE_DIR / "save" / "games" / "Ariel"
    backup = uiwalk.RUNS / "ariel_save_backup"
    try:
        if save_name:
            # Load a COPY of the operator's save (~200 mana, Ariel). Turn ends autosave
            # into games/Ariel, so that folder is backed up here and restored in finally.
            src = uiwalk.find_save(save_name)
            if backup.exists():
                shutil.rmtree(backup)
            shutil.copytree(ariel_dir, backup)
            scratch = uiwalk.RUNS / "saves" / src.name
            scratch.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, scratch)
            game.launch(None, [f'-l"{scratch}"'])
            inp = uiwalk.PostInput(game)
            uiwalk.run_steps(game, inp, [{"do": "wait_stable", "ms": 15000}], run_dir,
                             baseline=False, dry=False)
        else:
            game.launch(None, [])
            inp = uiwalk.PostInput(game)
            uiwalk.run_steps(game, inp, steps[:PROLOGUE], run_dir, baseline=False, dry=False)
            uiwalk.run_steps(game, inp, [{"do": "wait_stable", "ms": 8000}], run_dir,
                             baseline=False, dry=False)

        def run(seq):
            uiwalk.run_steps(game, inp, seq, run_dir, baseline=False, dry=False)

        cv2.imwrite(str(run_dir / "00_start.png"), game.screenshot())
        for n, act in enumerate(actions, 1):
            if act == "fire":
                run([{"do": "trigger",
                      "path": "ControlPanelWindow.ControlPanel.ShortcutPad.MagicButton"}])
            elif act.startswith("type:"):
                run([{"do": "type", "text": act[5:]}])
            elif act == "j":
                run([{"do": "key", "keys": "j"}])
            elif act == "esc":
                run([{"do": "key", "keys": "esc"}])
            elif act == "end":
                run([{"do": "key", "keys": "enter"}])
            elif act == "turn":
                # End the turn (shift+a, as steps/force_endturn.json does) and let the AI play.
                # END TURN takes mouse input first: hover the top bar, then the key
                # (steps/full_game_v3.json does the same ping at the top of each turn).
                run([{"do": "hover", "fx": 0.586, "y": 6}, {"do": "wait", "ms": 1500},
                     {"do": "key", "keys": "shift+a"}, {"do": "wait", "ms": 20000},
                     {"do": "wait_stable", "ms": 30000}])
            elif act.startswith("click:"):
                # click:X,Y in the live client; used when a button has no number key.
                x, y = (int(v) for v in act[6:].split(","))
                inp.click(x, y)
            time.sleep(1.0)
            run([{"do": "wait_stable", "ms": 6000}])
            name = act.replace(":", "_")
            cv2.imwrite(str(run_dir / f"{n:02d}_{name}.png"), game.screenshot())
            print(f"{n:02d} {act}")
    finally:
        game.kill()
        if save_name and backup.exists():
            # Put the operator's Ariel save folder back exactly as it was.
            shutil.rmtree(ariel_dir, ignore_errors=True)
            shutil.copytree(backup, ariel_dir)
            print("restored games/Ariel from backup")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
