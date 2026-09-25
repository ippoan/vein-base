"""Run KiCad DRC on a board (default pcb/vein_base.kicad_pcb) and fail on real errors (library warnings are ignored)."""
import argparse, re, sys
import pcbnew

ap = argparse.ArgumentParser()
ap.add_argument('--board', default='pcb/vein_base.kicad_pcb')
ap.add_argument('--report', default='fab/drc.rpt')
ap.add_argument('--ignore', action='append', default=[], metavar='RULE', help='also ignore this rule (added to the defaults)')
a = ap.parse_args()

b = pcbnew.LoadBoard(a.board)
pcbnew.WriteDRCReport(b, a.report, pcbnew.EDA_UNITS_MILLIMETRES, True)
rpt = open(a.report).read()
print(rpt)
kinds = re.findall(r'^\[(\w+)\]', rpt, re.M)
ignored = {'lib_footprint_issues', 'lib_footprint_mismatch', 'silk_over_copper', 'silk_overlap', 'text_height'} | set(a.ignore)
errors = [k for k in kinds if k not in ignored]
unconnected = int(re.search(r'Found (\d+) unconnected', rpt).group(1))
if errors or unconnected:
    sys.exit(f'DRC failed: {errors} unconnected={unconnected}')
print('DRC OK')
