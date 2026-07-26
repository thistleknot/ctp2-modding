---
name: feedback-hypothesis-not-assertion
description: "Never assert a mechanism as fact — state a candidate thesis, name the evidence it rests on, and give the falsifiable prediction that would kill it"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T00:36:53.782Z
---

**Do not state mechanisms as fact. State a CANDIDATE THESIS, the evidence it
rests on, and the prediction that would falsify it.**

**Why:** on 2026-07-24 I asserted "clicks can't work — aui polls GetCursorPos and
CTP2_LISTBOX is `atomic true` so the scrollbar has no addressable path." That was
explanation-fitting: a borrowed mechanism dressed up as a finding. The user pushed
back ("it's a window bro — clicks obviously register in it") and was RIGHT. A
later run proved clicks do register: (797,555) selected a list row. My assertion
had shut down the correct line of attack and cost real time.

**How to apply:**
- Separate the OBSERVATION from the EXPLANATION. Observation: "36 synthetic
  clicks produced 0 response." Explanation: "possibly GetCursorPos polling" —
  label it as a guess, never as the reason.
- Give every thesis a falsifiable prediction, then run it. Example that worked:
  "clicks are scaled x0.8" predicts row 1 needs capture x 1.25 = (625,300).
- A thesis that explains 2 of 2 successes but contradicts an earlier null result
  is still only a thesis. Say so and name the unreconciled evidence rather than
  quietly dropping it.
- One observed change is a hypothesis, not proof of causation. Diff consecutive
  screenshots and re-run controlled before attributing cause. I twice attributed
  a row-highlight to the wrong cause by skipping this.
- When the user's model conflicts with mine, treat their counter-evidence as
  data, not as something to explain away.

Related: [[ctp2-menu-injection-not-clicks]] (the entry whose click claim this
corrects), [[ctp2-headless-checkpoint-method]].
