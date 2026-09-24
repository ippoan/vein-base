"""Build the 3D preview (site/index.html) from the generated PCB/case STEP files.
Run from the repository root after pcb/ and case/ have been built:
    python3 tools/build_viewer.py
Coordinates: origin = VoiceS3R center (M2 screw), z=0 = VoiceS3R bottom face, PCB bottom at z=-4.1.
"""
import base64, json, os
import numpy as np
import cadquery as cq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KICAD_ORIGIN = (100.0, 100.0)   # build_pcb.py places the board at (100,100) in KiCad coordinates


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def header(x, ys):
    pl = pins = None
    for y in ys:
        b = box(x - 1.27, x + 1.27, y - 1.27, y + 1.27, -2.5, 0)
        p = box(x - 0.32, x + 0.32, y - 0.32, y + 0.32, -7.1, 6.0)
        pl = b if pl is None else pl.union(b)
        pins = p if pins is None else pins.union(p)
    return pl, pins


def tri(shape):
    vs, ts = shape.val().tessellate(0.03, 0.15)
    v = np.array([(p.x, p.y, p.z) for p in vs], dtype=np.float32)
    return v[np.array(ts)].reshape(-1).astype(np.float32)


def main():
    shell = cq.importers.importStep(os.path.join(ROOT, 'case/vein_base_shell.step'))
    plate = cq.importers.importStep(os.path.join(ROOT, 'case/vein_base_plate.step'))
    pcb = cq.importers.importStep(os.path.join(ROOT, 'fab/vein_base_pcb.step')).translate((-KICAD_ORIGIN[0], KICAD_ORIGIN[1], -4.1))
    hR_pl, hR_pin = header(7.62, [7.62, 5.08, 2.54, 0, -2.54])
    hL_pl, hL_pin = header(-7.62, [7.62, 5.08, 2.54, 0])
    j3 = (box(-4.3, 4.3, -10.6, -4.2, -7.5, -4.1).cut(box(-3.7, 3.7, -10.7, -7.1, -6.9, -4.6))
          .union(box(-5.5, -3.4, -9.5, -6.5, -4.4, -4.1)).union(box(3.4, 5.5, -9.5, -6.5, -4.4, -4.1)))
    plug = box(-3.7, 3.7, -17.0, -10.6, -6.8, -4.7).union(box(-2.8, 2.8, -19.0, -17.0, -6.3, -5.2))
    screw = (cq.Workplane('XY').workplane(offset=-8.3).circle(1.0).extrude(11.3)
             .union(cq.Workplane('XY').workplane(offset=-9.6).circle(1.9).extrude(1.3)))
    atom = box(-12, 12, -12, 12, 0, 16.8).edges('|Z').fillet(3.0)
    usb = box(-4.5, 4.5, -13.0, -11.0, 0.6, 3.8)
    grplug = box(-4.9, 4.9, -22.0, -12.0, 4.2, 9.0)

    parts = [
        ('atom', 'VoiceS3R(外形のみ)', '#9fb6c8', 0.18, 'atom', atom),
        ('usb', 'USB-C 口', '#6b7a86', 0.9, 'atom', usb),
        ('grplug', 'NFC ケーブル(PORT.A・位置は参考)', '#e7e1cf', 0.85, 'atom', grplug),
        ('shell', 'ケース上部(24×24)', '#3d6fb6', 0.55, 'shell', shell),
        ('hdrpl', 'ピンヘッダー樹脂', '#2b2f33', 1, 'pcb', hR_pl.union(hL_pl)),
        ('hdrpin', 'ピン', '#d8b25a', 1, 'pcb', hR_pin.union(hL_pin)),
        ('pcb', '中継基板', '#1f7a4d', 1, 'pcb', pcb),
        ('mx', 'J3 MX1.25 4P', '#f1efe8', 1, 'pcb', j3),
        ('mxplug', '指静脈ケーブル', '#e7e1cf', 0.85, 'pcb', plug),
        ('plate', '底板', '#5b8fd6', 0.8, 'plate', plate),
        ('screw', 'M2×12 ネジ', '#a9adb2', 1, 'screw', screw),
    ]

    # interference check: fail the build if the case collides with anything
    bad = []
    for name, obj in [('pcb', pcb), ('headers', hR_pl.union(hL_pl).union(hR_pin).union(hL_pin)), ('J3', j3),
                      ('plug', plug), ('screw', screw), ('VoiceS3R', box(-12, 12, -12, 12, 0.01, 16.8))]:
        for cname, case in (('shell', shell), ('plate', plate)):
            v = case.intersect(obj).val().Volume()
            print(f'interference {cname:5s} x {name:8s} = {v:.3f} mm3')
            if v > 0.01:
                bad.append(f'{cname}/{name}')
    v = shell.intersect(plate).val().Volume()
    print(f'interference shell x plate = {v:.3f} mm3')
    if v > 0.01:
        bad.append('shell/plate')
    if bad:
        raise SystemExit('interference: ' + ', '.join(bad))

    model = [dict(key=k, label=l, color=c, opacity=o, group=g, data=base64.b64encode(tri(s).tobytes()).decode())
             for k, l, c, o, g, s in parts]
    tpl = open(os.path.join(ROOT, 'tools/viewer_template.html'), encoding='utf-8').read()
    os.makedirs(os.path.join(ROOT, 'site'), exist_ok=True)
    out = os.path.join(ROOT, 'site/index.html')
    open(out, 'w', encoding='utf-8').write(tpl.replace('__MODEL__', json.dumps(model)))
    open(os.path.join(ROOT, 'site/.nojekyll'), 'w').write('')
    print('wrote', out, os.path.getsize(out), 'bytes')


if __name__ == '__main__':
    main()
