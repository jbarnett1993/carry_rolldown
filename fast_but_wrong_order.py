import pandas as pd
import tia.bbg.datamgr as dm
import tia.analysis.ta as ta
import tia.analysis.model as model
from collections import OrderedDict
import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

mgr = dm.BbgDataManager()

# Set the base ticker values for each currency
base_spot_tickers = {
    'aud': 'ADSW', 'cad': 'CDSW', 'chf': 'SFSNT',
    'eur': 'EUSA', 'gbp': 'BPSWS', 'jpy': 'JYSO',
    'nzd': 'NDSWAP', 'sek': 'SKSW', 'usd': 'USOSFR'
}

curve_frequency = {
    'aud': 4, 'cad': 2, 'chf': 2,
    'eur': 2, 'gbp': 2, 'jpy': 2,
    'nzd': 4, 'sek': 4, 'usd': 4
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

updated_spot_curves['tenor'] = spot_tenors
updated_spot_curves.set_index('tenor', inplace=True)


all_tenors = (list(range(1, 31)))
interpolated_spot_curves = pd.DataFrame(index=all_tenors)

for currency in updated_spot_curves.columns:
    original_tenors = spot_tenors
    original_rates = updated_spot_curves[currency].values

    spline = CubicSpline(original_tenors,original_rates, bc_type='natural')
    interpolated_rates = spline(all_tenors)
    interpolated_spot_curves[currency] = interpolated_rates


discountf1 = 1 + (interpolated_spot_curves.div(pd.Series(curve_frequency), axis=1))/100


# Calculate the compounding DataFrame
compounding = pd.DataFrame(
    [[curve_frequency[currency] * tenor for currency in curve_frequency] for tenor in all_tenors],
    index=all_tenors,
    columns=curve_frequency.keys()
)



discountf1 = 1 / (discountf1.pow(compounding))



# build out the forward curves 
fwds = pd.DataFrame({"point": []})

fwds["point"] = [f"{i}y{j}y" for i in all_tenors for j in all_tenors if i + j <= 30]

forward_rates = {}

fwds['t1'] = fwds['point'].str.extract('(\d+)y', expand=False).astype(int)
fwds['t2'] = fwds['point'].str.extract('(\d+)y$', expand=False).astype(int) + fwds['t1']



for currency in interpolated_spot_curves.columns:
    forward_rates[currency] = pd.DataFrame(index=all_tenors)


def calculate_forward_rate(t1, t2, currency):
    D1 = discountf1.loc[t1, currency]
    D2 = discountf1.loc[t2, currency]
    dT = t2 - t1
    return (np.log(D1 / D2) / dT)*100

for currency in interpolated_spot_curves.columns:
    fwds[currency] = fwds.apply(lambda row: calculate_forward_rate(row['t1'], row['t2'], currency), axis=1)


fwds.set_index('point', inplace=True)

fwds.drop('t1', inplace=True, axis=1)






# def calculate_rolldown(row, currency):
#     try:
#         t1 = row['t1']
#         t2 = row['t2']

#         if t1 == 1:
#             spot_rate = interpolated_spot_curves.loc[int(t2), currency]
#             return row[currency] - spot_rate
#         elif f"{t1-1}y{t2}y" in fwds.index:
#             prev_rate = fwds.loc[f"{t1-1}y{t2}y", currency]
#             return row[currency] - prev_rate
#         else:
#             return None
#     except Exception as e:
#         print(f"Error processing row: {row.name} - {str(e)}")

# # Initialize DataFrame to hold rolldown values
# rolldowns = pd.DataFrame(index=fwds.index)

# for currency in fwds:
#     if currency not in ['point','t1', 't2']:
#         rolldowns[currency] = fwds.apply(calculate_rolldown, args=(currency,), axis=1)

# print(rolldowns)


# rolldowns = fwds.copy()

# for currency in rolldowns.columns:
#     for i, row in fwds.iterrows():
#         t1 = row['t1']
#         t2 = row['t2']

#         if t1>1:




# # PLOTS if you want to compare them

# for currency in updated_spot_curves.columns:
#     plt.figure()
#     plt.plot(updated_spot_curves.index, updated_spot_curves[currency],label='bbg data')
#     plt.plot(interpolated_spot_curves.index,interpolated_spot_curves[currency],label="interpolated data")
#     plt.title(f"spot curve comparison - {currency.upper()}")
#     plt.xlabel="tenor"
#     plt.ylabel="rate"
#     plt.legend()
#     plt.show()


