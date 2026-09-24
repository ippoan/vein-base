import re, sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); pcbnew.WriteDRCReport(b, '/tmp/drc.rpt', pcbnew.EDA_UNITS_MILLIMETRES, True)
rpt = open('/tmp/drc.rpt').read(); print(rpt[-3500:])
