"""Shared by the station scripts: CadQuery box helpers, the vein module as a picture, and the 3D preview page
(tools/station_template.html). z_top is the height the preview puts at 0 (the top face of the assembly)."""
import base64, json, os, shutil
import numpy as np
import cadquery as cq
from m5_cad import stl_tris

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def rbox(x0, x1, y0, y1, z0, z1, r):
    return box(x0, x1, y0, y1, z0, z1).edges('|Z').fillet(r)


def cyl_z(x, y, r, z0, z1):
    return cq.Workplane('XY').workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def cyl_y(x, y0, y1, z, r):
    return cq.Workplane('XZ').workplane(offset=-y1).center(x, z).circle(r).extrude(y1 - y0)  # XZ normal is -Y


def sym(f):
    """Union of f(sx, sy) over the four quadrants."""
    out = None
    for sx in (1, -1):
        for sy in (1, -1):
            s = f(sx, sy)
            out = s if out is None else out.union(s)
    return out


def quad(x0, x1, y0, y1, z0, z1):
    """Box in the +x +y quadrant (x0..x1, y0..y1 > 0), mirrored to all four."""
    return sym(lambda sx, sy: box(*sorted((sx * x0, sx * x1)), *sorted((sy * y0, sy * y1)), z0, z1))


def union(*shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.union(s)
    return out


def tri(shape, z_top):
    vs, ts = shape.val().tessellate(0.03, 0.15)
    v = np.array([(p.x, p.y, p.z - z_top) for p in vs], dtype=np.float32)
    return v[np.array(ts)].reshape(-1).astype(np.float32)


def stl_at(key, x, y, z, z_top, turn=False):
    """An official M5Stack STL moved to (x, y, z); ports / Grove on -y and the top (label face) on +z as in the file,
    or on +y with turn (half a turn about z)."""
    t = stl_tris(key).copy()
    c = (t.reshape(-1, 3).min(axis=0) + t.reshape(-1, 3).max(axis=0)) / 2
    t[..., :2] -= c[:2] if turn else 0
    if turn:
        t[..., :2] *= -1
    return (t + np.float32([x, y, z - z_top])).reshape(-1).astype(np.float32)


def vein_parts(rect, z0):
    """The vein module (x0, x1, y0, y1) standing on z0, long side along x, as a picture only (Waveshare publishes no
    CAD): drawn by hand inside its 59 × 26 × 15 box after the product photos, not measured. A finger scoop over the
    IR lens at +x, the flat dark window at -x, a channel across the bottom and the MX1.25 9P socket low in the -x end
    (the flat window's end, where Waveshare's photo shows the cable leaving level).
    Interference checks use the plain box."""
    vx0, vx1, vy0, vy1 = rect
    vz1 = z0 + 15.0
    yc = (vy0 + vy1) / 2
    scoop = (cq.Workplane('XY').workplane(offset=vz1 - 9.0).center(vx1 - 19.0, yc).rect(18.0, 9.0)
             .workplane(offset=9.5).rect(31.0, 21.0).loft())
    look = (rbox(*rect, z0, vz1, 2.0).edges('>Z').fillet(1.0).cut(scoop)
            .cut(box(vx0 + 3.0, vx1 - 36.0, vy0 + 2.5, vy1 - 2.5, vz1 - 0.3, vz1 + 1))
            .cut(box(vx0 + 26.0, vx0 + 36.0, vy0 - 1, vy1 + 1, z0 - 1, z0 + 1.5)))
    return [('vein', '指静脈モジュール(外形は公式値、細部は写真からのイメージ、コネクタ位置は未確定)', '#23272a', 1, 'mods', look),
            ('veinwin', '指静脈の平らな窓(イメージ)', '#0b0e10', 1, 'mods',
             box(vx0 + 3.0, vx1 - 36.0, vy0 + 2.5, vy1 - 2.5, vz1 - 0.3, vz1 - 0.05)),
            ('veinlens', '指静脈のレンズ(イメージ)', '#3b4d5e', 1, 'mods', cyl_z(vx1 - 19.0, yc, 3.0, vz1 - 9.0, vz1 - 8.7)),
            ('veinsock', '指静脈の MX1.25 9P(位置はイメージ)', '#f1efe8', 1, 'mods',
             box(vx0 - 0.05, vx0 + 0.5, yc - 6.5, yc + 6.5, z0 + 1.5, z0 + 5.0))]


def write_page(sub_dir, rev, parts, sub, dims, note, z_top, downloads=(), extra='', tz='-18'):
    """site/<sub_dir>/index.html; parts = [(key, label, colour, opacity, group, shape or float32 triangles)],
    downloads = [(label, path)] copied next to the page."""
    model = [dict(key=k, label=l, color=c, opacity=o, group=g,
                   data=base64.b64encode((s if isinstance(s, np.ndarray) else tri(s, z_top)).tobytes()).decode())
             for k, l, c, o, g, s in parts]
    site = os.path.join(ROOT, 'site', sub_dir)
    os.makedirs(site, exist_ok=True)
    rows = []
    for label, p in downloads:
        shutil.copyfile(p, os.path.join(site, os.path.basename(p)))
        rows.append(f'<a href="{os.path.basename(p)}" download>{label}<span>{os.path.basename(p)}</span></a>')
    rows.append(extra)
    table = ''.join(f'        <tr><td>{k}</td><td>{v}</td></tr>\n' for k, v in dims)
    tpl = open(os.path.join(ROOT, 'tools/station_template.html'), encoding='utf-8').read()
    page = os.path.join(site, 'index.html')
    open(page, 'w', encoding='utf-8').write(
        tpl.replace('__MODEL__', json.dumps(model)).replace('__REV__', rev).replace('__SUB__', sub)
        .replace('__DIMS__', table).replace('__NOTE__', note).replace('__TZ__', tz).replace('__DOWNLOADS__', ''.join(rows)))
    print('wrote', page, os.path.getsize(page), 'bytes')
