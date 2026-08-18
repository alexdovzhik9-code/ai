#!/usr/bin/env python3
"""
Generates the illustrative SVG scenery used across the site.

The site ships without photography on purpose: rather than stand-in stock
images, every visual is a layered vector scene built from one shared palette
(Bodden sea, dune sand, reed gold), so the art reads as part of the brand.
Replace any file in assets/img/ with real photography when it is available —
the markup uses plain <img>, so nothing else has to change.

Usage:  python3 tools/make-art.py
"""

import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "img"

# --- shared palette -------------------------------------------------------
P = {
    "sea_900": "#0d2830",
    "sea_800": "#123a46",
    "sea_700": "#184c5b",
    "sea_600": "#1f5f70",
    "sea_500": "#2f7787",
    "sea_400": "#5b9aa8",
    "sea_300": "#86b4bf",
    "sea_200": "#a9c8d0",
    "sand_50": "#fdfaf5",
    "sand_100": "#f2e8d6",
    "sand_200": "#e6d5b8",
    "sand_300": "#d8c39f",
    "sand_400": "#c3aa82",
    "sand_500": "#a98f6a",
    "reed_300": "#dcc characters",
    "reed_400": "#c9aa6b",
    "reed_500": "#b18d4d",
    "reed_600": "#96743a",
    "reed_700": "#7a5d2d",
    "reed_800": "#5d4622",
    "grass": "#7d8f63",
    "grass_dark": "#57663f",
    "grass_deep": "#3d4a2c",
    "wall": "#f6f1e7",
    "wall_shade": "#ded4c2",
    "glass": "#3f7f92",
    "glass_lit": "#f0cb84",
    "warm_light": "#ffd9a0",
}
P["reed_300"] = "#dcc characters"
P["reed_300"] = "#d8bd84"

# time-of-day skies: (zenith, mid, horizon)
SKIES = {
    "dawn":  ("#33566b", "#7d8ba0", "#f0c3a0"),
    "day":   ("#4f8ba6", "#8fb9c8", "#d9e6e3"),
    "gold":  ("#2c5878", "#c68f72", "#f8d5a2"),
    "dusk":  ("#1b3546", "#6b5e78", "#e0a184"),
    "blue":  ("#0f2a3a", "#1f4a60", "#4a7d92"),
    "clear": ("#3d7d9c", "#7fb0c4", "#cfe2e4"),
}


def rnd(seed):
    return random.Random(seed)


