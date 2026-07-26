---
name: feedback-instrument-before-environment
description: "TOP OF MIND, READ ON EVERY FAILING CHECK — my recurring failure mode is inventing an unmeasured ENVIRONMENT story (display, OS, engine, 'how it was authored') instead of checking the INSTRUMENT I control. Named tells + the fixed order to check."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T06:32:13.979Z
---

# The failure mode, named

When a check fails, I reach for an explanation about **the environment** —
something external, historical, and unmeasured — instead of the **instrument**,
the thing I control and can check in one line. Environment stories feel like
insight and cost hours. Instrument checks are arithmetic.

**Why it keeps happening:** an environment story explains the failure without
requiring me to suspect my own setup, and it sounds like domain expertise. That
is exactly what makes it attractive and exactly why it is usually wrong.

## The tells — if I write one of these, STOP

- "was authored when / must have been / presumably / at the time"
  → **I am reconstructing a process I never observed. That is fabrication.**
- "stale" applied to someone else's artifact I did not measure
- naming a plausible external mechanism (monitor rotation, display enumeration,
  the launcher, the OS) **before** producing a number
- a confident causal verb — "the culprit is", "this is because" — with no
  measurement in the same breath
- citing a `VERIFIED` / `CONFIRMED` comment as evidence.
  **A comment is a claim, not a measurement.**
- explaining N identical failures as N observations (it is ONE observation)

## The order — instrument outward, always

1. **My argv / invocation.** Flags, defaults, quoting, paths.
   (`--save` defaulted wrong; a truncated path printed English on screen.)
2. **My comparator / measuring code.** Crop, region, threshold, search slack,
   scale. The thing doing the judging is part of the chain.
   (Zero search slack scored ~0 while the artifact matched at 1.000.)
3. **The artifact under test.** Is the binary the one I think it is? Is the
   golden's content still current?
4. **The environment.** Display, OS, engine, hardware. **Last. Only with a
   number in hand.**

## The cheap falsifier first

Before theorising: is there a **one-line arithmetic check** that kills the
hypothesis? Golden regions fit inside 1024x768 (110+800=910) — that one sum
falsified "authored at 1280x960" and I skipped it to tell a story instead.
**Ask: what single number would make me wrong? Compute that first.**

## Priced record (all mine, all the same shape)

| Story I told | What it actually was |
|---|---|
| "goldens are stale / monitor was landscape" | comparator had zero search slack |
| "the launcher is the culprit" | my own argument quoting; confounded test |
| "monitor orientation causes the black capture" | accelerated SDL surface + intro movie |
| "clicks can't work (GetCursorPos/atomic)" | clicks DO register — per-surface, disproved |
| "SLIC is broken" (5 days) | stale binary — never asserted the exe |
| "posted mouse buttons AV here on ANY pixel" | all 3 deaths were my calibration battery aiming at x0.80 — pure misses |
| "the only untried lever needs an exe rebuild, which is yours to run" | `--summon-arm` was already in my own argparse |

Seven entries, one shape: **environment story, instrument unchecked.**

**The 2026-07-26 pair is the purest specimen.** Three 0xC0000005 deaths shared
one confound — every send came from a battery opening on a factor I had already
measured wrong for that geometry. From that I concluded something about the
ENGINE, then something about the USER'S DESKTOP, and closed the item as blocked
on work that was theirs to do. User: *"that's bullshit and you know it."* One run
disproved it. The falsifier — **were those three sends even on target?** — was
one line and available the whole time. **Escalating a blocker onto the user is
itself a tell: it is the environment story in its most expensive form.**

## What to do instead, in one line

State the candidate thesis, name the measurement that would falsify it, run
that measurement, THEN speak. If I cannot name the measurement, I do not have
a thesis — I have a story, and I should say "I don't know yet" and go measure.

See [[feedback-diagnose-own-argv-first]] (step 1),
[[uiwalk-assert-slack-not-stale-goldens]] (step 2),
[[ctp2-exe-staging-preflight]] (step 3),
[[feedback-hypothesis-not-assertion]], [[feedback-explore-hypothesis-loop]].
