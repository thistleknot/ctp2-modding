"""Run the MOO unit transformation through CTPEd and publish a passing result.

Stage | Mechanism | Tag | Requirements
-------|-----------|-----|-------------
STAGE | Copy the current scenario and run the generator twice in isolation | [mandatory] | R1-R2
WORKBOOKS | Build named-Entry rules and Excel formula expectations from CSV/policy | [mandatory] | R3-R5
TRANSFORM | Recalculate Excel caches and apply CTPEd rules to staged Units.txt | [mandatory] | R6-R8
VALIDATE | Run mod validators against the live baseline and compare staged outputs | [mandatory] | R9-R10,R18
PUBLISH | Atomically replace the generated Units.txt after all gates pass | [mandatory] | R11
MOM QA | Stage MoM generator output, run CTPEd + Excel, validate, and publish only Units.txt | [mandatory] | R17-R18

R1. When build is called, the active mod shall be `moo` and the scenario shall exist.
R2. When generator output is produced, it shall be written under a disposable sibling staging directory.
R3. When a MOO unit row is read, the pipeline shall resolve one matching Entry by its generated UNIT identifier.
R4. When a targeted rule is written, it shall carry the Civ2 cost as InputValue and the policy formula as Operand.
R5. When an expectation is written, its Excel formula shall calculate from the same mapped cost and policy constants.
R6. When the expectation workbook is recalculated, Excel shall save cached scalar values before CTPEd reads it.
R7. When CTPEd applies the rules, it shall compare all targeted results and publish an overlay only on a full match.
R8. When the overlay is merged, it shall contain only `default/gamedata/Units.txt`.
R9. When MOO validators run, they shall target the staged scenario.
R10. If any generated path other than Units.txt differs from the live scenario, then publication shall stop.
R11. When all gates pass, the pipeline shall atomically replace only the live Units.txt file.
R12. When the MoM command runs, the generator shall target an isolated scenario copy and preserve every non-Units.txt live path.
R13. When MoM unit rows are read, the rules shall use `unit_stat_scaling` and the `unit_roles.vessels` zero-value decision.
R14. When MoM QA passes, CTPEd's output shall match the Excel cached expectations for all mapped units.
R15. When MoM validators run, they shall compare the candidate's failure signatures with the live baseline.
R16. When MoM publication completes, only `default/gamedata/Units.txt` shall replace the live file.

CLOSED
- The current generator output is the baseline input tree; only the CTPEd QA overlay may alter MOO ShieldHunger values.
- Excel is run hidden through COM to recalculate formulas; missing Excel or caches stop the build.
- The pipeline does not change MOO scenario files before successful formula comparison and validation.

Preconditions: Windows Excel automation, openpyxl, CTPEd source descriptors, and the MOO CSV/policy are available.
Failures: generator, parser, formula, QA, validation, or diff failures leave the published scenario unchanged.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

from openpyxl import Workbook

import modpaths


TARGET_HEADERS = (
    "StructureFile", "EntryName", "FieldPath", "InputValue", "Operation", "Operand"
)
QA_HEADERS = ("StructureFile", "EntryOrdinal", "FieldPath", "Expected")


def _sanitize_unit_name(name: str) -> str:
    """Return the generator's canonical uppercase unit identifier suffix.

    Require: name is the display name from units.csv.
    Guarantee: return the same sanitized token used by ctp2_generator.
    Maintain: apply only the generator's documented punctuation rules.
    Assert: the result contains letters, digits, and underscores only.
    """
    value = name.upper().replace(" ", "_").replace("'", "").replace("-", "_")
    return re.sub(r"_+", "_", re.sub(r"[^A-Z0-9_]", "", value)).strip("_")


def _recalculate_excel(path: Path) -> None:
    """Recalculate and save cached formula results using installed Excel.

    Require: path is a valid .xlsx workbook and Excel COM is registered.
    Guarantee: save workbook formula caches before CTPEd reads them.
    Maintain: keep Excel hidden and disable workbook macros.
    Assert: the workbook is closed and the Excel process is quit on completion.
    """
    import win32com.client

    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.AutomationSecurity = 3
    workbook = None
    try:
        workbook = excel.Workbooks.Open(str(path.resolve()), UpdateLinks=0, ReadOnly=False)
        excel.CalculateFullRebuild()
        workbook.Save()
    finally:
        if workbook is not None:
            workbook.Close(SaveChanges=False)
        excel.Quit()


def _unit_qa_policy(
    mod_name: str, policy: dict
) -> tuple[str, int, int, set[str], str, str]:
    """Return the ShieldHunger source contract for one mod.

    Require: mod policy contains the existing unit scaling contract.
    Guarantee: return source field, minimum, divisor, and literal-zero unit IDs.
    Maintain: preserve each mod's current policy values.
    Assert: minimum and divisor are positive integers.
    """
    if mod_name.casefold() == "moo":
        qa_policy = policy["ctped_transform_qa"]["unit_shield_hunger"]
        source_field = str(qa_policy["source_field"])
        minimum = int(qa_policy["minimum"])
        divisor = int(qa_policy["divisor"])
        field_path = str(qa_policy["field_path"])
        structure_file = str(qa_policy["structure_file"])
        zero_units: set[str] = set()
    elif mod_name.casefold() == "mom":
        scaling = policy["unit_stat_scaling"]
        qa_policy = policy["ctped_transform_qa"]["unit_shield_hunger"]
        source_field = str(qa_policy["source_field"])
        minimum = int(qa_policy["minimum"])
        divisor = int(qa_policy["divisor"])
        if (minimum, divisor) != (
            int(scaling["shield_hunger_min"]), int(scaling["shield_hunger_div"])
        ):
            raise ValueError("MoM CTPEd formula policy differs from unit_stat_scaling")
        field_path = "ShieldHunger"
        structure_file = "units.ces"
        zero_units = {str(name).casefold() for name in policy.get("unit_roles", {}).get("vessels", [])}
    else:
        raise ValueError(f"No ShieldHunger QA contract is defined for {mod_name}")
    if minimum < 1 or divisor < 1:
        raise ValueError(f"Invalid ShieldHunger formula policy for {mod_name}")
    return source_field, minimum, divisor, zero_units, structure_file, field_path


def _write_workbooks(
    rules_path: Path,
    qa_path: Path,
    source_rows: list[dict[str, str]],
    unit_file,
    policy: dict,
    mod_name: str,
) -> None:
    """Create CTPEd rule and Excel expectation workbooks for mapped units.

    Require: every non-stub source unit resolves to one parsed target Entry.
    Guarantee: write per-Entry mapped-input rules and matching Excel formulas.
    Maintain: derive values only from the active mod's units.csv and mod_policy.json.
    Assert: every rule has exactly one QA expectation.
    """
    source_field, minimum, divisor, zero_units, structure_file, field_path = _unit_qa_policy(
        mod_name, policy
    )
    expression = f"Math.max({minimum}, Math.floor(value / {divisor}))"
    qa_policy = policy["ctped_transform_qa"]["unit_shield_hunger"]
    if qa_policy["expression"] != expression:
        raise ValueError(
            f"{mod_name} ShieldHunger policy expression differs from its minimum/divisor"
        )
    if qa_policy["structure_file"] != structure_file or qa_policy["field_path"] != field_path:
        raise ValueError(f"{mod_name} CTPEd target differs from the unit QA contract")
    entry_ordinals: dict[str, int] = {}
    for ordinal, entry in enumerate(unit_file.entries, start=1):
        entry_ordinals.setdefault(entry.name.casefold(), ordinal)

    rules = Workbook()
    rules_sheet = rules.active
    rules_sheet.title = "Rules"
    rules_sheet.append(TARGET_HEADERS)
    qa = Workbook()
    qa_sheet = qa.active
    qa_sheet.title = "CTPEdQA"
    qa_sheet.append(QA_HEADERS)
    seen: set[str] = set()
    count = 0
    for row in source_rows:
        name = row.get("name", "").strip()
        if not name or name.casefold() == "blah" or (len(name) == 2 and name[0].upper() == "B" and name[1].isdigit()):
            continue
        ident = f"UNIT_{_sanitize_unit_name(name)}"
        key = ident.casefold()
        if key in seen:
            raise ValueError(f"MOO units.csv has duplicate unit identity {ident}")
        seen.add(key)
        ordinal = entry_ordinals.get(key)
        if ordinal is None:
            raise ValueError(f"Generated Units.txt is missing {ident}")
        cost = int(row[source_field].strip() or "0")
        if cost < 0:
            raise ValueError(f"{mod_name} unit {name} has a negative mapped cost")
        operation = "set" if ident.casefold() in zero_units else "formula"
        operand = "0" if operation == "set" else expression
        excel_formula = "=0" if operation == "set" else f"=MAX({minimum},ROUNDDOWN({cost}/{divisor},0))"
        rules_sheet.append((
            structure_file, ident, field_path, cost, operation, operand,
        ))
        qa_sheet.append((structure_file, ordinal, field_path, excel_formula))
        count += 1
    if count != len(seen) or not count:
        raise AssertionError("MOO target rule count is invalid")
    rules.save(rules_path)
    qa.save(qa_path)
    rules.close()
    qa.close()
    assert count == qa_sheet.max_row - 1


def _compare_scenario_trees(live: Path, staged: Path) -> tuple[Path, ...]:
    """Return every relative file whose presence or bytes differ.

    Require: live and staged are scenario directories on the same volume.
    Guarantee: list all changed relative file paths in stable order.
    Maintain: read files only and never compare timestamps.
    Assert: results are relative to the staged scenario root.
    """
    live_files = {path.relative_to(live) for path in live.rglob("*") if path.is_file()}
    staged_files = {path.relative_to(staged) for path in staged.rglob("*") if path.is_file()}
    changed = []
    for relative in sorted(live_files | staged_files):
        old = live / relative
        new = staged / relative
        if not old.is_file() or not new.is_file() or old.read_bytes() != new.read_bytes():
            changed.append(relative)
    return tuple(changed)


def _restore_non_target_paths(live: Path, staged: Path, target: Path) -> tuple[Path, ...]:
    """Restore generator-only changes outside the single approved target.

    Require: `staged` is an isolated generator output copied from `live`.
    Guarantee: all non-target file bytes and presence match `live`.
    Maintain: preserve the staged target file for CTPEd transformation.
    Assert: the scenario tree differs only at `target` after restoration.
    """
    restored: list[Path] = []
    for relative in _compare_scenario_trees(live, staged):
        if relative == target:
            continue
        baseline = live / relative
        candidate = staged / relative
        if baseline.is_file():
            candidate.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(baseline, candidate)
        elif candidate.exists():
            candidate.unlink()
        restored.append(relative)
    remaining = _compare_scenario_trees(live, staged)
    if any(path != target for path in remaining):
        raise AssertionError(f"non-target scenario paths remained changed: {remaining}")
    return tuple(restored)


def _assert_unit_fields_preserved(live_bytes: bytes, candidate_bytes: bytes) -> None:
    """Require unchanged unit identities and all non-target unit fields.

    Require: both byte strings are complete CTP2 Units.txt files.
    Guarantee: only ShieldHunger values and duplicate DeathEffectsHappy flags may differ.
    Maintain: compare normalized per-Entry lines while preserving order and duplicate multiplicity.
    Assert: every unit has the same non-target field sequence in both files.
    """
    entry_start = re.compile(r"^(UNIT_[A-Z0-9_]+)\s*\{\s*$")
    shield_field = re.compile(r"^ShieldHunger\s+", re.IGNORECASE)

    def parse(data: bytes, candidate: bool) -> dict[str, tuple[str, ...]]:
        text = data.decode("latin-1")
        entries: dict[str, tuple[str, ...]] = {}
        current_name: str | None = None
        current_lines: list[str] = []
        for line in text.splitlines():
            match = entry_start.match(line)
            if match:
                if current_name is not None:
                    raise ValueError(f"nested unit block before {match.group(1)}")
                current_name = match.group(1)
                current_lines = []
                continue
            if current_name is None:
                continue
            stripped = line.strip()
            if stripped == "}":
                if current_name in entries:
                    raise ValueError(f"duplicate Unit Entry {current_name}")
                normalized: list[str] = []
                happy_flags = sum(value == "DeathEffectsHappy" for value in current_lines)
                if candidate and current_name == "UNIT_PEASANTS" and happy_flags != 1:
                    raise ValueError(
                        f"candidate UNIT_PEASANTS must have one DeathEffectsHappy flag, found {happy_flags}"
                    )
                for value in current_lines:
                    if shield_field.match(value):
                        continue
                    if current_name == "UNIT_PEASANTS" and value == "DeathEffectsHappy":
                        continue
                    normalized.append(value)
                if current_name == "UNIT_PEASANTS":
                    normalized.append("DeathEffectsHappy")
                entries[current_name] = tuple(normalized)
                current_name = None
                current_lines = []
                continue
            current_lines.append(stripped)
        if current_name is not None:
            raise ValueError(f"unterminated Unit Entry {current_name}")
        return entries

    before = parse(live_bytes, candidate=False)
    after = parse(candidate_bytes, candidate=True)
    if before.keys() != after.keys():
        missing = sorted(before.keys() - after.keys())
        extra = sorted(after.keys() - before.keys())
        raise ValueError(f"Units.txt identity changes are forbidden; missing={missing}, extra={extra}")
    for name in before:
        if before[name] != after[name]:
            raise ValueError(f"Units.txt non-ShieldHunger fields changed for {name}")


def _validator_failures(output: str, exit_code: int) -> tuple[str, ...]:
    """Extract stable failure lines from the existing validators.

    Require: output and exit code come from a validator run on one scenario.
    Guarantee: return comparable failure signatures without scenario-root paths.
    Maintain: retain every concrete failure line and treat unknown failures as failures.
    Assert: a successful validator has no failure signatures.
    """
    failures = tuple(
        line.strip()
        for line in output.splitlines()
        if "[BAD]" in line or "[FAIL]" in line or line.strip().startswith("FAIL ")
    )
    if exit_code and not failures:
        failures = tuple(line.strip() for line in output.splitlines() if line.strip())
    if not exit_code and failures:
        raise AssertionError("validator returned failure diagnostics with a success exit code")
    return failures


def _run_baseline_comparison(
    script: Path,
    live: Path,
    staged: Path,
    environment: dict[str, str],
) -> None:
    """Reject new validator failures while allowing identical live-baseline failures.

    Require: live and staged scenarios are complete, isolated trees.
    Guarantee: each validator passes or reports the same failures on both trees.
    Maintain: validators receive explicit scenario roots and cannot mutate live data.
    Assert: differing failure signatures stop publication.
    """
    if script.name == "validate_scenario.py":
        command_for = lambda root: [sys.executable, str(script), "--scenario", str(root)]
    else:
        command_for = lambda _root: [sys.executable, str(script)]
    outcomes: dict[str, tuple[int, tuple[str, ...], str]] = {}
    for label, root in (("live baseline", live), ("staged candidate", staged)):
        current_environment = environment.copy()
        current_environment["CTP2_GENERATOR_SCENARIO_DIR"] = str(root)
        completed = subprocess.run(
            command_for(root),
            cwd=modpaths.TOOLS_DIR,
            env=current_environment,
            text=True,
            capture_output=True,
        )
        output = completed.stdout + completed.stderr
        failures = _validator_failures(output, completed.returncode)
        outcomes[label] = (completed.returncode, failures, output)
        if output:
            print(f"[{script.name}: {label}]\n{output.rstrip()}")
    baseline_code, baseline_failures, _ = outcomes["live baseline"]
    staged_code, staged_failures, _ = outcomes["staged candidate"]
    if staged_code and (not baseline_code or staged_failures != baseline_failures):
        raise RuntimeError(
            f"{script.name} found new staged failures: {staged_failures}; "
            f"live baseline is {baseline_failures}"
        )
    if staged_code:
        print(f"{script.name}: staged failures match the live baseline ({len(staged_failures)}).")


def build_moo() -> None:
    """Generate, transform, validate, then publish the MOO unit QA pilot.

    Require: `CTP2_MOD=moo`, source scenario, CSVs, policy, Excel, and CTPEd exist.
    Guarantee: publish a new Units.txt only after all QA and MOO checks pass.
    Maintain: stage all generation and overlays beside the live scenario.
    Assert: the only changed scenario path is default/gamedata/Units.txt.
    """
    if modpaths.MOD_NAME.casefold() != "moo":
        raise ValueError("set CTP2_MOD=moo before running ctpedit moo-build")
    live = modpaths.SCEN_DIR.resolve()
    mod_dir = modpaths.MOD_DIR.resolve()
    csv_root = modpaths.CSV_DIR.resolve()
    if not live.is_dir():
        raise FileNotFoundError(f"MOO scenario does not exist: {live}")
    policy = json.loads((csv_root / "mod_policy.json").read_text(encoding="utf-8"))
    if "ctped_transform_qa" not in policy:
        raise ValueError("MOO mod_policy.json has no ctped_transform_qa policy")
    stage_root = mod_dir / ".qa-staging"
    stage_root.mkdir(exist_ok=True)
    run_root = stage_root / uuid.uuid4().hex
    run_root.mkdir()
    staged = run_root / "scen0000"
    shutil.copytree(live, staged)
    ctped_root = modpaths.ROOT / "ctpedit"
    ctped_src = ctped_root / "src"
    if not ctped_src.is_dir():
        raise FileNotFoundError(f"CTPEd source tree is missing: {ctped_src}")
    sys.path.insert(0, str(ctped_src))
    from app import load_gamefile, resolve_project_structure_file

    environment = os.environ.copy()
    environment.update({
        "CTP2_MOD": "moo",
        "CTP2_GENERATOR_SCENARIO_DIR": str(staged),
        "CTP2_MOO_QA_STAGE": "1",
        "CTP2_SKIP_WORKBOOK_EXPORT": "1",
    })
    for _ in range(2):
        result = subprocess.run(
            [sys.executable, str(modpaths.TOOLS_DIR / "ctp2_generator.py")],
            cwd=modpaths.TOOLS_DIR,
            env=environment,
        )
        if result.returncode:
            raise RuntimeError(f"MOO generator failed with exit code {result.returncode}")

    allowed = Path("default") / "gamedata" / "Units.txt"
    restored = _restore_non_target_paths(live, staged, allowed)
    if restored:
        print(f"Restored {len(restored)} unrelated generator output(s) from the live scenario.")

    data_dir = staged / "default" / "gamedata"
    gamefile = data_dir / "gamefile.txt"
    shutil.copy2(modpaths.BASE_DIR / "gamedata" / "gamefile.txt", gamefile)
    template = ctped_root / ".private_samples" / "default.ced"
    structure_root = ctped_root / ".private_samples" / "Structure"
    document = load_gamefile(gamefile, template, structure_root, "default")
    unit_file = resolve_project_structure_file(document, "units.ces")
    if unit_file is None:
        raise ValueError("MOO Gamefile does not declare units.ces")
    with (csv_root / "units.csv").open(newline="", encoding="utf-8-sig") as handle:
        source_rows = list(csv.DictReader(handle))
    rules_path = run_root / "moo_unit_transform_rules.xlsx"
    qa_path = run_root / "moo_unit_transform_qa.xlsx"
    _write_workbooks(rules_path, qa_path, source_rows, unit_file, policy, "moo")
    _recalculate_excel(qa_path)
    overlay = run_root / "overlay"
    result = subprocess.run([
        sys.executable, str(ctped_src / "transform_api.py"), "apply",
        "--rules-workbook", str(rules_path),
        "--qa-workbook", str(qa_path),
        "--gamefile", str(gamefile),
        "--template", str(template),
        "--structure-root", str(structure_root),
        "--language", "default",
        "--output-directory", str(overlay),
    ])
    if result.returncode:
        raise RuntimeError(f"CTPEd QA failed with exit code {result.returncode}")
    relative = Path("default") / "gamedata" / "Units.txt"
    overlay_files = tuple(path.relative_to(overlay) for path in overlay.rglob("*") if path.is_file())
    if overlay_files != (relative,):
        raise ValueError(f"CTPEd overlay changed unexpected paths: {overlay_files}")
    shutil.copy2(overlay / relative, staged / relative)
    gamefile.unlink()
    _assert_unit_fields_preserved((live / relative).read_bytes(), (staged / relative).read_bytes())

    for validator in ("validate_all_surfaces.py", "validate_scenario.py"):
        _run_baseline_comparison(modpaths.TOOLS_DIR / validator, live, staged, environment)

    changed = _compare_scenario_trees(live, staged)
    if changed not in ((), (allowed,)):
        raise ValueError(f"MOO rebuild changed unexpected scenario paths: {changed}")

    from export_mod_workbook import export_workbook

    export_workbook(csv_root / "mod_inventory.xlsx", csv_root=csv_root)
    published_rules = csv_root / "moo_unit_transform_rules.xlsx"
    published_qa = csv_root / "moo_unit_transform_qa.xlsx"
    shutil.copy2(rules_path, published_rules)
    shutil.copy2(qa_path, published_qa)
    target = live / allowed
    if allowed in changed:
        os.replace(staged / allowed, target)
    shutil.rmtree(run_root)
    print(
        f"MOO ShieldHunger QA passed for {len(source_rows)} source unit rows; "
        f"{'published' if allowed in changed else 'already current'}: {target}."
    )


def build_mom() -> None:
    """Build MoM in staging, apply CTPEd ShieldHunger QA, publish changed outputs.

    Require: `CTP2_MOD=mom`, source CSVs, policy, generator, descriptors, and Excel exist.
    Guarantee: publish every generator output that changed or was added, with
    Units.txt carrying CTPEd's Excel-approved values; staged deletions are
    reported, never applied, so hand-kept untracked files cannot be lost.
    Maintain: generate, transform, and validate only an isolated scenario copy.
    Assert: all validators add no new failures and only approved Unit fields differ.

    NO GOVERNING SPEC. Basis: operator 2026-10-26 (Knights must need Swordsmen's
    tech). Publishing only Units.txt silently discarded every advances.csv edit,
    and `ctpedit patch` refuses to run while this QA is enabled.
    """
    if modpaths.MOD_NAME.casefold() != "mom":
        raise ValueError("set CTP2_MOD=mom before running ctpedit mom-build")
    live = modpaths.SCEN_DIR.resolve()
    csv_root = modpaths.CSV_DIR.resolve()
    policy_path = csv_root / "mod_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if "unit_stat_scaling" not in policy:
        raise ValueError("MoM policy is missing unit_stat_scaling")
    stage_root = modpaths.MOD_DIR.resolve() / ".qa-staging"
    stage_root.mkdir(exist_ok=True)
    run_root = stage_root / uuid.uuid4().hex
    run_root.mkdir()
    staged = run_root / "scen0000"
    shutil.copytree(live, staged)
    environment = os.environ.copy()
    environment.update({
        "CTP2_MOD": "mom",
        "CTP2_GENERATOR_SCENARIO_DIR": str(staged),
        "CTP2_MOM_QA_STAGE": "1",
        "CTP2_SKIP_WORKBOOK_EXPORT": "1",
    })
    for _ in range(2):
        generated = subprocess.run(
            [sys.executable, str(modpaths.TOOLS_DIR / "ctp2_generator.py")],
            cwd=modpaths.TOOLS_DIR,
            env=environment,
        )
        if generated.returncode:
            raise RuntimeError(f"MoM generator failed with exit code {generated.returncode}")

    relative = Path("default") / "gamedata" / "Units.txt"
    ctped_root = modpaths.ROOT / "ctpedit"
    ctped_src = ctped_root / "src"
    sys.path.insert(0, str(ctped_src))
    from app import load_gamefile, resolve_project_structure_file

    gamefile = staged / "default" / "gamedata" / "gamefile.txt"
    gamefile.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(modpaths.BASE_DIR / "gamedata" / "gamefile.txt", gamefile)
    template = ctped_root / ".private_samples" / "default.ced"
    structure_root = ctped_root / ".private_samples" / "Structure"
    document = load_gamefile(gamefile, template, structure_root, "default")
    unit_file = resolve_project_structure_file(document, "units.ces")
    if unit_file is None:
        raise ValueError("MoM Gamefile does not declare units.ces")
    with (csv_root / "units.csv").open(newline="", encoding="utf-8-sig") as handle:
        source_rows = list(csv.DictReader(handle))
    rules_path = run_root / "mom_unit_transform_rules.xlsx"
    qa_path = run_root / "mom_unit_transform_qa.xlsx"
    _write_workbooks(rules_path, qa_path, source_rows, unit_file, policy, "mom")
    _recalculate_excel(qa_path)
    overlay = run_root / "overlay"
    result = subprocess.run([
        sys.executable, str(ctped_src / "transform_api.py"), "apply",
        "--rules-workbook", str(rules_path),
        "--qa-workbook", str(qa_path),
        "--gamefile", str(gamefile),
        "--template", str(template),
        "--structure-root", str(structure_root),
        "--language", "default",
        "--output-directory", str(overlay),
    ])
    if result.returncode:
        raise RuntimeError(f"MoM CTPEd QA failed with exit code {result.returncode}")
    overlay_files = tuple(path.relative_to(overlay) for path in overlay.rglob("*") if path.is_file())
    if overlay_files != (relative,):
        raise ValueError(f"MoM CTPEd overlay changed unexpected paths: {overlay_files}")
    transformed = overlay / relative
    # Guard CTPEd's step only: compare against the generator's output, not the
    # live file, or every control-plane unit change (a new field, a new unit)
    # would be rejected as if CTPEd had made it.
    generated_units = (staged / relative).read_bytes()
    shutil.copy2(transformed, staged / relative)
    gamefile.unlink()
    _assert_unit_fields_preserved(generated_units, (staged / relative).read_bytes())

    for validator in ("validate_all_surfaces.py", "validate_scenario.py", "mom_audit.py"):
        _run_baseline_comparison(modpaths.TOOLS_DIR / validator, live, staged, environment)
    changed = _compare_scenario_trees(live, staged)

    shutil.copy2(rules_path, csv_root / "mom_unit_transform_rules.xlsx")
    shutil.copy2(qa_path, csv_root / "mom_unit_transform_qa.xlsx")
    published = []
    for path in changed:
        candidate = staged / path
        if candidate.is_file():
            (live / path).parent.mkdir(parents=True, exist_ok=True)
            os.replace(candidate, live / path)
            published.append(path)
            print(f"  published: {path}")
        else:
            print(f"  NOT deleted (staged build dropped it; remove by hand if intended): {path}")
    shutil.rmtree(run_root)
    print(
        f"MoM ShieldHunger QA passed for {len(source_rows)} source rows; "
        f"published {len(published)} changed output(s) to {live}."
    )

