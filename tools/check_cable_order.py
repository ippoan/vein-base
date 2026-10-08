"""The finger vein module's cable (the kit's MX1.25 9P -> 4P, its 9P end re-pinned to 3..6, the wires straight) must
reach the board's 4P with no twist and no wires crossed. Fails (exit 1) if not.

The module's 9P: pin 1 is the left end of its end face seen from outside with the window up (checked on the real one,
2026-10-07: the plug's holes read, from the left, - - red black green yellow - - -). The cable leaves the end face and
bends about an axis along that face (B: down under the module and back into J3; Unit P: out, up over and down into
J1), which keeps the wires' order along the face. So 9P 3..6 run left to right along it, and the 4P's pads, taken
in their order along the same axis (whatever their numbers), have to be on the nets of 9P 3..6 in turn, one pitch
apart in a row.

The lock (a board's 5th spec entry, None = not checked): the cable made with both ends' locks on the same face (the
user's, 2026-10-08) leaves the 9P lock up and bends down into a vertical 4P, so the 4P's lock must face out of the
9P's end face (+1; -1 = back towards the module). A vertical 53398's locking window is the long wall on its tails'
side (Molex 533980000-SD): seen from the row of pads 1..4, away from its fitting nails (MP).

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
    """3D 印刷 B (station/build_station_print.py concept_b): the module's 9P end at -y (the front); the cable goes out
    -y and bends down into the vertical J3 just in front of it, whose lock faces out (-y)."""
    v = literals(os.path.join(ROOT, 'station/build_station_print.py'), 'concept_b')
    vx0, vy0, vw = v['vx0'], v['vy0'], v['vw']
    return ('pcb/station_board/station_board_print_b.kicad_pcb', 'J3', (vx0 + vw / 2, vy0), (0.0, -1.0), +1)


def unit_p():
    """Vein Unit P (station/build_vein_unit_print.py): the module's 9P end at -x; the cable goes out -x, up over and
    down into the vertical J1 past it, whose lock faces out (-x)."""
    x0, x1, y0, y1 = literals(os.path.join(ROOT, 'station/build_vein_unit_print.py'))['VEIN']
    return ('pcb/vein_unit_board/vein_unit_board_p.kicad_pcb', 'J1', (x0, (y0 + y1) / 2), (-1.0, 0.0), +1)


def check(name, spec):
    board, ref, (cx, cy), (nx, ny), lock = spec
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
    pads, mps = [], []
    for p in fp.Pads():
        q = p.GetPosition()
        x, y = pcbnew.ToMM(q.x) - ox, oy - pcbnew.ToMM(q.y)
        if p.GetNumber() in ('1', '2', '3', '4'):
            pads.append((along(x, y), across(x, y), p.GetNumber(), p.GetNetname()))
        elif p.GetNumber() == 'MP':
            mps.append(across(x, y))
    pads.sort()                                          # along the face, 9P pin 3's side first
    ok = sorted(r[2] for r in pads) == ['1', '2', '3', '4']
    print(f'{name}: {board} {ref}; 9P end face at ({cx:g}, {cy:g}) facing ({nx:g}, {ny:g}), '
          f'pin 1 on its left seen from outside = toward ({-rx:g}, {-ry:g})')
    print('  wire  9P pin (along the face)       4P pad (along the face, out of the face)  net')
    for k, ((p9, what, nets), (a, c, num, net)) in enumerate(zip(WIRES, pads), start=1):
        a9 = (p9 - 5) * PITCH_9P                             # the 9P's middle pin (5) on the face's middle
        good = net.lstrip('/') in nets
        ok &= good
        print(f'  {k}     {p9} {what:12s} {a9:+6.2f}       {num}  {a:+7.2f} {c:+7.2f}       '
              f'{net}{"" if good else "  <- should be " + "/".join(sorted(nets))}')
    if len(pads) == 4 and not ok:
        print('  the 4P\'s pads along the face are not on the 9P 3..6 nets in turn: the cable would have to twist / cross')
    steps = [b[0] - a[0] for a, b in zip(pads, pads[1:])]
    spread = max(r[1] for r in pads) - min(r[1] for r in pads) if pads else 0
    if not all(abs(s - PITCH_9P) < 0.05 for s in steps) or spread > 0.05:
        print('  4P pads are not in a row along the face (the 4P is turned across it)')
        ok = False
    if lock is not None:
        # the locking window: from the pads' row, away from the fitting nails; its sign out of the face (+) or in (-)
        row = sum(r[1] for r in pads) / len(pads)
        side = (row - sum(mps) / len(mps)) if mps else 0.0
        faces = (side > 0) - (side < 0)
        good = faces == lock
        ok &= good
        print(f'  lock (the tails\' wall, away from the fitting nails) faces {"out of" if faces > 0 else "into"} the '
              f'9P\'s end face{"" if good else ", should face " + ("out of it" if lock > 0 else "into it") + " (both ends' locks on the same face)"}')
    print(f'  {"OK: straight, no twist, no wires crossed" if ok else "FAIL"}')
    return ok


if __name__ == '__main__':
    ok = True
    for name, spec in (('3D 印刷 B', print_b), ('Vein Unit P', unit_p)):
        ok &= check(name, spec())
    sys.exit(0 if ok else 1)