# ------------------------------------------------------------- path helpers
def smooth(points, close_to=None, w=None):
    """Catmull-Rom style smooth curve through `points` [(x, y), ...]."""
    if len(points) < 2:
        return ""
    d = "M{:.1f},{:.1f}".format(*points[0])
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += " C{:.1f},{:.1f} {:.1f},{:.1f} {:.1f},{:.1f}".format(
            c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if close_to is not None:
        d += " L{:.1f},{:.1f} L{:.1f},{:.1f} Z".format(
            points[-1][0], close_to, points[0][0], close_to)
    return d


def ridge(w, h, heights, bleed=80):
    """A dune silhouette. `heights` are y values sampled evenly across width."""
    n = len(heights)
    pts = [(-bleed, heights[0])]
    for i, y in enumerate(heights):
        pts.append((w * i / (n - 1), y))
    pts.append((w + bleed, heights[-1]))
    return smooth(pts, close_to=h + 4)


def jitter_ridge(w, h, base, amp, seed, n=7):
    r = rnd(seed)
    return ridge(w, h, [base + r.uniform(-amp, amp) for _ in range(n)])


# ---------------------------------------------------------------- elements
def defs_block(uid, sky, sea_top=None, sea_bottom=None, extra="", w=1600, h=900):
    z, m, hz = SKIES[sky]
    return (
        "<defs>"
        '<linearGradient id="sky{u}" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="{z}"/>'
        '<stop offset="52%" stop-color="{m}"/>'
        '<stop offset="100%" stop-color="{hz}"/></linearGradient>'
        '<linearGradient id="sea{u}" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="{s1}"/>'
        '<stop offset="100%" stop-color="{s2}"/></linearGradient>'
        '<radialGradient id="glow{u}" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="{warm}" stop-opacity=".85"/>'
        '<stop offset="45%" stop-color="{warm}" stop-opacity=".22"/>'
        '<stop offset="100%" stop-color="{warm}" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="glit{u}" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="{warm}" stop-opacity=".55"/>'
        '<stop offset="100%" stop-color="{warm}" stop-opacity="0"/></linearGradient>'
        '<filter id="soft{u}" filterUnits="userSpaceOnUse" x="-120" y="-120" '
        'width="{fw}" height="{fh}"><feGaussianBlur stdDeviation="14"/></filter>'
        '<filter id="soft2{u}" filterUnits="userSpaceOnUse" x="-120" y="-120" '
        'width="{fw}" height="{fh}"><feGaussianBlur stdDeviation="5"/></filter>'
        "{x}</defs>"
    ).format(u=uid, z=z, m=m, hz=hz, warm=P["warm_light"], fw=w + 240, fh=h + 240,
             s1=sea_top or P["sea_500"], s2=sea_bottom or P["sea_800"], x=extra)


def clouds(uid, w, top, bottom, count, seed, color="#ffffff", op=(.16, .40)):
    """Soft, blurred cloud bands."""
    r = rnd(seed)
    out = ['<g filter="url(#soft{})">'.format(uid)]
    for _ in range(count):
        cx, cy = r.uniform(-100, w + 100), r.uniform(top, bottom)
        rx = r.uniform(w * .10, w * .28)
        ry = rx * r.uniform(.055, .12)
        out.append('<ellipse cx="{:.0f}" cy="{:.0f}" rx="{:.0f}" ry="{:.0f}" fill="{}" '
                   'opacity="{:.2f}"/>'.format(cx, cy, rx, ry, color, r.uniform(*op)))
        out.append('<ellipse cx="{:.0f}" cy="{:.0f}" rx="{:.0f}" ry="{:.0f}" fill="{}" '
                   'opacity="{:.2f}"/>'.format(cx + rx * .3, cy - ry * 1.4, rx * .55,
                                               ry * 1.2, color, r.uniform(*op) * .8))
    out.append("</g>")
    return "".join(out)


def sun(uid, cx, cy, r_disc, glow=6.0, disc="#fbe6bd"):
    return (
        '<circle cx="{:.0f}" cy="{:.0f}" r="{:.0f}" fill="url(#glow{})"/>'
        '<circle cx="{:.0f}" cy="{:.0f}" r="{:.0f}" fill="{}" opacity=".95"/>'
    ).format(cx, cy, r_disc * glow, uid, cx, cy, r_disc, disc)


def waves(y0, y1, w, seed, color=None, rows=14, op0=.30):
    """Broken wave strokes that get shorter and sparser toward the horizon."""
    color = color or P["sea_200"]
    r = rnd(seed)
    out = []
    for i in range(rows):
        t = i / max(1, rows - 1)              # 0 at horizon -> 1 near viewer
        y = y0 + (y1 - y0) * (t ** 1.35)
        n = int(3 + t * 9)
        for _ in range(n):
            seg = r.uniform(w * .02, w * .09) * (.35 + t)
            x = r.uniform(-w * .05, w)
            sw = .8 + t * 1.9
            out.append(
                '<path d="M{:.0f},{:.1f} q{:.0f},{:.1f} {:.0f},0" stroke="{}" '
                'stroke-width="{:.1f}" fill="none" stroke-linecap="round" '
                'opacity="{:.2f}"/>'.format(
                    x, y, seg / 2, -2.2 - t * 3, seg, color, sw,
                    (op0 + t * .22) * r.uniform(.55, 1.0)))
    return "".join(out)


def glitter(uid, cx, y0, y1, w_top, w_bot):
    """The sun's reflection running toward the viewer."""
    return (
        '<path d="M{:.0f},{:.0f} L{:.0f},{:.0f} L{:.0f},{:.0f} L{:.0f},{:.0f} Z" '
        'fill="url(#glit{})" filter="url(#soft2{})"/>'
    ).format(cx - w_top / 2, y0, cx + w_top / 2, y0,
             cx + w_bot / 2, y1, cx - w_bot / 2, y1, uid, uid)


def grass_tuft(x, y, scale, seed, color, opacity=1.0):
    r = rnd(seed)
    blades = []
    for _ in range(r.randint(5, 9)):
        lean = r.uniform(-1.1, 1.1)
        hgt = scale * r.uniform(.55, 1.3)
        bx = x + r.uniform(-scale * .3, scale * .3)
        blades.append(
            '<path d="M{:.1f},{:.1f} Q{:.1f},{:.1f} {:.1f},{:.1f}" stroke="{}" '
            'stroke-width="{:.2f}" fill="none" stroke-linecap="round" opacity="{:.2f}"/>'.format(
                bx, y, bx + lean * hgt * .3, y - hgt * .62, bx + lean * hgt, y - hgt,
                color, max(.9, scale * .055), opacity))
    return "".join(blades)


def grass_band(w, y_lo, y_hi, count, seed, color, scale=(14, 38), opacity=1.0):
    r = rnd(seed)
    return "".join(
        grass_tuft(r.uniform(-20, w + 20), r.uniform(y_lo, y_hi),
                   r.uniform(*scale), seed * 7 + i, color, opacity)
        for i in range(count))


def thatch_house(x, base, w, h, seed=1, wall=None, roof=None, windows=3,
                 lit=False, door=False, shade=.0):
    """A Fischland thatched-roof house: steep reed roof, low light walls."""
    wall = wall or P["wall"]
    roof = roof or P["reed_500"]
    roof_h = h * .56
    wall_h = h - roof_h
    wy = base - wall_h
    ry = wy - roof_h
    r = rnd(seed)
    g = ["<g>"]

    g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="{}"/>'.format(
        x, wy, w, wall_h + 1, wall))
    g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="{}" '
             'opacity=".55"/>'.format(x + w * .72, wy, w * .28, wall_h + 1, P["wall_shade"]))

    over = w * .06
    apex_y = ry
    g.append(
        '<path d="M{:.1f},{:.1f} C{:.1f},{:.1f} {:.1f},{:.1f} {:.1f},{:.1f} '
        'C{:.1f},{:.1f} {:.1f},{:.1f} {:.1f},{:.1f} Z" fill="{}"/>'.format(
            x - over, wy + 1,
            x + w * .10, wy - roof_h * .30, x + w * .34, apex_y + roof_h * .06,
            x + w / 2, apex_y,
            x + w * .66, apex_y + roof_h * .06, x + w * .90, wy - roof_h * .30,
            x + w + over, wy + 1, roof))
    # reed texture: fine diagonal courses
    for i in range(1, 11):
        t = i / 11
        yy = apex_y + roof_h * t
        half = (w / 2 + over) * (t ** .68)
        g.append('<path d="M{:.1f},{:.1f} L{:.1f},{:.1f}" stroke="{}" stroke-width=".9" '
                 'opacity="{:.2f}"/>'.format(x + w / 2 - half, yy, x + w / 2 + half, yy,
                                             P["reed_700"], .13 + r.uniform(0, .07)))
    # shaded right flank of the roof
    g.append('<path d="M{:.1f},{:.1f} C{:.1f},{:.1f} {:.1f},{:.1f} {:.1f},{:.1f} L{:.1f},{:.1f} Z" '
             'fill="{}" opacity=".28"/>'.format(
                 x + w / 2, apex_y,
                 x + w * .66, apex_y + roof_h * .06, x + w * .90, wy - roof_h * .30,
                 x + w + over, wy + 1, x + w / 2, wy + 1, P["reed_800"]))
    # ridge cap
    g.append('<path d="M{:.1f},{:.1f} Q{:.1f},{:.1f} {:.1f},{:.1f}" stroke="{}" '
             'stroke-width="{:.1f}" fill="none" stroke-linecap="round"/>'.format(
                 x + w * .33, apex_y + roof_h * .10, x + w / 2, apex_y - 1.5,
                 x + w * .67, apex_y + roof_h * .10, P["reed_600"], max(2.2, w * .018)))
    # dormer
    dw = w * .20
    dx = x + w / 2 - dw / 2
    dy = apex_y + roof_h * .42
    g.append('<path d="M{:.1f},{:.1f} q{:.1f},{:.1f} {:.1f},0 v{:.1f} h{:.1f} Z" fill="{}"/>'.format(
        dx, dy, dw / 2, -dw * .58, dw, dw * .60, -dw, P["reed_600"]))
    g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" rx="1.5" fill="{}"/>'.format(
        dx + dw * .19, dy + dw * .05, dw * .62, dw * .42,
        P["glass_lit"] if lit else P["glass"]))
    # ground-floor windows
    slots = windows + (1 if door else 0)
    gw = w / (slots * 2 + 1)
    for i in range(slots):
        sx = x + gw * (i * 2 + 1)
        if door and i == slots // 2:
            dh = wall_h * .78
            g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" rx="{:.1f}" '
                     'fill="{}"/>'.format(sx, base - dh, gw, dh, gw * .35, P["reed_700"]))
            continue
        wh = wall_h * .50
        wy2 = wy + wall_h * .25
        g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" rx="1.5" '
                 'fill="{}"/>'.format(sx, wy2, gw, wh, P["glass_lit"] if lit else P["glass"]))
        g.append('<path d="M{:.1f},{:.1f} v{:.1f} M{:.1f},{:.1f} h{:.1f}" stroke="{}" '
                 'stroke-width="1" opacity=".55"/>'.format(
                     sx + gw / 2, wy2, wh, sx, wy2 + wh / 2, gw, P["wall"]))
        g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" rx="1.5" fill="none" '
                 'stroke="{}" stroke-width="1.6"/>'.format(sx, wy2, gw, wh, P["wall"]))
    if shade:
        g.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="{}" '
                 'opacity="{:.2f}"/>'.format(x - over, apex_y, w + over * 2, h, P["sea_900"], shade))
    g.append("</g>")
    return "".join(g)


