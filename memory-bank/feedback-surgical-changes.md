---
name: feedback-surgical-changes
description: "Between fixes, touch ONLY what the current fix strictly requires. Do NOT make speculative/exploratory edits to game data or engine files while chasing a different problem — each stray edit risks a NEW regression the user then has to catch."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**Don't touch what you don't need to between fixes.** (User, 2026-07-13, emphatic — after a speculative TGA edit to fix a fugly coincided with an advance-icon misalignment the user had to catch.)

**Why:** every stray edit is a new regression surface. The user is playtesting one thing at a time; when Claude edits files that aren't strictly part of the current fix (exploratory TGA rewrites, format experiments, "while I'm here" changes), it introduces bugs that get blamed on — and entangled with — the fix under test. This session repeatedly reintroduced fuglies/crashes by editing broadly instead of surgically.

**How to apply:**
- Make the SMALLEST change that addresses the confirmed root cause. One fix = one minimal edit.
- Before editing any file, ask: does THIS fix require THIS edit? If not, don't.
- NEVER do speculative "let me try changing X and see" edits on live game data during a playtest loop — diagnose from source/read-only first, edit only when the fix is confirmed.
- If a diagnostic edit turns out wrong, RESTORE it immediately AND verify byte-identical restoration before moving on.
- Keep a clean revert path: back up before editing, confirm the restore actually took.
- Relates to the Operating Contract "Surgical Changes" principle: touch only what you must; clean up only your own mess. See [[feedback_harness_only]].
