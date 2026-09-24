"""Run KiCad DRC on pcb/vein_base.kicad_pcb and fail on real errors (library warnings are ignored)."""
import re, sys
import pcbnew

b = pcbnew.LoadBoard('pcb/vein_base.kicad_pcb')
pcbnew.WriteDRCReport(b, 'fab/drc.rpt', pcbnew.EDA_UNITS_MILLIMETRES, True)
rpt = open('fab/drc.rpt').read()
print(rpt)
kinds = re.findall(r'^\[(\w+)\]', rpt, re.M)
ignored = {'lib_footprint_issues', 'lib_footprint_mismatch', 'silk_over_copper', 'silk_overlap', 'text_height'}
errors = [k for k in kinds if k not in ignored]
unconnected = int(re.search(r'Found (\d+) unconnected', rpt).group(1))
if errors or unconnected:
    sys.exit(f'DRC failed: {errors} unconnected={unconnected}')
print('DRC OK')
