---
name: mom-wiki
description: Project wiki locations — lessons_learned.md is the canonical hard-won-lessons log; check it FIRST before re-deriving any past diagnosis. Memory files here summarize; the wiki holds full detail.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8e98ae7c-8285-43fe-8244-da734fb5365b
---

**The project wiki** (canonical, in-repo, committed — full detail lives there, memory files here are summaries that must POINT INTO it, not duplicate it):

- `Scenarios/mom/lessons_learned.md` — running log of hard-won lessons, newest sections at top. Check it FIRST before re-investigating any crash, fugly, sprite, SLIC, or icon issue. Today's entries land here as `## [TAG] Title (date)` sections.
- `MOD_DIMENSIONS.md` (repo root) — dimension map companion.
- `Scenarios/mom/tools/INTERCONNECTION_TRACKING.md` — which file references which dimension.
- `Scenarios/mom/tools/improvements_bmp_layout.md` — Improvements.bmp grid geometry + tech-sheet / art_cell_index contract.
- `Scenarios/mom/docs/` — `civ2_ctp2_entity_map.md`, `improvements_image_grid.md`.
- `Scenarios/mom/specs/` — SLIC magic system, sphere layer, sprite transparency specs.
- `Scenarios/mom/SURROGATES.txt` — register of stock-CTP2 surrogate entities retained/hidden for compatibility.

**Workflow rule:** when a session learns something durable, write the full entry into `lessons_learned.md` (top of file) AND a one-paragraph summary memory here linking to it. Related: [[mom-advance-icons]], [[mom-fugly-double-load]], [[mom-canonical-toolchain]].
