"""Fetch the KiCad library 3D models (STEP) a board uses and write a copy of the board pointing at them, so that
`kicad-cli pcb export step` puts the parts in (the CI has no KiCad 3D model package; without this the STEP is the bare
board). Models the library does not have (e.g. the HRO TYPE-C-31-M-12 USB-C) are reported and left out.
    python3 tools/kicad_3d_models.py BOARD.kicad_pcb OUT_DIR    # -> OUT_DIR/<models>, OUT_DIR/<board>_3d.kicad_pcb
Plain python (no pcbnew); downloads from gitlab.com/kicad/libraries/kicad-packages3D at the KiCad 7 tag.
"""
import os, re, sys, urllib.request

TAG = '7.0.0'
URL = 'https://gitlab.com/kicad/libraries/kicad-packages3D/-/raw/{tag}/{path}.step'

board, out = sys.argv[1], os.path.abspath(sys.argv[2])
os.makedirs(out, exist_ok=True)
src = open(board, encoding='utf-8').read()
pat = re.compile(r'\$\{KICAD\d_3DMODEL_DIR\}/([^"]+)\.(?:wrl|step)')
got = {}
for path in sorted(set(pat.findall(src))):
    dst = os.path.join(out, path + '.step')
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            with urllib.request.urlopen(URL.format(tag=TAG, path=path), timeout=60) as r:
                data = r.read()
            open(dst, 'wb').write(data)
        except Exception as e:                      # not in the library: that part is left out of the STEP
            print('no 3D model:', path, '-', e)
            continue
    got[path] = dst
    print('3D model:', path)
dst_board = os.path.join(out, os.path.basename(board).replace('.kicad_pcb', '_3d.kicad_pcb'))
open(dst_board, 'w', encoding='utf-8').write(pat.sub(lambda m: got.get(m.group(1), m.group(0)), src))
print('wrote', dst_board)
