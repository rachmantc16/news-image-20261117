#!/usr/bin/env python3
"""Draw the news-image-20261117 entry: a newspaper front page summing up the
world news of Tuesday 17 November 2026, rendered with Pillow.

Run:  python3 draw.py   ->  writes entry.png (1024x1024) next to this file.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
PAPER = (247, 243, 233)      # warm off-white #f7f3e9
INK = (22, 20, 18)           # black ink
RED = (138, 31, 31)          # dark red accent #8a1f1f
SLATE = (70, 96, 107)        # muted colour for the water
ORANGE = (232, 119, 34)
YELLOW = (245, 197, 66)
SMOKE = (178, 172, 160)
SMOKE_LIGHT = (203, 197, 184)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

MARGIN = 56
CX0 = MARGIN                 # content left
CX1 = W - MARGIN             # content right
CW = CX1 - CX0               # content width (912)
CENTER = W // 2


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_width, draw):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def wrap_rich(tokens, max_width, draw):
    """Wrap a list of (word, font) tokens; returns lines of (word, font)."""
    space_w = draw.textlength(" ", font=tokens[0][1])
    lines, cur, cur_w = [], [], 0.0
    for word, fnt in tokens:
        w = draw.textlength(word, font=fnt)
        add = w if not cur else w + space_w
        if cur and cur_w + add > max_width:
            lines.append(cur)
            cur, cur_w = [(word, fnt)], w
        else:
            cur.append((word, fnt))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def tracked_width(text, fnt, draw, tracking):
    return draw.textlength(text, font=fnt) + tracking * max(0, len(text) - 1)


def draw_tracked(draw, xy, text, fnt, fill, tracking=0, anchor_center=False):
    x, y = xy
    if anchor_center:
        x = CENTER - tracked_width(text, fnt, draw, tracking) / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def fit_font(path, text, max_width, start_size, draw, tracking=0, min_size=10):
    size = start_size
    while size > min_size:
        fnt = font(path, size)
        if tracked_width(text, fnt, draw, tracking) <= max_width:
            return fnt
        size -= 2
    return font(path, min_size)


def star_points(cx, cy, r_out, r_in, n=12, phase=-math.pi / 2):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = phase + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_bridge(draw, box):
    """Flat graphic: bridge over wavy water, middle span broken, bursts."""
    gx0, gy0, gx1, gy1 = box
    cx = (gx0 + gx1) // 2
    deck_y = gy0 + 58                # top of the deck
    deck_h = 10
    gap = 66                         # half-width of the broken gap

    # water: sine waves in the lower part of the box
    for i, wy in enumerate(range(gy0 + 102, gy1 - 4, 15)):
        pts = []
        for x in range(gx0 + 6, gx1 - 4):
            pts.append((x, wy + 3.5 * math.sin((x - gx0) / 23.0 + i * 1.3)))
        draw.line(pts, fill=SLATE, width=2)

    # piers on the intact spans
    for px in (gx0 + 70, gx0 + 205, gx0 + 340, gx1 - 354, gx1 - 219, gx1 - 84):
        draw.rectangle([px, deck_y + deck_h, px + 14, gy1 - 22], fill=INK)

    # intact deck spans + a thinner chord beneath
    for x0, x1 in ((gx0 + 8, cx - gap), (cx + gap, gx1 - 8)):
        draw.rectangle([x0, deck_y, x1, deck_y + deck_h], fill=INK)
        draw.rectangle([x0, deck_y + deck_h + 7, x1, deck_y + deck_h + 11], fill=INK)
        # simple truss diagonals under the chord
        step = 46
        x = x0 + 6
        while x + step < x1:
            draw.line([x, deck_y + deck_h + 11, x + step, deck_y + deck_h + 26],
                      fill=INK, width=3)
            x += step + 8

    # fallen, tilted pieces of the broken span
    draw.polygon([(cx - gap, deck_y), (cx - gap + 12, deck_y),
                  (cx - 6, deck_y + 34), (cx - 18, deck_y + 34)], fill=INK)
    draw.polygon([(cx + gap - 12, deck_y), (cx + gap, deck_y),
                  (cx + 18, deck_y + 34), (cx + 6, deck_y + 34)], fill=INK)
    # a sunken chunk in the water
    draw.rectangle([cx - 26, gy1 - 34, cx + 26, gy1 - 24], fill=INK)

    # smoke above the break
    for sx, sy, r, col in ((cx - 34, gy0 + 22, 15, SMOKE),
                           (cx + 2, gy0 + 14, 19, SMOKE_LIGHT),
                           (cx + 38, gy0 + 24, 13, SMOKE)):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)

    # explosion bursts at both broken ends
    for bx, by, ro, ri in ((cx - gap, deck_y + 2, 34, 14), (cx + gap, deck_y + 2, 26, 11)):
        draw.polygon(star_points(bx, by, ro, ri), fill=ORANGE, outline=RED)
        draw.polygon(star_points(bx, by, ro * 0.52, ri * 0.55), fill=YELLOW)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- masthead block -------------------------------------------------
    draw.line([CX0, 40, CX1, 40], fill=INK, width=2)
    masthead = fit_font(SERIF_BOLD, "THE WORLD IN ONE PICTURE", CW, 72, draw, tracking=2)
    draw_tracked(draw, (0, 54), "THE WORLD IN ONE PICTURE", masthead, INK,
                 tracking=2, anchor_center=True)
    date_fnt = font(SANS_BOLD, 31)
    draw_tracked(draw, (0, 140), "TUESDAY · 17 NOVEMBER 2026", date_fnt, RED,
                 tracking=1, anchor_center=True)
    draw.line([CX0, 188, CX1, 188], fill=INK, width=5)
    draw.line([CX0, 198, CX1, 198], fill=INK, width=1)

    # ---- lead story ------------------------------------------------------
    lead_fnt = font(SERIF_BOLD, 76)
    y = 216
    for line in ("UKRAINE SHATTERS", "CRIMEA BRIDGE"):
        draw_tracked(draw, (0, y), line, lead_fnt, INK, tracking=1, anchor_center=True)
        y += 88
    sub_fnt = font(SERIF, 26)
    sub = ("Zelenskyy hails 'unprecedented operation' as Kerch crossing "
           "burns; Kyiv bridges hit in reply")
    for line in wrap(sub, sub_fnt, CW - 60, draw):
        w = draw.textlength(line, font=sub_fnt)
        draw.text(((W - w) / 2, y + 4), line, font=sub_fnt, fill=INK)
        y += 35

    # ---- lead graphic ----------------------------------------------------
    g_top = y + 18
    g_box = (CX0, g_top, CX1, g_top + 148)
    draw.rectangle(g_box, outline=INK, width=2)
    draw_bridge(draw, g_box)

    # ---- two columns ------------------------------------------------------
    col_top = g_top + 148 + 26
    col_w = 440
    right_x = CX1 - col_w
    divider_x = CENTER
    draw.line([divider_x, col_top, divider_x, col_top + 218], fill=INK, width=1)

    head_fnt = font(SERIF_BOLD, 25)
    body_fnt = font(SANS, 20)

    def column(x, headline, body):
        draw.line([x, col_top, x + col_w, col_top], fill=RED, width=3)
        yy = col_top + 12
        for line in wrap(headline, head_fnt, col_w, draw):
            draw.text((x, yy), line, font=head_fnt, fill=INK)
            yy += 31
        yy += 8
        for line in wrap(body, body_fnt, col_w, draw):
            draw.text((x, yy), line, font=body_fnt, fill=INK)
            yy += 28
        return yy

    left_end = column(
        CX0,
        "TRUMP IN ASIA: FIRST XI–PUTIN SUMMIT",
        "President Trump lands in Manila for ASEAN, then Shenzhen hosts the "
        "first-ever US–China–Russia trilateral on Thursday — nukes, Iran, "
        "Ukraine and trade on the table.")
    right_end = column(
        right_x,
        "TANKER ABLAZE IN HORMUZ",
        "A fourth tanker strikes a mine in the Strait of Hormuz as Iran "
        "fires drones at a US radar base in Bahrain and Washington weighs "
        "an alleged 'dirty bomb' plot.")
    cols_end = max(left_end, right_end)

    # ---- bottom strip ------------------------------------------------------
    strip_top = cols_end + 18
    draw.line([CX0, strip_top, CX1, strip_top], fill=INK, width=2)
    items = [
        ("JAPAN JETS SCRAMBLED",
         "Russian aircraft violate airspace; Tokyo protests."),
        ("COP31 DRAFT: $120BN",
         "Antalya talks push faster fossil-fuel phase-out."),
        ("ESTONIA SHUTS BORDER",
         "Crossings with Russia close 1 December over bomb plot."),
    ]
    strip_w = (CW - 48) // 3
    item_fnt_b = font(SANS_BOLD, 17)
    item_fnt = font(SANS, 17)
    for i, (head, rest) in enumerate(items):
        x = CX0 + i * (strip_w + 24)
        if i:
            draw.line([x - 12, strip_top + 12, x - 12, strip_top + 78],
                      fill=INK, width=1)
        tokens = [(w, item_fnt_b) for w in head.split()]
        tokens.append(("—", item_fnt))
        tokens += [(w, item_fnt) for w in rest.split()]
        yy = strip_top + 12
        space_w = draw.textlength(" ", font=item_fnt)
        for line in wrap_rich(tokens, strip_w, draw):
            xx = x
            for word, fnt in line:
                draw.text((xx, yy), word, font=fnt, fill=INK)
                xx += draw.textlength(word, font=fnt) + space_w
            yy += 22

    # ---- footer ------------------------------------------------------------
    foot_y = strip_top + 92
    draw.line([CX0, foot_y, CX1, foot_y], fill=INK, width=2)
    foot_fnt = font(SERIF_BOLD, 17)
    draw_tracked(draw, (0, foot_y + 10),
                 "ALL THE NEWS OF TUESDAY 17 NOVEMBER 2026 · IN ONE PICTURE",
                 foot_fnt, INK, tracking=1, anchor_center=True)

    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
