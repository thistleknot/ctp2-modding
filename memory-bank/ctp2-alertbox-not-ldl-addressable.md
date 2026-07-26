---
name: ctp2-alertbox-not-ldl-addressable
description: SLIC alertbox arms are NOT reachable by LDL name (duplicates collapse in the by-string table), but they ARE clickable -- the "posted buttons are lethal here" claim was my own miss-aimed battery and is falsified; derive aim from the live frame.
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T06:32:01.525Z
---

**TOP OF MIND. One channel is shut, one is OPEN -- and I got that backwards once.**

1. **~~Posted mouse BUTTON = process-lethal at the 1024x1280 client.~~ FALSIFIED
   2026-07-26.** All three 0xC0000005 deaths behind that claim were sends produced
   by turnloop's calibration battery at **x0.80** -- i.e. MISSES -- before the
   battery tried the identity factor first. With identity-first ordering at
   `capture_w == content_w`, a click on a frame-measured arm centre lands cleanly:
   `--summon-arm 1` gave `send = capture x1.00`, `closed=True`, the arm body ran,
   and the next turn read **"A Guardian Spirit manifests in your capital."** --
   6/6 turns, 0 SLIC errors. **MISSING is what kills on this surface, not
   clicking.** I generalized a broken instrument into a story about the engine,
   then into "needs an exe rebuild, which is yours to run" -- and the lever I
   called untried (`--summon-arm`) was already in my own argparse. See
   [[feedback-instrument-before-environment]].
2. **Arms are not addressable by LDL name.** (Stands.) With the box visibly open,
   all four response-button names returned `obj=00000000`; `StandardMinimizeButton`
   → `12D9C4B0` and the window itself → `12D88A78` both resolved (so the probe
   works). Cause: every arm is newed from the identical block string
   `StandardMessageWindow.StandardResponseButton`, `aui_Ldl::Associate` keys the
   by-string table on `hash(ldlBlock)`, so duplicates collapse to one entry.
   **Never inject the WINDOW** — the hook casts `aui_Window*` to `aui_Button*`
   and takes the process down (0xFFFFFFFF).
3. **Minimize is a dismissal, not an arm.** (Stands.) It hides the window without
   running any arm body, and does not reliably clear a SLIC alertbox (the shared
   table entry lands on whichever window registered last). So `dismiss_message`
   injects minimize first (free, no aim needed) and falls back to a CLICK.
4. **Dismiss aims at the LAST-declared arm, never index 0.** The engine renders in
   REVERSE declaration order, so index 0 is the FIRST declared arm — in MagicMenu
   that is `Summon Creature`. Closing a box by firing its side-effecting arm would
   silently place orders the run never asked for. Close is declared last, renders
   leftmost, decl_index `len-1`.
5. **Derived aim is safe; pinned aim is not.** `find_alert_box` /
   `find_alert_buttons` re-measure the parchment and the dark glyph runs on every
   frame, so a caption change cannot move an arm out from under the aim.

**Every legal mode on the primary display is portrait** (`\\.\DISPLAY4`, 19 modes,
all w < h). There is no legal landscape geometry without changing the user's
desktop — surface it, never do it silently. `768x1024` fails
`boot asserts failed: new_game_check`; `1024x1280` is the only geometry proven to
boot and advance turns. The engine REFLOWS its in-game UI to the client (it does
not letterbox), which is why aim points authored at 1024x768 are wrong here.

Related: [[ctp2-input-reach-by-surface]], [[ctp2-interactive-slic-link7]],
[[ctp2-primary-display-gates-harness]], [[feedback-instrument-before-environment]].
