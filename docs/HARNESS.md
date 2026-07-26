---
# MoM Modding Harness

This harness gates all MoM→CTP2 import changes through validation before commit.

---

## ⚠ AGENT RULES — READ FIRST

### Rule 1: All CTP2 Scenario Changes Go Through OpenCode CLI

**Agents (Copilot CLI, spawned sessions) MUST NOT directly edit scenario files.**
All changes to `Scenarios\mom\scen0000\**` must be issued as `opencode run` calls.
Direct `edit`/`create`/`view`+patch operations on scenario data files are forbidden.

```powershell
# Correct — route through OpenCode
Set-Location "H:\Program Files(x86)\Activision\Call To Power 2\Scenarios\mom\tools"
opencode run "<precise step-by-step task with exact commands>"

# Wrong — never do this
edit path: Scenarios\mom\scen0000\default\gamedata\Units.txt ...
```

**Exception:** top-level `.md` harness/documentation files (HARNESS.md, PROTECTED_FILES.md,
INTERCONNECTION_TRACKING.md, etc.) and upstream skill files may be edited directly by the agent.

### Rule 2: OpenCode Prompt Anti-Stall Rules

OpenCode **will stall or loop** if given a broad exploratory prompt. Always provide:
1. **Exact working directory** as the first line of the prompt
2. **Exact commands to run**, numbered, in order — no "explore first" steps
3. **No open-ended discovery** — never say "figure out which files", say exactly which file
4. **One tool call per step** — if step 1 output is needed for step 2, pass it inline as Python

**Stall pattern to avoid:**
> "Use the tools to figure out which units are non-MoM and then mask them"
→ OpenCode runs `--help` in a loop, never makes progress.

**Non-stall pattern:**
> "Run this exact Python one-liner: `python -c '...'`, then run `apply_masks.py --apply`, then run `mom_audit.py`"

### Rule 3: Never Modify Source Game or AE Files

All changes are **scenario-local only**: `Scenarios\mom\scen0000\**`.
Never touch `ctp2_data\**`, `ctp2_program\**`, or AE install files.
The only exception is restoring AE-baseline UI TGAs (see Protected Files Gate below).

---

## Unit Masking Workflow (Parser-Based)

**Canonical pipeline for masking non-MoM units across all dimensional txt files.**
Always use the parser tools — never edit txt files directly.

### CSV → UNIT_ID mapping

MoM units CSV: `Scenarios\mom\tools\momjr_csv\units.csv`
- Column `icon` = `ICON_UNIT_XXX` → strip prefix → `UNIT_XXX` is the game ID
- `UNIT_CITY` is engine-required — **never mask it**

### Step-by-step masking pipeline

```python
# Step 1: Compute non-MoM units (run inline via opencode)
import csv, subprocess, sys, re
sys.path.insert(0, '.')
with open('momjr_csv/units.csv') as f:
    mom_ids = set(
        'UNIT_' + r['icon'].replace('ICON_UNIT_', '')
        for r in csv.DictReader(f)
        if r.get('icon', '').startswith('ICON_UNIT_')
    )
units_txt = open('../scen0000/default/gamedata/Units.txt').read()
all_ids = set(re.findall(r'^(UNIT_\w+)\s*\{', units_txt, re.MULTILINE))
non_mom = sorted(all_ids - mom_ids - {'UNIT_CITY'})
print('Non-MoM units to mask:', len(non_mom))
for uid in non_mom:
    subprocess.run([sys.executable, 'mask_manager.py', 'mask', 'units', uid])
```

```powershell
# Step 2: Apply masks across all dimensional txt files
python apply_masks.py --apply

# Step 3: Validate
python mom_audit.py
```

### mask_manager.py CLI reference

```
python mask_manager.py mask   <dimension> <RECORD_ID>   # add to mask
python mask_manager.py unmask <dimension> <RECORD_ID>   # remove from mask
python mask_manager.py list   [dimension]               # show masked records
python mask_manager.py apply                            # generate override files
python mask_manager.py reset                            # clear all masks
```

Valid dimensions: `units`, `advances`, `improvements`, `wonders`, `tileimps`

### apply_masks.py CLI reference

```
python apply_masks.py           # preview (dry run)
python apply_masks.py --apply   # write changes to dimensional txt files
```

### Dimensional txt files affected by masking

| File | Location |
|---|---|
| `Units.txt` | `scen0000\default\gamedata\` |
| `uniticon.txt` | `scen0000\default\gamedata\` |
| `Units_historic.txt` | `scen0000\default\gamedata\` |
| `Units_release.txt` | `scen0000\default\gamedata\` |
| `Great_Library.txt` | `scen0000\english\gamedata\` |

---

## First-Class Protected Files Gate

Read `PROTECTED_FILES.md` before touching any CTP2 UI/image assets.

The protected base picture surface is:

```text
ctp2_data\default\graphics\pictures\**\*.tga
```

This surface must be restored from the manifest as a whole, not one named TGA
family at a time. The manifest includes the AE baseline plus LDL-required generated
closure files such as `uptg06a.tga` through `uptg06i.tga`. Before commit, run:

```powershell
python verify_protected_files.py
```

The commit is not ready unless the verifier reports zero missing files, zero hash
mismatches, zero MoM shadows, and zero unstaged/untracked protected files.

## Harness Flow

```
user_command (import Apprentice Mage)
    ↓
proposer (generate unit definition from spec)
    ↓
[validate against 3 critics]
    ├─ Critic 1: Grammar/Format
    ├─ Critic 2: Schema Consistency
    └─ Critic 3: Lessons Learned
    ↓
[if all critics pass → commit]
[if any critic fails → surface findings, iterate]
    ↓
