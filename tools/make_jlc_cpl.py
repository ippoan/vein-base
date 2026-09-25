"""Write the JLCPCB assembly files: CPL from KiCad pos.csv, BOM from pcb/jlc_bom.csv.
Outputs <outdir>/<prefix><VERSION>_jlc_cpl.csv and ..._jlc_bom.csv (default fab/vein_base_v<VERSION>_*).
If the BOM source does not exist, only the CPL is written.

--corrections <csv> (optional; without it the CPL is KiCad's pos.csv as is) turns KiCad's placement into JLC's
for the footprints listed (columns Footprint,Rotation,OffsetX,OffsetY; Footprint = the pos.csv Package):
  - Rotation: JLC's footprint is KiCad's turned by -Rotation, so the CPL gets (Rot + Rotation) mod 360.
  - OffsetX/Y: where JLC's footprint origin sits in KiCad's footprint coordinates (0 deg, mm, +y down as in the
    footprint editor). KiCad's pos.csv gives the footprint origin (+y up), so the offset is turned by the part's
    Rot and added to Mid X/Y.
The values come from overlaying JLC's footprint (EasyEDA data on the part page) on KiCad's, pad by pad.

Bottom-side parts (the same table applies; JLC's footprints are drawn for the top side):
  - Mid X/Y stay in top-view board coordinates, not mirrored. EasyEDA (JLC's own EDA), Export Pick and Place:
    "Mirror the coordinates of the components on the bottom side(Some SMT manufacturer may need it, while JLCPCB
    does not)" (https://docs.easyeda.com/en/PCB/Export-Coordinate/). kicad-cli 7 writes them unmirrored too.
  - kicad-cli 7 writes Rot = the footprint's orientation as is. KiCad puts a part on the bottom by mirroring its
    footprint top-to-bottom (footprint y) and then turning it by Rot counter-clockwise seen from the top, so the offset
    gets its y mirrored before the turn; the result is where that point of the part physically sits.
  - JLC's Rotation for the bottom is counter-clockwise seen from the bottom: (180 - Rot + Rotation) mod 360. JLC's help
    only says "Positive values are counter clockwise"; this is what Bouni/kicad-jlcpcb-tools (fabrication.py) and KiKit
    (discussion #664, checked on JLC's assembly preview) do. Check a bottom part in JLC's preview before ordering.
  - A bottom-side part must be listed in the table (write 0,0,0 if the footprints already match), or the script raises."""
import argparse, csv, math, os, shutil
ap = argparse.ArgumentParser()
ap.add_argument('--pos', default='fab/pos.csv')
ap.add_argument('--bom', default='pcb/jlc_bom.csv')
ap.add_argument('--prefix', default='vein_base_v')
ap.add_argument('--outdir', default='fab')
ap.add_argument('--corrections', help='CSV of per-footprint rotation / origin offset to JLC (see the docstring)')
a = ap.parse_args()
VER = open('VERSION').read().strip()
cpl, bom = f'{a.outdir}/{a.prefix}{VER}_jlc_cpl.csv', f'{a.outdir}/{a.prefix}{VER}_jlc_bom.csv'
rows = list(csv.DictReader(open(a.pos)))
fix = {c['Footprint']: c for c in csv.DictReader(open(a.corrections))} if a.corrections else {}


def place(r):
    """(Mid X, Mid Y, Rotation) strings for one pos.csv row, corrected to JLC's footprint if listed."""
    c = fix.get(r['Package'])
    bottom = r['Side'] != 'top'
    if not c:
        if fix and bottom:
            raise SystemExit(f"{r['Ref']}: bottom-side part {r['Package']} is not in the corrections table")
        return r['PosX'], r['PosY'], r['Rot']
    rot = float(r['Rot'])
    t = math.radians(rot)
    ox, oy = float(c['OffsetX']), -float(c['OffsetY'])  # footprint +y down -> pos.csv +y up
    if bottom:
        oy = -oy  # KiCad mirrors a bottom part's footprint top-to-bottom before turning it by Rot
    x = float(r['PosX']) + ox * math.cos(t) - oy * math.sin(t)
    y = float(r['PosY']) + ox * math.sin(t) + oy * math.cos(t)
    jrot = 180 - rot if bottom else rot  # JLC: bottom parts turn counter-clockwise seen from the bottom
    return f'{x:.6f}', f'{y:.6f}', f"{(jrot + float(c['Rotation'])) % 360:.6f}"


with open(cpl, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for r in rows:
        x, y, rot = place(r)
        w.writerow([r['Ref'], x + 'mm', y + 'mm', 'Top' if r['Side'] == 'top' else 'Bottom', rot])
print(open(cpl).read())
if os.path.exists(a.bom):
    shutil.copyfile(a.bom, bom)
    print(open(bom).read())
else:
    print(f'WARNING: {a.bom} not found, wrote the CPL only (no BOM)')
