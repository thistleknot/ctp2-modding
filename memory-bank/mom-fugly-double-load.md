---
name: ""
metadata: 
  node_type: memory
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

The MoM "fuglies" — rainbow static where the city name renders (Build Manager city
selector AND control-panel name banner) — are a COMPOUND bug with THREE co-occurring
causes, ALL documented in `git log --grep=fugl`. Fixing one is not enough; the static
persists until all three are clean:

1. DB double-load (7afc935): a concept as BOTH `IMPROVE_<X>` (buildings.txt) and
   `WONDER_<X>` (Wonder.txt) -> conflicting build-manager indices -> render corruption.
   Generator now skips wonder rows (improvements.csv cell_index>=40) when emitting
   IMPROVE_ blocks; validate_all_surfaces.py surface 8 guards the overlap (must be empty).
2. TGA format (032f463): CTP2 wants 16-bit TGAs as ARGB1555, descriptor byte
   (offset 17)=1 + TGA-2.0 footer (AE 160x120=38444B). desc=0 -> alpha read as 0 ->
   fill blits transparent -> unpainted surface -> heap-garbage static. Match AE per
   texture family (advance-icons upap* are desc=0 — do NOT blanket-force one value).
3. CRLF (7b7ecf2): stray `\r` in engine-parsed string files breaks lookups; keep
   gl_str/tips_str/civ_str/civilisation LF (.gitattributes eol=lf).

**Why:** I burned a whole session treating it as one texture bug (24bpp, loose UI
overrides, patch_ctp2_images placeholders — all red herrings) before the commit history
named all three. KEY trap: a PARTIAL fix still shows full static on a clean restart — the
DB fix alone did NOT clear the banner (user always full-restarts; it is NOT a texture-cache
effect — I wrongly inferred that). Each correct fix in a compound bug looks like a failure
until the last one lands, so fix all three surfaces before judging a hypothesis wrong.

**How to apply:** `git log --grep=fugl` FIRST, then fix ALL three surfaces before concluding.
See [[mom-gamefile-manifest]], [[mom-canonical-toolchain]], [[mom-sprite-pipeline]].