[only ask user to test if harness passes]
```

## Coherence Sentinel

coherence = False

Status: In progress. Will flip to True once:
- [ ] All 3 critics successfully review a change
- [ ] Critic reports are structured and stored
- [ ] Changes persist through critic review
- [ ] User never tests broken code (harness gates it)

## Reference Documents (Critics Use These)

1. **wiki/grammar.md** — CTP2 file format constraints
2. **docs/lessons-learned/CTP2_Modding_Lessons.md** — parser errors, gating architecture
3. **Scenarios/AE_Mod/scen0000/** — reference schema for units, advances, buildings

## Critic 1: Grammar/Format Validator

Checks proposed change against wiki/grammar.md rules:
- Required vs optional fields for Units.txt
- Icon syntax in uniticon.txt (all 10 fields?)
- String ID format in gl_str.txt (tab-separated)
- Advance.txt structure (omit Prerequisites if zero-prereq)

Output: PASS/FAIL with specific violations

## Critic 2: Schema Consistency

Compares proposed change against AE_Mod reference:
- Unit: does it have all fields that AE_Mod units have?
- String IDs: are they properly registered?
- Icons: does icon exist in base game (reuse, not invent)?
- Advance prerequisites: valid references?

Output: PASS/FAIL with schema gaps

## Critic 3: Lessons Learned Alignment

Cross-checks against known failure modes from prior sessions:
- No invalid Action/Special fields (Apprentice Mage audit)
- No stray EnableBuild fields
- Icons registered before unit references them
- EnableAdvance pointing to real advances (not typos)
- Missing DESCRIPTION strings caught early
- For MoM advances, `ICON_ADVANCE_* not found in Icon database` is triaged against the scenario `uniticon.txt` proxy block before `advanceicon.txt`
- `ADVANCE_* not found in Advance database` is triaged against `Advance.txt` semantic closure, not icon files
- Distinct advances need distinct Great Library bundles in `uniticon.txt` and `english\gamedata\Great_Library.txt`; shared fallback GL IDs cause page collapse even when load succeeds
- Reused proxy art is acceptable during import passes; reused Great Library IDs are not
- Prove one vertical slice first, then patch the whole mismatch cluster for that dimension

### Building Removal Checklist (confirmed via IMPROVE_THEATER test + bulk AE cull)

`"X not found in Building database"` at load = a live `IMPROVE_X` reference exists somewhere.

**Step 1 — Full scenario scan (ALL file types — `.txt`, `.slc`, `.json`, etc.):**
```python
# Authoritative scan — catches any file type referencing a building key
import re, json
from pathlib import Path
manifest = json.loads(open('Scenarios/mom/ae_building_removal_manifest.json').read())
ae_keys = {b['key'] for b in manifest['buildings'] if b['classification']=='ae'}
for fpath in sorted(Path('Scenarios/mom').rglob('*')):
    if not fpath.is_file() or fpath.suffix in ('.db', '.tga', '.avi', '.wav', '.mp3'):
        continue
    try:
        txt = fpath.read_text(encoding='utf-8', errors='ignore')
    except:
        continue
    non_comment = '\n'.join(l for l in txt.splitlines()
                            if not l.strip().startswith('#') and not l.strip().startswith('//'))
    hits = [k for k in ae_keys if re.search(r'\b' + re.escape(k) + r'\b', non_comment)]
    if hits:
        for k in hits:
            for i, ln in enumerate(txt.splitlines(), 1):
                s = ln.strip()
                if not s.startswith('#') and not s.startswith('//') and re.search(r'\b' + re.escape(k) + r'\b', ln):
                    print(f'{fpath.name}:{i}: {ln.strip()}')
