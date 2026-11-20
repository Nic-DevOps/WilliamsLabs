#!/usr/bin/env python3
"""Regenerate the homepage's hexagon-themed network background.

Rewrites the <svg id="network-bg-svg"> block in Website/html/index.html:
  - a faint honeycomb lattice (a single <pattern>) covers the canvas,
  - device icons (the existing dev-router / dev-switch / dev-firewall /
    dev-server symbols, kept verbatim from the current file) sit in hex
    cells, spaced 2-3 cells apart,
  - each device has 3 connections to nearby devices, routed along the
    honeycomb edges, each leaving its cell from a different corner and
    avoiding edges another connection already uses,
  - routers pulse with a hexagonal halo, switches get a running dashed
    ring, firewalls are drawn as solid bold cells.

Colors come from the same CSS variables as before (--nbg-line, --nbg-node,
--nbg-accent, --bg-page), so the light/dark theme still applies. The
animations are CSS (see network-bg.css); each element only carries its own
duration (--d) and a negative delay (--o).

Canvas height: #network-bg-inner is max(160vw, 130vh) tall and the SVG is
scaled to the viewport width, so a desktop only ever shows the top ~2,600
units and a tall phone ~4,600. H covers that with a little margin; anything
drawn below it would never be seen.

Usage: python3 Website/scripts/generate_hex_network.py
"""
import heapq
import math
import random
import re
from pathlib import Path

INDEX = Path(__file__).resolve().parent.parent / "html" / "index.html"

W, H = 1600, 4800
S = 90                      # hex side length (pointy-top)
HW = math.sqrt(3) * S       # horizontal distance between cell centers
VS = 1.5 * S                # vertical distance between rows
ICON_SCALE = 3.2
SEED = 20261119

MIN_GAP = 2                 # devices are at least 2 cells apart (never adjacent)
MAX_GAP = 3                 # ...and mostly 3 apart
EXTRA = 0.12                # share of the remaining gaps that get a 2-apart device
LINKS_PER_DEVICE = 3
BAND_H = 800                # topology tiers descend in bands of this height

LINE = "var(--nbg-line, #4a6b60)"
NODE = "var(--nbg-node, #6f9a8e)"
ACCENT = "var(--nbg-accent, #1D9E75)"
PAGE = "var(--bg-page, #0b0f0e)"


def f(v):
    return f"{v:.1f}"


def center(c, r):
    return (c * HW + (HW / 2 if r % 2 else 0), r * VS)


def corners(cx, cy, side=S):
    out = []
    for k in range(6):
        a = math.radians(-90 + 60 * k)
        out.append((cx + side * math.cos(a), cy + side * math.sin(a)))
    return out


def key(p):
    return (round(p[0], 1), round(p[1], 1))


def hex_points(cx, cy, side):
    return " ".join(f"{f(x)},{f(y)}" for x, y in corners(cx, cy, side))


def cube(c, r):
    """Offset (odd rows shifted right) -> cube coordinates."""
    x = c - (r - (r & 1)) // 2
    return x, r, -x - r


def hexdist(a, b):
    ax, ay, az = cube(*a)
    bx, by, bz = cube(*b)
    return max(abs(ax - bx), abs(ay - by), abs(az - bz))


def segments_cross(p1, p2, p3, p4):
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    return d1 * d2 < 0 and d3 * d4 < 0


