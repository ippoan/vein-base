"""Read a Specctra session file (freerouting output) into a pcbnew board: shared by the station boards
(pcb/station_board/build_board.py, pcb/station_esp_board/build_board.py). Run with KiCad's python."""
import re
import pcbnew

mm = pcbnew.FromMM
LAY = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}


def sexp(text):
    """Parse an s-expression into nested lists of strings (quoted strings lose their quotes)."""
    stack, cur = [], []
    for tok in re.findall(r'"[^"]*"|\(|\)|[^\s()]+', text):
        if tok == '(':
            stack.append(cur); cur = []
        elif tok == ')':
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(tok.strip('"'))
    return cur[0]


def find(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0] == key:
            yield c


def import_ses(b, nets, path, via_d=0.6, via_drill=0.3):
    """Add the wires and vias of a Specctra session file to board b (nets: name -> NETINFO_ITEM)."""
    ses = sexp(open(path).read())
    route = next(find(ses, 'routes'))
    unit, res = next(find(route, 'resolution'))[1:3]
    k = {'um': 0.001, 'mm': 1.0, 'mil': 0.0254, 'inch': 25.4}[unit] / int(res)
    n_w = n_v = 0
    added = []
    for net in find(next(find(route, 'network_out')), 'net'):
        ni = nets[net[1]]
        for w in find(net, 'wire'):
            path = next(find(w, 'path'))
            lay, width, c = path[1], float(path[2]) * k, [float(v) * k for v in path[3:]]
            pts = list(zip(c[0::2], c[1::2]))
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(b)
                t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(-y1))); t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(-y2)))
                t.SetWidth(mm(width)); t.SetLayer(LAY[lay]); t.SetNet(ni); b.Add(t); n_w += 1; added.append(t)
        for v in find(net, 'via'):
            x, y = float(v[2]) * k, float(v[3]) * k
            via = pcbnew.PCB_VIA(b); via.SetPosition(pcbnew.VECTOR2I(mm(x), mm(-y)))
            via.SetWidth(mm(via_d)); via.SetDrill(mm(via_drill)); via.SetNet(ni); b.Add(via); n_v += 1
    n_d = prune_dangling(b, added)
    print(f'ses: {n_w} track segments ({n_d} dangling dropped), {n_v} vias')


def prune_dangling(b, tracks):
    """Drop those of tracks with an end on nothing of their net (no pad, via or other track there): freerouting 2.4.1
    sometimes leaves a short stub by a pad (DRC track_dangling). Repeated until none is left; returns how many."""
    tracks, n = list(tracks), 0
    while True:
        bad = []
        for t in tracks:
            me = t.m_Uuid.AsString()                       # (SWIG gives each lookup its own proxy: no `is`)
            for p in (t.GetStart(), t.GetEnd()):
                net, lay = t.GetNetCode(), t.GetLayer()
                if any(o.GetNetCode() == net and o.IsOnLayer(lay) and o.HitTest(p) for o in b.GetPads()):
                    continue
                if any(o.m_Uuid.AsString() != me and o.GetNetCode() == net and o.IsOnLayer(lay) and o.HitTest(p, 1)
                       for o in b.GetTracks()):
                    continue
                bad.append(t)
                break
        if not bad:
            return n
        for t in bad:
            b.Remove(t); tracks.remove(t); n += 1
