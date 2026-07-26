---
name: ctp2-menu-injection-not-clicks
description: SETTLED — PostMessage clicks never work in CTP2 menus (0/36 grid sweep); drive them with the injection hook press:/select:; uiwalk captures are 1:1 with engine 1024x768 coords
metadata: 
  node_type: memory
  type: project
  originSessionId: ece7bf46-8181-44dc-a467-b8bd73e45062
  modified: 2026-07-25T00:38:15.131Z
---

**Do not re-litigate this.** Two things were settled by measurement on 2026-07-24.

**1. CORRECTED 2026-07-24 — clicks DO register; the earlier "clicks never work"
claim was WRONG.** A 36-point grid sweep produced 0 responses and I wrongly
concluded the channel was dead (blaming GetCursorPos polling). Later runs proved
otherwise: a click at (797,555) selected a list row, and (797,450) selected the
row above it.

Current CANDIDATE THESIS (not settled): click coords are scaled by **0.8**
(client -> logical, i.e. engine divides by 1.25), so to hit something seen at
capture (cx,cy) you must SEND (cx*1.25, cy*1.25). It explains both observed
successes exactly — (797,450)->(638,360)=row 2, (797,555)->(638,444)=row 3 —
and explains why nothing ever scrolled: x=797 scales to 638, which is INSIDE the
list, never on the scrollbar. UNRECONCILED: the 36-click sweep should have hit
rows under this model and didn't. Verify before relying on it.
See [[feedback-hypothesis-not-assertion]].

**2. uiwalk captures are 1:1 with engine coordinates.** `ScreenResWidth=1024`,
`ScreenResHeight=768`; client is 1280x960 and the engine draws the 1024x768
surface UNSCALED into the top-left with black padding. Proven from LDL geometry:
`ScenarioWindow` 640x480 centered → origin (192,144); `AvailableListBox` +(32,43)
564x378 → logical x224–788, y187–565, vs measured x222–784, y175–559.
The 1.25x ratio (1280/1024) exists ONLY between a human's scaled window
screenshot and a uiwalk capture — never between capture and engine.

**Drive menus via the injection hook** (`MoM_WindowsMessageHook`, `aui_sdl.cpp`:
write payload to `H:\mom_inject.txt`, then PostMessage `WM_APP+100`):
- `press:<LDL path>` → `aui_Button::InjectPress()`
- `select:<LDL path>,<index>` → `aui_ListBox::SelectItem()` (added 2026-07-24)
- bare name → `g_slicEngine->RunUITriggers()`

`CTP2_LISTBOX` is `atomic true`, so list rows and the scrollbar have **no**
addressable LDL path — index selection is the only way to pick a row, and it
needs no scrolling.

Verified headless walk: `press InitPlayWindow.NewGameButton` →
`press SPNewGameWindow.ScenarioButton` →
`select ScenarioWindow.AvailableListBox,3` (= **Masters of Magic**; 0 Apolyton,
1 Alexander, 2 Sieben Samurai) → `press ScenarioWindow.LoadButton`.

**HAZARD: `SelectItem` has no bounds check** — index 4 crashed the game
(`0xC0000005`). Guard the index before injecting.

**Attribution discipline:** diff consecutive screenshots to infer what a step did;
treat one observed change as a hypothesis, not proof (a row-highlight was wrongly
blamed on a click until a controlled rerun disproved it). Byte-identical
successive screenshots mean the input never landed — or a modal ate it.

See [[ctp2-headless-checkpoint-method]], [[ctp2-exe-staging-preflight]], and the
full entry at the top of `Scenarios/mom/lessons_learned.md` ([[mom-wiki]]).
