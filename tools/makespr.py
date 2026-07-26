"""
makespr.py — Python reimplementation of Activision's makespr 0.3 for Civilization: Call to Power

WORKFLOW ARCHITECTURE
=====================
1. CLI dispatch: parse -u/-c/-g/-x flags and sprite ID, derive script filename.
2. Script parser: tokenise the .txt script (comments stripped, nested {} blocks
   resolved) into a tree of tag→value/block pairs.
3. TIFF loader: load 32-bit ARGB source images and optional 24-bit shadow TIFFs
   from the numbered subdirectory, following the naming convention in §4.1.
4. Shadow merger: for each (image, shadow) pair, stamp shadow pixels into the
   image buffer at pixels where alpha == 0 (transparent), producing a unified
   ARGB32 buffer ready for encoding.
5. Scanline encoder: walk each row left-to-right, classify each pixel run as
   one of four types (chromakey/transparent, copy/opaque, shadow, feathered/
   partial-alpha), and emit the corresponding Pixel16 RLE words.
   Run-type tags live in the high byte; EOLN flag (0xF0) is OR'd into the high
   nybble when a run terminates at the right edge of the scanline.
6. Frame encoder: for each frame, build the height-table + data stream:
     [height: u16][row_offsets: u16 × height][rle_data …]
   Empty rows (all transparent) get sentinel offset 0xFFFF.
7. SPR assembler: stitch script metadata, animation descriptors, per-facing
   frame arrays, hot-points, shield-points, etc. into the final binary layout
   and write to GU##.SPR / GG##.SPR / GC###.SPR / GX##.SPR.

PRECONDITIONS
  • Script file follows the naming convention (gu01.txt → GU01.TXT).
  • TIFF images exist under the subdirectory named by the stripped sprite ID
    (e.g. sprite 01 → directory "1/").
  • Source TIFFs are 96×72 (units/effects/cities) or whatever SPRITE_WIDTH/
    SPRITE_HEIGHT the script declares; alpha channel present for image files,
    absent (24-bit) for shadow files.
  • Pillow (PIL) installed: pip install Pillow.

FAILURE MODES
  • Missing TIFF: logged as a warning; frame is skipped (matching original
    behaviour where shadow is optional and absent frames are omitted).
  • Invalid shadow format (upper-left pixel neither black nor white): hard exit,
    matching the original printf+exit(-1).
  • Pixel with alpha neither 0x00 nor 0xFF and not feathered context: hard exit.
  • Script syntax error: raises ParseError with line number.

PIXEL FORMAT
  16-bit output, selectable 565 (default) or 555 via --555 flag.
  Shadow magic colours: 565 → 0xF81F, 555 → 0x7C1F.
  Chromakey (fully transparent): RGB=0x0000, alpha=0x00.
  Feathered (partial alpha): single pixel per run, alpha in low byte of tag word.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

# ── Pillow is the only non-stdlib dependency ──────────────────────────────────
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow required: pip install Pillow")


# ─────────────────────────────────────────────────────────────────────────────
# Constants (mirroring the C header)
# ─────────────────────────────────────────────────────────────────────────────

CHROMAKEY_PIXEL   = 0x0000
SHADOW_PIXEL_565  = 0xF81F
SHADOW_PIXEL_555  = 0x7C1F
SHADOWBACKGD_PIXEL = 0xFFFF   # white background sentinel in shadow files

CHROMAKEY_RUN_ID  = 0x0A
COPY_RUN_ID       = 0x0C
SHADOW_RUN_ID     = 0x0E
FEATHERED_RUN_ID  = 0x0F

EOLN_FLAG         = 0xF0      # OR'd into high nybble of tag byte at row end
NO_ALPHA          = 0x00
ALL_ALPHA         = 0xFF
EMPTY_TABLE_ENTRY = 0xFFFF


# ─────────────────────────────────────────────────────────────────────────────
# Pixel conversion helpers
# ─────────────────────────────────────────────────────────────────────────────

def rgb32_to_16_565(r: int, g: int, b: int) -> int:
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def rgb32_to_16_555(r: int, g: int, b: int) -> int:
    return ((r & 0xF8) << 7) | ((g & 0xF8) << 2) | (b >> 3)


class PixelEncoder:
    """Converts (R,G,B,A) tuples to Pixel16 and shadow-pixel constants."""

    def __init__(self, use_555: bool = False):
        self.use_555 = use_555
        self.shadow_pixel = SHADOW_PIXEL_555 if use_555 else SHADOW_PIXEL_565
        self._convert = rgb32_to_16_555 if use_555 else rgb32_to_16_565

    def to_16(self, r: int, g: int, b: int) -> int:
        pix = self._convert(r, g, b)
        # filter pure black so it isn't confused with chromakey
        return 0x0001 if pix == 0x0000 else pix


# ─────────────────────────────────────────────────────────────────────────────
# Shadow merging
# ─────────────────────────────────────────────────────────────────────────────

def merge_shadow(image_pixels: list[list[tuple[int,int,int,int]]],
                 shadow_pixels: list[list[tuple[int,int,int]]],
                 width: int, height: int,
                 enc: PixelEncoder) -> None:
    """
    Stamp shadow data into image_pixels in-place.
    shadow_pixels is RGB (no alpha).  Black pixels = shadow; white = nothing.
    Precondition: upper-left shadow pixel is pure black (0,0,0) or pure white.
    Guarantee: pixels with alpha < 0xFF get shadow colour where shadow present.
    """
    sr, sg, sb = shadow_pixels[0][0][:3]
    if (sr, sg, sb) == (0xFF, 0xFF, 0xFF):
        white_bg = True
    elif (sr, sg, sb) == (0x00, 0x00, 0x00):
        white_bg = False
    else:
        sys.exit("Shadow file is in invalid format.")

    # Pure magenta (255,0,255) converts to the shadow magic pixel in BOTH
    # formats: 565 → 0xF81F, 555 → 0x7C1F — exactly enc.shadow_pixel, so the
    # scanline encoder emits a SHADOW run. (A previous revision stamped GREEN
    # here, which encoded as an opaque COPY run — units got a green/dark halo
    # instead of a translucent shadow. Caught by byte-diffing against Kull's
    # makespr.exe-built GU16.SPR: exe had 410 shadow px, we had 0.)
    _SHADOW_STAMP = (0xFF, 0x00, 0xFF, ALL_ALPHA)

    for j in range(height):
        for i in range(width):
            r, g, b, a = image_pixels[j][i]
            sr, sg, sb = shadow_pixels[j][i][:3]
            if white_bg:
                if (sr, sg, sb) != (0xFF, 0xFF, 0xFF):  # shadow pixel present
                    if a != ALL_ALPHA:
                        image_pixels[j][i] = _SHADOW_STAMP
            else:
                if (sr, sg, sb) != (0x00, 0x00, 0x00):  # nonzero = shadow
                    if a != ALL_ALPHA:
                        image_pixels[j][i] = _SHADOW_STAMP


# ─────────────────────────────────────────────────────────────────────────────
# RLE scanline encoder
# ─────────────────────────────────────────────────────────────────────────────

def _eoln(tag_byte: int, pos: int, width: int) -> int:
    if pos >= width:
        return tag_byte | EOLN_FLAG
    return tag_byte

def encode_scanline(row: list[tuple[int,int,int,int]],
                    width: int,
                    enc: PixelEncoder) -> tuple[bool, list[int]]:
    """
    Encode one row of ARGB pixels into Pixel16 RLE words.

    Returns (is_empty, words) where is_empty=True means the entire row is
    transparent (caller should write EMPTY_TABLE_ENTRY).

    Run types:
      Chromakey  — pixel==0x0000 and alpha==0x00  (transparent)
      Shadow     — pixel==shadow_pixel             (shadow colour)
      Feathered  — 0x00 < alpha < 0xFF            (partial alpha, 1 px per run)
      Copy       — alpha==0xFF, not shadow         (opaque run)
    """
    words: list[int] = []
    pos = 0

    while pos < width:
        r, g, b, a = row[pos]
        pix16 = enc.to_16(r, g, b) if a != NO_ALPHA else CHROMAKEY_PIXEL

        if pix16 == CHROMAKEY_PIXEL and a == NO_ALPHA:
            # ── chromakey run ─────────────────────────────────────────────
            run_len = 0
            while pos < width:
                r2, g2, b2, a2 = row[pos]
                p2 = enc.to_16(r2, g2, b2) if a2 != NO_ALPHA else CHROMAKEY_PIXEL
                if not (p2 == CHROMAKEY_PIXEL and a2 == NO_ALPHA):
                    break
                pos += 1
                run_len += 1
            if run_len >= width:
                return True, []   # empty row
            tag = _eoln(CHROMAKEY_RUN_ID, pos, width)
            words.append((tag << 8) | run_len)

        elif pix16 == enc.shadow_pixel:
            # ── shadow run ───────────────────────────────────────────────
            run_len = 0
            while pos < width:
                r2, g2, b2, a2 = row[pos]
                p2 = enc.to_16(r2, g2, b2)
                if p2 != enc.shadow_pixel:
                    break
                pos += 1
                run_len += 1
            tag = _eoln(SHADOW_RUN_ID, pos, width)
            words.append((tag << 8) | run_len)

        elif a != NO_ALPHA and a != ALL_ALPHA:
            # ── feathered run (single pixel) ──────────────────────────────
            # No premultiply here: pixels are already alpha-premultiplied at
            # load time (see load_tiff_rgba) exactly like the original tool.
            pos += 1
            tag = _eoln(FEATHERED_RUN_ID, pos, width)
            words.append((tag << 8) | a)
            words.append(pix16)

        elif a == ALL_ALPHA:
            # ── copy run ─────────────────────────────────────────────────
            header_idx = len(words)
            words.append(0)        # placeholder
            run_len = 0
            while pos < width:
                r2, g2, b2, a2 = row[pos]
                p2 = enc.to_16(r2, g2, b2)
                if p2 == enc.shadow_pixel or a2 != ALL_ALPHA:
                    break
                words.append(p2)
                pos += 1
                run_len += 1
            tag = _eoln(COPY_RUN_ID, pos, width)
            words[header_idx] = (tag << 8) | run_len

        else:
            sys.exit(f"Error in bitmap data: pixel at col {pos} has no associated alpha.")

    return False, words


def encode_frame(pixels: list[list[tuple[int,int,int,int]]],
                 width: int, height: int,
                 enc: PixelEncoder) -> bytes:
    """
    Build the binary frame block:
      u16  height
      u16  row_offset[height]    (relative to start of data section)
      u16  data[…]

    Empty rows get EMPTY_TABLE_ENTRY (0xFFFF).
    Postcondition: returned bytes is the complete encodable frame blob.
    """
    table: list[int] = [height]
    data_words: list[int] = []
    row_offsets: list[int] = []

    for y in range(height):
        empty, row_words = encode_scanline(pixels[y], width, enc)
        if empty:
            row_offsets.append(EMPTY_TABLE_ENTRY)
        else:
            row_offsets.append(len(data_words))
            data_words.extend(row_words)

    # assemble: height, then offsets, then data
    all_words = [height] + row_offsets + data_words
    return struct.pack(f"<{len(all_words)}H", *all_words)


# ─────────────────────────────────────────────────────────────────────────────
# TIFF loading
# ─────────────────────────────────────────────────────────────────────────────

def load_tiff_rgba(path: Path) -> Optional[list[list[tuple[int,int,int,int]]]]:
    """
    Load a 32-bit ARGB TIFF; return pixel grid or None if file missing.

    Every pixel is alpha-PREMULTIPLIED on load: c = ceil(c*a/255). This
    mirrors the original makespr.exe pipeline (verified byte-exact against
    Kull's GU16.SPR golden build): full-frame feathered pixels carry the
    premultiplied colour, and minis average the premultiplied values —
    premultiplying once at load reproduces both. Opaque pixels (a=255) are
    unchanged; fully transparent pixels become (0,0,0,0) = chromakey.
    """
    if not path.exists():
        return None
    img = Image.open(path)
    if "A" not in img.getbands():
        # 24-bit RGB input: every pixel becomes opaque (alpha 255), so the
        # background is NOT keyed and the frame encodes as a full bitmap
        # (~14KB instead of ~2.4KB). Source art must be 32-bit ARGB TIFF.
        print(f"  [warn] {path.name} has no alpha channel — background will "
              f"not be keyed (frame will be a full opaque bitmap)")
    img = img.convert("RGBA")
    w, h = img.size
    data = list(img.getdata())
    return [
        [
            (lambda r, g, b, a: (
                (r * a + 254) // 255,   # == ceil(c*a/255)
                (g * a + 254) // 255,
                (b * a + 254) // 255,
                a,
            ))(*data[y * w + x])
            for x in range(w)
        ]
        for y in range(h)
    ]


def load_tiff_rgb(path: Path) -> Optional[list[list[tuple[int,int,int]]]]:
    """Load a 24-bit RGB TIFF (shadow); return pixel grid or None if missing."""
    if not path.exists():
        return None
    img = Image.open(path).convert("RGB")
    w, h = img.size
    data = list(img.getdata())
    return [[data[y * w + x] for x in range(w)] for y in range(h)]


# ─────────────────────────────────────────────────────────────────────────────
# Script parser
# ─────────────────────────────────────────────────────────────────────────────

class ParseError(Exception):
    pass

def _tokenize(text: str) -> list[str]:
    """Strip comments, flatten to token stream."""
    tokens: list[str] = []
    for line in text.splitlines():
        line = line.split("#")[0]
        tokens.extend(line.split())
    return tokens

class TokenStream:
    def __init__(self, tokens: list[str]):
        self._t = tokens
        self._i = 0

    def peek(self) -> Optional[str]:
        return self._t[self._i] if self._i < len(self._t) else None

    def next(self) -> str:
        if self._i >= len(self._t):
            raise ParseError("Unexpected end of script")
        tok = self._t[self._i]
        self._i += 1
        return tok

    def expect(self, val: str) -> None:
        tok = self.next()
        if tok != val:
            raise ParseError(f"Expected '{val}', got '{tok}'")

    def next_int(self) -> int:
        return int(self.next())

    def next_float(self) -> float:
        return float(self.next())

    def has(self) -> bool:
        return self._i < len(self._t)


# ─────────────────────────────────────────────────────────────────────────────
# Data structures for parsed script
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class HotPoint:
    x: int
    y: int

@dataclass
class SpriteAction:
    num_frames: int = 0
    first_frame: int = 0
    width: int = 96
    height: int = 72
    hot_points: list[HotPoint] = field(default_factory=list)  # 5 for multi-facing, 1 for single

@dataclass
class AnimData:
    anim_type: int = 0
    num_frames: int = 0
    playback_time: int = 1000
    delay: int = 0
    frame_data: list[int] = field(default_factory=list)
    move_deltas: list[tuple[int,int]] = field(default_factory=list)
    transparencies: list[int] = field(default_factory=list)

@dataclass
class UnitShieldPoints:
    move: list[HotPoint] = field(default_factory=list)
    attack: list[HotPoint] = field(default_factory=list)
    idle: list[HotPoint] = field(default_factory=list)
    victory: list[HotPoint] = field(default_factory=list)
    work: list[HotPoint] = field(default_factory=list)

@dataclass
class UnitScript:
    move: Optional[SpriteAction] = None
    move_anim: Optional[AnimData] = None
    attack: Optional[SpriteAction] = None
    attack_anim: Optional[AnimData] = None
    idle: Optional[SpriteAction] = None
    idle_anim: Optional[AnimData] = None
    victory: Optional[SpriteAction] = None
    victory_anim: Optional[AnimData] = None
    is_death: bool = False
    is_directional: bool = False   # UNIT_SPRITE_ATTACK_IS_DIRECTIONAL
    work: Optional[SpriteAction] = None
    work_anim: Optional[AnimData] = None
    move_offsets: list[tuple[int,int]] = field(default_factory=list)
    shield_points: Optional[UnitShieldPoints] = None

@dataclass
class GoodScript:
    idle: Optional[SpriteAction] = None
    idle_anim: Optional[AnimData] = None

@dataclass
class EffectScript:
    play: Optional[SpriteAction] = None
    play_anim: Optional[AnimData] = None
    flash: Optional[SpriteAction] = None
    flash_anim: Optional[AnimData] = None


# ─────────────────────────────────────────────────────────────────────────────
# Script parsing logic
# ─────────────────────────────────────────────────────────────────────────────

def _parse_hot_points_multi(ts: TokenStream) -> list[HotPoint]:
    """Parse 5 x,y pairs (multi-facing actions: move/attack/work)."""
    pts = []
    for _ in range(5):
        x = ts.next_int()
        y = ts.next_int()
        pts.append(HotPoint(x, y))
    return pts

def _parse_hot_point_single(ts: TokenStream) -> list[HotPoint]:
    """Parse 1 x,y pair (single-facing actions: idle/victory)."""
    x = ts.next_int()
    y = ts.next_int()
    return [HotPoint(x, y)]

def _parse_sprite_action(ts: TokenStream, multi_facing: bool) -> SpriteAction:
    ts.expect("{")
    sa = SpriteAction()
    while ts.peek() != "}":
        tag = ts.next()
        if tag == "SPRITE_NUM_FRAMES":
            sa.num_frames = ts.next_int()
        elif tag == "SPRITE_FIRST_FRAME":
            sa.first_frame = ts.next_int()
        elif tag == "SPRITE_WIDTH":
            sa.width = ts.next_int()
        elif tag == "SPRITE_HEIGHT":
            sa.height = ts.next_int()
        elif tag == "SPRITE_HOT_POINTS":
            sa.hot_points = _parse_hot_points_multi(ts)
        elif tag == "SPRITE_HOT_POINT":
            sa.hot_points = _parse_hot_point_single(ts)
        else:
            raise ParseError(f"Unknown sprite action tag: {tag}")
    ts.expect("}")
    return sa

def _parse_anim(ts: TokenStream) -> AnimData:
    ts.expect("{")
    ad = AnimData()
    while ts.peek() != "}":
        tag = ts.next()
        if tag == "ANIM_TYPE":
            ad.anim_type = ts.next_int()
        elif tag == "ANIM_NUM_FRAMES":
            ad.num_frames = ts.next_int()
        elif tag == "ANIM_PLAYBACK_TIME":
            ad.playback_time = ts.next_int()
        elif tag == "ANIM_DELAY":
            ad.delay = ts.next_int()
        elif tag == "ANIM_FRAME_DATA":
            ad.frame_data = [ts.next_int() for _ in range(ad.num_frames)]
        elif tag == "ANIM_MOVE_DELTAS":
            flag = ts.next_int()
            if flag == 1:
                ts.expect("{")
                ad.move_deltas = []
                while ts.peek() != "}":
                    x = ts.next_int()
                    y = ts.next_int()
                    ad.move_deltas.append((x, y))
                ts.expect("}")
            # flag==0 → empty, leave list empty
        elif tag == "ANIM_TRANSPARENCIES":
            flag = ts.next_int()
            if flag == 1:
                ts.expect("{")
                ad.transparencies = []
                while ts.peek() != "}":
                    ad.transparencies.append(ts.next_int())
                ts.expect("}")
        else:
            raise ParseError(f"Unknown ANIM tag: {tag}")
    ts.expect("}")
    return ad

def _parse_shield_5(ts: TokenStream) -> list[HotPoint]:
    return [HotPoint(ts.next_int(), ts.next_int()) for _ in range(5)]

def _parse_unit_sprite(ts: TokenStream) -> UnitScript:
    ts.expect("{")
    us = UnitScript()
    while ts.peek() != "}":
        tag = ts.next()
        if tag == "UNIT_SPRITE_MOVE":
            flag = ts.next_int()
            if flag:
                us.move = _parse_sprite_action(ts, multi_facing=True)
                anim_flag = ts.next()   # "ANIM"
                assert anim_flag == "ANIM"
                assert ts.next_int() == 1
                us.move_anim = _parse_anim(ts)
        elif tag == "UNIT_SPRITE_ATTACK":
            flag = ts.next_int()
            # optional UNIT_SPRITE_ATTACK_IS_DIRECTIONAL <n> precedes the block
            # (e.g. Cradle 5 Legion GU16) — mirrors VICTORY's IS_DEATH tag
            if ts.peek() == "UNIT_SPRITE_ATTACK_IS_DIRECTIONAL":
                ts.next()
                us.is_directional = bool(ts.next_int())
            if flag:
                us.attack = _parse_sprite_action(ts, multi_facing=True)
                ts.next(); ts.next_int()
                us.attack_anim = _parse_anim(ts)
        elif tag == "UNIT_SPRITE_IDLE":
            flag = ts.next_int()
            if flag:
                us.idle = _parse_sprite_action(ts, multi_facing=False)
                ts.next(); ts.next_int()
                us.idle_anim = _parse_anim(ts)
        elif tag == "UNIT_SPRITE_VICTORY":
            flag = ts.next_int()
            if flag:
                death_tag = ts.next()
                assert death_tag == "UNIT_SPRITE_IS_DEATH"
                us.is_death = bool(ts.next_int())
                us.victory = _parse_sprite_action(ts, multi_facing=False)
                ts.next(); ts.next_int()
                us.victory_anim = _parse_anim(ts)
            else:
                # consume optional UNIT_SPRITE_IS_DEATH if present without block
                if ts.peek() == "UNIT_SPRITE_IS_DEATH":
                    ts.next(); ts.next_int()
        elif tag == "UNIT_SPRITE_WORK":
            flag = ts.next_int()
            if flag:
                us.work = _parse_sprite_action(ts, multi_facing=True)
                ts.next(); ts.next_int()
                us.work_anim = _parse_anim(ts)
        elif tag == "UNIT_SPRITE_FIREPOINTS":
            flag = ts.next_int()
            if flag:
                ts.expect("{"); _consume_block(ts)
        elif tag == "UNIT_SPRITE_FIREPOINTS_WORK":
            flag = ts.next_int()
            if flag:
                ts.expect("{"); _consume_block(ts)
        elif tag == "UNIT_SPRITE_MOVEOFFSETS":
            flag = ts.next_int()
            if flag:
                ts.expect("{")
                us.move_offsets = []
                while ts.peek() != "}":
                    x = ts.next_int(); y = ts.next_int()
                    us.move_offsets.append((x, y))
                ts.expect("}")
        elif tag == "UNIT_SPRITE_SHIELDPOINTS":
            flag = ts.next_int()
            if flag:
                ts.expect("{")
                sp = UnitShieldPoints()
                while ts.peek() != "}":
                    stag = ts.next()
                    if stag == "UNIT_SPRITE_SHIELDPOINTS_MOVE":
                        sp.move = _parse_shield_5(ts)
                    elif stag == "UNIT_SPRITE_SHIELDPOINTS_ATTACK":
                        sp.attack = _parse_shield_5(ts)
                    elif stag == "UNIT_SPRITE_SHIELDPOINTS_IDLE":
                        sp.idle = _parse_shield_5(ts)
                    elif stag == "UNIT_SPRITE_SHIELDPOINTS_VICTORY":
                        sp.victory = _parse_shield_5(ts)
                    elif stag == "UNIT_SPRITE_SHIELDPOINTS_WORK":
                        sp.work = _parse_shield_5(ts)
                us.shield_points = sp
                ts.expect("}")
        else:
            raise ParseError(f"Unknown UNIT_SPRITE tag: {tag}")
    ts.expect("}")
    return us

def _consume_block(ts: TokenStream) -> None:
    """Consume tokens up to and including the matching '}'."""
    depth = 1
    while depth > 0:
        tok = ts.next()
        if tok == "{": depth += 1
        elif tok == "}": depth -= 1

def _parse_good_sprite(ts: TokenStream) -> GoodScript:
    ts.expect("{")
    gs = GoodScript()
    while ts.peek() != "}":
        tag = ts.next()
        if tag == "GOOD_SPRITE_IDLE":
            flag = ts.next_int()
            if flag:
                gs.idle = _parse_sprite_action(ts, multi_facing=False)
                ts.next(); ts.next_int()
                gs.idle_anim = _parse_anim(ts)
    ts.expect("}")
    return gs

def _parse_effect_sprite(ts: TokenStream) -> EffectScript:
    ts.expect("{")
    es = EffectScript()
    while ts.peek() != "}":
        tag = ts.next()
        if tag == "EFFECT_SPRITE_PLAY":
            flag = ts.next_int()
            if flag:
                es.play = _parse_sprite_action(ts, multi_facing=False)
                ts.next(); ts.next_int()
                es.play_anim = _parse_anim(ts)
        elif tag == "EFFECT_SPRITE_FLASH":
            flag = ts.next_int()
            if flag:
                es.flash = _parse_sprite_action(ts, multi_facing=False)
                ts.next(); ts.next_int()
                es.flash_anim = _parse_anim(ts)
    ts.expect("}")
    return es

def parse_script(text: str) -> tuple[str, object]:
    """
    Parse a script file.
    Returns (sprite_type, parsed_object):
      sprite_type in {'UNIT', 'GOOD', 'EFFECT'}
    Precondition: text is the full contents of a .txt script file.
    """
    tokens = _tokenize(text)
    ts = TokenStream(tokens)
    ts.next()    # consume leading required number (ignored)
    sprite_type = ts.next()
    if sprite_type == "UNIT_SPRITE":
        return "UNIT", _parse_unit_sprite(ts)
    elif sprite_type == "GOOD_SPRITE":
        return "GOOD", _parse_good_sprite(ts)
    elif sprite_type == "EFFECT_SPRITE":
        return "EFFECT", _parse_effect_sprite(ts)
    else:
        raise ParseError(f"Unknown sprite type: {sprite_type}")


# ─────────────────────────────────────────────────────────────────────────────
# TIFF filename construction (§4.1)
# ─────────────────────────────────────────────────────────────────────────────

def unit_image_path(base_dir: Path, sprite_num: str, action: str, facing: int, frame: int) -> Path:
    """GU{NN}{action}A{facing}.{frame}.TIF  (action: M/A/I/V/W)"""
    name = f"GU{sprite_num}{action}A{facing}.{frame}.TIF"
    return base_dir / name

def unit_shadow_path(base_dir: Path, sprite_num: str, action: str, facing: int, frame: int) -> Path:
    name = f"GU{sprite_num}{action}S{facing}.{frame}.TIF"
    return base_dir / name

def good_image_path(base_dir: Path, sprite_num: str, frame: int) -> Path:
    return base_dir / f"GG{sprite_num}A.{frame}.TIF"

def good_shadow_path(base_dir: Path, sprite_num: str, frame: int) -> Path:
    return base_dir / f"GG{sprite_num}S.{frame}.TIF"

def city_image_path(base_dir: Path, sprite_num: str, frame: int) -> Path:
    return base_dir / f"GC{sprite_num}A.{frame}.TIF"

def city_shadow_path(base_dir: Path, sprite_num: str, frame: int) -> Path:
    return base_dir / f"GC{sprite_num}S.{frame}.TIF"

def effect_image_path(base_dir: Path, sprite_num: str, ef: str, frame: int) -> Path:
    """ef: 'E' for play, 'F' for flash"""
    return base_dir / f"GX{sprite_num}{ef}A.{frame}.TIF"

def effect_shadow_path(base_dir: Path, sprite_num: str, ef: str, frame: int) -> Path:
    return base_dir / f"GX{sprite_num}{ef}S.{frame}.TIF"


# ─────────────────────────────────────────────────────────────────────────────
# Frame loading and encoding pipeline
# ─────────────────────────────────────────────────────────────────────────────

def _load_and_merge(img_path: Path, shd_path: Path,
                    width: int, height: int,
                    enc: PixelEncoder) -> Optional[list[list[tuple[int,int,int,int]]]]:
    """Load a frame image + optional shadow and merge; return pixel grid or None."""
    pixels = load_tiff_rgba(img_path)
    if pixels is None:
        return None
    shadow = load_tiff_rgb(shd_path)
    if shadow is not None:
        merge_shadow(pixels, shadow, width, height, enc)
    return pixels


def _downscale_half(pixels: list[list[tuple[int,int,int,int]]],
                    width: int, height: int) -> list[list[tuple[int,int,int,int]]]:
    """
    Box-downscale an RGBA grid to (width//2 × height//2) for the mini (zoomed-out)
    frame. Fully-transparent source pixels are excluded from the colour average so
    the background never bleeds in; a mini pixel is transparent only when all four
    source pixels are transparent. Mirrors the engine's quarter-size minis, which
    CTP2 renders at normal map zoom (blank minis => invisible units).

    NOTE: kept for compile_good/compile_city/compile_effect. compile_unit now
    uses the faithful _quarter_rgba/_quarter_rgb port of the original tool's
    spriteutils_CreateQuarterSize pipeline (verified against Kull's
    makespr.exe-built GU16.SPR).
    """
    mw, mh = width // 2, height // 2
    out: list[list[tuple[int,int,int,int]]] = []
    for my in range(mh):
        row: list[tuple[int,int,int,int]] = []
        for mx in range(mw):
            ar = ag = ab = n = 0
            for dy in (0, 1):
                sy = my * 2 + dy
                if sy >= height:
                    continue
                for dx in (0, 1):
                    sx = mx * 2 + dx
                    if sx >= width:
                        continue
                    r, g, b, a = pixels[sy][sx]
                    if a != NO_ALPHA:
                        ar += r; ag += g; ab += b; n += 1
            row.append((ar // n, ag // n, ab // n, ALL_ALPHA) if n else (0, 0, 0, 0))
        out.append(row)
    return out


def _quarter_rgba(pixels: list[list[tuple[int,int,int,int]]],
                  width: int, height: int) -> list[list[tuple[int,int,int,int]]]:
    """
    Faithful port of spriteutils_CreateQuarterSize(aa=TRUE) +
    spriteutils_AveragePixel32 (spriteutils.cpp:551-604): each mini pixel is
    ceil((p1+p2+p3+p4)/4) per component — INCLUDING alpha (partial alpha ⇒
    feathered runs, exactly like the original tool) and INCLUDING fully
    transparent pixels' RGB in the average.
    """
    mw, mh = width // 2, height // 2
    return [
        [
            tuple(
                (c1 + c2 + c3 + c4 + 3) // 4    # == ceil(sum/4.0)
                for c1, c2, c3, c4 in zip(pixels[i*2][j*2],   pixels[i*2][j*2+1],
                                          pixels[i*2+1][j*2], pixels[i*2+1][j*2+1])
            )
            for j in range(mw)
        ]
        for i in range(mh)
    ]


def _quarter_rgb(pixels: list[list[tuple[int,int,int]]],
                 width: int, height: int) -> list[list[tuple[int,int,int]]]:
    """
    Faithful port of spriteutils_CreateQuarterSize(aa=FALSE) for shadow
    buffers: nearest-sample the top-left pixel of each 2×2 block.
    """
    mw, mh = width // 2, height // 2
    return [[pixels[i*2][j*2] for j in range(mw)] for i in range(mh)]


def load_and_encode_frame(img_path: Path, shd_path: Path,
                           width: int, height: int,
                           enc: PixelEncoder) -> Optional[bytes]:
    """
    Load image + optional shadow, merge, encode.
    Returns encoded bytes or None if image missing.
    """
    pixels = _load_and_merge(img_path, shd_path, width, height, enc)
    if pixels is None:
        print(f"  [warn] missing: {img_path.name}")
        return None
    return encode_frame(pixels, width, height, enc)


# ─────────────────────────────────────────────────────────────────────────────
# SPR binary serialisation
# ─────────────────────────────────────────────────────────────────────────────

def write_u16(buf: bytearray, v: int) -> None:
    buf += struct.pack("<H", v & 0xFFFF)

def write_u32(buf: bytearray, v: int) -> None:
    buf += struct.pack("<I", v & 0xFFFFFFFF)

def write_i16(buf: bytearray, v: int) -> None:
    buf += struct.pack("<h", v)

def pack_hot_points(pts: list[HotPoint]) -> bytes:
    out = bytearray()
    for p in pts:
        write_u32(out, p.x)
        write_u32(out, p.y)
    return bytes(out)


def _encode_blank_spr_frame(height: int) -> bytes:
    """All-transparent frame: height u16 + height×EMPTY_TABLE_ENTRY u16s.
    Safe to pass to spriteutils_ConvertPixelFormat (all rows skipped)."""
    words = [height] + [EMPTY_TABLE_ENTRY] * height
    return struct.pack(f"<{len(words)}H", *words)


def pack_anim(ad: AnimData) -> bytes:
    """
    Serialise an AnimData to the CTP2 VERSION0 SPR stream.
    Layout from SpriteFile::ReadAnimDataFull / WriteAnimData:
      type(u16)  num_frames(u16)  playback_time(u16)  delay(u16)
      frame_data(u16×N)
      move_deltas(POINT×N)  — POINT = {LONG x, LONG y} = 8 bytes on Win32
      transparencies(u16×N)
    Arrays are padded to num_frames entries if shorter: frame_data and
    move_deltas with zeros, transparencies with 15 (opaque; see below).
    """
    out = bytearray()
    out += struct.pack("<H", ad.anim_type)
    out += struct.pack("<H", ad.num_frames)
    out += struct.pack("<H", ad.playback_time)   # uint16, NOT uint32
    out += struct.pack("<H", ad.delay)           # uint16, NOT uint32
    for f in ad.frame_data:
        out += struct.pack("<H", f)
    # move_deltas: POINT[num_frames] — two sint32s per entry (8 bytes each)
    deltas = list(ad.move_deltas)
    while len(deltas) < ad.num_frames:
        deltas.append((0, 0))
    for dx, dy in deltas[:ad.num_frames]:
        out += struct.pack("<ii", int(dx), int(dy))
    # transparencies: uint16[num_frames] — engine blend alpha per frame
    # (alpha = value << 3). 15 = NO_TRANSPARENCY (opaque, Actor.h); 0 = fully
    # invisible: UnitActor adopts this value (UnitActor.cpp:470) and
    # pixelutils_Blend16 returns pure background at alpha 0. Stock sprites
    # carry 15s, so pad omitted entries with 15, never 0.
    transp = list(ad.transparencies)
    if transp and all(t == 0 for t in transp):
        print("  [warn] anim declares all-zero ANIM_TRANSPARENCIES — the unit "
              "will be INVISIBLE in-game (0 = fully transparent; use 15 for opaque)")
    while len(transp) < ad.num_frames:
        transp.append(15)
    for t in transp[:ad.num_frames]:
        out += struct.pack("<H", t)              # uint16, NOT uint8
    return bytes(out)


# ─────────────────────────────────────────────────────────────────────────────
# Top-level compile functions
# ─────────────────────────────────────────────────────────────────────────────

ACTION_CHARS = {
    "move":    ("M", 5),   # (file letter, num facings)
    "attack":  ("A", 5),
    "idle":    ("I", 1),
    "victory": ("V", 1),
    "work":    ("W", 5),
}

# CTP2 SpriteFile constants (from SpriteFile.h / Sprite.h)
_K_SPRITEFILE_TAG      = 0x53505246   # 'FRPS' in little-endian
_K_SPRITEFILE_VERSION0 = 0x00010003
_SPRITEFILETYPE_UNIT   = 4
_SPRITETYPE_NORMAL     = 0            # Sprite (1 facing)
_SPRITETYPE_FACED      = 1            # FacedSprite (k_NUM_FACINGS facings)
_K_NUM_FACINGS         = 5
_K_NUM_FIREPOINTS      = 8
_UNITACTION_MAX        = 5
_POINT_SIZE            = 8            # sizeof(POINT) = sizeof(LONG)*2 on Win32


def compile_unit(script_dir: Path, sprite_id: int, sprite: UnitScript,
                 enc: PixelEncoder, is_city: bool = False) -> bytes:
    """
    Compile all actions for a Unit sprite into a CTP2 VERSION0 SPR binary.

    Binary layout (from SpriteFile::ReadFull_v13 / ReadBasic_v13):
      12  file header  (tag u32, version u32, type u32)
      20  offset table (UNITACTION_MAX × u32, patched at end)
      per action:
        4  present flag (u32 TRUE/FALSE)
        if present:
          sprite header: spritetype(u16) width(u16) height(u16)
                         hot_points  first_frame(u16) num_frames(u16)
          size tables:   for each facing: ssizes(u32×N) msizes(u32×N)
          frame data:    for each facing: full_frames then mini_frames
          anim:          type(u16) nf(u16) time(u16) delay(u16)
                         frames(u16×N) move_deltas(POINT×N) transp(u16×N)
      888 trailing:  numFirePointsWork(u16) fire_pts_work fire_pts
                     move_offsets shield_points hasDeath hasDirectional
    """
    nn = f"{sprite_id:02d}"
    sprite_dir = script_dir / str(sprite_id)

    out = bytearray()

    # ── File header (12 bytes) ──────────────────────────────────────────────
    out += struct.pack("<I", _K_SPRITEFILE_TAG)       # 'FRPS'
    out += struct.pack("<I", _K_SPRITEFILE_VERSION0)  # 0x00010003
    out += struct.pack("<I", _SPRITEFILETYPE_UNIT)    # 4

    # ── Offset table (5 × u32 = 20 bytes, patched after writing data) ───────
    OFFSET_TABLE_POS = len(out)   # = 12
    out += struct.pack(f"<{_UNITACTION_MAX}I", *([0] * _UNITACTION_MAX))

    # ── Per-action data ─────────────────────────────────────────────────────
    actions = [
        ("move",    sprite.move,    sprite.move_anim,    "M", 5),
        ("attack",  sprite.attack,  sprite.attack_anim,  "A", 5),
        ("idle",    sprite.idle,    sprite.idle_anim,    "I", 1),
        ("victory", sprite.victory, sprite.victory_anim, "V", 1),
        ("work",    sprite.work,    sprite.work_anim,    "W", 5),
    ]

    offsets = [0xFFFFFFFF] * _UNITACTION_MAX   # absent sentinel

    for action_idx, (name, sa, ad, letter, n_facings) in enumerate(actions):
        if sa is None:
            out += struct.pack("<I", 0)    # uint32 FALSE
            continue

        # offset = position of sprite data (right after the u32 present flag)
        offsets[action_idx] = len(out) + 4
        out += struct.pack("<I", 1)        # uint32 TRUE

        # ── Sprite type + dimensions ──────────────────────────────────────
        is_faced = (n_facings > 1)
        out += struct.pack("<H", _SPRITETYPE_FACED if is_faced else _SPRITETYPE_NORMAL)
        out += struct.pack("<H", sa.width)
        out += struct.pack("<H", sa.height)

        # ── Hot points (POINT = two sint32s = 8 bytes each) ───────────────
        if is_faced:
            pts = list(sa.hot_points[:_K_NUM_FACINGS])
            while len(pts) < _K_NUM_FACINGS:
                pts.append(HotPoint(0, 0))
            for p in pts:
                out += struct.pack("<ii", p.x, p.y)
        else:
            p = sa.hot_points[0] if sa.hot_points else HotPoint(0, 0)
            out += struct.pack("<ii", p.x, p.y)

        # ── first_frame, num_frames ────────────────────────────────────────
        out += struct.pack("<H", sa.first_frame)
        out += struct.pack("<H", sa.num_frames)

        # ── Pre-encode frames (full + mini) for all facings ───────────────
        full_frames: list[list[bytes]] = []
        mini_frames: list[list[bytes]] = []
        for facing in range(1, n_facings + 1):
            ff, mf = [], []
            # Single-facing actions (IDLE, VICTORY) use facing digit 4 in their
            # filenames (GU16IA4.*, GU16VA4.*) — the default map facing.
            # Verified against Kull's Cradle 5 Legion (makespr.exe golden build).
            file_facing = 4 if n_facings == 1 else facing
            for frame_idx in range(sa.first_frame, sa.first_frame + sa.num_frames):
                img_p = unit_image_path(sprite_dir, nn, letter, file_facing, frame_idx)
                shd_p = unit_shadow_path(sprite_dir, nn, letter, file_facing, frame_idx)
                image = load_tiff_rgba(img_p)
                if image is None:
                    print(f"  [warn] missing: {img_p.name}")
                    ff.append(_encode_blank_spr_frame(sa.height))
                    mf.append(_encode_blank_spr_frame(sa.height // 2))
                    continue
                shadow = load_tiff_rgb(shd_p)
                # Original-tool pipeline (FacedSprite.cpp:143-152, verified
                # byte-identical vs Kull's makespr.exe GU16.SPR):
                #   1. quarter the PRISTINE image (aa averaging, alpha too)
                #   2. quarter the shadow (nearest-sample)
                #   3. merge shadow into full and mini independently, encode.
                mini_img = _quarter_rgba(image, sa.width, sa.height)
                mini_shd = _quarter_rgb(shadow, sa.width, sa.height) if shadow else None
                if shadow:
                    merge_shadow(image, shadow, sa.width, sa.height, enc)
                if mini_shd:
                    merge_shadow(mini_img, mini_shd, sa.width // 2, sa.height // 2, enc)
                ff.append(encode_frame(image, sa.width, sa.height, enc))
                mf.append(encode_frame(mini_img, sa.width // 2, sa.height // 2, enc))
            full_frames.append(ff)
            mini_frames.append(mf)

        # ── Size tables: for each facing j: ssizes(u32×N) msizes(u32×N) ──
        for j in range(n_facings):
            for i in range(sa.num_frames):
                out += struct.pack("<I", len(full_frames[j][i]))
            for i in range(sa.num_frames):
                out += struct.pack("<I", len(mini_frames[j][i]))

        # ── Frame data: for each facing j: full frames then mini frames ───
        for j in range(n_facings):
            for i in range(sa.num_frames):
                out += full_frames[j][i]
            for i in range(sa.num_frames):
                out += mini_frames[j][i]

        # ── Anim data ────────────────────────────────────────────────────
        if ad:
            out += pack_anim(ad)
        else:
            dummy = AnimData(anim_type=1, num_frames=sa.num_frames,
                             playback_time=1000, delay=0,
                             frame_data=list(range(sa.num_frames)))
            out += pack_anim(dummy)

    # ── Trailing data (888 bytes read by ReadFull_v13 / ReadBasic_v13) ────
    out += struct.pack("<H", 0)                                              # numFirePointsWork
    out += bytes(_K_NUM_FIREPOINTS * _K_NUM_FACINGS * _POINT_SIZE)          # fire_pts_work
    out += struct.pack("<H", 0)                                              # separator
    out += bytes(_K_NUM_FIREPOINTS * _K_NUM_FACINGS * _POINT_SIZE)          # fire_pts
    out += bytes(_K_NUM_FACINGS * _POINT_SIZE)                               # move_offsets
    # shield points: UNITACTION_MAX × k_NUM_FACINGS POINTs, in enum order
    # (move, attack, idle, victory, work); script values when parsed, else
    # the (24,24) default. Verified against Kull's makespr.exe GU16.SPR.
    sp = sprite.shield_points
    sp_lists = ([sp.move, sp.attack, sp.idle, sp.victory, sp.work]
                if sp else [[]] * _UNITACTION_MAX)
    for pts in sp_lists:
        for k in range(_K_NUM_FACINGS):
            if k < len(pts):
                out += struct.pack("<ii", pts[k].x, pts[k].y)
            else:
                out += struct.pack("<ii", 24, 24)                            # default shield pos
    out += struct.pack("<H", 1 if sprite.is_death else 0)                    # hasDeath
    out += struct.pack("<H", 1 if sprite.is_directional else 0)              # hasDirectional

    # ── Patch offset table ──────────────────────────────────────────────────
    for i, off in enumerate(offsets):
        struct.pack_into("<I", out, OFFSET_TABLE_POS + i * 4, off)

    return bytes(out)


def compile_good(script_dir: Path, sprite_id: int, script: GoodScript,
                 enc: PixelEncoder) -> bytes:
    nn = f"{sprite_id:02d}"
    sprite_dir = script_dir / str(sprite_id)
    sa = script.idle
    ad = script.idle_anim

    out = bytearray()
    out += b"GSPRITE\x00"
    if sa is None:
        return bytes(out)

    out += struct.pack("<HHH", sa.num_frames, sa.width, sa.height)
    out += pack_hot_points(sa.hot_points)
    if ad:
        out += pack_anim(ad)

    for frame_idx in range(sa.first_frame, sa.first_frame + sa.num_frames):
        img_p = good_image_path(sprite_dir, nn, frame_idx)
        shd_p = good_shadow_path(sprite_dir, nn, frame_idx)
        encoded = load_and_encode_frame(img_p, shd_p, sa.width, sa.height, enc)
        if encoded:
            out += struct.pack("<I", len(encoded))
            out += encoded
        else:
            out += struct.pack("<I", 0)

    return bytes(out)


def compile_city(script_dir: Path, sprite_id: int, script: UnitScript,
                 enc: PixelEncoder) -> bytes:
    """Cities are unit sprites with only the IDLE action; 3-digit ID."""
    nnn = f"{sprite_id:03d}"
    sprite_dir = script_dir / str(sprite_id)
    sa = script.idle
    ad = script.idle_anim

    out = bytearray()
    out += b"CSPRITE\x00"
    if sa is None:
        return bytes(out)

    out += struct.pack("<HHH", sa.num_frames, sa.width, sa.height)
    out += pack_hot_points(sa.hot_points)
    if ad:
        out += pack_anim(ad)

    for frame_idx in range(sa.first_frame, sa.first_frame + sa.num_frames):
        img_p = city_image_path(sprite_dir, nnn, frame_idx)
        shd_p = city_shadow_path(sprite_dir, nnn, frame_idx)
        encoded = load_and_encode_frame(img_p, shd_p, sa.width, sa.height, enc)
        if encoded:
            out += struct.pack("<I", len(encoded))
            out += encoded
        else:
            out += struct.pack("<I", 0)

    return bytes(out)


def compile_effect(script_dir: Path, sprite_id: int, script: EffectScript,
                   enc: PixelEncoder) -> bytes:
    nn = f"{sprite_id:02d}"
    sprite_dir = script_dir / str(sprite_id)
    out = bytearray()
    out += b"XSPRITE\x00"

    for part, sa, ad, ef in [("play",  script.play,  script.play_anim,  "E"),
                               ("flash", script.flash, script.flash_anim, "F")]:
        if sa is None:
            out += struct.pack("<B", 0)
            continue
        out += struct.pack("<B", 1)
        out += struct.pack("<HHH", sa.num_frames, sa.width, sa.height)
        out += pack_hot_points(sa.hot_points)
        if ad:
            out += pack_anim(ad)
        for frame_idx in range(sa.first_frame, sa.first_frame + sa.num_frames):
            img_p = effect_image_path(sprite_dir, nn, ef, frame_idx)
            shd_p = effect_shadow_path(sprite_dir, nn, ef, frame_idx)
            encoded = load_and_encode_frame(img_p, shd_p, sa.width, sa.height, enc)
            if encoded:
                out += struct.pack("<I", len(encoded))
                out += encoded
            else:
                out += struct.pack("<I", 0)

    return bytes(out)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="makespr.py — compile CTP sprite files from TIFF images"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", action="store_true", help="Unit sprite")
    group.add_argument("-c", action="store_true", help="City sprite")
    group.add_argument("-g", action="store_true", help="Good sprite")
    group.add_argument("-x", action="store_true", help="Effect sprite")
    parser.add_argument("id", type=int, help="Sprite ID (0-99, cities 0-999)")
    parser.add_argument("--555", dest="use_555", action="store_true",
                        help="Use 555 pixel format (default: 565)")
    args = parser.parse_args()

    enc = PixelEncoder(use_555=args.use_555)
    script_dir = Path(".")

    # derive script filename and output name
    if args.u:
        script_file = script_dir / f"GU{args.id:02d}.TXT"
        out_file    = script_dir / f"GU{args.id:02d}.SPR"
        mode = "unit"
    elif args.c:
        script_file = script_dir / f"GC{args.id:03d}.TXT"
        out_file    = script_dir / f"GC{args.id:03d}.SPR"
        mode = "city"
    elif args.g:
        script_file = script_dir / f"GG{args.id:02d}.TXT"
        out_file    = script_dir / f"GG{args.id:02d}.SPR"
        mode = "good"
    else:  # -x
        script_file = script_dir / f"GX{args.id:02d}.TXT"
        out_file    = script_dir / f"GX{args.id:02d}.SPR"
        mode = "effect"

    if not script_file.exists():
        sys.exit(f"Script not found: {script_file}")

    text = script_file.read_text(encoding="utf-8", errors="replace")
    sprite_type, parsed = parse_script(text)

    if mode == "unit":
        data = compile_unit(script_dir, args.id, parsed, enc)
    elif mode == "city":
        data = compile_city(script_dir, args.id, parsed, enc)
    elif mode == "good":
        data = compile_good(script_dir, args.id, parsed, enc)
    else:
        data = compile_effect(script_dir, args.id, parsed, enc)

    out_file.write_bytes(data)
    print(f"Written: {out_file}  ({len(data)} bytes)")


if __name__ == "__main__":
    main()
