#!/usr/bin/env python3
"""
Validate protected CTP2 base assets against the protected manifests.

Require:
- Run from the Call To Power 2 workspace root or invoke this file directly.
- protected_files_manifest.tsv and ctp_program_manifest.tsv exist beside this script.
- The current workspace is a git worktree.

Guarantee:
- Reports missing protected files, hash mismatches, extra program files, MoM
  scenario shadows, and unstaged/untracked protected changes.
- Exits non-zero if the protected surface is not commit-ready.

Failure modes:
- Missing manifest or git command failure raises immediately.
- Missing files, hash mismatches, extra program files, scenario shadows, or
  unstaged protected files return exit code 1 with exact counts.
"""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "protected_files_manifest.tsv"
CTP_PROGRAM_MANIFEST_PATH = ROOT / "ctp_program_manifest.tsv"
LDL_MISSING_ALLOWLIST_PATH = ROOT / "ldl_missing_tga_allowlist.tsv"
PROTECTED_ROOT = ROOT / "ctp2_data" / "default" / "graphics" / "pictures"
CTP_PROGRAM_ROOT = ROOT / "ctp2_program" / "ctp"
LAYOUT_ROOTS = (
    ROOT / "ctp2_data" / "default" / "uidata" / "layouts",
    ROOT / "ctp2_data" / "english" / "uidata" / "layouts",
)
MOM_SHADOW_ROOT = (
    ROOT
    / "Scenarios"
    / "mom"
    / "scen0000"
    / "default"
    / "graphics"
    / "pictures"
)


