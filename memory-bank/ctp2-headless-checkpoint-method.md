---
name: ctp2-headless-checkpoint-method
description: "Verify in-game behavior by building incremental golden checkpoints headless (uiwalk) — Claude launches and drives, user never hand-tests; includes the harness gotchas that cost real time"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T00:07:45.544Z
---

**Claude launches the game and drives every test. The user verifies nothing by
hand and should not even see the window.** Runs go through `uiwalk.py`, which
posts input to the window handle and captures with `PrintWindow`, with the window
stashed off-screen at -32000,-32000 (`_stash_offscreen`; `UIWALK_VISIBLE=1`
overrides).

**Why:** repeated attempts to verify one interactive feature end-to-end in a
single shot failed for days and pushed manual testing back onto the user, who was
explicit that automating this is the whole point of the harness.

**How to apply:** build ONE small verified state at a time, freeze it as a steps
JSON + golden, then extend from that checkpoint. Never attempt the full walk
first. Gate every run on [[ctp2-exe-staging-preflight]].

First green checkpoint (2026-07-24):
`Scenarios/mom/tools/uiwalk/steps/checkpoint_main_menu.json`
(wait → esc → wait → esc → wait_stable → shot → assert vs `goldens/main_menu.png`)
→ `main_menu_check 1.000 0.90 PASS`, exit 0.
Run: `python uiwalk.py --run steps/checkpoint_main_menu.json --save none`

Menu steps use the injection hook, NOT clicks — see
[[ctp2-menu-injection-not-clicks]] (settled: clicks are inert in menus, and
captures are 1:1 with engine coords).

Harness gotchas (each cost real time):
- `esc` **while in-game opens the modal Options window**, which swallows every
  later key. Signature: all subsequent screenshots are BYTE-IDENTICAL — that means
  "a modal ate the input", not "nothing happened". Don't send speculative `esc`.
- `assert`'s `golden` field must NOT include `.png` (uiwalk appends it).
- `wait_stable` is pixel-EXACT identity and silently degrades to a plain wait.
- `PrintWindow` works off-screen; the `mss` fallback and `--global-input` do NOT —
  off-screen they yield black/garbage that mimics "UI never appeared".
- `save/games/uiwalk_start` is a **MoM** save ("Tribes of Life"), so
  `--save uiwalk_start` boots deterministically and skips the crash-prone New Game
  menu walk. Saves cache compiled SLIC → use `/reloadslic` (apostrophe console,
  VK_OEM_7, now in the VK map) or start a NEW game. See [[mom-slic-save-cache]].

Full write-up at the top of `Scenarios/mom/lessons_learned.md` ([[mom-wiki]]).
