# Memory Index

## Read first (behavioural)
- [Headlessly OBSERVE the symptom before handing back](feedback-verify-the-claimed-symptom-headlessly.md) — READ BEFORE EVERY HANDBACK; name the instrument and what it would MISS.
- [INSTRUMENT before ENVIRONMENT](feedback-instrument-before-environment.md) — READ ON EVERY FAILING CHECK; order argv → comparator → artifact → environment LAST.
- [Diagnose your own argv FIRST](feedback-diagnose-own-argv-first.md) — the backward walk starts at MY command line; N identical failures = ONE observation.
- [Hypothesize, never assert](feedback-hypothesis-not-assertion.md) — thesis + evidence + falsifier; user counter-evidence is data.
- [Explore like a tree search](feedback-explore-hypothesis-loop.md) — MCTS not bandit; park after ~2 failed revisions; record false results too.
- [Assert slack, not stale goldens](uiwalk-assert-slack-not-stale-goldens.md) — measure the comparator before theorising; a `VERIFIED` comment is not evidence.
- [Control-plane edits + Claude runs the pipeline](feedback_harness_only.md) — edit sources not outputs; Claude runs regen/audit, user only tests in-game.
- [Always launch game](feedback-always-launch-game.md) — auto-launch via run-ctp2-dbg-crashcapture.ps1; still hand BUILD commands to the user.
- [Python path](feedback_python_path.md) — always C:\Users\user\py310\Scripts\python.
- [Integrate folder for WIP on revert](feedback-integrate-folder-wip.md) — move regressing WIP to `integrate/`, never delete.
- [MoM project wiki pointer](mom-wiki.md) — `Scenarios/mom/lessons_learned.md` is canonical; write BOTH wiki entry and memory.

## Harness / environment laws
- [THE LAWS: CTP2 environment model](ctp2-environment-laws.md) — one transition function; per-state pixel tables are DERIVED.
- [DPI artifact, not engine scale](ctp2-dpi-artifact-not-engine-scale.md) — SUPERSEDES all per-surface send-scale claims: DPI-unaware → send == capture 1:1 everywhere.
- [HEADLESS is a continuous invariant](ctp2-headless-invariant.md) — 150ms watchdog + re-stash; never launch the exe outside uiwalk.py.
- [SETTLED: menus = injection, not clicks](ctp2-menu-injection-not-clicks.md) — DO NOT RE-LITIGATE; drive via `press:`/`select:`; SelectItem has no bounds check.
- [L7: input reach is per-SURFACE](ctp2-input-reach-by-surface.md) — menus injection-only; in-game alertboxes take clicks, not keys.
- [END TURN needs mouse input](ctp2-endturn-needs-mouse-input.md) — ping inert chrome (600,6) before the key.
- [PROCESS: headless golden checkpoints](ctp2-headless-checkpoint-method.md) — one small state at a time, freeze as steps JSON + golden.
- [PROCESS: preflight the exe under test](ctp2-exe-staging-preflight.md) — assert a marker string in the exe that will actually launch.
- [PRIMARY display gates the harness](ctp2-primary-display-gates-harness.md) — portrait primary makes 1024x768 illegal → letterboxed UI → crash at turn 0.
- [MoM uiwalk harness](mom-uiwalk-harness.md) — launches via `-l"uiwalk_start"`; template-match vs contract-derived goldens.
- [Repo ancestry is unpushable](ctp2-repo-corruption-orphan-push.md) — work on `mom-base-clean`; `mom-base` can NEVER push.
- [MoM FS corruption recovery](mom-fs-corruption-recovery.md) — H: fault playbook.

