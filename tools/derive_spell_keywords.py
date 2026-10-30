"""tools/derive_spell_keywords.py -- pick up to 5 keywords per spell for the spellbook legend.

NO GOVERNING SPEC. Basis: operator 2026-10-26 ("dunning mmr terms ... sparsely
represent the top 3 keywords per spell, maybe top 5 if space permits ... present
the words in their natural ordering"). Promote to a REQ before this is depended on.

Method (derived once, persisted to the control plane, rendered by ctp2_generator):
  doc(s)   = the infobox Effects summary of the spell's wiki article: from
             "Effects " to where the body opens with "<Name> is", else to
             " Contents "; the spells.csv description when there is no article.
  G2(t, s) = Dunning 1993 log-likelihood ratio of term t in doc(s) against the
             whole wiki (all 878 articles), so generic words ("however",
             "grants") are recognised as generic; the 214 spell docs alone are
             too few to tell. Only over-represented terms are candidates:
             a/n_s > b/n_rest.
               a = count(t, s)            b = count(t, wiki) - a
               E1 = n_s * (a+b) / N       E2 = n_rest * (a+b) / N
               G2 = 2 * (a*ln(a/E1) + b*ln(b/E2))      (0*ln 0 = 0)
  MMR      = repeat: pick argmax  lam * G2(t)/max G2  -  (1-lam) * max J(t, k)
             over k already picked, J = Jaccard of the sets of spells each term
             occurs in. Two terms that always travel together are not both spent
             on one spell.
  Output   = column `keywords`: the top 5 in order of first appearance in doc(s),
             each tagged with its MMR rank, e.g. "switch:2 planes:1 freely:3".
             The renderer keeps the best-ranked N that fit and prints them in the
             stored (natural) order.

Writes `keywords`, plus `effects_text` (doc(s) in full, for the spell's Great
Library page), into momjr_csv/spells.csv in place. Re-run after
wiki_import.extract_spells, which rewrites spells.csv with fixed columns.

Run: python tools/derive_spell_keywords.py [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

import ctp2_generator
import modpaths
from wiki_import.common import WIKI_PATH, strip_furniture

TOP_N = 5
LAMBDA = 0.7  # mmr-dst skill default: relevance weighted over redundancy

# English function words plus words every spell article shares (realm, rarity,
# type, cost). The page title already says sphere and rarity.
_STOP = set(ENGLISH_STOP_WORDS) | set("""
whichever whenever otherwise upon yet
realm spell spells rarity common uncommon rare type casting cast cost costs upkeep
research effects effect enchantment enchantments instant combat summoning global
town curse belonging magic mana life nature sorcery death chaos arcane point
points turn turns
enchants selected reloaded lost
article articles incomplete incorrect buggy bug bugs flagged details game version
description applicable
grant grants gets gains receives causes called allowing allows previously addition
remains applies applied
""".split())


def _tokens(text: str) -> list[str]:
    """Lowercase word tokens of 3+ letters, possessive 's dropped, digits ignored."""
    return [t.removesuffix("'s") for t in re.findall(r"[a-z][a-z']{2,}", text.lower())]


def _stem(token: str) -> str:
    """Fold plural forms so 'planes' and 'plane' count as one term."""
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("s") and not token.endswith("ss") and len(token) > 4:
        return token[:-1]
    return token


def _spell_text(name: str, csv_desc: str, wiki_by_title: dict[str, str]) -> str:
    """Return the effect text for a spell, preferring the full wiki article."""
    key = name.lower()
    for title in (key, key + " (spell)", key.rstrip("s"), key.replace("'s", "s")):
        if title in wiki_by_title:
            text = wiki_by_title[title]
            break
    else:
        text = csv_desc
    if "Effects " in text:
        text = text.split("Effects ", 1)[1]
    # The infobox summary ends where the article body opens with "<Name> is ...";
    # the body is long prose whose rare filler words would outscore the effect.
    # Only at the start of a sentence: "...as long as Heroism is in effect" is
    # part of the effect and must not end the summary there.
    body = re.search(r"(?<=[.!?]\s)" + re.escape(name) + r"\s+is\s", text, re.I)
    if body:
        text = text[:body.start()]
    return text.split(" Contents ", 1)[0]


