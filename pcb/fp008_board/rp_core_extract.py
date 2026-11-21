"""Take the RP2350A core (the chip, its regulator, crystal, decoupling and USB series resistors, with their copper)
out of Raspberry Pi's "RP2350A Minimal" KiCad design (RPI-RP2350A-MINIMAL_R4-S1, MIT licence, see
rp2350_core_LICENSE.txt) into rp2350_core.json, for build_board.py (f6, through rp_core.py) to put on our board around the RP2354A (same
QFN-60 and pins, flash inside). The minimal design's own regulator layout is the one Raspberry Pi stands behind
("Hardware design with RP2350" 2.1: the inductor the right way round and this exact layout), so it is copied, not
redrawn. Plain Python, no KiCad (the design is KiCad 9; our CI has KiCad 7):
    python3 rp_core_extract.py RPI-RP2350A-MINIMAL_R4-S1.kicad_pcb
Coordinates in the JSON: mm from U1's origin, KiCad's axes (y down)."""
import json, re, sys

CORE = ['U1', 'L1', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18',
        'R2', 'R3', 'R7', 'R8', 'C3', 'C4', 'X1']
# the copper kept: nets of the core, inside BOX (U1-relative x0, x1, y0, y1)
NETS = {'+3V3', 'GND', '+1V1', '/VREG_AVDD', '/VREG_LX', '/XIN', '/XOUT', 'Net-(C4-Pad1)', 'Net-(U1-USB_DP)',
        'Net-(U1-USB_DM)'}
BOX = (-7.6, 8.2, -8.6, 14.8)


def parse(t):
    toks = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', t)
    st = [[]]
    for k in toks:
        if k == '(':
            st.append([])
        elif k == ')':
            x = st.pop(); st[-1].append(x)
        else:
            st[-1].append(k[1:-1] if k.startswith('"') else k)
    return st[0][0]


def find(n, key):
    return [c for c in n if isinstance(c, list) and c and c[0] == key]


def get(n, key):
    r = find(n, key)
    return r[0] if r else None


b = parse(open(sys.argv[1], encoding='utf-8').read())
fps = {}
for f in find(b, 'footprint'):
    ref = [p[2] for p in find(f, 'property') if p[1] == 'Reference'][0]
    at = get(f, 'at')
    fps[ref] = (f, float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0)
_, ox, oy, orot = fps['U1']
assert orot == 0
inside = lambda x, y: BOX[0] <= x - ox <= BOX[1] and BOX[2] <= y - oy <= BOX[3]

out = {'source': 'Raspberry Pi RPI-RP2350A-MINIMAL_R4-S1 (MIT)', 'footprints': [], 'segments': [], 'vias': [],
       'zones': []}
for ref in CORE:
    f, x, y, rot = fps[ref]
    pads = []
    for p in find(f, 'pad'):
        at = get(p, 'at'); size = get(p, 'size'); drill = get(p, 'drill'); net = get(p, 'net')
        pads.append({'num': p[1], 'type': p[2], 'shape': p[3], 'x': float(at[1]), 'y': float(at[2]),
                     'rot': float(at[3]) if len(at) > 3 else 0.0, 'w': float(size[1]), 'h': float(size[2]),
                     'drill': float(drill[1]) if drill else None, 'layers': get(p, 'layers')[1:],
                     'net': net[1] if net else ''})
    crt = []
    for r in find(f, 'fp_rect') + find(f, 'fp_line'):
        if get(r, 'layer')[1] == 'F.CrtYd':
            s, e = get(r, 'start'), get(r, 'end')
            crt.append((r[0], float(s[1]), float(s[2]), float(e[1]), float(e[2])))
    out['footprints'].append({'ref': ref, 'value': [q[2] for q in find(f, 'property') if q[1] == 'Value'][0],
                              'fp': f[1].split(':')[-1], 'x': x - ox, 'y': y - oy, 'rot': rot, 'pads': pads,
                              'courtyard': crt})