def strandkorb(x, base, s, hood, seat, seed=3):
    """A Baltic hooded beach chair, seen from the front."""
    r = rnd(seed)
    tilt = r.uniform(-4, 4)
    return (
        '<g transform="translate({:.1f},{:.1f}) rotate({:.1f}) scale({:.3f})">'
        '<ellipse cx="0" cy="3" rx="30" ry="6" fill="{shadow}" opacity=".28"/>'
        # hood shell
        '<path d="M-23,2 V-22 a23,28 0 0 1 46,0 V2 Z" fill="{hood}"/>'
        # canvas awning stripes
        '<path d="M-14,-45 a23,28 0 0 1 28,0" fill="none" stroke="{stripe}" stroke-width="2" '
        'opacity=".4"/>'
        '<path d="M-20,-33 a23,28 0 0 1 40,0" fill="none" stroke="{stripe}" stroke-width="2" '
        'opacity=".28"/>'
        # shaded interior of the hood
        '<path d="M-16,2 V-20 a16,20 0 0 1 32,0 V2 Z" fill="{shade}" opacity=".45"/>'
        # seat cushion + backrest
        '<rect x="-16" y="-16" width="32" height="10" rx="3" fill="{seat}"/>'
        '<rect x="-17" y="-6" width="34" height="8" rx="3" fill="{seat}"/>'
        # footrest drawer and frame
        '<rect x="-25" y="1" width="50" height="6" rx="2.5" fill="{frame}"/>'
        '<path d="M-18,7 v6 M18,7 v6" stroke="{frame}" stroke-width="3" stroke-linecap="round"/>'
        "</g>"
    ).format(x, base, tilt, s, hood=hood, seat=seat, stripe=P["sand_50"],
             shade=P["sea_900"], frame=P["reed_700"], shadow=P["sand_500"])


def svg(w, h, body, title):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        'width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" '
        'role="img" aria-label="{t}"><title>{t}</title>{b}</svg>\n'
    ).format(w=w, h=h, b=body, t=title)


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print("  {:<28} {:>7} bytes".format(name, len(content)))


# --------------------------------------------------------------- the scenes
def scene_hero():
    """Golden hour: looking over the dunes to the sea, the village on the left."""
    w, h = 1600, 900
    u = "H"
    hz = 372                                   # horizon
    b = [defs_block(u, "gold", P["sea_500"], P["sea_800"], w=w, h=h)]
    b.append('<rect width="{}" height="{}" fill="url(#sky{})"/>'.format(w, h, u))
    b.append(sun(u, 1210, hz - 96, 42, glow=5.4))
    b.append(clouds(u, w, 70, hz - 150, 7, 11, "#ffe9cd", (.14, .34)))
    b.append(clouds(u, w, hz - 130, hz - 30, 4, 17, "#ffd7ab", (.10, .24)))

    # --- sea
    b.append('<rect y="{}" width="{}" height="{}" fill="url(#sea{})"/>'.format(hz, w, 190, u))
    b.append(glitter(u, 1210, hz, hz + 190, 60, 300))
    b.append(waves(hz + 6, hz + 182, w, 23, rows=13, op0=.16))

    # --- wet sand and surf line
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [hz + 178, hz + 190, hz + 176, hz + 192, hz + 180, hz + 194, hz + 182]),
        P["sand_400"]))
    b.append('<path d="{}" fill="#ffffff" opacity=".5" filter="url(#soft2{})"/>'.format(
        ridge(w, h, [hz + 176, hz + 188, hz + 174, hz + 190, hz + 178, hz + 192, hz + 180]), u))
    b.append('<rect y="{}" width="{}" height="{}" fill="{}" opacity=".35"/>'.format(
        hz + 196, w, 40, P["warm_light"]))

    # --- beach flat
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [640, 628, 636, 626, 634, 630, 638]), P["sand_300"]))

    # --- village dune: crest rises to the left, houses sit on it
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [612, 600, 618, 645, 668, 672, 664]), P["sand_200"]))
    b.append(thatch_house(105, 690, 268, 186, seed=2, lit=True, windows=3, door=True))
    b.append(thatch_house(392, 700, 196, 132, seed=4, roof=P["reed_600"], windows=2, lit=True))
    b.append(thatch_house(1255, 702, 226, 150, seed=6, lit=True, windows=2, door=True))
    # hedge line tucking the houses in
    b.append('<path d="{}" fill="{}" opacity=".9"/>'.format(
        ridge(w, h, [706, 700, 712, 726, 742, 748, 740]), P["grass_dark"]))
    b.append(grass_band(w, 700, 746, 34, 29, P["grass_deep"], (14, 30), .8))

    # --- foreground dune, in shadow
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [790, 772, 800, 782, 806, 788, 796]), P["sand_400"]))
    b.append(strandkorb(690, 826, 1.7, P["sea_700"], P["sand_100"], 31))
    b.append(strandkorb(838, 838, 2.0, P["reed_600"], P["sand_100"], 33))
    b.append(strandkorb(985, 824, 1.6, P["sea_600"], P["sand_100"], 35))
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [872, 858, 884, 866, 890, 870, 880]), P["sand_500"]))
    b.append(grass_band(w, 840, 900, 52, 41, P["grass_deep"], (18, 46)))
    b.append('<rect y="{}" width="{}" height="{}" fill="{}" opacity=".22"/>'.format(
        830, w, 70, P["sea_900"]))
    return svg(w, h, "".join(b),
               "Reetgedeckte Häuser in den Dünen von Ahrenshoop im Abendlicht")


def scene_header(uid, sky, title, seed, houses=True, korb=True, sun_at=None):
    """Slimmer banner for the top of an inner page."""
    w, h = 1600, 620
    hz = 268
    b = [defs_block(uid, sky, P["sea_500"], P["sea_800"], w=w, h=h)]
    b.append('<rect width="{}" height="{}" fill="url(#sky{})"/>'.format(w, h, uid))
    if sun_at:
        b.append(sun(uid, sun_at[0], sun_at[1], sun_at[2], glow=5.0))
    b.append(clouds(uid, w, 50, hz - 90, 6, seed, "#ffffff", (.10, .26)))
    b.append('<rect y="{}" width="{}" height="{}" fill="url(#sea{})"/>'.format(hz, w, 150, uid))
    if sun_at:
        b.append(glitter(uid, sun_at[0], hz, hz + 150, 50, 220))
    b.append(waves(hz + 5, hz + 144, w, seed + 3, rows=10, op0=.15))
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [412, 420, 408, 424, 414, 426, 416]), P["sand_400"]))
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [452, 442, 458, 448, 462, 450, 456]), P["sand_300"]))
    if houses:
        b.append(thatch_house(1160, 498, 210, 142, seed=seed + 2, lit=True, windows=2, door=True))
        b.append(thatch_house(178, 504, 168, 112, seed=seed + 3, windows=2, lit=True))
        b.append('<path d="{}" fill="{}" opacity=".9"/>'.format(
            ridge(w, h, [512, 504, 518, 528, 538, 542, 534]), P["grass_dark"]))
    if korb:
        b.append(strandkorb(760, 540, 1.4, P["sea_700"], P["sand_100"], seed + 9))
        b.append(strandkorb(880, 548, 1.6, P["reed_600"], P["sand_100"], seed + 11))
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [566, 556, 574, 560, 578, 562, 570]), P["sand_400"]))
    b.append(grass_band(w, 560, 620, 34, seed + 5, P["grass_deep"], (16, 38)))
    b.append('<rect y="{}" width="{}" height="{}" fill="{}" opacity=".18"/>'.format(
        556, w, 64, P["sea_900"]))
    return svg(w, h, "".join(b), title)