def _g2(a: int, b: int, n_s: int, n_rest: int) -> float:
    """Dunning log-likelihood ratio for a term seen a times in s, b times elsewhere."""
    total = n_s + n_rest
    e1 = n_s * (a + b) / total
    e2 = n_rest * (a + b) / total
    g = 0.0
    if a:
        g += a * math.log(a / e1)
    if b:
        g += b * math.log(b / e2)
    return 2.0 * g


def derive(rows: list[dict], wiki_by_title: dict[str, str],
           shown: dict[str, str]) -> dict[str, str]:
    """Return {spell ident: keyword column value} for every row.

    Require: each row has `ident`, `name` and `description`; wiki_by_title maps
    lowercase article title -> article text and is the G2 reference corpus;
    shown maps ident -> the effect text the confirm box displays.
    Guarantee: at most TOP_N terms per spell, none of them a stop word or a word
    of the spell's own name, listed in order of first appearance with MMR rank.
    """
    reference = Counter(_stem(t) for text in wiki_by_title.values() for t in _tokens(text)
                        if t not in _STOP)
    n_reference = sum(reference.values())
    docs: dict[str, list[tuple[str, str]]] = {}
    for row in rows:
        own = {_stem(t) for t in _tokens(row["name"])}
        # Keywords jog the memory of the description the player reads, so they
        # come from the words that description shows (operator 2026-10-27).
        text = shown.get(row["ident"]) or _spell_text(
            row["name"].strip(), row.get("description", ""), wiki_by_title)
        docs[row["ident"]] = [(_stem(t), t) for t in _tokens(text)
                              if t not in _STOP and _stem(t) not in own]

    counts = {ident: Counter(s for s, _ in doc) for ident, doc in docs.items()}
    occurs: dict[str, set[str]] = {}
    for ident, c in counts.items():
        for stem in c:
            occurs.setdefault(stem, set()).add(ident)

    out: dict[str, str] = {}
    for ident, doc in docs.items():
        c = counts[ident]
        n_s = sum(c.values())
        if not n_s:
            out[ident] = ""
            continue
        n_rest = max(n_reference - n_s, 0)
        scores = {}
        for stem, a in c.items():
            b = max(reference[stem] - a, 0)
            if n_rest == 0 or a / n_s > b / n_rest:
                scores[stem] = _g2(a, b, n_s, n_rest)
        if not scores:
            out[ident] = ""
            continue
        top = max(scores.values()) or 1.0
        picked: list[str] = []
        while scores.keys() - set(picked) and len(picked) < TOP_N:
            def mmr(stem: str) -> float:
                overlap = max((len(occurs[stem] & occurs[k]) / len(occurs[stem] | occurs[k])
                               for k in picked), default=0.0)
                return LAMBDA * scores[stem] / top - (1 - LAMBDA) * overlap
            picked.append(max(sorted(scores.keys() - set(picked)), key=mmr))
        rank = {stem: i + 1 for i, stem in enumerate(picked)}
        first_surface: dict[str, str] = {}
        for stem, surface in doc:
            first_surface.setdefault(stem, surface)
        natural = [stem for stem in first_surface if stem in rank]
        out[ident] = " ".join(f"{first_surface[s]}:{rank[s]}" for s in natural)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="print, do not write spells.csv")
    args = parser.parse_args()

    path = modpaths.CSV_DIR / "spells.csv"
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    wiki = json.loads(WIKI_PATH.read_text(encoding="utf-8"))
    wiki_by_title = {page["t"].lower(): strip_furniture(page.get("x", "")) for page in wiki}

    # effects_text first: the shown text is built from it.
    for row in rows:
        text = _spell_text(row["name"].strip(), row.get("description", ""), wiki_by_title)
        row["effects_text"] = " ".join(text.split())
    shown = {row["ident"]: ctp2_generator.spell_shown_text(row) for row in rows}
    keywords = derive(rows, wiki_by_title, shown)
    for row in rows:
        row["keywords"] = keywords[row["ident"]]
    if args.dry_run:
        for row in rows:
            print(f"{row['name']:<28} {row['keywords']}")
        return
    for column in ("keywords", "effects_text"):
        if column not in fields:
            fields.append(column)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote keywords for {sum(1 for r in rows if r['keywords'])}/{len(rows)} spells -> {path}")


if __name__ == "__main__":
    main()
