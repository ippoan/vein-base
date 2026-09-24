"""Write the JLCPCB assembly files: CPL from KiCad pos.csv, BOM from pcb/jlc_bom.csv.
Outputs fab/vein_base_v<VERSION>_jlc_cpl.csv and fab/vein_base_v<VERSION>_jlc_bom.csv."""
import csv, shutil
VER = open('VERSION').read().strip()
cpl, bom = f'fab/vein_base_v{VER}_jlc_cpl.csv', f'fab/vein_base_v{VER}_jlc_bom.csv'
rows = list(csv.DictReader(open('fab/pos.csv')))
with open(cpl, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for r in rows:
        w.writerow([r['Ref'], r['PosX'] + 'mm', r['PosY'] + 'mm', 'Top' if r['Side'] == 'top' else 'Bottom', r['Rot']])
shutil.copyfile('pcb/jlc_bom.csv', bom)
print(open(cpl).read())
print(open(bom).read())