for s in find(b, 'segment'):
    a, e, net = get(s, 'start'), get(s, 'end'), get(s, 'net')[1]
    if net in NETS and inside(float(a[1]), float(a[2])) and inside(float(e[1]), float(e[2])):
        out['segments'].append({'x0': float(a[1]) - ox, 'y0': float(a[2]) - oy, 'x1': float(e[1]) - ox,
                                'y1': float(e[2]) - oy, 'w': float(get(s, 'width')[1]),
                                'layer': get(s, 'layer')[1], 'net': net})
for v in find(b, 'via'):
    at, net = get(v, 'at'), get(v, 'net')[1]
    if net in NETS and inside(float(at[1]), float(at[2])):
        out['vias'].append({'x': float(at[1]) - ox, 'y': float(at[2]) - oy, 'size': float(get(v, 'size')[1]),
                            'drill': float(get(v, 'drill')[1]), 'net': net})
for z in find(b, 'zone'):
    net = get(z, 'net')[1]
    pts = [(float(p[1]) - ox, float(p[2]) - oy) for p in get(get(z, 'polygon'), 'pts') if p[0] == 'xy']
    if net not in NETS or not all(BOX[0] <= x <= BOX[1] and BOX[2] <= y <= BOX[3] for x, y in pts):
        continue                                   # the board-wide pours are ours to make
    cpads = get(z, 'connect_pads'); fill = get(z, 'fill')
    out['zones'].append({'net': net, 'layer': get(z, 'layer')[1], 'priority': int(get(z, 'priority')[1]) if get(z, 'priority') else 0,
                         'pts': pts, 'clearance': float(get(cpads, 'clearance')[1]) if cpads and get(cpads, 'clearance') else 0.2,
                         'connect': cpads[1] if cpads and len(cpads) > 1 and not isinstance(cpads[1], list) else 'thermal',
                         'min_thickness': float(get(z, 'min_thickness')[1]) if get(z, 'min_thickness') else 0.2,
                         'thermal_gap': float(get(fill, 'thermal_gap')[1]) if fill and get(fill, 'thermal_gap') else 0.5,
                         'thermal_width': float(get(fill, 'thermal_bridge_width')[1]) if fill and get(fill, 'thermal_bridge_width') else 0.5})
# drop the kept tracks left with an end on nothing kept (they went on to parts outside the core, e.g. the RUN
# button's GND): an end counts as connected on a core pad of its net, a kept via, another kept track's end, or inside
# a kept zone of its net (3V3: anywhere, build_board.py pours it over the core)
import math


def pad_pts(net):
    for f in out['footprints']:
        c, s_ = math.cos(math.radians(-f['rot'])), math.sin(math.radians(-f['rot']))
        for q in f['pads']:
            if q['net'] == net:
                # KiCad: pad 'at' is in the footprint's frame; turn by the footprint's rotation (y down)
                yield (f['x'] + q['x'] * c - q['y'] * s_, f['y'] + q['x'] * s_ + q['y'] * c, max(q['w'], q['h']) / 2)


def in_poly(x, y, pts):
    inside = False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def connected(x, y, net, me):
    if net == '+3V3':                  # rp_core.py pours 3V3 on F.Cu over the whole BOX (as the minimal design's F.Cu)
        return True
    if any(math.hypot(x - px, y - py) <= r for px, py, r in pad_pts(net)):
        return True
    if any(v['net'] == net and math.hypot(x - v['x'], y - v['y']) <= v['size'] / 2 for v in out['vias']):
        return True
    if any(z['net'] == net and in_poly(x, y, z['pts']) for z in out['zones']):
        return True
    return any(t is not me and t['net'] == net and any(math.hypot(x - ex, y - ey) < 1e-3 for ex, ey in
                                                         ((t['x0'], t['y0']), (t['x1'], t['y1'])))
               for t in out['segments'])


while True:
    bad = [t for t in out['segments'] if not (connected(t['x0'], t['y0'], t['net'], t) and connected(t['x1'], t['y1'], t['net'], t))]
    if not bad:
        break
    out['segments'] = [t for t in out['segments'] if t not in bad]
    print('dropped dangling', [(t['net'], round(t['x0'], 2), round(t['y0'], 2)) for t in bad])
json.dump(out, open('rp2350_core.json', 'w'), indent=1)
print({k: len(v) for k, v in out.items() if isinstance(v, list)})
