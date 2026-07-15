"""Faction/sphere-gate units — build the reviewable taxonomy and set prereqs.

Purpose:
    Replaces flat cost-tiering with FACTION identity. Each unit is assigned a
    magic sphere (life/nature/death/chaos/sorcery) or 'neutral', inferred from
    its creature type and overridden by explicit design assignments. It then
    gates on that sphere's advance ladder at a tier derived from cost:
    LORE (cheap) -> ADEPT -> MAGE -> WIZARD -> MASTER (elite). So a Nature tribe
    researching Nature magic unlocks its Fae units, Death unlocks undead, etc.

    Writes TWO things:
      1. unit_factions.csv  — the reviewable taxonomy control plane
         (unit_id, name, cost, sphere, tier, gate_code, gate_advance). Edit
         'sphere'/'tier' here to correct the seed; re-run preserves edits.
      2. units.csv prereq   — set to the sphere-ladder gate code.

    Runs post-mask, pre-generator. Units with a real non-sphere prereq
    (MoM heroes on Mys) and neutral/starter units (cost <= STARTER) keep it.

Usage:
    assign_unit_factions.py --csv <merged csv dir>
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

NO_PREREQ = {"no", "nil", ""}
STARTER_COST = 2  # <= this stays turn-1 (WARRIOR_CODE), no sphere gate

# Sphere ladder -> gate code per tier (from advance_code_map, unit lane).
# All ladders are AGE_TWO; tier within the ladder sets how deep you research.
SPHERE_LADDER = {
    "life":    {"lore": "Inv", "adept": "Lab", "mage": "Las", "wizard": "Too", "master": "Mag"},
    "nature":  {"lore": "Plu", "adept": "PT",  "mage": "Rad", "wizard": "Rec", "master": "Ref"},
    "death":   {"lore": "Rfg", "adept": "Rob", "mage": "SFl", "wizard": "Sth", "master": "SE"},
    "chaos":   {"lore": "MP",  "adept": "Med", "mage": "Met", "wizard": "Min", "master": "Mob"},
    "sorcery": {"lore": "The", "adept": "X2",  "mage": "NP",  "wizard": "Phy", "master": "Pla"},
}
TIER_ORDER = ["lore", "adept", "mage", "wizard", "master"]

# Creature-type -> sphere inference (first match wins; order matters).
SPHERE_KEYWORDS = [
    ("death",   ["skeleton", "zombie", "wraith", "undead", "bone", "ghoul",
                 "vampire", "lich", "wight", "necro", "shade", "minion",
                 "death", "malleus", "rjak", "barrow", "mummy"]),
    ("nature",  ["centaur", "elf", "elven", "halfling", "sprite", "faerie",
                 "unicorn", "pegasus", "griffin", "treant", "dryad", "faun",
                 "warbear", "cockatrice", "wolf", "hawk", "bear", "boar",
                 "great wyrm", "behemoth", "mammoth", "gnome"]),
    ("chaos",   ["goblin", "efreet", "salamander", "hell", "chaos", "orc",
                 "troll", "hydra", "warrax", "tauron", "hound", "fire",
                 "demon", "infernal", "gargoyle", "minotaur", "fanatic",
                 "dragon"]),   # dragons -> chaos MASTER placeholder (see DRAGONS)
    ("life",    ["angel", "archangel", "paladin", "priest", "cleric", "healer",
                 "guardian", "serena", "ariel", "alorra", "monk", "crusader",
                 "templar", "knight hosp"]),
    ("sorcery", ["elemental", "phantom", "storm", "djinn", "genie", "jafar",
                 "warlock", "sorcer", "air ", "water", "earth", "wind",
                 "merman", "merfolk", "porpoise", "galley", "frigate",
                 "galleon", "transport", "ironclad", "warship"]),
]

# Explicit design overrides (user-directed). name-substring -> sphere.
EXPLICIT = {
    "centaur": "nature", "halfling": "nature", "elf warrior": "nature",
    "goblin": "chaos",       # barbarian-aligned -> chaos ladder for now
    "skeleton": "death",
}


def sanitize(name: str) -> str:
    s = name.upper().replace(" ", "_").replace("'", "").replace("-", "_")
    return re.sub(r"[^A-Z0-9_]", "", s)


def cost_num(v: str) -> int:
    return int(re.sub(r"[^0-9]", "", str(v)) or 0)


def infer_sphere(name: str) -> str:
    low = name.lower()
    for key, sphere in EXPLICIT.items():
        if key in low:
            return sphere
    for sphere, kws in SPHERE_KEYWORDS:
        if any(k in low for k in kws):
            return sphere
    return "neutral"


def cost_to_tier(cost: int) -> str:
    if cost <= 4:   return "lore"
    if cost <= 8:   return "adept"
    if cost <= 15:  return "mage"
    if cost <= 40:  return "wizard"
    return "master"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    args = parser.parse_args()
    csv_dir = args.csv

    # Preserve prior taxonomy edits.
    tax_path = csv_dir / "unit_factions.csv"
    prior: dict[str, dict[str, str]] = {}
    if tax_path.exists():
        with tax_path.open(newline="", encoding="utf-8-sig") as fh:
            prior = {r["unit_id"]: r for r in csv.DictReader(fh)}

    upath = csv_dir / "units.csv"
    with upath.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames
        rows = list(reader)

    tax_rows = []
    from collections import Counter
    counts = Counter()
    for r in rows:
        name = (r.get("name") or "").strip()
        if not name:
            continue
        uid = "UNIT_" + sanitize(name)
        cost = cost_num(r.get("cost", "0"))
        prereq = (r.get("prereq") or "").strip().lower()

        source = r.get("source", "")
        edit = prior.get(uid, {})
        inferred = edit.get("sphere") or infer_sphere(name)
        # BASE (curated MoM) units keep their prereq verbatim — MoM's hero
        # gating (Mys) and tech placement are intentional. Only MERGED-source
        # units are (re)gated by sphere, overriding whatever civ2 code they
        # arrived with (e.g. Minotaur's 'War' -> Chaos).
        if source == "base" or (prereq not in NO_PREREQ and inferred == "neutral"):
            sphere = edit.get("sphere", "base" if source == "base" else "gated")
            tier = ""
            gate_code = r.get("prereq", "")
        else:
            sphere = inferred
            # dragons are elite/event units regardless of cost -> MASTER tier
            tier = edit.get("tier") or ("master" if "dragon" in name.lower()
                                        else cost_to_tier(cost))
            if sphere in SPHERE_LADDER:
                # Faction units ALWAYS gate on their sphere (LORE minimum),
                # even cheap ones — that IS the faction identity. A Death
                # tribe's basic skeleton requires Death Lore.
                gate_code = SPHERE_LADDER[sphere].get(tier, SPHERE_LADDER[sphere]["lore"])
                r["prereq"] = gate_code
            elif cost <= STARTER_COST:
                # generic neutral starter (Peasants, Spearmen) -> WARRIOR_CODE
                sphere = "starter"
                gate_code = ""
            else:
                sphere = "neutral"
                gate_code = ""
            counts[sphere] += 1

        gate_adv = ""
        tax_rows.append({"unit_id": uid, "name": name, "cost": str(cost),
                         "sphere": sphere, "tier": tier, "gate_code": gate_code,
                         "gate_advance": gate_adv, "source": r.get("source", "")})

    with upath.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, lineterminator="\r\n", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

    tax_header = ["unit_id", "name", "cost", "sphere", "tier", "gate_code", "gate_advance", "source"]
    with tax_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=tax_header, lineterminator="\r\n", extrasaction="ignore")
        w.writeheader(); w.writerows(tax_rows)

    print(f"unit_factions.csv: {len(tax_rows)} units")
    print("gated by sphere:", dict(counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
