---
name: feedback-explore-hypothesis-loop
description: "How to explore an opaque UI/system — telos, one-variable battery, falsifiable prediction, pixel-delta as reward signal, revise-or-park, and record every result into a JSON map that becomes the supervised set"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T01:15:32.304Z
---

**Treat UI exploration as a TREE SEARCH (MCTS/minimax in prompts), not a bandit.**
Nodes = UI states. Edges = actions (press / select / click / key). The reward is
SPARSE: it only pays when you reach the next PREFERABLE STATE on the path to the
goal. Everything else is a rollout that returns 0.

- **Goal state** drives value: distance-to-goal is the heuristic. Current goal =
  a loaded MoM game so the SLIC hotkey can finally be exercised.
- **Root is cheap and deterministic**, which is what makes this tractable: a
  relaunch replays to any known node in ~40s, and the goldens PROVE you landed on
  the node you think you did. So simulate from root freely.
- **BACKTRACK IS A LEGAL MOVE.** Back / reopen / relaunch to restore a known node
  and re-test a hypothesis from clean state. Do not try to reason your way out of
  a dirty state -- replay to a node you trust.
- **Expand the frontier deliberately:** from a node, list the untried edges, pick
  the one with the best shot at the next preferable state, and record the outcome
  (verified true OR false) into the map. False edges have real value: they prune.
- **Do not grind one hypothesis** -- pivot to another edge when it stops paying.

**Why:** on 2026-07-24 a "clicks don't work" belief blocked progress for hours.
Running the loop properly killed it in three iterations and produced a
deterministic fix. The user's framing: *"give some thought to what states you
want to explore, document their telos and attempt it, else place it to the side
and try something else — this gives a more robust supervised set."*

**BUILD AN ENVIRONMENT MODEL, NOT A PER-STATE LOOKUP TABLE.** The latent space
does not collapse between states -- there is ONE transition function underneath
every screen. A per-state coordinate table cannot be wrong in a useful way; it
just goes silent off-table. A model makes falsifiable claims about states you
have never opened.

So the object of study is the LAWS (`ui_map.json -> environment_model`):
coordinate transform, click protocol, injection channel, observation decoder,
SLIC persistence, binary identity. Per-state pixels are DERIVED from those laws.

**The test of a law is that it predicts an UNVISITED state.** Before opening a
new screen, predict what an action there will do; then open it and check. A law
confirmed only where it was discovered is still a guess with good PR.

**The loop:**
1. **Telos first.** Name the state you want to reach and why. No aimless probing.
2. **Vary ONE thing.** A battery where only the variable under test differs
   (e.g. same coords, same target, only "before scroll" vs "after scroll").
3. **State a falsifiable prediction BEFORE running** ("row 1 needs send
   (625,300)"). A test with no prediction teaches nothing.
4. **Read the delta, not the vibe.** Diff consecutive screenshots; the pixel
   count is the reward signal (see the delta table below).
5. **Falsified → revise the THESIS, not the symptom.** Guess A (button latched;
   release at new position) was falsified; Guess B (grab held at the PREVIOUS
   position) was confirmed. Do not stack patches on a dead thesis.
6. **Park, don't grind.** After ~2 failed revisions, write the gap down with its
   workaround and move on. Parked here: clicks still dead after Back→reopen;
   workaround = injection.
7. **Record every result — including the false ones — into the JSON map**
   (`tools/uiwalk/ui_map.json`), with a `verified` flag. That file IS the
   supervised set: a future session reads it zero-shot instead of rediscovering.

**Pixel-delta → meaning (CTP2 menus, 1280x960 capture):**
| delta | means |
|---|---|
| 0 px | input never landed (or a modal ate it) |
| ~4-5k | one list row selected / a button enabled |
| ~75-80k | list scrolled a page |
| ~180k | panel opened or closed |
| ~477k | whole screen — crash/blank, NOT a UI response |

**Worked example (3 iterations, ending in a deterministic fix):**
- Thesis 1 "clicks never work" → FALSIFIED (a click selected a row).
- Thesis 2 "only the FIRST click registers" → held, and retro-explained the
  36-click sweep whose first click hit empty space and burned the one live click.
- Mechanism A "button latched, release at new position" → FALSIFIED (no change).
- Mechanism B "grab held at PREVIOUS position" → CONFIRMED. Fix: before each
  click, move to and release at the previous click position. 1/3 → 3/3 clicks.

Related: [[feedback-hypothesis-not-assertion]], [[ctp2-menu-injection-not-clicks]],
[[ctp2-headless-checkpoint-method]].
