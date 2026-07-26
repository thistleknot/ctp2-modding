---
name: feedback-diagnose-own-argv-first
description: "The backward walk starts at MY command line, not the launcher — plus three sibling failures (confounded test with a prediction, six failures counted as six observations, forensic channels read while English error text was on screen)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T02:13:39.452Z
---

**Check your own argv, flag DEFAULTS, and cwd BEFORE any binary, launcher, or
engine hypothesis.** Operator-dictated 2026-07-24 after six runs of `uiwalk.py`
died with WER `0xC0000374` and the real cause was `--save` defaulting to
`uiwalk_start` on a walk that starts at the main menu. Fix: `--save none`.

Four distinct failures, cheapest lesson last:

1. **A stated prediction does NOT make a test clean — one variable does.**
   Direct-launch changed two things (bypassed PowerShell *and* changed `-l`
   quoting). It survived; I credited the wrong variable. Having predicted the
   outcome first does not launder a confounded result into a causal claim.

2. **Six identical failures is ONE observation.** Repeating the same wrong
   invocation proves REPRODUCIBILITY, not LOCATION. "Deterministic, not the
   documented intermittent" felt like narrowing; it narrowed nothing.
   Determinism was a property of my input.

3. **Rank evidence channels by information content, not by how technical they
   feel.** I read exit codes, WER signatures, md5s and pixel deltas while a
   dialog on screen said `Could not open "H:\Program`. One operator screenshot
   beat six runs. Heap-corruption codes felt like real debugging; they were
   noise generated downstream of a truncated path.

4. **The one to keep: the chain starts at my own invocation.** I began the
   backward walk at the launcher, having excluded my own command line from the
   search space without noticing. My inputs are part of the chain and are the
   cheapest link to check.

**Compressed:** a crash signature proves the process died, not that the engine
is broken. When an invocation/harness defect and a WER signature coexist,
eliminate the harness first — likelier AND cheaper to falsify.

Full text: `Scenarios/mom/lessons_learned.md` R11.
See [[ctp2-headless-invariant]], [[feedback-hypothesis-not-assertion]],
[[feedback-explore-hypothesis-loop]], [[mom-wiki]].
