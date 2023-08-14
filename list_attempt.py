
from tia.bbg import LocalTerminal
import pandas as pd

curves = {
    'aud': '303', 'cad': '4', 'chf': '21',
    'eur': '45', 'gbp': '22', 'jpy': '13',
    'nzd': '15', 'sek': '20', 'usd': '490'
}

def get_curve(ccy):
    for ccy, curve in curves.items():
        resp = LocalTerminal.get_reference_data('YCSW'+curve.zfill(4)+' Index','par_curve')
        df = resp.as_frame()['par_curve']['YCSW'+curve.zfill(4)+' Index']
        print (df)

get_curve(curves)



# # Retrieve the EURUSD Forward Curve
# resp = LocalTerminal.get_reference_data('YCSW0023 Index', 'par_curve')
# # must retrieve a frame from the first row
# # respo = resp.as_map()['YCSW0023 Index']['par_curve']

# df = resp.as_frame()['par_curve']['YCSW0023 Index']
# # print(respo)
# print(df)
