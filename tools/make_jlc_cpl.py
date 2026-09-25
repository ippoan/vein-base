"""Write the JLCPCB assembly files: CPL from KiCad pos.csv, BOM from pcb/jlc_bom.csv.
Outputs <outdir>/<prefix><VERSION>_jlc_cpl.csv and ..._jlc_bom.csv (default fab/vein_base_v<VERSION>_*).
If the BOM source does not exist, only the CPL is written."""
import argparse, csv, os, shutil
ap = argparse.ArgumentParser()
ap.add_argument('--pos', default='fab/pos.csv')
ap.add_argument('--bom', default='pcb/jlc_bom.csv')
ap.add_argument('--prefix', default='vein_base_v')
ap.add_argument('--outdir', default='fab')
a = ap.parse_args()
VER = open('VERSION').read().strip()
cpl, bom = f'{a.outdir}/{a.prefix}{VER}_jlc_cpl.csv', f'{a.outdir}/{a.prefix}{VER}_jlc_bom.csv'
rows = list(csv.DictReader(open(a.pos)))
with open(cpl, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for r in rows:
        w.writerow([r['Ref'], r['PosX'] + 'mm', r['PosY'] + 'mm', 'Top' if r['Side'] == 'top' else 'Bottom', r['Rot']])
print(open(cpl).read())
if os.path.exists(a.bom):
    shutil.copyfile(a.bom, bom)
    print(open(bom).read())
else:
    print(f'WARNING: {a.bom} not found, wrote the CPL only (no BOM)')