def scene_house(uid, roof, wall, sky, title, seed=41, lit=True, sun_at=None):
    """Card image of a single house behind its garden."""
    w, h = 900, 675
    b = [defs_block(uid, sky, P["sea_500"], P["sea_800"], w=w, h=h)]
    b.append('<rect width="{}" height="{}" fill="url(#sky{})"/>'.format(w, h, uid))
    if sun_at:
        b.append(sun(uid, sun_at[0], sun_at[1], sun_at[2], glow=5.0))
    b.append(clouds(uid, w, 40, 210, 5, seed, "#ffffff", (.12, .30)))
    # tree line behind the house
    r = rnd(seed + 1)
    for _ in range(11):
        tx = r.uniform(-40, w + 40)
        rad = r.uniform(48, 104)
        b.append('<circle cx="{:.0f}" cy="{:.0f}" r="{:.0f}" fill="{}" opacity=".85"/>'.format(
            tx, 420 - rad * .55, rad, P["grass_dark"]))
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [452, 444, 458, 448, 460], bleed=40), P["sand_300"]))
    b.append(thatch_house(196, 556, 508, 356, seed=seed, roof=roof, wall=wall,
                          lit=lit, windows=3, door=True))
    # hedge, garden path, foreground grass
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [566, 558, 572, 560, 570], bleed=40), P["grass"]))
    b.append('<path d="M{:.0f},{:.0f} L{:.0f},{} L{:.0f},{} L{:.0f},{:.0f} Z" fill="{}"/>'.format(
        w * .42, 562, w * .30, h, w * .70, h, w * .58, 562, P["sand_200"]))
    b.append('<path d="{}" fill="{}" opacity=".95"/>'.format(
        ridge(w, h, [614, 606, 620, 608, 618], bleed=40), P["grass_dark"]))
    b.append('<path d="M{:.0f},{:.0f} L{:.0f},{} L{:.0f},{} L{:.0f},{:.0f} Z" fill="{}"/>'.format(
        w * .38, 612, w * .28, h, w * .72, h, w * .62, 612, P["sand_200"]))
    rg = rnd(seed + 3)
    for i in range(26):
        x = rg.uniform(-10, w + 10)
        if w * .28 < x < w * .72:
            continue
        b.append(grass_tuft(x, rg.uniform(614, h), rg.uniform(16, 40), seed + i, P["grass_deep"]))
    return svg(w, h, "".join(b), title)


