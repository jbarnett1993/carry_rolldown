
from tia.bbg import LocalTerminal
import pandas as pd


# Retrieve the EURUSD Forward Curve
resp = LocalTerminal.get_reference_data('YCSW0023 Index', 'par_curve')
# must retrieve a frame from the first row
respo = resp.as_map()['YCSW0023 Index']['par_curve']
print(respo)
