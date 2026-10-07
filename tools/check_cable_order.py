"""The finger vein module's cable (the kit's MX1.25 9P -> 4P, its 9P end re-pinned to 3..6, wired straight: 9P 3..6
-> 4P 1..4, red on the 4P's ▲) must reach the board's 4P with no twist and no wires crossed. Fails (exit 1) if not.

The module's 9P: pin 1 is the left end of its end face seen from outside with the window up (checked on the real one,
2026-10-07: the plug's holes read, from the left, - - red black green yellow - - -). The cable leaves the end face and
bends about an axis along that face (B: down under the module and back into J3; Unit P: out, up over and down into
J1), which keeps the wires' order along the face. So 9P 3..6 run left to right along it, and the 4P's pads 1..4 have
to run the same way along the same axis, each on the net of its 9P pin.

The module's place comes from the case scripts (read as literals, no CadQuery), the 4P's pads from the generated
.kicad_pcb (pcbnew): run after the boards are built.
Run from the repository root:  python3 tools/check_cable_order.py"""
import ast, os, sys
import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PITCH_9P = 1.25
# the 9P's pins 3..6 and the nets the 4P's pads 1..4 must be on (the board names them by the VoiceS3R's pins or
# the module's)
WIRES = [(3, 'VCC (red)', {'3V3'}), (4, 'GND (black)', {'GND'}), (5, 'RXD (green)', {'RXD', 'G5'}),
         (6, 'TXD (yellow)', {'TXD', 'G6'})]


def literals(path, func=None):
    """The literal assignments (a = 1.0, a, b = 1.0, 2.0) at the top of a script or of one of its functions."""
    tree = ast.parse(open(path, encoding='utf-8').read())
    body = tree.body if func is None else next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == func).body
    out = {}
    for n in body:
        if not isinstance(n, ast.Assign) or len(n.targets) != 1:
            continue
        try:
            v = ast.literal_eval(n.value)
        except ValueError:
            continue
        t = n.targets[0]
        if isinstance(t, ast.Name):
            out[t.id] = v
        elif isinstance(t, ast.Tuple) and isinstance(v, tuple) and len(t.elts) == len(v):
            out.update({e.id: x for e, x in zip(t.elts, v) if isinstance(e, ast.Name)})
    return out


def print_b():
    """3D 印刷 B (station/build_station_print.py concept_b): the module's 9P end at -y (the front); the cable bends
    down there and back (+y) into J3 under the module, opening -y."""
    v = literals(os.path.join(ROOT, 'station/build_station_print.py'), 'concept_b')
    vx0, vy0, vw = v['vx0'], v['vy0'], v['vw']
    return ('pcb/station_board/station_board_print_b.kicad_pcb', 'J3', (vx0 + vw / 2, vy0), (0.0, -1.0))


def unit_p():
    """Vein Unit P (station/build_vein_unit_print.py): the module's 9P end at -x; the cable goes out -x, up over and
    down into the vertical J1 past it."""
    x0, x1, y0, y1 = literals(os.path.join(ROOT, 'station/build_vein_unit_print.py'))['VEIN']
    return ('pcb/vein_unit_board/vein_unit_board_p.kicad_pcb', 'J1', (x0, (y0 + y1) / 2), (-1.0, 0.0))


def check(name, spec):
    board, ref, (cx, cy), (nx, ny) = spec
    # seen from outside (looking along -n) with the window up (+z), the viewer's right is (-n) x z = (-ny, nx)
    rx, ry = -ny, nx
    along = lambda x, y: (x - cx) * rx + (y - cy) * ry   # noqa: E731
    across = lambda x, y: (x - cx) * nx + (y - cy) * ny  # noqa: E731
    o = literals(os.path.join(ROOT, os.path.dirname(board), 'build_board.py'))   # its P(x, y): (OX + x, OY - y)
    ox, oy = o['OX'], o['OY']
    fp = pcbnew.LoadBoard(os.path.join(ROOT, board)).FindFootprintByReference(ref)
    if fp is None:
        print(f'{name}: no {ref} on {board}')
        return False
    pads = {}
    for p in fp.Pads():
        if p.GetNumber() in ('1', '2', '3', '4'):
            q = p.GetPosition()
            pads[int(p.GetNumber())] = (pcbnew.ToMM(q.x) - ox, oy - pcbnew.ToMM(q.y), p.GetNetname())
    ok = sorted(pads) == [1, 2, 3, 4]
    print(f'{name}: {board} {ref}; 9P end face at ({cx:g}, {cy:g}) facing ({nx:g}, {ny:g}), '
          f'pin 1 on its left seen from outside = toward ({-rx:g}, {-ry:g})')
    print('  wire  9P pin (along the face)       4P pad (along the face, out of the face)  net')
    rows = []
    for k, (p9, what, nets) in enumerate(WIRES, start=1):
        a9 = (p9 - 5) * PITCH_9P                             # the 9P's middle pin (5) on the face's middle
        x, y, net = pads.get(k, (float('nan'), float('nan'), '?'))
        rows.append((along(x, y), across(x, y)))
        good = net.lstrip('/') in nets
        ok &= good
        print(f'  {k}     {p9} {what:12s} {a9:+6.2f}       {k}  {rows[-1][0]:+7.2f} {rows[-1][1]:+7.2f}       '
              f'{net}{"" if good else "  <- should be " + "/".join(sorted(nets))}')
    steps = [b[0] - a[0] for a, b in zip(rows, rows[1:])]
    spread = max(r[1] for r in rows) - min(r[1] for r in rows)
    if not all(s > 0 for s in steps):
        print('  4P pads 1..4 do not run the 9P 3..6 way along the face: the cable would have to twist / cross')
        ok = False
    elif not all(abs(s - PITCH_9P) < 0.05 for s in steps) or spread > 0.05:
        print('  4P pads 1..4 are not in a row along the face (the 4P is turned across it)')
        ok = False
    print(f'  {"OK: straight, no twist, no wires crossed" if ok else "FAIL"}')
    return ok


if __name__ == '__main__':
    ok = True
    for name, spec in (('3D 印刷 B', print_b), ('Vein Unit P', unit_p)):
        ok &= check(name, spec())
    sys.exit(0 if ok else 1)
