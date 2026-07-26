---
name: ctp2-headless-invariant
description: "HEADLESS IS ABSOLUTE — the user must never see a ctp2 window; enforce it as a continuous watchdog invariant, never as a stash-on-discovery event. Plus the --save default that faked six engine crashes."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T02:04:41.770Z
---

**HEADLESS IS NON-NEGOTIABLE.** *"FUCKING HEADLESS BRO. I SHOULDN'T SEE SHIT."*
If a CTP2 window is visible, the run FAILED regardless of what it asserted.
Never launch the exe outside `uiwalk.py` — a bare `Popen` bypasses the stash.

**Why event-driven stashing is not enough (measured 2026-07-24, leaked twice).**
`_stash_offscreen` ran at window DISCOVERY and re-ran only when the handle DIED.
The engine repositions its window on-screen during the scenario-load video-mode
change **while keeping the handle alive**, and long `wait` steps take no capture,
so nothing re-stashed it. Fix now in `uiwalk.py`:
- `_start_stash_watchdog()` — 150ms daemon thread forcing every window titled
  `Call To Power 2` to -32000,-32000. Started in `launch()` BEFORE the exe runs.
- `get_hwnd()` re-stashes on every access.
Enforce as a continuous invariant, never by hoping each path calls in.

**`--save` defaults to `uiwalk_start` — pass `--save none` for menu walks.**
The default silently appended `-l"<save>"`; that path contains a space, and on
direct argv the pre-embedded quotes get re-escaped, so the engine got a path
truncated at the first space (`Could not open "H:\Program`) and died ~1.5s after
window creation. That produced SIX consecutive `0xC0000374` heap-corruption WER
signatures which I wrongly pinned on `run-ctp2-dbg-crashcapture.ps1`.
**The launcher was innocent.** Build `-l<path>` UNQUOTED for direct argv.

**General:** a crash signature proves the process died, not that the engine is
buggy. When a harness defect and a WER signature coexist, eliminate the harness
first — it is far cheaper to test.

See [[ctp2-headless-checkpoint-method]], [[ctp2-environment-laws]],
[[feedback-hypothesis-not-assertion]].
