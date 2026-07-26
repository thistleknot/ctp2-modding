---
name: mom-gl-dbname-crash
description: "Great Library <L:DATABASE_X,...> hyperlink with an invalid DB-name X crashes at greatlibrary.cpp:352 (0xC0000005); only 12 names are legal"
metadata: 
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

A Great Library hyperlink `<L:DATABASE_X,OBJECT>Text<e>` whose `X` is not one of the
engine's 12 database names makes `GreatLibrary::Get_Database_From_Name` hit
`Assert(false)` at greatlibrary.cpp:352 → `0xC0000005` the instant that entry renders
(debug build). MoM shipped 84 `<L:DATABASE_IMPROVEMENTS,IMPROVE_X>` links — there is **no
bare DATABASE_IMPROVEMENTS**; city improvements are `DATABASE_BUILDINGS`, wonders are
`DATABASE_WONDERS`. Crash surfaced browsing to the Guardian Spirit / Life Lore entry.

The 12 legal names (greatlibrary.cpp `s_database_names[]`): DEFAULT, UNITS, BUILDINGS,
WONDERS, ADVANCES, TERRAIN, CONCEPTS, GOVERNMENTS, TILE_IMPROVEMENTS, RESOURCE, ORDERS,
SEARCH. Authored links only ever use the middle ~10; DEFAULT/SEARCH are valid but unused.

**Why:** the GL descriptions with `<L:` cross-links live in `english/gamedata/Great_Library.txt`
(NOT `gl_str.txt`, which holds only record names). Route by object home: `WONDER_X` in
Wonder.txt → `DATABASE_WONDERS,WONDER_X`; else → `DATABASE_BUILDINGS,IMPROVE_X`.

**How to apply:** `validate_all_surfaces.py` surface 2a now flags any `<L:DATABASE_X,...>`
where X ∉ the 12 names — the guard that would have caught this offline (the old per-type
loop only checked KNOWN names, silently skipping the typo). Run it before every launch.
Related: [[mom-db-error-class]] (orphan GL advance sections), [[mom-fugly-double-load]].
