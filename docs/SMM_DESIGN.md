# Super Magic Mod (SMM) — design & roadmap

A merged fantasy/medieval total conversion for CTP2, built on the universal mod
encoder control plane. Everything regenerates from `Scenarios/smm/csv/`.

## v0 — SHIPPED (this folder)

Merged control plane (`csv/`) = ordered union, first source wins name collisions:

| Priority | Source | Lane | What it contributes |
|---|---|---|---|
| 1 (base) | MoM (momjr_csv, curated) | civ2→encoder | Magic system framing, 5 spheres, tribes, policy, SLIC, working art |
| 2 | HoMM2Mod1.1 | civ2→encoder | HoMM creature roster (dragons, genies, undead), hero units |
| 3 | MIDGARD | civ2→encoder | Norse fantasy layer (sorcerers, mythic units) |
| 4 | CRUSADES | civ2→encoder | Medieval military layer (crusaders, templar-era units) |

Numbers: 307 merged advances / 223 units / 128 improvements → generated DB:
461 advances, 217 units. 105 name collisions deduped (Alphabet, Barracks, ...).

Key mechanism: **civ2 short codes are positional per source** — the merge
namespaces every non-base code as `tag:code` in rows AND advance_code_map.csv,
so cross-source prereq wiring is impossible (`merge_control_planes.py`).

Regenerate:
```
set CTP2_GENERATOR_CSV_DIR=Scenarios\smm\csv
set CTP2_GENERATOR_SCENARIO_DIR=Scenarios\smm\scen0000
python Scenarios\mom\tools\ctp2_generator.py
```
Full regen sequence (proxy art step is required for merged mods):
```
rmdir /s /q scen0000 & xcopy /e /i ..\mom\scen0000 scen0000   # base scenario
python ..\mom\tools\assign_proxy_art.py --scenario scen0000 --csv csv   # borrow art BEFORE gen
set CTP2_GENERATOR_CSV_DIR=csv & set CTP2_GENERATOR_SCENARIO_DIR=scen0000
python ..\mom\tools\ctp2_generator.py
python ..\mom\tools\validate_scenario.py --scenario scen0000
```
`assign_proxy_art.py` copies a real icon TGA (from the base mod's ~96 advance /
61 unit / 68 improve icons) to every merged entity missing its own art, named
as the generator expects, so the icon reconcile uses it instead of the UPLG001
placeholder. Deterministic (byte-stable). v0: 418 icons borrowed; 0 visible
advances/units left on the placeholder.

Re-merge after editing sources:
```
python Scenarios\mom\tools\merge_control_planes.py --base Scenarios\mom\tools\momjr_csv ^
  --source homm2=Scenarios\smm\sources\homm2 --source midgard=Scenarios\smm\sources\midgard ^
  --source crusades=Scenarios\smm\sources\crusades --out Scenarios\smm\csv --display-name "Super Magic" --force
```

## Genre mask (staging control plane)

`csv/genre_mask.csv` — the reviewable staging sheet for cutting content that
doesn't fit the bronze/iron/medieval/fantasy/hellenistic motif. One row per
merged unit/advance/improvement: `dimension,id,name,source,mask,reason`. Set
`mask=yes` to drop; `reason` is free-text comment. Merged civ2 sources ship
full 62-slot unit tables, so this is where AEGIS Cruiser, Battleship, Nuclear
Msl., Bomber, etc. get removed.

Era gate: `--max-age AGE_FOUR` keeps bronze/hellenistic/iron/medieval (AGE_ONE–FOUR)
and flags every advance past it, cascading to units/buildings gated on cut advances.
A keyword screen backstops UNGATED modern units (civ2 scenario mods like Crusades
ship the full 62-slot unit table with no tech prereqs — Mech Inf, Howitzer, AEGIS,
Fighter, etc. are buildable from turn 1 and only a name screen catches them).

**Workflow — ORDER MATTERS (the mask must see the FULL unmasked roster):**
```
# 1. merge UNMASKED so the mask sheet sees every unit
python ..\mom\tools\merge_control_planes.py --base ..\mom\tools\momjr_csv ^
  --source homm2=sources\homm2 --source midgard=sources\midgard ^
  --source crusades=sources\crusades --out csv --display-name "Super Magic" --force
# 2. build the mask on the full set (age-gate + keyword screen)
python ..\mom\tools\make_genre_mask.py --csv csv --scenario scen0000 --max-age AGE_FOUR
# 3. (optional) edit csv\genre_mask.csv — set mask=yes / add reasons
# 4. re-merge WITH the mask to drop flagged rows
python ..\mom\tools\merge_control_planes.py --base ..\mom\tools\momjr_csv ^
  --source homm2=sources\homm2 --source midgard=sources\midgard ^
  --source crusades=sources\crusades --out csv --mask csv\genre_mask.csv ^
  --display-name "Super Magic" --force
# 5. regenerate (proxy art + generator + validate — see the regen sequence above)
```
PITFALL: generating the mask AFTER a masked merge makes it blind to already-dropped
units, which then reappear on the next unmasked re-merge. Always regenerate the mask
from step-1 output. v1: 59 flagged (25 units incl all modern military), 190 visible
units remain (all fantasy/medieval). The research tree is already era-clean — all
AGE_FIVE+ advances are GLHidden by the fantasy-tree isolation.