def scene_room(uid, accent, title, seed=51, night=False, mirror=False,
               french_door=False, skylight=False, kitchen=False):
    """Interior: a bed under the sloped reed roof, window onto the dunes.

    The four categories differ in layout, not just in colour: the room is
    mirrored, the window becomes a door onto a balcony, a skylight opens in
    the reed roof, or a small kitchen table replaces the armchair.
    """
    w, h = 900, 675
    wall = "#f3ede2" if not night else "#20363f"
    ceil = "#e7dccb" if not night else "#1a2e37"
    floor = "#c4a67c" if not night else "#3a4a52"
    linen = P["sand_50"] if not night else "#dfe7e6"
    trim = P["wall_shade"] if not night else "#16303a"
    view_top = "#8fbdcf" if not night else "#12303f"
    view_bot = P["sand_300"] if not night else "#2f5061"
    outside = P["grass_deep"] if not night else "#16323c"

    b = ['<defs><linearGradient id="win{u}" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0%" stop-color="{a}"/><stop offset="62%" stop-color="{c}"/>'
         '<stop offset="100%" stop-color="{d}"/></linearGradient>'
         '<radialGradient id="lamp{u}" cx="50%" cy="50%" r="50%">'
         '<stop offset="0%" stop-color="{warm}" stop-opacity=".55"/>'
         '<stop offset="100%" stop-color="{warm}" stop-opacity="0"/></radialGradient>'
         "</defs>".format(u=uid, a=view_top, c="#cfe0e2" if not night else "#254a5c",
                          d=view_bot, warm=P["warm_light"])]
    b.append('<rect width="{}" height="{}" fill="{}"/>'.format(w, h, wall))

    # everything after the flat background can be mirrored as one block
    if mirror:
        b.append('<g transform="translate({},0) scale(-1,1)">'.format(w))

    # sloping ceiling with exposed rafters, clipped to the ceiling itself
    b.append('<path d="M0,0 H{} V96 L0,286 Z" fill="{}"/>'.format(w, ceil))
    b.append('<clipPath id="cclip{}"><path d="M0,0 H{} V96 L0,286 Z"/></clipPath>'.format(uid, w))
    b.append('<g clip-path="url(#cclip{})">'.format(uid))
    for i in range(7):
        y0 = 300 - i * 44
        b.append('<path d="M-20,{:.0f} L{},{:.0f}" stroke="{}" stroke-width="9" '
                 'opacity=".45" stroke-linecap="round"/>'.format(y0, w + 20, y0 - 196, P["reed_600"]))
    if skylight:
        b.append('<path d="M188,44 L344,14 L392,120 L232,156 Z" fill="{}"/>'.format(trim))
        b.append('<path d="M200,52 L336,26 L378,116 L240,146 Z" fill="{}"/>'.format(
            "#123045" if night else "#a9cbdb"))
        if night:
            for sx, sy, sr in ((238, 62, 2.6), (280, 52, 2.0), (318, 74, 2.9),
                               (262, 96, 2.2), (330, 106, 2.4), (296, 122, 1.8)):
                b.append('<circle cx="{}" cy="{}" r="{}" fill="#f4e6c4" opacity=".9"/>'.format(
                    sx, sy, sr))
        b.append('<path d="M200,52 L336,26 L378,116 L240,146 Z" fill="none" stroke="{}" '
                 'stroke-width="4"/>'.format(trim))
    b.append("</g>")
    b.append('<path d="M0,286 L{},96" stroke="{}" stroke-width="6" opacity=".75"/>'.format(w, trim))

    # floor + boards + rug
    b.append('<rect y="500" width="{}" height="{}" fill="{}"/>'.format(w, h - 500, floor))
    for i in range(12):
        b.append('<path d="M0,{} h{}" stroke="#000" stroke-width=".9" opacity=".06"/>'.format(
            504 + i * 15, w))
    b.append('<ellipse cx="470" cy="628" rx="270" ry="46" fill="{}" opacity=".45"/>'.format(
        P["sea_400"]))

    # --- the opening onto the outside: window, or a door down to the floor
    if french_door:
        wx, wy, ww, wh = 528, 150, 320, 350
    else:
        wx, wy, ww, wh = 540, 176, 300, 250
    b.append('<rect x="{}" y="{}" width="{}" height="{}" rx="5" fill="url(#win{})"/>'.format(
        wx, wy, ww, wh, uid))
    b.append('<g transform="translate({},{}) scale({:.4f},{:.4f})">'.format(
        wx, wy, ww / 900, wh / 750))
    b.append('<path d="{}" fill="{}" opacity=".9"/>'.format(
        ridge(900, 750, [500, 470, 515, 486, 505], bleed=30),
        P["sand_300"] if not night else "#2a4450"))
    b.append(grass_tuft(120, 620, 60, seed, outside))
    b.append(grass_tuft(690, 640, 52, seed + 1, outside))
    b.append("</g>")
    if french_door:
        # balcony railing seen through the glass
        for rx in range(wx + 18, wx + ww - 10, 34):
            b.append('<rect x="{}" y="{}" width="5" height="86" fill="{}" opacity=".8"/>'.format(
                rx, wy + wh - 150, linen))
        b.append('<rect x="{}" y="{}" width="{}" height="7" rx="3" fill="{}" opacity=".9"/>'.format(
            wx + 12, wy + wh - 156, ww - 24, linen))
    b.append('<rect x="{}" y="{}" width="{}" height="{}" rx="5" fill="none" stroke="{}" '
             'stroke-width="10"/>'.format(wx, wy, ww, wh, trim))
    b.append('<path d="M{},{} v{} M{},{} h{}" stroke="{}" stroke-width="8"/>'.format(
        wx + ww / 2, wy, wh, wx, wy + wh / 2, ww, trim))
    # linen curtains either side
    for cx, flip in ((wx - 46, 1), (wx + ww + 6, -1)):
        b.append('<path d="M{},{} c{},{} {},{} {},{} h{} c{},{} {},{} {},{} Z" fill="{}" '
                 'opacity=".92"/>'.format(
                     cx, wy - 18,
                     10 * flip, wh * .34, -8 * flip, wh * .66, 4 * flip, wh + 46,
                     40 * flip,
                     -10 * flip, -wh * .3, 8 * flip, -wh * .68, -4 * flip, -(wh + 46),
                     linen))
        b.append('<path d="M{},{} c{},{} {},{} {},{}" stroke="{}" stroke-width="2" fill="none" '
                 'opacity=".25"/>'.format(
                     cx + 20 * flip, wy - 10,
                     8 * flip, wh * .34, -6 * flip, wh * .66, 3 * flip, wh + 40, trim))

    # --- the bed
    bx, by, bw = 84, 500, 400
    b.append('<rect x="{}" y="{}" width="{}" height="188" rx="9" fill="{}" opacity=".95"/>'.format(
        bx - 14, by - 320, bw + 28, P["reed_600"]))
    b.append('<rect x="{}" y="{}" width="{}" height="126" rx="8" fill="{}"/>'.format(
        bx, by - 126, bw, linen))
    b.append('<rect x="{}" y="{}" width="{}" height="50" rx="8" fill="{}"/>'.format(
        bx, by - 68, bw, accent))
    for px in (bx + 26, bx + 200):
        b.append('<rect x="{}" y="{}" width="152" height="60" rx="14" fill="{}"/>'.format(
            px, by - 176, linen))
    b.append('<rect x="{}" y="{}" width="{}" height="14" rx="5" fill="{}"/>'.format(
        bx - 6, by - 12, bw + 12, P["reed_700"]))

    # bedside table + lamp
    tx = bx + bw + 26
    b.append('<rect x="{}" y="{}" width="86" height="96" rx="6" fill="{}"/>'.format(
        tx, by - 96, P["reed_700"]))
    b.append('<rect x="{}" y="{}" width="8" height="34" fill="{}"/>'.format(
        tx + 39, by - 130, P["reed_800"]))
    b.append('<path d="M{},{} l-30,-46 h60 Z" fill="{}"/>'.format(
        tx + 43, by - 128, P["glass_lit"] if night else "#efe7d8"))
    if night:
        b.append('<circle cx="{}" cy="{}" r="150" fill="url(#lamp{})"/>'.format(
            tx + 43, by - 150, uid))

    # --- the corner by the window
    if kitchen:
        # small round dining table with two chairs
        b.append('<ellipse cx="724" cy="486" rx="104" ry="26" fill="{}"/>'.format(linen))
        b.append('<rect x="716" y="486" width="16" height="80" fill="{}"/>'.format(P["reed_800"]))
        b.append('<ellipse cx="724" cy="566" rx="44" ry="11" fill="{}"/>'.format(P["reed_800"]))
        for dx in (-76, 76):
            b.append('<g transform="translate({},520)">'
                     '<rect x="-26" y="-74" width="52" height="74" rx="9" fill="{c}"/>'
                     '<rect x="-21" y="-64" width="42" height="42" rx="7" fill="{l}" opacity=".5"/>'
                     '<rect x="-20" y="0" width="8" height="20" rx="3" fill="{f}"/>'
                     '<rect x="12" y="0" width="8" height="20" rx="3" fill="{f}"/>'
                     "</g>".format(724 + dx, c=P["reed_700"], l=linen, f=P["reed_800"]))
        b.append('<ellipse cx="700" cy="482" rx="20" ry="6" fill="#ffffff"/>')
        b.append('<path d="M756,482 q-7,-22 3,-34" stroke="{}" stroke-width="3" fill="none" '
                 'stroke-linecap="round"/>'.format(P["grass_dark"]))
        b.append('<rect x="746" y="466" width="20" height="22" rx="4" fill="{}" '
                 'opacity=".85"/>'.format(P["sea_400"]))
    else:
        ch = P["sea_600"] if not night else P["sea_700"]
        b.append('<g transform="translate(726,500)">'
                 '<path d="M-56,0 v-72 a20,20 0 0 1 20,-20 h72 a20,20 0 0 1 20,20 V0 Z" fill="{c}"/>'
                 '<path d="M-36,-92 v-38 a22,22 0 0 1 22,-22 h44 a22,22 0 0 1 22,22 v38 Z" fill="{c}"/>'
                 '<path d="M-30,-96 v-34 a16,16 0 0 1 16,-16 h36 a16,16 0 0 1 16,16 v34 Z" '
                 'fill="{l}" opacity=".45"/>'
                 '<rect x="-40" y="-96" width="80" height="18" rx="9" fill="{l}" opacity=".85"/>'
                 '<rect x="-48" y="0" width="14" height="26" rx="5" fill="{f}"/>'
                 '<rect x="34" y="0" width="14" height="26" rx="5" fill="{f}"/>'
                 "</g>".format(c=ch, l=linen, f=P["reed_700"]))
        b.append('<path d="M782,410 q22,26 6,58 h-20 q14,-30 -4,-58 Z" fill="{}" '
                 'opacity=".9"/>'.format(accent))

    if mirror:
        b.append("</g>")
    return svg(w, h, "".join(b), title)


