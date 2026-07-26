---
name: ctp2-two-repos-harness-vs-mod
description: "CLOSED — ctp2-modding is the HARNESS (code, wiki, memory-bank, control-plane scripts); ctp2-momjr is the MOD. Never merge one tree into the other."
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T17:19:47.906Z
---

Two repos, two purposes. Confusing them destroyed the harness repo once.

- **`ctp2-modding`** = the harness. `tools/` (pipeline + `tools/uiwalk/`),
  `docs/`, `wiki/lessons_learned.md`, `memory-bank/`, `README.md`, and
  `examples/<mod>/control-plane/` with a README **pointing at** the mod's repo.
  **No scenario data ever lands here** — `.gitignore` blocks `Scenarios/` and
  `scen0000/`. Remote `modding` on the parent checkout.
- **`ctp2-momjr`** = the mod, and it IS `Scenarios\mom` (there is no
  `Scenarios/momjr` folder). Scenario, workbook, `mom.zip`. Remote `origin`
  inside that nested repo.

**The failure.** The parent checkout (the whole game install) carried a `momjr`
remote and I pushed the game tree into the scenario repo; then I merged
`mom-base-clean` into `ctp2-modding`'s `main`, wiping `tools/`, `control-plane/`,
`wiki/`, `memory-bank/` and the README. Recovery was only possible because
`archive/toolkit-main` (`123db97`) preserved the original layout. Restored as
`92d3e1d` on top of the bad merge — history kept, tree replaced, 267 files.

**Laws.**
- Check `git remote -v` in BOTH repos before any push. The parent must have
  exactly one remote: `modding`.
- Never `git checkout` a small branch in the parent — its tree is the game
  install, and checkout would delete it. Use `git commit-tree` to build a
  commit from a chosen tree with chosen parents; it touches zero working files.
- `git gc` is chronically broken in the parent (ancestry corruption). Prefix
  every git call with `-c gc.auto=0` ([[ctp2-repo-corruption-orphan-push]]).
- Harness-vs-live file diffs are mostly CRLF noise; use
  `diff --strip-trailing-cr` to find the real changes.
- Curate, don't bulk-copy: `tools/uiwalk/runs/` alone is 1.8 GB. Scripts, step
  JSON and goldens are tracked; captures and logs are not.

Related: [[mom-canonical-toolchain]], [[mom-slic-control-plane-dimension]],
[[mom-wiki]], [[feedback-integrate-folder-wip]].
