---
name: ctp2-repo-corruption-orphan-push
description: "CLOSED 2026-07-26 - the CTP2 repo ancestry is permanently unpushable (2 objects lost to the H: FS fault); work lives on branch mom-base-clean, pushed to BOTH remotes"
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T03:18:19.665Z
---

**Push to `modding`/`momjr` on branch `mom-base` will ALWAYS fail.** Not a network
or auth problem: `git push` must walk the full ancestry, and two objects are gone
from the H: filesystem fault and exist in no clone or remote:

- commit `7a8c2eaa` -- parent of `ec2da57`
- blob `d859b919` -- under a tree introduced by `73e7a6f` ("gate MoM heroes behind magic")

Symptom is always `error: Could not read <sha>` / `revision walk setup failed`,
before a byte goes over the wire. `git replace --graft ec2da57` makes the walk
succeed LOCALLY but **push ignores replace refs**, so it does not help.
`git filter-branch` is blocked by the Claude Code classifier in this environment.
The disk was already chkdsk'd once -- the objects are not coming back.

**Resolution (done):** orphan branch **`mom-base-clean`** at the current tree.
`2ef227d`, pushed to BOTH `modding` and `momjr`, remote SHA verified equal to
local. `mom-base` is left in place locally, deleted nothing.

**The near-miss worth remembering:** while verifying the snapshot I found **214
`GU*.SPR` unit sprites on disk with ZERO tracked** -- `git check-ignore` returned
nothing, so they were never ignored, just never `git add`ed. Every MoM unit's map
art was one fault from gone. **A file being present and correct on disk is not
evidence it is in a commit.** Now tracked (523 spr total, 114 MB, with
`Scenarios/mom`). The remaining ~1.8 GB untracked is stock Activision bulk
(zfs/PDF/DLL), deliberately excluded -- recoverable from install media and the
`(copy)` backup tree.

Work on `mom-base-clean` from now on. See [[mom-fs-corruption-recovery]].
