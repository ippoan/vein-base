"""Convert KiCad pos.csv to JLCPCB CPL format (fab/jlc_cpl.csv)."""
import csv
rows = list(csv.DictReader(open('fab/pos.csv')))
with open('fab/jlc_cpl.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for r in rows:
        w.writerow([r['Ref'], r['PosX'] + 'mm', r['PosY'] + 'mm', 'Top' if r['Side'] == 'top' else 'Bottom', r['Rot']])
print(open('fab/jlc_cpl.csv').read())
