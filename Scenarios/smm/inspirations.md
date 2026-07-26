# Super Magic Mod — inspirations

Design ideas and flavor notes, newest first. These are *aspirational*, not yet
built — the roadmap in `DESIGN.md` tracks what's implemented.

---

## Mythic beasts belong to eras — they die out as man tames the wild (2026-07-15)

**Source:** user, watching dragons dominate air combat in early play. Feels like
Rise of Nations (mythic edition): each age has its own creature roster, and the
story tells the tale of the world changing.

**The idea — flavor per age, driven by what phases in *and* out:**

- **Air superiority transitions across eras.** Dragons are the early-era "superior
  air support." By the **Renaissance**, *hot air balloons* take over the sky —
  and they aren't afraid to mount ballistas and cannons. Dragons can still swat
  a balloon, but the balloon is the *technology-based* successor. So one era's
  magic air power is phased out for the next era's engineered version.
- **By the Renaissance, the dragons have died out.** The story explains the
  roster change: the age of dragons ends. Same for **giants** — as man "tames
  the wild," the great beasts vanish.
- **Races persist, mythic beasts don't.** The surviving races into the later
  ages are **humans, dwarves, elves, and goblins**. The rest of the mythic
  bestiary — **cyclops** and the like — were creatures of the *earlier* era
  (Hellas / bronze-hellenistic), and drop out as the world modernizes.
- **Net effect:** each age reads differently. Bronze/Hellenistic = full mythic
  menagerie (cyclops, giants, dragons). Medieval = fading magic, dragons rare.
  Renaissance = magic gone, engineered air power, only the four grounded races.

**How this maps to the engine (implementation sketch, not built):**

- This is fundamentally an **age-gated availability** design: a unit is buildable
  only within an age window `[appears, obsoletes]`, not just `appears`. CTP2 has
  `Obsolete`-style gating; mythic units get an *obsoleting advance* in the
  Renaissance branch so they stop being buildable (and existing ones can be
  attritioned via SLIC — "the last dragons die out").
- Depends on **faithful per-age tagging** of merged content. Right now the
  control-plane `epoch_age_map` (inherited from MoM) caps at AGE_THREE, so
  imported historical content squashes into the low ages. A real age-flavored
  roster needs the SMM policy to map epochs 0–9 → AGE_ONE…AGE_TEN so each
  creature/tech lands in its true era first. (See DESIGN.md "Hellas integration"
  + "Balance pass".)
- Ties into the **dragon SLIC mechanic** already in DESIGN.md: dragons as
  temporary, event-summoned, GoT-style bound units. The "die out by Renaissance"
  rule is the *upper* bound on that mechanic — a hard sunset, not just scarcity.

**Why it's good:** gives every age a distinct identity and a narrative arc (magic
recedes as technology rises), instead of a flat roster where a turn-1 dragon is
still relevant in the industrial age.