def main():
    rnd = random.Random(SEED)
    html = INDEX.read_text(encoding="utf-8")
    defs = re.findall(r'^<g id="dev-[a-z]+">.*?</g>$', html, re.M)
    assert len(defs) == 4, "expected the four device icon definitions"

    cols = range(-1, int(W / HW) + 2)
    rows = range(-1, int(H / VS) + 2)

    # Honeycomb graph: vertices = hex corners, edges = hex sides.
    adj = {}
    cell_vertices = {}
    for r in rows:
        for c in cols:
            cx, cy = center(c, r)
            vs = [key(p) for p in corners(cx, cy)]
            cell_vertices[(c, r)] = vs
            for i in range(6):
                a, b = vs[i], vs[(i + 1) % 6]
                adj.setdefault(a, set()).add(b)
                adj.setdefault(b, set()).add(a)

    # --- Place devices 2-3 cells apart.
    # Pass 1 packs devices MAX_GAP cells apart (which also leaves no empty
    # spot further than that from a device); pass 2 adds a few more wherever
    # MIN_GAP still allows, so the nearest-neighbour spacing is a mix of 2 and 3.
    valid = [(c, r) for r in rows for c in cols
             if 70 < center(c, r)[0] < W - 70 and 120 < center(c, r)[1] < H - 120]
    rnd.shuffle(valid)
    cells = []

    def nearest(cell):
        return min((hexdist(cell, t) for t in cells), default=99)

    for cell in valid:
        if nearest(cell) >= MAX_GAP:
            cells.append(cell)
    for cell in valid:
        if nearest(cell) >= MIN_GAP and rnd.random() < EXTRA:
            cells.append(cell)
    cells.sort(key=lambda cr: (cr[1], cr[0]))

    # --- Device types descend edge -> access -> distribution -> core.
    bands = int(math.ceil(H / BAND_H))
    tiers = [
        {"dev-switch": 5, "dev-server": 3, "dev-router": 2, "dev-firewall": 1},
        {"dev-switch": 4, "dev-router": 3, "dev-server": 2, "dev-firewall": 1},
        {"dev-router": 4, "dev-firewall": 3, "dev-switch": 2, "dev-server": 1},
    ]
    devices = []          # (cell, type, band)
    for cell in cells:
        b = min(bands - 1, int(center(*cell)[1] // BAND_H))
        weights = tiers[min(2, b * 3 // bands)]
        t = rnd.choices(list(weights), list(weights.values()))[0]
        devices.append((cell, t, b))

    # Every band gets at least one firewall: in a band that rolled none, the
    # device nearest the band's centre becomes one.
    for b in range(bands):
        members = [k for k, d in enumerate(devices) if d[2] == b]
        if members and not any(devices[k][1] == "dev-firewall" for k in members):
            mid = (W / 2, b * BAND_H + BAND_H / 2)
            k = min(members, key=lambda k: math.dist(center(*devices[k][0]), mid))
            devices[k] = (devices[k][0], "dev-firewall", b)

    # --- Choose links: LINKS_PER_DEVICE short links per device.
    # Shortest candidate pairs first; a pair is taken only while both ends
    # still need links. Pass 1 takes only pairs up to 6 cells apart whose
    # straight line doesn't cross a link already taken (keeps the routes
    # untangled); pass 2 allows crossings; pass 3 lets the few devices still
    # short of links pair up over up to 10 cells.
    n = len(devices)
    pos = [center(*d[0]) for d in devices]
    degree = [0] * n
    links = []
    cand = sorted(((hexdist(devices[i][0], devices[j][0]), rnd.random(), i, j)
                   for i in range(n) for j in range(i + 1, n)
                   if hexdist(devices[i][0], devices[j][0]) <= 10))
    taken = set()
    for allow_cross, reach in ((False, 6), (True, 6), (True, 10)):
        for dist_ij, _, i, j in cand:
            if dist_ij > reach:
                break
            if degree[i] >= LINKS_PER_DEVICE or degree[j] >= LINKS_PER_DEVICE:
                continue
            if (i, j) in taken:
                continue
            if not allow_cross and any(
                    len({i, j, a, b}) == 4 and segments_cross(pos[i], pos[j], pos[a], pos[b])
                    for a, b in links):
                continue
            links.append((i, j))
            taken.add((i, j))
            degree[i] += 1
            degree[j] += 1

    # --- Route each link along hex edges.
    device_vertex_owner = {}
    for i, (cell, _, _) in enumerate(devices):
        for v in cell_vertices[cell]:
            device_vertex_owner.setdefault(v, set()).add(i)
    used_edges = set()
    used_exits = {i: set() for i in range(n)}   # corners a device already links from

    def route(i, j):
        def ends(k):
            vs = cell_vertices[devices[k][0]]
            free = [v for v in vs if v not in used_exits[k]]
            return set(free or vs)
        src, dst = ends(i), ends(j)
        pq = [(0.0, v, None) for v in sorted(src)]
        heapq.heapify(pq)
        prev, best = {}, {v: 0.0 for v in src}
        while pq:
            d, v, p = heapq.heappop(pq)
            if v in prev:
                continue
            prev[v] = p
            if v in dst:
                path = [v]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])
                return path[::-1]
            for nb in sorted(adj.get(v, ())):
                if not (-HW < nb[0] < W + HW):
                    continue
                owners = device_vertex_owner.get(nb, set())
                cost = S
                if owners - {i, j}:
                    cost *= 6           # skirt other devices only if needed
                if (owners & {i, j}) and nb not in dst and nb not in src:
                    cost *= 6           # don't wrap around an endpoint's cell
                if tuple(sorted((v, nb))) in used_edges:
                    cost *= 12          # keep connections visually separate
                cost *= 1 + rnd.random() * 0.15
                nd = d + cost
                if nd < best.get(nb, 1e18):
                    best[nb] = nd
                    heapq.heappush(pq, (nd, nb, v))
        return None

    paths = []
    for i, j in sorted(links, key=lambda l: math.dist(pos[l[0]], pos[l[1]])):
        p = route(i, j)
        if not p or len(p) < 2:
            continue
        for a, b2 in zip(p, p[1:]):
            used_edges.add(tuple(sorted((a, b2))))
        used_exits[i].add(p[0])
        used_exits[j].add(p[-1])
        paths.append(p)

    def d_attr(p):
        return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in p)

    # --- Emit SVG.
    out = []
    out.append(f'<svg id="network-bg-svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
               'xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMin slice" '
               'aria-hidden="true" focusable="false">')
    out.append("<defs>")
    out.extend(defs)
    # Honeycomb tile: pointy-top lattice, one tile = HW x 3S.
    tile = []
    for (cx, cy) in [(0, 0), (HW, 0), (HW / 2, VS), (0, 2 * VS), (HW, 2 * VS)]:
        tile.append(f'<polygon points="{hex_points(cx, cy, S)}" />')
    out.append(f'<pattern id="hex-grid" patternUnits="userSpaceOnUse" x="0" y="0" '
               f'width="{f(HW)}" height="{f(3 * S)}">'
               f'<g fill="none" stroke="{LINE}" stroke-width="1">{"".join(tile)}</g></pattern>')
    out.append("</defs>")
    out.append(f'<rect id="network-hexgrid" x="0" y="0" width="{W}" height="{H}" '
               f'fill="url(#hex-grid)" opacity="0.28" />')

    out.append(f'<g id="network-links" fill="none" stroke="{LINE}" stroke-width="2.4" '
               'stroke-linejoin="round" opacity="0.7">')
    for p in paths:
        out.append(f'<path d="{d_attr(p)}" />')
    out.append("</g>")

    out.append(f'<g id="network-links-flow" fill="none" stroke="{ACCENT}" stroke-width="2.4" '
               'stroke-linejoin="round">')
    # Animations are CSS (network-bg.css): --d is the duration and --o a
    # negative delay, so each one is already mid-cycle on the first frame.
    for k, p in enumerate(paths):
        dur = 0.4 + 0.1 * (k % 4) + 0.04 * (len(p) % 5)
        cls = ' class="r"' if k % 2 else ""     # odd links flow the other way
        offset = (k * 0.35) % 4
        out.append(f'<path d="{d_attr(p)}"{cls} style="--d:{dur:.1f}s;--o:-{offset:.2f}s" />')
    out.append("</g>")

    # Each device type has its own look (styles in network-bg.css):
    #   routers   - a glowing hexagonal halo that pulses behind the cell,
    #   switches  - a dashed accent ring that runs around the cell,
    #   firewalls - a solid, bold accent cell with the shield knocked out,
    #   servers   - blinking activity lights on the rack units, plus lights
    #               chasing round the cell's corners.
    def of_type(t):
        return [d for d in devices if d[1] == t]

    out.append(f'<g id="network-nodes-active" fill="{ACCENT}">')
    for k, (cell, _, _) in enumerate(of_type("dev-router")):
        cx, cy = center(*cell)
        dur = 1.8 + 0.4 * (k % 4)
        out.append(f'<polygon points="{hex_points(cx, cy, S * 0.98)}" '
                   f'style="--d:{dur:.1f}s;--o:-{(k * 0.7) % dur:.2f}s" />')
    out.append("</g>")

    out.append('<g id="network-nodes">')
    for cell, t, _ in devices:
        cx, cy = center(*cell)
        pts = hex_points(cx, cy, S * 0.82)
        icon = f'<use href="#{t}" transform="translate({f(cx)} {f(cy)}) scale({ICON_SCALE})"'
        if t == "dev-firewall":
            out.append(f'<polygon class="fw" points="{pts}" />')
            out.append(icon + ' class="fw-icon" />')
        else:
            out.append(f'<polygon points="{pts}" fill="{PAGE}" stroke="{LINE}" stroke-width="2" />')
            out.append(icon + " />")
    out.append("</g>")

    # pathLength=120 makes the 6+4 dash pattern divide the ring evenly, so
    # there's no seam where the outline closes.
    out.append('<g id="network-switch-rings">')
    for k, (cell, _, _) in enumerate(of_type("dev-switch")):
        cx, cy = center(*cell)
        dur = 1.6 + 0.3 * (k % 3)
        rev = ' class="r"' if k % 2 else ""
        out.append(f'<polygon points="{hex_points(cx, cy, S * 0.82)}" pathLength="120"{rev} '
                   f'style="--d:{dur:.1f}s;--o:-{(k * 0.45) % dur:.2f}s" />')
    out.append("</g>")

    # Server activity lights: accent squares laid over the 4 status LEDs on
    # each of the dev-server icon's 3 rack units (coordinates match that
    # icon's LED rects). The 12 lights are split into 3 interleaved groups
    # and each group blinks as one, so a server costs 3 animations, not 12,
    # while still looking like independent lights.
    led_x = (2.0, 4.2, 6.4, 8.6)
    led_y = (-11.4, -3.4, 4.6)
    out.append(f'<g id="network-server-leds" fill="{ACCENT}">')
    for k, (cell, _, _) in enumerate(of_type("dev-server")):
        cx, cy = center(*cell)
        out.append(f'<g transform="translate({f(cx)} {f(cy)}) scale({ICON_SCALE})">')
        for g in range(3):
            dur = 1.1 + 0.35 * ((k + g) % 4)
            rects = "".join(
                f'<rect x="{x}" y="{y}" width="1.4" height="1.4" rx="0.3" />'
                for u, y in enumerate(led_y) for s, x in enumerate(led_x)
                if (u + s) % 3 == g)
            out.append(f'<g style="--d:{dur:.2f}s;--o:-{(k * 0.53 + g * 0.37) % dur:.2f}s">'
                       f'{rects}</g>')
        out.append("</g>")
    out.append("</g>")

    # Server corner chasers: a light on each of the cell's 6 corners. They all
    # share one cycle (--d on the group), and each corner starts 1/6 of a
    # cycle after the previous one, so the light runs around the hex.
    out.append(f'<g id="network-server-chase" fill="{ACCENT}">')
    for k, (cell, _, _) in enumerate(of_type("dev-server")):
        cx, cy = center(*cell)
        dur = 1.2 + 0.2 * (k % 3)
        base = (k * 0.41) % dur
        dots = "".join(
            f'<circle cx="{f(x)}" cy="{f(y)}" r="7" style="--o:-{(base + (5 - i) * dur / 6) % dur:.2f}s" />'
            for i, (x, y) in enumerate(corners(cx, cy, S * 0.82)))
        out.append(f'<g style="--d:{dur:.1f}s">{dots}</g>')
    out.append("</g>")
    out.append("</svg>")

    new = re.sub(r'<svg id="network-bg-svg".*?</svg>', lambda m: "\n".join(out), html,
                 count=1, flags=re.S)
    INDEX.write_text(new, encoding="utf-8")

    # --- Report.
    nn = [min(hexdist(devices[i][0], devices[j][0]) for j in range(n) if j != i)
          for i in range(n)]
    linked = [0] * n
    for i, j in links:
        linked[i] += 1
        linked[j] += 1
    hist = lambda xs: {v: xs.count(v) for v in sorted(set(xs))}
    types = hist([d[1][4:] for d in devices])
    print(f"{n} devices, {len(paths)}/{len(links)} links routed")
    print(f"nearest-neighbour spacing (cells): {hist(nn)}")
    print(f"links per device: {hist(linked)}")
    print(f"types: {types}")


if __name__ == "__main__":
    main()
