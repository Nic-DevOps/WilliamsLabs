#!/usr/bin/env python3
"""Regenerate the homepage's hexagon-themed network background.

Rewrites the <svg id="network-bg-svg"> block in Website/html/index.html:
  - a faint honeycomb lattice (a single <pattern>) covers the canvas,
  - each device icon (the existing dev-router / dev-switch / dev-firewall /
    dev-server symbols, kept verbatim from the current file) sits in its own
    hex cell,
  - connections are routed along the honeycomb edges (shortest path that
    avoids other devices' cells), with the same flowing-packet animation,
  - a few cells pulse as hexagonal halos.

Colors come from the same CSS variables as before (--nbg-line, --nbg-node,
--nbg-accent, --bg-page), so the light/dark theme still applies.

Usage: python3 Website/scripts/generate_hex_network.py
"""
import heapq
import math
import random
import re
from pathlib import Path

INDEX = Path(__file__).resolve().parent.parent / "html" / "index.html"

W, H = 1600, 15400
S = 90                      # hex side length (pointy-top)
HW = math.sqrt(3) * S       # horizontal distance between cell centers
VS = 1.5 * S                # vertical distance between rows
ICON_SCALE = 3.2
SEED = 20261119

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


def main():
    rnd = random.Random(SEED)
    html = INDEX.read_text()
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

    # --- Place devices in bands, descending edge -> access -> dist -> core.
    band_h = 1400
    bands = int(math.ceil(H / band_h))
    tiers = [
        {"dev-switch": 5, "dev-server": 3, "dev-router": 1, "dev-firewall": 1},
        {"dev-switch": 4, "dev-router": 3, "dev-server": 2, "dev-firewall": 1},
        {"dev-router": 4, "dev-firewall": 3, "dev-switch": 2, "dev-server": 1},
    ]
    devices = []          # (cell, type, band)
    taken = []
    min_gap = 2.6 * HW
    for b in range(bands):
        y0, y1 = b * band_h + 140, min(H - 140, (b + 1) * band_h)
        weights = tiers[min(2, b * 3 // bands)]
        want = rnd.randint(8, 10)
        tries = 0
        placed = 0
        while placed < want and tries < 4000:
            tries += 1
            r = rnd.randint(int(y0 / VS), int(y1 / VS))
            c = rnd.randint(0, int((W - HW / 2) / HW))
            cx, cy = center(c, r)
            if not (70 < cx < W - 70):
                continue
            if any(math.dist((cx, cy), center(*t)) < min_gap for t in taken):
                continue
            t = rnd.choices(list(weights), list(weights.values()))[0]
            devices.append(((c, r), t, b))
            taken.append((c, r))
            placed += 1

    # --- Choose links: nearest neighbours within a band + uplinks to the band above.
    def dist(i, j):
        return math.dist(center(*devices[i][0]), center(*devices[j][0]))

    links = set()
    by_band = {}
    for i, d in enumerate(devices):
        by_band.setdefault(d[2], []).append(i)
    for b, idx in by_band.items():
        # minimum spanning tree inside the band keeps every band connected
        inside = {idx[0]}
        while len(inside) < len(idx):
            i, j = min(((i, j) for i in inside for j in idx if j not in inside),
                       key=lambda p: dist(*p))
            links.add(tuple(sorted((i, j))))
            inside.add(j)
        for i in idx:  # a few extra redundant links
            if rnd.random() < 0.35:
                others = sorted((j for j in idx if j != i), key=lambda j: dist(i, j))
                if len(others) > 1:
                    links.add(tuple(sorted((i, others[1]))))
        if b > 0 and by_band.get(b - 1):
            above = by_band[b - 1]
            for i in rnd.sample(idx, min(3, len(idx))):
                j = min(above, key=lambda j: dist(i, j))
                links.add(tuple(sorted((i, j))))

    # --- Route each link along hex edges.
    device_vertex_owner = {}
    for i, (cell, _, _) in enumerate(devices):
        for v in cell_vertices[cell]:
            device_vertex_owner.setdefault(v, set()).add(i)
    used = set()

    def route(i, j):
        src = set(cell_vertices[devices[i][0]])
        dst = set(cell_vertices[devices[j][0]])
        pq = [(0.0, v, None) for v in src]
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
            for n in adj.get(v, ()):
                if not (-HW < n[0] < W + HW):
                    continue
                owners = device_vertex_owner.get(n, set())
                cost = S
                if owners - {i, j}:
                    cost *= 40          # don't run through other devices
                e = tuple(sorted((v, n)))
                if e in used:
                    cost *= 0.75        # gently bundle parallel runs
                cost *= 1 + rnd.random() * 0.15
                nd = d + cost
                if nd < best.get(n, 1e18):
                    best[n] = nd
                    heapq.heappush(pq, (nd, n, v))
        return None

    paths = []
    for i, j in sorted(links):
        p = route(i, j)
        if not p or len(p) < 2:
            continue
        for a, b2 in zip(p, p[1:]):
            used.add(tuple(sorted((a, b2))))
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
    for n, p in enumerate(paths):
        dur = 0.4 + 0.1 * (n % 4) + 0.04 * (len(p) % 5)
        frm, to = ("0", "-62") if n % 2 == 0 else ("-62", "0")
        begin = (n * 0.35) % 4
        out.append(f'<path d="{d_attr(p)}" stroke-dasharray="7 55" opacity="0.8">'
                   f'<animate attributeName="stroke-dashoffset" from="{frm}" to="{to}" '
                   f'dur="{dur:.1f}s" begin="{begin:.2f}s" repeatCount="indefinite" /></path>')
    out.append("</g>")

    out.append(f'<g id="network-nodes-active" fill="{ACCENT}">')
    for n, i in enumerate(rnd.sample(range(len(devices)), min(18, len(devices)))):
        cx, cy = center(*devices[i][0])
        dur = 1.8 + 0.4 * (n % 4)
        out.append(f'<polygon points="{hex_points(cx, cy, S * 0.98)}" opacity="0.3">'
                   f'<animate attributeName="opacity" values="0.3;0.04;0.3" dur="{dur:.1f}s" '
                   f'begin="{n * 0.3:.2f}s" repeatCount="indefinite" /></polygon>')
    out.append("</g>")

    out.append('<g id="network-nodes">')
    for cell, t, _ in devices:
        cx, cy = center(*cell)
        out.append(f'<polygon points="{hex_points(cx, cy, S * 0.82)}" fill="{PAGE}" '
                   f'stroke="{LINE}" stroke-width="2" />')
        out.append(f'<use href="#{t}" transform="translate({f(cx)} {f(cy)}) scale({ICON_SCALE})" />')
    out.append("</g>")
    out.append("</svg>")

    new = re.sub(r'<svg id="network-bg-svg".*?</svg>', lambda m: "\n".join(out), html,
                 count=1, flags=re.S)
    INDEX.write_text(new)
    print(f"{len(devices)} devices, {len(paths)} hex-routed links")


if __name__ == "__main__":
    main()
