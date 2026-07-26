---
name: mom-slic-control-plane-dimension
description: "CLOSED — SLIC is a control-plane dimension that flows BACKWARD (slc -> xlsx); a cell holds real source, not signatures; drift gates must normalise openpyxl's None."
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-26T16:38:46.172Z
---

CLOSED 2026-07-26. `mom_dimension_inventory.xlsx` is the artifact the mod is
based on: **one tab per dimension**, and **a cell is a file and/or a set of
constants/classes/functions — the content itself, not a manifest describing it**.
I first shipped the SLIC dimension as a flat CSV of signatures and was corrected.
A table of names is a table of contents; nothing can be rebuilt from it.

**Direction.** Every dimension is forward-generated (Civ2 RULES.TXT -> xlsx ->
scenario) EXCEPT SLIC, which has no Civ2 upstream. `tools/backcast_slic.py` runs
`scenario/*.slc --> xlsx` and **never writes SLIC** — text stays diffable and
compilable. Writes the `slic` tab (module rows; columns constants / functions /
handlers / triggers / segments / source, whole blocks) plus flat `slic_index`.
Run it AFTER `export_mod_workbook.py`, which rebuilds the forward tabs and does
not know about SLIC.

Derived: 8 modules, 48 declarations, 57,196 bytes. Include order parsed from
`scenario.slc`'s `#include` list, never hardcoded. The tab it replaced was
hand-maintained and rotted: 17 declarations, `mom_magic.slc` marked PLANNED
though it ships and was verified ([[mom-magic-menu-verified]]), `mom_spells.slc`
absent, and no tool read it.

**Structure derived, prose merged.** `purpose`/`status` persist in
`tools/momjr_csv/slic_purpose.json` keyed `module:name`, so new code surfaces
with an empty purpose (a visible TODO) and curated intent is never clobbered —
except a stale `PLANNED`, which never survives over code that exists.

**HARNESS LAW: openpyxl round-trips an empty string as `None`.** `--check`
reported STALE right after a clean write because the comparison hit `None` vs
`""`. Normalise BOTH sides of any table drift gate. Test the gate in both
directions — clean exit 0, injected handler STALE exit 1, revert exit 0. A gate
exercised only on the passing case is not a gate
([[feedback-verify-the-claimed-symptom-headlessly]]).

**`mom.zip` is the MOD, not the repo — the repo holds the code.** Built by
`tools/build_mod_zip.py` from exactly what the engine loads (`packicon.tga`,
`packlist.txt`, `scen0000/**`, the shape shipped scenarios use), under a `mom/`
prefix: 666 files, ~3.9 MB. The zip that was there before wrongly carried
`tools/` and the xlsx.
Related: [[mom-canonical-toolchain]], [[mom-universal-encoder]],
[[mom-slic-namespace-segments]], [[mom-wiki]].
