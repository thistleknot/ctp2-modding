"""Populate proxy art for every csv-defined entity missing its own icon TGA.

Purpose:
    Merged super-mods pull in units/advances/improvements that have no icon art
    on disk, so the generator falls back to the UPLG001 placeholder (ugly grey
    box). This borrows real art: for each entity whose ICON_<X>.tga is absent
    from the scenario pictures dir, copy a deterministic proxy from the same
    dimension's real-art pool, named exactly as the generator expects
    (sanitize(name)). Run AFTER copying the base scenario, BEFORE ctp2_generator
    — the generator's icon reconcile then points at the now-present TGA.

    Deterministic (sorted target -> sorted pool round-robin) so a regen is
    byte-stable. Entities that already have real art are skipped, so a base mod
    whose visible entities all ship art (e.g. MoM) gets zero proxies.

Usage:
    assign_proxy_art.py --scenario <scen0000 dir> --csv <merged csv dir>

Desc-byte guard: proxies are copied verbatim from already-normalized source
TGAs (desc byte 0x00), so the GL SourceList crash guard is preserved.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
from pathlib import Path

DIMENSIONS = (
    ("units.csv", "UNIT_", "ICON_UNIT_"),
    ("advances.csv", "ADVANCE_", "ICON_ADVANCE_"),
    ("improvements.csv", "IMPROVE_", "ICON_IMPROVE_"),
)


def sanitize(name: str) -> str:
    """Identifier sanitizer — MUST match ctp2_generator.sanitize exactly."""
    s = name.upper().replace(" ", "_").replace("'", "").replace("-", "_")
    return re.sub(r"[^A-Z0-9_]", "", s)


def pool_for(pictures: Path, icon_prefix: str) -> list[Path]:
    """Real TGAs already on disk for this dimension, sorted for determinism."""
    hits = [p for p in pictures.iterdir()
            if p.is_file() and p.name.upper().startswith(icon_prefix)
            and p.suffix.lower() == ".tga"]
    return sorted(hits, key=lambda p: p.name.upper())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    args = parser.parse_args()
    pictures = args.scenario / "default" / "graphics" / "pictures"
    if not pictures.exists():
        raise SystemExit(f"no pictures dir under {args.scenario}")

    total_proxied = 0
    for fname, prefix, icon_prefix in DIMENSIONS:
        csv_path = args.csv / fname
        if not csv_path.exists():
            continue
        pool = pool_for(pictures, icon_prefix)
        if not pool:
            print(f"  [skip] {icon_prefix}: no real-art pool to borrow from")
            continue

        # Existing target ids on disk (skip — real or already-proxied art).
        have = {p.name.upper() for p in pictures.iterdir() if p.is_file()}
        with csv_path.open(newline="", encoding="utf-8-sig") as fh:
            names = [r["name"].strip() for r in csv.DictReader(fh)
                     if (r.get("name") or "").strip()]

        missing = []
        for name in sorted(set(names)):
            tga = f"{icon_prefix}{sanitize(name)}.tga"
            if tga.upper() not in have:
                missing.append(tga)

        for i, tga in enumerate(missing):
            donor = pool[i % len(pool)]
            shutil.copy2(donor, pictures / tga)
            total_proxied += 1
        print(f"  {icon_prefix}: {len(missing)} proxied from {len(pool)} real art(s)")

    print(f"proxy art: {total_proxied} icon(s) borrowed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