def scene_dining():
    """The sea terrace: laid table, railing, water beyond."""
    w, h = 900, 675
    u = "D"
    hz = 250
    b = [defs_block(u, "gold", P["sea_500"], P["sea_700"], w=w, h=h)]
    b.append('<rect width="{}" height="{}" fill="url(#sky{})"/>'.format(w, h, u))
    b.append(sun(u, 654, hz - 62, 30, glow=5.6))
    b.append(clouds(u, w, 40, hz - 100, 5, 61, "#ffe9cd", (.12, .30)))
    b.append('<rect y="{}" width="{}" height="120" fill="url(#sea{})"/>'.format(hz, w, u))
    b.append(glitter(u, 654, hz, hz + 120, 34, 150))
    b.append(waves(hz + 6, hz + 114, w, 63, rows=8, op0=.15))
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [372, 364, 378, 368, 376], bleed=40), P["sand_300"]))
    b.append(grass_band(w, 372, 396, 16, 65, P["grass_deep"], (12, 26), .85))

    # terrace decking
    b.append('<rect y="404" width="{}" height="{}" fill="{}"/>'.format(w, h - 404, P["reed_600"]))
    for i in range(16):
        b.append('<path d="M0,{} h{}" stroke="{}" stroke-width="1.6" opacity=".3"/>'.format(
            410 + i * 18, w, P["reed_800"]))
    # railing
    b.append('<rect y="366" width="{}" height="8" rx="4" fill="{}"/>'.format(w, P["sand_50"]))
    for x in range(24, w, 76):
        b.append('<rect x="{}" y="366" width="7" height="42" rx="3" fill="{}" opacity=".92"/>'.format(
            x, P["sand_50"]))

    # round table
    cx, ty = 430, 486
    b.append('<ellipse cx="{}" cy="{}" rx="240" ry="120" fill="{}" opacity=".16"/>'.format(
        cx, ty + 168, P["reed_800"]))
    b.append('<rect x="{}" y="{}" width="22" height="140" fill="{}"/>'.format(cx - 11, ty, P["reed_800"]))
    b.append('<ellipse cx="{}" cy="{}" rx="76" ry="16" fill="{}"/>'.format(cx, ty + 140, P["reed_800"]))
    b.append('<ellipse cx="{}" cy="{}" rx="238" ry="58" fill="{}"/>'.format(cx, ty, P["sand_50"]))
    b.append('<ellipse cx="{}" cy="{}" rx="238" ry="58" fill="none" stroke="{}" '
             'stroke-width="2" opacity=".5"/>'.format(cx, ty, P["sand_300"]))
    # place settings
    for dx in (-132, 132):
        b.append('<ellipse cx="{}" cy="{}" rx="54" ry="17" fill="#ffffff"/>'.format(cx + dx, ty - 2))
        b.append('<ellipse cx="{}" cy="{}" rx="30" ry="9" fill="{}" opacity=".45"/>'.format(
            cx + dx, ty - 3, P["sand_200"]))
        b.append('<path d="M{},{} l-12,-34 h24 Z" fill="#e6f2f4" opacity=".9"/>'.format(
            cx + dx + 74, ty - 8))
        b.append('<rect x="{}" y="{}" width="4" height="12" fill="#e6f2f4" opacity=".9"/>'.format(
            cx + dx + 72, ty - 8))
    # candle + small vase
    b.append('<rect x="{}" y="{}" width="11" height="40" rx="4" fill="{}"/>'.format(
        cx - 6, ty - 46, P["sand_50"]))
    b.append('<ellipse cx="{}" cy="{}" rx="5" ry="10" fill="{}"/>'.format(cx, ty - 54, P["glass_lit"]))
    b.append('<circle cx="{}" cy="{}" r="46" fill="url(#glow{})"/>'.format(cx, ty - 54, u))
    b.append('<path d="M{},{} q-8,-26 4,-40 M{},{} q10,-22 22,-30" stroke="{}" stroke-width="3" '
             'fill="none" stroke-linecap="round"/>'.format(
                 cx + 62, ty - 10, cx + 62, ty - 10, P["grass_dark"]))
    b.append('<rect x="{}" y="{}" width="22" height="26" rx="4" fill="{}" opacity=".85"/>'.format(
        cx + 52, ty - 16, P["sea_400"]))
    # chairs
    for dx in (-206, 206):
        b.append('<g transform="translate({},{})">'
                 '<rect x="-38" y="-108" width="76" height="108" rx="12" fill="{}"/>'
                 '<rect x="-32" y="-96" width="64" height="66" rx="9" fill="{}" opacity=".5"/>'
                 '<rect x="-30" y="0" width="10" height="24" rx="4" fill="{}"/>'
                 '<rect x="20" y="0" width="10" height="24" rx="4" fill="{}"/>'
                 "</g>".format(cx + dx, ty + 96, P["reed_800"], P["sand_200"],
                               P["reed_800"], P["reed_800"]))
    return svg(w, h, "".join(b), "Gedeckter Tisch auf der Seeterrasse im Abendlicht")


def scene_wellness():
    """Indoor pool looking into the green."""
    w, h = 900, 675
    u = "W"
    b = ['<defs><linearGradient id="pool{u}" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0%" stop-color="{a}"/><stop offset="100%" stop-color="{b}"/>'
         "</linearGradient>"
         '<linearGradient id="garden{u}" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0%" stop-color="#cfe0e2"/><stop offset="100%" stop-color="#9fbb9a"/>'
         "</linearGradient>"
         '<radialGradient id="cand{u}" cx="50%" cy="50%" r="50%">'
         '<stop offset="0%" stop-color="{warm}" stop-opacity=".5"/>'
         '<stop offset="100%" stop-color="{warm}" stop-opacity="0"/></radialGradient>'
         '<filter id="blur{u}" filterUnits="userSpaceOnUse" x="-60" y="-60" '
         'width="1020" height="795"><feGaussianBlur stdDeviation="6"/></filter>'
         "</defs>".format(u=u, a=P["sea_300"], b=P["sea_700"], warm=P["warm_light"])]
    b.append('<rect width="{}" height="{}" fill="#efe8dc"/>'.format(w, h))
    # glass wall onto the garden
    b.append('<rect width="{}" height="346" fill="url(#garden{})"/>'.format(w, u))
    r = rnd(71)
    for _ in range(12):
        tx = r.uniform(-30, w + 30)
        rad = r.uniform(52, 118)
        b.append('<rect x="{:.0f}" y="{:.0f}" width="10" height="{:.0f}" fill="{}" '
                 'opacity=".7"/>'.format(tx - 5, 300 - rad * .5, rad * .7, P["reed_700"]))
        b.append('<circle cx="{:.0f}" cy="{:.0f}" r="{:.0f}" fill="{}" opacity=".8"/>'.format(
            tx, 300 - rad * .75, rad, P["grass_dark"]))
    b.append('<rect y="300" width="{}" height="46" fill="{}" opacity=".85"/>'.format(w, P["grass"]))
    # mullions + reflection
    for x in range(0, w + 1, 150):
        b.append('<rect x="{}" y="0" width="11" height="346" fill="#f6f1e7"/>'.format(x))
    b.append('<path d="M60,0 L200,346 L262,346 L122,0 Z" fill="#ffffff" opacity=".16"/>')
    b.append('<rect y="338" width="{}" height="14" fill="#f6f1e7"/>'.format(w))

    # pool deck + water
    b.append('<rect y="352" width="{}" height="{}" fill="#e6ddcd"/>'.format(w, h - 352))
    b.append('<rect x="66" y="424" width="{}" height="212" rx="16" fill="url(#pool{})"/>'.format(
        w - 132, u))
    b.append('<g clip-path="inset(0 round 16px)">')
    b.append('<rect x="66" y="424" width="{}" height="212" fill="none"/>'.format(w - 132))
    b.append("</g>")
    b.append('<g transform="translate(66,0)">{}</g>'.format(
        waves(432, 626, w - 132, 73, color="#ffffff", rows=9, op0=.12)))
    b.append('<rect x="66" y="424" width="{}" height="212" rx="16" fill="none" stroke="#f6f1e7" '
             'stroke-width="7"/>'.format(w - 132))
    # reflection of the garden in the water
    b.append('<rect x="66" y="424" width="{}" height="70" fill="{}" opacity=".18" '
             'filter="url(#blur{})"/>'.format(w - 132, P["grass_dark"], u))
    # loungers
    for dx in (96, 250):
        b.append('<g transform="translate({},372)">'
                 '<path d="M0,0 h132 v13 H0 Z" fill="#f6f1e7"/>'
                 '<path d="M104,0 l34,-48 l16,11 l-27,37 Z" fill="#f6f1e7"/>'
                 '<path d="M10,13 v15 M122,13 v15" stroke="{}" stroke-width="5" '
                 'stroke-linecap="round"/>'
                 '<rect x="26" y="-8" width="46" height="10" rx="4" fill="{}"/>'
                 "</g>".format(dx, P["reed_700"], P["sea_400"]))
    # candles on the ledge
    for cx in (w - 130, w - 100, w - 70):
        b.append('<rect x="{}" y="352" width="12" height="30" rx="4" fill="#f6f1e7"/>'.format(cx))
        b.append('<ellipse cx="{}" cy="348" rx="4.5" ry="8" fill="{}"/>'.format(cx + 6, P["glass_lit"]))
        b.append('<circle cx="{}" cy="348" r="34" fill="url(#cand{})"/>'.format(cx + 6, u))
    # rolled towels
    b.append('<rect x="{}" y="392" width="64" height="20" rx="10" fill="{}"/>'.format(
        w - 190, P["sea_400"]))
    b.append('<rect x="{}" y="370" width="64" height="20" rx="10" fill="{}" opacity=".85"/>'.format(
        w - 190, P["sea_300"]))
    return svg(w, h, "".join(b), "Schwimmbad mit Blick ins Grüne im Wellnessbereich")


