---
name: mom-sprite-numbering-pinned
description: "newsprite.txt custom sprite ids are PINNED to GU<id>.SPR filenames on disk — renumbering breaks every custom unit's art. Generator merge now preserves existing assignments; regen reverts any output-only hand-fix (backport to csv same-session)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8e98ae7c-8285-43fe-8244-da734fb5365b
---

2026-07-14 peasant-wrong-art regression, root-caused:
- **newsprite.txt name→id assignments are pinned to disk**: build_sprites.py bakes the id into the GU<id>.SPR filename (SPRITE_PEASANTS 104 ↔ GU104.SPR). The generator's newsprite merge used to renumber customs from Units.txt encounter order → regen scrambled all custom unit art. Fixed in ctp2_generator.py (merge preserves existing scenario assignments, appends only new names). Never renumber without rebuilding/renaming the .SPR files.
- **Regen reverts output-only hand-fixes**: commit 73e7a6f's hero gating (9 champions behind ADVANCE_MYSTICISM) lived only in Units.txt; units.csv said 'no' → regen flipped them to WARRIOR_CODE (start-guaranteed → turn-0 hero flood). Backported: units.csv prereq='Mys'. **Any generated-.txt fix must land in the csv/control plane the same session.**
- Wiki: lessons_learned.md § "[REGRESSION+FIX] generator regen reverted committed hand-fixes". Related: [[mom-canonical-toolchain]], [[mom-sprite-pipeline]], [[mom-wiki]].