## Faction / sphere unit gating

Units belong to a magic **sphere** (life/nature/death/chaos/sorcery) and gate on
that sphere's advance ladder — faction identity and tech progression in one. A
Nature tribe researching Nature magic unlocks its Fae units (Centaur, Halfling,
Elf Warriors); Death unlocks undead; etc.

`csv/unit_factions.csv` is the reviewable taxonomy: `unit_id, name, cost, sphere,
tier, gate_code, gate_advance, source`. Edit `sphere`/`tier` to correct the seed;
`assign_unit_factions.py` preserves edits on re-run. Sphere is inferred from
creature type + explicit overrides; tier (lore→adept→mage→wizard→master) from
cost. BASE MoM units keep their curated prereqs (only merged content is re-gated).

Sphere ladder gate codes (all AGE_TWO): life Inv/Lab/Las/Too/Mag · nature
Plu/PT/Rad/Rec/Ref · death Rfg/Rob/SFl/Sth/SE · chaos MP/Med/Met/Min/Mob ·
sorcery The/X2/NP/Phy/Pla.

Pipeline order (after mask): `assign_unit_factions.py --csv csv` sets prereqs,
then regenerate. v1: ~57 units sphere-gated, turn-1 buildable down to ~13 generic
starters. STILL A SEED — sphere assignments need human review in the csv.

## DRAGONS (designed, not yet built)

Per design: dragons are late-age, **SLIC-event-summoned, temporary**, and have a
mind of their own (GoT-style) — NOT freely buildable. Current state is a
placeholder (gated to Chaos MASTER). The real mechanic to implement:
1. A dragon is summoned via a SLIC event (ritual/wonder/quest), not built.
2. It is temporary — despawns after N turns or one battle unless bound.
3. Binding: pairing a unit with a dragon creates a group; that group becomes a
   high-value **hill target** (AI prioritizes killing it; killing frees/kills the
   dragon). Unbound dragons may turn on their summoner.
Implementation: mark dragon units CantBuild (summon-only), add SLIC in
`mom_*.slc` for the summon/timer/binding/target-priority, and a wonder or advance
as the summon gate. Scope: a dedicated SLIC feature — see mom magic-system specs.

## Staged layers (roadmap)

1. **ctp2-native importer** — Cradle 5.1 (`H:\Games\ctp2\Cradle51\Cradle51`),
   Ages of Man IV (`...\AOM_IV\ctp2_data`), LotR (`H:\Games\ctp2\lotr_extracted`)
   are already in CTP2 format; they need a gamedata→csv importer (inverse of the
   generator) so they join the merge as source dirs. Caveat: Cradle 5.1 targets
   the 2011 AE — re-basing through the control plane is the point.
2. **Hellas v12 integration** (`C:\Users\user\Documents\wiki\rpg\hellas\Hellas_v12_Rules.md`)
   — lore/mechanics source, not a mod: sphere/class/faction design language to
   reorganize the merged advance tree (magic schools × epochs), name the
   governments, and theme the tribes. Design pass, edits land in csv + policy.
3. **Art pass** — merged units currently fall back to sprite proxy rules /
   placeholder icons where no SPRITE_/ICON art exists. CoMM3.7z (Conquests of
   Might & Magic 3, Civ3) holds ~9k fantasy art files incl. all nine HoMM3 town
   sets — extraction + TGA conversion feeds the atlas pipeline.
4. **Balance pass** — cost bands/branch weights in `csv/mod_policy.json` are
   inherited from MoM; retune once the roster settles.
5. **Wonders** — sources' `wonders_civ2.csv` are raw material; CTP2 block_text
   authoring per wonder (momjr_csv/wonders.csv is the template).

## Known v0 limits

- Tribes/players are MoM's 5; HoMM2/Midgard/Crusades factions not yet seeded.
- Non-MoM units use proxy sprites (rule table) until the art pass.
- mom_audit.py is MoM-rooted; SMM validation currently = generator exit-0 +
  in-game playtest.