def scene_coast():
    """The Ahrenshoop cliff coast — the Hohes Ufer."""
    w, h = 900, 675
    u = "C"
    hz = 268
    b = [defs_block(u, "clear", P["sea_400"], P["sea_700"], w=w, h=h)]
    b.append('<rect width="{}" height="{}" fill="url(#sky{})"/>'.format(w, h, u))
    b.append(clouds(u, w, 40, 190, 7, 81, "#ffffff", (.3, .65)))
    b.append('<rect y="{}" width="{}" height="{}" fill="url(#sea{})"/>'.format(hz, w, h - hz, u))
    b.append(waves(hz + 6, 520, w, 83, rows=12, op0=.16))
    # surf
    b.append('<path d="{}" fill="#ffffff" opacity=".65" filter="url(#soft2{})"/>'.format(
        ridge(w, h, [512, 524, 508, 528, 514, 530, 518]), u))
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [548, 558, 544, 562, 550, 564, 552]), P["sand_400"]))
    # cliff on the right, layered
    b.append('<path d="M{},{} L{},{} L{},{} L{},{} Z" fill="{}"/>'.format(
        w * .50, 560, w, 196, w, h, w * .50, h, P["grass_deep"]))
    b.append('<path d="M{},{} C{},{} {},{} {},{} L{},{} L{},{} Z" fill="{}"/>'.format(
        w * .56, 572, w * .70, 520, w * .82, 360, w, 250,
        w, h, w * .56, h, P["sand_400"]))
    b.append('<path d="M{},{} C{},{} {},{} {},{} L{},{} L{},{} Z" fill="{}"/>'.format(
        w * .64, 586, w * .76, 546, w * .88, 430, w, 336,
        w, h, w * .64, h, P["sand_300"]))
    # erosion streaks in the cliff face
    rr = rnd(85)
    for _ in range(14):
        x0 = rr.uniform(w * .62, w)
        y0 = rr.uniform(300, 560)
        b.append('<path d="M{:.0f},{:.0f} q6,26 -2,52" stroke="{}" stroke-width="2" '
                 'fill="none" opacity=".18"/>'.format(x0, y0, P["sand_500"]))
    # wind-bent trees on the cliff edge
    for tx, ty, s in ((w * .70, 560, .9), (w * .80, 452, 1.15), (w * .90, 348, 1.0),
                      (w * .98, 268, .85)):
        b.append('<path d="M{:.0f},{:.0f} q{:.0f},{:.0f} {:.0f},{:.0f}" stroke="{}" '
                 'stroke-width="{:.0f}" fill="none" stroke-linecap="round"/>'.format(
                     tx, ty, -14 * s, -36 * s, -44 * s, -56 * s, P["reed_800"], 7 * s))
        b.append('<ellipse cx="{:.0f}" cy="{:.0f}" rx="{:.0f}" ry="{:.0f}" fill="{}" '
                 'transform="rotate(-20 {:.0f} {:.0f})"/>'.format(
                     tx - 52 * s, ty - 66 * s, 56 * s, 27 * s, P["grass_dark"],
                     tx - 52 * s, ty - 66 * s))
    # foreground beach
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [606, 616, 600, 620, 606, 622, 610]), P["sand_200"]))
    b.append(grass_band(w * .62, 618, h, 14, 91, P["grass_deep"], (14, 30)))
    # a few stones on the sand
    rs = rnd(93)
    for _ in range(9):
        b.append('<ellipse cx="{:.0f}" cy="{:.0f}" rx="{:.0f}" ry="{:.0f}" fill="{}" '
                 'opacity=".55"/>'.format(rs.uniform(0, w * .6), rs.uniform(620, h),
                                          rs.uniform(5, 13), rs.uniform(3, 7), P["sand_500"]))
    return svg(w, h, "".join(b), "Steilküste und Ostseestrand bei Ahrenshoop")


