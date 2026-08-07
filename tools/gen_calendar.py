"""gen_calendar.py — Own the game calendar: DiffDB TIME_SCALE + Const END_OF_GAME_YEAR.

SHAPE (years per turn per difficulty tier) comes from calendar_periods.csv.
PACE comes from mod_policy.json calendar.turns_target.

Target game lengths by difficulty: Beginner=800 .. Impossible=1500 turns.
Per calendar_mapping.xlsx design doc.
"""
import re
from pathlib import Path


def calendar_periods(policy_csv_rows) -> dict[int, list[tuple[int, int]]]:
    """Load calendar_periods.csv into {tier: [(start_turn, years_per_turn), ...]}."""
    tiers: dict[int, list[tuple[int, int]]] = {}
    for row in policy_csv_rows("calendar_periods.csv"):
        if not (row.get("tier") or "").strip():
            continue
        tier = int(row["tier"])
        start = int(row["start_turn"])
        ypt = int(row["years_per_turn"])
        if ypt < 1:
            raise SystemExit(
                f"calendar_periods.csv: tier {tier} start_turn {start} has "
                f"years_per_turn {ypt}; must be >= 1")
        tiers.setdefault(tier, []).append((start, ypt))
    if sorted(tiers) != list(range(6)):
        raise SystemExit(
            f"calendar_periods.csv: expected tiers 0-5, got {sorted(tiers)}")
    for tier, periods in tiers.items():
        periods.sort()
        if periods[0][0] != 0:
            raise SystemExit(
                f"calendar_periods.csv: tier {tier} has no start_turn 0 row")
        starts = [p[0] for p in periods]
        if len(set(starts)) != len(starts):
            raise SystemExit(
                f"calendar_periods.csv: tier {tier} has duplicate start_turns")
    return tiers


def calendar_end_turn(periods: list[tuple[int, int]], end_year: int,
                      start_year: int, cap: int = 20000) -> int:
    """First turn on which the calendar has reached end_year."""
    year = start_year
    ypt = periods[0][1]
    for turn in range(cap):
        for start, per_turn in periods:
            if start <= turn:
                ypt = per_turn
        if year >= end_year:
            return turn
        year += ypt
    return cap


def calendar_year_at(periods: list[tuple[int, int]], turns: int,
                     start_year: int) -> int:
    """Calendar year reached after advancing `turns` turns from start_year."""
    year = start_year
    ypt = periods[0][1]
    for turn in range(turns):
        for start, per_turn in periods:
            if start <= turn:
                ypt = per_turn
        year += ypt
    return year


def write_calendar(mod_policy: dict, scenario: Path, read_rel, write_rel,
                   policy_csv_rows) -> dict[str, int]:
    """Rewrite DiffDB TIME_SCALE blocks and Const END_OF_GAME_YEAR.

    Returns dict with end_year, reference_tier, and end_turn_tier_N for each tier.
    """
    policy = mod_policy.get("calendar")
    if not policy:
        raise SystemExit("mod_policy.json: missing 'calendar' block")
    start_year = int(policy["start_year"])
    ref_tier = int(policy["reference_tier"])
    turns_target = int(policy["turns_target"])
    warn_gap = int(policy["early_warning_years_before_end"])

    tiers = calendar_periods(policy_csv_rows)
    if ref_tier not in tiers:
        raise SystemExit(
            f"mod_policy calendar.reference_tier {ref_tier} has no rows in "
            f"calendar_periods.csv")

    end_year = calendar_year_at(tiers[ref_tier], turns_target, start_year)

    # --- DiffDB TIME_SCALE blocks ---
    rel = "default/gamedata/DiffDB.txt"
    text = read_rel(rel)
    block_re = re.compile(r"(?ms)^TIME_SCALE\{\n.*?^\}")
    seen = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal seen
        tier = seen
        seen += 1
        periods = tiers[tier]
        lines = [
            "TIME_SCALE{",
            f"\tSTART_YEAR\t{start_year}",
            f"\tNUM_PERIODS\t{len(periods)}",
        ]
        for start, ypt in periods:
            lines += ["\tPERIOD {",
                      f"\t\tSTART_TURN\t{start}",
                      f"\t\tYEARS_PER_TURN\t{ypt}",
                      "\t}"]
        lines += ["\tNEGATIVE_YEAR_FORMAT BC_YEAR_FORMAT",
                  "\tPOSITIVE_YEAR_FORMAT AD_YEAR_FORMAT",
                  "}"]
        return "\n".join(lines)

    new_text = block_re.sub(_replace, text)
    if seen != 6:
        raise SystemExit(
            f"{rel}: expected 6 TIME_SCALE blocks, found {seen}")

    path = scenario / rel
    if not path.exists() or path.read_text(encoding="latin-1") != new_text:
        write_rel(rel, new_text)

    # --- Const.txt END_OF_GAME_YEAR ---
    const_rel = "default/gamedata/Const.txt"
    const_text = read_rel(const_rel)
    for key, value in (("END_OF_GAME_YEAR", end_year),
                       ("END_OF_GAME_YEAR_EARLY_WARNING", end_year - warn_gap)):
        const_text, hits = re.subn(
            rf"(?m)^({re.escape(key)}\s+)-?\d+$",
            lambda m, v=value: f"{m.group(1)}{v}",
            const_text)
        if hits != 1:
            raise SystemExit(
                f"{const_rel}: expected exactly one {key} line, found {hits}")
    const_path = scenario / const_rel
    if not const_path.exists() or const_path.read_text(encoding="latin-1") != const_text:
        write_rel(const_rel, const_text)

    result = {"end_year": end_year, "reference_tier": ref_tier}
    for tier in sorted(tiers):
        result[f"end_turn_tier_{tier}"] = calendar_end_turn(
            tiers[tier], end_year, start_year)
    return result
