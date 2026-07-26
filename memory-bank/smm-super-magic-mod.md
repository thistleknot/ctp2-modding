---
name: smm-super-magic-mod
description: "2026-07-15 NEW MOD: Super Magic Mod v0 at Scenarios/smm (commits 510c1c4+1a54fd5) — merged control plane (MoM base + HoMM2 + Midgard + Crusades via merge_control_planes.py; codes namespaced tag:code), generated scenario 461 advances/217 units. Staged: ctp2-native importer (Cradle 5.1/AoM IV/LotR), Hellas v12 design pass, CoMM3 art. See Scenarios/smm/DESIGN.md."
metadata:
  node_type: memory
  type: project
  originSessionId: 77eb8577-a451-4ba1-84c7-af8b7cf3cf0e
---

**STATUS 2026-07-17: PARKED by user ("give up on this mash for now") — do NOT resume SMM work unprompted.** Working tree is uncommitted but gate-clean (validate passes, sphere-home exclusivity + clustering + art all landed; see lessons_learned 2026-07-16/17 entries). Base MoM is intact, resynced, playable. The staged next idea was a Mage-Knight-style reduction (5 race civs: human/mountain folk/fae/barbarians/undead; soft city cap via government TooManyCitiesThreshold) as a CLONE at Scenarios/mk — design discussed, never started.

**Super Magic Mod (SMM) v0 — created 2026-07-15** at `Scenarios/smm/` (user goal: merge ANYTHING fantasy/medieval).

- **Merged control plane** `smm/csv/` = `merge_control_planes.py --base momjr_csv --source homm2/midgard/crusades` (first-wins name dedup, provenance column, **codes namespaced `tag:code`** — civ2 short codes are positional per source; unnamespaced merge cross-wires prereqs). 307/223/128 rows → generated 461 advances, 217 units (Black/Bone Dragon, Genie, Crusaders, Midgard Sorcerer line).
- **Sources found (all 5 requested)**: Cradle 5.1 `H:\Games\ctp2\Cradle51\Cradle51` (⚠ targets 2011 AE); AoM IV `...\AOM_IV\ctp2_data`; HoMM2 `H:\Games\civ2\HoMM2Mod1.1`; LotR `H:\Games\ctp2\lotr_extracted\...\ctp2_data`; Hellas `C:\Users\user\Documents\wiki\rpg\hellas\Hellas_v12_Rules.md` (a FILE, homebrew RPG ruleset — design source). Bonus: MIDGARD/CRUSADES/MONGOL/SAMURAI/JIHAD/ATLANTIS civ2 scenarios have own RULES.TXT; CoMM3.7z = Civ3 HoMM3 mod, ~9k art files (art goldmine, unextracted).
- **Roadmap** (Scenarios/smm/DESIGN.md): ctp2-native gamedata→csv importer for Cradle/AoM/LotR; Hellas design pass (spheres/factions); CoMM3 art extraction; balance; wonders authoring. v0 limits: MoM's 5 tribes only, proxy sprites for new units, no smm audit lane.
- **7-source expansion (2026-07-16, uncommitted)**: cradle/aom/lotr joined via ctp2-native importer → 591 advances/539 units. VERIFIED: merge + generator deterministic (byte-diff gates), 0 dangling refs, base protected, validate passes; live scen0000 had gone STALE vs csv (AdvanceLists.txt missing all 473 merged advances) — resynced by regen; the regen byte-diff is the only proof of csv↔scenario sync. New audit sheets in csv/: `collision_ledger.csv` (788 first-wins drops) + `collapse_candidates.csv` (52 advance + 21 unit cross-mod concept groups, e.g. Archery ×5 — REDUCE decision pending with user).
- **Unreachable-gate defect class (2026-07-16, FIXED)**: source mods gate scenario-granted content behind unreachable prereqs (LotR racials/Hextapul/AoM govs → ADVANCE_GAIA_CONTROLLER); the generator's foreign-edge sever pass rootified such advances → 56 "H <faction>" hero units buildable turn-1. Fix = sever pass self-prereqs any advance whose prereqs were ALL foreign (38 kept closed; no-op on MoM). RULES: data fixes at the sever layer need a FULL rebuild (in-place regen can't see already-severed state); after any full rebuild run the generator TWICE (pass 1 ≠ fixed point: costs use pre-sever prereq counts). See lessons_learned 2026-07-16.
- .gitattributes extended: smm/scen0000 LF-protected (fugly prevention).
- **MANDATORY GATE (learned the hard way, 2 live-dialog failures)**: run `validate_scenario.py --scenario <scen dir>` after EVERY generation, before playtest — newsprite grammar, ident charset, engine reserved-token scan (engine_reserved_tokens.txt, 76 keywords: a unit named "Sprite" → UNIT_SPRITE keyword → load exit), gl_str grammar. Generator exit-0 ≠ engine-parseable. Merged-source names carry punctuation ("Water/Air Elementals", "Jack O'Lantern") — sanitize() everywhere an ident is derived.
- GitHub mirror of prior working MoM: https://github.com/thistleknot/ctp2-momjr (mom.zip = frozen hand-patched regression reference).

Related: [[mom-universal-encoder]], [[mom-wiki]].