def scene_art():
    """A nod to the artists' colony: an easel in the dunes at first light."""
    w, h = 900, 675
    u = "A"
    hz = 300
    b = [defs_block(u, "dawn", P["sea_500"], P["sea_800"], w=w, h=h)]
    b.append('<rect width="{}" height="{}" fill="url(#sky{})"/>'.format(w, h, u))
    b.append(sun(u, 640, hz - 40, 26, glow=6.2))
    b.append(clouds(u, w, 40, 230, 6, 101, "#ffd9b8", (.14, .34)))
    b.append('<rect y="{}" width="{}" height="120" fill="url(#sea{})"/>'.format(hz, w, u))
    b.append(glitter(u, 640, hz, hz + 120, 30, 140))
    b.append(waves(hz + 6, hz + 114, w, 103, rows=8, op0=.14))
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [432, 424, 440, 428, 436], bleed=40), P["sand_300"]))
    b.append('<path d="{}" fill="{}"/>'.format(
        ridge(w, h, [508, 496, 516, 502, 512], bleed=40), P["sand_400"]))
    # easel
    ex, ey = 300, 592
    b.append('<g stroke="{}" stroke-width="9" stroke-linecap="round" fill="none">'
             '<path d="M{},{} L{},{}"/><path d="M{},{} L{},{}"/><path d="M{},{} L{},{}"/>'
             "</g>".format(P["reed_800"], ex, ey, ex + 66, ey - 268,
                           ex + 132, ey, ex + 66, ey - 268,
                           ex + 66, ey - 268, ex + 78, ey - 8))
    b.append('<rect x="{}" y="{}" width="196" height="152" rx="3" fill="{}" stroke="{}" '
             'stroke-width="8"/>'.format(ex - 32, ey - 250, P["sand_50"], P["sand_400"]))
    b.append('<rect x="{}" y="{}" width="176" height="66" fill="#b9d2dc"/>'.format(ex - 22, ey - 240))
    b.append('<rect x="{}" y="{}" width="176" height="66" fill="{}"/>'.format(
        ex - 22, ey - 174, P["sea_600"]))
    b.append('<circle cx="{}" cy="{}" r="17" fill="#f6cf9b"/>'.format(ex + 108, ey - 208))
    b.append('<path d="M{},{} q22,-9 44,0 t44,0" stroke="#ffffff" stroke-width="2.4" fill="none" '
             'opacity=".7"/>'.format(ex - 14, ey - 146))
    # palette resting on the easel ledge
    b.append('<ellipse cx="{}" cy="{}" rx="34" ry="20" fill="{}"/>'.format(
        ex + 152, ey - 92, P["reed_600"]))
    for i, col in enumerate(("#c0492f", "#e0b64a", P["sea_600"], P["grass"])):
        b.append('<circle cx="{}" cy="{}" r="4.5" fill="{}"/>'.format(
            ex + 136 + i * 11, ey - 96 + (i % 2) * 8, col))
    b.append(grass_band(w, 520, h, 30, 107, P["grass_deep"], (16, 38)))
    return svg(w, h, "".join(b), "Staffelei in den Dünen — Erinnerung an die Künstlerkolonie")


def scene_pattern():
    """Seamless reed/wave motif used as a section ornament."""
    w = h = 120
    b = []
    for i in range(4):
        y = 15 + i * 30
        b.append('<path d="M0,{y} q15,-11 30,0 t30,0 t30,0 t30,0" fill="none" stroke="{c}" '
                 'stroke-width="1.6" opacity=".45"/>'.format(y=y, c=P["reed_500"]))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            'height="{h}">{b}</svg>\n'.format(w=w, h=h, b="".join(b)))


def logo_mark():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" '
        'role="img" aria-label="Signet Hotel Namenlos">'
        '<circle cx="32" cy="32" r="30" fill="none" stroke="currentColor" stroke-width="1.5" '
        'opacity=".5"/>'
        '<path d="M15 35 C20 20 26 13 32 13 C38 13 44 20 49 35 Z" fill="currentColor" opacity=".92"/>'
        '<path d="M23 35 h18 v9 h-18 Z" fill="currentColor" opacity=".3"/>'
        '<path d="M13 49 q6.5-5 13 0 t13 0 t13 0" fill="none" stroke="currentColor" '
        'stroke-width="2.4" stroke-linecap="round"/>'
        "</svg>\n"
    )


def favicon():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
        '<rect width="64" height="64" rx="13" fill="#0d2830"/>'
        '<path d="M15 35 C20 19 26 12 32 12 C38 12 44 19 49 35 Z" fill="#c9aa6b"/>'
        '<path d="M24 35 h16 v9 h-16 Z" fill="#f2e8d6" opacity=".5"/>'
        '<path d="M13 50 q6.5-5 13 0 t13 0 t13 0" fill="none" stroke="#5b9aa8" '
        'stroke-width="3.2" stroke-linecap="round"/>'
        "</svg>\n"
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("Generating scenery into", OUT)

    write("hero-duenen.svg", scene_hero())

    write("kopf-haeuser.svg", scene_header("K1", "clear", "Die Häuser des Hotels in den Dünen", 131))
    write("kopf-zimmer.svg", scene_header("K2", "dawn", "Morgenlicht über der Ostsee", 141,
                                          sun_at=(1180, 140, 34)))
    write("kopf-kulinarik.svg", scene_header("K3", "gold", "Abendstimmung über der Ostsee", 151,
                                             sun_at=(420, 150, 38)))
    write("kopf-wellness.svg", scene_header("K4", "blue", "Ruhige See in der blauen Stunde", 161,
                                            houses=False, korb=False))
    write("kopf-arrangements.svg", scene_header("K5", "clear", "Strandkörbe am Ostseestrand", 171))
    write("kopf-ahrenshoop.svg", scene_header("K6", "dusk", "Ahrenshoop zwischen Bodden und Ostsee",
                                              181, sun_at=(1320, 190, 40)))
    write("kopf-kontakt.svg", scene_header("K7", "day", "Der Weg ans Meer", 191,
                                           houses=False, korb=True))

    write("haus-namenlos.svg", scene_house("N1", P["reed_500"], P["wall"], "gold",
                                           "Haus Namenlos mit Reetdach", 41, sun_at=(720, 130, 34)))
    write("haus-fischerwiege.svg", scene_house("N2", P["reed_600"], "#cddfe6", "clear",
                                               "Das meerblaue Haus Fischerwiege", 47))
    write("haus-gaestehaus.svg", scene_house("N3", P["reed_400"], "#f2e6d4", "dawn",
                                             "Gästehaus mit Reetdach im Garten", 53,
                                             sun_at=(180, 150, 30)))
    write("haus-appartements.svg", scene_house("N4", P["reed_500"], "#e9dfd1", "clear",
                                               "Ferienwohnungen im Reetdachhaus", 59))

    write("zimmer-komfort.svg", scene_room(
        "R1", P["sea_400"], "Komfortzimmer mit Blick in die Dünen", 51))
    write("zimmer-duenenblick.svg", scene_room(
        "R2", P["reed_400"], "Zimmer mit Balkontür zur Dünenseite", 55,
        mirror=True, french_door=True))
    write("zimmer-kapitaenssuite.svg", scene_room(
        "R3", P["sea_600"], "Kapitänssuite unter dem Reetdach mit Dachfenster", 57,
        night=True, skylight=True))
    write("zimmer-appartement.svg", scene_room(
        "R4", P["grass"], "Ferienwohnung mit Esstisch und eigener Terrasse", 63,
        mirror=True, french_door=True, kitchen=True))

    write("kulinarik-terrasse.svg", scene_dining())
    write("wellness-pool.svg", scene_wellness())
    write("ahrenshoop-steilkueste.svg", scene_coast())
    write("ahrenshoop-kunst.svg", scene_art())

    write("muster-reet.svg", scene_pattern())
    write("signet.svg", logo_mark())
    write("favicon.svg", favicon())
    print("done.")


if __name__ == "__main__":
    main()
