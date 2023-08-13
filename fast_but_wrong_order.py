import pandas as pd
import tia.bbg.datamgr as dm
import tia.analysis.ta as ta
import tia.analysis.model as model
from collections import OrderedDict
import numpy as np
from scipy.interpolate import CubicSpline

mgr = dm.BbgDataManager()

# Set the base ticker values for each currency
base_spot_tickers = {
    'aud': 'ADSW', 'cad': 'CDSW', 'chf': 'SFSNT',
    'eur': 'EUSA', 'gbp': 'BPSWS', 'jpy': 'JYSO',
    'nzd': 'NDSWAP', 'sek': 'SKSW', 'usd': 'USOSFR'
}

# Create an empty dictionary to hold the extended tickers
spot_curves = {}

# Specify the desired tenors
spot_tenors = list(range(1, 11)) + [15, 20, 25, 30]

# Extend the base tickers for each currency to include specified tenors
for currency, base_ticker in base_spot_tickers.items():
    spot_curves[currency] = [base_ticker + str(tenor) + ' Curncy' for tenor in spot_tenors]

# Convert the spot_curves dictionary to a pandas DataFrame
spot_curves = pd.DataFrame.from_dict(spot_curves)


def get_last_prices(tickers):
    return mgr[tickers].PX_LAST

# Retrieve the last prices for all tickers in batches
n = len(spot_curves)
batch_size = 100  # You can adjust the batch size as needed

last_prices = []
for i in range(0, n, batch_size):
    tickers_batch = spot_curves.iloc[:, i:i+batch_size].stack().tolist()
    prices = get_last_prices(tickers_batch)
    prices = prices.reindex(tickers_batch)
    last_prices.extend(prices.values.tolist())

# Shape the last_prices list to match the spot_curves DataFrame
last_prices = np.array(last_prices).reshape(n, -1)

# Create the updated_spot_curves DataFrame with last prices
updated_spot_curves = pd.DataFrame(last_prices, columns=spot_curves.columns)

updated_spot_curves['tenor'] = [f"{i}" for i in spot_tenors]
updated_spot_curves.set_index('tenor', inplace=True)

print(updated_spot_curves)
# print(updated_spot_curves)

# for currency in updated_spot_curves.columns:
#     print(spot_tenors)
#     print(updated_spot_curves[currency].values)

# print(updated_spot_curves.values)

all_tenors = (list(range(1, 31)))
interpolated_spot_curves = pd.DataFrame(index=all_tenors)

for currency in updated_spot_curves.columns:
    original_tenors = spot_tenors
    original_rates = updated_spot_curves[currency].values

    spline = CubicSpline(original_tenors,original_rates, bc_type='natural')
    interpolated_rates = spline(all_tenors)
    interpolated_spot_curves[currency] = interpolated_rates




# final_spot_curves = pd.concat([updated_spot_curves, interpolated_spot_curves], axis=1)


# print(final_spot_curves)
