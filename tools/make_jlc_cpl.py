"""Write the JLCPCB assembly files: CPL from KiCad pos.csv, BOM from pcb/jlc_bom.csv.
Outputs <outdir>/<prefix><VERSION>_jlc_cpl.csv and ..._jlc_bom.csv (default fab/vein_base_v<VERSION>_*).
If the BOM source does not exist, only the CPL is written.

--corrections <csv> (optional; without it the CPL is KiCad's pos.csv as is) turns KiCad's placement into JLC's
for the footprints listed (columns Footprint,Rotation,OffsetX,OffsetY; Footprint = the pos.csv Package):
  - Rotation: JLC's footprint is KiCad's turned by -Rotation, so the CPL gets (Rot + Rotation) mod 360.
  - OffsetX/Y: where JLC's footprint origin sits in KiCad's footprint coordinates (0 deg, mm, +y down as in the
    footprint editor). KiCad's pos.csv gives the footprint origin (+y up), so the offset is turned by the part's
    Rot and added to Mid X/Y. Bottom-side parts are not handled (raises).
The values come from overlaying JLC's footprint (EasyEDA data on the part page) on KiCad's, pad by pad."""
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
    if not c:
        return r['PosX'], r['PosY'], r['Rot']
    if r['Side'] != 'top':
        raise SystemExit(f"{r['Ref']}: correction for a bottom-side part is not supported")
    rot = float(r['Rot'])
    t = math.radians(rot)
    ox, oy = float(c['OffsetX']), -float(c['OffsetY'])  # footprint +y down -> pos.csv +y up
    x = float(r['PosX']) + ox * math.cos(t) - oy * math.sin(t)
    y = float(r['PosY']) + ox * math.sin(t) + oy * math.cos(t)
    return f'{x:.6f}', f'{y:.6f}', f"{(rot + float(c['Rotation'])) % 360:.6f}"


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