def sha1_file(path: Path) -> str:
    """Return the SHA1 digest for a file."""
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_manifest(path: Path) -> list[dict[str, str]]:
    """Load the protected file manifest."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_tga_allowlist(path: Path) -> set[str]:
    """Load documented LDL TGA references allowed to be absent as loose files."""
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            row["relative_path"].lower()
            for row in csv.DictReader(handle, delimiter="\t")
            if row.get("relative_path")
        }


def scan_ldl_tga_references(layout_roots: tuple[Path, ...]) -> set[str]:
    """Return lower-case TGA filenames referenced by stock LDL layout files."""
    refs: set[str] = set()
    pattern = re.compile(r'"([^"]+\.tga)"', re.IGNORECASE)
    for layout_root in layout_roots:
        if not layout_root.exists():
            continue
        for path in layout_root.glob("*.ldl"):
            text = path.read_text(encoding="cp1252", errors="replace")
            for match in pattern.finditer(text):
                refs.add(Path(match.group(1)).name.lower())
    return refs


def git_porcelain() -> list[str]:
    """Return git porcelain status lines for the workspace."""
    result = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def protected_status_lines(status_lines: list[str]) -> list[str]:
    """Filter git status lines to protected assets and guardrail files."""
    protected_prefix = "ctp2_data/default/graphics/pictures/"
    ctp_program_prefix = "ctp2_program/ctp/"
    guardrails = {
        "ctp_program_manifest.tsv",
        "HARNESS.md",
        "PROTECTED_FILES.md",
        "ldl_missing_tga_allowlist.tsv",
        "protected_files_manifest.tsv",
        "verify_protected_files.py",
    }
    selected: list[str] = []
    for line in status_lines:
        path = line[3:].replace("\\", "/")
        if (
            path.startswith(protected_prefix)
            or path.startswith(ctp_program_prefix)
            or path in guardrails
        ):
            selected.append(line)
    return selected


def unstaged_or_untracked(lines: list[str]) -> list[str]:
    """Return protected status lines that are not staged for commit."""
    failures: list[str] = []
    for line in lines:
        index_status = line[0]
        worktree_status = line[1]
        if line.startswith("??") or worktree_status != " " or index_status == " ":
            failures.append(line)
    return failures


def current_relative_files(root: Path) -> set[str]:
    """Return lower-case relative file paths currently present below root."""
    if not root.exists():
        return set()
    return {
        path.relative_to(root).as_posix().lower()
        for path in root.rglob("*")
        if path.is_file()
    }


def main() -> int:
    """Validate the protected asset surface and commit readiness."""
    rows = load_manifest(MANIFEST_PATH)
    ctp_program_rows = load_manifest(CTP_PROGRAM_MANIFEST_PATH)
    manifest_names = {row["relative_path"].lower() for row in rows}
    ctp_program_names = {
        row["relative_path"].replace("\\", "/").lower() for row in ctp_program_rows
    }
    allowlist = load_tga_allowlist(LDL_MISSING_ALLOWLIST_PATH)
    missing: list[str] = []
    hash_mismatches: list[str] = []
    mom_shadows: list[str] = []
    missing_ldl_refs: list[str] = []
    ctp_program_missing: list[str] = []
    ctp_program_hash_mismatches: list[str] = []
    ctp_program_extra: list[str] = []

    for row in rows:
        rel = row["relative_path"]
        expected_sha1 = row["sha1"].upper()
        protected_path = PROTECTED_ROOT / rel
        if not protected_path.exists():
            missing.append(rel)
            continue
        if sha1_file(protected_path) != expected_sha1:
            hash_mismatches.append(rel)
        if (MOM_SHADOW_ROOT / rel).exists():
            mom_shadows.append(rel)

    for row in ctp_program_rows:
        rel = row["relative_path"]
        expected_sha1 = row["sha1"].upper()
        ctp_program_path = CTP_PROGRAM_ROOT / rel
        if not ctp_program_path.exists():
            ctp_program_missing.append(rel)
            continue
        if sha1_file(ctp_program_path) != expected_sha1:
            ctp_program_hash_mismatches.append(rel)

    ctp_program_extra = sorted(current_relative_files(CTP_PROGRAM_ROOT) - ctp_program_names)

    for ref in sorted(scan_ldl_tga_references(LAYOUT_ROOTS)):
        if (PROTECTED_ROOT / ref).exists():
            continue
        if ref in manifest_names:
            missing_ldl_refs.append(ref)
            continue
        if ref not in allowlist:
            missing_ldl_refs.append(ref)

    protected_git_lines = protected_status_lines(git_porcelain())
    unstaged = unstaged_or_untracked(protected_git_lines)

    print(f"protected_manifest_entries={len(rows)}")
    print(f"ctp_program_manifest_entries={len(ctp_program_rows)}")
    print(f"missing_files={len(missing)}")
    print(f"hash_mismatches={len(hash_mismatches)}")
    print(f"mom_shadow_files={len(mom_shadows)}")
    print(f"ctp_program_missing_files={len(ctp_program_missing)}")
    print(f"ctp_program_hash_mismatches={len(ctp_program_hash_mismatches)}")
    print(f"ctp_program_extra_files={len(ctp_program_extra)}")
    print(f"missing_nonallowlisted_ldl_tga_refs={len(missing_ldl_refs)}")
    print(f"unstaged_or_untracked_protected_files={len(unstaged)}")

    for label, values in (
        ("missing", missing),
        ("hash_mismatch", hash_mismatches),
        ("mom_shadow", mom_shadows),
        ("ctp_program_missing", ctp_program_missing),
        ("ctp_program_hash_mismatch", ctp_program_hash_mismatches),
        ("ctp_program_extra", ctp_program_extra),
        ("missing_ldl_ref", missing_ldl_refs),
        ("unstaged_or_untracked", unstaged),
    ):
        for value in values[:50]:
            print(f"{label}: {value}")
        if len(values) > 50:
            print(f"{label}: ... {len(values) - 50} more")

    if (
        missing
        or hash_mismatches
        or mom_shadows
        or ctp_program_missing
        or ctp_program_hash_mismatches
        or ctp_program_extra
        or missing_ldl_refs
        or unstaged
    ):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