```

**Step 2 — ctp2_data files broad grep** (base-game files NOT overridden by scenario are still loaded):
Confirm that every ctp2_data file found has a matching scenario override. If not, create a scenario override.

Full scenario file list to clean atomically (**14 files + all SLC scripts** — expanded from original 10):

| File | Location | What to remove |
|---|---|---|
| `buildings.txt` | `default\gamedata\` | `IMPROVE_X { }` block |
| `uniticon.txt` | `default\gamedata\` | `ICON_IMPROVE_X { }` line |
| `improveicon.txt` | `default\gamedata\` | `ICON_IMPROVE_X` tab-delimited line (separate legacy icon file) |
| `feat.txt` | `default\gamedata\` | Any `FEAT_*` block whose content references `IMPROVE_X`. **Also check for orphaned closing `}` after block removal** — bulk removal leaves closing brace behind. |
| `Units.txt` | `default\gamedata\` | Any unit with `SettleBuilding IMPROVE_X` |
| `Wonder.txt` | `default\gamedata\` | Any `BuildingEverywhere` or `ActualBuildingEverywhere IMPROVE_X` line — comment it out, do NOT leave an empty block |
| `EndGameObjects.txt` | `default\gamedata\` | Any `ENDGAME_*` block with `Building IMPROVE_X`. Also remove any `PowerSource ENDGAME_X` back-reference in other blocks that pointed to the removed block. |
| `BuildingBuildLists.txt` | `default\aidata\` | `Building IMPROVE_X` line in any AI build list (scenario must have its OWN version — lives in aidata, not gamedata) |
| `Great_Library.txt` | `english\gamedata\` | All **8** GL section types: `_PREREQ`, `_STATISTICS`, `_GAMEPLAY`, `_HISTORICAL` (base) + `_WAW_PREREQ`, `_WAW_STATISTICS`, `_WAW_GAMEPLAY`, `_WAW_HISTORICAL` (WAW variants). Plus any advance `_STATISTICS` block with `<L:DATABASE_BUILDINGS,IMPROVE_X>`. **If IMPROVE_X was the ONLY `Gives:` entry, also remove the bare `Gives:` heading** — empty `Gives:\n[END]` crashes the GL parser. After removal, run Script A to confirm 0 orphaned sections. |
| `WAW_Great_Library.txt` | `english\gamedata\` | Same 8 GL section types. **MUST be written with CRLF** — LF drift causes wicker background. After any write, confirm bare-LF = 0. |
| `gl_str.txt` | `english\gamedata\` | Name string line (keys are **unquoted**: `IMPROVE_X\t\t"Name"`) |
| `junk_str.txt` | `english\gamedata\` | `DESCRIPTION_IMPROVE_X` line + `IMPROVE_X_PREREQ` line (keys are **unquoted**) |
| `tut2_str.txt` | `english\gamedata\` | Any `{BuildingDB(IMPROVE_X).Field}` SLIC expression — replace with static text |
| `tut2_main.slc` | `default\gamedata\` | Any `BuildingDB(IMPROVE_X)` in event handler conditions — replace condition with `if(0)`. **SLC is compiled at load time; a missing building key causes a SILENT CRASH with no error dialog.** |
| **All other `.slc` files** | `default\gamedata\` | Run the full-scan script (see Step 1, but use `rglob('*')` not `rglob('*.txt')`) to catch all file types |

**ctp2_data override status (confirmed):**
- `default\gamedata\buildings.txt`, `feat.txt`, `Units.txt`, `uniticon.txt`, `improveicon.txt`, `Wonder.txt`, `EndGameObjects.txt` — all overridden by scenario ✓
- `default\gamedata\Improve.txt` — NOT loaded when scenario provides `buildings.txt` (old format, replaced by buildings.txt) ✓
- `english\gamedata\gl_str.txt`, `Great_Library.txt`, `junk_str.txt`, `WAW_Great_Library.txt`, `tut2_str.txt` — overridden by scenario ✓
- **`default\aidata\BuildingBuildLists.txt` — scenario must maintain its own copy** (`Scenarios\mom\scen0000\default\aidata\BuildingBuildLists.txt`) and update it with every building removal

Mirror rule: `"ICON_IMPROVE_X not found in Icon database"` = building exists but icon entry was removed without removing the building. Always remove building + all icons + all GL refs atomically.

**Format gotchas:**

1. **GL `Gives:` entries use link syntax, not plain text.**
   In `Great_Library.txt` and `WAW_Great_Library.txt`, building references inside advance `_STATISTICS` blocks appear as:
   ```
   <L:DATABASE_BUILDINGS,IMPROVE_X>DisplayName<e>
   ```
   NOT as `Building IMPROVE_X`. Two removal cases:
   - Whole-line Gives: entry → remove the entire line.
   - Embedded prose link → strip the `<L:...>` and `<e>` tags, keeping display text.
   Scripts that look for `Building IMPROVE_X` in GL files will miss every reference.

2. **`junk_str.txt` and `gl_str.txt` keys are unquoted.**
   Correct format: `DESCRIPTION_IMPROVE_X\t\t\t"junkstring_..."` (key has NO surrounding quotes).
   Wrong regex: `^"DESCRIPTION_IMPROVE_X"` — matches nothing.
   Correct patterns: `^DESCRIPTION_{key}\b` and `^{key}_PREREQ\b` for junk_str; `^{key}\b` for gl_str.

3. **`WAW_Great_Library.txt` MUST be written with CRLF line endings.**
   LF drift causes the "wicker" background glitch across all GL pages.
   Always normalize CRLF→LF before processing, then convert LF→CRLF before writing.

4. **`feat.txt` bulk removal leaves orphaned closing braces.**
   When a script removes the content of a `FEAT_X { ... }` block, the final `}` is often left behind.
   Always verify no bare `}` lines remain after removal. Parser reports this as "missing open brace".

5. **`Wonder.txt` and `EndGameObjects.txt` are outside the standard 10-file set but hold live building refs.**
   `BuildingEverywhere`/`ActualBuildingEverywhere` in Wonder.txt and `Building` in EndGameObjects.txt
   are validated at load time. Comment out — do not leave empty blocks.

6. **SLC scripts with `BuildingDB(IMPROVE_X)` cause SILENT CRASHES — no error dialog.**
   CTP2 compiles `.slc` files at startup. A `BuildingDB()` call referencing a missing building key
   causes the game process to exit silently before the main menu appears.
   Fix: replace the condition with `if(0) { // IMPROVE_X removed - AE building culled`.
   Affected file in this scenario: `tut2_main.slc` (4 event handlers for CITY_WALLS, FOOD_SILO, SHRINE, BAZAAR).

7. **GL section removal scripts MUST handle `[END][SECTION_NAME]` combined lines.**
   MoM-added GL sections use `[END][SECTION_NAME]` on a single line (no newline between the close and the
   next section open). A removal script that only checks `if s == '[END]'` will treat these as section
   OPENS (not closes), causing depth to increment and consuming adjacent MoM sections silently.
   Fix pattern for removal scripts:
   ```python
   if s.startswith('[END]'):       # catches both '[END]' alone and '[END][NEXT_SECTION]'
       depth -= 1
       remainder = s[5:].strip()   # re-inject '[NEXT_SECTION]' part as next line if present
       if remainder:
           lines.insert(i, remainder)
   ```
   Fix pattern for verification scripts: scan for `[END][SECTION_NAME]` patterns in addition to
   standalone `[SECTION_NAME]` lines when checking which sections are present.

8. **`[END]` embedded at the end of a content line causes global wicker.**
   CTP2's GL parser reads sections line-by-line. If a line looks like:
   ```
   Some content text here.[END]
   ```
   the parser does NOT treat the trailing `[END]` as a section close — it reads the entire line as
   prose content. The section opened above it is never closed, and all subsequent GL sections
   are treated as nested content inside it → corrupts the parser → global wicker.
   **Fix**: move `[END]` to its own line, immediately after the content.
   **Detection**: `verify_all.py` Script E reports any `[END]` found mid-line as "WICKER RISK (WAW)".

9. **`improveicon.txt` fields are TAB-delimited, NOT quote-concatenated.**
   Correct format: `ICON_IMPROVE_X\t"front.tga"\t"anim.avi"\t"game.txt"\t"hist.txt"\t"prereq.txt"\t"variant.txt"\t"portrait.tga"\t"stats.txt"`
   Wrong format: `ICON_IMPROVE_X"front.tga""anim.avi"...` (no tabs)
   Without tabs the parser silently falls back to ICON_IMPROVE_DEFAULT for every entry it can't parse.
   Symptom: all buildings show the "modern machine" portrait with no error dialog.
   Check: `open('improveicon.txt','rb').read()` must contain `\t"` byte patterns in every non-comment entry.

10. **`improveicon.txt` TGA files must live in `ctp2_data\default\graphics\pictures\`, NOT the scenario pictures folder.**
    CTP2's building-icon loader does NOT walk the scenario-data path. TGAs referenced from `improveicon.txt` are
    looked up only in `ctp2_data\default\graphics\pictures\`. Placing them in
    `Scenarios\mom\scen0000\default\graphics\pictures\` causes CTP2 to silently fail to load every icon → all
    buildings disappear from the build queue → empty-list crash with no error dialog.
    The scenario pictures folder IS used by the GL texture system (upfg*.tga), but NOT by the icon loader.
    `build_mom_icons.py` PICS_DIR must point to `ctp2_data\default\graphics\pictures\`.

Output: PASS/FAIL with risk assessment

---

## Wicker Triage (GL Background Shows Basket-Weave Pattern)

Wicker = the GL renderer fell back to its "no image" pattern. Run these checks in order.

```
Step 1:  python verify_all.py
         → "WAW CRLF: N CRLF, 0 bare-LF"  — bare-LF > 0 = global wicker
         → "Script E — WAW section depth at EOF: 0" — depth ≠ 0 or inline [END] = global wicker

Step 2:  Check TGA image descriptor bytes for GL background tiles
         python -c "
         import struct
         for name in ['upfg500','upfg501','upfg502','uptg04e']:
             p = 'Scenarios/mom/scen0000/default/graphics/pictures/' + name + '.tga'
             raw = open(p,'rb').read()
             desc = raw[17]
             pix = struct.unpack_from('<H', raw, 18)[0] if len(raw) > 19 else 0
             bit15 = (pix >> 15) & 1
             print(f'{name}: desc=0x{desc:02X} (need 0x01), bit15={bit15} (need 0), px=0x{pix:04X}')
         "
         → desc must be 0x01 (NOT 0x20), bit15 must be 0

Step 3:  Check for duplicate GL section headers (causes global wicker)
         python -c "
         from pathlib import Path, collections
         for gl in ['Scenarios/mom/scen0000/english/gamedata/Great_Library.txt',
                    'Scenarios/mom/scen0000/english/gamedata/WAW_Great_Library.txt']:
             raw = Path(gl).read_bytes()
             lines = raw.split(b'\r\n')
             seen = {}
             for i, ln in enumerate(lines, 1):
                 s = ln.decode('cp1252', errors='replace').strip()
                 if s.startswith('[') and s.endswith(']') and not s.startswith('[END]'):
                     k = s[1:-1]
                     if k in seen:
                         print(f'DUPE in {Path(gl).name}: [{k}] at lines {seen[k]} and {i}')
                     else:
                         seen[k] = i
         "
         → Must print nothing

Step 4:  Verify GL background TGAs exist in scenario folder
         → Must have: upfg500.tga, upfg501.tga, upfg502.tga, uptg04e.tga
         → Missing = wicker for sections that need them

Step 5:  Verify UI progress-bar TGAs exist in scenario/base pictures
         → Must have: ug026.tga and ug027.tga
         → Missing = Targa Load Error before/while loading UI layouts
         → Fix: python patch_ctp2_images.py
         → Do NOT create blanket placeholders for every LDL-referenced UI TGA.
           Loose files override packed UI art and produce blank/grey menus.
```

**Known wicker causes (ranked):**
1. bare-LF in WAW_Great_Library.txt or Great_Library.txt → immediate global wicker
2. Inline `[END]` at end of content line (not on own line) → GL parser misses the close → unclosed section → global wicker ← **this session's root cause**
3. Unclosed section at EOF (depth > 0) → same as above
4. Duplicate GL section headers → global wicker
5. Wrong TGA `desc` byte (0x20 instead of 0x01) → wicker fallback
6. Missing GL background TGAs (upfg500/501/502/uptg04e) in scenario folder
7. Missing UI progress-bar TGAs (ug026/ug027) in reachable pictures folders → Targa Load Error
8. Blanket LDL UI placeholders in pictures dirs → black/grey menu art because loose TGAs override packed/base UI assets; `upbt01*`, `ug026`/`ug027`, `upbt06*`, `upbt07*`, startup `upsg*`, and LDL-required `uptg06*` files must match the protected manifest rather than generated placeholders or MoM shadows
9. Bad LDL filename reference (`uptg06f-2.tga` instead of packed `uptg06f.tga`) → Targa Load Error; fix the LDL reference, do not create a loose placeholder
10. Obsolete CTP1 button references (`ctp1_button_up/down.tga`) in `fancy.ldl` or `ns_template.ldl` → Targa Load Error; replace with packed CTP2 `upbt01aU/D.tga`
11. Default-only `upcb28/29/30` minimap buttons in `controlpanel.ldl` → repeated Targa Load Error; compare against English peer and remove the dead sibling button family

---

## Hard Lesson: Wrong-Looking Startup UI Is a Base-Install Diff Problem

**Symptom signature:** startup/menu UI loads with wrong-looking art, or it fails with a
Targa Load Error for an LDL-referenced UI file such as `upbt01aX.tga`. Related visual
symptoms include rectangular/generated brown buttons, wrong button shapes,
placeholder-like loading panels, and dark/flat loading-screen backgrounds.

**Root cause from 2026-05-23:** the first investigation used the wrong boundary. The
bad files were not only inside `Scenarios\mom`. Generated loose TGAs had polluted
`ctp2_data\default\graphics\pictures`, so the base install no longer matched the AE
baseline. The bad files shadowed packed/base UI art and made the menu look wrong even
though the LDL references were mostly valid. A later failure proved the lesson was still
too narrow: AE has loose lowercase `upbt01*` files, so deleting generated `upbt01*`
without restoring the AE originals caused `Unable to find the file 'upbt01aX.tga'`.
The wrong loading panel came from MoM scenario shadows of AE startup backgrounds
(`upsg001`/`upsg002`/`upsg003`), especially a bad `upsg001.tga` shadow.

**Cost-control rule:** before spending model calls patching individual UI references,
diff the current install against the baseline outside `Scenarios\mom` across all file
types, not only loose `.tga` files. Do not trust visual intuition or one-family fixes
(`upbt01*`, `upbt06*`, `upsg*`, etc.) until the outside-MoM file diff is clean.

```powershell
$current = 'H:\Program Files(x86)\Activision\Call To Power 2'
$ae = 'H:\Program Files(x86)\Activision\Call To Power 2 - ae'

function Get-Inventory($root) {
  Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
      $rel = $_.FullName.Substring($root.Length).TrimStart('\')
      $rel -notlike 'Scenarios\mom\*' -and $rel -notlike '.git\*'
    } |
    ForEach-Object {
      $rel = $_.FullName.Substring($root.Length).TrimStart('\')
      [pscustomobject]@{
        Rel = $rel
        Length = $_.Length
        Hash = (Get-FileHash -Algorithm SHA1 -LiteralPath $_.FullName).Hash
      }
    }
}

$curInv = Get-Inventory $current
$aeInv = Get-Inventory $ae
$cur = @{}; foreach ($f in $curInv) { $cur[$f.Rel.ToLowerInvariant()] = $f }
$base = @{}; foreach ($f in $aeInv) { $base[$f.Rel.ToLowerInvariant()] = $f }

foreach ($k in $cur.Keys) {
  if ($base.ContainsKey($k) -and $cur[$k].Hash -ne $base[$k].Hash) {
    [pscustomobject]@{
      Rel = $cur[$k].Rel
      CurrentLength = $cur[$k].Length
      AeLength = $base[$k].Length
      CurrentHash = $cur[$k].Hash.Substring(0, 12)
      AeHash = $base[$k].Hash.Substring(0, 12)
    }
  }
} | Sort-Object Rel | Format-Table -AutoSize
```

**Known recovered families from this failure:**

- `ug026.tga`, `ug027.tga`
- `upbt01aX/U/D/H.tga`, `upbt01bX/U/D/H.tga`, `upbt01cX/U/D/H.tga`, `upbt01xu.tga`
- `upbt06aX/U/D/H.tga`, `upbt06bX/U/D/H.tga`, `upbt06cX/U/D/H.tga`
- `upbt07aX/U/D/H.tga`, `upbt07bX/U/D/H.tga`, `upbt07cX/U/D/H.tga`
- Startup backgrounds: `upsg001.tga`, `upsg002.tga`, `upsg003.tga`, `upsg005.tga`,
  `upsg006.tga`
- LDL-required generated closure: `uptg06a.tga` through `uptg06i.tga`
- Packed picture archives: `pic555.zfs` and `pic565.zfs`; missing archives can
  surface as Targa Load Errors for stock LDL refs such as `upba2317.tga` even when
  no loose `.tga` exists in any baseline.
- Base MVP program tree: every file under
  `H:\Program Files(x86)\Activision\Call To Power 2 - Copy\ctp2_program\ctp` is
  canonical for the current repo's `ctp2_program\ctp` path and must be committed
  as a complete tree, not piecemeal.

**Fix rule:**

1. If AE has the file, copy AE's file into the same base path in the current install.
2. Remove the same filename from `Scenarios\mom\scen0000\default\graphics\pictures`
   unless the scenario intentionally owns custom art for that exact asset.
3. Do not generate a placeholder for any AE-owned UI file.
4. Only generate a placeholder when the file is genuinely absent from AE and the game
   crashes with a Targa Load Error.
5. If a stock LDL reference exists inside `pic555.zfs` or `pic565.zfs`, restore the
   packed archive from the Copy baseline instead of generating a loose override.
6. If the base program folder looks suspect, back up current `ctp2_program\ctp`,
   mirror the entire Copy `ctp2_program\ctp` folder, and verify
   `missing_from_current=0`, `extra_in_current=0`, and `hash_different=0`.
7. If stock LDLs reference a missing same-family surface such as `uptg06a` through
   `uptg06i`, generate the complete sibling family, add it to
   `protected_files_manifest.tsv`, and stage the whole protected surface.

**Validation after restore:**

```powershell
$current = 'H:\Program Files(x86)\Activision\Call To Power 2'
$ae = 'H:\Program Files(x86)\Activision\Call To Power 2 - ae'
$names = @('ug026.tga', 'ug027.tga')
foreach ($pattern in @('upbt01*.tga', 'upsg001.tga', 'upsg002.tga', 'upsg003.tga', 'upsg005.tga', 'upsg006.tga')) {
  Get-ChildItem -LiteralPath (Join-Path $ae 'ctp2_data\default\graphics\pictures') -File -Filter $pattern -ErrorAction SilentlyContinue |
    ForEach-Object { $names += $_.Name }
}
foreach ($fam in @('upbt06', 'upbt07')) {
  foreach ($mid in @('a', 'b', 'c')) {
    foreach ($state in @('X', 'U', 'D', 'H')) {
      $names += "$fam$mid$state.tga"
    }
  }
}

$mismatches = @()
foreach ($name in $names) {
  $c = Join-Path $current "ctp2_data\default\graphics\pictures\$name"
  $a = Join-Path $ae "ctp2_data\default\graphics\pictures\$name"
  if ((Get-FileHash -Algorithm SHA1 -LiteralPath $c).Hash -ne
      (Get-FileHash -Algorithm SHA1 -LiteralPath $a).Hash) {
    $mismatches += $name
  }
}

$momShadow = Get-ChildItem -Path (Join-Path $current 'Scenarios\mom\scen0000\default\graphics\pictures') -File -ErrorAction SilentlyContinue |
  Where-Object { $names -contains $_.Name }

"ae_base_ui_mismatches=$($mismatches.Count)"
"mom_ui_shadow_count=$($momShadow.Count)"
```

Expected:

```text
ae_base_ui_mismatches=0
mom_ui_shadow_count=0
```

**Lesson:** a no-crash visual regression is not proof that the current asset exists in
the right layer. For CTP2 UI art, first restore the base-install invariant against AE,
then remove MoM scenario shadows for AE-owned startup/UI assets unless the scenario
intentionally owns custom art for that exact filename.

---

## Silent Crash Triage (Game Exits Without Error Dialog)

Run these checks in order. Stop at the first failure — that's your root cause.

```
Step 1:  python verify_all.py
         → Must print: "0 / 0 / 0" and "0 bare-LF"
         → Any non-zero: see Script A/C/D output for specifics

Step 2:  python name_audit.py
         → Must print: "25 MoM building keys" with 25 display names
         → Missing entries = gl_str entries absent for that building → rerun apply_name_fixes.py

Step 3:  git --no-pager diff --stat HEAD
         → gl_str.txt and Great_Library.txt must appear as modified (apply_name_fixes.py was run)
         → If NOT in diff: run apply_name_fixes.py then re-verify

Step 4:  python -c "
         import re; from pathlib import Path
         raw = Path('Scenarios/mom/scen0000/english/gamedata/gl_str.txt').read_bytes()
         lines = raw.split(b'\r\n')
         tab_keys = {l.split(b'\t')[0].decode() for l in lines if b'\t' in l and l.startswith(b'IMPROVE_')}
         notab_keys = {l.split(b'\"')[0].decode() for l in lines if b'\t' not in l and l.startswith(b'IMPROVE_')}
         only_notab = notab_keys - tab_keys
         print('Block-2-only keys (no Block 1 entry): ' + str(only_notab))
         "
         → Must print empty set. Non-empty = those buildings only have Block 2 entries → rerun apply_name_fixes.py

Step 5:  Check for SLIC references to dead keys in ALL file types (Script D covers .slc; expand to .txt):
         python -c "
         import re, json
         from pathlib import Path
         manifest = json.loads(open('Scenarios/mom/ae_building_removal_manifest.json').read())
         ae_keys = {b['key'] for b in manifest['buildings'] if b['classification']=='ae'}
         for fpath in Path('Scenarios/mom').rglob('*'):
             if not fpath.is_file(): continue
             if fpath.suffix in ('.db','.tga','.avi','.wav','.mp3','.xlsx','.json','.md','.csv','.py'): continue
             txt = fpath.read_text(encoding='utf-8', errors='ignore')
             for i, ln in enumerate(txt.splitlines(), 1):
                 if ln.strip().startswith('//'): continue
                 for k in ae_keys:
                     if re.search(r'BuildingDB\s*\(\s*' + re.escape(k) + r'\s*\)', ln):
                         print(fpath.name + ':' + str(i) + ': ' + ln.strip())
         "
         → Must print nothing. Any hit = SLIC reference to removed AE building = silent crash
```

**Recovery for Step 2/3/4 failures (gl_str or apply_name_fixes not run):**
```
python apply_name_fixes.py
python verify_all.py   ← must be 0/0/0
python name_audit.py   ← must be 25 keys
```

**Recovery for Step 5 failures (SLIC reference to removed building):**  
Open the file, find the `BuildingDB(IMPROVE_X)` expression, replace with `if(0) { // IMPROVE_X culled`.

---

## Debugging Discipline

**Single-pass diagnosis — no iterative second-guessing.**

When a crash or regression appears:
1. List all hypotheses ranked by likelihood against the diff
2. One review pass — check each against available evidence
3. Pick the highest-probability cause, fix it, test
4. If wrong, re-rank and repeat from step 1 — do NOT hedge by reverting speculatively

Do not restore files, run multiple partial fixes, or loop through hypotheses in sequence without user test results. Every extra cycle costs a user test round-trip.

---

## Post-Edit Verification (Run After EVERY File Change)

**This is not optional.** Every file modification must be followed by the verification for that file type before testing or committing. The wicker regression (and similar) happened because a fix was applied to one building and never confirmed clean across all buildings.

### Mandatory verification by file type

| File modified | Run this check immediately after |
|---|---|
| `Great_Library.txt` or `WAW_Great_Library.txt` | **Script A** (orphan scan) + **Script C** (MoM integrity) |
| `WAW_Great_Library.txt` | CRLF check: bare-LF must be 0 + **Script E** (section depth must be 0 at EOF; inline `[END]` in content lines must be 0) |
| `feat.txt` | Count `}` lines — must equal number of open `FEAT_* {` blocks |
| Any `.slc` file | **Script D** (SLC BuildingDB scan) — any hit for a removed building = silent crash at load |
| Any file at all | **Script B** (full rglob scan) — same key may appear in other files |
| Before every test | Mentally confirm: (1) no orphaned GL sections, (2) no SLC BuildingDB hits, (3) WAW CRLF clean, (4) gl_str entries present for ALL loaded buildings (run `python name_audit.py`), (5) game reaches title screen without silent exit |

### Script A — GL orphan section scan (run after any GL edit)

```python
import json, re
from pathlib import Path

manifest = json.loads(open('Scenarios/mom/ae_building_removal_manifest.json').read())
ae_keys = {b['key'] for b in manifest['buildings'] if b['classification']=='ae'}

SUFFIXES = ['_WAW_PREREQ','_WAW_STATISTICS','_WAW_GAMEPLAY','_WAW_HISTORICAL',
            '_PREREQ','_STATISTICS','_GAMEPLAY','_HISTORICAL']

def get_base_key(name):
    for suf in SUFFIXES:
        if name.endswith(suf):
            return name[:-len(suf)]
    return None

def extract_sections(line):
    '''Handle both [SECTION] and [END][SECTION] formats on the same line.'''
    s = line.strip()
    results = []
    if s.startswith('[END]'):
        s = s[5:].strip()
    if s.startswith('[') and s.endswith(']') and len(s) > 2:
        results.append(s[1:-1])
    return results

total = 0
for gl in ['Scenarios/mom/scen0000/english/gamedata/Great_Library.txt',
           'Scenarios/mom/scen0000/english/gamedata/WAW_Great_Library.txt']:
    for i, line in enumerate(open(gl, encoding='utf-8', errors='ignore'), 1):
        for sname in extract_sections(line):
            base = get_base_key(sname)
            if base and base in ae_keys:
                print(f'{Path(gl).name}:{i}: [{sname}]')
                total += 1
print(f'Orphaned AE GL sections remaining: {total}')  # must be 0
```

### Script B — Full scenario scan (run after ANY building-related change)

```python
import re, json
from pathlib import Path
manifest = json.loads(open('Scenarios/mom/ae_building_removal_manifest.json').read())
ae_keys = {b['key'] for b in manifest['buildings'] if b['classification']=='ae'}
for fpath in sorted(Path('Scenarios/mom').rglob('*')):
    if not fpath.is_file() or fpath.suffix in ('.db', '.tga', '.avi', '.wav', '.mp3'):
        continue
    try:
        txt = fpath.read_text(encoding='utf-8', errors='ignore')
    except:
        continue
    non_comment = '\n'.join(l for l in txt.splitlines()
                            if not l.strip().startswith('#') and not l.strip().startswith('//'))
    hits = [k for k in ae_keys if re.search(r'\b' + re.escape(k) + r'\b', non_comment)]
    if hits:
        for k in hits:
            for i, ln in enumerate(txt.splitlines(), 1):
                s = ln.strip()
                if not s.startswith('#') and not s.startswith('//') and re.search(r'\b' + re.escape(k) + r'\b', ln):
                    print(f'{fpath.name}:{i}: {ln.strip()}')
```

### Script C — MoM building GL integrity check (run after any GL removal)

```python
import json
from pathlib import Path

manifest = json.loads(open('Scenarios/mom/ae_building_removal_manifest.json').read())
ae_keys = {b['key'] for b in manifest['buildings'] if b['classification']=='ae'}

def extract_sections(line):
    '''Handle both [SECTION] and [END][SECTION] formats.'''
    s = line.strip()
    if s.startswith('[END]'):
        s = s[5:].strip()
    if s.startswith('[') and s.endswith(']') and len(s) > 2:
        return {s[1:-1]}
    return set()

section_names = set()
for gl in ['Scenarios/mom/scen0000/english/gamedata/Great_Library.txt',
           'Scenarios/mom/scen0000/english/gamedata/WAW_Great_Library.txt']:
    for l in open(gl, encoding='utf-8', errors='ignore'):
        section_names.update(extract_sections(l))

buildings_lines = open('Scenarios/mom/scen0000/default/gamedata/buildings.txt', encoding='utf-8', errors='ignore').readlines()
missing = 0
for bl in buildings_lines:
    bl = bl.strip()
    if bl and not bl.startswith('#') and '{' in bl:
        key = bl.split('{')[0].strip()
        if key and key not in ae_keys and key.startswith('IMPROVE_'):
            gaps = [t for t in [key+'_PREREQ',key+'_STATISTICS',key+'_GAMEPLAY',key+'_HISTORICAL']
                    if t not in section_names]
            if gaps:
                print(f'MISSING {key}: {gaps}')
                missing += 1
print(f'MoM buildings with missing GL sections: {missing}')  # must be 0
```

### Script D — SLC silent crash scan (run after any SLC edit or building removal)

```python
import re, json
from pathlib import Path
manifest = json.loads(open('Scenarios/mom/ae_building_removal_manifest.json').read())
ae_keys = {b['key'] for b in manifest['buildings'] if b['classification']=='ae'}
hits = 0
for fpath in Path('Scenarios/mom').rglob('*.slc'):
    for i, ln in enumerate(open(fpath, encoding='utf-8', errors='ignore'), 1):
        if ln.strip().startswith('//'):
            continue
        for k in ae_keys:
            if re.search(r'BuildingDB\s*\(\s*' + re.escape(k) + r'\s*\)', ln):
                print(f'SILENT CRASH: {fpath.name}:{i}: {ln.strip()}')
                hits += 1
print(f'SLC BuildingDB hits on removed keys: {hits}')  # must be 0
```

---

## Change Tracking

Each proposed change gets a record:
```json
{
  "id": "unit-apprentice-mage-001",
  "type": "unit",
  "change": "UNIT_APPRENTICE_MAGE definition",
  "files": ["Units.txt", "gl_str.txt", "uniticon.txt"],
  "critic_reports": {
    "grammar": { "status": "PASS", "issues": [] },
    "schema": { "status": "PASS", "issues": [] },
    "lessons": { "status": "PASS", "issues": [] }
  },
  "ready_to_commit": true,
  "timestamp": "2026-05-03T11:06:09Z"
}
```

---

## MoM→CTP2 Reference Model

We're replicating **d:\games\civ2\mom** (Civ2 Masters of Magic mod).

Key constraints from that mod:
- 48 MoM units + 90 advances + 52 buildings
- Low-era tech focus (avoid mod bloat in Renaissance+)
- Sprite proxies (reuse existing Civ2/CTP2 sprites, swap later)
- Gating: advances unlock unit classes, not individual units (usually)
- Factions: MoM factions map to CTP2 civs

Current state:
- Unit pilot proved the vertical-slice workflow in-game
- Advance dimension now reaches game start and has confirmed loader/display triage rules
- Remaining advance work is full-family cleanup and polish, not basic loader survival
- Next dimension is buildings, starting with one pilot building before any bulk rollout

---

## Next Step

1. **MILESTONE: All 25 MoM buildings in-game — names correct, no crash, no wicker.** ✅
2. Building index lives at `Scenarios/mom/mom_buildings.csv` (25 rows, all status=in_game).
3. Next dimension: building art (TGA asset swaps — Phase 3 in building_plan.md).
4. WAW sections missing for 24 of 25 buildings (only CATHEDRAL has WAW) — low priority, WAW is supplementary display content.

---

## Hard Lesson: Nuclear Reset Is the Only Safe Recovery When Base-Install Is Contaminated

**Date:** 2026-05-23
**Cost:** Multiple GPT-5.5 sessions spent patching individual TGA families.

### What Went Wrong

Every one-family patch (upbt01*, upbt06*, upbt07*, upsg*, pic555.zfs) was correct in
isolation but left the base install in an unknown state. Contamination was wider than
any one directory and included ctp2_program\ctp.

Symptoms indicating full contamination (do NOT patch -- reset immediately):
- Wrong UI background color (teal/blue instead of stone/tan)
- Targa Load Errors surviving after fixing the named file
- Game crashes before map loads with no Targa error dialog
- Non-MoM diff against Copy shows hash_different > 0 in multiple directories

### The Canonical Reset Procedure

Rule: when non-MoM diff shows drift across more than one directory, stop patching. Do the reset.

`powershell
$src  = 'H:\Program Files(x86)\Activision\Call To Power 2 - Copy'
$dest = 'H:\Program Files(x86)\Activision\Call To Power 2'
$arch = "$dest - bunk-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
# 1. Archive bunk install
robocopy $dest $arch /E /COPYALL /R:1 /W:1 /NFL /NDL /NJH
# 2. Mirror Copy baseline in-place, preserving .git and Scenarios\mom
robocopy $src $dest /E /COPYALL /PURGE /R:1 /W:1 /NFL /NDL /NJH /XD "$dest\.git" "$dest\Scenarios\mom"
# 3. Verify: all must be 0
# missing=0 extra=0 hash_diff=0
`

### Partition of Concerns (invariant)

Everything outside .git and Scenarios\mom must match Copy byte-for-byte.
Scenarios\mom is the additive mod layer. .git is version history. Nothing else differs.

If any file outside Scenarios\mom and .git differs from Copy: it is contamination -- reset it.

### Cost-Control Checklist (run BEFORE spending model calls on image bugs)

- [ ] Non-MoM hash diff: missing=0 extra=0 hash_diff=0
- [ ] ctp2_program\ctp matches Copy exactly (48 files, all hashes identical)
- [ ] No MoM scenario shadows of startup/UI assets

If any box is unchecked: reset first, patch never.


---

## GL Visibility: Hiding Items Without Removing Them

**Rule: to hide a tile improvement, order, or concept from the Great Library, you MUST override it with `GLHidden` in the scenario file. Deleting the block achieves nothing.**

CTP2 scenarios have a layered fallback: if the scenario `tileimp.txt` does not contain block `TILEIMP_X`, the engine falls back to `ctp2_data/default/gamedata/tileimp.txt`. The base data file does NOT have `GLHidden` on any block, so every item in base data is visible by default.

Deleting a block from the scenario file is a **no-op** for visibility purposes — the game silently falls back to the base-data block (which is visible).

**Correct hide pattern:**
```python
# Copy block from base if missing in scenario, then add GLHidden
for ident in HIDDEN_ITEMS:
    if ident not in scenario_blocks and ident in base_blocks:
        scenario_blocks.add(ident, base_blocks[ident])
    scenario_blocks.ensure_flags(ident, ["GLHidden"])
```

**Wrong pattern (no-op):**
```python
# BAD: deleting from scenario lets base-data fallback show it
for ident in HIDDEN_ITEMS:
    if ident in scenario_blocks:
        del scenario_blocks[ident]
```

This applies to: `tileimp.txt`, `Orders.txt`, `govern.txt`, and any other CTP2 gamedata file where the scenario file overrides base data.

**GL article pruning** (removing the `[SECTION_NAME_PREREQ]`, etc. sections from `Great_Library.txt`) is a separate operation and must be done in addition to the `GLHidden` flag. The flag hides the item from the database list; the GL article pruning removes its associated text pages. Both must be applied for full hiding.

---

## Total Conversion Mod -- Next Phase

MoM is a total conversion: every CTP2 stock element must be replaced by CSV-defined
MoM elements. No stock CTP2 entry should appear in any dimension.

Dimensions to convert (dependency order):
1. Advances/Technology  -- mom_advances.csv drives advance.txt
2. Units                -- mom_units.csv drives unit.txt + uniticon.txt
3. Buildings            -- mom_buildings.csv drives improve.txt [DONE: 25 in-game]
4. Governments          -- mom_governments.csv drives govt.txt
5. Tile Improvements    -- mom_tileimps.csv drives tileimp.txt
6. Wonders              -- from advances/buildings CSV where type=wonder

Rule: parser reads CSV -> generator writes CTP2 gamedata -> audit verifies no stock elements remain.
Do NOT hand-edit unit.txt, advance.txt, etc. directly -- always go through parser/generator.