## SLIC / gameplay
- [SLIC: the two crash classes](slic-two-crash-classes.md) — 2-level user-fn chain from HandleEvent = AV; use `value[0] == AdvanceDB(...)`.
- [Interactive SLIC CLOSED (link 7)](ctp2-interactive-slic-link7.md) — arm globals survive BeginTurn; buttons render in REVERSE order; derive geometry.
- [Alertbox buttons MUTATE state](ctp2-alertbox-interactive-confirmed.md) — button bodies run and persist.
- [Alertbox arms: not LDL-addressable, but CLICKABLE](ctp2-alertbox-not-ldl-addressable.md) — click the frame-measured centre; dismiss aims at the LAST-declared arm.
- [MoM SLIC save-cache](mom-slic-save-cache.md) — saves cache compiled SLIC; test from a NEW game.
- [MoM SLIC namespace/segments](mom-slic-namespace-segments.md) — Message() needs messagebox SEGMENTS; ONE flat namespace.
- [MoM SLIC msg interpolation](mom-slic-message-interpolation.md) — plain `{scalar}` only; `{Arr[Idx]}` silently drops the message.
- [MagicMenu VERIFIED in-game](mom-magic-menu-verified.md) — `j` → MAGIC STATUS alertbox, 6/6 PASS.
- [Mana is a real resource; Summon costs 75](mom-magic-economy-priced.md) — the pool-overflow auto-summon made the spellbook unaffordable by construction.
- [MoM magic verified clean](mom-magic-verified-clean.md) — magic+gold SLIC correct vs engine source.
- [MoM peasant settle](mom-peasant-settle.md) — no settler unit; peasants found cities.
- [MoM anarchy science regression](mom-anarchy-science-regression.md) — GOVERNMENT_ANARCHY MaxScienceRate 0.
- [MoM endgame auto-defeat](mom-endgame-autodefeat.md) — countdown ignored the endgame wonder.
- [MoM duplicate-civ overflow](mom-duplicate-civ-overflow.md) — cosmetic; players capped to civ count.
- [MoM intermittent setup crash](mom-intermittent-setup-crash.md) — RETRY, don't re-investigate.

## Art / sprites / icons
- [Sprite extent and anchor are ONE coupled bug](mom-sprite-extent-anchor-coupled.md) — stock `bottom - hot_y = 12`, h55/top10/bot64; never change extent without the anchor.
- [Icon over-zoom: uniformity is the tell](ctp2-icon-overzoom-uniformity-tell.md) — median==max across 55 files proves normalization, not source variance. OPEN.
- [Spearman WAS a real bug](mom-sprite-chain-verified-clean.md) — exe reads BOTH GU%.2d and GU%.3d; builder now writes both names.
- [MoM sprite numbering pinned](mom-sprite-numbering-pinned.md) — newsprite.txt ids are baked into filenames.
- [MoM sprite pipeline](mom-sprite-pipeline.md) — invisible units = anim transparency 0; makespr.py byte-identical to makespr.exe.
- [MoM advance icons](mom-advance-icons.md) — 85 visible = 11 canonical category cells; durable truth is ICON_ADVANCE_*.tga.
- [MoM fugly double-load](mom-fugly-double-load.md) — compound: DB double-load + TGA desc byte + CRLF.
- [MoM dropdown RIM fugly](mom-dropdown-rim-fugly.md) — zfs-RIM surfaces AV every blit; extract to loose TGA.
- [MoM city-panel fugly RESOLVED](mom-citypanel-fugly-engine.md) — desc requirements are per texture family.

## Pipeline / build / data
- [Generator pass ordering ate the cost rescale](mom-generator-pass-ordering.md) — retune ran ~1300 lines BEFORE the ingest that rewrites buildings.txt.
- [SLIC is a control-plane dimension, flowing BACKWARD](mom-slic-control-plane-dimension.md) — xlsx tab per dimension, cells hold real source; normalise openpyxl `None` in drift gates.
- [MoM canonical toolchain](mom-canonical-toolchain.md) — control plane is truth; `ctpedit.py patch all`.
- [MoM universal encoder](mom-universal-encoder.md) — civ2 mod → csv/xlsx control plane → ctp2; gate is regen byte-stability.
- [SKILL: mod schema map-reduce](skill-mod-schema-mapreduce.md) — MAP native → NORMALIZE universal → REDUCE; not first-wins union.
- [SKILL: CTP2 crash classes](skill-ctp2-crash-classes.md) — 9 validate_scenario.py gates; run before EVERY playtest.
- [MoM gamefile manifest](mom-gamefile-manifest.md) — improvements load from buildings.txt, not Improve.txt.
- [MoM DB error class](mom-db-error-class.md) — "not found in Advance database" = orphan Great Library sections.
- [MoM GL DB-name crash](mom-gl-dbname-crash.md) — only 12 `<L:DATABASE_X>` names are legal.
- [MoM engine build toolchain](mom-engine-build-toolchain.md) — standalone BuildTools at H:\BuildTools.
- [Working msbuild command + 3 gotchas](mom-engine-build-cdkdir-toolset.md) — PlatformToolset=v145, CDKDIR for flex/byacc.
- [MoM stack-overflow crashes = 1 MB stack](mom-ai-endturn-stackoverflow.md) — fix is an 8 MB stack, not SLIC.
- [MoM crash symbolication](mom-crash-symbolication.md) — stale ctp2-dbg.map yields fictional symbols.
- [SMM Super Magic Mod](smm-super-magic-mod.md) — merged control plane at Scenarios/smm.
- [momjr source](reference_momjr_source.md) — original MoM magic design at h:\games\ctp2\mom.
