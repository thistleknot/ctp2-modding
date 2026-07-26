---
name: ctp2-dpi-artifact-not-engine-scale
description: "SUPERSEDES every per-surface send-scale memory — the x0.80/x1.25 scales were OUR SetProcessDPIAware() call, not engine behaviour. uiwalk is now DPI-unaware: send == capture, 1:1, everywhere."
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T14:16:29.709Z
---

**TOP OF MIND. Supersedes the coordinate claims in
[[ctp2-primary-display-gates-harness]], [[ctp2-input-reach-by-surface]],
[[ctp2-environment-laws]] (L1), and [[ctp2-alertbox-not-ldl-addressable]].**

**Root cause.** `uiwalk.py` called
`ctypes.windll.user32.SetProcessDPIAware()` while `ctp2.exe` ships **no DPI
manifest**. On a 125%-scaled primary that puts harness and game in different
coordinate spaces: `GetClientRect`/`GetWindowRect` returned PHYSICAL pixels
(1280x960) for a client the game believed was logical (1024x768). Ratio:
exactly **1.25**.

Everything built on top of that was an artifact. The "empirical per-surface send
scales" — message x0.80 (= 1/1.25) and alertbox x1.25 — were the same single
mismatch observed from two directions and mistaken for engine behaviour.

**With uiwalk DPI-unaware, send == capture, 1:1, on EVERY surface.** Fix was
deleting the awareness call. Captures returned to 1024x768; the four goldens
went from 0/4 (0.144 / 0.075 / 0.193 / 0.454) to **4/4 at 1.000**.

**A perfect 1.000 is the proof the goldens were never stale.** I had claimed
they were "captured at 1024x1280 under a portrait primary". They were always
correct; the instrument was broken. Third occurrence of blaming the environment
before the instrument — see [[feedback-instrument-before-environment]].

**Two other harness facts settled the same day:**

- A **native `#32770` modal blocks the engine's message pump**, so PrintWindow
  returns the last painted bitmap forever and every capture in a run comes back
  byte-identical. That reads as "hung game" or "stale capture" and it is
  neither. Here it was `'Load save game Error'`, raised because `--save`
  **defaults to `uiwalk_start`** — a save the engine cannot load. Menu-entry
  walks need `--save none`. Now guarded by
  `Game._assert_no_blocking_modal()` on every `get_hwnd()`, which raises naming
  the dialog. Found by enumerating the PID's top-level windows, not by
  reasoning about coordinates.

- **A posted in-game `click` is process-lethal** (0xC0000005, ~5 runs), even at
  the corrected 1:1 coordinate, and even with stock sprites restored. The click
  itself is the trigger. `verify_centering.json` now waits instead and completes
  all 14 shots at 4/4. Use the `press:`/`select:` injection hook — it posts no
  mouse input and needs no coordinates.
